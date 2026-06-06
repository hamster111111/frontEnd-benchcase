# 可跑 Framework 复现核验表

最后更新：2026-06-02

## 目的

这份表专门记录每个候选 benchmark/framework 的工程可跑性，供后面决定主实验路线。重点字段是：

- 代码是否公开
- 数据是否公开
- 评测脚本是否公开
- 本地环境依赖
- 是否需要商业 API
- 是否需要 GPU
- 预计工程成本
- 可刷分入口
- 下一步 smoke test

结论先行：**Design2Code、Interaction2Code、DesignBench、DCGen 最适合先做可跑性验证；VAB-CSS、UI2Code^N、Vision2Web、WebGen-Bench 更适合第二阶段，因为工程依赖或成本更高。**

补充资料：近年顶会/强会 framework 与对应 benchmark 已单独整理到 `research/recent-top-venue-design-frameworks.md`，并同步进 web 展示的“可跑 Framework”页。

## 复现优先级总表

| Framework | 代码 | 数据 | 评测脚本 | API 依赖 | GPU 依赖 | 工程成本 | 优先级 | 判断 |
|---|---|---|---|---|---|---|---|---|
| Design2Code / HARD | 公开 | HF + Drive | 公开 | 跑商业模型需要 | 仅跑 API/评测不需要；跑/训开源模型需要 | 低-中 | P0 | 最适合先跑 smoke test。 |
| Interaction2Code | 公开 | HF + Drive | 公开 | 跑 GPT/Claude/Gemini/Qwen 需要 | 仅 API 路线不需要 | 中 | P0 | 静态 UI-to-code 的自然扩展，值得优先跑。 |
| DesignBench | 公开 | Google Drive | 公开 | 多 API key | API 路线不需要 | 中-高 | P0/P1 | 多框架、多任务，论文价值高但环境较复杂。 |
| DCGen | 公开 | HF + sample | 公开 | 默认 GPT-4/GPT-4o 类 API | API 路线不需要 | 中 | P0/P1 | segment-aware baseline，适合做方法对比。 |
| Web2Code | 公开 | HF | 公开 | 视模型而定 | 训练/本地模型需要 | 中 | P1 | 数据和训练价值高，适合作泛化/训练线。 |
| VAB-CSS | 公开 | repo/ModelScope | 公开 | 可接 GPT-4o 等 API | 只 API 不需要；训练 open LMM 需要 | 高 | P1 | Agentic CSS repair，方法潜力高。 |
| UI2Code^N | 公开 | 预处理数据需下载 | 公开 | judge 默认可用 OpenAI 类 API | 本地跑 UI2Code^N 需要 GPU | 高 | P1 | 和 Zhipu 生态强相关，适合第二阶段重点核对。 |
| Vision2Web | 公开 | HF | 公开 | LiteLLM/Claude Code/OpenHands/API judge | API 路线不需要训练 GPU | 高 | P1/P2 | 完整网站开发，价值高但成本重。 |
| WebGen-Bench | 公开 | repo 内置 + HF | 公开 | OpenRouter/OpenAI-like 等 | 自部署 Qwen2.5-VL-32B 需 4 GPU | 很高 | P2 | 更像 agent/web-app 系统工程。 |
| Figma2Code | 数据公开 | HF | 未确认官方代码 | 视实现而定 | 视实现而定 | 中-高 | P2 | metadata 方向价值高，但先确认代码。 |
| PSD2Code | 未确认 | 论文称有约 100 PSD 样本 | 未确认 | 视实现而定 | 视实现而定 | 未知 | P3 | 先作为 design-file-to-code 思路储备。 |
| ScreenCoder / ScreenBench | 公开 | HF | 部分公开 | Doubao/Qwen/GPT/Gemini API | 本地训练需要 | 中-高 | P1/P2 | 多 agent + UIED，适合方法参考。 |
| VisualWebBench | 公开 | HF | 公开 | 视模型而定 | 视模型而定 | 低-中 | 背景 | 偏网页理解/grounding，不是设计生成主实验。 |
| App-Bench | 网站公开 | 分析数据需继续确认 | 人工评分为主 | N/A | N/A | 高 | 背景 | 产品/agent 趋势参考，不适合学术主实验。 |

## 静态目录评估（未 clone）

