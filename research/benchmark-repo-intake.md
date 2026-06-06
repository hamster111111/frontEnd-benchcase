# Benchmark 仓库拉取与本地 intake 记录

最后更新：2026-06-03

## 本次动作

这次只做 benchmark / framework 仓库浅克隆和目录级 intake，没有安装依赖、没有跑模型、没有额外下载 HuggingFace / Google Drive 数据。

- 本地目录：`benchmarks/`
- Git 策略：`git clone --depth 1 --filter=blob:none`
- LFS 策略：设置 `GIT_LFS_SKIP_SMUDGE=1`，避免自动拉大文件
- 当前结果：10 个仓库全部 clone 成功

## 本地仓库版本

| 本地目录 | 来源 | commit | 日期 | 体积 | 文件数 |
|---|---|---|---|---:|---:|
| `benchmarks/design2code` | `https://github.com/NoviScl/Design2Code.git` | `7a575e4` | 2024-11-01 | 111.82 MB | 115 |
| `benchmarks/ui2code_n` | `https://github.com/zai-org/UI2Code_N.git` | `2f3c0f5` | 2026-05-02 | 314.53 MB | 2114 |
| `benchmarks/designbench` | `https://github.com/WebPAI/DesignBench.git` | `03bdb41` | 2026-05-25 | 15.12 MB | 519 |
| `benchmarks/vab_css_visualagentbench` | `https://github.com/THUDM/VisualAgentBench.git` | `9055fc2` | 2025-04-24 | 16.45 MB | 1510 |
| `benchmarks/vision2web` | `https://github.com/zai-org/Vision2Web.git` | `3111cc3` | 2026-05-02 | 4.87 MB | 41 |
| `benchmarks/interaction2code` | `https://github.com/WebPAI/Interaction2Code.git` | `3e55b39` | 2026-02-15 | 208.47 MB | 894 |
| `benchmarks/dcgen` | `https://github.com/WebPAI/DCGen.git` | `22af69b` | 2025-06-12 | 169.73 MB | 350 |
| `benchmarks/web2code` | `https://github.com/MBZUAI-LLM/web2code.git` | `48c356a` | 2024-10-23 | 11.94 MB | 157 |
| `benchmarks/screencoder` | `https://github.com/leigest519/ScreenCoder.git` | `e7c2cae` | 2025-10-22 | 84.36 MB | 492 |
| `benchmarks/visualwebbench` | `https://github.com/VisualWebBench/VisualWebBench.git` | `5840afa` | 2024-10-19 | 1.22 MB | 27 |

## 本地是否已有样本

| 仓库 | 本地已有样本/数据 | 判断 |
|---|---|---|
| UI2Code_N | `evaluation/data/Design2Code` 486 files / 101.12 MB；`Flame` 82 files / 1.96 MB；`UI2Code-Real` 117 files / 48.94 MB；`UIPolish-Real` 102 files / 41.20 MB；`UIPolish-Synthetic` 102 files / 51.20 MB；`Web2Code` 1200 files / 62.09 MB | 最意外也最有价值：repo 已带预处理 evaluation data，可直接做数据格式和评测脚本 intake。 |
| DCGen | `data/demo`、`data/dcgen_demo`、`data/direct_demo`、`data/original`，含 HTML/PNG demo | 第一轮最容易做小样本评测/失败案例分析。 |
| Interaction2Code | `sample/` 下 27 个样本目录，含 `action.json`、原型图、mark 图、interaction 图 | 可做交互任务格式分析，不必先下全量 127 个网页。 |
| DesignBench | repo 主要带 `assets/` 示例和 evaluator/web 模板；900 样本数据需要另下 | 价值高，但第一轮需要先小心处理数据下载和 Node/browser 环境。 |
| Design2Code | repo 主要带脚本和链接，没有完整 HARD 数据；README 给出 HARD zip / HF 链接 | 仍建议下载 HARD 小样本或直接用 UI2Code_N 里的 Design2Code 数据先跑脚本格式。 |
| VAB-CSS | repo 带 framework/task 代码；未看到 CSS benchmark 数据本体 | 需要继续确认 dataset 路径或 ModelScope/训练数据下载入口。 |
| Vision2Web | repo 只有代码和文档，dataset 在 HuggingFace | 先不跑，后续只拉 Level 1 static 小样本。 |
| Web2Code | repo 带 code generation / understanding 评测脚本，数据在 HuggingFace | 第二阶段泛化数据线。 |
| ScreenCoder | repo 带 demo、UIED、post-training 代码；ScreenBench 在 HuggingFace | 方法参考价值高，标准评测还需继续确认。 |
| VisualWebBench | repo 带 `run.py`、`run.sh` 和 model adapters，数据在 HuggingFace | 网页理解/grounding 背景，不是 design 主线。 |

