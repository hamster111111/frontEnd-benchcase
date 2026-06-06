const state = {
  data: null,
  frameworkData: null,
  zhipuAgentData: null,
  activeSectionId: null,
  activeView: "overview",
  activeFrameworkView: "runnable",
  selectedBenchmarkId: null,
  query: "",
  scoreCanvasBars: [],
};

const palette = ["#b7e36d", "#62d6cc", "#ff7a59", "#f2c66d", "#b59cff", "#ff5e6d", "#7aa2ff", "#9adf7a", "#ff9ecb", "#d2e1ff", "#e6a86a", "#8bd3ff"];

const $ = (selector) => document.querySelector(selector);

const sectionCopy = {
  zhipu_main_design_scores: {
    eyebrow: "智谱主线",
    title: "Zhipu / GLM 主线前端设计分数",
  },
  agentic_design_scores: {
    eyebrow: "闭环设计",
    title: "Agent 闭环设计评测",
  },
  website_development_scores: {
    eyebrow: "网站开发",
    title: "完整网站开发",
  },
  web_gui_agent_context: {
    eyebrow: "网页与 GUI Agent",
    title: "Web / GUI Agent 背景能力",
  },
  external_benchmark_landscape: {
    eyebrow: "横向对比",
    title: "其他模型横向环境",
  },
};

const viewCopy = [
  { id: "overview", title: "概览", subtitle: "当前分组" },
  { id: "benchmark", title: "Benchmark 详情", subtitle: "输入/输出/指标" },
  { id: "scores", title: "分数记录", subtitle: "跑分与来源" },
  { id: "comparison", title: "横向对比", subtitle: "其他模型" },
  { id: "frameworks", title: "可跑 Framework", subtitle: "复现与刷分" },
];

const frameworkViewCopy = [
  { id: "runnable", title: "复现候选", subtitle: "优先级/成本" },
  { id: "zhipu", title: "Zhipu 跑法", subtitle: "直接 vs framework" },
  { id: "venue", title: "顶会线索", subtitle: "论文与 benchmark" },
];

const benchmarkGuides = {
  design2code: {
    summary: "看模型能不能把一张网页截图或设计稿还原成可渲染的网页。",
    input: "通常给模型一张参考网页截图；部分论文还会附加文本提示，帮助模型理解页面结构或内容。",
    output: "模型需要产出 HTML/CSS，评测端会把代码重新渲染成网页，再和参考截图比较。",
    evaluation: "重点看视觉还原：版块结构、文字、位置、颜色，以及 CLIP 或 VLM 评审相似度。不同报告的评分口径不完全相同，不能直接混成一个总榜。",
  },
  flame_react_eval: {
    summary: "看模型能不能生成可运行的 React 前端 UI，而不是只生成静态 HTML。",
    input: "输入可以是 UI 截图、多模态提示或任务指令，要求模型理解组件结构和页面目标。",
    output: "输出是 React 代码，随后渲染成 UI 进行检查。",
    evaluation: "常见指标是 pass@k 或 VLM-Code 分数，反映代码能否运行、视觉是否接近目标、组件是否满足任务要求。",
  },
  vision2web: {
    summary: "看模型能不能从视觉原型或任务描述完成更完整的网站开发链路。",
    input: "输入包括原型图或截图、任务规格、素材，以及环境上下文；任务可能不止一个静态页面。",
    output: "输出可以是静态网页、交互式前端，或带状态与后端逻辑的全栈网站。",
    evaluation: "分数通常拆成静态、交互、全栈三个层级；它比单页截图还原更强调工作流完成度和功能可用性。",
  },
  cc_frontend: {
    summary: "这是前端代码任务，不是视觉设计还原 benchmark。",
    input: "输入是文本需求、仓库上下文或已有代码，类似真实开发中的 issue 或 coding task。",
    output: "输出是代码补丁或前端实现，需要能通过任务检查。",
    evaluation: "分数反映前端 coding 能力，对视觉设计理解只有间接参考价值。",
  },
  vab_css: {
    summary: "看 Agent 能不能通过修改 CSS 把错误页面修回目标设计。",
    input: "输入包括目标设计截图、当前错误页面截图、页面 HTML，以及自然语言差异描述。",
    output: "输出不是整页重写，而是多轮 CSS 规则修改，最终得到修复后的渲染网页。",
    evaluation: "主要看最终渲染是否比初始页面更接近目标图，或 SSIM 是否超过成功阈值；它是闭环修复任务，不是从零生成页面。",
  },
  designbench_webpai: {
    summary: "覆盖多框架前端生成、编辑和修复，适合看模型在不同前端任务形态上的整体表现。",
    input: "输入可能是设计提示、网页截图、目标状态，或明确的编辑/修复指令。",
    output: "输出可能是 React、Vue、Angular 或原生 HTML/CSS/JS 代码。",
    evaluation: "指标包括视觉相似度、结构相似度、执行成功率和多模态评审分；更适合分任务看，不适合压成单一总分。",
  },
  web2code: {
    summary: "看模型能不能把网页截图或 UI 图转成前端代码。",
    input: "输入是一张网页截图或 UI 图片，通常不提供完整代码上下文。",
    output: "输出是前端代码，并通过渲染网页来检查最终效果。",
    evaluation: "重点看渲染结果与目标图的视觉匹配程度，以及代码是否能稳定生成页面。",
  },
  ui2code_real: {
    summary: "用真实网页截图测试 UI 转代码能力，比合成页面更接近真实前端场景。",
    input: "输入是真实世界网页截图，页面布局和视觉细节通常更复杂。",
    output: "输出是前端代码和对应的渲染网页。",
    evaluation: "主要看真实网页的视觉还原质量，适合观察模型在非模板化页面上的鲁棒性。",
  },
  uipolish: {
    summary: "看模型能不能根据目标 UI 和当前渲染结果，迭代优化已有前端代码。",
    input: "输入包括目标 UI、当前代码和当前渲染图，相当于告诉模型“现在差在哪里”。",
    output: "输出是改进后的前端代码，以及更接近目标的渲染结果。",
    evaluation: "重点看闭环优化是否真的让页面更接近目标，而不是一次性生成是否成功。",
  },
  design2code_hard: {
    summary: "Design2Code 的高难版本，用更复杂的网页截图拉开模型差距。",
    input: "输入是布局更复杂、细节更密集的网页截图。",
    output: "输出是前端代码和渲染网页。",
    evaluation: "用于看模型在复杂视觉布局、长尾组件和细节还原上的上限。",
  },
  webcode2m_long: {
    summary: "看模型能不能处理长网页 UI，而不是只还原首屏或短页面。",
    input: "输入是长网页 UI，通常包含跨屏内容和更长的结构依赖。",
    output: "输出是能覆盖长页面结构的前端代码。",
    evaluation: "重点看长上下文页面结构是否完整，以及跨屏布局是否稳定。",
  },
  webvoyager: {
    summary: "这是网页操作 Agent benchmark，用来补充模型是否会真实浏览网页。",
    input: "输入是网页观察、浏览器状态和自然语言任务。",
    output: "输出是浏览器动作序列，并最终完成任务。",
    evaluation: "它不直接评估视觉设计生成，但能反映模型是否具备网页理解和操作能力。",
  },
  osworld: {
    summary: "看模型在桌面操作系统里的 GUI 操作能力。",
    input: "输入是桌面截图或状态观察，以及任务指令。",
    output: "输出是鼠标、键盘等桌面动作，并完成目标任务。",
    evaluation: "它是 GUI Agent 背景指标，和前端设计生成不是同一类任务。",
  },
  androidworld: {
    summary: "看模型在 Android 应用中的移动端 GUI 操作能力。",
    input: "输入是移动端屏幕观察和任务指令。",
    output: "输出是移动端动作，例如点击、滑动、输入，并完成任务。",
    evaluation: "它适合观察移动 UI 理解与操作能力，不直接衡量网页生成质量。",
  },
  webquest: {
    summary: "看模型能不能在网页中检索信息并回答问题。",
    input: "输入是网页内容和问题，可能需要多步浏览或信息定位。",
    output: "输出是答案，以及必要时的网页交互轨迹。",
    evaluation: "它衡量网页信息检索和问答能力，属于 Web Agent 背景，不是前端视觉生成。",
  },
  mind2web: {
    summary: "看模型能不能根据网页状态预测下一步正确操作。",
    input: "输入是网页快照、历史动作和任务指令。",
    output: "输出是下一步动作、目标元素和操作类型。",
    evaluation: "它常用于离线评估网页 Agent 的动作选择能力，不要求模型真正生成前端代码。",
  },
  aitw: {
    summary: "看模型能不能根据 Android 屏幕和目标预测下一步移动端操作。",
    input: "输入是 Android 截图、目标指令和历史动作。",
    output: "输出是下一步移动端动作，以及点击、滑动或输入参数。",
    evaluation: "它衡量移动端操作预测能力，主要作为 GUI Agent 背景指标。",
  },
  autowebbench: {
    summary: "看模型能不能在真实中英文网页上执行多步浏览任务。",
    input: "输入是简化 HTML、URL、窗口位置和任务指令。",
    output: "输出是网页动作序列，并最终完成任务。",
    evaluation: "它侧重真实网页导航和任务完成，能补充模型的 Web Agent 能力。",
  },
  miniwob: {
    summary: "用可控的模拟网页环境测试基础网页操作能力。",
    input: "输入是网页环境状态和任务指令。",
    output: "输出是网页动作，例如点击、输入和选择。",
    evaluation: "它适合看基础操作能力，但和真实前端设计生成距离较远。",
  },
  webarena: {
    summary: "在真实网站镜像环境中测试多步网页操作能力。",
    input: "输入是网页环境状态和任务指令，任务通常需要跨页面操作。",
    output: "输出是网页动作序列，并完成最终任务。",
    evaluation: "它更接近真实 Web Agent 场景，可作为网页理解和操作能力背景。",
  },
  vab_webarena_lite: {
    summary: "VisualAgentBench 中的网页操作子集，用视觉网页观察测试 Agent。",
    input: "输入是浏览器观察和任务指令。",
    output: "输出是浏览器动作，并尝试完成任务。",
    evaluation: "它不是设计生成任务，但能说明模型在视觉网页环境里的操作能力。",
  },
  androidlab: {
    summary: "看模型在交互式 Android 环境中完成移动端任务的能力。",
    input: "输入是 Android 屏幕和任务指令。",
    output: "输出是移动端动作，并完成目标任务。",
    evaluation: "它是移动 GUI Agent 指标，可作为模型多模态操作能力背景。",
  },
};

