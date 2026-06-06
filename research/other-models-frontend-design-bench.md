# 近几年其他模型的前端 / Design Bench 结果

最后更新：2026-06-02

## 范围

这里整理 2024-2026 年公开论文或项目页中，和前端视觉还原、UI-to-code、React UI 生成、网站生成相关的模型评测结果。不同 benchmark 的指标定义差异很大，不能直接横向相加或简单排序。

## 总览

| Benchmark | 年份 | 任务重点 | 代表模型结果 | 备注 |
|---|---:|---|---|---|
| Design2Code | 2024/2025 | 真实网页截图转 HTML/CSS | GPT-4o Direct: CLIP 90.4；GPT-4V Self-Revision: CLIP 87.2；Claude 3 Opus Direct: CLIP 87.0 | 单页 UI-to-code，484 个真实网页；另有 80 个 hard cases。 |
| DesignBench | 2026 | 多框架前端 generation / edit / repair | Claude-3.7、GPT-4o、Gemini-2.0、Pixtral-124B 是论文中整体 top tier | 覆盖 React、Vue、Angular、Vanilla，共 900 个样本。 |
| Flame-React-Eval / Flame-VLM-Code | 2025 | React code generation | Flame-Waterfall-7B: pass@1 52.6%；Flame-Additive-7B: 51.6%；Gemini 1.5 Flash: 11.1%；GPT-4o: 4.9% | 更偏 React 工程正确性和 functional correctness，专门模型明显强于通用 VLM。 |
| Vision2Web | 2026 | 静态网页、交互前端、全栈网站开发 | OpenHands + Claude Opus 4.5: Static Avg 53.4、Interactive Avg 56.6、Full-stack Avg 48.0 | 更接近完整网站开发流程，难度高于单页 UI-to-code。 |

## Design2Code

来源：`Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering`

任务：输入网页截图，输出可渲染的 HTML/CSS。原始 benchmark 包含 484 个真实网页；后续还构造了 `Design2Code-HARD`，包含 80 个更难网页。

### 主 benchmark 关键结果

| 模型 / 方法 | Block | Text | Position | Color | CLIP |
|---|---:|---:|---:|---:|---:|
| GPT-4o Direct | 93.0 | 98.2 | 85.5 | 84.1 | 90.4 |
| GPT-4o Text-Augmented | 92.4 | 98.6 | 84.5 | 83.1 | 89.9 |
| GPT-4o Self-Revision | 92.7 | 98.6 | 84.9 | 83.3 | 90.1 |
| GPT-4V Direct | 85.8 | 97.4 | 80.5 | 73.3 | 86.9 |
| GPT-4V Text-Augmented | 87.6 | 98.2 | 80.2 | 73.0 | 87.2 |
| GPT-4V Self-Revision | 88.8 | 98.1 | 81.1 | 72.9 | 87.2 |
| Claude 3 Opus Direct | 90.2 | 97.5 | 77.9 | 71.4 | 87.0 |
| Gemini 1.0 Pro Vision Direct | 80.2 | 94.6 | 72.3 | 66.2 | 84.4 |
| WebSight VLM-8B | 55.9 | 86.6 | 77.3 | 79.4 | 87.6 |
| Design2Code-18B | 78.5 | 96.4 | 74.3 | 67.0 | 85.8 |

解读：GPT-4o 在原始 Design2Code 自动指标中最强。GPT-4V 通过 text-augmented / self-revision 有明显改善。Claude 3 Opus 在 block/text 上强，但 position/color 不如 GPT-4o。微调模型可以接近商业模型的某些指标，但整体还不稳定。

### Design2Code-HARD 关键结果

| 模型 / 方法 | Block | Text | Position | Color | CLIP |
|---|---:|---:|---:|---:|---:|
| GPT-4o Direct | 56.6 | 89.8 | 78.6 | 81.9 | 87.1 |
| GPT-4o Self-Revision | 72.1 | 96.4 | 81.1 | 82.4 | 88.2 |
| GPT-4o Mini Direct | 57.7 | 90.7 | 77.9 | 77.5 | 86.3 |
| Claude 3.5 Sonnet Direct | 61.7 | 91.1 | 83.0 | 84.4 | 89.5 |
| Claude 3 Opus Direct | 57.1 | 88.7 | 74.2 | 72.4 | 85.8 |
| Gemini 1.5 Pro Text-Augmented | 73.7 | 95.9 | 79.8 | 79.1 | 88.2 |
| Gemini 1.5 Flash Text-Augmented | 72.7 | 97.4 | 79.4 | 78.2 | 87.6 |

解读：hard set 上，Claude 3.5 Sonnet 的视觉相似指标很强，GPT-4o 通过 self-revision 能明显拉高 block/CLIP，Gemini 1.5 Pro/Flash 也有竞争力。

## DesignBench

来源：`DesignBench: A Comprehensive Benchmark for MLLM-based Front-end Code Generation`

任务：多框架、多任务前端评测。覆盖 React、Vue、Angular、Vanilla，任务包括 design generation、design edit、design repair，共 900 个 webpage samples。

论文主结论：Claude-3.7、GPT-4o、Gemini-2.0、Pixtral-124B 是整体 top-tier 模型。

### 论文报告的高层范围结果

