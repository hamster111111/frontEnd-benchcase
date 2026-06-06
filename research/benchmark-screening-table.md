# Benchmark 筛选表：先拉入研究主线的候选

最后更新：2026-06-02

## 筛选原则

这张表的目的不是做总榜，而是决定我们第一阶段要把哪些 benchmark 拉进研究主线、哪些只做背景资料。当前采用三个维度：

- 分数空间：公开代表分数越低，越容易证明还有 headroom；90+ 的 benchmark 不适合作单纯刷分主线。
- 可跑性：优先 API-only、少量样本可 smoke test、评测脚本清楚的 benchmark。
- 故事贴合：优先前端 design / UI-to-code / repair / interaction，GUI/Web agent 只作背景或远期扩展。

分数判断只在同一个 benchmark 内看，不跨 benchmark 合并。CLIP、DINO、VLM Judge、Success Rate、pass@k 不能混成一个总分。

## 第一批建议

| 层级 | Benchmark | 为什么先看 |
|---|---|---|
| P0 主实验 | Design2Code-HARD | 分数未到 90，样本小，前端截图到代码主线明确，适合做 render-feedback / rerank / 局部修复。 |
| P0 主实验 | UIPolish-Real | 真实 UI polishing 只有 80 左右，比一次生成更贴近真实前端修复流程。 |
| P0/P1 主实验 | VAB-CSS | 公开成功率低，CSS repair story 很强；工程比 Design2Code 重，所以作为第二个主线候选。 |
| P0/P1 主实验 | WebPAI DesignBench | 覆盖 generation / edit / repair / compile error repair，多框架前端价值高；分数口径需继续补齐。 |
| P1 扩展 | Vision2Web | 真实网站开发分数低，论文价值强，但 agent/evaluation 成本高，建议先只看 static level。 |
| P1 基线 | Design2Code / Flame / Web2Code | 分数偏高，但适合作 baseline、跨 benchmark 泛化和 React/网页理解扩展。 |

## 全量 benchmark 筛选表