const zhLabels = {
  "Agentic / Closed-loop Design Bench": "Agent 闭环设计评测",
  "Web / GUI Agent 背景": "Web / GUI Agent 背景能力",
  "UI-to-code / Visual Restoration": "视觉还原 / UI 转代码",
  "Frontend Code Generation": "前端代码生成",
  "Website Development": "网站开发",
  "Text Frontend Coding": "文本前端编程",
  "Agentic Visual Design": "Agent 闭环视觉设计",
  "Multi-framework Frontend Design": "多框架前端设计",
  "UI-to-code / Real-world": "真实网页 UI 转代码",
  "Closed-loop UI Refinement": "闭环 UI 优化",
  "Hard UI-to-code": "高难 UI 转代码",
  "Long UI-to-code": "长网页 UI 转代码",
  "Web GUI Agent": "网页 GUI Agent",
  "Desktop GUI Agent": "桌面 GUI Agent",
  "Mobile GUI Agent": "移动 GUI Agent",
  "Web QA Agent": "网页问答 Agent",
  "Web Navigation Agent": "网页导航 Agent",
  "视觉网站开发，覆盖 static webpage、interactive frontend、full-stack website": "视觉网站开发，覆盖静态网页、交互前端、全栈网站",
  "纯文本前端 coding 子项": "纯文本前端代码子项",
  "CSS repair / visual design repair": "CSS 视觉设计修复",
  "多框架前端 generation / edit / repair": "多框架前端生成 / 编辑 / 修复",
  "UI polishing / rendered-feedback code refinement": "UI 润色 / 渲染反馈代码优化",
  "direct generation; some papers also evaluate text augmentation or self revision": "直接生成；部分论文也评估文本补充或自我修订",
  "code generation; GLM reports may use VLM-code scoring": "代码生成；GLM 报告可能使用 VLM-code 评分",
  "agentic website development with workflow verification": "Agent 化网站开发，并验证工作流完成度",
  "coding benchmark": "代码任务评测",
  "agentic tool use with iterative CSS editing": "使用工具进行多轮 CSS 编辑",
  "generation / edit / repair": "生成 / 编辑 / 修复",
  "UI-to-code generation": "UI 转代码生成",
  "UI drafting": "UI 草稿生成",
  "closed-loop visual refinement": "闭环视觉优化",
  "agent comparison / end-to-end comparison": "Agent 对比 / 端到端对比",
  "browser agent": "浏览器 Agent",
  "desktop GUI agent": "桌面 GUI Agent",
  "mobile GUI agent": "移动端 GUI Agent",
  "web QA agent": "网页问答 Agent",
  "offline web agent action prediction": "离线网页动作预测",
  "mobile action prediction": "移动端动作预测",
  "web navigation agent": "网页导航 Agent",
  "visual web agent": "视觉网页 Agent",
  "interactive mobile GUI agent": "交互式移动 GUI Agent",
  "reference webpage screenshot": "参考网页截图",
  "optional text augmentation in some protocols": "部分协议可加文本补充",
  "UI screenshot or multimodal prompt": "UI 截图或多模态提示",
  "task instruction": "任务指令",
  "prototype or screenshot": "原型或截图",
  "task specification": "任务规格",
  "assets and environment context": "素材与环境上下文",
  "text instruction": "文本指令",
  "repository or code context": "代码仓库或代码上下文",
  "target design screenshot": "目标设计截图",
  "current corrupted webpage screenshot": "当前错误网页截图",
  "natural-language difference description": "自然语言差异描述",
  "design prompt": "设计提示",
  "webpage screenshot or target state": "网页截图或目标状态",
  "edit or repair instruction": "编辑或修复指令",
  "webpage screenshot or UI image": "网页截图或 UI 图",
  "target UI": "目标 UI",
  "real-world webpage screenshot": "真实网页截图",
  "current code": "当前代码",
  "current rendering": "当前渲染",
  "challenging webpage screenshot": "高难网页截图",
  "long webpage UI": "长网页 UI",
  "webpage observation": "网页观察",
  "goal instruction": "目标指令",
  "previous actions": "历史动作",
  "browser observation": "浏览器观察",
  "desktop screen observation": "桌面屏幕观察",
  "mobile screen observation": "移动端屏幕观察",
  question: "问题",
  "webpage content": "网页内容",
  "webpage snapshot": "网页快照",
  "action history": "动作历史",
  "Android screen": "Android 屏幕",
  "Android screenshot": "Android 截图",
  "交互式 Android agent benchmark": "交互式 Android Agent 评测集",
  "web environment state": "网页环境状态",
  "browser state": "浏览器状态",
  "window position": "窗口位置",
  "simplified HTML": "简化 HTML",
  "rendered webpage": "渲染网页",
  "rendered UI": "渲染 UI",
  "static webpage": "静态网页",
  "interactive frontend": "交互前端",
  "full-stack website": "全栈网站",
  "code patch": "代码补丁",
  "frontend implementation": "前端实现",
  "CSS rule edits": "CSS 规则修改",
  "final rendered webpage": "最终渲染网页",
  "React code": "React 代码",
  "Vue code": "Vue 代码",
  "Angular code": "Angular 代码",
  "Vanilla HTML/CSS/JS": "原生 HTML/CSS/JS",
  "frontend code": "前端代码",
  "refined frontend code": "优化后的前端代码",
  "improved rendering": "改进后的渲染",
  answer: "答案",
  operation: "操作",
  "task completion": "任务完成",
  "next action": "下一步动作",
  "next mobile action": "下一步移动端动作",
  "tap/swipe/type parameters": "点击 / 滑动 / 输入参数",
  "target element": "目标元素",
  "browser actions": "浏览器动作",
  "desktop actions": "桌面动作",
  "mobile actions": "移动端动作",
  "web actions": "网页动作",
  "web action sequence": "网页动作序列",
  "web interaction trace": "网页交互轨迹",
  higher_is_better: "越高越好",
  lower_is_better: "越低越好",
  mixed: "混合口径",
  high: "高",
  medium_high: "中高",
  medium: "中",
  low_medium: "中低",
  very_high: "很高",
  official_report: "官方报告",
  benchmark_paper: "Benchmark 论文",
  project_page: "项目页",
  derived_note: "整理说明",
  "general VLM": "通用视觉语言模型",
  "VLM series": "视觉语言模型系列",
  "specialized UI-to-code model": "UI 转代码专用模型",
  "Agent-based UI-to-code": "Agent 化 UI 转代码",
  "Open-source UI-to-code": "开源 UI 转代码模型",
  "Flame-Code-VLM": "FLAME 专项模型",
  "Google Gemini": "Google Gemini",
  "Mistral / Pixtral": "Mistral / Pixtral",
  "ByteDance Seed": "ByteDance Seed",
  "Alibaba Qwen": "Alibaba Qwen",
  InternVL: "InternVL",
  "LLaVA / Qwen": "LLaVA / Qwen",
  Block: "块结构",
  Text: "文本",
  Position: "位置",
  Color: "颜色",
  "VLM Judge": "VLM 评审",
  "VLM Judge Score": "VLM 评审分数",
  "VLM Judge Acc.": "VLM 评审准确率",
  "VLM-Code Score": "VLM-Code 分数",
  "Official Report Score": "官方报告分数",
  "Frontend Score": "前端分数",
  "OpenHands Static Avg": "OpenHands 静态平均分",
  "OpenHands Interactive Avg": "OpenHands 交互平均分",
  "OpenHands Full-stack Avg": "OpenHands 全栈平均分",
  "pass@1": "pass@1",
  "Static Avg": "静态平均分",
  "Interactive Avg": "交互平均分",
  "Full-stack Avg": "全栈平均分",
  "Success Rate": "成功率",
  "Improve Rate": "提升率",
  "Polish Accuracy": "润色准确率",
  "CLIP Similarity": "CLIP 相似度",
  "Matching Score": "匹配分",
  "Overall Matching Score": "总体匹配分",
  "DINO Acc.": "DINO 准确率",
  "Step Success Rate": "单步成功率",
  "Average Step SR": "平均单步成功率",
  "Overall Step SR": "总体单步成功率",
  "Overall SSR summary": "总体单步成功率摘要",
  "QA Score": "问答分数",
  Latency: "延迟",
  "Token Cost": "Token 成本",
  SingleQA: "单题问答",
  "Success Rate pass@2": "成功率 pass@2",
  "UIPolish-Real Accuracy": "UIPolish-Real 准确率",
  "UIPolish-Synthetic Accuracy": "UIPolish-Synthetic 准确率",
  "mixed ranges": "混合区间",
};

