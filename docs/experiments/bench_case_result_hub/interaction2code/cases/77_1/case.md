# 77_1

## 任务

- 页面：`77`
- 交互：`1`
- Topic：technology
- Framework：
- 原站链接：https://www.angloinfo.com/brussels/directory/brussels-auto-spares-parts-accessories-439
- 用户动作：
- 目标变化：
- 标签类型：button, textarea, option
- 视觉类型：text, new component

## 分数

| 口径 | CLIP | SSIM | Text | Position | IR/Flag | 状态 |
|---|---:|---:|---:|---:|---:|---|
| 官方 evaluator | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | scored |
| staged evaluator |  |  |  |  | 0 | trigger_error |

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
- staged_interaction_crop：缺失
- official_source：[official_0_source.png](output/official_0_source.png)
- official_click：缺失
- official_interact：缺失

## 文件

- `scores/scores.json`：该 case 的官方/staged 汇总分数。
- `scores/official_evaluator_record.json`：第二档官方 evaluator 原始记录。
- `scores/staged_eval_record.json`：旧 staged evaluator 原始记录。
- `input/metadata.json`：任务元数据。
