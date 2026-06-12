# Widget2Code: image_1629

## 状态

- status：evaluated

## 分数

| metric | score |
|---|---:|
| diagnostic_proxy_score | 32.7702 |
| layout_avg | 14.2757 |
| legibility_avg | 20.3197 |
| style_avg | 9.6557 |
| perceptual_proxy_0_100 | 19.6000 |
| ssim | 0.1210 |
| LPIPS↓ | 0.7290 |
| Geometry | 100.0000 |

## 细分指标

| Layout | Legibility | Style |
|---|---|---|
| Margin 5.0100 / Content 0.0000 / Area 37.8170 | Text 40.0000 / Contrast 0.0000 / Local 20.9590 | Palette 0.0510 / Vibrancy 0.0380 / Polarity 28.8780 |

## 输入

- input_image：[input.png](input/input.png)

## 输出

- output_image：[output.png](output/output.png)
- widget_jsx：[widget.jsx](output/widget.jsx)
- layout_jsx：[layout.jsx](output/layout.jsx)
- widget_json：[widget.json](output/widget.json)
- final_json：[final.json](output/final.json)
- prompt：[prompt.md](output/prompt.md)
- raw_response：[raw_response.txt](output/raw_response.txt)

## 分数与调试

- scores_json：[scores.json](scores/scores.json)
- evaluation_json：[evaluation.json](scores/evaluation.json)
- debug_json：[debug.json](scores/debug.json)
- run_log：[run.log](scores/run.log)
- dsl_stage_meta：[dsl_stage_meta.json](scores/dsl_stage_meta.json)
- bounding_boxes：[bounding_boxes.json](scores/bounding_boxes.json)

<!-- widget2code-intermediate-start -->
## 中间产物索引

这些文件来自已经跑完的分阶段实验，用来定位失败原因；没有重新调用模型或评测器。

- manifest：[intermediate_manifest.json](intermediate/intermediate_manifest.json)
- 预处理：1 个文件，缺失 0 项，目录 [1-preprocess](intermediate/1-preprocess/)
- 布局检测：5 个文件，缺失 0 项，目录 [2-layout](intermediate/2-layout/)
- 图标语义描述：2 个文件，缺失 0 项，目录 [3-icon-caption](intermediate/3-icon-caption/)
- 图标检索：3 个文件，缺失 0 项，目录 [4-icon-retrieval](intermediate/4-icon-retrieval/)
- 应用 Logo 检索：5 个文件，缺失 0 项，目录 [5-applogo](intermediate/5-applogo/)
- 图表与颜色识别：10 个文件，缺失 0 项，目录 [6-graph-color](intermediate/6-graph-color/)
- DSL 生成：4 个文件，缺失 0 项，目录 [7-dsl](intermediate/7-dsl/)
- DSL 编译：5 个文件，缺失 0 项，目录 [8-compilation](intermediate/8-compilation/)
- 渲染中间结果：5 个文件，缺失 0 项，目录 [9-rendering](intermediate/9-rendering/)

建议排查顺序：先看 `2-layout/layout-visualization.png` 和 `layout-data.json` 判断组件识别是否错；再看 `3-icon-caption`、`4-icon-retrieval`、`5-applogo` 判断图标/Logo 是否错；然后看 `6-graph-color/prompts/6-final.md` 与 `7-dsl/raw_response.txt` 判断模型是否把中间信息转成正确 DSL；最后看 `8-compilation` 和 `9-rendering` 判断是否是编译或渲染问题。
<!-- widget2code-intermediate-end -->

## 原始路径

- input：`benchmarks/widget2code/data/widget2code-benchmark/test/image_1629.png`
- case_dir：`benchmarks/widget2code/experiments/widget2code/dsl_qwen35-9b_cached_prompt_full997_c50_retry1_20260609_193427/image_1629`
- output：`benchmarks/widget2code/experiments/widget2code/dsl_qwen35-9b_cached_prompt_full997_c50_retry1_20260609_193427/image_1629/output.png`
- evaluation：`benchmarks/widget2code/experiments/widget2code/dsl_qwen35-9b_cached_prompt_full997_c50_retry1_20260609_193427/image_1629/evaluation.json`