## 每个仓库 intake

### 1. UI2Code_N

- 路径：`benchmarks/ui2code_n`
- 对应 benchmark：Design2Code、Flame-React-Eva、Web2Code、UI2Code-Real、UIPolish-Real、UIPolish-Synthetic。
- 关键入口：`evaluation/readme.md`、`evaluation/scripts/extract_html_code.py`、`render.py`、`autocall_multi_judge.py`、`rate_statistics_ui2code.py`、`rate_statistics.py`。
- 评测链路：抽取 HTML -> 渲染截图 -> VLM judge 比较参考图和渲染图 -> 统计 UI-to-code 或 UI polishing accuracy。
- API/GPU：跑本地 UI2Code^N-9B 需要 GPU；只分析数据、渲染已有 HTML、调用 judge 可走 API-only。
- 第一判断：P0。它已经带了我们最关心的 `UIPolish-Real` 和 `UI2Code-Real` 数据，建议先做数据格式和脚本 smoke test。

### 2. DCGen

- 路径：`benchmarks/dcgen`
- 对应 benchmark：DCGen real-world website set / segment-aware UI-to-code。
- 关键入口：`README.md`、`utils.py`、`scripts/evaluate.py`、`data/demo`、`data/direct_demo`、`data/dcgen_demo`。
- 评测链路：截图分块 -> 每块生成描述/代码 -> 重组网页 -> 用 `scripts/evaluate.py` 比较 direct 与 DCGen 输出。
- API/GPU：默认 API-only；本地不需要 GPU。README 提醒 fine-grained metrics 仅 Linux/macOS 稳定，Windows 可能受限。
- 第一判断：P0。自带 demo 和 direct/DCGen 输出，很适合先做 failure taxonomy 和指标复现。

### 3. Design2Code

- 路径：`benchmarks/design2code`
- 对应 benchmark：Design2Code / Design2Code-HARD。
- 关键入口：`Design2Code/metrics/multi_processing_eval.py`、`Design2Code/prompting`、`Design2Code/data_utils`。
- 数据入口：README 给出 Design2Code testset、Design2Code-HARD zip / HF 链接；HARD 是 80 对截图和 HTML。
- 评测链路：预测 HTML 目录 -> Playwright 渲染 -> Block/Text/Position/Color/CLIP 自动指标。
- API/GPU：自动评测不需要 GPU；API prompting 需要 key；本地跑 18B 模型才需要大 GPU。
- 第一判断：P0/P1。主线 benchmark，建议优先拿 HARD 小样本，但最快可以先复用 UI2Code_N 里的 Design2Code data 检查格式。

### 4. DesignBench

- 路径：`benchmarks/designbench`
- 对应 benchmark：WebPAI DesignBench，generation / edit / repair / compile error repair。
- 关键入口：`code/demo.ipynb`、`code/runner/main.py`、`code/evaluator/main.py`、`compile.py`、`metric.py`。
- 数据入口：HuggingFace / Google Drive；repo 未带完整 900 样本。
- 评测链路：生成或编辑多框架代码 -> 启动 React/Vue/Angular/Vanilla 项目 -> evaluator 输出 CLIP/SSIM/CSR/MLLM score 等。
- API/GPU：API-only 可跑模型；需要 Node、npm、Chrome、Firefox/geckodriver、single-file-cli；不需要本地训练 GPU。
- 第一判断：P0/P1，但工程比 DCGen/UI2Code_N 重。建议先只跑 Vanilla/React 小样本。

### 5. Interaction2Code

