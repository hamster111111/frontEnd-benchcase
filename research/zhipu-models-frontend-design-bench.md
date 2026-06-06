# Zhipu / Z.AI 近几年模型的前端 Design Bench 调研

最后更新：2026-06-02

## 范围

这里整理近几年 Zhipu / Z.AI / THUDM 相关模型在前端设计、UI-to-code、网页生成、Web/GUI agent 等 benchmark 上的公开结果。这里的 `design bench` 仍按泛概念处理，不特指 WebPAI 的 `DesignBench`。

## 核心结论

Zhipu 线里真正和前端设计生成强相关的公开结果，主要集中在 2025 年之后：`GLM-4.1V-Thinking`、`GLM-4.5V`、`GLM-4.6V`、`GLM-5V-Turbo`，以及基于 `GLM-4.1V-9B-Base` 训练的 `UI2Code^N`。

从公开数字看，GLM 系在 `Design2Code` 和 `Flame` 这类 UI-to-code / React UI 生成任务上进步很明显：`GLM-4.1V` 到 `GLM-4.6V` 的 `Design2Code` 从 64.7 提到 88.6，`Flame-React-Eval` 从 72.5 提到 86.3。`GLM-5V-Turbo` 进一步在官方报告里给出 `Design2Code 94.8` 和 `Flame-VLM-Code 93.8`。

`UI2Code^N` 是目前最值得单独看的 Zhipu/Tsinghua UI-to-code 专项模型。它不是通用 VLM 直接跑前端任务，而是把 UI-to-code 当作可渲染反馈下的交互式视觉优化任务；`UI2Code^N-9B-RL` 在论文主表里达到 `Design2Code 88.6`、`Flame 95.0`、`Web2Code 92.5`、`UI2Code-Real 76.5`、`UIPolish-Real 80.0`、`UIPolish-Synthetic 94.0`。

2023/2024 年的 `CogAgent` 更偏 GUI/Web agent，不是设计转代码。它跑了 `Mind2Web` 和 `AITW`，可以作为网页界面理解、控件定位、操作规划能力的历史线索，但不要和 `Design2Code`、`Flame` 混成同一种 design-generation 指标。

## 时间线

| 时间 | 模型 / 系统 | 相关 benchmark | 和前端 design 的关系 | 备注 |
|---|---|---|---|---|
| 2023/2024 | CogAgent | Mind2Web、AITW | 低到中 | GUI/Web agent；看网页截图和历史动作预测下一步操作，不生成前端代码。 |
| 2024 | GLM-4V-9B / GLM-4V 系 | VAB-CSS；暂未找到 Design2Code / Web2Code / Flame 这类 design-to-code 分数 | 中 | GLM-4V 在 VisualAgentBench 的 `VAB-CSS` 上有 CSS repair agent 结果 23.6；但这不是单图转代码 benchmark。 |
| 2025 | GLM-4.1V-9B-Thinking | Design2Code、Flame-React-Eval、WebVoyager、OSWorld、AndroidWorld、WebQuest | 高 / 中 | 9B thinking 模型，已进入 UI-to-code 和 GUI agent 表格。 |
| 2025 | GLM-4.5V | Design2Code、Flame-React-Eval、WebVoyager、OSWorld、AndroidWorld、WebQuest | 高 / 中 | 106B A12B thinking 模型，Design2Code 和 GUI agent 分数明显高于 GLM-4.1V。 |
| 2025 | GLM-4.6V | Design2Code、Flame-React-Eval、WebVoyager、OSWorld、AndroidWorld、WebQuest | 高 / 中 | 官方报告表里 `Design2Code 88.6`、`Flame-React-Eval 86.3`。 |
| 2025/2026 | UI2Code^N-9B-SFT / RL | Design2Code、Flame、Web2Code、UI2Code-Real、UIPolish、WebCode2M-Long、Design2Code-HARD | 很高 | 基于 `GLM-4.1V-9B-Base` 的专项 UI-to-code 模型。 |
| 2026 | GLM-5V-Turbo | Design2Code、Flame-VLM-Code、Vision2Web、CC-Frontend、WebVoyager | 很高 / 中 | 当前最强的 Zhipu 通用 VLM 前端相关公开结果。 |

## UI-to-code / 前端生成结果

