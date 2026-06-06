const state = {
  data: null,
  filter: "all",
  query: "",
  sort: "status",
  selectedId: null,
};

const $ = (selector) => document.querySelector(selector);

const filters = [
  { id: "all", label: "全部" },
  { id: "smoke", label: "已跑 smoke" },
  { id: "judged", label: "已 VLM judge" },
  { id: "unjudged", label: "待评分" },
  { id: "rendered", label: "已渲染" },
  { id: "nonhtml", label: "非 HTML 输出" },
  { id: "skipped", label: "未跑通" },
];

const stages = [
  { key: "data", label: "数据", color: "#63d8d1" },
  { key: "smoke", label: "Smoke", color: "#b7e36d" },
  { key: "render", label: "渲染", color: "#f0ca6a" },
  { key: "vlmJudge", label: "VLM", color: "#b59cff" },
  { key: "officialScore", label: "官方分", color: "#ff9364" },
];

function webPath(path) {
  if (!path) return "";
  return `../${path.replaceAll("\\", "/")}`;
}

function formatNumber(value) {
  if (value === null || value === undefined) return "待补";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  return String(value);
}

function outputType(bench) {
  if (bench.counts.html) return "页面";
  if (bench.counts.code) return "代码";
  if (bench.counts.text) return "文本";
  return bench.skipped ? "未跑" : "待核";
}

function visibleBenches() {
  const q = state.query.trim().toLowerCase();
  let items = state.data.benchmarks.filter((bench) => {
    if (state.filter === "smoke" && !bench.counts.selected) return false;
    if (state.filter === "judged" && !bench.judge) return false;
    if (state.filter === "unjudged" && (bench.judge || !bench.counts.selected)) return false;
    if (state.filter === "rendered" && !bench.rendered) return false;
    if (state.filter === "nonhtml" && (bench.counts.html || bench.skipped)) return false;
    if (state.filter === "skipped" && !bench.skipped) return false;
    if (!q) return true;
    return [
      bench.id,
      bench.name,
      bench.family,
      bench.task,
      bench.input,
      bench.output,
      bench.officialScoring,
      bench.nextScoring,
      bench.lossFocus,
    ]
      .join(" ")
      .toLowerCase()
      .includes(q);
  });

  const priorityRank = { 高: 0, 中: 1, 低: 2 };
  const statusRank = { "已跑 smoke": 0, 部分失败: 1, 未跑通: 2, 待处理: 3 };
  items = items.slice().sort((a, b) => {
    if (state.sort === "name") return a.name.localeCompare(b.name);
    if (state.sort === "priority") return (priorityRank[a.priority] ?? 9) - (priorityRank[b.priority] ?? 9) || a.name.localeCompare(b.name);
    if (state.sort === "judge") return (b.judge?.mean ?? -1) - (a.judge?.mean ?? -1) || a.name.localeCompare(b.name);
    return (statusRank[a.status] ?? 9) - (statusRank[b.status] ?? 9) || (priorityRank[a.priority] ?? 9) - (priorityRank[b.priority] ?? 9);
  });
  return items;
}

function selectedBench() {
  return state.data.benchmarks.find((bench) => bench.id === state.selectedId) ?? visibleBenches()[0] ?? state.data.benchmarks[0];
}

function filterCount(filterId) {
  const original = state.filter;
  state.filter = filterId;
  const count = visibleBenches().length;
  state.filter = original;
  return count;
}

function renderFilters() {
  const target = $("#filterList");
  target.innerHTML = filters
    .map(
      (filter) => `
        <button class="filter-button ${state.filter === filter.id ? "is-active" : ""}" type="button" data-filter="${filter.id}">
          <span>${filter.label}</span>
          <b>${filterCount(filter.id)}</b>
        </button>
      `,
    )
    .join("");

  target.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      const first = visibleBenches()[0];
      if (first) state.selectedId = first.id;
      render();
    });
  });
}

function renderKpis() {
  const t = state.data.totals;
  const j = state.data.judge;
  const items = [
    { value: t.smokeBenches, label: "已跑 smoke benchmark" },
    { value: t.selectedSamples, label: "随机样本总数" },
    { value: t.okSamples, label: "HTTP 200 输出" },
    { value: t.renderedImages, label: "已渲染截图" },
    { value: t.vlmJudgedSamples, label: "VLM judge 样本" },
    { value: formatNumber(j.overallMean), label: "VLM judge 总均分" },
  ];
  $("#kpiGrid").innerHTML = items.map((item) => `<div class="kpi"><strong>${item.value}</strong><span>${item.label}</span></div>`).join("");
}

