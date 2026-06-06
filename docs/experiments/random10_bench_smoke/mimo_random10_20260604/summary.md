# Random 10 Benchmark Smoke Summary

- run_dir: `experiments\random10_bench_smoke\mimo_random10_20260604`
- provider/model: `mimo` / `mimo-v2.5`
- max_tokens: `omitted`
- bypass_proxy: `True`
- sample_size_per_bench: `10`
- seed: `20260604`
- dry_run: `False`

| bench | available | selected | ok | html | complete | code | text | failed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| design2code | 484 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| flame | 80 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| ui2code_real | 115 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| uipolish_real | 100 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| uipolish_synthetic | 100 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| web2code | 1198 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| dcgen_original | 110 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| interaction2code | 155 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| designbench | 120 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| fullfront | 60 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| screencoder_screenbench | 1000 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| vision2web | 100 | 10 | 10 | 10 | 10 | 0 | 0 | 0 |
| visualwebbench | 1536 | 10 | 10 | 0 | 0 | 0 | 10 | 0 |
| humaneval_v | 253 | 10 | 10 | 0 | 0 | 10 | 0 | 0 |

## Skipped

| bench | reason |
|---|---|
| vab_css | 本地缺少官方 `data/css_dataset`，README 只给 VAB-CSS 配置说明，没有可直接抽样的测试数据；该任务还依赖 CSS edit agent 环境，不适合用单轮截图到 HTML smoke 代替。 |
| frontendbench | 论文页此前说明 data/code will be released soon；当前本地没有官方数据或仓库，暂不能补跑。 |
