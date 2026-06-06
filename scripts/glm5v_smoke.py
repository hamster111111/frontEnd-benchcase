import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "benchmarks" / "ui2code_n" / "evaluation" / "data" / "UI2Code-Real" / "data.jsonl"
DEFAULT_OUT_ROOT = ROOT / "experiments" / "glm5v_smoke"
DEFAULT_DOMESTIC_PROVIDERS = {"zhipu", "qwen", "deepseek", "mimo", "doubao"}

PROVIDERS = {
    "zhipu": {
        "api_key_vars": ["ZHIPU_API_KEY"],
        "base_url_vars": ["ZHIPU_OPENAI_BASE_URL", "ZHIPU_BASE_URL"],
        "model_vars": ["ZHIPU_VISION_MODEL", "ZHIPU_MODEL"],
        "default_model": "glm-5v-turbo",
        "supports_image": True,
    },
    "deepseek": {
        "api_key_vars": ["DEEPSEEK_API_KEY"],
        "base_url_vars": ["DEEPSEEK_BASE_URL"],
        "model_vars": ["DEEPSEEK_MODEL"],
        "default_model": "deepseek-v4-pro",
        "supports_image": False,
    },
    "qwen": {
        "api_key_vars": ["QWEN_API_KEY"],
        "base_url_vars": ["QWEN_BASE_URL"],
        "model_vars": ["QWEN_VISION_MODEL", "QWEN_MODEL"],
        "default_model": "qwen3-vl-plus",
        "supports_image": True,
    },
    "mimo": {
        "api_key_vars": ["MIMO_API_KEY"],
        "base_url_vars": ["MIMO_BASE_URL"],
        "model_vars": ["MIMO_VISION_MODEL", "MIMO_MODEL"],
        "default_model": "mimo-v2.5",
        "supports_image": True,
    },
    "openrouter": {
        "api_key_vars": ["OPENROUTER_API_KEY"],
        "base_url_vars": ["OPENROUTER_BASE_URL"],
        "model_vars": ["OPENROUTER_VISION_MODEL", "OPENROUTER_MODEL"],
        "default_model": "qwen/qwen3.5-9b",
        "supports_image": True,
    },
}


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def first_env(env: dict, names: list[str], default: str = "") -> str:
    for name in names:
        value = env.get(name, "")
        if value:
            return value
    return default


