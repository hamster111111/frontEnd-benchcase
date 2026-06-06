# 前端 Design Bench 调研资料

这个目录用来沉淀 GLM / Zhipu 及其他模型在前端、视觉设计、UI-to-code、网站生成等方向的 benchmark 资料，后续会整理成一个 web 展示页面。

## 目录结构

- `research/`：可读的调研笔记、来源摘要、后续问题。
- `data/`：结构化数据，后面做 web 页面时可以直接读取。
- `web/`：当前的静态 web 展示页面，直接读取 `data/web_display_data.json`。
- `benchmarks/`：已浅克隆的 benchmark / framework 仓库；未安装依赖，未额外下载大数据。

## 本地预览

从项目根目录启动静态服务：

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

然后打开：

```text
http://127.0.0.1:4173/web/
```

## 当前资料

- `research/glm-5v-turbo-frontend-design-bench.md`：当前已确认的 benchmark 和结论。
- `research/other-models-frontend-design-bench.md`：近几年其他模型在相关 design bench 上的公开结果。
- `research/zhipu-models-frontend-design-bench.md`：Zhipu / Z.AI 近几年模型在相关 design bench 上的公开结果。
- `research/zhipu-agent-systems-for-design-bench.md`：Zhipu / THUDM agent 系统和 design bench 的关系。
- `research/zhipu-framework-benchmark-details.md`：Zhipu/THUDM framework 实际跑过的 benchmark 输入、输出、指标、规模与口径。
- `research/design-bench-painpoints-and-opportunities.md`：当前 design bench 痛点、近年修复方向和容易达成的论文机会。
- `research/benchmark-screening-table.md`：按分数空间、可跑性和论文故事筛选第一阶段要拉入研究主线的 benchmark。
- `research/benchmark-repo-intake.md`：本地已 clone 仓库的版本、样本情况、入口脚本和 smoke test 顺序。
- `research/web-display-data-spec.md`：后续 web 展示使用的数据字段说明。
- `research/investigation-backlog.md`：后续还要继续查的资料清单。
- `data/glm5v_frontend_design_benchmarks.json`：给前端展示使用的结构化数据。
- `data/other_models_frontend_design_benchmarks.json`：其他模型的结构化 benchmark 结果。
- `data/zhipu_models_frontend_design_benchmarks.json`：Zhipu / Z.AI 模型的结构化 benchmark 结果。
- `data/zhipu_agent_design_bench_systems.json`：Zhipu / THUDM agent 系统的结构化资料。
- `data/zhipu_framework_benchmark_details.json`：Zhipu/THUDM framework 到 benchmark 的结构化映射。
- `data/benchmark_screening_table.json`：benchmark 筛选表的结构化版本，后续可直接整合进 web。
- `data/benchmark_repo_intake.json`：本地已 clone 仓库的结构化 intake 记录。
- `data/web_display_data.json`：给 web 页面直接消费的聚合展示数据。
- `web/index.html`、`web/styles.css`、`web/app.js`：无需构建步骤的展示页面。
