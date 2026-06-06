import argparse
import datetime as dt
import json
import random
import re
import shutil
import time
from pathlib import Path

from glm5v_smoke import (
    ROOT,
    extract_html,
    html_looks_complete,
    image_to_data_url,
    load_env,
    parse_optional_int,
    post_chat,
    resolve_provider,
    safe_write_jsonl,
)


OUT_ROOT = ROOT / "experiments" / "random10_bench_smoke"
UI2CODE_DATA = ROOT / "benchmarks" / "ui2code_n" / "evaluation" / "data"


UI2CODE_JSONL_BENCHES = [
    {
        "bench": "design2code",
        "jsonl": UI2CODE_DATA / "Design2Code" / "data.jsonl",
        "task_type": "static_generation",
        "source": "UI2Code_N/evaluation/data/Design2Code",
    },
    {
        "bench": "flame",
        "jsonl": UI2CODE_DATA / "Flame" / "data.jsonl",
        "task_type": "react_generation",
        "source": "UI2Code_N/evaluation/data/Flame",
    },
    {
        "bench": "ui2code_real",
        "jsonl": UI2CODE_DATA / "UI2Code-Real" / "data.jsonl",
        "task_type": "real_static_generation",
        "source": "UI2Code_N/evaluation/data/UI2Code-Real",
    },
    {
        "bench": "uipolish_real",
        "jsonl": UI2CODE_DATA / "UIPolish-Real" / "data.jsonl",
        "task_type": "repair_direct_incomplete",
        "source": "UI2Code_N/evaluation/data/UIPolish-Real",
        "notes": "本地 jsonl 只含目标截图和 prompt，缺少当前 HTML/渲染图；本轮按 direct 输入跑。",
    },
    {
        "bench": "uipolish_synthetic",
        "jsonl": UI2CODE_DATA / "UIPolish-Synthetic" / "uipolish_synthetic.jsonl",
        "task_type": "repair_direct_incomplete",
        "source": "UI2Code_N/evaluation/data/UIPolish-Synthetic",
        "notes": "本地 jsonl 只含目标截图和 prompt，缺少当前 HTML/渲染图；本轮按 direct 输入跑。",
    },
    {
        "bench": "web2code",
        "jsonl": UI2CODE_DATA / "Web2Code" / "web2code_image_eval.jsonl",
        "task_type": "webpage_generation",
        "source": "UI2Code_N/evaluation/data/Web2Code",
    },
]


