# 119_7

## 任务

- 页面：`119`
- 交互：`7`
- Topic：Code
- Framework：react
- 原站链接：https://sentry.io/
- 用户动作：click to the Triangle mark
- 目标变化：When the Triangle mark is clicked, the image switches
- 标签类型：button, image
- 视觉类型：switch, position

## 分数

| 口径 | CLIP | SSIM | Text | Position | IR/Flag | 状态 |
|---|---:|---:|---:|---:|---:|---|
| 官方 evaluator | 0.4744 | 0.4902 | 0.0000 | 0.5270 | 1 | scored |
| staged evaluator | 0.6665 | 0.4779 | 0.7499 | 0.8684 | 1 | triggered |

## 输入

- before：[before.png](input/before.png)
- after：[after.png](input/after.png)
- before_mark：[before_mark.png](input/before_mark.png)
- after_mark：[after_mark.png](input/after_mark.png)
- interaction_crop：[interaction_crop.png](input/interaction_crop.png)
- prompt：[prompt.txt](input/prompt.txt)

## 输出

- generated_html：[index.html](output/index.html)
- model_content：[content.txt](output/content.txt)
- model_reasoning：[reasoning.txt](output/reasoning.txt)
- raw_response：[response.json](output/response.json)

## 渲染与评测图

- staged_before：[staged_before_generated.png](output/staged_before_generated.png)
- staged_after：[staged_after_generated.png](output/staged_after_generated.png)
- staged_interaction_crop：[staged_generated_interaction_crop.png](output/staged_generated_interaction_crop.png)
- official_source：[official_0_source.png](output/official_0_source.png)
- official_click：[1_1295_494_click.png](output/1_1295_494_click.png)
- official_interact：[official_interact.png](output/official_interact.png)

## 文件

- `scores/scores.json`：该 case 的官方/staged 汇总分数。
- `scores/official_evaluator_record.json`：第二档官方 evaluator 原始记录。
- `scores/staged_eval_record.json`：旧 staged evaluator 原始记录。
- `input/metadata.json`：任务元数据。
