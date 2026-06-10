# 104_4

## 任务

- 页面：`104`
- 交互：`4`
- Topic：news
- Framework：react
- 原站链接：https://www.bbc.com/pidgin
- 用户动作：click the area of one news
- 目标变化：aftter clicking the area of one news, go to a new page of this news.
- 标签类型：, button, link, textarea, image, text
- 视觉类型：, new page, text

## 分数

| 口径 | CLIP | SSIM | Text | Position | IR/Flag | 状态 |
|---|---:|---:|---:|---:|---:|---|
| 官方 evaluator |  |  |  |  | 0 | score_error |
| staged evaluator | 0.6928 | 0.6808 | 0.5861 | 0.8591 | 1 | triggered |

官方 evaluator 错误：

```text
ValueError: min() iterable argument is empty
```

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
- official_click：[1_0_199_click.png](output/1_0_199_click.png)
- official_interact：缺失

## 文件

- `scores/scores.json`：该 case 的官方/staged 汇总分数。
- `scores/official_evaluator_record.json`：第二档官方 evaluator 原始记录。
- `scores/staged_eval_record.json`：旧 staged evaluator 原始记录。
- `input/metadata.json`：任务元数据。
