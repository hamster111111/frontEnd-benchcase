import argparse
import json
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def iter_results(summary: dict):
    for bench, info in summary.get("benches", {}).items():
        for item in info.get("results", []):
            yield bench, item


def render_page(browser, html_path: Path, output_path: Path, width: int, height: int, full_page: bool) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page = browser.new_page(viewport={"width": width, "height": height})
    try:
        page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=30000)
        page.wait_for_selector("body", timeout=10000)
        page.wait_for_timeout(500)
        page.screenshot(path=str(output_path), full_page=full_page)
    finally:
        page.close()
    rendered_width, rendered_height = image_size(output_path)
    return {
        "output_path": str(output_path.relative_to(ROOT)),
        "viewport_width": width,
        "viewport_height": height,
        "full_page": full_page,
        "rendered_width": rendered_width,
        "rendered_height": rendered_height,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render generated HTML outputs for random multi-bench smoke runs.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir-name", default="rendered_fixed")
    parser.add_argument("--full-page", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    summary_path = run_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        try:
            for bench, item in iter_results(summary):
                html_rel = item.get("html_path")
                image_rels = item.get("local_image_paths") or []
                if not html_rel or not image_rels:
                    continue
                html_path = ROOT / html_rel
                target_path = ROOT / image_rels[0]
                output_path = run_dir / bench / args.output_dir_name / f"{safe_name(str(item['sample_id']))}.png"
                record = {
                    "bench": bench,
                    "sample_id": item["sample_id"],
                    "html_path": str(html_path.relative_to(ROOT)),
                    "target_path": str(target_path.relative_to(ROOT)),
                }
                try:
                    width, height = image_size(target_path)
                    record.update({"target_width": width, "target_height": height})
                    record.update(render_page(browser, html_path, output_path, width, height, args.full_page))
                    record["status"] = "rendered"
                except Exception as exc:
                    record["status"] = "render_error"
                    record["error"] = f"{type(exc).__name__}: {exc}"
                records.append(record)
                print(json.dumps({"bench": bench, "sample_id": item["sample_id"], "status": record["status"]}, ensure_ascii=False), flush=True)
        finally:
            browser.close()

    log_path = run_dir / f"{args.output_dir_name}.json"
    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    by_bench = {}
    for record in records:
        info = by_bench.setdefault(record["bench"], {"rendered": 0, "errors": 0})
        if record["status"] == "rendered":
            info["rendered"] += 1
        else:
            info["errors"] += 1

    md_lines = [
        "# Render Summary",
        "",
        f"- run_dir: `{run_dir.relative_to(ROOT)}`",
        f"- output_dir_name: `{args.output_dir_name}`",
        f"- full_page: `{args.full_page}`",
        "",
        "| bench | rendered | errors |",
        "|---|---:|---:|",
    ]
    for bench, info in by_bench.items():
        md_lines.append(f"| {bench} | {info['rendered']} | {info['errors']} |")
    (run_dir / f"{args.output_dir_name}.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "render_log": str(log_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
