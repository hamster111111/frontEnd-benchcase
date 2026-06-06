# 前端 Design Bench 资料索引

最后更新：2026-06-02

## 调研目标

这份资料索引用来支持后续两个目标：

1. 系统整理 Zhipu/GLM 及其他模型在前端 design benchmark 上的公开结果。
2. 筛选我们可以实际跑、可以改进刷分、可以形成论文贡献的 benchmark/framework。

这里的 design bench 采用宽口径：包括 UI-to-code、前端代码生成、CSS repair、UI polishing、交互网页生成、完整网站开发、设计文件到代码，以及 Web/GUI agent 中和网页界面强相关的评测。

复现可跑性、环境依赖、API/GPU 成本和 smoke test 路线另见：`research/framework-reproducibility-audit.md`。

Zhipu/GLM 到底是直接模型跑分还是用 framework 跑 design bench，另见：`research/zhipu-direct-vs-framework-design-bench.md`。

## 证据等级

| 等级 | 含义 | 用途 |
|---|---|---|
| L1 | 代码、数据、评测脚本基本公开，理论上可复现 | 优先作为实验主线 |
| L2 | benchmark 论文或项目页给出清晰结果，但复现成本较高 | 可作为补充实验或对比 |
| L3 | 模型官方报告结果，跑分条件不完全公开 | 可用于横向展示，需要标 caveat |
| L4 | 项目 demo、博客、非正式榜单 | 只作线索，不作核心证据 |

## Benchmark / Framework 索引

| 名称 | 任务形态 | 输入 | 输出 | 可跑性 | 论文潜力 | 当前判断 |
|---|---|---|---|---|---|---|
| Design2Code / Design2Code-HARD | UI-to-code / visual restoration | 网页截图，可选文本增强 | HTML/CSS + 渲染网页 | A | 高 | 官方 repo 有数据、prompting、自动评测、模型预测；适合作主实验基线。 |
| Web2Code | 大规模 webpage-to-code | 网页截图/网页理解样本 | 前端代码或网页理解答案 | A- | 中高 | 代码、HuggingFace 数据、训练代码和评测 suite 公开；数据规模更大，适合做训练/泛化线。 |
| WebPAI DesignBench | 多框架前端生成/编辑/修复 | 图片、代码、图片+代码、标注区域 | React/Vue/Angular/Vanilla 代码 | A- | 高 | 覆盖 generation/edit/repair，任务更贴近真实前端 workflow；工程依赖较多。 |
| VisualAgentBench / VAB-CSS | Agentic CSS repair | 目标截图、错误截图、HTML、差异描述 | 多轮 CSS rule edits | B+ | 高 | 适合做闭环 agent / CSS repair；需要跑 AgentBench 风格环境和任务服务。 |
| FLAME / Flame-React-Eval | React UI code generation | UI 截图或多模态提示 | React 代码 | B | 中高 | 专门展示“通用 VLM 不一定擅长 React 工程生成”；需继续核对公开代码和 split。 |
| UI2Code^N | 交互式 UI-to-code / UI polishing | UI 截图、当前代码、当前渲染 | 生成、编辑、润色后的前端代码 | B+ | 很高 | Zhipu 生态相关，模型和 evaluation 指南公开；重 GPU/推理成本，需要确认实际可跑门槛。 |
| Interaction2Code | 交互网页生成 | 交互原型图、action 描述 | 交互网页代码 | A- | 高 | ASE 2025；数据、代码、metric 公开，能补静态 UI-to-code 的交互短板。 |
| Vision2Web | 视觉网站开发 | 原型图、需求、assets、环境上下文 | 静态网页、交互前端、全栈网站 | B | 很高 | 最接近完整网站开发；官方 pipeline 和提交格式公开，但工程成本高。 |
| WebGen-Bench | 从零生成交互/功能网站 | 自然语言网站需求 | 完整网站/应用 | B | 高 | 评估 Bolt.diy、OpenHands、Aider 等 agent；更偏 prompt-to-app，成本和环境复杂。 |
| Figma2Code | Figma 设计文件到代码 | 截图、Figma metadata、assets | UI 代码 | B | 很高 | ICLR 2026，数据集公开但体量约 17GB；补足“设计文件 metadata”方向。 |
| PSD2Code | PSD 设计文件到 React+SCSS | PSD layer、assets、截图 | React + SCSS | C | 中高 | 方法思路有价值，但需要继续确认数据/代码是否公开。 |
| DCGen | 分而治之的截图到 UI 代码 | 网页截图，分割后的局部区域 | HTML/CSS | A- | 中高 | FSE 2025 artifact，有 code、sample data、HF 数据；适合做 segment-aware baseline。 |
| ScreenCoder / ScreenBench | 模块化多模态 agent UI-to-code | UI 截图 | HTML/CSS | B+ | 高 | Apache-2.0 repo，含 post-training 代码和 ScreenBench；适合看 multi-agent + UIED 路线。 |
| VisualWebBench | Web 页面理解与 grounding | 网页截图/网页 QA/元素定位 | QA、grounding、action prediction | A- | 中 | 不是代码生成，但可作为网页视觉理解能力背景。 |
| App-Bench | Prompt-to-web-app builder benchmark | 单条自然语言 app 需求 | 完整 Web app | C+ | 中高 | 非学术但很贴近 agent 产品；人工评分、任务少，适合作趋势参考。 |