本节只基于 GitHub contents API、README 和项目介绍做判断，没有 clone 仓库，也没有安装依赖。

| Framework | 根目录/关键目录信号 | 静态复杂度 | 目录层判断 |
|---|---|---:|---|
| Design2Code | 根目录包含 `requirements.txt`、`setup.py`、`Design2Code/data_utils`、`Design2Code/metrics`、`Design2Code/prompting` | 2/5 | 结构集中，metric 和 prompting 分离清楚，适合第一个 smoke test。 |
| DCGen | 根目录包含 `requirements.txt`、`utils.py`、`data`、`scripts/evaluate.py`、`scripts/experiments.py`、`Tool` | 2/5 | pipeline 较短，demo/evaluate 入口明确；主要成本是 API 和 Playwright/metric 环境。 |
| Interaction2Code | 根目录包含 `sample`、`example`、`human_evaluation`；`code/annotation`、`code/metric`、`code/prompting` | 3/5 | 结构清晰但涉及网页交互执行，复杂度高于静态 UI-to-code。 |
| DesignBench | 根目录包含 `designbench.yml`、`code/evaluator`、`code/mllm`、`code/prompt`、`code/runner`、`web` | 3.5/5 | 工程结构完整，但多框架、多任务、多服务，环境比 Design2Code 重。 |
| Web2Code | 根目录包含 `code_generation`、`webpage_understanding`、`web2code`；`code_generation` 内有 `cli.py`、`evaluate.py`、`gpt4_vision_evaluation.py` | 3/5 | code generation 和 understanding 分开，适合后续看训练/大规模数据线。 |
| UI2Code^N | 根目录包含 `demo`、`evaluation`、`assets`；`evaluation/scripts` 和 `evaluation/readme.md` 明确 | 3.5/5 | 评测链清楚，但本地跑模型/生成预测需要 GPU 或外部推理服务。 |
| ScreenCoder | 根目录有 `main.py`、`block_parsor.py`、`html_generator.py`、`image_replacer.py`、`UIED`、`post-training` | 3.5/5 | 单样本推理看起来不重；post-training 和 benchmark 复现会变重。 |
| VAB-CSS | VisualAgentBench 根目录有 `configs`、`src`、`scripts`、`docs/detailed_setups/VAB-CSS.md`、`VAB-WebArena-Lite` | 4/5 | AgentBench 式任务服务和多环境架构，适合第二阶段，不适合第一轮轻跑。 |
| Vision2Web | 根目录有 `docker`、`docs`、`scripts/run_inference.sh`、`scripts/run_evaluation.sh`、`vision2web` | 4/5 | 官方脚本清楚，但需要 Docker、agent framework、VLM judge、GUI agent。 |
| WebGen-Bench | 根目录有 `data`、`outputs.zip`、`webvoyager`、`src`、`src-remote`；`src` 下有 Bolt/OpenHands/Aider/WebGen 多套测试目录 | 5/5 | 明显是系统级 agent benchmark，先不作为第一轮。 |

静态目录结论：

1. **最轻且最值得先碰**：Design2Code、DCGen。
2. **中等复杂但论文价值高**：Interaction2Code、DesignBench、Web2Code。
3. **Zhipu 相关但需要 GPU/API judge**：UI2Code^N。
4. **重型 agent 系统**：VAB-CSS、Vision2Web、WebGen-Bench。
5. **方法参考优先**：ScreenCoder、Figma2Code、PSD2Code、VisualWebBench、App-Bench。

## P0 候选详表

### Design2Code / Design2Code-HARD

来源：

- repo: https://github.com/NoviScl/Design2Code
- paper: https://arxiv.org/abs/2403.03163
- dataset: https://huggingface.co/datasets/SALT-NLP/Design2Code
- hard dataset: https://huggingface.co/datasets/SALT-NLP/Design2Code-HARD

公开情况：

- 代码：公开。
- 数据：Design2Code 484 对截图/HTML；Design2Code-HARD 80 对截图/HTML。
- 评测：`metrics/multi_processing_eval.py`，输出 Block、Text、Position、Color、CLIP 等。
- 预测：公开 GPT-4V、Gemini、WebSight、Design2Code-18B 等预测结果。

环境：

