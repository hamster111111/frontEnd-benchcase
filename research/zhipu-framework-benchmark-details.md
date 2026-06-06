# Zhipu Framework 跑过的 Benchmark 资料整理

最后更新：2026-06-02

## 结论先行

Zhipu / THUDM 相关 framework 跑过的 benchmark 可以分成两条线：

1. **主线 design / UI-to-code：** `UI2Code^N` 跑 `Design2Code`、`Flame-React-Eval`、`Web2Code`、`UI2Code-Real`、`UIPolish-Real/Synthetic`、`Design2Code-HARD`、`WebCode2M-Long`。这条线最适合我们后续做“render-feedback + verifier/reward + 多轮修复”的刷分框架。
2. **背景 Web/GUI agent：** `VisualAgentBench`、`AutoWebGLM`、`AutoGLM` 跑 `VAB-CSS`、`VAB-WebArena-Lite`、`AndroidLab/VAB-Mobile`、`AutoWebBench`、`Mind2Web`、`MiniWoB++`、`WebArena`。其中只有 `VAB-CSS` 是前端 visual design repair，其他主要是网页/手机/具身操作 agent 背景。

一句话：**如果目标是发前端 design bench 论文，重点看 UI2Code^N + VAB-CSS；AutoWebGLM/AutoGLM 只作为 Zhipu agent 积累和相关工作背景。**

## Framework 到 Benchmark 映射

| Framework | Zhipu 关系 | 跑的 benchmark | 主线判断 |
|---|---|---|---|
| `UI2Code^N` | Z.AI / Zhipu；基于 `GLM-4.1V-9B-Base` | `Design2Code`、`Flame-React-Eval`、`Web2Code`、`UI2Code-Real`、`UIPolish-Real/Synthetic`、`Design2Code-HARD`、`WebCode2M-Long` | 最重要，是 closed-loop UI-to-code / UI polishing 主线 |
| `VisualAgentBench / VAB-CSS` | THUDM / Tsinghua GLM 生态；ICLR 2025 | `VAB-CSS`、`VAB-WebArena-Lite`、`VAB-Mobile`、`VAB-OmniGibson`、`VAB-Minecraft` | `VAB-CSS` 直接相关，其余为 agent 背景 |
| `AutoWebGLM` | THUDM / Zhipu 生态；KDD 2024 | `AutoWebBench`、`Mind2Web`、`MiniWoB++`、`WebArena` | Web navigation agent，不是 design-to-code |
| `AutoGLM` | Zhipu AI + Tsinghua | `VAB-WebArena-Lite`、`OpenTable`、`AndroidLab / VAB-Mobile` | GUI foundation agent，不是前端设计生成 |

## UI2Code^N 主线 Benchmark

| Benchmark | 输入 | 输出 | 指标 | 规模 | UI2Code^N 结果/用途 |
|---|---|---|---|---|---|
| `Design2Code` | 网页参考截图；部分原论文 setting 可加文本增强 | HTML/CSS，重新渲染后和目标截图比较 | UI2Code^N 用 VLM Judge；原论文有 Block、Text、Position、Color、CLIP | 484 个真实网页 | `UI2Code^N-9B-RL` VLM Judge 88.6；传统指标 Block 88.7 / Text 93.1 / Position 83.8 / Color 72.6 / CLIP 80.5 |
| `Flame-React-Eval` | 设计截图、结构化 layout 描述、React gold implementation | React code + styling | compile success、non-error render、DINOv2 cosine > 0.9；原论文报 pass@1/3/5 | 80 个 curated React cases | `UI2Code^N-9B-RL` 95.0；适合现代 React 前端扩展实验 |
| `Web2Code` | 网页截图 + instruction；另有网页理解 QA | HTML code；网页理解任务输出 yes/no answer | Webpage Code Generation Benchmark 用 GPT-4V/VLM 评估渲染质量；Webpage Understanding Benchmark 用 QA accuracy | 约 1.18M instruction-response pairs；WUB 5,990 QA；WCGB 1,198 screenshots | `UI2Code^N-9B-RL` 92.5；适合泛化实验 |
| `UI2Code-Real` | 真实网页截图 | 前端代码 | VLM-based human-aligned score；可看 test-time scaling | 115 个真实网页 | `UI2Code^N-9B-RL` 76.5；N=1 到 N=5 有持续提升 |
| `UIPolish-Real` | 目标截图 A、当前渲染 B、生成 B 的 HTML/CSS | 修复后的 HTML/CSS | verifier / comparator / round-robin visual preference accuracy | 100 个真实网页 polishing samples | `UI2Code^N-9B-RL` 80.0；最贴近 render-feedback repair |
| `UIPolish-Synthetic` | 目标截图、初始渲染、对应 HTML/CSS | 修复后的 HTML/CSS | accuracy / verifier judgment；可做 test-time scaling | 100 个 synthetic webpages | `UI2Code^N-9B-RL` 94.0；适合可控 ablation |
| `Design2Code-HARD` | hard 网页截图 | HTML/CSS | DINO Acc、VLM Judge Acc、latency、token cost、human preference | 80 个 hard examples | `UI2Code^N-9B-RL` DINO 86.1、VLM Judge 88.6、约 40s、约 2600 token；用于对比 DCGen/ScreenCoder |
| `WebCode2M-Long` | 真实网页 design image；数据含 bbox、HTML/CSS、语言、token 统计 | HTML/CSS | CLIP similarity、Visual Score、TreeBLEU | WebCode2M 训练集 2,563,905；Long test 256，代码 4098-10990 tokens | `UI2Code^N-9B-RL` CLIP 0.79 ± 0.09；长网页压力测试 |

