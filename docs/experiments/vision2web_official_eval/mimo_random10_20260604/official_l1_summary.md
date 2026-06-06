# Vision2Web 官方 evaluator 本地评测摘要

- 评测日期：2026-06-04
- 评测范围：Level 1 Static Webpage，random-10 smoke run 的 10 个样本
- 生成结果：mimo-v2.5 单文件 HTML，经脚本包装为 Vision2Web 官方 results 目录结构
- 评测命令：`vision2web evaluate --task webpage --framework smoke_html --model mimo-v2.5`
- Judge：`qwen3-vl-plus`，OpenAI-compatible API
- 说明：这是本地官方 evaluator 复跑，不是 Vision2Web 官方 leaderboard 维护者复测。

## 总分

| 指标 | 分数 |
|---|---:|
| Desktop VS | 62.05 |
| Tablet VS | 63.24 |
| Mobile VS | 53.75 |
| L1 Avg VS | 59.68 |

官方 analyzer 输出的 `Overall=19.9` 是把未跑的 L2/L3 记为 0 后平均；本轮只应看 L1 Avg VS。

## 项目级分数

| Project | Desktop | Tablet | Mobile | Avg |
|---|---:|---:|---:|---:|
| ebay | 46.88 | 40.62 | 50.00 | 45.83 |
| klamath | 62.50 | 50.00 | 33.33 | 48.61 |
| humankinetics | 59.09 | 60.42 | 28.12 | 49.21 |
| rottentomatoes | 62.50 | 65.38 | 57.50 | 61.79 |
| eventgroove | 68.18 | 63.64 | 58.33 | 63.38 |
| eventbrite | 66.67 | 67.86 | 56.25 | 63.59 |
| pagerduty | 60.71 | 68.75 | 62.50 | 63.99 |
| splunk | 65.91 | 70.45 | 58.33 | 64.90 |
| visitseoul | 61.36 | 68.75 | 67.50 | 65.87 |
| nxp | 66.67 | 76.56 | 65.62 | 69.62 |

## 最低样本

- ebay：Avg 45.83，desktop 46.88 / tablet 40.62 / mobile 50.00
- klamath：Avg 48.61，desktop 62.50 / tablet 50.00 / mobile 33.33
- humankinetics：Avg 49.21，desktop 59.09 / tablet 60.42 / mobile 28.12
