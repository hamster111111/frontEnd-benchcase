from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs"
WEB_DIR = ROOT / "web"
DATA_DIR = ROOT / "data"
BOARD_DATA = DATA_DIR / "benchmark_run_board.json"
OFFICIAL_VISION2WEB_DIR = ROOT / "experiments/vision2web_official_eval/mimo_random10_20260604"


def reset_path(path: Path) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    out_root = OUT_DIR.resolve()
    if resolved == out_root or out_root not in resolved.parents:
        raise RuntimeError(f"Refusing to remove path outside docs/: {resolved}")
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    reset_path(dst)
    shutil.copytree(src, dst)


def collect_board_assets() -> list[Path]:
    data = json.loads(BOARD_DATA.read_text(encoding="utf-8"))
    rel_paths: set[str] = set()
    for bench in data.get("benchmarks", []):
        for item in (bench.get("judge") or {}).get("lowCases", []) or []:
            for key in ("target", "generated"):
                value = item.get(key)
                if value:
                    rel_paths.add(value.replace("\\", "/"))

    assets: list[Path] = []
    for rel in sorted(rel_paths):
        path = ROOT / rel
        if path.exists() and path.is_file():
            assets.append(path)
        else:
            print(f"WARNING missing asset: {rel}")
    return assets


def copy_assets(paths: list[Path]) -> None:
    for src in paths:
        rel = src.relative_to(ROOT)
        dst = OUT_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_official_eval_summaries() -> None:
    if not OFFICIAL_VISION2WEB_DIR.exists():
        return
    files = [
        "analysis.json",
        "official_l1_scores.csv",
        "official_l1_summary.md",
        "manifest.json",
    ]
    for name in files:
        src = OFFICIAL_VISION2WEB_DIR / name
        if not src.exists():
            continue
        dst = OUT_DIR / "experiments/vision2web_official_eval/mimo_random10_20260604" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_entry_page() -> None:
    (OUT_DIR / "index.html").write_text(
        """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="refresh" content="0; url=./web/benchmark-board.html" />
    <title>前端 Benchmark 看板</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #172033; }
      a { color: #2457d6; }
    </style>
  </head>
  <body>
    <p>正在打开 <a href="./web/benchmark-board.html">前端 Benchmark 看板</a>。</p>
  </body>
</html>
""",
        encoding="utf-8",
        newline="\n",
    )


def write_nojekyll() -> None:
    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    copytree(WEB_DIR, OUT_DIR / "web")
    copytree(DATA_DIR, OUT_DIR / "data")

    reset_path(OUT_DIR / "experiments/random10_bench_smoke")
    assets = collect_board_assets()
    copy_assets(assets)
    copy_official_eval_summaries()
    write_entry_page()
    write_nojekyll()

    total_size = sum(path.stat().st_size for path in OUT_DIR.rglob("*") if path.is_file())
    manifest = {
        "siteDir": str(OUT_DIR.relative_to(ROOT)),
        "webFiles": len(list((OUT_DIR / "web").rglob("*"))),
        "dataFiles": len(list((OUT_DIR / "data").rglob("*"))),
        "boardAssets": len(assets),
        "totalBytes": total_size,
    }
    (OUT_DIR / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
