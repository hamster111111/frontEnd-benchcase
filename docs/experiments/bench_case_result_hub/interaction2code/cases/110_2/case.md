# 110_2

## 任务

- 页面：`110`
- 交互：`2`
- Topic：software development
- Framework：nextjs
- 原站链接：https://supabase.com/
- 用户动作：click on the "Postgres Database" block
- 目标变化：after clicking, turn to the database page
- 标签类型：link
- 视觉类型：new page

## 分数

| 口径 | CLIP | SSIM | Text | Position | IR/Flag | 状态 |
|---|---:|---:|---:|---:|---:|---|
| 官方 evaluator |  |  |  |  | 0 | missing_generated |
| staged evaluator |  |  |  |  | 0 | missing_html |

## 输入

- before：[before.png](input/before.png)
- after：[after.png](input/after.png)
- before_mark：[before_mark.png](input/before_mark.png)
- after_mark：[after_mark.png](input/after_mark.png)
- interaction_crop：[interaction_crop.png](input/interaction_crop.png)
- prompt：[prompt.txt](input/prompt.txt)

## 输出

- generated_html：缺失
- model_content：[content.txt](output/content.txt)
- model_reasoning：[reasoning.txt](output/reasoning.txt)
- raw_response：[response.json](output/response.json)

## 渲染与评测图

- staged_before：缺失
- staged_after：缺失
- staged_interaction_crop：缺失
- official_source：缺失
- official_click：缺失
- official_interact：缺失

## 文件

- `scores/scores.json`：该 case 的官方/staged 汇总分数。
- `scores/official_evaluator_record.json`：第二档官方 evaluator 原始记录。
- `scores/staged_eval_record.json`：旧 staged evaluator 原始记录。
- `input/metadata.json`：任务元数据。
