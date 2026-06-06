import argparse
import json
from pathlib import Path

from glm5v_smoke import ROOT, html_looks_complete


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild logs/summary.json for an interrupted smoke run.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--provider", default="qwen")
    parser.add_argument("--model", default="qwen3-vl-plus")
    parser.add_argument("--dataset-jsonl", default="benchmarks\\ui2code_n\\evaluation\\data\\UI2Code-Real\\data.jsonl")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    inputs = read_jsonl(run_dir / "inputs" / "selected_samples.jsonl")
    raw = read_jsonl(run_dir / "raw" / "responses.jsonl")
    raw_by_id = {str(item["id"]): item for item in raw}
    results = []
    for item in inputs:
        item_id = str(item["id"])
        result = dict(item)
        raw_record = raw_by_id.get(item_id)
        if raw_record:
            result["http_status"] = raw_record.get("http_status")
            response = raw_record.get("response")
            html_path = run_dir / "html" / f"{item_id}.html"
            if result["http_status"] == 200 and html_path.exists():
                html = html_path.read_text(encoding="utf-8")
                result["usage"] = response.get("usage") if isinstance(response, dict) else None
                result["html_extracted"] = True
                result["html_complete"] = html_looks_complete(html)
                result["html_path"] = str(html_path.relative_to(ROOT))
            else:
                result["error"] = response
        else:
            result["status"] = "missing_raw_response"
        results.append(result)

    summary = {
        "run_dir": str(run_dir.relative_to(ROOT)),
        "dataset_jsonl": args.dataset_jsonl,
        "provider": args.provider,
        "model": args.model,
        "base_url": "",
        "supports_image": True,
        "dry_run": False,
        "sample_count": len(results),
        "started_at": "",
        "finished_at": "",
        "results": results,
        "rebuilt": True,
    }
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Rebuilt Smoke Test Summary",
        "",
        f"- run_dir: `{summary['run_dir']}`",
        f"- provider: `{args.provider}`",
        f"- model: `{args.model}`",
        f"- samples: `{len(results)}`",
        "",
        "| id | status | html | usage / error |",
        "|---:|---:|---:|---|",
    ]
    for item in results:
        status = item.get("http_status", item.get("status", ""))
        html = item.get("html_extracted", "")
        if html and "html_complete" in item:
            html = f"{html} / complete={item['html_complete']}"
        detail = item.get("usage") or item.get("error") or ""
        detail_text = json.dumps(detail, ensure_ascii=False)[:180].replace("|", "\\|")
        lines.append(f"| {item['id']} | {status} | {html} | `{detail_text}` |")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(run_dir / "logs" / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
