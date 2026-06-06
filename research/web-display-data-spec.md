# Web 展示数据说明

最后更新：2026-06-02

## 文件

用于后续 web 展示的聚合数据在：

- `data/web_display_data.json`

这个文件不是原始调研材料，而是给前端页面消费的整理版。它把 benchmark 元数据、模型分数、来源、口径和展示分组放在同一个结构里。

## 已补齐字段

每个 benchmark 都补了这些字段：

- `task_type`：任务类型，例如 UI-to-code、CSS repair、website development、GUI agent。
- `frontend_relevance`：和前端 design 的关系，分为 very_high / high / medium / low_medium。
- `input_modality`：输入模态，例如截图、HTML、CSS、自然语言需求、浏览器状态。
- `output_artifact`：输出产物，例如 HTML/CSS、React code、CSS rule edit、完整网站、浏览器操作轨迹。
- `interaction_mode`：direct generation、closed-loop refinement、agentic tool use、browser/mobile agent 等。
- `metrics`：指标含义、方向、分数解释、是否可跨论文比较。
- `source_type`：official_report、benchmark_paper、project_page、paper_result 等。
- `confidence`：high / medium_high / medium，并保留 caveat。
- `publication`：benchmark 来源论文/报告、首次公开日期、venue、venue 评级提示、发表状态。

每条 score 都补了这些主要字段：

- `benchmark_id`
- `model`
- `model_family`
- `score`
- `metric`
- `score_scale`
- `rank_hint`：可选，用于首页强调强弱结论。
- `source_type`
- `source_url`
- `provenance`：分数来源报告、来源发布日期、跑分时间说明、来源 venue/评级。
- `confidence`
- `caveat`

## Provenance 口径

多数论文和模型报告只公开表格结果，没有披露每个分数实际跑分日期。因此页面中的“跑分时间”默认使用分数来源的首次公开日期或技术报告发布日期，并在表格中标注“未披露实际跑分日”。

会议/期刊评级是为了快速浏览而加的提示：CVPR、NeurIPS、ICML、KDD、ACL/NAACL、ICLR 等按常见顶会口径标注；arXiv 预印本和官方技术报告不标会议评级。正式写论文或对外发布时，应按目标机构使用的 CCF/CORE/中科院目录版本再复核。

## 展示建议

首页可以按 `display_sections` 渲染：

1. `zhipu_main_design_scores`：Zhipu/GLM 主线的 design-to-code 分数。
2. `agentic_design_scores`：VAB-CSS 和 UI2Code^N 这种 agentic / closed-loop 设计能力。
3. `website_development_scores`：Vision2Web 和完整网站开发。
4. `web_gui_agent_context`：WebVoyager、OSWorld、AutoGLM、AutoWebGLM、CogAgent 等背景。
5. `external_benchmark_landscape`：其他模型在 Design2Code、DesignBench、FLAME、Vision2Web 上的横向位置。

## 口径提醒

`Design2Code` 在不同来源里有两套常见口径：原论文的 CLIP / block / text / position / color 自动指标，以及 GLM / UI2Code^N 报告里的 VLM judge 分数。web 页面里不要把二者合成一个排行榜。

`Flame-VLM-Code` 和 `Flame-React-Eval` 的命名还需继续核对。展示时可以先合并在一个 benchmark family 下，但必须显示 caveat。

`VAB-CSS` 是 CSS repair / visual design repair，不是从零生成网页。它应和 `Design2Code` 分栏展示。

`WebVoyager`、`OSWorld`、`AndroidWorld`、`Mind2Web`、`AITW`、`AutoWebBench` 等属于 GUI/Web agent 背景，不应作为前端设计生成能力主证据。