function renderStageLegend() {
  $("#stageLegend").innerHTML = stages
    .map((stage) => `<span class="legend-chip"><i class="legend-dot" style="--dot:${stage.color}"></i>${stage.label}</span>`)
    .join("");
}

function renderBenchNav() {
  const benches = visibleBenches();
  $("#visibleCount").textContent = benches.length;
  $("#benchNav").innerHTML = benches
    .map(
      (bench) => `
        <button class="bench-button ${bench.id === state.selectedId ? "is-active" : ""}" type="button" data-id="${bench.id}">
          <strong>${bench.name}</strong>
          <small>${bench.family} · ${bench.status}</small>
        </button>
      `,
    )
    .join("");
  $("#benchNav").querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.id;
      render();
    });
  });
}

function stageDots(bench) {
  return stages
    .map((stage) => {
      const on = bench.phases?.[stage.key];
      return `<span class="stage-dot ${on ? "" : "is-off"}" style="--dot:${stage.color}" title="${stage.label}: ${on ? "已完成" : "未完成"}"></span>`;
    })
    .join("");
}

function judgeCell(bench) {
  if (!bench.judge) return `<span class="muted">未评分</span>`;
  const w = Math.max(0, Math.min(100, bench.judge.mean));
  return `
    <div class="judge-score">
      <strong>${bench.judge.mean}</strong>
      <div class="judge-track"><span class="judge-fill" style="--w:${w}%"></span></div>
      <span class="muted">${bench.judge.count} 条 · ${bench.judge.model}</span>
    </div>
  `;
}

function renderBenchTable() {
  const benches = visibleBenches();
  const tbody = $("#benchTable");
  tbody.innerHTML = benches
    .map(
      (bench) => `
        <tr class="bench-row ${bench.id === state.selectedId ? "is-selected" : ""}" data-id="${bench.id}">
          <td class="bench-name"><strong>${bench.name}</strong><small>${bench.family} · ${bench.priority}优先级</small></td>
          <td class="task-cell"><strong>${bench.task}</strong><small>${bench.input}</small></td>
          <td class="task-cell"><strong>${outputType(bench)}</strong><small>${bench.output}</small></td>
          <td class="task-cell"><strong>${bench.counts.selected}/${bench.available ?? "?"}</strong><small>ok ${bench.counts.ok} · rendered ${bench.rendered}</small></td>
          <td><div class="stage-line">${stageDots(bench)}</div></td>
          <td>${judgeCell(bench)}</td>
          <td>${bench.nextScoring}</td>
        </tr>
      `,
    )
    .join("");
  tbody.querySelectorAll("tr").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedId = row.dataset.id;
      render();
    });
  });
}

function phaseStrip(bench) {
  return `
    <div class="phase-strip">
      ${stages
        .map(
          (stage) => `
            <div class="phase-cell ${bench.phases?.[stage.key] ? "is-on" : ""}">
              <strong>${stage.label}</strong>
              <span>${bench.phases?.[stage.key] ? "已完成" : "待补"}</span>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderDetail() {
  const bench = selectedBench();
  if (!bench) return;
  const judge = bench.judge
    ? `<p><strong>VLM judge：</strong>${bench.judge.mean} 分，范围 ${bench.judge.min}-${bench.judge.max}，${bench.judge.count} 条。</p>`
    : `<p><strong>VLM judge：</strong>未跑。</p>`;

  $("#detailPanel").innerHTML = `
    <p class="eyebrow">当前选中</p>
    <h2>${bench.name}</h2>
    <p class="muted">${bench.family} · ${bench.status} · ${bench.priority}优先级</p>
    ${phaseStrip(bench)}
    <div class="detail-grid">
      <div class="detail-item"><strong>输入</strong><span>${bench.input}</span></div>
      <div class="detail-item"><strong>输出</strong><span>${bench.output}</span></div>
      <div class="detail-item"><strong>官方评分</strong><span>${bench.officialScoring}</span></div>
      <div class="detail-item"><strong>我们这轮</strong><span>${bench.counts.selected} 条，${bench.counts.ok} 条成功，${bench.rendered} 张渲染图。</span></div>
      <div class="detail-item"><strong>失分焦点</strong><span>${bench.lossFocus}</span></div>
      <div class="detail-item"><strong>下一步</strong><span>${bench.nextScoring}</span></div>
    </div>
    ${judge}
    ${bench.skipReason ? `<p class="muted">${bench.skipReason}</p>` : ""}
  `;
}

function renderQueue() {
  const items = state.data.benchmarks
    .filter((bench) => !bench.skipped && bench.counts.selected && !bench.judge)
    .sort((a, b) => (a.priority === "高" ? -1 : 1) - (b.priority === "高" ? -1 : 1))
    .slice(0, 7);
  $("#queueList").innerHTML = items.length
    ? items
        .map(
          (bench) => `
            <button class="queue-item" type="button" data-id="${bench.id}">
              <strong>${bench.name}</strong>
              <span>${bench.nextScoring}</span>
            </button>
          `,
        )
        .join("")
    : `<p class="empty">当前筛选下没有待评分项。</p>`;
  $("#queueList").querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.id;
      render();
    });
  });
}