| 模型 | Design2Code | Flame / Flame-React-Eval | Web2Code | UI2Code-Real | UIPolish-Real | UIPolish-Synthetic | Vision2Web | CC-Frontend | 来源口径 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GLM-4.1V-9B-Thinking | 64.7 | 72.5 | 71.3 | 53.0 | 42.0 | 46.0 | - | - | GLM-4.5V/4.1V 报告；UI2Code^N 表 1 |
| GLM-4.5V | 82.2 | 82.5 | - | - | - | - | - | - | GLM-4.5V/4.1V 报告 |
| GLM-4.6V | 88.6 | 86.3 | - | - | - | - | - | - | GLM-4.5V/4.1V 报告 |
| UI2Code^N-9B-SFT | 79.3 | 85.0 | 80.8 | 67.0 | 76.0 | 89.0 | - | - | UI2Code^N 论文表 1 |
| UI2Code^N-9B-RL | 88.6 | 95.0 | 92.5 | 76.5 | 80.0 | 94.0 | - | - | UI2Code^N 论文表 1 |
| GLM-5V-Turbo | 94.8 | 93.8 | - | - | - | - | 31.0 | 68.4 | GLM-5V 技术报告 / Z.AI 文档 |

### 解读

`Design2Code` 是最直接的前端视觉还原证据。GLM-4.1V、GLM-4.5V、GLM-4.6V、GLM-5V-Turbo 都有公开结果，形成了比较清晰的迭代曲线。

`Flame` / `Flame-React-Eval` 更偏 React UI / 前端代码生成。这里 `UI2Code^N-9B-RL` 的 95.0 很突出，说明专项 UI coding 训练能明显提高这类任务表现。

`Vision2Web` 目前只在 GLM-5V-Turbo 资料中看到公开分数。它更接近真实网站开发流程，分数 `31.0` 说明即便 UI-to-code 指标很高，完整网站开发链路仍然是另一类难度。

`CC-Frontend` 是前端 coding 子项，和视觉设计无关或弱相关。它可以支持“前端代码能力”叙事，但不应作为视觉设计能力的核心证据。

## GLM-4.1V / 4.5V / 4.6V 的 GUI/Web agent 结果

| 模型 | OSWorld | AndroidWorld | WebVoyager | WebQuest-SingleQA | WebQuest-MultiQA | 前端相关性 |
|---|---:|---:|---:|---:|---:|---|
| GLM-4.1V-9B-Thinking | 14.9 | 41.7 | 69.0 | 72.1 | 54.7 | 中 |
| GLM-4.5V | 35.8 | 57.0 | 84.4 | 76.9 | 60.6 | 中 |
| GLM-4.6V | 37.2 | 57.0 | 81.0 | 79.5 | 59.0 | 中 |

这些指标主要说明模型理解和操作网页/GUI 的能力。它们对“前端 UI 理解”有帮助，但不是“从设计图生成页面”的直接证据。

## CogAgent 的早期 GUI/Web 结果

| 模型 | Mind2Web cross-task | Mind2Web cross-website | Mind2Web cross-domain | Mind2Web overall | AITW overall | 备注 |
|---|---:|---:|---:|---:|---:|---|
| CogAgent | 62.3 | 54.0 | 59.4 | 58.2 | 76.88 | GUI agent；输入是截图/历史动作，输出下一步操作。 |

CogAgent 的价值在于说明 Zhipu/THUDM 早期已经在高分辨率 GUI 理解、网页控件定位、网页动作预测上积累数据和模型能力。但它不覆盖 `Design2Code`、`Flame`、`Web2Code` 这类 UI 生成 benchmark。

## VisualAgentBench / VAB-CSS

`VisualAgentBench` 是 THUDM / Tsinghua 参与的 visual foundation agent benchmark，其中 `VAB-CSS` 属于 visual design 场景。任务是给 agent 目标设计截图、当前错误页面截图、HTML 和自然语言差异描述，让 agent 通过工具定位并修改 CSS rule。

这个 benchmark 和 `Design2Code` 不同：它不是从零生成网页，而是已有前端项目里的 CSS repair / visual design repair。

| 模型 | 评测方式 | VAB-CSS SR |
|---|---|---:|
| GPT-4o-2024-05-13 | Prompting | 34.5 |
| GPT-4-Vision-Preview | Prompting | 29.1 |
| GPT-4-Turbo-0409 | Prompting | 27.9 |
| GLM-4V | Fine-tuning | 23.6 |
| CogAgent | Fine-tuning | 13.9 |

这里要更新前面的判断：没有找到 `GLM-4V` 的 `Design2Code` / `Web2Code` / `Flame` 公开结果，但 `GLM-4V` 确实有 `VAB-CSS` 这种 agentic visual design benchmark 结果。

## UI2Code^N 重点摘录

`UI2Code^N` 论文把 UI-to-code 分成两个方向：

- UI drafting：从参考 UI 生成代码，覆盖 `Design2Code`、`Flame`、`Web2Code`、`UI2Code-Real`。
- UI polishing：给定已有 UI/code，再根据渲染反馈改进，覆盖 `UIPolish-Real` 和 `UIPolish-Synthetic`。

### 主结果

