# Zhipu / THUDM Agent 系统与 Design Bench 关系

最后更新：2026-06-02

## 结论

Zhipu / THUDM 确实做过 agent 或 agent-like 系统来跑和前端、网页、视觉设计相关的 benchmark，但需要分清三类：

1. **直接 design 相关的 agent benchmark**：`VisualAgentBench` 里的 `VAB-CSS`。这是最直接回答“agent 跑 design bench”的证据，任务是让 agent 通过工具修改 CSS，使当前页面渲染接近目标设计截图。
2. **UI-to-code 的闭环优化系统**：`UI2Code^N`。它不是传统多模块 agent，但有渲染、视觉反馈、迭代修正、RL 优化，属于 agent-like 的闭环可执行 UI 生成系统。
3. **Web/GUI 操作 agent**：`AutoWebGLM`、`AutoGLM`、`CogAgent`，以及 GLM-4.1V/4.5V/4.6V 在 `WebVoyager`、`OSWorld`、`AndroidWorld` 等 benchmark 上的结果。这些说明网页/GUI 理解和操作能力，但不是设计生成或 CSS 修复 benchmark。

换句话说：如果我们要做 web 展示，`VAB-CSS` 应放在“agentic visual design / CSS repair”模块，`UI2Code^N` 放在“closed-loop UI-to-code / visual optimization”模块，`AutoWebGLM` 和 `AutoGLM` 放在“web/GUI agent background”模块。

## 系统一览

| 系统 / benchmark | 时间 | Zhipu 关系 | 是否直接 design bench | 任务形态 | 关键结果 / 证据 |
|---|---:|---|---|---|---|
| VisualAgentBench / VAB-CSS | 2024 | THUDM / Tsinghua 的 GLM 生态工作，不是纯 Z.AI 官方产品 | 是 | CSS repair agent：看目标截图和当前页面，调用工具定位/修改 CSS | GLM-4V 在 VAB-CSS 上 SR 23.6；CogAgent 13.9；GPT-4o 34.5 |
| UI2Code^N | 2025/2026 | Zhipu / Tsinghua；基于 GLM-4.1V-9B-Base | 是，偏 UI-to-code | 生成代码、渲染、看视觉反馈、迭代 polish；RVPO 训练 | UI2Code^N-9B-RL：Design2Code 88.6，Flame 95.0，Web2Code 92.5 |
| AutoWebGLM | 2024 | Tsinghua & Zhipu AI；基于 ChatGLM3-6B | 否 | Web navigation agent，主要处理网页浏览和操作 | AutoWebBench 62.7，Mind2Web 59.5，MiniWoB++ 89.3，WebArena 18.2 |
| AutoGLM | 2024 | Zhipu AI & Tsinghua；ChatGLM family agents | 否 | Foundation GUI agent，覆盖浏览器和 Android | VAB-WebArena-Lite 55.2 / pass@2 59.1；OpenTable 96.2；AndroidLab 36.2 |
| CogAgent | 2023/2024 | THUDM / CogVLM 系 | 否 | Visual GUI agent | Mind2Web overall 58.2；AITW overall 76.88 |
| GLM-4.1V/4.5V/4.6V as agent backend | 2025 | Z.AI / GLM-V 系 | 否 | 跑 GUI agent benchmark | WebVoyager、OSWorld、AndroidWorld、WebQuest 等 |

## VisualAgentBench / VAB-CSS

`VisualAgentBench` 是一个面向 “LMM-as-Visual-Foundation-Agent” 的 benchmark，覆盖三类场景：embodied、GUI、visual design。其中 visual design 对应 `VAB-CSS`。

### VAB-CSS 任务

`VAB-CSS` 的任务不是从零生成网页，而是 **CSS 修复 / 视觉设计修复**：

- 输入：目标设计截图、当前错误页面截图、当前 HTML、自然语言差异描述。
- 问题构造：随机破坏某个 CSS rule 的某个 categorical property，使页面产生可见偏差。
- Agent 可用工具：
  - `get_selectors_by_html_element`
  - `select_rule`
  - `edit_rule`
  - `revert_last_edit`
- Agent 需要通过多轮工具调用定位错误 CSS 规则，并修改属性值，让最终渲染接近目标设计。

### 数据规模和指标

| 项 | VAB-CSS |
|---|---:|
| Action space | 4 |
| Test instance | 165 |
| Train trajectory | 829 |
| Train step | 5,250 |
| Max round limit | 10 |

指标：

- `Success Rate (SR)`：主指标。最终渲染和目标设计的 SSIM 大于 0.9 视为成功。
- `Improve Rate (IR)`：软指标。最终渲染比初始错误渲染更接近目标设计。

### VAB-CSS 公开结果

| 模型 | 评测方式 | VAB-CSS SR |
|---|---|---:|
| GPT-4o-2024-05-13 | Prompting | 34.5 |
| GPT-4-Vision-Preview | Prompting | 29.1 |
| GPT-4-Turbo-0409 | Prompting | 27.9 |
| InternVL-2 | Fine-tuning | 24.2 |
| GLM-4V | Fine-tuning | 23.6 |
| LLaVA-NeXT | Fine-tuning | 18.2 |
| CogVLM2 | Fine-tuning | 17.6 |
| CogAgent | Fine-tuning | 13.9 |
| CogVLM | Fine-tuning | 10.3 |