- Python 3.11。
- `pip install -e .`
- Playwright 浏览器：`playwright install`。
- 跑 prompting 需要 API key：OpenAI/Gemini/Claude。

成本判断：

- 只跑已有预测和评测：成本低。
- 跑商业模型全量 484/80：API 成本中等。
- 跑或训练 Design2Code-18B：GPU 成本高。

可刷分入口：

- self-revision。
- text-augmented prompting。
- 多候选生成 + CLIP/VLM rerank。
- render-feedback 局部修复。
- hard set 上做 layout planning / component planning。

建议 smoke test：

1. clone repo。
2. 下载 hard set 80 个样本。
3. 跑 3-5 个样本的截图渲染和 metric。
4. 用一个 API 模型生成 3-5 个 HTML。
5. 验证 metric pipeline 可复现。

### Interaction2Code

来源：

- repo: https://github.com/WebPAI/Interaction2Code
- paper: https://arxiv.org/abs/2411.03292
- dataset: https://huggingface.co/datasets/whale99/Interaction2Code

公开情况：

- 代码：公开，包含 `code/prompting`、`code/metric`、annotation tool。
- 数据：127 个网页、374 个交互，HF 和 Google Drive。
- 评测：自动交互网页并计算 full page / interact 指标。

环境：

- Python + JavaScript/HTML/CSS。
- API key：Gemini、GPT、Claude、Qwen。
- 需要能打开/交互生成网页，可能依赖浏览器环境。

成本判断：

- 数据小，API 成本低-中。
- 工程复杂度中等，主要在交互执行和 metric pipeline。
- 不需要本地 GPU，除非自部署模型。

可刷分入口：

- interactive element highlighting。
- failure-aware prompting。
- visual saliency enhancement。
- visual-textual descriptions combination。
- 事件/状态转移 planning。

建议 smoke test：

1. 下载 sample 或 HF dataset。
2. 跑 1 个 webpage 的 direct/cot/mark prompt。
3. 生成 HTML 后跑 `code/metric`。
4. 检查 interact flag、CLIP、SSIM、Text、Position 是否输出。

### WebPAI DesignBench

来源：

- repo: https://github.com/WebPAI/DesignBench
- paper: https://arxiv.org/abs/2506.06251
- project: https://webpai.github.io/DesignBench/

公开情况：

- 代码：公开。
- 数据：Google Drive。
- 评测：generation/edit/repair/compile repair 对应 evaluator。
- 支持框架：React、Vue、Angular、Vanilla。

环境：

- conda 环境：`designbench.yml`。
- Node/npm/nvm。
- Chrome、Firefox、geckodriver。
- `single-file-cli`。
- React/Vue/Angular demo 项目需要分别启动。
- API key：Gemini、OpenAI、DeepInfra、Qwen、Anthropic、Mistral。

成本判断：

- 只跑少量样本：中等。
- 全量跨 4 framework × 多任务 × 多模型：成本高。
- API 路线不需要 GPU。

可刷分入口：

- framework-aware prompting。
- image/code/both mode 选择。
- repair 任务做局部 patch。
- compile error repair 加代码诊断。
- 多候选 + MLLM judge。

建议 smoke test：

1. 建 conda 环境。
2. 下载少量数据到 `data/`。
3. 只选 Vanilla 或 React generation 跑 2 个样本。
4. 跑对应 evaluator，确认 CLIP/SSIM/CSR/MLLM score 是否能出。

### DCGen

来源：

- repo: https://github.com/WebPAI/DCGen
- paper: https://arxiv.org/abs/2406.16386
- dataset: https://huggingface.co/datasets/iforgott/DCGen

公开情况：

- 代码：公开。
- 数据：sample 在 repo，全量在 HuggingFace。
- 评测：`scripts/evaluate.py`；fine-grained metrics 在 Linux/macOS 更可靠。

环境：

- Python requirements。
- Playwright。
- 需要 GPT-4/GPT-4o 类 API 或可替代模型 API。

成本判断：

- sample 小跑成本中等。
- 全量跑 API 成本中-高。
- 不需要 GPU，除非自部署模型。

可刷分入口：

- 更好的 image segmentation。
- segment-level verifier。
- 局部重生成。
- 全局 layout reassembly。
- segment-to-component mapping。

