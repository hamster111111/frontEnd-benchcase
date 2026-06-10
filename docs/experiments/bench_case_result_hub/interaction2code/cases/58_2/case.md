# 58_2

## 任务

- 页面：`58`
- 交互：`2`
- Topic：manufacturer
- Framework：
- 原站链接：https://www.monarchbrands.com/category/industrial-wiping/new-mill-ends/
- 用户动作：
- 目标变化：
- 标签类型：a, a
- 视觉类型：new component

## 分数

| 口径 | CLIP | SSIM | Text | Position | IR/Flag | 状态 |
|---|---:|---:|---:|---:|---:|---|
| 官方 evaluator | 0.4656 | 0.3482 | 0.0000 | 0.1039 | 1 | scored |
| staged evaluator | 0.5359 | 0.4108 | 0.0000 | 0.5821 | 1 | triggered |

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
- official_click：[1_729_86_click.png](output/1_729_86_click.png)
- official_interact：[official_interact.png](output/official_interact.png)

## 文件

- `scores/scores.json`：该 case 的官方/staged 汇总分数。
- `scores/official_evaluator_record.json`：第二档官方 evaluator 原始记录。
- `scores/staged_eval_record.json`：旧 staged evaluator 原始记录。
- `input/metadata.json`：任务元数据。
