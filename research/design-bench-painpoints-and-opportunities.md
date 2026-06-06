# Design Bench 痛点、近年修复方向与可达成机会

最后更新：2026-06-02

## 总体判断

基于目前收集的资料，前端 design bench 的核心痛点已经不只是“模型不够强”，而是评测对象正在从静态截图还原，转向真实前端工程流程：

- 可运行
- 可修复
- 可交互
- 可复现
- 可解释成本
- 可跨框架泛化

如果目标是“改进刷分然后发论文”，最值得关注的不是单个榜单分数，而是如何把一次性 UI-to-code 变成可执行闭环：生成、渲染、比较、定位问题、局部修复、重新评估。

## 当前主要痛点

| 痛点 | 具体表现 | 对论文任务的含义 |
|---|---|---|
| 指标口径混乱 | CLIP、Block/Text/Position/Color、DINO、VLM Judge、SR、pass@k 不能直接混排 | 必须明确优化目标，否则 claim 会虚 |
| 视觉相似不等于前端可用 | 页面看起来像，但代码乱、不可维护、不可复用、不可交互 | 可以补 code quality / component structure 指标 |
| 一次生成不稳定 | 复杂页面、长页面、hard case 容易漏块、错位、样式漂移 | render-feedback 和局部修复是天然方向 |
| benchmark 太小或太干净 | Design2Code 484、Flame 80、UIPolish 100/100，容易过拟合 | 需要跨 benchmark 或 held-out hard subset |
| 真实网页太复杂 | WebCode2M-Long 有长代码、真实 DOM、assets、外部依赖 | 第一阶段不宜碰大训练，适合作压力测试 |
| 交互和状态难评 | Interaction2Code / Vision2Web 要检查 hover、click、状态变化 | 比静态截图更有论文价值，但工程成本高 |
| 多框架差异大 | React/Vue/Angular/Vanilla 的生成和修复方式不同 | DesignBench 适合做 framework-aware 方法 |
| API/GPU 成本不透明 | UI2Code^N、VAB-CSS、Vision2Web 都有 API judge 或本地模型成本 | 论文里要报告 token、latency、API/GPU，否则不可复现 |
| 人类偏好和自动指标不一致 | CLIP 不敏感，VLM Judge 也会有偏差 | 需要小规模 human eval 或 judge agreement |
| agent 环境重 | VAB-CSS、WebArena、OSWorld、Vision2Web 需要 Docker/浏览器/任务服务 | 不适合第一轮，但适合第二阶段扩展故事 |

## 近几年大家在修什么

| 方向 | 代表工作 | 修复的痛点 |
|---|---|---|
| 更真实的 UI-to-code benchmark | Design2Code、Design2Code-HARD | 从简单 synthetic 转到真实网页和 hard case |
| 更大规模数据 | Web2Code、WebCode2M | 缓解训练数据不足和泛化问题 |
| 更现代的前端框架 | Flame-React-Eval、DesignBench | 从 HTML/CSS 扩到 React、多框架代码 |
| 分块/组件化生成 | DCGen、ScreenCoder | 缓解复杂页面整体生成失败 |
| 闭环视觉反馈 | UI2Code^N、VAB-CSS、UIPolish | 从一次生成变成渲染后修复 |
| 修复/编辑任务 | DesignBench repair、UIPolish、VAB-CSS | 更贴近真实前端开发流程 |
| 交互网页 | Interaction2Code、Vision2Web | 从静态截图扩到交互和功能 |
| 设计 metadata | Figma2Code | 不只看截图，利用设计文件结构和 assets |

## 比较容易达成的点

| 优先级 | 点子 | 为什么容易 |
|---|---|---|
| P0 | 多候选生成 + VLM/CLIP/DINO rerank | 不训练模型，只加推理策略，API-only 可做 |
| P0 | render-feedback 一轮或多轮修复 | Playwright 渲染 + 截图 diff + 再 prompt，工程可控 |
| P0 | 局部 CSS patch | 比整页重写稳定，适合 Design2Code-HARD / UIPolish / VAB-CSS 思路 |
| P0 | compile error repair | DesignBench/React 任务很自然，容易量化 pass/fail |
| P0 | 错误类型 taxonomy | 跑少量样本就能沉淀：漏块、错位、颜色、字体、响应式、交互失败 |
| P1 | framework-aware prompt/template | React/Vue/Vanilla 分别生成和修复，成本低但有清晰 ablation |
| P1 | layout/component planning | 先让模型输出结构计划，再生成代码；不一定训练 |
| P1 | 指标聚合与分歧分析 | 把 CLIP、DINO、VLM Judge、人评小样本对齐，容易形成可信实验 |
| P1 | budget-aware repair | 固定 token/API 预算，比 UI2Code^N/agent pipeline 更便宜更快 |

## 最有希望的论文切口

### 1. Budget-aware Render-Feedback Repair for UI-to-Code

固定 API、token 和 latency 预算，用截图差异定位、局部 patch、rerank，提高 Design2Code-HARD / UIPolish / DesignBench repair。这个方向的优势是工程成本可控，claim 也比较清楚：同等预算下更稳、更省、更接近目标 UI。

### 2. Framework-Aware Visual Repair

针对 React、Vue、Vanilla 等不同框架生成不同修复策略。这个方向可以避免只做 HTML/CSS 的老问题，和 DesignBench / Flame-React-Eval 更贴近。

### 3. Disagreement-Aware Verifier

不盲信单个 VLM Judge，而是利用 CLIP、DINO、layout metrics、VLM judge 的分歧决定是否修复、修哪里。适合做 evaluator / verifier 贡献。

### 4. From Screenshot-to-Code to UI Polishing

把一次生成问题转成“先生成，再修复”的流程，对齐 UI2Code^N 和 VAB-CSS，但做得更轻、更可复现。

## 还需要补充的资料

1. 每个候选 benchmark 的真实输入输出样例：截图、code、evaluator output 各 3 个。
2. baseline outputs 是否公开：没有输出就要自己跑，成本会明显升高。
3. evaluator 的具体命令、judge 模型版本、prompt、随机性控制。
4. API 成本估算：每 100 样本大概多少美元、多少分钟。
5. 小规模 human eval 方案：例如 50 pair、2 annotators、win/tie/lose。
6. license / 数据使用限制，尤其是 WebCode2M、Figma2Code、真实网页数据。
7. 先跑 3-5 个 Design2Code-HARD 样本，拿真实失败案例反推方法。

## 建议的下一步

不要继续无限扩 benchmark。下一步建议选：

1. Design2Code-HARD
2. UIPolish-Real/Synthetic
3. Flame-React-Eval

先做一个最小实验设计，把 P0 点变成可跑 pipeline：

- API-only 多候选生成
- 渲染截图
- 自动差异分析
- 局部 CSS / code patch
- rerank
- 记录 token、latency、API 成本
- 对比 direct generation、self-revision、简单 rerank baseline

这样最容易从调研转到可写论文的实验闭环。