| 模型 | Design2Code | Flame | Web2Code | UI2Code-Real | UIPolish-Real | UIPolish-Synthetic |
|---|---:|---:|---:|---:|---:|---:|
| GLM-4.1V-9B-Thinking | 64.7 | 72.5 | 71.3 | 53.0 | 42.0 | 46.0 |
| UI2Code^N-9B-SFT | 79.3 | 85.0 | 80.8 | 67.0 | 76.0 | 89.0 |
| UI2Code^N-9B-RL | 88.6 | 95.0 | 92.5 | 76.5 | 80.0 | 94.0 |
| GPT-5 | 89.7 | 91.3 | 93.7 | 67.8 | 85.0 | 68.0 |
| Gemini-2.5-Pro | 89.5 | 87.5 | 90.6 | 68.7 | 74.0 | 68.0 |

### Design2Code 传统指标 / 视觉评审交叉验证

| 模型 | Block | Text | Position | Color | CLIP | DINOv3 | VLM Judge |
|---|---:|---:|---:|---:|---:|---:|---:|
| UI2Code^N-9B-SFT | 86.8 | 91.5 | 81.7 | 69.7 | 79.0 | 78.8 | 79.3 |
| UI2Code^N-9B-RL | 88.7 | 93.1 | 83.8 | 72.6 | 80.5 | 86.1 | 88.6 |

### Design2Code-HARD 上的 agent 对比

| 系统 | DINO Acc. | VLM Judge Acc. | Latency | Token Cost |
|---|---:|---:|---:|---:|
| DCGen | 69.6 | 45.0 | 约 137s | 约 7600 |
| ScreenCoder | 85.7 | 80.0 | 约 66s | 约 4600 |
| UI2Code^N-9B-RL | 86.1 | 88.6 | 约 40s | 约 2600 |

### WebCode2M-Long

| 模型 | CLIP Similarity |
|---|---:|
| WebSight VLM-7B | 0.69 ± 0.12 |
| Design2Code-18B | 0.74 ± 0.10 |
| UICopilot | 0.77 ± 0.11 |
| UI2Code^N-9B-RL | 0.79 ± 0.09 |

## 评价协议注意点

GLM-4.1V / GLM-4.5V 报告写明，VLM coding 评测沿用 `Design2Code` 的 direct setting，省略 text augmentation 和 self-revision，并使用 GPT-o4-mini 作为视觉 judge，而不是原始 `Design2Code` 论文里的 CLIP 主指标。因此这些分数适合在 Zhipu 官方报告内部比较，但和其他论文里直接报的 CLIP 分数不是完全同口径。

GLM-5V-Turbo 的 `Flame-VLM-Code` 命名和 FLAME 原论文中的 `Flame-React-Eval` 需要继续核对。现阶段可以把它归为高度相关的前端 VLM coding 证据，但正式展示页最好保留一条口径注释。

`UI2Code^N` 的很多分数来自 VLM-based scoring，论文也单独做了 human agreement / evaluator stability。它比纯 CLIP 更贴近人类视觉偏好，但也意味着跨论文横向对比时要标明 judge。

`CogAgent`、`WebVoyager`、`OSWorld`、`AndroidWorld`、`Mind2Web` 属于 GUI/Web agent，不属于设计生成。它们可以放在“网页界面理解与操作”章节，不宜放在“前端设计还原”主榜里。

## 待继续确认

1. 是否有 GLM-4V-Plus / GLM-4V-9B 在 `Design2Code`、`Web2Code`、`Flame`、`Vision2Web` 上的第三方复测。
2. `GLM-5V-Turbo` 的 `Flame-VLM-Code` 与原始 `Flame-React-Eval` 的 split / judge 是否一致。
3. 是否有 Zhipu 模型进入 WebPAI `DesignBench`、`DesignArena`、`VIBE Bench` 或类似前端设计 benchmark 的公开榜单。
4. `UI2Code^N` 是否发布了模型权重、评测脚本和可复现 leaderboard；后续做 web 展示时应区分“论文结果”和“可复测结果”。

## 来源链接

- CogAgent 论文：https://arxiv.org/abs/2312.08914
- CogAgent / THUDM GitHub：https://github.com/THUDM/CogAgent
- VisualAgentBench 论文：https://arxiv.org/abs/2408.06327
- VisualAgentBench GitHub：https://github.com/THUDM/VisualAgentBench
- GLM-4.5V and GLM-4.1V-Thinking 技术报告：https://arxiv.org/abs/2507.01006
- Z.AI GLM-4.5V 文档：https://docs.z.ai/guides/vlm/glm-4.5v
- Z.AI GLM-4.6V 文档：https://docs.z.ai/guides/vlm/glm-4.6v
- UI2Code^N 论文：https://arxiv.org/abs/2511.08195
- UI2Code^N Hugging Face：https://huggingface.co/zai-org/UI2Code_N
- GLM-5V 技术报告：https://arxiv.org/abs/2604.26752
- Z.AI GLM-5V-Turbo 文档：https://docs.z.ai/guides/vlm/glm-5v-turbo