const textReplacements = [
  ["UI-to-code", "UI 转代码"],
  ["UI polishing", "UI 润色"],
  ["agentic design", "Agent 闭环设计"],
  ["agentic website development", "Agent 化网站开发"],
  ["design-to-code", "设计转代码"],
  ["CSS repair", "CSS 修复"],
  ["direct setting", "直接生成设置"],
  ["split", "数据切分"],
  ["judge", "评审"],
  ["benchmark", "评测集"],
  ["coding", "代码"],
];

const scoreTextReplacements = [
  ["generation", "生成"],
  ["edit", "编辑"],
  ["repair", "修复"],
  ["range", "范围"],
  [" real", " 真实集"],
  [" synthetic", " 合成集"],
];

function zh(value) {
  return zhLabels[value] ?? value;
}

function zhText(value) {
  if (!value) return "";
  return textReplacements
    .reduce((text, [from, to]) => text.replaceAll(from, to), zh(value))
    .replaceAll(" 或 ", "或")
    .replaceAll(" 和 ", "和")
    .replaceAll(" 或", "或")
    .replaceAll(" 和", "和")
    .replaceAll("CLIP或", "CLIP 或")
    .replaceAll("或VLM", "或 VLM")
    .replaceAll("SSIM或", "SSIM 或")
    .replaceAll("设置 分数", "设置分数");
}

function zhScoreText(value) {
  return scoreTextReplacements.reduce((text, [from, to]) => text.replaceAll(from, to), zhText(value));
}

function zhList(items) {
  return items.map((item) => zhText(item)).join(" / ");
}

function sectionTitle(section) {
  return sectionCopy[section.id]?.title ?? zh(section.title);
}

function sectionEyebrow(section) {
  return sectionCopy[section.id]?.eyebrow ?? "展示分组";
}

function explainLegend(kind, key) {
  const label = zh(key);
  const note = state.data.legends?.[kind]?.[key];
  return note ? `${label}：${zhText(note)}` : label;
}

function benchmarkGuide(benchmark) {
  return (
    benchmarkGuides[benchmark.id] ?? {
      summary: zhText(benchmark.task_type),
      input: `模型输入包括：${zhList(benchmark.input_modality)}。`,
      output: `模型输出包括：${zhList(benchmark.output_artifact)}。`,
      evaluation: zhText(benchmark.score_interpretation),
    }
  );
}

async function loadData() {
  const [response, frameworkResponse, zhipuAgentResponse] = await Promise.all([
    fetch("../data/web_display_data.json", { cache: "no-store" }),
    fetch("../data/framework_reproducibility.json", { cache: "no-store" }),
    fetch("../data/zhipu_agent_design_bench_systems.json", { cache: "no-store" }),
  ]);
  if (!response.ok) {
    throw new Error(`Failed to load data: ${response.status}`);
  }
  if (!frameworkResponse.ok) {
    throw new Error(`Failed to load framework data: ${frameworkResponse.status}`);
  }
  if (!zhipuAgentResponse.ok) {
    throw new Error(`Failed to load Zhipu framework data: ${zhipuAgentResponse.status}`);
  }
  const [data, frameworkData, zhipuAgentData] = await Promise.all([response.json(), frameworkResponse.json(), zhipuAgentResponse.json()]);
  state.data = data;
  state.frameworkData = frameworkData;
  state.zhipuAgentData = zhipuAgentData;
  state.activeSectionId = data.display_sections[0]?.id ?? null;
  state.selectedBenchmarkId = data.display_sections[0]?.benchmark_ids[0] ?? data.benchmarks[0]?.id ?? null;
  render();
}

function currentSection() {
  return state.data.display_sections.find((section) => section.id === state.activeSectionId);
}

function benchmarkById(id) {
  return state.data.benchmarks.find((benchmark) => benchmark.id === id);
}

function sectionBenchmarkIds() {
  const section = currentSection();
  return new Set(section?.benchmark_ids ?? state.data.benchmarks.map((benchmark) => benchmark.id));
}

function normalizedQuery() {
  return state.query.trim().toLowerCase();
}