| 模型 | Design Generation CLIP 范围 | Design Edit MLLM Score 范围 | Design Repair MLLM Score 范围 |
|---|---:|---:|---:|
| Claude-3.7 | 0.6024-0.8319 | 8.0152-9.1500 | 6.5926-7.1786 |
| GPT-4o | 0.5963-0.7734 | 8.0093-9.2250 | 5.9286-7.0714 |
| Gemini-2.0 | 0.6006-0.7611 | 7.8148-9.1364 | 5.2857-7.3214 |
| Pixtral-124B | 0.6324-0.7811 | 8.0185-9.1125 | 6.3704-6.9643 |

解读：DesignBench 不适合只看一个总分。Generation 看 CLIP / SSIM / CSR；Edit 和 Repair 还看 MLLM score、CMLS、CMCS、CSR。论文发现 Vanilla 最容易，React/Vue 居中，Angular 最难；generation 的瓶颈主要是视觉渲染和编译错误，edit/repair 的瓶颈主要是代码定位和局部修改。

## FLAME / Flame-React-Eval

来源：`Advancing Vision-Language Models in Front-end Development via Data Synthesis`

任务：React code generation，关注语法正确性、功能正确性和视觉一致性。指标是 pass@k。

| 模型 | pass@1 | pass@3 | pass@5 |
|---|---:|---:|---:|
| Flame-Evo-7B | 43.8% | 62.9% | 69.1% |
| Flame-Waterfall-7B | 52.6% | 65.5% | 70.3% |
| Flame-Additive-7B | 51.6% | 67.0% | 71.9% |
| LLaVA-Qwen2-7B-OV | 3.6% | 6.5% | 8.0% |
| InternVL2.5 78B | 3.8% | 5.6% | 6.5% |
| GPT-4o-2024-08-06 | 4.9% | 6.7% | 7.6% |
| Gemini 1.5 Flash | 11.1% | 13.7% | 14.5% |

解读：这个 benchmark 的信息很有价值，因为它显示通用强模型未必擅长 React 工程式生成。专门用前端数据训练的 Flame 系列在 pass@k 上显著更强。

## Vision2Web

来源：`Vision2Web: A Hierarchical Benchmark for Visual Website Development with Agent Verification`

任务：层级化视觉网站开发，覆盖 static webpage、interactive frontend、full-stack website。数据包含 193 个 website development tasks、1255 个 test cases、918 个 prototypes。

### OpenHands 框架下的主结果

| 模型 | Static Avg | Interactive Avg | Full-stack Avg | 备注 |
|---|---:|---:|---:|---|
| Claude Opus 4.5 | 53.4 | 56.6 | 48.0 | 整体最强。 |
| Claude Sonnet 4.5 | 47.1 | 45.7 | 20.4 | 全栈掉幅明显。 |
| GPT-5 | 约 44.7 | 43.2 | 34.1 | static avg 按 desktop/tablet/mobile 计算；论文 OCR 表格该处需回看原图确认。 |
| Gemini 3 Pro Preview | 55.8 | 35.2 | 17.2 | 静态网页强，交互/全栈下降明显。 |
| Gemini 3 Flash Preview | 47.8 | 32.2 | 12.5 | 类似 Pro，但整体更弱。 |
| Seed-1.8-VL | 1.3 | 20.2 | 0.0 | 全栈失败。 |
| Qwen3-VL-32B-Instruct | 0.0 | 0.0 | 0.0 | 在该设置中基本无法完成。 |
| Qwen3-VL-8B-Instruct | 0.1 | 0.0 | 0.0 | 在该设置中基本无法完成。 |

### Claude Code 框架下的主结果

| 模型 | Static Avg | Interactive Avg | Full-stack Avg |
|---|---:|---:|---:|
| Claude Opus 4.5 | 50.5 | 54.9 | 43.7 |
| Claude Sonnet 4.5 | 40.0 | 36.8 | 20.7 |
| GPT-5 | 43.1 | 44.0 | 16.5 |
| Gemini 3 Pro Preview | 52.3 | 14.0 | 9.3 |
| Gemini 3 Flash Preview | 43.3 | 20.5 | 3.5 |
| Seed-1.8-VL | 18.0 | 10.2 | 0.0 |
| Qwen3-VL-32B-Instruct | 0.9 | 0.0 | 0.0 |
| Qwen3-VL-8B-Instruct | 11.9 | 0.0 | 0.0 |

解读：Vision2Web 说明从“静态视觉还原”到“交互前端”再到“全栈网站”，模型能力会系统性下降。Claude Opus 4.5 目前在这个 benchmark 里最稳；Gemini 3 Pro Preview 静态页面强，但复杂任务掉得很快；Qwen3-VL 在这个 agentic website setting 下结果很差。

## 待继续补充

- `WebGenBench` / `WebGen-Bench`：需要进一步确认模型列表、指标和是否偏 text-only website generation。
- `VIBE Bench`：Vision2Web 引用了它，但还需要单独查清楚是否有可复现公开分数。
- `Web2Code`、`WebCode2M`：更偏数据集/训练或网页设计转代码，需要区分是否有标准 leaderboard。

## 来源链接

- Design2Code：https://arxiv.org/abs/2403.03163
- DesignBench：https://arxiv.org/abs/2506.06251
- DesignBench GitHub：https://github.com/WebPAI/DesignBench
- FLAME / Flame-React-Eval：https://arxiv.org/abs/2503.01619
- Vision2Web：https://arxiv.org/abs/2603.26648
- Vision2Web 项目页：https://vision2web-bench.github.io/