| Benchmark | 任务对象 | 代表分数空间 | 发表/发布 | API/GPU 粗判 | 建议用途 | 下一步 |
|---|---|---|---|---|---|---|
| Design2Code | 网页截图或设计图转 HTML/CSS | GLM-5V-Turbo 94.8，主榜偏饱和；HARD 子集另看 | 2024-03 首发，NAACL 2025 Long | API 模型生成不需要 GPU；只跑自动评测基本无 GPU；训练 18B 级模型才需要 40GB+ | P1 基线，不作为单纯刷分主线 | 拉少量样本跑渲染和 Block/Text/Position/Color/CLIP，和 HARD 共享 pipeline |
| Flame-React-Eval | React UI 代码生成 | 代表分数 90+，Claude Opus 4.6 98.8，UI2Code^N 95.0，GLM-5V 93.8 | 2025-03 预印本 | API-only 可跑生成；本地 React 编译/渲染不需要 GPU | P1 React 扩展，重点看 compile/render 失败，不刷纯分 | 选 5 个 case 检查编译失败、布局漂移、交互缺失 |
| Vision2Web | static / interactive / full-stack 网站开发 | 公开 OpenHands interactive 最高约 56.6，GLM-5V 官方 31.0，空间大 | 2026-03 预印本 | API agent 可无 GPU；自部署 VLM/GUI agent 约 24-80GB | P1/P2 高价值扩展，先不全跑 | 只拉 static level 样本和 evaluator，估 token/latency 成本 |
| CC-Frontend | 纯文本前端 coding | GLM-5V 68.4，Claude Opus 4.6 75.9 | 2026-02 GLM-5 技术报告 | API-only 可跑；不是视觉 design | P2 背景，证明 coding 能力，不做主实验 | 只保留为 Zhipu 前端 coding 背景 |
| VAB-CSS | 目标截图 + 错误页面 + HTML + CSS 工具的视觉修复 | GPT-4o prompting 34.5，GLM-4V FT 23.6，CogAgent 13.9，低分空间大 | 2024-08 首发，ICLR 2025 Poster | API agent 可无 GPU；训练 open LMM 约 24GB+；环境/Docker 成本高 | P0/P1 visual repair 主线 | 先读 VAB-CSS setup，跑 1-2 个 CSS repair task 或先分析样例 |
| WebPAI DesignBench | React/Vue/Angular/Vanilla 的 generation/edit/repair | 当前聚合数据未收统一公开分数；任务本身有明显 repair/compile 空间 | 2025-06 预印本 | 多框架评测需要 Node/browser/API key；API 路线不需要 GPU | P0/P1 多框架前端主线 | 先拉 Vanilla/React 小样本，核对 CLIP/SSIM/CSR/MLLM score 输出 |
| Web2Code | 网页截图到 HTML + 网页理解 | UI2Code^N 92.5，GLM-4.1V-9B 71.3；主表高分但可做泛化 | 2024-06 首发，NeurIPS 2024 D&B | 小样本 API 评测可无 GPU；训练/本地模型建议 40GB+ | P1 泛化和数据线 | 只跑小样本 evaluate，确认能否作为 held-out 泛化集 |
| UI2Code-Real | 真实网页 UI-to-code | UI2Code^N-9B-RL 76.5，真实网页仍有空间 | 2025-11 首发，ICML 2026 | 本地 9B 推理约 24-48GB；只跑 judge/已有输出可用 API | P0/P1 真实网页主线 | 核对 UI2Code_N evaluation 数据是否完整公开，先不训练 |
| UIPolish-bench | 基于目标图、当前渲染和代码的 UI polishing | Real 80.0，Synthetic 94.0；真实集更值得做 | 2025-11 首发，ICML 2026 | 本地 9B 推理约 24-48GB；API judge 可无 GPU | P0 repair 主实验 | 先优先 Real，Synthetic 只作可控 ablation |
| Design2Code-HARD | 困难网页截图转代码 | UI2Code^N VLM Judge Acc. 88.6；CLIP 最好约 89.5，未明显 90+ | 2025-11 随 UI2Code^N 使用，来源基于 Design2Code-HARD 数据 | API-only 可做生成/修复/重排；评测不需要训练 GPU | P0 最优先 smoke test | 下载 3-5 个样本，跑 direct、multi-candidate、render-feedback 三个 baseline |
| WebCode2M-Long | 长网页真实代码生成 | UI2Code^N CLIP 0.79 +/- 0.09，长代码压力明显 | 2025-11 随 UI2Code^N 使用；WebCode2M 为 WWW 2025 Oral 相关数据线 | 数据/训练重；小样本 API 可试，训练倾向 80GB 级或多卡 | P2 压力测试，不做第一轮 | 只记录格式和 license，暂不下载大数据 |
| WebVoyager | 真实网页浏览和操作 | GLM-5V 88.5，GLM 系列已较高 | 2024-01 首发，ACL 2024 Long | API agent 可跑；浏览器环境成本中等 | 背景：Zhipu web agent 能力 | 不拉主实验，只在 related work 中引用 |
| OSWorld | 桌面系统 GUI agent | GLM-4.6V 37.2，低但和前端 design 距离远 | 2024-04 首发，NeurIPS 2024 D&B | 环境重；本地 VLM 可能 24-80GB，API agent 也需虚拟机/桌面环境 | 背景/暂缓 | 只保留为 GUI agent 上限证据 |
| AndroidWorld | Android GUI agent | GLM-4.6V 57.0 | 2024-05 首发，ICLR 2025 | Android 环境成本高；非前端 web design | 背景/暂缓 | 不进第一轮 |
| WebQuest | 网页序列 QA | GLM-4.6V SingleQA 79.5 | 2024-09 预印本 | API-only 可评，但任务是 QA | 背景 | 只作为网页理解背景 |
| Mind2Web | 真实网站动作预测 | AutoWebGLM avg 59.5，CogAgent 58.2 | 2023-06 首发，NeurIPS 2023 D&B Spotlight | offline action prediction 可 API；训练/本地模型需 GPU | P2 UI grounding 背景 | 如果做 browser repair agent，可用作 action grounding 参考 |
| AITW | Android 操作预测 | CogAgent 76.88 | 2023-07 首发，NeurIPS 2023 D&B | 移动端数据/模型路线，非前端主线 | 背景/暂缓 | 不进第一轮 |
| AutoWebBench | 中英文真实网页浏览 | AutoWebGLM overall SSR 62.7 | 2024-04 首发，KDD 2024 | API agent 可跑；真实网页环境需维护 | 背景：Zhipu framework 证据 | 用来回答“Zhipu 有 framework 跑 bench 吗”，不做 design 主实验 |
| MiniWoB++ | 模拟网页操作任务 | AutoWebGLM 89.3，偏饱和且环境老 | 2018-02 ICLR 2018 相关 | 环境轻，但任务离现代前端 design 远 | 背景/暂缓 | 不投入 |
| WebArena | 真实网站镜像 web agent | AutoWebGLM 18.2，低分但工程重且不是 design-to-code | 2023-07 首发，ICLR 2024 | 自托管环境重；API agent 可无 GPU但成本高 | 远期 browser agent 扩展 | 当前不拉，只保留远期 |
| VAB-WebArena-Lite | VisualAgentBench 中 web GUI 子集 | AutoGLM 55.2，pass@2 59.1 | 2024-08 首发，ICLR 2025 Poster | API agent 可无 GPU；环境比 VAB-CSS 更偏 web task | 背景/远期扩展 | 若 VAB-CSS 跑通，再考虑 |
| AndroidLab / VAB-Mobile | Android GUI agent | AutoGLM 36.2 | 2024-10 AutoGLM 预印本 | Android 环境和 agent 成本高 | 背景/暂缓 | 不进第一轮 |