建议 smoke test：

1. 跑 repo demo image。
2. 对比 direct baseline 和 dcgen pipeline。
3. 跑 `scripts/evaluate.py` 输出视觉指标。
4. 检查 Linux/macOS metric 依赖，Windows 可能需要绕开。

## P1/P2 高潜力候选

### Web2Code

来源：

- repo: https://github.com/MBZUAI-LLM/web2code
- paper: https://arxiv.org/abs/2406.20098
- dataset: https://huggingface.co/datasets/MBZUAI/Web2Code

公开情况：

- 代码：公开。
- 数据：HuggingFace，MIT license。
- 评测：包含 webpage code generation benchmark 和 webpage understanding benchmark。
- 训练：training code 和 checkpoint 已释放。

环境/成本：

- 需要看 `code_generation/README.md` 和 `webpage_understanding/README.md` 细节。
- 评测应该可本地跑；训练/本地模型会需要 GPU。

定位：

- 比 Design2Code 更偏大规模数据和训练线。
- 如果我们想做 SFT/RL/data synthesis，可以作为重要数据源。

### VAB-CSS

来源：

- repo: https://github.com/THUDM/VisualAgentBench
- paper: https://arxiv.org/abs/2408.06327

公开情况：

- 代码：公开。
- 数据：包含 test/train split 和 trajectory training set。
- 评测：基于 AgentBench framework，VAB-CSS 有独立 setup 文档。

环境：

- Python 3.9。
- Docker。
- task worker / assigner 架构。
- `configs/tasks/css.yaml` 配置任务。
- 需要稳定截图环境；官方提到必要时用 Docker screenshot 环境。

成本判断：

- API agent 路线不一定需要 GPU。
- 如果训练 open LMM，需要 GPU。
- 工程成本高于 Design2Code。

可刷分入口：

- CSS patch agent。
- 多轮 visual feedback。
- action planning。
- state memory。
- verifier-guided repair。

### UI2Code^N

来源：

- repo: https://github.com/zai-org/UI2Code_N
- paper: https://arxiv.org/abs/2511.08195
- model: https://huggingface.co/zai-org/UI2Code_N

公开情况：

- 模型：公开，基于 GLM-4.1V-9B-Base。
- 评测：`evaluation/readme.md` 公开流程。
- benchmark：Design2Code、Flame-React-Eva、Web2Code、UI2Code-Real、UIPolish-Real、UIPolish-Synthetic。

环境：

- `transformers==4.57.1`
- `torch`
- 可选 `vllm==0.10.2`、`sglang==0.5.2`
- `playwright`
- 评测需要先生成预测，再抽取 HTML、渲染、调用 judge、统计 accuracy。
- judge 示例使用 `o4-mini-2025-04-16`，需要 OpenAI-compatible API。

成本判断：

- 本地跑 9B VLM：需要 GPU。
- 只跑已有输出的 evaluation：主要是渲染 + judge API 成本。
- 和 Zhipu 主线强相关，值得单独花时间核对。

可刷分入口：

- test-time scaling。
- UI polishing reward/verifier。
- round-robin comparator。
- render-feedback 多轮优化。

### Vision2Web

来源：

- repo: https://github.com/zai-org/Vision2Web
- project: https://vision2web-bench.github.io/
- dataset: https://huggingface.co/datasets/zai-org/Vision2Web
- paper: https://arxiv.org/abs/2603.26648

公开情况：

- 代码：公开。
- 数据：HF。
- 评测：本地 inference/evaluation/analysis scripts 公开；官方 leaderboard 由维护者最终评测。

环境：

- Python 3.8+。
- Docker。
- LiteLLM proxy 推荐。
- agent framework：`claude_code` 或 `openhands`。
- evaluation 需要 GUI agent model 和 VLM judge model。

成本判断：

- 工程成本高。
- API 成本高，因为包含 agent inference + GUI testing + VLM visual judging。
- 适合作第二阶段主打完整网站开发，不适合作第一个 smoke test。

可刷分入口：

- agent framework 改造。
- workflow-aware planning。
- visual/function 双 judge。
- static -> interactive -> full-stack 分层优化。

### WebGen-Bench

来源：

