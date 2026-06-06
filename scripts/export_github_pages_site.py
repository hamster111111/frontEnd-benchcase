from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs"
WEB_DIR = ROOT / "web"
DATA_DIR = ROOT / "data"
BOARD_DATA = DATA_DIR / "benchmark_run_board.json"
RANDOM10_RUN_DIR = ROOT / "experiments/random10_bench_smoke/mimo_random10_20260604"
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


def copy_random10_experiment() -> tuple[int, int]:
    if not RANDOM10_RUN_DIR.exists():
        return 0, 0
    dst = OUT_DIR / "experiments/random10_bench_smoke/mimo_random10_20260604"
    reset_path(dst)
    shutil.copytree(RANDOM10_RUN_DIR, dst)
    files = [path for path in dst.rglob("*") if path.is_file()]
    return len(files), sum(path.stat().st_size for path in files)


def write_entry_page() -> None:
    (OUT_DIR / "index.html").write_text(
        """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>前端 Benchmark 资料入口</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f6f7fb;
        --panel: #ffffff;
        --text: #172033;
        --muted: #647084;
        --line: #d9dfeb;
        --accent: #2457d6;
      }
      * {
        box-sizing: border-box;
      }
      body {
        margin: 0;
        min-height: 100vh;
        background: var(--bg);
        color: var(--text);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      main {
        width: min(980px, calc(100% - 40px));
        margin: 0 auto;
        padding: 56px 0;
      }
      .eyebrow {
        margin: 0 0 8px;
        color: var(--muted);
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0;
      }
      h1 {
        margin: 0;
        font-size: 32px;
        line-height: 1.2;
      }
      .lead {
        margin: 14px 0 28px;
        max-width: 680px;
        color: var(--muted);
        line-height: 1.7;
      }
      .entry-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }
      .entry {
        min-height: 190px;
        padding: 22px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        color: inherit;
        text-decoration: none;
      }
      .entry:hover {
        border-color: var(--accent);
      }
      .entry h2 {
        margin: 0 0 10px;
        font-size: 22px;
      }
      .entry p {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
      }
      .entry span {
        margin-top: 24px;
        color: var(--accent);
        font-weight: 700;
      }
      @media (max-width: 720px) {
        main {
          width: min(100% - 24px, 980px);
          padding: 32px 0;
        }
        .entry-grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <p class="eyebrow">前端设计评测</p>
      <h1>Benchmark 资料入口</h1>
      <p class="lead">这里保留两类页面：一个是调研阶段收集的 benchmark / framework / 模型资料库，一个是我们已经跑过的实验看板。</p>
      <section class="entry-grid" aria-label="页面入口">
        <a class="entry" href="./web/index.html">
          <div>
            <h2>Benchmark 资料库</h2>
            <p>整理 Zhipu / GLM、其他模型、可跑 framework、评分方式、论文信息和调研来源。</p>
          </div>
          <span>打开资料库</span>
        </a>
        <a class="entry" href="./web/benchmark-board.html">
          <div>
            <h2>已跑 Benchmark 看板</h2>
            <p>展示 random-10 smoke run、VLM judge 分数、低分样例和已跑实验进度。</p>
          </div>
          <span>打开看板</span>
        </a>
      </section>
    </main>
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
    random10_files, random10_bytes = copy_random10_experiment()
    copy_official_eval_summaries()
    write_entry_page()
    write_nojekyll()

    total_size = sum(path.stat().st_size for path in OUT_DIR.rglob("*") if path.is_file())
    manifest = {
        "siteDir": str(OUT_DIR.relative_to(ROOT)),
        "webFiles": len(list((OUT_DIR / "web").rglob("*"))),
        "dataFiles": len(list((OUT_DIR / "data").rglob("*"))),
        "boardAssets": len(assets),
        "random10ExperimentFiles": random10_files,
        "random10ExperimentBytes": random10_bytes,
        "totalBytes": total_size,
    }
    (OUT_DIR / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