### 对我们最有用的点

- `Design2Code-HARD` 很适合拿来证明方法比 agent pipeline 更省 token、更快。UI2Code^N 对比了 `DCGen`、`ScreenCoder`，报告 `UI2Code^N-9B-RL` 在 VLM Judge 和 token cost 上更强。
- `UIPolish-Real/Synthetic` 是最接近“看渲染结果再改”的任务。如果我们要做论文，最自然的方向是把一次生成扩展为局部修复、比较器选择、round-robin rerank 或 verifier-guided patch。
- `Flame-React-Eval` 可以作为 React 前端任务扩展，不要只停在 HTML/CSS。
- `WebCode2M-Long` 证明长代码网页生成非常难，但下载/训练成本高，不建议第一轮跑。

## VisualAgentBench / VAB 相关 Benchmark

| Benchmark | 输入 | 输出 | 指标 | 规模 | Zhipu/THUDM 结果/用途 |
|---|---|---|---|---|---|
| `VAB-CSS` | 目标设计截图、当前错误页面截图、HTML、自然语言差异描述、CSS rule 工具 | 多轮 CSS rule edits | Success Rate；final SSIM > 0.9；也看 Improve Rate | 1,210 instances；test 165；train trajectories 829；action space 4；max round 10 | `GLM-4V` fine-tuning SR 23.6；`CogAgent` 13.9；`GPT-4o` prompting 34.5 |
| `VAB-WebArena-Lite` | 网页任务指令、视觉观察/SoM 标注、可操作 HTML elements | Playwright/browser actions | task success rate / pass rate | WebArena 812 tasks 清洗成 165-task subset；train 1,186；action space 12；max round 20 | `AutoGLM` 55.2% SR；pass@2 59.1 |
| `VAB-Mobile / AndroidLab` | Android GUI visual state + task instruction | Android device actions | task success rate | VAB-Mobile: test 119；train trajectories 1,213；action space 7；max round 25 | `AutoGLM` AndroidLab SR 36.2；中文 Android app human eval 89.7 |
| `VAB-OmniGibson / VAB-Minecraft` | embodied 环境视觉观察 + 指令 | 环境动作序列 | task success rate | OmniGibson test 181；Minecraft test 116 | 只作为 visual foundation agent 背景，不进前端主实验 |

### VAB-CSS 对我们为什么重要

`VAB-CSS` 不是“从零截图转代码”，而是 **CSS repair / visual design repair**。这对我们很有启发：真实前端工作里很多时候不是重写整个页面，而是定位视觉差异、调整局部 CSS、渲染检查、继续修。它的 action space 很小，只有 4 类工具，但任务要求细粒度视觉 grounding 和多轮决策。

如果我们想把 `Design2Code` 或 `DesignBench` 做成可发论文的刷分框架，可以借鉴 `VAB-CSS` 的思想，但要改造成更贴近 screenshot-to-code 的闭环：先生成初版，再局部 patch，而不是单纯编辑预置 CSS rule。

## AutoWebGLM / AutoGLM 背景 Benchmark

