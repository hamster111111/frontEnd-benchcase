import argparse
import html
import json
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = ROOT / "experiments" / "random10_bench_smoke" / "mimo_random10_20260604"
DEFAULT_BENCHES = ["visualwebbench", "humaneval_v"]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_") or "sample"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n[TRUNCATED: original length={len(text)} chars]"


def read_text(path: Path | None, limit: int = 6000) -> str:
    if not path or not path.exists():
        return ""
    return truncate(path.read_text(encoding="utf-8", errors="replace"), limit)


def image_size(path: Path) -> tuple[int, int] | None:
    if not path.exists():
        return None
    with Image.open(path) as image:
        return image.size


def iter_results(summary: dict, benches: set[str]):
    for bench, info in summary.get("benches", {}).items():
        if bench not in benches:
            continue
        for item in info.get("results", []):
            if item.get("html_path"):
                continue
            if item.get("text_path") or item.get("code_path"):
                yield bench, item


def metadata_brief(item: dict) -> str:
    metadata = item.get("metadata") or {}
    if not metadata:
        return "无 metadata。"
    keep = {}
    for key in [
        "id",
        "qid",
        "task_type",
        "website",
        "answer",
        "elem_desc",
        "bbox",
        "options",
        "capability_aspects",
        "function_signature",
    ]:
        if key in metadata:
            keep[key] = metadata[key]
    return truncate(json.dumps(keep, ensure_ascii=False, indent=2), 6000)


def image_markup(paths: list[Path]) -> str:
    if not paths:
        return '<p class="empty">无输入图片。</p>'
    blocks = []
    for index, path in enumerate(paths, start=1):
        size = image_size(path)
        size_text = f"{size[0]} x {size[1]}" if size else "size unknown"
        blocks.append(
            f"""
            <figure>
              <figcaption>输入图 {index} · {html.escape(size_text)}</figcaption>
              <img src="{path.resolve().as_uri()}" alt="input image {index}" />
            </figure>
            """
        )
    return "\n".join(blocks)


