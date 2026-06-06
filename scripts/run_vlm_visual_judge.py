import argparse
import csv
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

from glm5v_smoke import (
    PROVIDERS,
    ROOT,
    image_to_data_url,
    load_env,
    parse_optional_int,
    post_chat,
    resolve_provider,
    safe_write_jsonl,
)


DEFAULT_RUN_DIR = ROOT / "experiments" / "random10_bench_smoke" / "mimo_random10_20260604"
DEFAULT_BENCHES = ["design2code", "flame", "fullfront"]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_") or "sample"


def read_summary(run_dir: Path) -> dict:
    path = run_dir / "summary.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_existing_scores(path: Path) -> set[tuple[str, str]]:
    done = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("parsed_ok"):
                done.add((row.get("bench", ""), row.get("sample_id", "")))
    return done


def rendered_path_for(run_dir: Path, bench: str, sample_id: str) -> Path:
    return run_dir / bench / "rendered_fixed" / f"{safe_name(sample_id)}.png"


def make_items(run_dir: Path, summary: dict, benches: list[str]) -> list[dict]:
    items = []
    for bench in benches:
        bench_info = summary.get("benches", {}).get(bench)
        if not bench_info:
            continue
        for row in bench_info.get("results", []):
            if row.get("http_status") != 200 or not row.get("html_path"):
                continue
            sample_id = str(row["sample_id"])
            rendered = rendered_path_for(run_dir, bench, sample_id)
            refs = [ROOT / p for p in row.get("local_image_paths", [])]
            refs = [p for p in refs if p.exists()]
            if not refs or not rendered.exists():
                continue
            items.append(
                {
                    "bench": bench,
                    "sample_id": sample_id,
                    "task_type": row.get("task_type", ""),
                    "metadata": row.get("metadata", {}),
                    "reference_images": refs,
                    "generated_image": rendered,
                    "html_path": ROOT / row["html_path"],
                }
            )
    return items


def build_prompt(item: dict) -> str:
    has_interaction_context = len(item["reference_images"]) > 1
    interaction_note = ""
    if has_interaction_context:
        interaction_note = (
            "\n本样本有两张参考图：第 1 张是初始页面参考图，第 2 张是交互后的目标状态参考图。"
            "当前生成截图是直接打开生成 HTML 后的静态截图，未执行点击/悬停等动作。"
            "请主要按第 1 张参考图评价静态视觉还原；第 2 张只作为理解页面和交互目标的上下文，"
            "不要因为没有执行交互而直接给 0 分。"
        )

    return f"""你是一个严格但公平的前端视觉还原 benchmark 裁判。

图片顺序：
1. reference_1：目标/参考截图。
2. 如果存在 reference_2：交互后目标状态，仅作为上下文。
3. generated：模型生成 HTML 在浏览器中渲染后的截图。

请比较 generated 和 reference_1 的视觉还原质量，并给出 0-100 分。评分含义：
- 90-100：几乎一致，只存在非常小的字体/间距差异。
- 75-89：整体布局和主要内容正确，局部样式、图片、间距或细节有明显差异。
- 50-74：能看出页面大结构，但多个关键区域缺失、错位或风格不一致。
- 25-49：只还原了少量组件或大致主题，主要布局明显错误。
- 0-24：基本不匹配、空白、严重错页或无法判断。

请从以下维度综合判断：
布局结构、组件层级、文本内容、颜色/背景、字体和字号、间距和对齐、图片/图标占位、整体视觉密度。
{interaction_note}

Benchmark：{item["bench"]}
样本 ID：{item["sample_id"]}
任务类型：{item.get("task_type", "")}

只返回一个 JSON 对象，不要输出 Markdown 或解释性前后缀。JSON schema：
{{
  "score": 0,
  "layout_score": 0,
  "content_score": 0,
  "style_score": 0,
  "asset_score": 0,
  "major_issues": ["中文短语"],
  "minor_issues": ["中文短语"],
  "one_sentence_reason": "中文一句话说明主要扣分原因",
  "confidence": "high|medium|low"
}}
"""