function matchesQuery(benchmark) {
  const q = normalizedQuery();
  if (!q) return true;
  const scores = state.data.scores.filter((score) => score.benchmark_id === benchmark.id);
  const haystack = [
    benchmark.id,
    benchmark.name,
    benchmark.task_type,
    benchmark.display_group,
    zh(benchmark.task_type),
    zh(benchmark.display_group),
    benchmark.frontend_relevance,
    zh(benchmark.frontend_relevance),
    benchmark.publication?.paper_title,
    benchmark.publication?.venue,
    benchmark.publication?.venue_rating,
    benchmark.publication?.first_public_date,
    ...benchmark.input_modality,
    ...benchmark.input_modality.map((item) => zh(item)),
    ...benchmark.output_artifact,
    ...benchmark.output_artifact.map((item) => zh(item)),
    ...benchmark.metrics.map((metric) => `${zh(metric.name)} ${zh(metric.direction)}`),
    ...scores.map((score) => `${score.model} ${score.metric} ${score.score} ${score.provenance?.run_date_display ?? ""} ${score.provenance?.report_title ?? ""}`),
    ...scores.map((score) => `${score.model} ${zh(score.metric)} ${score.score} ${score.provenance?.report_venue ?? ""}`),
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(q);
}

function filteredBenchmarks() {
  const ids = sectionBenchmarkIds();
  return state.data.benchmarks.filter((benchmark) => ids.has(benchmark.id) && matchesQuery(benchmark));
}

function filteredScores() {
  const ids = sectionBenchmarkIds();
  const q = normalizedQuery();
  return state.data.scores.filter((score) => {
    if (!ids.has(score.benchmark_id)) return false;
    return scoreMatchesQuery(score, q);
  });
}

function selectedBenchmarkScores() {
  const q = normalizedQuery();
  return state.data.scores.filter((score) => score.benchmark_id === state.selectedBenchmarkId && scoreMatchesQuery(score, q));
}

function scoreRunner(score) {
  const url = score.source_url ?? "";
  const title = score.provenance?.report_title ?? "";
  if (url.includes("2604.26752")) return "Z.AI（GLM-5V-Turbo 报告）";
  if (url.includes("2507.01006")) return "Z.AI（GLM-4.5V/4.1V 报告）";
  if (url.includes("2511.08195")) return "Z.AI / UI2Code^N 作者";
  if (url.includes("2403.03163")) return "Design2Code benchmark 作者";
  if (url.includes("2408.06327")) return "THUDM / VisualAgentBench 作者";
  if (url.includes("2312.08914")) return "THUDM / CogAgent 作者";
  if (url.includes("2404.03648")) return "THUDM / AutoWebGLM 作者";
  if (url.includes("2411.00820")) return "Z.AI + Tsinghua / AutoGLM 作者";
  if (url.includes("2506.06251")) return "WebPAI / DesignBench 作者";
  if (url.includes("2503.01619")) return "FLAME 论文作者";
  if (url.includes("2603.26648")) return "Z.AI / Vision2Web 作者";
  if (/Z\.AI technical report/i.test(score.provenance?.report_venue ?? "")) return "Z.AI 官方报告";
  if (title) return title;
  return zh(score.source_type);
}

function scoreMatchesQuery(score, q) {
  if (!q) return true;
  const benchmark = benchmarkById(score.benchmark_id);
  return `${benchmark?.name ?? ""} ${zh(benchmark?.display_group ?? "")} ${benchmark?.publication?.paper_title ?? ""} ${benchmark?.publication?.venue ?? ""} ${score.model} ${zh(score.model_family)} ${score.metric} ${zh(score.metric)} ${score.score} ${scoreRunner(score)} ${score.provenance?.run_date_display ?? ""} ${score.provenance?.report_title ?? ""} ${score.provenance?.report_venue ?? ""} ${zh(score.source_type)} ${zh(score.confidence)} ${score.caveat ?? ""}`
    .toLowerCase()
    .includes(q);
}

function setActiveSection(id) {
  state.activeSectionId = id;
  const first = filteredBenchmarks()[0] ?? state.data.benchmarks.find((benchmark) => currentSection().benchmark_ids.includes(benchmark.id));
  state.selectedBenchmarkId = first?.id ?? state.selectedBenchmarkId;
  render();
}

function setSelectedBenchmark(id) {
  state.selectedBenchmarkId = id;
  render();
}

function render() {
  renderCounts();
  renderSections();
  renderViewTabs();
  renderBenchmarks();
  renderHero();
  renderScoreLegend();
  renderScoreRunnerSummary();
  renderModels();
  renderBenchmarkDetail();
  renderScoreBars();
  renderScoreTable();
  renderComparison();
  renderFrameworkSubTabs();
  renderFrameworkSummary();
  renderZhipuFrameworks();
  renderFrameworks();
  syncViewPanels();
  syncFrameworkPanels();
  drawScoreCanvas();
}

function renderCounts() {
  $("#benchCount").textContent = state.data.benchmarks.length;
  $("#scoreCount").textContent = state.data.scores.length;
  $("#sourceCount").textContent = state.data.source_index.length;
}

function renderSections() {
  const tabs = $("#sectionTabs");
  tabs.innerHTML = "";
  state.data.display_sections.forEach((section) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `tab-button${section.id === state.activeSectionId ? " is-active" : ""}`;
    button.innerHTML = `${sectionTitle(section)}<span>${section.benchmark_ids.length} 个评测集</span>`;
    button.addEventListener("click", () => setActiveSection(section.id));
    tabs.appendChild(button);
  });
}

function setActiveView(id) {
  state.activeView = id;
  render();
}

function setActiveFrameworkView(id) {
  state.activeFrameworkView = id;
  render();
}

function renderViewTabs() {
  const tabs = $("#viewTabs");
  tabs.innerHTML = "";
  viewCopy.forEach((view) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `view-tab${view.id === state.activeView ? " is-active" : ""}`;
    button.innerHTML = `<strong>${view.title}</strong><span>${view.subtitle}</span>`;
    button.addEventListener("click", () => setActiveView(view.id));
    tabs.appendChild(button);
  });
}

function renderFrameworkSubTabs() {
  const tabs = $("#frameworkSubTabs");
  if (!tabs) return;
  tabs.innerHTML = "";
  frameworkViewCopy.forEach((view) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `framework-subtab${view.id === state.activeFrameworkView ? " is-active" : ""}`;
    button.innerHTML = `<strong>${view.title}</strong><span>${view.subtitle}</span>`;
    button.addEventListener("click", () => setActiveFrameworkView(view.id));
    tabs.appendChild(button);
  });
}

function syncViewPanels() {
  document.querySelectorAll("[data-view]").forEach((panel) => {
    panel.hidden = panel.dataset.view !== state.activeView;
  });
}

function syncFrameworkPanels() {
  document.querySelectorAll("[data-framework-view]").forEach((panel) => {
    panel.hidden = panel.dataset.frameworkView !== state.activeFrameworkView;
  });
}

function renderBenchmarks() {
  const list = $("#benchmarkList");
  const benchmarks = filteredBenchmarks();
  list.innerHTML = "";
  if (!benchmarks.length) {
    list.innerHTML = `<p class="empty">没有匹配的 benchmark。</p>`;
    return;
  }
  if (!benchmarks.some((benchmark) => benchmark.id === state.selectedBenchmarkId)) {
    state.selectedBenchmarkId = benchmarks[0].id;
  }
  benchmarks.forEach((benchmark) => {
    const count = state.data.scores.filter((score) => score.benchmark_id === benchmark.id).length;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `bench-button${benchmark.id === state.selectedBenchmarkId ? " is-active" : ""}`;
    button.innerHTML = `<strong>${benchmark.name}</strong><small>${zh(benchmark.display_group)} · ${count} 条分数</small>`;
    button.addEventListener("click", () => setSelectedBenchmark(benchmark.id));
    list.appendChild(button);
  });
}

function renderHero() {
  const section = currentSection();
  $("#activeSectionName").textContent = section ? sectionEyebrow(section) : "展示分组";
  $("#activeSectionTitle").textContent = section ? sectionTitle(section) : "评测集";
  $("#activeSectionDescription").textContent = zhText(section?.description ?? state.data.scope_note);
}

function benchmarkColor(benchmarkId) {
  const ids = currentSection()?.benchmark_ids ?? state.data.benchmarks.map((benchmark) => benchmark.id);
  const index = ids.indexOf(benchmarkId);
  return palette[(index >= 0 ? index : 0) % palette.length];
}

function renderScoreLegend() {
  const target = $("#scoreLegend");
  if (!target) return;
  const ids = currentSection()?.benchmark_ids ?? [];
  const items = ids
    .map((id) => {
      const benchmark = benchmarkById(id);
      const count = state.data.scores.filter((score) => score.benchmark_id === id && typeof score.score === "number").length;
      return { id, benchmark, count };
    })
    .filter((item) => item.benchmark && item.count > 0);

  if (!items.length) {
    target.innerHTML = `<div class="legend-note">当前分组暂无可绘制的数值分数。</div>`;
    return;
  }

  target.innerHTML = `
    <div class="legend-note">颜色代表 benchmark；当前左侧选中的 benchmark 在图中更亮，其他 benchmark 半透明。</div>
    ${items
      .map(
        (item) => `
          <div class="legend-item${item.id === state.selectedBenchmarkId ? " is-selected" : ""}">
            <span class="legend-swatch" style="--legend-color:${benchmarkColor(item.id)}"></span>
            <span><strong>${item.benchmark.name}</strong><span>${zh(item.benchmark.display_group)} · ${item.count} 条数值分数</span></span>
          </div>
        `
      )
      .join("")}
  `;
}