- 路径：`benchmarks/interaction2code`
- 对应 benchmark：Interaction2Code，127 webpages / 374 interactions。
- 关键入口：`code/prompting/generate.py`、`code/metric/calculate_metric.py`、`sample/*/action.json`。
- 本地样本：`sample/` 下 27 个样本目录。
- 评测链路：按 action.json 和原型图生成可交互页面 -> 自动交互 -> 计算 full page / interaction 指标。
- API/GPU：API-only；需要浏览器自动化和前端执行环境；不需要本地 GPU。
- 第一判断：P1。交互 story 很强，但先作为第二个 smoke test。

### 6. VisualAgentBench / VAB-CSS

- 路径：`benchmarks/vab_css_visualagentbench`
- 对应 benchmark：VAB-CSS、VAB-WebArena-Lite 等。
- 关键入口：`docs/detailed_setups/VAB-CSS.md`、`configs/tasks/css.yaml`、`src/server/tasks/css_agent`。
- 文档关键信息：VAB-CSS 多数情况下不需要额外外部环境，核心是编辑本地 CSS 并用 Python Playwright 对本地 HTML 截图；Docker 主要用于修正某些系统截图尺寸不一致。
- API/GPU：API agent 可无 GPU；训练 open LMM 需要 GPU；完整 VAB framework 仍需 AgentBench-style controller/worker 配置。
- 第一判断：P1。低分空间大，但 dataset 路径和 task worker 运行方式还要继续核对。

### 7. Vision2Web

- 路径：`benchmarks/vision2web`
- 对应 benchmark：Vision2Web Level 1 static webpage、Level 2 interactive frontend、Level 3 full-stack website。
- 关键入口：`scripts/run_inference.sh`、`scripts/run_evaluation.sh`、`vision2web/cli.py`、`vision2web/evaluation`。
- 数据入口：HuggingFace `zai-org/Vision2Web`。
- 评测链路：agent 生成项目实现 -> Docker sandbox 运行 -> VLM judge 视觉分 + GUI agent 功能分。
- API/GPU：API agent 可无本地 GPU；需要 Docker、LiteLLM proxy；自部署 VLM 另需 24-80GB。
- 第一判断：P2。高价值但重，等 P0 跑通后只拉 Level 1 static。

### 8. Web2Code

- 路径：`benchmarks/web2code`
- 对应 benchmark：Web2Code code generation / webpage understanding。
- 关键入口：`code_generation/README.md`、`code_generation/evaluate.py`、`generate_images.py`、`gpt4_vision_evaluation.py`。
- 评测链路：HTML 输出 -> 转渲染图 -> GPT-4V/VLM judge 评价。
- API/GPU：API judge 需要 key；README 示例也提到 LLaVA 环境和 `--cuda`，本地模型路线需要 GPU。
- 第一判断：P1/P2。适合作泛化，不作为第一轮主实验。

### 9. ScreenCoder / ScreenBench

- 路径：`benchmarks/screencoder`
- 对应 benchmark：ScreenBench，1000 个真实网页截图和 HTML source。
- 关键入口：`main.py`、`block_parsor.py`、`html_generator.py`、`image_replacer.py`、`UIED/run_single.py`。
- 数据入口：HuggingFace `Leigest/ScreenCoder`。
- API/GPU：支持 Doubao、Qwen、GPT、Gemini API；post-training 需要 GPU。
- 第一判断：P1/P2。模块化 UI-to-code 方法参考强，但标准 benchmark evaluator 还要继续确认。

### 10. VisualWebBench

- 路径：`benchmarks/visualwebbench`
- 对应 benchmark：webpage understanding / grounding。
- 关键入口：`run.py`、`run.sh`、`model_adapters`、`configs`。
- 数据入口：HuggingFace `visualwebbench/VisualWebBench`。
- API/GPU：闭源 API 可无 GPU；本地 VLM 需要 GPU。
- 第一判断：P3。作为 web UI understanding 背景，不进入 design 主线。

## 建议的下一步 smoke test 顺序

1. `UI2Code_N/evaluation`：先不跑模型，只抽 3 个 `UIPolish-Real` 和 `UI2Code-Real` 样本，确认输入字段、HTML 输出格式、渲染脚本、judge 输入格式。
2. `DCGen`：用 repo 自带 `data/demo`、`data/direct_demo`、`data/dcgen_demo` 跑或至少 dry-run `scripts/evaluate.py`，拿第一批 failure taxonomy。
3. `Design2Code-HARD`：下载 3-5 个 HARD 样本，接 Design2Code metric pipeline。
4. `DesignBench`：只跑 Vanilla/React 的 1-2 个 generation/repair 样本，重点看 compile error repair。
5. `VAB-CSS`：确认 CSS dataset 下载路径和 task worker 最小启动方式。