## 还没进聚合页但建议下一批补入的 benchmark

这些来自可跑 framework 调研，和“能不能发论文”关系很强，后续应该补入 `data/web_display_data.json` 或单独开一个 web 子视图。

| Benchmark / Framework | 价值 | 初步优先级 |
|---|---|---|
| Interaction2Code | 交互原型到可交互网页，127 webpages / 374 interactions，ASE 2025；比静态截图更接近真实前端 | P0/P1 |
| DCGen real-world website set | FSE 2025，分块 UI-to-code，API-only 可跑，适合做 segment-aware baseline | P0/P1 |
| Figma2Code | ICLR 2026，Figma metadata + screenshot + assets，设计文件结构价值高 | P2 |
| ScreenBench / ScreenCoder | 1000 个真实网页截图和 HTML source，模块化 UI-to-code agent | P1/P2 |
| WebMMU Mockup2Code | EMNLP 2025，多语言网站理解、代码编辑和 mockup-to-code | P2 |
| WebGen-Bench | prompt-to-web-app / agent benchmark，系统级工程重 | P2/P3 |

## 下载/拉取顺序建议

第一轮不要全量 clone 或下载大数据。按这个顺序更稳：

1. Design2Code-HARD：小样本优先，先把渲染和指标跑通。
2. UIPolish-Real：确认 UI2Code_N evaluation 是否公开完整数据和已有输出。
3. WebPAI DesignBench：只拉 Vanilla/React 小样本，先看 repair 和 compile error repair。
4. VAB-CSS：先读 setup 和样例，确认 Docker/AgentBench 环境成本。
5. Vision2Web static level：只在前面三个跑通后进入。

这个顺序对应一个可写论文的最小闭环：一次生成 -> 渲染 -> 自动比较 -> 局部修复 -> rerank -> 记录 token/latency/API 成本。