function renderScoreRunnerSummary() {
  const target = $("#scoreRunnerSummary");
  if (!target) return;
  const scores = filteredScores();
  if (!scores.length) {
    target.innerHTML = `<div class="score-runner-title">当前分组暂无匹配的跑分来源。</div>`;
    return;
  }

  const groups = new Map();
  scores.forEach((score) => {
    const runner = scoreRunner(score);
    const entry = groups.get(runner) ?? { runner, count: 0, benchmarks: new Set(), models: new Set() };
    entry.count += 1;
    entry.benchmarks.add(benchmarkById(score.benchmark_id)?.name ?? score.benchmark_id);
    entry.models.add(score.model);
    groups.set(runner, entry);
  });

  const items = Array.from(groups.values()).sort((a, b) => b.count - a.count || a.runner.localeCompare(b.runner));
  target.innerHTML = `
    <div class="score-runner-title">当前分组跑分来源：按来源报告/论文作者归类；具体每条见“分数记录”的“跑分方”列。</div>
    <div class="runner-chip-grid">
      ${items
        .slice(0, 8)
        .map((item) => `<span class="runner-chip"><strong>${item.count}</strong>${item.runner}</span>`)
        .join("")}
      ${items.length > 8 ? `<span class="runner-chip"><strong>+${items.length - 8}</strong>更多来源</span>` : ""}
    </div>
  `;
}

function renderModels() {
  const strip = $("#modelStrip");
  strip.innerHTML = "";
  state.data.model_cards.forEach((model) => {
    const tile = document.createElement("article");
    tile.className = "model-tile";
    const chips = model.key_scores
      .map((item) => {
        const benchmark = benchmarkById(item.benchmark_id);
        return `<span class="chip">${benchmark?.name ?? item.benchmark_id}<strong>${formatScore(item.score)}</strong></span>`;
      })
      .join("");
    tile.innerHTML = `
      <p class="section-label">${zh(model.type)}</p>
      <h3>${model.name}</h3>
      <p>${zhText(model.headline)}</p>
      <div class="mini-scores">${chips}</div>
    `;
    strip.appendChild(tile);
  });
}

function renderBenchmarkDetail() {
  const target = $("#benchmarkDetail");
  const benchmark = benchmarkById(state.selectedBenchmarkId);
  if (!benchmark) {
    target.innerHTML = `<p class="empty">请选择一个 benchmark。</p>`;
    return;
  }
  const metrics = benchmark.metrics
    .map((metric) => `<span class="metric-chip">${zh(metric.name)}: ${zh(metric.direction)}</span>`)
    .join("");
  const guide = benchmarkGuide(benchmark);
  const pub = benchmark.publication;
  const publication = pub
    ? `
      <div class="publication-strip">
        <div>
          <strong>评测来源论文</strong>
          <a class="source-link" href="${pub.source_url}" target="_blank" rel="noreferrer">${pub.paper_title}</a>
        </div>
        <div><strong>首次公开</strong><span>${pub.first_public_date}</span></div>
        <div><strong>会议 / 评级</strong><span>${pub.venue} · ${pub.venue_rating}</span></div>
        <div><strong>发表状态</strong><span>${pub.publication_status}</span></div>
      </div>
    `
    : "";
  target.innerHTML = `
    <p class="section-label">${zh(benchmark.display_group)}</p>
    <h3>${benchmark.name}</h3>
    <p>${guide.summary}</p>
    <div class="mini-scores">${metrics}</div>
    ${publication}
    <div class="bench-guide">
      <div><strong>输入：模型拿到什么</strong><span>${guide.input}</span></div>
      <div><strong>输出：模型要交付什么</strong><span>${guide.output}</span></div>
      <div><strong>怎么看分数</strong><span>${guide.evaluation}</span></div>
    </div>
    <div class="meta-grid">
      <div class="meta-item"><strong>输入字段</strong><span>${zhList(benchmark.input_modality)}</span></div>
      <div class="meta-item"><strong>输出字段</strong><span>${zhList(benchmark.output_artifact)}</span></div>
      <div class="meta-item"><strong>任务形态</strong><span>${zhText(benchmark.interaction_mode)}</span></div>
      <div class="meta-item"><strong>原始解释</strong><span>${zhText(benchmark.score_interpretation)}</span></div>
      <div class="meta-item"><strong>相关性</strong><span>${explainLegend("frontend_relevance", benchmark.frontend_relevance)}</span></div>
      <div class="meta-item"><strong>可信度</strong><span>${explainLegend("confidence", benchmark.confidence)}</span></div>
    </div>
    <p class="muted" style="margin-top: 18px;">${zhText(benchmark.caveat)}</p>
  `;
}

function renderScoreBars() {
  const scores = state.data.scores.filter((score) => score.benchmark_id === state.selectedBenchmarkId);
  const bars = $("#scoreBars");
  const benchmark = benchmarkById(state.selectedBenchmarkId);
  $("#scoreTitle").textContent = benchmark?.name ?? "选中的评测集";
  $("#scoreMeta").textContent = `${scores.length} 条记录`;
  bars.innerHTML = "";
  if (!scores.length) {
    bars.innerHTML = `<p class="empty">这个 benchmark 暂无分数记录。</p>`;
    return;
  }
  const numericScores = scores.filter((score) => typeof score.score === "number");
  const max = Math.max(...numericScores.map((score) => normalizeScore(score)), 1);
  scores
    .slice()
    .sort((a, b) => {
      if (typeof a.score === "number" && typeof b.score === "number") return normalizeScore(b) - normalizeScore(a);
      return String(a.model).localeCompare(String(b.model));
    })
    .forEach((score, index) => {
      const isNumeric = typeof score.score === "number";
      const width = isNumeric ? Math.max(3, (normalizeScore(score) / max) * 100) : 100;
      const row = document.createElement("div");
      row.className = "score-row";
      row.innerHTML = `
        <div class="score-name"><strong>${score.model}</strong><span>${zh(score.model_family)}</span></div>
        <div class="bar-track"><div class="bar-fill" style="--w:${width}%; --bar:${palette[index % palette.length]}"></div></div>
        <div class="score-value">${formatScore(score.score)}</div>
      `;
      bars.appendChild(row);
    });
}

