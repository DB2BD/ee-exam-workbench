// src/components/topTopics.js
/**
 * Seven Layers & formal high-frequency topic analysis component.
 *
 * Statistics and study entries deliberately use the question-list filtering
 * seam. This keeps the displayed denominator, ranking QIDs, and destination
 * QIDs aligned without maintaining a second classifier.
 */

function normalizeSelectedYears(records, options, baseRecords) {
  const opts = options || {};
  if (Array.isArray(opts.selectedYears)) {
    return [...new Set(opts.selectedYears.map(Number).filter(Number.isFinite))].sort((a, b) => a - b);
  }
  if (opts.year && opts.year !== 'all' && Number.isFinite(Number(opts.year))) {
    return [Number(opts.year)];
  }
  return [...new Set((records || []).map(record => Number(record && record[2])).filter(Number.isFinite))]
    .sort((a, b) => a - b);
}

function buildTopicStatistics(records, options) {
  const opts = Object.assign({}, options || {}, {
    facetTag: null,
    includeSecondary: false,
  });
  const allRecords = Array.isArray(records) ? records : [];
  const baseRecords = typeof getFilteredQuestionRecords === 'function'
    ? getFilteredQuestionRecords(allRecords, opts)
    : [];
  const selectedYears = normalizeSelectedYears(allRecords, opts, baseRecords);
  const denominator = baseRecords.length;

  if (denominator === 0 || opts.examFamily === 'GK') {
    return {
      examFamily: opts.examFamily || null,
      denominator,
      selectedYears,
      items: [],
      empty: true,
      message: opts.examFamily === 'GK' ? 'no-formal-taxonomy' : 'no-data',
    };
  }

  const facets = typeof getQuestionFacetOptions === 'function'
    ? getQuestionFacetOptions(allRecords, opts)
    : [];
  const items = facets.map(facet => {
    const facetRecords = getFilteredQuestionRecords(allRecords, Object.assign({}, opts, { facetTag: facet.id }));
    const qids = facetRecords.map(record => record[0]);
    const years = [...new Set(facetRecords.map(record => Number(record[2])).filter(Number.isFinite))]
      .sort((a, b) => a - b);
    return {
      id: facet.id,
      name: facet.name,
      count: qids.length,
      qids,
      years,
      denominator,
      questionPct: Math.round((qids.length / denominator) * 100),
      yearCoveragePct: selectedYears.length ? Math.round((years.length / selectedYears.length) * 100) : 0,
    };
  }).filter(item => item.count > 0)
    .sort((left, right) => right.count - left.count || left.name.localeCompare(right.name, 'zh-Hant'));

  return {
    examFamily: opts.examFamily || null,
    denominator,
    selectedYears,
    items,
    empty: items.length === 0,
    message: items.length === 0 ? 'no-formal-taxonomy' : null,
  };
}

function resolveStudyAction(action, records, options) {
  if (action === 'mock') return [];
  const quickFilter = action || 'all';
  return typeof getFilteredQuestionRecords === 'function'
    ? getFilteredQuestionRecords(records || [], Object.assign({}, options || {}, { quickFilter }))
    : [];
}

function buildStudyLayerModel(records, layers, options) {
  return (layers || []).map(layer => {
    const resolvedRecords = resolveStudyAction(layer.action, records, options);
    return Object.assign({}, layer, {
      qids: resolvedRecords.map(record => record[0]),
      records: resolvedRecords,
      count: resolvedRecords.length,
    });
  });
}

function getCurrentQuestionFilterOptions() {
  const subject = document.getElementById('filter-subject');
  const year = document.getElementById('filter-year');
  const status = document.getElementById('filter-status');
  const diff = document.getElementById('filter-diff');
  const search = document.getElementById('search-input');
  return {
    examFamily: typeof currentExamCategory !== 'undefined' ? currentExamCategory : 'PE',
    subject: subject ? subject.value : 'all',
    year: year ? year.value : 'all',
    difficulty: diff ? diff.value : 'all',
    status: status ? status.value : 'all',
    searchText: search ? search.value.trim().toLowerCase() : '',
    quickFilter: typeof activeQuickFilter !== 'undefined' ? activeQuickFilter : 'all',
    progressState: typeof progressState !== 'undefined' ? progressState : {},
    starredState: typeof starredState !== 'undefined' ? starredState : {},
    dueQuestionIds: typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : [],
  };
}

function getActiveStatsQuestions() {
  if (typeof getActiveQuestionsList === 'function') return getActiveQuestionsList();
  if (typeof DB_DATA !== 'undefined' && Array.isArray(DB_DATA.questions)) return DB_DATA.questions;
  return [];
}