| Benchmark | 属于谁跑 | 输入/任务 | 指标 | 规模/结果 | 是否设计主线 |
|---|---|---|---|---|---|
| `AutoWebBench` | AutoWebGLM | 中英双语真实网页浏览任务 | Step Success Rate | 每个 split 50 traces；AutoWebGLM 英文 cross-task 64.8、英文 cross-domain 58.6、中文 cross-task 65.4、中文 cross-domain 61.8 | 否 |
| `Mind2Web` | AutoWebGLM | 真实网站任务、候选 DOM elements | element accuracy、operation F1、step SR、task SR | 2,350 tasks、137 websites、31 domains；AutoWebGLM average 59.5 | 否 |
| `MiniWoB++` | AutoWebGLM | simulated web interaction | success rate | AutoWebGLM 按 56 tasks × 100 episodes 跑；结果 89.3 | 否 |
| `WebArena` | AutoWebGLM / VAB-WebArena-Lite 来源 | 真实可托管网站上的高层任务 | functional task success | 原始 812 tasks；AutoWebGLM 18.2；VAB-WebArena-Lite 是 165-task subset | 否 |
| `OpenTable` | AutoGLM | 真实订餐/预约网站任务 | success rate | AutoGLM 96.2 | 否 |

这些 benchmark 的价值主要是 related work：说明 Zhipu/THUDM 在 Web/GUI agent 上有框架和 RL 经验。它们不应该和 `Design2Code`、`UIPolish`、`VAB-CSS` 放到同一个前端设计分数榜里。

## 口径风险

1. **指标不能混排。** `UI2Code^N` 的 VLM Judge、`Flame` 的 DINOv2 pass@k、`Design2Code` 原始 CLIP/Block 指标、`VAB` 的 SR 是不同口径。
2. **VAB-CSS 不是从零生成。** 它给了 HTML/CSS 和错误页面，agent 做 CSS repair。把它叫 design repair 更准确。
3. **UI2Code-Real / UIPolish 是 UI2Code^N 自建 benchmark。** 论文价值高，但要继续确认数据和 evaluator 是否完整公开。
4. **Web agent 背景不要抢主线。** AutoWebGLM/AutoGLM 很有用，但它们跑的是 Web navigation / GUI operation，不是前端 design-to-code。

## 后续实验优先级

1. `Design2Code-HARD`：先复现少量样本，验证渲染和指标；可以做多轮 repair 对比。
2. `UIPolish-Real/Synthetic`：最适合做 verifier-guided patch / round-robin rerank。
3. `Flame-React-Eval`：扩展到 React 前端，增强论文覆盖面。
4. `VAB-CSS`：借鉴工具式 CSS repair，但不直接作为 screenshot-to-code 主榜。
5. `WebCode2M-Long`：作为长网页压力测试，等轻量主线跑通后再看。

## 主要来源

- UI2Code^N arXiv: https://arxiv.org/html/2511.08195v3
- UI2Code^N repo: https://github.com/zai-org/UI2Code_N
- Design2Code project: https://salt-nlp.github.io/Design2Code/
- Design2Code repo: https://github.com/NoviScl/Design2Code
- Design2Code-HARD dataset: https://huggingface.co/datasets/SALT-NLP/Design2Code-HARD
- Flame paper: https://arxiv.org/pdf/2503.01619
- Flame repo: https://github.com/Flame-Code-VLM/Flame-Code-VLM
- Flame-Eval-React dataset: https://huggingface.co/datasets/Flame-Code-VLM/Flame-Eval-React
- Web2Code paper: https://arxiv.org/html/2406.20098
- Web2Code repo: https://github.com/MBZUAI-LLM/web2code
- WebCode2M project: https://webcode2m.github.io/
- WebCode2M paper: https://arxiv.org/html/2404.06369
- WebCode2M dataset: https://huggingface.co/datasets/xcodemind/webcode2m
- VisualAgentBench paper: https://arxiv.org/html/2408.06327
- VisualAgentBench ICLR page: https://proceedings.iclr.cc/paper_files/paper/2025/hash/eea71dc576381b88f2a0ca4dedc2140d-Abstract-Conference.html
- VisualAgentBench repo: https://github.com/THUDM/VisualAgentBench
- VAB-WebArena-Lite: https://github.com/THUDM/VisualAgentBench/tree/main/VAB-WebArena-Lite
- AutoWebGLM paper: https://arxiv.org/html/2404.03648v2
- AutoWebGLM repo: https://github.com/THUDM/AutoWebGLM
- Mind2Web project: https://osu-nlp-group.github.io/Mind2Web/
- Mind2Web repo: https://github.com/OSU-NLP-Group/Mind2Web
- AutoGLM paper: https://arxiv.org/html/2411.00820v1
- AutoGLM project: https://xiao9905.github.io/AutoGLM/
