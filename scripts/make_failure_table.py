import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

FAILURE_COLUMNS = [
    "布局结构",
    "组件完整性",
    "文字还原",
    "颜色/视觉密度",
    "尺寸/间距",
    "图片/icon",
    "幻觉元素",
    "viewport/溢出",
    "备注",
]


def image_size(path: Path) -> tuple[int | None, int | None]:
    if not path.exists():
        return None, None
    with Image.open(path) as image:
        return image.size


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Chinese manual failure table template for a smoke run.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--render-dir-name", default="rendered_fixed")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    run_dir = args.run_dir
    summary = read_json(run_dir / "logs" / "summary.json", {})
    render_records = read_json(run_dir / "logs" / f"{args.render_dir_name}.json", [])
    render_by_id = {str(item["id"]): item for item in render_records}

    output = args.output or run_dir / "failure_table.md"
    lines = [
        f"# {run_dir.name} 痛点标注表",
        "",
        "这张表用于人工快速标注 direct baseline 的失败类型。建议先只填 `高/中/低/无`，备注写最明显的 1-2 个问题。",
        "",
        "## 自动检查",
        "",
        "| id | API | HTML | 目标尺寸 | 渲染尺寸 | 输入图 | 渲染图 | HTML |",
        "|---:|---:|---:|---:|---:|---|---|---|",
    ]

    for item in summary.get("results", []):
        item_id = str(item["id"])
        target_path = ROOT / item.get("local_image_path", item.get("image_path", ""))
        target_width, target_height = image_size(target_path)
        render_record = render_by_id.get(item_id, {})
        rendered_path = ROOT / render_record.get("output_path", "")
        rendered_width, rendered_height = image_size(rendered_path) if rendered_path != ROOT else (None, None)
        status = item.get("http_status", item.get("status", ""))
        html_state = "完整" if item.get("html_complete") else ("已提取" if item.get("html_extracted") else "无")
        input_link = item.get("local_image_path", item.get("image_path", ""))
        html_link = item.get("html_path", "")
        rendered_link = render_record.get("output_path", "")
        lines.append(
            f"| {item_id} | {status} | {html_state} | {target_width}x{target_height} | "
            f"{rendered_width}x{rendered_height} | `{input_link}` | `{rendered_link}` | `{html_link}` |"
        )

    lines.extend([
        "",
        "## 人工失败类型",
        "",
        "| id | " + " | ".join(FAILURE_COLUMNS) + " |",
        "|---:|" + "|".join(["---"] * len(FAILURE_COLUMNS)) + "|",
    ])
    for item in summary.get("results", []):
        cells = ["待标注"] * len(FAILURE_COLUMNS)
        lines.append(f"| {item['id']} | " + " | ".join(cells) + " |")

    lines.extend([
        "",
        "## 标注口径",
        "",
        "- `布局结构`：主体区域、左右栏、header/footer、浮动盒子位置是否正确。",
        "- `组件完整性`：按钮、输入框、表格、卡片、导航、列表等是否缺失或多出。",
        "- `文字还原`：关键标题、文本内容、字号、字重、换行是否接近。",
        "- `颜色/视觉密度`：主色、灰阶、边框、背景、元素密集程度是否接近。",
        "- `尺寸/间距`：宽高、padding、margin、行高、元素之间距离是否接近。",
        "- `图片/icon`：logo、头像、图标、插图是否相似，是否被错误替代。",
        "- `幻觉元素`：是否出现目标图不存在的 bullet、导航、卡片、文字等。",
        "- `viewport/溢出`：是否超过目标高度、横向溢出、滚动区域异常。",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
