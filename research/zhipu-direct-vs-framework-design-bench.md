# Zhipu / GLM 跑 Design Bench：直接模型还是 Framework？

最后更新：2026-06-02

## 一句话结论

**两种都有，但目前公开证据里要分清楚：**

- **GLM-4.1V / GLM-4.5V / GLM-4.6V / GLM-5V-Turbo** 的 design bench 多数是模型级直接评测，属于“模型本身拿去跑 benchmark”。
- **UI2Code^N** 是真正面向 UI-to-code / UI polishing 的 closed-loop framework，带渲染反馈、test-time scaling 和 RVPO 训练，属于“用 framework 去提高 design bench 表现”。
- **VisualAgentBench / VAB-CSS** 是 agentic visual design / CSS repair benchmark+framework，属于“通过 agent 工具编辑 CSS 来修页面”，但不是传统 Design2Code 截图到 HTML 的主线。
- **AutoWebGLM / AutoGLM / CogAgent** 是 Web/GUI agent 线，能说明 Zhipu/THUDM 有 agent 框架积累，但它们跑的是 Web/GUI 操作 benchmark，不是 design-to-code 主 benchmark。

这些 framework 实际跑过的 benchmark 输入、输出、指标、规模和口径，详见 `research/zhipu-framework-benchmark-details.md`。

## 分类表

| 系统 | 是直接模型跑分吗 | 是 framework 吗 | 跑的 benchmark | 论文/发表状态 | 是否顶会 |
|---|---|---|---|---|---|
| GLM-4.1V / 4.5V / 4.6V | 是 | 否，公开证据主要是模型报告 | Design2Code、Flame-React-Eval、WebVoyager、OSWorld、AndroidWorld、WebQuest | arXiv 技术报告 | 未见顶会正式发表证据 |
| GLM-5V-Turbo | 是 | 否，虽然可接 Claude Code/OpenClaw 等 agent workflow | Design2Code、Flame-VLM-Code、Vision2Web、CC-Frontend、WebVoyager | arXiv 技术报告 + 官方文档 | 未见顶会正式发表证据 |
| UI2Code^N | 不是简单 direct；是模型+闭环优化系统 | 是，closed-loop UI-to-code framework | Design2Code、Flame-React-Eval、Web2Code、UI2Code-Real、UIPolish、Design2Code-HARD、WebCode2M-Long | repo citation 标注 ICML 2026；OpenReview/PDF 仍有 ICLR submitted 字样 | 按 repo citation 是顶会 |
| VisualAgentBench / VAB-CSS | 不是 direct；是 agentic benchmark/framework | 是，CSS repair agent framework | VAB-CSS、VAB-WebArena-Lite、VAB-Embodied 等 | ICLR 2025 | 是，顶会 |
| AutoWebGLM | 否 | 是，Web navigation agent | AutoWebBench、Mind2Web、WebArena、MiniWoB++ | KDD 2024 | 是，顶会，但不是 design bench |
| AutoGLM / Open-AutoGLM | 否 | 是，GUI/Web/Phone agent | VAB-WebArena-Lite、OpenTable、AndroidLab/VAB-Mobile | arXiv / project page | 未见顶会正式发表证据 |
| CogAgent | 偏模型/agent model | 不是专门刷 design bench 的 framework | Mind2Web、AITW；在 VAB-CSS 中有结果 | arXiv | 未见顶会正式发表证据 |

## 对“刷 design bench”的判断

### 1. 直接模型跑分线

GLM-4.5V/4.6V 和 GLM-5V-Turbo 的公开报告更像直接模型评测：给模型输入截图、网页/GUI任务或前端题目，然后按对应 benchmark 协议打分。这里的收益主要来自模型训练、数据、推理能力，而不是公开额外的 benchmark-specific agent pipeline。

这类分数适合做横向展示，但如果我们要“改进刷分然后发论文”，直接复刻模型报告路线很难，因为我们没有同等训练资源，也不容易把贡献讲清楚。

### 2. UI2Code^N：真正值得重点看的 framework 线

UI2Code^N 明确把 UI-to-code 做成闭环优化问题：先生成代码，再渲染成图，再比较视觉差异，然后继续 polish。它还引入 RVPO 训练和 test-time scaling。

它跑的 benchmark 很全：Design2Code、Flame-React-Eval、Web2Code、UI2Code-Real、UIPolish-Real/Synthetic、Design2Code-HARD、WebCode2M-Long。对我们最有价值的不是单个分数，而是它说明了一条论文方向：**render-feedback + verifier/reward + 多轮优化** 可以成为 design bench 的刷分 framework。

### 3. VAB-CSS：agentic repair 线

VAB-CSS 不是截图到整页 HTML，而是 CSS repair：给目标截图、错误截图、HTML 和差异描述，agent 用工具修改 CSS rule。它适合研究“前端视觉修复 agent”，而不是纯 UI-to-code。

它的价值在于能把我们的方法从一次生成扩展到“看渲染结果再改”。如果我们做 Design2Code/DesignBench 的 repair 任务，可以借鉴 VAB-CSS 的 action space、success rate、improvement rate。

### 4. AutoWebGLM / AutoGLM：agent 背景线

AutoWebGLM 已发表在 KDD 2024，但它主要是网页导航 agent，不是前端设计生成。AutoGLM 则是更大的 GUI foundation agent，跑 VAB-WebArena-Lite、AndroidLab 等。

它们可以放在相关工作里说明 Zhipu/THUDM 在 Web/GUI agent 上有积累，但不能直接当作 design bench 刷分框架。

## 给我们任务的建议

如果师兄问“Zhipu 是不是有 framework 刷 design bench”，建议回答：

1. **GLM-5V-Turbo 等模型报告里的 design bench，多数应理解为模型级 direct evaluation。**
2. **真正可以称为 UI-to-code 刷分 framework 的是 UI2Code^N。它是 Zhipu/Z.AI 相关，repo 标注 ICML 2026，跑了 Design2Code、Flame、Web2Code、UIPolish 等。**
3. **VisualAgentBench/VAB-CSS 是 THUDM/GLM 生态的 agentic visual design framework，ICLR 2025，跑 CSS repair，不是传统截图到代码。**
4. **AutoWebGLM 是 KDD 2024 顶会 agent framework，但跑 Web navigation benchmark，不跑 design-to-code。**
5. **我们最值得仿照和改进的是 UI2Code^N + VAB-CSS 之间的交集：render-feedback、多轮修复、局部 CSS patch、verifier/reward。**

## 主要来源

- GLM-4.5V / GLM-4.1V report: https://arxiv.org/abs/2507.01006
- GLM-5V-Turbo docs: https://docs.z.ai/guides/vlm/glm-5v-turbo
- GLM-5V-Turbo report: https://arxiv.org/abs/2604.26752
- UI2Code^N repo: https://github.com/zai-org/UI2Code_N
- UI2Code^N paper: https://arxiv.org/abs/2511.08195
- UI2Code^N OpenReview: https://openreview.net/forum?id=i5Y3OD7NQB
- VisualAgentBench ICLR 2025: https://proceedings.iclr.cc/paper_files/paper/2025/hash/eea71dc576381b88f2a0ca4dedc2140d-Abstract-Conference.html
- VisualAgentBench repo: https://github.com/THUDM/VisualAgentBench
- AutoWebGLM KDD 2024 DBLP: https://dblp.org/rec/conf/kdd/LaiLIYCSYZZD024
- AutoWebGLM repo: https://github.com/THUDM/AutoWebGLM
- AutoGLM project: https://xiao9905.github.io/AutoGLM/
- AutoGLM paper: https://arxiv.org/abs/2411.00820