function renderScoreTable() {
  const table = $("#scoreTable");
  const benchmark = benchmarkById(state.selectedBenchmarkId);
  const scores = selectedBenchmarkScores();
  $("#scoreTableTitle").textContent = benchmark ? `${benchmark.name} 的分数记录` : "当前评测集的分数记录";
  $("#tableCount").textContent = benchmark ? `${zh(benchmark.display_group)} · ${scores.length} 条记录` : `${scores.length} 条记录`;
  table.innerHTML = "";
  if (!scores.length) {
    table.innerHTML = `<tr><td colspan="8">当前选中的 benchmark 没有匹配的分数记录。</td></tr>`;
    return;
  }
  scores.forEach((score) => {
    const rowBenchmark = benchmarkById(score.benchmark_id);
    const provenance = score.provenance ?? {};
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${rowBenchmark?.name ?? score.benchmark_id}<small>${zh(rowBenchmark?.display_group ?? "")}</small></td>
      <td>${score.model}<small>${zh(score.model_family)}</small></td>
      <td>${zh(score.metric)}<small>${zh(score.score_scale)}</small></td>
      <td>${formatScore(score.score)}</td>
      <td>${scoreRunner(score)}<small>${zh(score.source_type)}</small></td>
      <td>${provenance.run_date_display ?? "未公开"}<small>${provenance.run_date ? "" : "未披露实际跑分日"}</small></td>
      <td><a class="source-link" href="${score.source_url}" target="_blank" rel="noreferrer">${provenance.report_title ?? zh(score.source_type)}</a><small>${provenance.report_venue ?? zh(score.source_type)} · ${provenance.report_venue_rating ?? ""}</small></td>
      <td>${zh(score.confidence)}<small>${zhText(score.caveat)}</small></td>
    `;
    table.appendChild(row);
  });
}

function isExternalModel(score) {
  return !/Zhipu|GLM|THUDM|CogVLM/i.test(`${score.model} ${score.model_family}`);
}

function comparisonBenchmarkIds() {
  if (state.activeSectionId === "external_benchmark_landscape") {
    return state.data.cross_comparison?.benchmark_ids ?? Array.from(sectionBenchmarkIds());
  }
  return Array.from(sectionBenchmarkIds());
}

function preferredMetricRank(benchmarkId, metric) {
  const metrics = state.data.cross_comparison?.preferred_metrics?.[benchmarkId] ?? [];
  const index = metrics.indexOf(metric);
  return index === -1 ? metrics.length + 1 : index;
}

function renderComparison() {
  const grid = $("#comparisonGrid");
  const meta = $("#comparisonMeta");
  const ids = comparisonBenchmarkIds();
  grid.innerHTML = "";
  let cardCount = 0;

  ids.forEach((benchmarkId) => {
    const benchmark = benchmarkById(benchmarkId);
    if (!benchmark) return;
    const rows = state.data.scores
      .filter((score) => score.benchmark_id === benchmarkId && isExternalModel(score))
      .slice()
      .sort((a, b) => {
        const metricDelta = preferredMetricRank(benchmarkId, a.metric) - preferredMetricRank(benchmarkId, b.metric);
        if (metricDelta !== 0) return metricDelta;
        if (typeof a.score === "number" && typeof b.score === "number") return normalizeScore(b) - normalizeScore(a);
        return String(a.model).localeCompare(String(b.model));
      })
      .slice(0, 8);
    if (!rows.length) return;

    const card = document.createElement("article");
    card.className = "comparison-card";
    card.innerHTML = `
      <div class="comparison-card-head">
        <div>
          <p class="section-label">${zh(benchmark.display_group)}</p>
          <h4>${benchmark.name}</h4>
        </div>
        <span>${benchmark.publication?.first_public_date ?? benchmark.year}</span>
      </div>
      <div class="comparison-rows">
        ${rows
          .map((score) => {
            const provenance = score.provenance ?? {};
            return `
              <div class="comparison-row">
                <strong>${score.model}</strong>
                <span>${zh(score.metric)}<small>${provenance.run_date_display ?? "跑分时间未公开"}</small></span>
                <b>${formatScore(score.score)}</b>
              </div>
            `;
          })
          .join("")}
      </div>
    `;
    grid.appendChild(card);
    cardCount += 1;
  });

  meta.textContent = cardCount ? `${cardCount} 个评测集 · 同评测内排序` : "暂无横向记录";
  if (!cardCount) {
    grid.innerHTML = `<p class="empty">当前分组没有可展示的其他模型横向记录。</p>`;
  }
}

function frameworkPriorityRank(priority) {
  const order = { P0: 0, "P0/P1": 1, P1: 2, "P1/P2": 3, P2: 4, P3: 5, 背景: 6 };
  return order[priority] ?? 9;
}

function frameworkCostRank(cost) {
  const order = { low: 0, medium: 1, high: 2, very_high: 3 };
  return order[cost] ?? 9;
}

function frameworkCostLabel(cost) {
  return {
    low: "低",
    medium: "中",
    high: "高",
    very_high: "很高",
  }[cost] ?? cost;
}

function matchesFrameworkQuery(framework) {
  const q = normalizedQuery();
  if (!q) return true;
  return [
    framework.name,
    framework.category,
    framework.priority,
    ...(framework.benchmarks_run ?? []),
    framework.paper_potential,
    framework.code_status,
    framework.data_status,
    framework.eval_status,
    framework.api_dependency,
    framework.gpu_dependency,
    framework.directory_signal,
    framework.runnable_judgment,
    ...(framework.boost_entries ?? []),
    ...(framework.smoke_test ?? []),
  ]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

function matchesTopVenueQuery(item) {
  const q = normalizedQuery();
  if (!q) return true;
  const requirement = topVenueComputeRequirement(item, state.frameworkData);
  return [
    item.name,
    item.year,
    item.publication_month,
    item.venue,
    item.venue_rating,
    item.status,
    item.task_scope,
    item.runnable_signal,
    item.takeaway,
    requirement.mode,
    requirement.gpu,
    ...(item.benchmarks_run ?? []),
  ]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

function matchesZhipuFrameworkQuery(item) {
  const q = normalizedQuery();
  if (!q) return true;
  const requirement = zhipuComputeRequirement(item);
  return [
    item.name,
    item.framework_type,
    item.zhipu_relation,
    item.publication,
    item.publication_month,
    requirement.mode,
    requirement.gpu,
    item.top_venue ? "顶会" : "非顶会",
    item.is_framework_for_design_bench ? "framework design bench" : "direct model agent",
    ...(item.benchmarks_run ?? []),
    ...(item.sources ?? []),
  ]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

function uniqueItems(items) {
  return Array.from(new Set(items.filter(Boolean)));
}

function miniList(items, limit = 5) {
  const visible = uniqueItems(items).slice(0, limit);
  return `<div class="benchmark-mini-list">${visible.map((item) => `<span>${item}</span>`).join("")}</div>`;
}

function sourceLinks(urls, limit = 2) {
  return (urls ?? [])
    .slice(0, limit)
    .map((url, index) => `<a class="source-link" href="${url}" target="_blank" rel="noreferrer">来源 ${index + 1}</a>`)
    .join(" · ");
}

function frameworkSourceLinks(framework) {
  return sourceLinks(framework.sources);
}

function publicationMonthLabel(item) {
  return item.publication_month ?? item.year ?? "时间待核";
}

function frameworkComputeRequirement(framework = {}) {
  const fallback = {
    design2code: {
      mode: "可只用 API",
      gpu: "闭源模型生成与自动评测不需要 GPU；若本地跑/训 18B 模型，建议 40GB+ 显存。",
    },
    interaction2code: {
      mode: "可只用 API",
      gpu: "交互评测走浏览器 + API key；自部署模型才需要本地 GPU，通常 24-80GB 视模型而定。",
    },
    dcgen: {
      mode: "可只用 API",
      gpu: "默认 GPT-4/GPT-4o 类 API 路线不需要 GPU。",
    },
    designbench: {
      mode: "可只用 API",
      gpu: "多框架评测需要 Node/browser/API key；不需要本地训练 GPU。",
    },
    web2code: {
      mode: "不只 API（训练线）",
      gpu: "小样本 API 评测可无 GPU；本地模型/SFT 建议 40GB+，大规模训练更接近 80GB 级或多卡。",
    },
    ui2code_n: {
      mode: "不只 API（本地 9B）",
      gpu: "只跑 judge 可用 API；本地跑 GLM-4.1V-9B 建议 24-48GB 显存。",
    },
    vab_css: {
      mode: "可只用 API",
      gpu: "API agent 路线不需要 GPU；训练 open LMM 建议 24GB+ 显存。",
    },
    vision2web: {
      mode: "可只用 API（agent 线）",
      gpu: "LiteLLM/Claude Code/OpenHands 可无本地 GPU；自部署 VLM/GUI agent 约 24-80GB。",
    },
    webgen_bench: {
      mode: "不只 API（重型 agent）",
      gpu: "API runner 可跑一部分；自部署 32B UI agent 建议多卡高显存，约 4×40GB 起、80GB 更稳。",
    },
    figma2code: {
      mode: "数据线不只 API",
      gpu: "仅 API 生成可无 GPU；训练/微调 metadata-aware 模型约 24-80GB，取决于模型规模。",
    },
    screencoder: {
      mode: "可只用 API",
      gpu: "Doubao/Qwen/GPT/Gemini API demo 不需要 GPU；post-training 建议 24GB+。",
    },
    visualwebbench: {
      mode: "视模型而定",
      gpu: "闭源 API 不需要 GPU；本地 VLM 通常 24GB+，大模型需要 40-80GB。",
    },
    app_bench: {
      mode: "无需 API/GPU",
      gpu: "人工/产品工具评测为主，不是本地模型推理主线。",
    },
  };
  return framework.compute_requirement ?? fallback[framework.id] ?? {
    mode: framework.api_dependency ?? "待核",
    gpu: framework.gpu_dependency ?? "待核",
  };
}

function requirementCell(requirement) {
  return `<strong>${requirement.mode}</strong><small>${requirement.gpu}</small>`;
}

function topVenueComputeRequirement(item, data = state.frameworkData) {
  const framework = (data?.frameworks ?? []).find((candidate) => candidate.id === item.related_framework_id);
  if (framework) return frameworkComputeRequirement(framework);

  const fallback = {
    webcode2m: {
      mode: "不只 API（数据/训练线）",
      gpu: "只做 API 小样本评测可无 GPU；复现训练/数据线建议 80GB 级或多卡，且需下载 2.56M 数据。",
    },
    webmmu: {
      mode: "可只用 API（评测线）",
      gpu: "Mockup2Code / code editing 评测可用 API；本地 VLM 视规模约 24-80GB。",
    },
    webarena: {
      mode: "不只 API（环境重）",
      gpu: "API agent 可无 GPU；但需要 Docker/自托管网页环境，本地模型约 24-80GB。",
    },
    osworld: {
      mode: "不只 API（桌面环境）",
      gpu: "API agent 可无 GPU；需要虚拟桌面/系统环境，本地多模态模型约 24-80GB。",
    },
    workarena: {
      mode: "不只 API（企业 Web 环境）",
      gpu: "API agent 可无 GPU；需要 BrowserGym/ServiceNow 环境，本地模型约 24-80GB。",
    },
    webagent: {
      mode: "视实现而定",
      gpu: "API planning 可无 GPU；自部署 planner/HTML 模型通常 24-80GB。",
    },
    mind2web: {
      mode: "可只用 API（离线评测）",
      gpu: "离线 action prediction / API agent 可无 GPU；训练 candidate/action model 需 24GB+。",
    },
  };

  return item.compute_requirement ?? fallback[item.related_framework_id] ?? {
    mode: "待核",
    gpu: item.runnable_signal ?? "需继续确认是否有 API-only 路线。",
  };
}

function zhipuComputeRequirement(item) {
  if (item.compute_requirement) return item.compute_requirement;
  const frameworkId = item.name === "UI2Code^N"
    ? "ui2code_n"
    : item.name.includes("VisualAgentBench")
      ? "vab_css"
      : null;
  const framework = (state.frameworkData?.frameworks ?? []).find((candidate) => candidate.id === frameworkId);
  if (framework) return frameworkComputeRequirement(framework);

  if (item.name.includes("AutoWebGLM")) {
    return {
      mode: "可只用 API（Web agent）",
      gpu: "API/托管推理可无 GPU；本地 ChatGLM3-6B 推理约 16-24GB，训练/RL 需多卡。",
    };
  }
  if (item.name.includes("AutoGLM")) {
    return {
      mode: "不只 API（GUI agent）",
      gpu: "只用现成服务可无 GPU；复现 Web/Android RL 需交互环境，本地训练通常 80GB 级或多卡。",
    };
  }
  if (item.name.includes("GLM-5V")) {
    return {
      mode: "可只用 API",
      gpu: "官方 API 跑公开 design bench 不需本地 GPU；自部署同级 VLM 通常需 80GB 级或多卡。",
    };
  }
  return {
    mode: item.is_framework_for_design_bench ? "视 framework 而定" : "视模型而定",
    gpu: "需继续确认 API-only 路线和本地模型规模。",
  };
}

function frameworkBenchmarkTargets(framework, data) {
  const topVenueMatches = (data.top_venue_frameworks ?? []).filter((item) => item.related_framework_id === framework.id);
  return uniqueItems([
    ...(framework.benchmarks_run ?? []),
    ...topVenueMatches.flatMap((item) => item.benchmarks_run ?? []),
  ]);
}

function renderFrameworkSummary() {
  const target = $("#frameworkSummary");
  const frameworkData = state.frameworkData;
  const zhipuData = state.zhipuAgentData;
  if (!target || !frameworkData || !zhipuData) return;

  const firstRound = frameworkData.recommended_first_round?.length ?? 0;
  const zhipuFrameworks = (zhipuData.framework_publication_table ?? []).filter((item) => item.is_framework_for_design_bench).length;
  const topVenue = frameworkData.top_venue_frameworks?.length ?? 0;
  const runnable = frameworkData.frameworks?.length ?? 0;
  const cards = [
    { value: firstRound, label: "第一轮 smoke test 候选" },
    { value: zhipuFrameworks, label: "Zhipu 相关 design framework" },
    { value: topVenue, label: "近年顶会/强会线索" },
    { value: runnable, label: "可跑 framework 总候选" },
  ];

  target.innerHTML = cards
    .map((card) => `<div class="framework-summary-item"><strong>${card.value}</strong><span>${card.label}</span></div>`)
    .join("");
}

function zhipuRunMode(item) {
  if (item.is_framework_for_design_bench) return "Framework 刷 design bench";
  if (/model-level|foundation model/i.test(item.framework_type)) return "模型直接跑分";
  return "Agent framework / 非 design 主线";
}

function renderZhipuFrameworks() {
  const data = state.zhipuAgentData;
  const table = $("#zhipuFrameworkTable");
  if (!data || !table) return;

  const items = (data.framework_publication_table ?? []).filter(matchesZhipuFrameworkQuery);
  $("#zhipuFrameworkMeta").textContent = `${items.length} / ${data.framework_publication_table?.length ?? 0} 条`;
  $("#zhipuFrameworkNote").textContent = data.direct_vs_framework_summary?.short_answer ?? data.answer_summary ?? "";
  table.innerHTML = "";

  if (!items.length) {
    table.innerHTML = `<tr><td colspan="5">没有匹配的 Zhipu framework 线索。</td></tr>`;
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.name}<small>${item.zhipu_relation}</small></td>
      <td>${zhipuRunMode(item)}<small>${item.framework_type}</small></td>
      <td>${miniList(item.benchmarks_run ?? [], 7)}</td>
      <td>${item.publication}<small>发表/公开：${publicationMonthLabel(item)} · ${item.top_venue ? "顶会/强会" : "未确认顶会"} · ${sourceLinks(item.sources)}</small></td>
      <td>${requirementCell(zhipuComputeRequirement(item))}</td>
    `;
    table.appendChild(row);
  });
}

