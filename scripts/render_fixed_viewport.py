import argparse
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def render_one(html_path: Path, output_path: Path, width: int, height: int, full_page: bool) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.wait_for_selector("body")
            page.screenshot(path=str(output_path), full_page=full_page)
        finally:
            browser.close()
    rendered_width, rendered_height = image_size(output_path)
    return {
        "html_path": str(html_path.relative_to(ROOT)),
        "output_path": str(output_path.relative_to(ROOT)),
        "viewport_width": width,
        "viewport_height": height,
        "full_page": full_page,
        "rendered_width": rendered_width,
        "rendered_height": rendered_height,
    }


def load_summary(run_dir: Path) -> dict:
    summary_path = run_dir / "logs" / "summary.json"
    return json.loads(summary_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render generated HTML with viewport fixed to each target image size.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir-name", default="rendered_fixed")
    parser.add_argument("--full-page", action="store_true", help="Capture full page instead of viewport-sized screenshot.")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    summary = load_summary(run_dir)
    records = []
    for item in summary.get("results", []):
        if not item.get("html_path"):
            continue
        html_path = ROOT / item["html_path"]
        target_path = ROOT / item.get("local_image_path", item["image_path"])
        target_width, target_height = image_size(target_path)
        output_path = run_dir / args.output_dir_name / f"{item['id']}.png"
        record = render_one(html_path, output_path, target_width, target_height, args.full_page)
        record.update({
            "id": item["id"],
            "target_path": str(target_path.relative_to(ROOT)),
            "target_width": target_width,
            "target_height": target_height,
        })
        records.append(record)

    log_path = run_dir / "logs" / f"{args.output_dir_name}.json"
    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "rendered": records}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