## 现阶段优先跑的候选

### A 类：优先复现

1. **Design2Code / Design2Code-HARD**
   - 优点：认知度高、代码和数据齐、评测脚本明确。
   - 刷分入口：self-revision、多候选 rerank、render-feedback、layout planning、局部 CSS 修复。
   - 风险：竞争激烈；CLIP/SSIM/VLM judge 口径需要分清。

2. **Interaction2Code**
   - 优点：从静态页面扩展到交互效果，论文角度更鲜明。
   - 刷分入口：interactive element detection、状态转移规划、交互后截图对齐、failure-aware prompting。
   - 风险：数据规模 127 页面，容易被质疑泛化；需要补更多实验或跨 bench 验证。

3. **WebPAI DesignBench**
   - 优点：generation/edit/repair + React/Vue/Angular/Vanilla，覆盖真实前端 workflow。
   - 刷分入口：多模态输入选择、代码+图联合修复、compile error repair、framework-aware prompting。
   - 风险：工程依赖较复杂；不同任务/框架不能合成一个总分。

4. **DCGen**
   - 优点：已有 segment-aware 思路和 artifact，适合对比“整体生成 vs 分块生成”。
   - 刷分入口：更好的分割、层级规划、局部重生成、segment verifier。
   - 风险：容易被认为是工程 pipeline，需要有清楚方法创新。

### B 类：强潜力但工程成本高

1. **VAB-CSS**
   - 适合做 agentic visual repair。优势是闭环、多轮、可解释。
   - 主要成本是任务服务、Docker/环境和 agent 调度。

2. **Vision2Web**
   - 适合做“从 UI-to-code 到完整网站开发”的高价值实验。
   - 主要成本是 agent framework、GUI/VLM judge、功能测试和提交格式。

3. **UI2Code^N**
   - 和 Zhipu 生态最相关，也最贴近 test-time scalable interactive UI-to-code。
   - 需要确认模型推理成本、evaluation scripts 的完整性、是否适合我们复现/改进。

4. **WebGen-Bench**
   - 可以接入 Bolt.diy、OpenHands、Aider，适合 agent-web-app 方向。
   - 主要成本是 full app 环境、UI agent 评测、人工/自动外观评分。

5. **Figma2Code**
   - 很适合做设计 metadata 方向，和纯 screenshot-to-code 形成差异。
   - 主要成本是数据体量大、Figma metadata 处理复杂。

## 可刷分方法空间

| 方法方向 | 适配 benchmark | 可能 claim |
|---|---|---|
| Render-feedback refinement | Design2Code、UIPolish、VAB-CSS、DesignBench | 利用渲染截图反馈能稳定提升视觉一致性。 |
| 多候选生成 + verifier/rerank | Design2Code、DesignBench、Interaction2Code | 同预算下通过视觉/结构 verifier 选择更优代码。 |
| CSS 局部 patch | VAB-CSS、DesignBench repair、UIPolish | 局部修改比整页重写更稳定，减少回归。 |
| Component/layout planning | Design2Code、DCGen、ScreenCoder、Figma2Code | 先规划结构再生成代码，提高布局和组件还原。 |
| Segment-aware generation | DCGen、ScreenCoder、Design2Code-HARD | 分块生成能缓解复杂页面的遗漏和错位。 |
| Interaction planning | Interaction2Code、Vision2Web、WebGen-Bench | 显式状态/事件建模能提升交互网页完成度。 |
| Design metadata grounding | Figma2Code、PSD2Code | 结构化设计文件信息能显著减少截图推断误差。 |
| Agent framework comparison | Vision2Web、WebGen-Bench、App-Bench | 同一模型在不同 agent scaffold 下差异很大。 |