SKIPPED_BENCHES = [
    {
        "bench": "designbench",
        "reason": "本地仓库没有完整 900 样本数据，需要先下载 HuggingFace/Google Drive 数据并确认 Node/browser evaluator。",
    },
    {
        "bench": "vab_css",
        "reason": "本地仓库已有 framework/task 代码，但 CSS benchmark 数据本体和最小 worker 配置还没落地。",
    },
    {
        "bench": "vision2web",
        "reason": "本地仓库只有代码；数据在 HuggingFace，需另拉 Level 1 static 后再跑。",
    },
    {
        "bench": "screencoder_screenbench",
        "reason": "本地仓库主要是方法代码；ScreenBench 数据在 HuggingFace，标准 evaluator 还需确认。",
    },
    {
        "bench": "visualwebbench",
        "reason": "任务偏网页理解/grounding，不是本轮 design-to-code 主线；数据也需 HuggingFace。",
    },
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if line.strip():
                row = json.loads(line)
                row["_row_index"] = idx
                rows.append(row)
    return rows


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def build_html_prompt(sample: dict) -> str:
    task_type = sample["task_type"]
    original_prompt = sample.get("original_prompt", "")
    extra = ""
    if task_type == "repair_direct_incomplete":
        extra = (
            "\n注意：原 benchmark 的完整 repair 输入通常还包含当前 HTML 代码和当前渲染截图；"
            "本轮 smoke test 只提供目标 UI 截图，因此请先按截图直接生成一个尽量贴近目标的完整 HTML。"
        )
    elif task_type == "interaction_generation":
        extra = (
            "\n请根据两张原型图生成一个可交互的单文件 HTML。第一张图是交互前状态，第二张图是交互后目标状态。"
            "必须实现描述中的交互行为，使用户执行该操作后页面能切换或呈现到第二张图对应的状态。"
        )

    return f"""你是一个严谨的前端工程师。请根据输入的 UI 截图和任务描述，生成一个完整、可直接运行的单文件 HTML。

要求：
1. 输出必须包含 <!DOCTYPE html>、<html>、<head>、<style>、<body>。
2. CSS 写在 <style> 中，不要依赖外部 CSS、JS、图片、字体或网络资源。
3. 尽可能还原截图中的布局、颜色、字体大小、间距、组件层级和视觉密度。
4. 如果截图中有真实图片或头像，无法复用原图时用 CSS 色块或渐变占位，但尺寸和布局要对齐。
5. 如果任务涉及交互，请在单文件内写必要的 JavaScript。
6. 只输出一个 fenced code block，格式为 ```html ... ```，不要输出额外解释。
{extra}

Benchmark：{sample['bench']}
任务类型：{task_type}
原始任务提示：
{original_prompt}
"""


def build_ui2code_samples(bench_cfg: dict) -> list[dict]:
    jsonl_path = bench_cfg["jsonl"]
    if not jsonl_path.exists():
        return []
    root = jsonl_path.parent
    samples = []
    for row in read_jsonl(jsonl_path):
        image_path = root / row["image_path"]
        if not image_path.exists():
            continue
        sample_id = str(row.get("id", row.get("_row_index", image_path.stem)))
        samples.append(
            {
                "bench": bench_cfg["bench"],
                "sample_id": sample_id,
                "task_type": bench_cfg["task_type"],
                "source": bench_cfg["source"],
                "notes": bench_cfg.get("notes", ""),
                "original_prompt": row.get("prompt", ""),
                "image_paths": [image_path],
                "reference_present": "reference" in row,
            }
        )
    return samples


def build_dcgen_samples() -> list[dict]:
    data_dir = ROOT / "benchmarks" / "dcgen" / "data" / "original"
    if not data_dir.exists():
        return []
    samples = []
    for image_path in sorted(data_dir.glob("*.png")):
        if image_path.name == "placeholder.png":
            continue
        reference_html = image_path.with_suffix(".html")
        if not reference_html.exists():
            continue
        samples.append(
            {
                "bench": "dcgen_original",
                "sample_id": image_path.stem,
                "task_type": "static_generation",
                "source": "DCGen/data/original",
                "notes": "使用 DCGen repo 自带 sample dataset 的 original 截图；reference HTML 只保存为元信息，不喂给模型。",
                "original_prompt": "请根据这张网页截图生成一个完整、可直接运行的单文件 HTML，尽量还原原网页。",
                "image_paths": [image_path],
                "reference_path": reference_html,
            }
        )
    return samples


def build_interaction2code_samples(rng: random.Random) -> list[dict]:
    sample_root = ROOT / "benchmarks" / "interaction2code" / "sample"
    if not sample_root.exists():
        return []
    samples = []
    for folder in sorted(p for p in sample_root.iterdir() if p.is_dir()):
        action_path = folder / "action.json"
        if not action_path.exists():
            continue
        action_data = json.loads(action_path.read_text(encoding="utf-8"))
        action_keys = [key for key in action_data if key.isdigit()]
        for action_key in action_keys:
            action = action_data[action_key]
            src = folder / f"{action['src']}.png"
            dst = folder / f"{action['dst']}.png"
            if not src.exists() or not dst.exists():
                continue
            prompt = (
                f"主题：{action_data.get('topic', '')}\n"
                f"框架：{action_data.get('framework', '')}\n"
                f"交互动作：{action.get('action', '')}\n"
                f"交互描述：{action.get('description', '')}\n"
                f"标签类型：{', '.join(action.get('tag type', []))}\n"
                f"视觉变化：{', '.join(action.get('visual type', []))}"
            )
            samples.append(
                {
                    "bench": "interaction2code",
                    "sample_id": f"{folder.name}_{action_key}",
                    "task_type": "interaction_generation",
                    "source": "Interaction2Code/sample",
                    "notes": "每个样本使用交互前/交互后两张图和 action.json 描述。",
                    "original_prompt": prompt,
                    "image_paths": [src, dst],
                    "action_json": action,
                    "page_id": folder.name,
                    "action_id": action_key,
                }
            )
    rng.shuffle(samples)
    return samples


def collect_benches(rng: random.Random) -> dict[str, list[dict]]:
    benches: dict[str, list[dict]] = {}
    for cfg in UI2CODE_JSONL_BENCHES:
        benches[cfg["bench"]] = build_ui2code_samples(cfg)
    benches["dcgen_original"] = build_dcgen_samples()
    benches["interaction2code"] = build_interaction2code_samples(rng)
    return benches


def copy_inputs(sample: dict, bench_dir: Path) -> dict:
    item = {
        "bench": sample["bench"],
        "sample_id": sample["sample_id"],
        "task_type": sample["task_type"],
        "source": sample.get("source", ""),
        "notes": sample.get("notes", ""),
        "original_prompt": sample.get("original_prompt", ""),
        "reference_present": sample.get("reference_present", False),
    }
    local_images = []
    for idx, image_path in enumerate(sample["image_paths"]):
        suffix = image_path.suffix.lower()
        local_path = bench_dir / "inputs" / "images" / f"{safe_name(sample['sample_id'])}_{idx}{suffix}"
        if not local_path.exists():
            shutil.copy2(image_path, local_path)
        local_images.append(str(local_path.relative_to(ROOT)))
    prompt_path = bench_dir / "inputs" / "prompts" / f"{safe_name(sample['sample_id'])}.txt"
    prompt = build_html_prompt(sample)
    prompt_path.write_text(prompt, encoding="utf-8")
    item["image_paths"] = [str(path.relative_to(ROOT)) for path in sample["image_paths"]]
    item["local_image_paths"] = local_images
    item["local_prompt_path"] = str(prompt_path.relative_to(ROOT))
    if sample.get("reference_path"):
        item["reference_path"] = str(sample["reference_path"].relative_to(ROOT))
    if sample.get("action_json"):
        item["action_json"] = sample["action_json"]
    return item


def make_run_dir(run_name: str | None) -> Path:
    if not run_name:
        run_name = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def ensure_bench_dirs(run_dir: Path, bench: str) -> Path:
    bench_dir = run_dir / bench
    for sub in ["inputs/images", "inputs/prompts", "raw", "texts", "html", "logs"]:
        (bench_dir / sub).mkdir(parents=True, exist_ok=True)
    return bench_dir


def run_sample(sample: dict, item: dict, bench_dir: Path, provider: dict, args, max_tokens: int) -> dict:
    prompt = build_html_prompt(sample)
    content = [{"type": "text", "text": prompt}]
    for image_path in sample["image_paths"]:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}})
    body = {
        "model": provider["model"],
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
    }
    if max_tokens > 0:
        body["max_tokens"] = max_tokens

    final_record = None
    for attempt in range(args.retries + 1):
        status, response = post_chat(
            provider["base_url"],
            provider["api_key"],
            body,
            args.timeout,
            provider["bypass_proxy"],
        )
        final_record = {
            "bench": sample["bench"],
            "sample_id": sample["sample_id"],
            "attempt": attempt,
            "http_status": status,
            "response": response,
        }
        if status == 200:
            break
        if status in {429, 500, 502, 503, 504} and attempt < args.retries:
            time.sleep(args.retry_delay)
            continue
        break

    safe_write_jsonl(bench_dir / "raw" / "responses.jsonl", final_record)
    result = {**item, "http_status": final_record["http_status"]}
    if final_record["http_status"] == 200 and isinstance(final_record["response"], dict):
        message = final_record["response"].get("choices", [{}])[0].get("message", {}).get("content", "")
        text_path = bench_dir / "texts" / f"{safe_name(sample['sample_id'])}.txt"
        text_path.write_text(message, encoding="utf-8")
        html = extract_html(message)
        result["text_path"] = str(text_path.relative_to(ROOT))
        result["usage"] = final_record["response"].get("usage")
        result["html_extracted"] = bool(html)
        if html:
            result["html_complete"] = html_looks_complete(html)
            html_path = bench_dir / "html" / f"{safe_name(sample['sample_id'])}.html"
            html_path.write_text(html, encoding="utf-8")
            result["html_path"] = str(html_path.relative_to(ROOT))
    else:
        result["error"] = final_record["response"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Randomly sample runnable frontend design benches and run a smoke test.")
    parser.add_argument("--provider", default="mimo")
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--only", nargs="*", default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    env = load_env(ROOT / ".env")
    provider = resolve_provider(env, args.provider)
    env_max_tokens = parse_optional_int(env.get("EXPERIMENT_MAX_TOKENS"), 0)
    max_tokens = env_max_tokens if args.max_tokens is None else args.max_tokens

    if args.provider != provider["name"]:
        raise ValueError(f"Provider mismatch: {args.provider} vs {provider['name']}")
    if not args.dry_run and (not provider["api_key"] or not provider["base_url"]):
        raise RuntimeError(f"{args.provider} API key or base URL is empty. Fill .env first.")
    if not args.dry_run and not provider["supports_image"]:
        raise RuntimeError(f"{args.provider} does not support image input in this runner.")

    run_dir = make_run_dir(args.run_name)
    benches = collect_benches(rng)
    selected_benches = set(args.only) if args.only else None
    summary = {
        "run_dir": str(run_dir.relative_to(ROOT)),
        "provider": args.provider,
        "model": provider["model"],
        "base_url": provider["base_url"].rstrip("/") if provider["base_url"] else "",
        "bypass_proxy": provider["bypass_proxy"],
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "sample_size_per_bench": args.sample_size,
        "seed": args.seed,
        "dry_run": args.dry_run,
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "benches": {},
        "skipped": SKIPPED_BENCHES,
    }

    for bench, samples in benches.items():
        if selected_benches and bench not in selected_benches:
            continue
        bench_dir = ensure_bench_dirs(run_dir, bench)
        if not samples:
            summary["benches"][bench] = {"available": 0, "selected": 0, "results": []}
            continue
        selected = rng.sample(samples, min(args.sample_size, len(samples)))
        bench_summary = {"available": len(samples), "selected": len(selected), "results": []}
        for sample in selected:
            item = copy_inputs(sample, bench_dir)
            safe_write_jsonl(bench_dir / "inputs" / "selected_samples.jsonl", item)
            if args.dry_run:
                result = {**item, "status": "dry_run"}
            else:
                result = run_sample(sample, item, bench_dir, provider, args, max_tokens)
            bench_summary["results"].append(result)
            status = result.get("http_status", result.get("status"))
            print(json.dumps({"bench": bench, "sample_id": sample["sample_id"], "status": status}, ensure_ascii=False), flush=True)
        summary["benches"][bench] = bench_summary

    summary["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Random 10 Benchmark Smoke Summary",
        "",
        f"- run_dir: `{summary['run_dir']}`",
        f"- provider/model: `{args.provider}` / `{provider['model']}`",
        f"- max_tokens: `{'omitted' if max_tokens <= 0 else max_tokens}`",
        f"- bypass_proxy: `{provider['bypass_proxy']}`",
        f"- sample_size_per_bench: `{args.sample_size}`",
        f"- seed: `{args.seed}`",
        f"- dry_run: `{args.dry_run}`",
        "",
        "| bench | available | selected | ok | html | complete | failed |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for bench, info in summary["benches"].items():
        results = info["results"]
        ok = sum(1 for r in results if r.get("http_status") == 200 or r.get("status") == "dry_run")
        html = sum(1 for r in results if r.get("html_extracted"))
        complete = sum(1 for r in results if r.get("html_complete"))
        failed = len(results) - ok
        md_lines.append(f"| {bench} | {info['available']} | {info['selected']} | {ok} | {html} | {complete} | {failed} |")

    md_lines.extend(["", "## Skipped", "", "| bench | reason |", "|---|---|"])
    for item in summary["skipped"]:
        md_lines.append(f"| {item['bench']} | {item['reason']} |")
    (run_dir / "summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "summary": str(run_dir / "summary.md")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
