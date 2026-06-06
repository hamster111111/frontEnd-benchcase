# 近年顶会/强会前端设计与 Web Agent Framework 调研

最后更新：2026-06-02

## 调研范围

本表服务于“Zhipu/GLM design bench 与可刷分 framework”任务，重点记录 2023-2026 年和前端设计、UI-to-code、网页生成、Web/GUI agent 相关的公开 benchmark/framework。只做静态调研：看论文、项目页、README、数据页，不 clone 仓库、不安装依赖、不实际跑。

## 结论

可优先跑的前端设计主线仍然是 **Design2Code-HARD -> Interaction2Code -> DCGen -> DesignBench**。其中 Design2Code、Interaction2Code、DCGen 已有顶会/强会发表记录，工程成本相对可控。

如果要把论文故事做得更大，应把 **Web2Code、WebCode2M、Figma2Code、UI2Code^N、WebMMU** 作为“近年顶会演化线”：从截图到代码、从真实网页到大规模训练数据、从设计 metadata 到代码、从一次生成到多轮优化。

WebArena、Mind2Web、OSWorld、WorkArena 不是前端设计主实验，但能支撑“agentic / closed-loop / real web workflow”背景。

## 顶会/强会线索表

| 工作 | Venue / 评级口径 | 实际跑的 benchmark | 可跑性判断 |
|---|---|---|---|
| Figma2Code | ICLR 2026，机器学习顶会 | Figma2Code；213 curated cases；HF 全量 2817 rows | 数据公开，官方代码仓库仍需确认。适合 metadata-aware design-to-code 方法线。 |
| UI2Code^N | repo 标注 ICML 2026；OpenReview 仍保留 ICLR submitted 页面 | Design2Code、Flame-React-Eval、Web2Code、UI2Code-Real、UIPolish-Real、UIPolish-Synthetic | Zhipu 相关度最高；模型和 evaluation 公开，但 GPU/API judge 成本高。 |
| WebCode2M / Vision2UI | WWW 2025 Oral，Web 顶会 / CCF A | WebCode2M、Vision2UI、TreeBLEU | 大数据训练线，顶会背书强，但 2.56M instances 下载/训练成本高。 |
| DCGen | FSE 2025 Research Track，软件工程顶会 / CCF A | DCGen real-world website set；visual similarity metrics；多 MLLM 对比 | repo 和 HF 数据公开，适合 P0/P1 优先跑。 |
| Interaction2Code | ASE 2025，软件工程顶会 / CCF A | Interaction2Code；127 webpages；374 interactions；15 webpage types；31 interaction categories | 数据小，交互评测更贴近真实前端，适合作第二个 smoke test。 |
| WebMMU | EMNLP 2025 Main，NLP 顶会 | WebQA、HTML/CSS/JS code editing、Mockup2Code，多语言网站任务 | 可作为 mockup-to-code 和 code-editing 补充，不是主线第一跑。 |
| Design2Code | NAACL 2025 Long，ACL family 主会长文 | Design2Code 484 webpages；Design2Code-HARD 80 examples；Block/Text/Position/Color/CLIP | 最轻且最主线，建议第一个跑通。 |
| Web2Code | NeurIPS 2024 D&B Track，机器学习顶会 | Web2Code code generation；Web2Code webpage understanding；instruction-tuning evaluation | 数据和 evaluation framework 公开，适合训练/泛化线。 |
| WebArena | ICLR 2024，机器学习顶会 | WebArena；e-commerce/forum/gitlab/CMS tasks；functional correctness | 重型 web agent 环境，适合 agent 背景。 |
| OSWorld | NeurIPS 2024 D&B Track，机器学习顶会 | OSWorld；369 computer tasks；web + desktop apps；execution-based evaluation | 更重型的 GUI/Web agent，可作为背景指标。 |
| WorkArena / BrowserGym | ICML 2024，机器学习顶会 | WorkArena；29 ServiceNow tasks；BrowserGym environment | 企业软件 web agent，工程成本高。 |
| WorkArena++ | NeurIPS 2024 D&B Track，机器学习顶会 | WorkArena++；682 realistic workflow tasks | 多步 workflow agent 背景。 |
| WebAgent | ICLR 2024 Oral，机器学习顶会 Oral | MiniWoB、Mind2Web、HTML understanding tasks | 方法参考：planner + HTML summarizer + program synthesis。 |
| Mind2Web | NeurIPS 2023 D&B Track，机器学习顶会 | Mind2Web；2000+ tasks；137 websites；31 domains | offline web action prediction，适合作 grounding / agent 背景。 |
| DesignBench | arXiv/project，未确认顶会 | DesignBench；React/Vue/Angular/Vanilla；generation/edit/repair/compile-error repair | 虽非顶会确认项，但最接近“前端刷分 frame”，值得优先静态核验。 |

## 对我们任务的取舍

第一轮可跑 smoke test：

1. Design2Code-HARD：先跑 3-5 个样本，确认渲染和指标。
2. Interaction2Code：跑 1 个交互网页，确认 full page / interact 指标。
3. DCGen：跑 demo，对比 direct baseline 和 segment-aware pipeline。
4. DesignBench：只跑 Vanilla 或 React generation 少量样本。

第二轮顶会扩展：

1. Web2Code：看是否能补训练/泛化数据线。
2. UI2Code^N：核对 evaluation 输入输出和 judge API 成本。
3. Figma2Code：确认官方代码；如没有，先做 metadata-aware 小样本重建。
4. WebMMU：抽 Mockup2Code 或 code-editing split，作为补充 benchmark。
5. WebArena / OSWorld / WorkArena：仅在研究走 agentic closed-loop 时纳入。

## 主要来源

- Design2Code NAACL 2025: https://aclanthology.org/2025.naacl-long.199/
- Web2Code NeurIPS 2024 D&B: https://proceedings.neurips.cc/paper_files/paper/2024/hash/cb66be286795d71f89367d596bf78ea7-Abstract-Datasets_and_Benchmarks_Track.html
- WebCode2M / Vision2UI WWW 2025: https://openreview.net/forum?id=aeP5nmlw5B
- DCGen FSE 2025: https://conf.researchr.org/details/fse-2025/fse-2025-research-papers/36/Divide-and-Conquer-Generating-UI-Code-from-Screenshots
- Interaction2Code ASE 2025: https://ink.library.smu.edu.sg/sis_research/10733/
- WebMMU EMNLP 2025: https://aclanthology.org/2025.emnlp-main.1276/
- Figma2Code ICLR 2026: https://openreview.net/forum?id=CaXZB6bI31
- UI2Code^N: https://github.com/zai-org/UI2Code_N
- WebArena ICLR 2024: https://openreview.net/forum?id=oKn9c6ytLx
- Mind2Web NeurIPS 2023 D&B: https://papers.neurips.cc/paper_files/paper/2023/hash/5950bf290a1570ea401bf98882128160-Abstract-Datasets_and_Benchmarks.html
- OSWorld NeurIPS 2024 D&B: https://papers.nips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html
- WorkArena ICML 2024: https://www.servicenow.com/research/publication/alexandre-drouin-work-icml2024.html
- WorkArena++ NeurIPS 2024 D&B: https://proceedings.neurips.cc/paper_files/paper/2024/hash/0b82662b6c32e887bb252a74d8cb2d5e-Abstract-Datasets_and_Benchmarks_Track.html
- WebAgent ICLR 2024 Oral: https://iclr.cc/virtual/2024/oral/19785
