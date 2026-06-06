from __future__ import annotations

import argparse
import json
import shutil
import tarfile
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SMOKE_DIR = ROOT / "experiments/random10_bench_smoke/mimo_random10_20260604/vision2web"
DEFAULT_OUT_DIR = ROOT / "experiments/vision2web_official_eval/mimo_random10_20260604"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def extract_project_from_archive(tar: tarfile.TarFile, task_name: str, datasets_root: Path) -> None:
    prefix = f"webpage/{task_name}/"
    members = [member for member in tar.getmembers() if member.name.startswith(prefix)]
    if not members:
        raise FileNotFoundError(f"Project not found in archive: {task_name}")
    datasets_root.mkdir(parents=True, exist_ok=True)
    tar.extractall(path=datasets_root, members=members)


def copy_result_project(smoke_dir: Path, out_dir: Path, item: dict, framework: str, model: str) -> None:
    task_name = item["sample_id"]
    result_dir = out_dir / "results" / "webpage" / framework / model / task_name
    result_dir.mkdir(parents=True, exist_ok=True)

    html_src = smoke_dir / "html" / f"{task_name}.html"
    if not html_src.exists():
        raise FileNotFoundError(f"Missing generated HTML: {html_src}")
    shutil.copy2(html_src, result_dir / "index.html")

    dataset_project = out_dir / "datasets" / "webpage" / task_name
    for child in ["prototypes", "resources"]:
        src = dataset_project / child
        dst = result_dir / child
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    (result_dir / "start.sh").write_text(
        "#!/usr/bin/env bash\n"
        "set -e\n"
        "cd /workspace\n"
        "python3 -m http.server 3000 --bind 0.0.0.0\n",
        encoding="utf-8",
        newline="\n",
    )

    (result_dir / "README.md").write_text(
        f"# Vision2Web smoke result: {task_name}\n\n"
        "This project wraps the single-file HTML generated in the random-10 smoke run "
        "so the official Vision2Web evaluator can launch it via `bash /workspace/start.sh`.\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-dir", type=Path, default=DEFAULT_SMOKE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--framework", default="smoke_html")
    parser.add_argument("--model", default="mimo-v2.5")
    args = parser.parse_args()

    smoke_dir = args.smoke_dir.resolve()
    out_dir = args.out_dir.resolve()
    selected_path = smoke_dir / "inputs" / "selected_samples.jsonl"
    samples = read_jsonl(selected_path)

    archive_path = Path(
        hf_hub_download(
            repo_id="zai-org/Vision2Web",
            repo_type="dataset",
            filename="archives/webpage.tar.gz",
        )
    )

    datasets_root = out_dir / "datasets"
    datasets_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as tar:
        for item in samples:
            extract_project_from_archive(tar, item["sample_id"], datasets_root)

    for item in samples:
        copy_result_project(smoke_dir, out_dir, item, args.framework, args.model)

    manifest = {
        "source_smoke_dir": str(smoke_dir),
        "archive_path": str(archive_path),
        "out_dir": str(out_dir),
        "framework": args.framework,
        "model": args.model,
        "task": "webpage",
        "count": len(samples),
        "projects": [item["sample_id"] for item in samples],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