def extract_message(response: dict) -> str:
    content = response["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)


def parse_json_object(text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def clamp_score(value) -> float | None:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(100.0, score))


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "bench",
        "sample_id",
        "task_type",
        "score",
        "layout_score",
        "content_score",
        "style_score",
        "asset_score",
        "confidence",
        "one_sentence_reason",
        "reference_images",
        "generated_image",
        "html_path",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def make_summary(run_dir: Path, out_dir: Path, provider: dict, rows: list[dict], errors: list[dict]) -> dict:
    by_bench = {}
    for row in rows:
        by_bench.setdefault(row["bench"], []).append(row)

    bench_stats = {}
    for bench, bench_rows in by_bench.items():
        scores = [row["score"] for row in bench_rows if isinstance(row.get("score"), (int, float))]
        bench_stats[bench] = {
            "count": len(bench_rows),
            "mean": round(sum(scores) / len(scores), 2) if scores else None,
            "min": min(scores) if scores else None,
            "max": max(scores) if scores else None,
            "low_score_count_lt_60": sum(1 for score in scores if score < 60),
        }

    all_scores = [row["score"] for row in rows if isinstance(row.get("score"), (int, float))]
    return {
        "run_dir": rel(run_dir),
        "judge_dir": rel(out_dir),
        "judge_provider": provider["name"],
        "judge_model": provider["model"],
        "bypass_proxy": provider["bypass_proxy"],
        "scoring_note": "VLM judge visual score; for FullFront interaction samples, generated screenshot is initial static render and reference_2 is interaction context only.",
        "total_scored": len(rows),
        "total_errors": len(errors),
        "overall_mean": round(sum(all_scores) / len(all_scores), 2) if all_scores else None,
        "bench_stats": bench_stats,
        "finished_at": dt.datetime.now().isoformat(timespec="seconds"),
    }


def write_markdown(path: Path, summary: dict, rows: list[dict], errors: list[dict]) -> None:
    lines = [
        "# VLM Judge 视觉评分汇总",
        "",
        f"- 评分模型：{summary['judge_provider']} / {summary['judge_model']}",
        f"- 样本数：{summary['total_scored']}",
        f"- 错误数：{summary['total_errors']}",
        f"- 总平均分：{summary['overall_mean']}",
        f"- 说明：{summary['scoring_note']}",
        "",
        "## 分组统计",
        "",
        "| Benchmark | 样本数 | 平均分 | 最低分 | 最高分 | <60 数量 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for bench, stat in summary["bench_stats"].items():
        lines.append(
            f"| {bench} | {stat['count']} | {stat['mean']} | {stat['min']} | {stat['max']} | {stat['low_score_count_lt_60']} |"
        )

    lines += [
        "",
        "## 逐条结果",
        "",
        "| Benchmark | Sample | Score | 主要原因 | 目标图 | 生成图 |",
        "|---|---|---:|---|---|---|",
    ]
    for row in sorted(rows, key=lambda r: (r["bench"], r["score"], r["sample_id"])):
        reason = str(row.get("one_sentence_reason", "")).replace("|", "/")
        ref = row.get("reference_images", "").split(";")[0]
        lines.append(
            f"| {row['bench']} | {row['sample_id']} | {row['score']} | {reason} | `{ref}` | `{row.get('generated_image', '')}` |"
        )

    if errors:
        lines += ["", "## 错误", ""]
        for err in errors:
            lines.append(f"- {err.get('bench')} / {err.get('sample_id')}: {err.get('error')}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run VLM judge visual scoring on rendered benchmark outputs.")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="qwen")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--benches", nargs="+", default=DEFAULT_BENCHES)
    parser.add_argument("--out-name", default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=20)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Defaults to EXPERIMENT_MAX_TOKENS. Set to 0 to omit max_tokens from the request body.",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    env = load_env(ROOT / ".env")
    provider = resolve_provider(env, args.provider)
    env_max_tokens = parse_optional_int(env.get("EXPERIMENT_MAX_TOKENS"), 0)
    max_tokens = env_max_tokens if args.max_tokens is None else args.max_tokens

    if not args.dry_run and (not provider["api_key"] or not provider["base_url"]):
        print(f"{args.provider} API key or base URL is empty. Fill .env first.", file=sys.stderr)
        return 2
    if not args.dry_run and not provider["supports_image"]:
        print(f"{args.provider} does not support image input in this project config.", file=sys.stderr)
        return 2

    summary = read_summary(run_dir)
    items = make_items(run_dir, summary, args.benches)
    out_name = args.out_name or f"{provider['name']}_{provider['model']}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = run_dir / "vlm_judge" / safe_name(out_name)
    for sub in ["raw", "logs"]:
        (out_dir / sub).mkdir(parents=True, exist_ok=True)

    raw_path = out_dir / "raw" / "responses.jsonl"
    scores_path = out_dir / "scores.jsonl"
    completed = set() if args.force else read_existing_scores(scores_path)

    manifest = {
        "run_dir": rel(run_dir),
        "judge_dir": rel(out_dir),
        "provider": provider["name"],
        "model": provider["model"],
        "bypass_proxy": provider["bypass_proxy"],
        "benches": args.benches,
        "max_tokens": max_tokens if max_tokens > 0 else None,
        "dry_run": args.dry_run,
        "item_count": len(items),
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    (out_dir / "logs" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.dry_run:
        print(json.dumps({**manifest, "items": [
            {
                "bench": item["bench"],
                "sample_id": item["sample_id"],
                "reference_images": [rel(p) for p in item["reference_images"]],
                "generated_image": rel(item["generated_image"]),
            }
            for item in items
        ]}, ensure_ascii=False, indent=2))
        return 0

    rows = []
    errors = []
    if scores_path.exists() and not args.force:
        with scores_path.open("r", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip() and json.loads(line).get("parsed_ok")]

    for index, item in enumerate(items, start=1):
        key = (item["bench"], item["sample_id"])
        if key in completed:
            print(f"[{index}/{len(items)}] skip {item['bench']} {item['sample_id']}", flush=True)
            continue

        content = [{"type": "text", "text": build_prompt(item)}]
        for image_path in item["reference_images"]:
            content.append({"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}})
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(item["generated_image"])}})

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
                "bench": item["bench"],
                "sample_id": item["sample_id"],
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
        print(f"[{index}/{len(items)}] {item['bench']} {item['sample_id']} http={final_record['http_status']}", flush=True)

        if final_record["http_status"] != 200 or not isinstance(final_record["response"], dict):
            err = {
                "bench": item["bench"],
                "sample_id": item["sample_id"],
                "http_status": final_record["http_status"],
                "error": final_record["response"],
            }
            errors.append(err)
            continue

        try:
            message = extract_message(final_record["response"])
            parsed = parse_json_object(message)
            score = clamp_score(parsed.get("score"))
            if score is None:
                raise ValueError("score is missing or non-numeric")
            row = {
                "bench": item["bench"],
                "sample_id": item["sample_id"],
                "task_type": item.get("task_type", ""),
                "score": score,
                "layout_score": clamp_score(parsed.get("layout_score")),
                "content_score": clamp_score(parsed.get("content_score")),
                "style_score": clamp_score(parsed.get("style_score")),
                "asset_score": clamp_score(parsed.get("asset_score")),
                "major_issues": parsed.get("major_issues", []),
                "minor_issues": parsed.get("minor_issues", []),
                "one_sentence_reason": parsed.get("one_sentence_reason", ""),
                "confidence": parsed.get("confidence", ""),
                "reference_images": ";".join(rel(p) for p in item["reference_images"]),
                "generated_image": rel(item["generated_image"]),
                "html_path": rel(item["html_path"]),
                "parsed_ok": True,
            }
            safe_write_jsonl(scores_path, row)
            rows.append(row)
        except Exception as exc:
            err = {
                "bench": item["bench"],
                "sample_id": item["sample_id"],
                "http_status": final_record["http_status"],
                "error": repr(exc),
            }
            errors.append(err)

    error_path = out_dir / "errors.jsonl"
    if errors:
        for err in errors:
            safe_write_jsonl(error_path, err)

    final_summary = make_summary(run_dir, out_dir, provider, rows, errors)
    (out_dir / "summary.json").write_text(json.dumps(final_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(out_dir / "scores.csv", rows)
    write_markdown(out_dir / "summary.md", final_summary, rows, errors)

    print(json.dumps(final_summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