function renderJudge() {
  const judged = state.data.benchmarks.filter((bench) => bench.judge);
  $("#judgeMeta").textContent = `${state.data.judge.provider} / ${state.data.judge.model} · ${state.data.judge.totalScored} 条`;
  $("#judgeBars").innerHTML = judged
    .map(
      (bench) => `
        <article class="judge-card">
          <div class="judge-card-head">
            <strong>${bench.name}</strong>
            <span class="score-big">${bench.judge.mean}</span>
          </div>
          <div class="judge-track"><span class="judge-fill" style="--w:${bench.judge.mean}%"></span></div>
          <p class="muted">最低 ${bench.judge.min} · 最高 ${bench.judge.max} · ${bench.lossFocus}</p>
        </article>
      `,
    )
    .join("");

  const cases = judged
    .flatMap((bench) => bench.judge.lowCases.map((item) => ({ ...item, bench: bench.name, benchId: bench.id })))
    .sort((a, b) => a.score - b.score)
    .slice(0, 6);
  $("#lowCaseGallery").innerHTML = cases
    .map(
      (item) => `
        <article class="low-case" data-id="${item.benchId}">
          <div class="low-case-head">
            <strong>${item.bench} / ${item.sampleId}</strong>
            <span>VLM judge ${item.score}</span>
          </div>
          <div class="image-pair">
            <div class="image-tile"><span>目标</span><img src="${webPath(item.target)}" alt="${item.bench} ${item.sampleId} 目标图" loading="lazy" /></div>
            <div class="image-tile"><span>生成</span><img src="${webPath(item.generated)}" alt="${item.bench} ${item.sampleId} 生成图" loading="lazy" /></div>
          </div>
          <p>${item.reason}</p>
        </article>
      `,
    )
    .join("");
  $("#lowCaseGallery").querySelectorAll(".low-case").forEach((node) => {
    node.addEventListener("click", () => {
      state.selectedId = node.dataset.id;
      render();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

function renderRunMeta() {
  const run = state.data.run;
  $("#runName").textContent = `${run.provider} / ${run.model}`;
  $("#runMeta").textContent = `seed ${run.seed} · 每组 ${run.sampleSizePerBench} 条 · max_tokens ${run.maxTokens ?? "不限"}`;
  $("#runSubtitle").textContent = `${state.data.totals.smokeBenches} 个 benchmark 已跑 smoke，${state.data.totals.vlmJudgedSamples} 条已做 VLM judge。`;
}

function render() {
  renderRunMeta();
  renderKpis();
  renderStageLegend();
  renderFilters();
  const benches = visibleBenches();
  if (!benches.some((bench) => bench.id === state.selectedId)) {
    state.selectedId = benches[0]?.id ?? state.data.benchmarks[0]?.id;
  }
  renderBenchNav();
  renderBenchTable();
  renderDetail();
  renderQueue();
  renderJudge();
}

async function init() {
  const response = await fetch("../data/benchmark_run_board.json");
  if (!response.ok) throw new Error(`数据加载失败：${response.status}`);
  state.data = await response.json();
  state.selectedId = state.data.benchmarks[0]?.id;
  $("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
  $("#sortSelect").addEventListener("change", (event) => {
    state.sort = event.target.value;
    render();
  });
  render();
}

init().catch((error) => {
  document.body.innerHTML = `<main class="board-main"><h1>看板加载失败</h1><p>${error.message}</p></main>`;
});