def split_csv(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def is_enabled(value: str) -> bool:
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def parse_optional_int(value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError:
        return default


def resolve_provider(env: dict, provider_name: str) -> dict:
    provider = PROVIDERS[provider_name]
    domestic_providers = split_csv(env.get("EXPERIMENT_DOMESTIC_PROVIDERS", ""))
    if not domestic_providers:
        domestic_providers = DEFAULT_DOMESTIC_PROVIDERS
    bypass_proxy = is_enabled(env.get("EXPERIMENT_NO_PROXY_DOMESTIC", "0")) and provider_name in domestic_providers
    return {
        "name": provider_name,
        "api_key": first_env(env, provider["api_key_vars"]),
        "base_url": first_env(env, provider["base_url_vars"]),
        "model": first_env(env, provider["model_vars"], provider["default_model"]),
        "supports_image": provider["supports_image"],
        "bypass_proxy": bypass_proxy,
    }


def image_to_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("utf-8")


def build_prompt(row: dict) -> str:
    task_prompt = row.get("prompt", "")
    return f"""你是一个严谨的前端工程师。请根据给定 UI 截图生成一个完整、可直接运行的单文件 HTML。

要求：
1. 输出必须是完整 HTML 文件，包含 <!DOCTYPE html>、<html>、<head>、<style>、<body>。
2. CSS 写在 <style> 中，不要依赖外部 CSS、JS、图片或网络资源。
3. 尽可能还原截图中的布局、颜色、字体大小、间距、组件层级和视觉密度。
4. 如果截图中有真实图片或头像，无法复用原图时用 CSS 色块或渐变占位，但尺寸和布局要对齐。
5. 只输出一个 fenced code block，格式为 ```html ... ```，不要输出额外解释。

原始任务提示：
{task_prompt}
"""


def extract_html(text: str) -> str | None:
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    match = re.search(r"```html\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*([\s\S]*?)\s*```", cleaned)
    if match and "<html" in match.group(1).lower():
        return match.group(1).strip()
    idx = cleaned.lower().find("<!doctype html")
    if idx >= 0:
        return cleaned[idx:].strip()
    idx = cleaned.lower().find("<html")
    if idx >= 0:
        return cleaned[idx:].strip()
    return None


def html_looks_complete(html: str) -> bool:
    lowered = html.lower()
    return "</html>" in lowered and "</body>" in lowered


def post_chat(base_url: str, api_key: str, body: dict, timeout: int, bypass_proxy: bool = False) -> tuple[int, dict | str]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if bypass_proxy else None
        response = opener.open(req, timeout=timeout) if opener else urllib.request.urlopen(req, timeout=timeout)
        with response as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text)
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(text) if text else ""
        except json.JSONDecodeError:
            parsed = text
        return e.code, parsed
    except (TimeoutError, urllib.error.URLError, OSError) as e:
        return -1, {"error": {"code": type(e).__name__, "message": str(e)}}


def safe_write_jsonl(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def make_run_dir(out_root: Path, run_name: str | None) -> Path:
    if not run_name:
        run_name = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_name
    for sub in ["inputs", "inputs/images", "inputs/prompts", "raw", "html", "logs"]:
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    return run_dir


def select_rows(rows: list[dict], ids: list[int] | None, limit: int) -> list[dict]:
    if ids:
        id_set = set(ids)
        selected = [row for row in rows if int(row["id"]) in id_set]
    else:
        selected = rows[:limit]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a small UI2Code smoke test with an OpenAI-compatible model.")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="zhipu")
    parser.add_argument("--dataset-jsonl", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--ids", nargs="*", type=int, default=None)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Defaults to EXPERIMENT_MAX_TOKENS. Set to 0 to omit max_tokens from the request body.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    env = load_env(ROOT / ".env")
    provider = resolve_provider(env, args.provider)
    api_key = provider["api_key"]
    base_url = provider["base_url"]
    model = provider["model"]
    env_max_tokens = parse_optional_int(env.get("EXPERIMENT_MAX_TOKENS"), 0)
    max_tokens = env_max_tokens if args.max_tokens is None else args.max_tokens

    if not args.dry_run and (not api_key or not base_url):
        print(f"{args.provider} API key or base URL is empty. Fill .env first.", file=sys.stderr)
        return 2

    if not args.dry_run and not provider["supports_image"]:
        print(
            f"{args.provider} is configured as a text-only provider for this script; "
            "the current UI2Code smoke test requires image_url input.",
            file=sys.stderr,
        )
        return 2

    rows = read_jsonl(args.dataset_jsonl)
    selected = select_rows(rows, args.ids, args.limit)
    dataset_dir = args.dataset_jsonl.parent
    run_dir = make_run_dir(args.out_root, args.run_name)

    summary = {
        "run_dir": str(run_dir.relative_to(ROOT)),
        "dataset_jsonl": str(args.dataset_jsonl.relative_to(ROOT)),
        "provider": args.provider,
        "model": model,
        "base_url": base_url.rstrip("/") if base_url else "",
        "supports_image": provider["supports_image"],
        "bypass_proxy": provider["bypass_proxy"],
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "dry_run": args.dry_run,
        "sample_count": len(selected),
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "results": [],
    }

    inputs_path = run_dir / "inputs" / "selected_samples.jsonl"
    raw_path = run_dir / "raw" / "responses.jsonl"

    for row in selected:
        image_path = dataset_dir / row["image_path"]
        item = {
            "id": row["id"],
            "prompt": row.get("prompt", ""),
            "image_path": str(image_path.relative_to(ROOT)),
        }
        local_image_path = run_dir / "inputs" / "images" / f"{row['id']}{image_path.suffix.lower()}"
        local_prompt_path = run_dir / "inputs" / "prompts" / f"{row['id']}.txt"
        if image_path.exists() and not local_image_path.exists():
            shutil.copy2(image_path, local_image_path)
        local_prompt_path.write_text(build_prompt(row), encoding="utf-8")
        item["local_image_path"] = str(local_image_path.relative_to(ROOT))
        item["local_prompt_path"] = str(local_prompt_path.relative_to(ROOT))
        safe_write_jsonl(inputs_path, item)

        if args.dry_run:
            summary["results"].append({**item, "status": "dry_run"})
            continue

        content = [
            {"type": "text", "text": build_prompt(row)},
            {"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}},
        ]
        body = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0,
        }
        if max_tokens > 0:
            body["max_tokens"] = max_tokens

        final_record = None
        for attempt in range(args.retries + 1):
            status, response = post_chat(base_url, api_key, body, args.timeout, provider["bypass_proxy"])
            final_record = {
                "id": row["id"],
                "image_path": row["image_path"],
                "attempt": attempt,
                "http_status": status,
                "response": response,
            }
            if status == 200:
                break
            if status == 429 and attempt < args.retries:
                time.sleep(args.retry_delay)
                continue
            break

        safe_write_jsonl(raw_path, final_record)

        result = {**item, "http_status": final_record["http_status"]}
        if final_record["http_status"] == 200 and isinstance(final_record["response"], dict):
            message = final_record["response"]["choices"][0]["message"]["content"]
            html = extract_html(message)
            result["usage"] = final_record["response"].get("usage")
            result["html_extracted"] = bool(html)
            if html:
                result["html_complete"] = html_looks_complete(html)
                html_path = run_dir / "html" / f"{row['id']}.html"
                html_path.write_text(html, encoding="utf-8")
                result["html_path"] = str(html_path.relative_to(ROOT))
        else:
            result["error"] = final_record["response"]
        summary["results"].append(result)

        if final_record["http_status"] == 429:
            break

    summary["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    (run_dir / "logs" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# GLM-5V Smoke Test Summary",
        "",
        f"- run_dir: `{summary['run_dir']}`",
        f"- provider: `{args.provider}`",
        f"- model: `{model}`",
        f"- max_tokens: `{'omitted' if max_tokens <= 0 else max_tokens}`",
        f"- bypass_proxy: `{provider['bypass_proxy']}`",
        f"- dry_run: `{args.dry_run}`",
        f"- samples: `{len(selected)}`",
        "",
        "| id | status | html | usage / error |",
        "|---:|---:|---:|---|",
    ]
    for item in summary["results"]:
        status = item.get("http_status", item.get("status", ""))
        html = item.get("html_extracted", "")
        if html and "html_complete" in item:
            html = f"{html} / complete={item['html_complete']}"
        detail = item.get("usage") or item.get("error") or ""
        detail_text = json.dumps(detail, ensure_ascii=False)[:180].replace("|", "\\|")
        md_lines.append(f"| {item['id']} | {status} | {html} | `{detail_text}` |")
    (run_dir / "summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({"run_dir": str(run_dir), "results": summary["results"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