这个结果很重要：它说明 Zhipu/THUDM 不是只做了网页浏览 agent，也做过把视觉设计修复形式化成 agent benchmark 的工作。`VAB-CSS` 不是 `Design2Code` 那种单图转代码，而是更接近“已有前端项目里调 CSS，让页面匹配目标设计”。

## UI2Code^N：不是传统 agent，但更接近设计生成

`UI2Code^N` 把 UI-to-code 建模为 interactive visual optimization。它的流程和 agent 有相似之处：

1. 根据目标 UI 生成初始代码。
2. 渲染代码得到当前页面。
3. 对比目标截图和当前渲染。
4. 继续 polish 代码。
5. 用相对视觉偏好做 RL 优化。

它直接跑的 benchmark 包括 `Design2Code`、`Flame`、`Web2Code`、`UI2Code-Real`、`UIPolish`、`Design2Code-HARD`、`WebCode2M-Long`。

`UI2Code^N` 论文还专门和 agent-based UI-to-code 系统比较：

| 系统 | DINO Acc. | VLM Judge Acc. | Latency | Token Cost |
|---|---:|---:|---:|---:|
| DCGen | 69.6 | 45.0 | 约 137s | 约 7600 |
| ScreenCoder | 85.7 | 80.0 | 约 66s | 约 4600 |
| UI2Code^N-9B-RL | 86.1 | 88.6 | 约 40s | 约 2600 |

所以目前能确认的是：Zhipu 没有公开一个“多模块 agent pipeline 去刷 Design2Code”的主线；相反，`UI2Code^N` 的论点是 end-to-end VLM + 渲染反馈闭环，在 `Design2Code-HARD` 上比传统 agent-based pipeline 更稳、更省 token。

## AutoWebGLM

`AutoWebGLM` 是 2024 年 KDD 论文，基于 `ChatGLM3-6B`，定位是网页浏览 agent。它做了 HTML 简化、网页浏览数据构造、curriculum training、DPO / RFT 等，不是设计生成系统。

公开结果：

| Benchmark | AutoWebGLM |
|---|---:|
| AutoWebBench English Cross-Task | 64.8 |
| AutoWebBench English Cross-Domain | 58.6 |
| AutoWebBench Chinese Cross-Task | 65.4 |
| AutoWebBench Chinese Cross-Domain | 61.8 |
| Mind2Web Average | 59.5 |
| MiniWoB++ | 89.3 |
| WebArena | 18.2 |

对我们后续 web 展示的价值：它可以说明 Zhipu 在网页 DOM/HTML 操作、网页 action space、任务轨迹训练方面有 agent 基础，但不应放进 design-to-code 主榜。

## AutoGLM

`AutoGLM` 是 Zhipu AI / Tsinghua 的 foundation GUI agent 系统，覆盖 Web browser 和 Android。它的两个关键设计是：

- Intermediate interface design：把 planner 和 grounder 分离，避免端到端坐标点击难以训练。
- Self-evolving online curriculum RL：让 agent 在 web/android 环境中逐步采样、训练和提升。

公开结果：

| Benchmark / eval | AutoGLM |
|---|---:|
| VAB-WebArena-Lite | 55.2 |
| VAB-WebArena-Lite pass@2 | 59.1 |
| OpenTable real website eval | 96.2 |
| AndroidLab / VAB-Mobile | 36.2 |
| Chinese Android app human eval | 89.7 |

`AutoGLM` 和 design bench 的关系是间接的：它使用了 VisualAgentBench 里的 WebArena/Mobile 方向，但没有看到它报告 `VAB-CSS` 或 `Design2Code` 结果。

## 判断

如果问题是“Zhipu 有没有用 agent 跑前端/design 相关 benchmark”，答案是：

- **有**：`VAB-CSS` 是直接的 agentic visual design benchmark，GLM-4V 和 CogAgent 都有结果。
- **有另一条更强的非传统 agent 路线**：`UI2Code^N` 用渲染反馈闭环和 RL 跑 UI-to-code benchmark。
- **也有很多 GUI/Web agent 线**：`AutoWebGLM`、`AutoGLM`、`CogAgent`、GLM-V 的 WebVoyager/OSWorld/AndroidWorld 结果，但这些不能直接证明设计生成能力。

## 来源链接

- VisualAgentBench 论文：https://arxiv.org/abs/2408.06327
- VisualAgentBench GitHub：https://github.com/THUDM/VisualAgentBench
- UI2Code^N 论文：https://arxiv.org/abs/2511.08195
- AutoWebGLM 论文：https://arxiv.org/abs/2404.03648
- AutoWebGLM GitHub：https://github.com/THUDM/AutoWebGLM
- AutoGLM 论文：https://arxiv.org/abs/2411.00820
- AutoGLM 项目页：https://xiao9905.github.io/AutoGLM
- CogAgent 论文：https://arxiv.org/abs/2312.08914