function renderFrameworks() {
  const data = state.frameworkData;
  const highlights = $("#frameworkHighlights");
  const table = $("#frameworkTable");
  const topTable = $("#topVenueTable");
  if (!data) return;

  const frameworks = data.frameworks
    .filter(matchesFrameworkQuery)
    .slice()
    .sort((a, b) => {
      const priorityDelta = frameworkPriorityRank(a.priority) - frameworkPriorityRank(b.priority);
      if (priorityDelta !== 0) return priorityDelta;
      const costDelta = frameworkCostRank(a.engineering_cost) - frameworkCostRank(b.engineering_cost);
      if (costDelta !== 0) return costDelta;
      return a.static_complexity - b.static_complexity;
    });

  const topVenueItems = (data.top_venue_frameworks ?? [])
    .filter(matchesTopVenueQuery)
    .slice()
    .sort((a, b) => b.year - a.year || a.name.localeCompare(b.name));

  $("#frameworkMeta").textContent = `${data.frameworks.length} 候选 · ${data.top_venue_frameworks?.length ?? 0} 顶会线索 · ${state.zhipuAgentData?.framework_publication_table?.length ?? 0} Zhipu`;
  $("#frameworkCandidateMeta").textContent = `${frameworks.length} / ${data.frameworks.length} 个候选`;
  $("#topVenueMeta").textContent = `${topVenueItems.length} / ${data.top_venue_frameworks?.length ?? 0} 条`;
  $("#frameworkNote").textContent = data.scope_note;
  highlights.innerHTML = "";
  table.innerHTML = "";
  topTable.innerHTML = "";

  if (!topVenueItems.length) {
    topTable.innerHTML = `<tr><td colspan="4">没有匹配的顶会/强会线索。</td></tr>`;
  } else {
    topVenueItems.forEach((item) => {
      const row = document.createElement("tr");
      const requirement = topVenueComputeRequirement(item, data);
      row.innerHTML = `
        <td>${item.name}<small>${item.status}</small><small>${sourceLinks(item.sources)}</small></td>
        <td>${item.venue}<small>会议/发表：${publicationMonthLabel(item)} · ${item.venue_rating}</small></td>
        <td>${miniList(item.benchmarks_run ?? [], 6)}</td>
        <td>${requirementCell(requirement)}</td>
      `;
      topTable.appendChild(row);
    });
  }

  if (!frameworks.length) {
    highlights.innerHTML = `<p class="empty">没有匹配的 framework。</p>`;
    table.innerHTML = `<tr><td colspan="5">没有匹配的 framework。</td></tr>`;
    return;
  }

  const recommendedIds = new Set(data.recommended_first_round ?? []);
  const highlightItems = (normalizedQuery() ? frameworks : frameworks.filter((framework) => recommendedIds.has(framework.id))).slice(0, 4);
  highlightItems.forEach((framework) => {
    const complexity = Math.max(0, Math.min(100, (framework.static_complexity / 5) * 100));
    const card = document.createElement("article");
    card.className = "framework-card";
    card.innerHTML = `
      <div class="framework-card-head">
        <div>
          <p class="section-label">${framework.category}</p>
          <h4>${framework.name}</h4>
        </div>
        <span class="priority-pill">${framework.priority}</span>
      </div>
      <p>${framework.runnable_judgment}</p>
      <div class="complexity-meter" aria-label="静态复杂度 ${framework.static_complexity} / 5">
        <span style="--w:${complexity}%"></span>
      </div>
      <div class="framework-facts">
        <span>工程成本：${frameworkCostLabel(framework.engineering_cost)}</span>
        <span>论文潜力：${framework.paper_potential}</span>
        <span>复杂度：${framework.static_complexity}/5</span>
      </div>
      <div class="mini-scores">
        ${(framework.boost_entries ?? []).slice(0, 4).map((item) => `<span class="chip">${item}</span>`).join("")}
      </div>
    `;
    highlights.appendChild(card);
  });

  frameworks.forEach((framework) => {
    const row = document.createElement("tr");
    const benchmarks = frameworkBenchmarkTargets(framework, data);
    const requirement = frameworkComputeRequirement(framework);
    row.innerHTML = `
      <td>${framework.name}<small>${framework.category}</small><small>${frameworkSourceLinks(framework)}</small></td>
      <td>${miniList(benchmarks.length ? benchmarks : [framework.category], 6)}</td>
      <td>${framework.priority}<small>${data.priority_legend?.[framework.priority] ?? ""}</small></td>
      <td>${frameworkCostLabel(framework.engineering_cost)}<small>静态复杂度 ${framework.static_complexity}/5</small></td>
      <td>${requirementCell(requirement)}</td>
    `;
    table.appendChild(row);
  });
}