## 一手来源清单

### UI-to-code / design-to-code

- Design2Code paper: https://arxiv.org/abs/2403.03163
- Design2Code repo: https://github.com/NoviScl/Design2Code
- Design2Code dataset: https://huggingface.co/datasets/SALT-NLP/Design2Code
- Design2Code-HARD dataset: https://huggingface.co/datasets/SALT-NLP/Design2Code-HARD
- Web2Code paper: https://arxiv.org/abs/2406.20098
- Web2Code repo: https://github.com/MBZUAI-LLM/web2code
- Web2Code dataset: https://huggingface.co/datasets/MBZUAI/Web2Code
- DCGen paper: https://arxiv.org/abs/2406.16386
- DCGen repo: https://github.com/WebPAI/DCGen
- ScreenCoder repo: https://github.com/leigest519/ScreenCoder

### 多框架前端生成/编辑/修复

- DesignBench paper: https://arxiv.org/abs/2506.06251
- DesignBench repo: https://github.com/WebPAI/DesignBench
- DesignBench project: https://webpai.github.io/DesignBench/

### 交互网页 / 完整网站

- Interaction2Code paper: https://arxiv.org/abs/2411.03292
- Interaction2Code repo: https://github.com/WebPAI/Interaction2Code
- Interaction2Code dataset: https://huggingface.co/datasets/whale99/Interaction2Code
- Vision2Web paper: https://arxiv.org/abs/2603.26648
- Vision2Web project: https://vision2web-bench.github.io/
- Vision2Web repo: https://github.com/zai-org/Vision2Web
- WebGen-Bench paper: https://arxiv.org/abs/2505.03733
- WebGen-Bench repo: https://github.com/mnluzimu/WebGen-Bench
- App-Bench: https://appbench.ai/

### Design file to code

- Figma2Code OpenReview: https://openreview.net/forum?id=CaXZB6bI31
- Figma2Code dataset: https://huggingface.co/datasets/xcodemind/Figma2Code
- PSD2Code paper: https://arxiv.org/abs/2511.04012

### Agentic / GUI / Web understanding 背景

- VisualAgentBench paper: https://arxiv.org/abs/2408.06327
- VisualAgentBench repo: https://github.com/THUDM/VisualAgentBench
- VisualWebBench paper: https://arxiv.org/abs/2404.05955
- VisualWebBench repo: https://github.com/VisualWebBench/VisualWebBench

### Zhipu / GLM 相关

- GLM-5V-Turbo docs: https://docs.z.ai/guides/vlm/glm-5v-turbo
- GLM-5V-Turbo report: https://arxiv.org/abs/2604.26752
- GLM-4.5V / GLM-4.1V report: https://arxiv.org/abs/2507.01006
- GLM-5 report / CC-Frontend: https://arxiv.org/abs/2602.15763
- UI2Code^N paper: https://arxiv.org/abs/2511.08195
- UI2Code^N repo: https://github.com/zai-org/UI2Code_N

## 下一轮需要继续核对

1. **FLAME / Flame-React-Eval** 的代码、数据、evaluation split 是否完整公开。
2. **Vision2Web repo** 是否已经包含完整官方 evaluation pipeline，还是只开放 submission pipeline。
3. **UI2Code^N** 的 evaluation/readme 是否能直接跑 Design2Code、Flame、Web2Code、UIPolish。
4. **Figma2Code** 是否有官方代码仓库；目前已确认 OpenReview 和 HF 数据集。
5. **PSD2Code** 是否有代码和数据；目前只确认 arXiv 文本。
6. **ScreenCoder / ScreenBench** 的 benchmark 数据、训练代码和评测方式是否能独立复现。
7. **WebGen-Bench** 的自动评测是否能在我们本地/服务器跑通，尤其是 Bolt.diy、OpenHands、Aider 三条路径。
8. 检查每个候选的 license、数据使用限制、API 成本和 GPU 成本。
