# 后续调研清单

最后更新：2026-06-02

## 最高优先级

1. 核对 GLM-5V-Turbo 在 `Design2Code` 上的具体评测协议。
2. 核对 GLM-5V 报告里的 `Flame-VLM-Code` 是否严格对应原论文中的 `Flame-React-Eval`，还是另一个 FLAME evaluation split。
3. 持续关注 `Vision2Web` 是否公开包含 GLM-5V-Turbo 的 leaderboard。
4. 搜索是否有第三方独立复测 GLM-5V-Turbo 的 visual-to-code 或 frontend coding 结果。
5. 按 `research/design-bench-material-collection.md` 核对可跑 framework：Design2Code、Interaction2Code、DesignBench、DCGen、VAB-CSS、Vision2Web、WebGen-Bench、UI2Code^N。
6. 按 `research/framework-reproducibility-audit.md` 做第一轮 smoke test：Design2Code-HARD、Interaction2Code、DCGen、DesignBench。
7. 继续补 `WebGenBench` / `VIBE Bench` / `Web2Code` / `WebCode2M` 的模型分数，确认它们是否应纳入主展示页。
8. 继续确认 GLM-4V-9B / GLM-4V-Plus 是否有前端 design-to-code benchmark 的第三方复测。
9. 跟进 UI2Code^N 是否发布可复现实验脚本、模型权重和 benchmark leaderboard。
10. 确认 Figma2Code、PSD2Code、ScreenBench 是否有完整代码、数据、license 和可复现实验脚本。

## 后续需要横向比较的 Benchmark

- WebPAI DesignBench
- VisualAgentBench / VAB-CSS
- Design2Code
- Design2Code-HARD
- Interaction2Code
- Vision2Web
- Flame-React-Eval / Flame-VLM-Code
- Web2Code
- DCGen
- ScreenBench / ScreenCoder
- Figma2Code
- WebGen-Bench
- CC-Bench-V2 Frontend
- WebVoyager
- DesignArena 或类似 UI generation arena，前提是公开且可复现

## 做 Web 展示还需要补的数据

已补到 `data/web_display_data.json` 和 `research/web-display-data-spec.md`。下面这些字段已经结构化：

- benchmark 的任务类型
- 输入模态：纯文本、截图、mockup、PRD、assets 等
- 输出产物：HTML、React、完整网站、浏览器操作结果等
- 指标含义和分数解释
- GLM-5V-Turbo 分数
- 竞品模型分数
- 结果来源类型：官方报告、benchmark 官方榜单、第三方复测
- 来源 URL
- 可信度等级
