# GLM-5V-Turbo 前端 / Design Bench 调研笔记

最后更新：2026-06-02

## 范围

这份笔记记录 GLM-5V-Turbo 在前端、视觉设计、UI-to-code、网站生成等方向已经能确认的 benchmark 信息。这里的 “design bench” 是泛指前端设计能力评测，不是特指 WebPAI 的 `DesignBench` 这个具体 benchmark。

## 核心结论

目前能确认和前端/design 相关的评测主要有：

1. `Design2Code`
2. `Flame-VLM-Code` / `Flame-React-Eval`
3. `Vision2Web`
4. `CC-Frontend`
5. `WebVoyager`，它更偏 GUI / 网页交互能力，不是设计生成 benchmark

GLM-5V-Turbo 在单页视觉还原、设计图转代码这类任务上表现最强，典型代表是 `Design2Code`。但在更完整的网站开发流程类 benchmark 上，比如 `Vision2Web`，它并没有领先 Kimi K2.5 和 Claude Opus 4.6。

## 已确认 Benchmark

| Benchmark | GLM-5V-Turbo | 对比模型分数 | 相关性 | 备注 |
|---|---:|---|---|---|
| Design2Code | 94.8 | Kimi K2.5: 91.3；Claude Opus 4.6: 77.3 | 高 | 视觉设计 / 网页截图转前端代码。目前最直接支持 GLM-5V-Turbo 前端视觉还原能力的证据。 |
| Flame-VLM-Code | 93.8 | Kimi K2.5: 88.8；Claude Opus 4.6: 98.8 | 高 | 面向 VLM 的前端开发能力评测。GLM 很强，但官方表里低于 Claude Opus 4.6。 |
| Vision2Web | 31.0 | Kimi K2.5: 33.2；Claude Opus 4.6: 43.5 | 高 | 更接近真实网站开发流程，包含更丰富的任务规范和 workflow verification。GLM 在这里落后于 Kimi 和 Claude。 |
| CC-Frontend | 68.4 | GLM-5-Turbo: 69.4；Kimi K2.5: 62.3；Claude Opus 4.6: 75.9 | 中 | CC-Bench-V2 的纯文本前端 coding 子项。它和前端相关，但不是视觉设计 benchmark。 |
| WebVoyager | 88.5 | Kimi K2.5: 84.3；Claude Opus 4.6: 88.0 | 低到中 | Web GUI agent benchmark。能说明网页界面理解和浏览器操作能力，但不能直接证明设计生成能力。 |

## 解读

`Design2Code` 是最应该重点看的指标。它直接对应设计图或网页截图到前端代码的场景，能支持 “GLM-5V-Turbo 视觉转代码能力强” 这个判断。

`Flame-VLM-Code` 也和前端能力高度相关，尤其是 VLM 场景下的 UI / React / 前端代码生成。不过 GLM 技术报告里的命名和原始 FLAME 论文中的评测命名不完全一致，后续做正式对比时需要进一步核对它到底对应哪个 split 或 evaluation protocol。

`Vision2Web` 更接近真实网站开发，不只是单图还原，而是可能包含 PRD、mockup、参考页面、素材资源、agent workflow verification 等要素。GLM-5V-Turbo 在这里不是领先模型，这说明它的强项更偏视觉到代码的局部任务，而不是完整网站开发链路。

`CC-Frontend` 是纯文本 coding 能力，不是视觉设计理解能力。它说明 GLM-5V-Turbo 在加入视觉能力后，仍然保留了较强的基础前端 coding 能力，但不能单独作为 design bench 证据。

`WebVoyager` 只在我们把 “前端相关能力” 扩展到网页 UI 操作、浏览器 agent、网页理解时才有参考价值。它应和 design-to-code 类 benchmark 分开看。

## 尚未确认

- 暂时没有找到 GLM-5V-Turbo 在 WebPAI `DesignBench` 上的公开独立结果。
- `Vision2Web` 官网当前没有公开包含 GLM-5V-Turbo 的 leaderboard；`31.0` 这个分数来自 GLM-5V 技术报告。
- 检索中看到的一些第三方页面大多是在转述 Z.AI 官方数字。没有复现实验日志前，不应该把它们当成独立复测证据。

## 来源链接

- GLM-5V 技术报告：https://arxiv.org/abs/2604.26752
- Z.AI GLM-5V-Turbo 文档：https://docs.z.ai/guides/vlm/glm-5v-turbo
- Design2Code 论文：https://arxiv.org/abs/2403.03163
- FLAME 前端 VLM 评测论文：https://arxiv.org/abs/2503.01619
- Vision2Web 论文：https://arxiv.org/abs/2603.26648
- Vision2Web 项目页：https://vision2web-bench.github.io/
- GLM-5 / CC-Bench-V2 来源论文：https://arxiv.org/abs/2602.15763