## 当前风险

- Windows 环境风险：DCGen fine-grained metrics 标注 Linux/macOS 更稳；DesignBench 文档偏 Linux；Playwright/Chrome/Firefox 路径可能需要适配。
- API 成本风险：UI2Code_N、DesignBench、VAB-CSS、Vision2Web 都可能调用 VLM judge 或 agent API。
- 数据 license 风险：Vision2Web 明确 CC-BY-NC-SA-4.0、学术非商业；Design2Code 数据基于 C4；后续论文实验需逐项记录 license。
- 指标口径风险：Design2Code 自动指标、UI2Code_N VLM judge、DesignBench MLLM score、VAB-CSS SR 不能混排。

## 2026-06-04 补拉：`其他bench.jpg` 中的新候选

这次按图片中的候选先补拉能找到官方仓库的项目；已存在的 `Design2Code` 和 `DesignBench` 不重复 clone。

| 本地目录 / 状态 | 来源 | commit / 状态 | 本地数据情况 | 初步判断 |
|---|---|---|---|---|
| `benchmarks/fullfront` | `https://github.com/Mikivishy/FullFront.git` | `c27e96d` | 仓库仅带代码、README 和示意图；未带 `.parquet` 数据文件；生成脚本默认期望 `datasets/*.parquet` 或 `data/*.parquet` | 强相关，覆盖 front-end workflow；需要继续找/下载数据本体 |
| `benchmarks/humaneval_v` | `https://github.com/HumanEval-V/HumanEval-V-Benchmark.git` | `c8c4e53` | 仓库带 `humaneval_v_test_hf/data-00000-of-00001.arrow`，约 32 MB；共 253 个 diagram-to-code 任务 | 中相关，偏视觉推理 + Python code，不是前端 UI 主实验 |
| `FrontendBench` | 论文 `arXiv:2506.13832` | 暂未 clone | arXiv 页面写明 data/code will be released soon；当前未找到官方 GitHub | 中高相关，等仓库或数据公开后再拉 |

### FullFront intake

- 路径：`benchmarks/fullfront`
- 对应 benchmark：FullFront，评估 MLLM 的完整前端工程 workflow。
- README 任务：`Webpage Design`、`Webpage Perception QA`、`Webpage Code Generation`。
- 关键入口：`generate_response/openai_code.py`、`generate_response/openai_qa.py`、`generate_response/qwen_code.py`、`calculate_similarity/render_img.py`、`clip_score.py`、`code_score.py`、`gemini_evaluate.py`。
- 数据格式线索：代码读取 `.parquet`，其中 code generation 任务字段包括 `Image`、`Before_image`、`After_image` 等 base64 图片字段。
- 第一判断：P0/P1。和我们“截图/交互图 -> 前端代码”的主线高度相关，但当前还不能直接跑随机 10，下一步要定位 dataset 下载地址或从 HF/论文页找数据。

### HumanEval-V intake

- 路径：`benchmarks/humaneval_v`
- 对应 benchmark：HumanEval-V，253 个 diagram-to-code 任务。
- 关键入口：`inference.py`、`evaluate.py`、`prompts.py`、`models/example.py`、`models/gpt_4o.py`。
- 评测链路：视觉输入 + function signature -> Python 代码；执行 handcrafted test cases，输出 `pass@1/3` 与 `parse_success_rate`。
- 本地数据：`humaneval_v_test_hf` 已存在 Arrow 数据；不需要额外下载即可做小样本 intake。
- 第一判断：P2 背景。它能支撑“视觉理解影响代码生成”的动机，但离 front-end design-to-code 有距离，不建议进入第一轮主实验。

### FrontendBench 状态

- 对应 benchmark：FrontendBench，自动评测 LLM 前端开发能力。
- 当前状态：论文存在，但官方代码/数据暂未公开；未 clone。
- 第一判断：P1/P2。若后续开放仓库，可作为 text-to-frontend / 自动测试补充线；当前只记录为待跟踪。
