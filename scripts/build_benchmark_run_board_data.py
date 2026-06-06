import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "experiments" / "random10_bench_smoke" / "mimo_random10_20260604"
JUDGE_DIR = RUN_DIR / "vlm_judge" / "qwen3-vl-plus_visual_judge_20260604"
OUT_PATH = ROOT / "data" / "benchmark_run_board.json"


BENCH_META = {
    "design2code": {
        "name": "Design2Code",
        "family": "视觉还原",
        "task": "UI 截图/设计图生成前端页面",
        "input": "参考网页截图 + 可选文本提示",
        "output": "HTML/CSS/渲染网页",
        "officialScoring": "渲染后用 VLM judge 或视觉相似度比较目标图和生成图。",
        "nextScoring": "已跑 VLM judge；后续可补 CLIP/SSIM 或官方 UI2Code_N evaluator。",
        "lossFocus": "主题色、导航/边栏背景、CTA/tag/分享组件等局部样式。",
        "priority": "高",
    },
    "flame": {
        "name": "Flame",
        "family": "React/UI 生成",
        "task": "根据 UI 目标生成 React/前端界面",
        "input": "UI 截图或多模态提示",
        "output": "前端代码/渲染 UI",
        "officialScoring": "通常看 VLM-Code 分、可运行性和视觉还原。",
        "nextScoring": "已跑 VLM judge；后续可补组件可运行检查和细粒度样式指标。",
        "lossFocus": "表单控件、状态文本、按钮对齐、spacing、图表比例。",
        "priority": "高",
    },
    "ui2code_real": {
        "name": "UI2Code-Real",
        "family": "真实网页 UI 转代码",
        "task": "真实网页截图生成前端页面",
        "input": "真实网页截图",
        "output": "HTML/CSS/渲染网页",
        "officialScoring": "渲染截图与目标截图做 VLM/视觉相似度评审。",
        "nextScoring": "补 VLM judge，优先看真实网页细节还原。",
        "lossFocus": "真实网页复杂布局、图片/图标资产、响应式比例。",
        "priority": "高",
    },
    "uipolish_real": {
        "name": "UIPolish-Real",
        "family": "UI 润色",
        "task": "根据目标 UI 改进页面视觉质量",
        "input": "目标 UI；正式协议还应包含当前代码/当前渲染",
        "output": "改进后的前端页面",
        "officialScoring": "比较改进前后是否更接近目标，常用准确率或 VLM preference。",
        "nextScoring": "本轮只有 direct smoke；需补当前渲染/代码后再做闭环评估。",
        "lossFocus": "反馈闭环缺失时容易变成一次性生成，不是真正 polish。",
        "priority": "中",
    },
    "uipolish_synthetic": {
        "name": "UIPolish-Synthetic",
        "family": "UI 润色",
        "task": "合成 UI 润色/修复",
        "input": "目标 UI；正式协议还应包含当前代码/当前渲染",
        "output": "改进后的前端页面",
        "officialScoring": "比较改进结果是否更接近高质量目标。",
        "nextScoring": "需要按官方 repair 输入重跑，否则只能作为 direct 生成参考。",
        "lossFocus": "缺少错误页面上下文，难以定位局部修复点。",
        "priority": "中",
    },
    "web2code": {
        "name": "Web2Code",
        "family": "网页截图转代码",
        "task": "网页截图生成前端代码",
        "input": "网页截图",
        "output": "HTML/CSS/渲染网页",
        "officialScoring": "视觉还原为主，可用 VLM judge、CLIP、SSIM 或结构指标。",
        "nextScoring": "补 VLM judge 和 CLIP/SSIM；适合观察长尾网页组件。",
        "lossFocus": "网页细节、图片替代、布局比例、长页面截断。",
        "priority": "高",
    },
    "dcgen_original": {
        "name": "DCGen Original",
        "family": "视觉相似度",
        "task": "网页截图生成 HTML",
        "input": "目标网页截图",
        "output": "HTML/CSS/渲染网页",
        "officialScoring": "渲染图与目标图做 SSIM/视觉相似度和细粒度指标。",
        "nextScoring": "优先补 SSIM；VLM judge 可作为辅助。",
        "lossFocus": "像素级位置、图像/颜色匹配、细粒度区域相似度。",
        "priority": "中",
    },
    "interaction2code": {
        "name": "Interaction2Code",
        "family": "交互生成",
        "task": "根据交互前/后截图生成可交互页面",
        "input": "交互前截图 + 交互后截图 + 动作描述",
        "output": "可交互 HTML",
        "officialScoring": "CLIP、SSIM、Text、Position、Implement Rate，分静态态和交互态。",
        "nextScoring": "需要执行交互后截图，再评初始态/交互态。",
        "lossFocus": "交互触发元素、状态切换、交互后布局是否达到目标。",
        "priority": "高",
    },
    "designbench": {
        "name": "DesignBench",
        "family": "多框架前端",
        "task": "生成/编辑/修复 React、Vue、Angular、Vanilla 页面",
        "input": "截图、设计描述、编辑/修复指令",
        "output": "多框架前端代码",
        "officialScoring": "编译成功、AST/code-level、视觉相似度和 LLM/VLM judge。",
        "nextScoring": "先跑 vanilla visual judge；再评编译/AST 指标。",
        "lossFocus": "跨框架可运行性、编译错误、视觉细节和代码结构。",
        "priority": "高",
    },
    "fullfront": {
        "name": "FullFront",
        "family": "视觉到前端",
        "task": "图像/文本/交互 authoring 生成完整前端",
        "input": "截图、文本描述或交互前后截图",
        "output": "HTML/CSS/JS",
        "officialScoring": "CLIP 图像相似度、代码结构/内容相似度和 Gemini/VLM judge。",
        "nextScoring": "已跑静态 VLM judge；交互样本需补 click/hover 后截图。",
        "lossFocus": "真实图片、logo、产品图、hero 背景、品牌视觉一致性。",
        "priority": "高",
    },
    "screencoder_screenbench": {
        "name": "ScreenCoder / ScreenBench",
        "family": "屏幕到代码",
        "task": "根据网页/屏幕截图生成 HTML",
        "input": "屏幕截图",
        "output": "HTML/CSS/渲染网页",
        "officialScoring": "官方 scorer 不如 FullFront 明确；通常可做渲染视觉/代码相似度。",
        "nextScoring": "补 VLM judge + HTML 结构相似度。",
        "lossFocus": "页面结构、细节资产、长尾布局。",
        "priority": "中",
    },
    "vision2web": {
        "name": "Vision2Web",
        "family": "网站开发",
        "task": "从视觉原型到静态/交互/全栈网站",
        "input": "原型/截图 + 任务规格 + 环境上下文",
        "output": "静态网页、交互前端或全栈网站",
        "officialScoring": "Level 1 用 Visual Score；Level 2/3 加 Functional Score。",
        "nextScoring": "先对 Level 1 补 VLM visual judge；交互/全栈需 GUI agent 验证。",
        "lossFocus": "从静态视觉还原扩展到功能流程和多页面工作流。",
        "priority": "高",
    },
    "visualwebbench": {
        "name": "VisualWebBench",
        "family": "网页理解",
        "task": "网页 caption、OCR、grounding、QA、action prediction",
        "input": "网页截图/元素/问题",
        "output": "文本答案、坐标或动作",
        "officialScoring": "ROUGE/F1/accuracy，按任务类型切换。",
        "nextScoring": "直接跑官方 eval_utils；不需要视觉生成 judge。",
        "lossFocus": "网页理解和 grounding，不是前端视觉生成。",
        "priority": "中",
    },
    "humaneval_v": {
        "name": "HumanEval-V",
        "family": "视觉编程",
        "task": "根据视觉题面生成可执行代码",
        "input": "视觉题面/图像 + 编程任务",
        "output": "Python 代码",
        "officialScoring": "parse success 和 pass@k。",
        "nextScoring": "补执行 harness，统计 pass@1。",
        "lossFocus": "代码正确性，和视觉设计还原关系较弱。",
        "priority": "中",
    },
    "vab_css": {
        "name": "VAB-CSS",
        "family": "CSS Agent 修复",
        "task": "通过多轮 CSS edit 修复错误页面",
        "input": "目标图、当前错误页面、HTML/CSS、差异描述",
        "output": "CSS 修改动作和最终渲染",
        "officialScoring": "成功率/EM，内部用 SSIM 距离改善判断。",
        "nextScoring": "缺官方 data/css_dataset，需补数据后跑 agent 环境。",
        "lossFocus": "闭环局部修复、动作选择、SSIM 改善。",
        "priority": "高",
    },
    "frontendbench": {
        "name": "FrontendBench",
        "family": "前端综合",
        "task": "待确认",
        "input": "官方数据暂未落地",
        "output": "待确认",
        "officialScoring": "官方代码/数据未获取，暂不硬填。",
        "nextScoring": "等官方 data/code 可用后再纳入。",
        "lossFocus": "待确认。",
        "priority": "低",
    },
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def count_outputs(results: list[dict]) -> dict:
    ok = [row for row in results if row.get("http_status") == 200]
    html = [row for row in ok if row.get("html_path")]
    code = [row for row in ok if row.get("code_path")]
    text = [row for row in ok if row.get("text_path") and not row.get("html_path")]
    complete = [row for row in html if row.get("html_complete")]
    return {
        "selected": len(results),
        "ok": len(ok),
        "html": len(html),
        "complete": len(complete),
        "code": len(code),
        "text": len(text),
        "failed": len(results) - len(ok),
    }


def render_count(bench: str) -> int:
    path = RUN_DIR / bench / "rendered_fixed"
    if not path.exists():
        return 0
    return len(list(path.glob("*.png")))


def status_label(item: dict) -> str:
    if item.get("skipped"):
        return "未跑通"
    if item["counts"]["selected"] and item["counts"]["failed"] == 0:
        return "已跑 smoke"
    if item["counts"]["selected"]:
        return "部分失败"
    return "待处理"


def phase_flags(item: dict) -> dict:
    counts = item["counts"]
    judged = bool(item.get("judge"))
    return {
        "data": counts["selected"] > 0 or item.get("skipped"),
        "smoke": counts["selected"] > 0 and counts["failed"] == 0,
        "render": item.get("rendered", 0) > 0,
        "vlmJudge": judged,
        "officialScore": False,
    }


def main() -> int:
    summary = read_json(RUN_DIR / "summary.json")
    judge_summary = read_json(JUDGE_DIR / "summary.json") if (JUDGE_DIR / "summary.json").exists() else {}
    judge_rows = read_jsonl(JUDGE_DIR / "scores.jsonl")
    judge_by_bench: dict[str, list[dict]] = {}
    for row in judge_rows:
        judge_by_bench.setdefault(row["bench"], []).append(row)

    benchmarks = []
    for bench, bench_info in summary.get("benches", {}).items():
        meta = BENCH_META.get(bench, {"name": bench, "family": "未分类"})
        counts = count_outputs(bench_info.get("results", []))
        item = {
            "id": bench,
            **meta,
            "available": bench_info.get("available"),
            "counts": counts,
            "rendered": render_count(bench),
            "skipped": False,
        }
        rows = judge_by_bench.get(bench, [])
        if rows:
            scores = [row["score"] for row in rows if isinstance(row.get("score"), (int, float))]
            low_cases = sorted(rows, key=lambda row: row["score"])[:3]
            issue_terms = Counter()
            for row in rows:
                for issue in (row.get("major_issues") or []) + (row.get("minor_issues") or []):
                    issue_terms[str(issue)] += 1
            item["judge"] = {
                "model": f"{judge_summary.get('judge_provider', 'qwen')} / {judge_summary.get('judge_model', 'qwen3-vl-plus')}",
                "count": len(rows),
                "mean": round(sum(scores) / len(scores), 2) if scores else None,
                "min": min(scores) if scores else None,
                "max": max(scores) if scores else None,
                "lowCases": [
                    {
                        "sampleId": row["sample_id"],
                        "score": row["score"],
                        "reason": row.get("one_sentence_reason", ""),
                        "target": row.get("reference_images", "").split(";")[0],
                        "generated": row.get("generated_image", ""),
                    }
                    for row in low_cases
                ],
                "issueTerms": [term for term, _ in issue_terms.most_common(5)],
            }
        item["status"] = status_label(item)
        item["phases"] = phase_flags(item)
        benchmarks.append(item)

    skipped = []
    for bench in ["vab_css", "frontendbench"]:
        status_path = RUN_DIR / bench / "status.md"
        reason = status_path.read_text(encoding="utf-8").strip() if status_path.exists() else BENCH_META[bench]["nextScoring"]
        item = {
            "id": bench,
            **BENCH_META[bench],
            "available": None,
            "counts": {"selected": 0, "ok": 0, "html": 0, "complete": 0, "code": 0, "text": 0, "failed": 0},
            "rendered": 0,
            "skipped": True,
            "skipReason": reason,
        }
        item["status"] = status_label(item)
        item["phases"] = phase_flags(item)
        skipped.append(item)

    benchmarks.extend(skipped)
    total_selected = sum(item["counts"]["selected"] for item in benchmarks)
    total_ok = sum(item["counts"]["ok"] for item in benchmarks)
    total_rendered = sum(item["rendered"] for item in benchmarks)
    total_judged = sum(item.get("judge", {}).get("count", 0) for item in benchmarks)

    data = {
        "schemaVersion": "1.0",
        "updatedAt": "2026-06-04",
        "title": "已跑 Benchmark 看板",
        "run": {
            "dir": str(RUN_DIR.relative_to(ROOT)),
            "provider": summary.get("provider"),
            "model": summary.get("model"),
            "sampleSizePerBench": summary.get("sample_size_per_bench"),
            "seed": summary.get("seed"),
            "maxTokens": summary.get("max_tokens"),
            "bypassProxy": summary.get("bypass_proxy"),
            "startedAt": summary.get("started_at"),
        },
        "judge": {
            "dir": str(JUDGE_DIR.relative_to(ROOT)),
            "provider": judge_summary.get("judge_provider"),
            "model": judge_summary.get("judge_model"),
            "overallMean": judge_summary.get("overall_mean"),
            "totalScored": judge_summary.get("total_scored", 0),
            "note": judge_summary.get("scoring_note"),
        },
        "totals": {
            "benchmarks": len(benchmarks),
            "smokeBenches": sum(1 for item in benchmarks if item["counts"]["selected"] > 0),
            "skipped": sum(1 for item in benchmarks if item.get("skipped")),
            "selectedSamples": total_selected,
            "okSamples": total_ok,
            "renderedImages": total_rendered,
            "vlmJudgedSamples": total_judged,
        },
        "benchmarks": benchmarks,
        "boardNotes": [
            "本看板展示我们已跑的 smoke run，不等于官方 benchmark 分数。",
            "VLM judge 目前只覆盖 design2code、flame、fullfront 三组。",
            "FullFront interaction 样本当前只评初始静态渲染图，尚未执行 click/hover 后截图。",
        ],
    }

    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