def build_preview_html(bench: str, item: dict) -> str:
    sample_id = str(item["sample_id"])
    prompt_path = ROOT / item["local_prompt_path"] if item.get("local_prompt_path") else None
    text_path = ROOT / item["text_path"] if item.get("text_path") else None
    code_path = ROOT / item["code_path"] if item.get("code_path") else None
    output_path = code_path if code_path and code_path.exists() else text_path
    output_title = "模型代码输出" if code_path and code_path.exists() else "模型文本输出"
    image_paths = [ROOT / path for path in item.get("local_image_paths", [])]

    prompt = read_text(prompt_path, 5000)
    output = read_text(output_path, 9000)
    metadata = metadata_brief(item)

    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(bench)} / {html.escape(sample_id)} 预览</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4f1ea;
        --panel: #ffffff;
        --ink: #1f242b;
        --muted: #66707c;
        --line: #d7d2c8;
        --accent: #0f766e;
        --accent-2: #b45309;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--ink);
      }}
      main {{
        width: 1280px;
        min-height: 900px;
        padding: 26px;
      }}
      header {{
        display: flex;
        justify-content: space-between;
        gap: 20px;
        align-items: flex-end;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 18px;
      }}
      h1 {{
        margin: 0;
        font-size: 28px;
        line-height: 1.15;
        letter-spacing: 0;
      }}
      .meta {{
        margin: 6px 0 0;
        color: var(--muted);
        font-size: 13px;
      }}
      .badge {{
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 7px 10px;
        color: var(--accent);
        font-weight: 700;
        font-size: 12px;
        white-space: nowrap;
      }}
      .grid {{
        display: grid;
        grid-template-columns: 0.9fr 1.1fr;
        gap: 18px;
        align-items: start;
      }}
      section {{
        min-width: 0;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
      }}
      h2 {{
        margin: 0;
        padding: 12px 14px;
        border-bottom: 1px solid var(--line);
        font-size: 14px;
        line-height: 1.2;
        color: var(--accent-2);
        background: #fbfaf7;
      }}
      .body {{
        padding: 14px;
      }}
      figure {{
        margin: 0 0 12px;
      }}
      figcaption {{
        margin-bottom: 6px;
        color: var(--muted);
        font-size: 12px;
      }}
      img {{
        width: 100%;
        max-height: 520px;
        object-fit: contain;
        border: 1px solid var(--line);
        background: white;
      }}
      pre {{
        margin: 0;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font: 12px/1.55 "Cascadia Mono", Consolas, "SFMono-Regular", monospace;
      }}
      .two-stack {{
        display: grid;
        gap: 18px;
      }}
      .empty {{
        margin: 0;
        color: var(--muted);
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>{html.escape(bench)} / {html.escape(sample_id)}</h1>
          <p class="meta">非 HTML 输出预览渲染：输入图、任务提示、metadata/reference 和模型输出放在同一张图中。</p>
        </div>
        <span class="badge">{html.escape(item.get("task_type", "unknown"))}</span>
      </header>
      <div class="grid">
        <div class="two-stack">
          <section>
            <h2>输入图片</h2>
            <div class="body">{image_markup(image_paths)}</div>
          </section>
          <section>
            <h2>任务提示</h2>
            <div class="body"><pre>{html.escape(prompt)}</pre></div>
          </section>
        </div>
        <div class="two-stack">
          <section>
            <h2>{html.escape(output_title)}</h2>
            <div class="body"><pre>{html.escape(output)}</pre></div>
          </section>
          <section>
            <h2>参考信息 / Metadata</h2>
            <div class="body"><pre>{html.escape(metadata)}</pre></div>
          </section>
        </div>
      </div>
    </main>
  </body>
</html>
"""


def render_preview(browser, html_path: Path, output_path: Path, width: int, height: int) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page = browser.new_page(viewport={"width": width, "height": height})
    try:
        page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=30000)
        page.wait_for_selector("body", timeout=10000)
        page.wait_for_timeout(300)
        page.screenshot(path=str(output_path), full_page=True)
    finally:
        page.close()
    with Image.open(output_path) as image:
        rendered_width, rendered_height = image.size
    return {
        "output_path": rel(output_path),
        "preview_html_path": rel(html_path),
        "rendered_width": rendered_width,
        "rendered_height": rendered_height,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render text/code benchmark outputs into preview screenshots.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--benches", nargs="+", default=DEFAULT_BENCHES)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    benches = set(args.benches)
    records = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        try:
            for bench, item in iter_results(summary, benches):
                sample_id = safe_name(item["sample_id"])
                bench_dir = run_dir / bench
                preview_html_path = bench_dir / "preview_html" / f"{sample_id}.html"
                output_path = bench_dir / "rendered_fixed" / f"{sample_id}.png"
                record = {
                    "bench": bench,
                    "sample_id": item["sample_id"],
                    "task_type": item.get("task_type", ""),
                    "source_kind": "code" if item.get("code_path") else "text",
                }
                try:
                    preview_html_path.parent.mkdir(parents=True, exist_ok=True)
                    preview_html_path.write_text(build_preview_html(bench, item), encoding="utf-8")
                    record.update(render_preview(browser, preview_html_path, output_path, args.width, args.height))
                    record["status"] = "rendered"
                except Exception as exc:
                    record["status"] = "render_error"
                    record["error"] = f"{type(exc).__name__}: {exc}"
                records.append(record)
                print(json.dumps({"bench": bench, "sample_id": item["sample_id"], "status": record["status"]}, ensure_ascii=False), flush=True)
        finally:
            browser.close()

    log_path = run_dir / "nonhtml_rendered_previews.json"
    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    by_bench = {}
    for record in records:
        bucket = by_bench.setdefault(record["bench"], {"rendered": 0, "errors": 0})
        if record["status"] == "rendered":
            bucket["rendered"] += 1
        else:
            bucket["errors"] += 1

    md_lines = [
        "# Non-HTML Rendered Preview Summary",
        "",
        f"- run_dir: `{run_dir.relative_to(ROOT)}`",
        f"- benches: `{', '.join(args.benches)}`",
        "",
        "| bench | rendered previews | errors |",
        "|---|---:|---:|",
    ]
    for bench, info in by_bench.items():
        md_lines.append(f"| {bench} | {info['rendered']} | {info['errors']} |")
    (run_dir / "nonhtml_rendered_previews.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({"run_dir": rel(run_dir), "log": rel(log_path), "by_bench": by_bench}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