function renderTopTopics() {
  const container = document.getElementById('top-topics-container');
  if (!container) return;

  const options = getCurrentQuestionFilterOptions();
  const model = buildTopicStatistics(getActiveStatsQuestions(), options);
  const categoryLabel = document.getElementById('stats-category-label');
  const yearLabel = document.getElementById('stats-year-range');
  const denominatorLabel = document.getElementById('stats-denominator');
  const totalLabel = document.getElementById('stats-total-count');
  const categoryName = options.examFamily === 'GK' ? '高考三級參考題庫' : '電機工程技師題庫';
  const selectedYearText = model.selectedYears.length
    ? `${model.selectedYears[0]}~${model.selectedYears[model.selectedYears.length - 1]} 年`
    : '目前範圍無年度';
  if (categoryLabel) categoryLabel.innerText = categoryName;
  if (yearLabel) yearLabel.innerText = selectedYearText;
  if (denominatorLabel) denominatorLabel.innerText = model.denominator;
  if (totalLabel) totalLabel.innerText = model.denominator;

  if (model.empty) {
    const message = model.message === 'no-formal-taxonomy'
      ? '此題庫目前沒有可用的正式章節分類，暫不產生章節排行。'
      : '目前年度與篩選條件沒有可計算的正式章節統計。';
    container.innerHTML = `<div style="padding:18px; color:var(--muted); background:var(--bg); border:1px dashed var(--line); border-radius:var(--radius-sm);">${message}</div>`;
    return;
  }

  container.innerHTML = model.items.map(item => `
    <button type="button" onclick="focusStatsTopic('${item.id}')" style="display:block; width:100%; text-align:left; background:var(--bg); border:1px solid var(--line); border-radius:var(--radius-sm); padding:14px 18px; margin-bottom:12px; cursor:pointer; color:var(--ink);">
      <div style="display:flex; justify-content:space-between; align-items:baseline; gap:12px; font-size:0.95rem; margin-bottom:6px;">
        <span style="font-weight:700;">${item.name}</span>
        <span style="color:var(--accent-dark); font-weight:700; font-size:0.9rem;">${item.count} 題</span>
      </div>
      <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:0.82rem; color:var(--muted); margin-bottom:8px;">
        <span>題數占比 ${item.questionPct}%（${item.count}/${item.denominator}）</span>
        <span>有出題年度 ${item.yearCoveragePct}%（${item.years.length}/${model.selectedYears.length}）</span>
      </div>
      <div style="height:8px; background:var(--line); border-radius:9999px; overflow:hidden;"><div style="width:${item.questionPct}%; background:var(--accent); height:100%; border-radius:9999px;"></div></div>
      <div style="font-size:0.78rem; color:var(--muted); margin-top:8px;">點擊後以相同章節 QID 集合查看題目</div>
    </button>
  `).join('');
}

function focusStatsTopic(chapterId) {
  const node = typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[chapterId] : null;
  if (!node || typeof setFacetTag !== 'function') return;
  if (typeof switchTab === 'function') switchTab('questions');

  const sub = document.getElementById('filter-subject');
  if (sub) sub.value = node.subject;
  if (typeof updateQuestionFacetContext === 'function') {
    updateQuestionFacetContext(typeof currentExamCategory !== 'undefined' ? currentExamCategory : 'PE', node.subject);
  }
  if (typeof resetQuestionFacetState === 'function') resetQuestionFacetState();
  setFacetTag(chapterId);
}

function renderLayers() {
  const container = document.getElementById('layers-container');
  if (!container || typeof DB_DATA === 'undefined' || !DB_DATA.sevenLayers) return;

  const questions = getActiveStatsQuestions();
  const state = typeof progressState !== 'undefined' ? progressState : {};
  const options = getCurrentQuestionFilterOptions();
  const models = buildStudyLayerModel(questions, DB_DATA.sevenLayers, options);

  container.innerHTML = models.map(layer => {
    const pool = layer.records;
    const unstable = pool.filter(q => (state[q[0]] || 0) !== 1).length;
    const percent = pool.length ? Math.round(((pool.length - unstable) / pool.length) * 100) : 0;
    const isMock = layer.action === 'mock';
    return `<div style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 18px 22px; margin-bottom: 14px; box-shadow: var(--shadow);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"><h4 style="color: var(--accent-dark); font-size: 1.05rem; font-weight: 700;">${layer.id} · ${layer.title || layer.name || '未命名層級'}</h4><span style="font-size: 0.8rem; font-weight: 600; color: var(--muted); background: var(--bg-secondary); padding: 2px 8px; border-radius: 4px;">${layer.objective || '考試得分'}</span></div>
      <p style="font-size: 0.88rem; color: var(--ink-light); line-height: 1.6; margin-bottom: 10px;">${layer.desc}</p>
      <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:0.82rem; color:var(--muted); margin-bottom:8px;"><span>${isMock ? '建議以整卷模考驗證' : `範圍 ${layer.count} 題 · 尚未穩定 ${unstable} 題`}</span><span>${isMock ? '輸出訓練' : `目前穩定度 ${percent}%`}</span></div>
      <div style="height:7px; background:var(--line); border-radius:9999px; overflow:hidden; margin-bottom:12px;"><div style="width:${isMock ? 0 : percent}%; background:var(--accent); height:100%;"></div></div>
      <button class="btn-sol" type="button" onclick="focusStudyLayer('${layer.action}')">${isMock ? '前往計時模考' : '開始處理這一層'}</button>
    </div>`;
  }).join('');
}

function focusStudyLayer(action) {
  if (action === 'mock') {
    if (typeof switchTab === 'function') switchTab('mock');
    return;
  }
  if (typeof switchTab === 'function') switchTab('questions');
  const sub = document.getElementById('filter-subject');
  const year = document.getElementById('filter-year');
  const status = document.getElementById('filter-status');
  const diff = document.getElementById('filter-diff');
  if (sub) sub.value = 'all';
  if (year) year.value = 'all';
  if (status) status.value = 'all';
  if (diff) diff.value = 'all';
  const quick = ['all', 'formula', 'dedicated', 'review', 'top10', 'due'].includes(action) ? action : 'all';
  if (typeof setQuickFilter === 'function') setQuickFilter(quick);
  else if (typeof renderQuestions === 'function') renderQuestions();
}