function normalizeScore(score) {
  if (score.score_scale === "0-1") return score.score * 100;
  return score.score;
}

function formatScore(score) {
  if (typeof score === "number") {
    return Number.isInteger(score) ? String(score) : score.toFixed(score < 1 ? 2 : 1).replace(/\.0$/, "");
  }
  return zhScoreText(score);
}

function scoreTooltipHtml(score) {
  const benchmark = benchmarkById(score.benchmark_id);
  const provenance = score.provenance ?? {};
  return `
    <strong>${score.model} <b>${formatScore(score.score)}</b></strong>
    <span>${benchmark?.name ?? score.benchmark_id} · ${zh(score.metric)} · ${zh(score.score_scale)}</span>
    <span>跑分方：${scoreRunner(score)}</span>
    <span>来源时间：${provenance.run_date_display ?? "未公开"}</span>
  `;
}

function hideScoreTooltip() {
  const tooltip = $("#scoreTooltip");
  if (tooltip) tooltip.hidden = true;
}

function handleScoreCanvasMove(event) {
  const canvas = $("#scoreCanvas");
  const tooltip = $("#scoreTooltip");
  const panel = canvas?.closest(".score-canvas-panel");
  if (!canvas || !tooltip || !panel) return;

  const canvasRect = canvas.getBoundingClientRect();
  const x = event.clientX - canvasRect.left;
  const y = event.clientY - canvasRect.top;
  const hit = state.scoreCanvasBars.find((bar) => x >= bar.x - 2 && x <= bar.x + bar.width + 2 && y >= bar.y - 2 && y <= bar.y + bar.height + 2);
  if (!hit) {
    hideScoreTooltip();
    return;
  }

  tooltip.innerHTML = scoreTooltipHtml(hit.score);
  tooltip.hidden = false;
  const panelRect = panel.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  const padding = 10;
  let left = event.clientX - panelRect.left + 12;
  let top = event.clientY - panelRect.top + 12;
  left = Math.max(padding, Math.min(left, panelRect.width - tooltipRect.width - padding));
  top = Math.max(padding, Math.min(top, panelRect.height - tooltipRect.height - padding));
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function drawScoreCanvas() {
  if (!state.data) return;
  const canvas = $("#scoreCanvas");
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();
  state.scoreCanvasBars = [];
  if (!rect.width || !rect.height) return;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(rect.width * dpr);
  canvas.height = Math.floor(rect.height * dpr);
  ctx.scale(dpr, dpr);
  const width = rect.width;
  const height = rect.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#11130f";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "rgba(244, 240, 230, 0.08)";
  ctx.lineWidth = 1;
  for (let x = 0; x < width; x += 48) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 0; y < height; y += 42) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  const ids = sectionBenchmarkIds();
  const scores = state.data.scores
    .filter((score) => ids.has(score.benchmark_id) && typeof score.score === "number")
    .map((score) => ({ ...score, norm: Math.max(0, Math.min(100, normalizeScore(score))) }))
    .sort((a, b) => b.norm - a.norm)
    .slice(0, 42);

  if (!scores.length) return;
  const gap = 3;
  const barWidth = Math.max(6, (width - 44) / scores.length - gap);
  scores.forEach((score, index) => {
    const h = (score.norm / 100) * (height - 64);
    const x = 24 + index * (barWidth + gap);
    const y = height - 32 - h;
    ctx.fillStyle = benchmarkColor(score.benchmark_id);
    ctx.globalAlpha = score.benchmark_id === state.selectedBenchmarkId ? 1 : 0.52;
    ctx.fillRect(x, y, barWidth, h);
    state.scoreCanvasBars.push({ x, y, width: barWidth, height: h, score });
  });
  ctx.globalAlpha = 1;

  ctx.fillStyle = "#f4f0e6";
  ctx.font = "700 14px Inter, sans-serif";
  ctx.fillText("分数地形", 22, 28);
  ctx.fillStyle = "#a9a394";
  ctx.font = "12px Inter, sans-serif";
  ctx.fillText("当前分组中的数值型分数", 22, 48);
}

function wireEvents() {
  $("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
  $("#resetButton").addEventListener("click", () => {
    state.query = "";
    $("#searchInput").value = "";
    state.activeSectionId = state.data.display_sections[0].id;
    state.activeView = "overview";
    state.activeFrameworkView = "runnable";
    state.selectedBenchmarkId = state.data.display_sections[0].benchmark_ids[0];
    render();
  });
  $("#scoreCanvas").addEventListener("mousemove", handleScoreCanvasMove);
  $("#scoreCanvas").addEventListener("mouseleave", hideScoreTooltip);
  window.addEventListener("resize", () => drawScoreCanvas());
}

wireEvents();
loadData().catch((error) => {
  document.body.innerHTML = `<main class="main-panel"><h1>数据加载失败</h1><p>${error.message}</p></main>`;
});