- repo: https://github.com/mnluzimu/WebGen-Bench
- paper: https://arxiv.org/abs/2505.03733
- dataset: https://huggingface.co/datasets/luzimu/WebGen-Bench

公开情况：

- 代码：公开。
- 数据：repo 内有 data，HF/Kaggle 也有。
- 输出：论文测试过的 agent outputs 放在 `outputs.zip`。
- 支持评测 Bolt.diy、OpenHands、Aider。

环境：

- Node.js。
- `pm2`。
- WebVoyager conda 环境。
- Bolt.diy fork + pnpm。
- OpenHands Docker runtime。
- Aider fork。
- OpenRouter/OpenAI-like API。
- 如果自部署 Qwen2.5-VL-32B 做 UI agent，需要 4 GPU。

成本判断：

- 工程成本很高。
- 适合做 agent/web-app builder 方向，不适合第一轮跑。

可刷分入口：

- agent scaffold。
- UI agent evaluator。
- appearance scoring。
- functional test recovery。
- training data filtering。

## 设计文件方向

### Figma2Code

来源：

- OpenReview: https://openreview.net/forum?id=CaXZB6bI31
- dataset: https://huggingface.co/datasets/xcodemind/Figma2Code

公开情况：

- 数据：HF，2817 rows，约 17GB。
- 每个样本含 root screenshot、raw/processed Figma metadata、image refs、SVG assets。
- 代码：未确认官方代码仓库。

成本判断：

- 数据下载成本中高。
- 如果自己搭 pipeline，工程成本中高。

价值：

- 很适合做“metadata-aware design-to-code”，和 screenshot-only 方法形成清晰区别。

### PSD2Code

来源：

- paper: https://arxiv.org/abs/2511.04012

公开情况：

- 论文描述约 100 个 PSD 样本，含 PSD、截图、assets、ground-truth React+SCSS、rendered outputs。
- 代码/数据是否公开未确认。

价值：

- 方法思路值得吸收：Parse-Align-Generate / design metadata grounding。
- 目前不适合作主实验，除非后续找到数据或自己构造小集。

## 背景/参考类

### ScreenCoder / ScreenBench

来源：

- repo: https://github.com/leigest519/ScreenCoder
- dataset: https://huggingface.co/datasets/Leigest/ScreenCoder

公开情况：

- 代码：公开，Apache-2.0。
- 数据：ScreenBench，1000 个真实网页截图和 HTML source。
- 支持 Doubao、Qwen、GPT、Gemini API。
- repo 公开 SFT + RL post-training 代码。

价值：

- 更像方法参考和 baseline，而不是标准 benchmark 首选。
- UIED + modular multi-agent 路线值得借鉴。

### VisualWebBench

来源：

- repo: https://github.com/VisualWebBench/VisualWebBench
- paper: https://arxiv.org/abs/2404.05955
- dataset: https://huggingface.co/datasets/visualwebbench/VisualWebBench

定位：

- 网页理解、OCR、grounding、action prediction。
- 可跑性较好，但不是 design generation 主线。

### App-Bench

来源：

- website: https://appbench.ai/

定位：

- Web app builder 趋势参考。
- 人工评分为主，任务少，非学术 benchmark。
- 可用于观察 agent 产品差距，不建议作为论文主实验。

## 推荐下一步

### 第一轮 smoke test

按这个顺序做：

1. Design2Code-HARD：跑 5 个样本，验证渲染和 metric。
2. Interaction2Code：跑 1 个交互网页，验证生成和 interact metric。
3. DCGen：跑 demo，比较 direct vs segment-aware。
4. DesignBench：只跑 Vanilla/React generation 各 1-2 个样本。

### 第二轮 heavy test

第一轮跑通后再做：

1. UI2Code^N evaluation pipeline。
2. VAB-CSS CSS repair agent。
3. Vision2Web static webpage level。
4. WebGen-Bench 的 Bolt.diy 或 OpenHands 路线。

### 需要立刻补查

1. FLAME/Flame-React-Eval 的 evaluation code 是否和 paper 结果完全对应。
2. Figma2Code 是否有官方代码仓库。
3. PSD2Code 是否有开源代码/数据。
4. ScreenCoder 的 ScreenBench 评测脚本是否能独立跑。
5. Web2Code `code_generation/README.md` 的具体环境和指标。
