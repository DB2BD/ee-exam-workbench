// src/components/questionList.js
/**
 * Question List Component.
 * Filters and renders question cards based on category, subject, year, diff, status, search, and quick filter.
 */

function getSubjectMeta(sid) {
  if (currentExamCategory === 'GK' && typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.subjects) {
    const s = NATIONAL_EXAMS_DATA.subjects.find(s => s.id === sid);
    if (s) return s;
  }
  if (typeof DB_DATA === 'undefined' || !DB_DATA.meta || !DB_DATA.meta.subjects) {
    return { name: '考科', icon: '⚡', color: '#4a7c8f' };
  }
  return DB_DATA.meta.subjects.find(s => s.id === sid) || { name: '未知', icon: '📝', color: '#798694' };
}

let activeFacetTag = null;
let includeSecondaryFacets = false;
let facetContextKey = null;

function getQuestionExamFamily(record, explicitFamily) {
  if (explicitFamily) return explicitFamily;
  return String(record && record[0] || '').startsWith('GK-') ? 'GK' : 'PE';
}

function getQuestionFacetIds(record, includeSecondary, examFamily) {
  const detectedFamily = getQuestionExamFamily(record);
  if ((examFamily || detectedFamily) !== detectedFamily || detectedFamily !== 'PE') return [];
  const qid = record && record[0];
  const evidence = typeof QUESTION_TAXONOMY_MAP !== 'undefined'
    ? QUESTION_TAXONOMY_MAP[qid]
    : null;
  if (!evidence || !evidence.primaryChapter) return [];

  const ids = [evidence.primaryChapter];
  if (includeSecondary && Array.isArray(evidence.secondaryTopicIds)) {
    ids.push(...evidence.secondaryTopicIds);
  }
  return [...new Set(ids)].filter(id => {
    const node = typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[id] : null;
    return node && String(node.subject) === String(record[1]);
  });
}

function getQuestionFacetLabel(facetId) {
  const node = typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[facetId] : null;
  return node && node.name ? node.name : facetId;
}

function uniqueQuestionRecords(records) {
  const seen = new Set();
  return (records || []).filter(record => {
    const qid = record && record[0];
    if (!qid || seen.has(qid)) return false;
    seen.add(qid);
    return true;
  });
}

function matchesQuestionListFilters(record, options) {
  const [qid, sid, year, qnum, topic, tags, solLink, pdfLink, difficulty, status, ftags, hasDedicated] = record;
  const opts = options || {};
  const family = getQuestionExamFamily(record);
  if (opts.examFamily && family !== opts.examFamily) return false;
  if (opts.subject && opts.subject !== 'all' && sid !== opts.subject) return false;
  if (opts.year && opts.year !== 'all' && String(year) !== String(opts.year)) return false;
  if (opts.difficulty && opts.difficulty !== 'all' && String(difficulty) !== String(opts.difficulty)) return false;

  const progress = opts.progressState || {};
  const starred = opts.starredState || {};
  const currentStatus = progress[qid] || 0;
  const isStarred = !!starred[qid];
  if (opts.status && opts.status === 'starred' && !isStarred) return false;
  if (opts.status && opts.status !== 'all' && opts.status !== 'starred' && String(currentStatus) !== String(opts.status)) return false;

  const quick = opts.quickFilter || 'all';
  if (quick === 'review' && currentStatus !== 2) return false;
  if (quick === 'starred' && !isStarred) return false;
  if (quick === 'formula') {
    const formulaTags = Array.isArray(ftags) ? ftags : [];
    if (formulaTags.length === 0 && (!tags || tags.length < 2)) return false;
  }
  if (quick === 'dedicated' && !hasDedicated) return false;
  if (quick === 'due') {
    const dueIds = opts.dueQuestionIds || (typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : []);
    if (!dueIds.includes(qid) && currentStatus !== 2) return false;
  }
  if (quick === 'top10') {
    if (Number(difficulty) < 4 && (!tags || tags.length < 4)) return false;
  }

  const search = String(opts.searchText || '').trim().toLowerCase();
  if (search) {
    const searchable = [qid, topic, ...(tags || []), ...(ftags || [])]
      .map(value => String(value || '').toLowerCase());
    if (!searchable.some(value => value.includes(search))) return false;
  }

  if (opts.facetTag && !getQuestionFacetIds(record, !!opts.includeSecondary, opts.examFamily).includes(opts.facetTag)) {
    return false;
  }
  return true;
}

function getFilteredQuestionRecords(records, options) {
  return uniqueQuestionRecords(records).filter(record => matchesQuestionListFilters(record, options));
}

function getQuestionFacetOptions(records, options) {
  const opts = Object.assign({}, options || {}, { facetTag: null });
  const baseRecords = getFilteredQuestionRecords(records, opts);
  const counts = new Map();
  baseRecords.forEach(record => {
    new Set(getQuestionFacetIds(record, !!opts.includeSecondary, opts.examFamily)).forEach(id => {
      counts.set(id, (counts.get(id) || 0) + 1);
    });
  });
  return [...counts.entries()]
    .map(([id, count]) => ({ id, name: getQuestionFacetLabel(id), count }))
    .sort((left, right) => left.name.localeCompare(right.name, 'zh-Hant'));
}

function buildQuestionFacetModel(records, options) {
  const opts = options || {};
  const questions = getFilteredQuestionRecords(records, opts);
  return {
    examFamily: opts.examFamily || null,
    questions,
    facets: getQuestionFacetOptions(records, opts),
    unclassifiedCount: questions.filter(record => getQuestionFacetIds(record, !!opts.includeSecondary, opts.examFamily).length === 0).length,
  };
}

function refreshAnalysisViews() {
  if (typeof renderTopTopics === 'function') renderTopTopics();
  if (typeof renderLayers === 'function') renderLayers();
}

function setQuestionFacetState(tag, includeSecondary) {
  activeFacetTag = tag || null;
  includeSecondaryFacets = !!includeSecondary;
}

function getQuestionFacetState() {
  return { activeFacetTag, includeSecondary: includeSecondaryFacets };
}

function updateQuestionFacetContext(examFamily, subjectId) {
  const nextKey = `${examFamily}:${subjectId || 'all'}`;
  if (facetContextKey !== null && facetContextKey !== nextKey) {
    setQuestionFacetState(null, false);
  }
  facetContextKey = nextKey;
}

function resetQuestionFacetState() {
  setQuestionFacetState(null, false);
  facetContextKey = null;
}

function setFacetTag(tag) {
  setQuestionFacetState(activeFacetTag === tag ? null : tag, includeSecondaryFacets);
  if (typeof renderQuestions === 'function') renderQuestions();
}

function setSecondaryFacetIncluded(enabled) {
  setQuestionFacetState(activeFacetTag, enabled);
  if (typeof renderQuestions === 'function') renderQuestions();
}

function handleQuestionSubjectFilterChange(subjectId) {
  updateQuestionFacetContext(currentExamCategory, subjectId);
  renderQuestions();
}

function renderFacetTagsBar(currentSubFilter, model) {
  const bar = document.getElementById('facet-filter-bar');
  if (!bar) return;

  const facets = model.facets || [];
  if (facets.length === 0) {
    if (model.examFamily === 'GK' && model.unclassifiedCount > 0) {
      bar.style.display = 'flex';
      bar.innerHTML = '<span class="facet-filter-label">📌 本考別尚無正式章節分類，題目列為未分類</span>';
    } else {
      bar.style.display = 'none';
    }
    return;
  }

  bar.style.display = 'flex';
  let pills = `<span class="facet-filter-label">🎯 考點快篩：</span>`;
  pills += `<label class="facet-secondary-toggle"><input type="checkbox" ${includeSecondaryFacets ? 'checked' : ''} onchange="setSecondaryFacetIncluded(this.checked)"> 包含相關考點</label>`;
  facets.forEach(facet => {
    const isActive = activeFacetTag === facet.id;
    pills += `
      <button class="facet-tag-pill ${isActive ? 'active' : ''}" onclick="setFacetTag('${facet.id}')">
        ${facet.name} <span class="facet-tag-count">(${facet.count})</span>
      </button>
    `;
  });

  if (activeFacetTag) {
    pills += `<button class="facet-tag-pill" style="color:var(--review);border-color:var(--review);" onclick="setFacetTag(null)">✕ 清除標籤快篩</button>`;
  }

  bar.innerHTML = pills;
}

function renderQuestions() {
  const container = document.getElementById('questions-container');
  if (!container) return;

  const subFilter = document.getElementById('filter-subject').value;
  const yrFilter = document.getElementById('filter-year').value;
  const statusFilter = document.getElementById('filter-status').value;
  const diffFilter = document.getElementById('filter-diff').value;
  const searchText = document.getElementById('search-input').value.trim().toLowerCase();

  // Save filters
  localStorage.setItem('filter-subject', subFilter);
  localStorage.setItem('filter-year', yrFilter);
  localStorage.setItem('filter-status', statusFilter);
  localStorage.setItem('filter-diff', diffFilter);

  const activeQuestions = getActiveQuestionsList();

  updateQuestionFacetContext(currentExamCategory, subFilter);
  const model = buildQuestionFacetModel(activeQuestions, {
    examFamily: currentExamCategory,
    subject: subFilter,
    year: yrFilter,
    difficulty: diffFilter,
    status: statusFilter,
    searchText,
    quickFilter: activeQuickFilter,
    progressState,
    starredState,
    facetTag: activeFacetTag,
    includeSecondary: includeSecondaryFacets,
  });

  // Render the same formal-taxonomy model used by the list.
  renderFacetTagsBar(subFilter, model);

  const filtered = model.questions;


  const countBadge = document.getElementById('filtered-count');
  if (countBadge) countBadge.innerText = `顯示 ${filtered.length} 題`;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 60px 20px; color: var(--muted); background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius);">
        <div style="font-size: 2.2rem; margin-bottom: 12px;">🔍</div>
        <h3 style="color: var(--ink); margin-bottom: 6px;">查無符合條件的試題</h3>
        <p style="font-size: 0.88rem;">請嘗試調整或重設篩選條件與搜尋關鍵字</p>
      </div>
    `;
    refreshAnalysisViews();
    return;
  }

  container.innerHTML = filtered.map(q => {
    const [qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, status, ftags, hasDed] = q;
    const meta = getSubjectMeta(sid);
    const curStatus = progressState[qid] || 0;
    const isStarred = !!starredState[qid];

    const starIcons = '⭐'.repeat(Math.max(1, Math.min(5, diff || 3)));
    const statusLabels = ['⚪ 未開始', '🟢 已掌握', '🔴 需二刷'];
    const auditLabels = {
      verified: '✅ 解答已校驗',
      suspected_error: '⚠️ 待更正',
      needs_manual_review: '🟡 待人工覆核',
      not_attempted: '⏳ 尚未校驗',
    };
    const auditLabel = auditLabels[status] || '';

    const dueInfo = typeof getReviewBadgeInfo === 'function' ? getReviewBadgeInfo(qid) : { text: '', cssClass: 'due-none' };

    return `
      <div class="qcard" id="card-${qid}">
        <div class="qhead">
          <div class="qmeta">
            <span class="qid">${qid}</span>
            <span class="qtag" style="background: ${meta.color}15; color: ${meta.color}; border: 1px solid ${meta.color}30;">
              ${meta.icon} ${meta.name.split('（')[0]}
            </span>
            <span class="diff-badge" title="難度評定：${diff} 星">${starIcons}</span>
            ${(tags || []).slice(1, 3).map(t => `<span class="qtag">${t}</span>`).join('')}
            ${auditLabel ? `<span class="qtag solution-audit s-audit-${status}" title="詳解稽核狀態">${auditLabel}</span>` : ''}
          </div>
          <button class="btn-star ${isStarred ? 'active' : ''}" onclick="toggleStarred('${qid}', event)" title="${isStarred ? '取消收藏' : '加入重點收藏'}">
            ${isStarred ? '★' : '☆'}
          </button>
        </div>

        <div class="qtopic">${renderQuestionTopic(topic)}</div>

        <div class="qfooter">
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button class="status-badge s-${curStatus}" onclick="toggleStatus('${qid}', event)" title="點擊切換做題掌握狀態">
              ${statusLabels[curStatus]}
            </button>
            ${dueInfo.text ? `<span class="due-badge ${dueInfo.cssClass}" title="SM-2 智能間隔重複排程">${dueInfo.text}</span>` : ''}
          </div>
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, false, true)" class="btn-sol" style="background: var(--warn); border-color: var(--warn); box-shadow: 0 2px 6px rgba(196, 124, 93, 0.25);" title="開啟白紙蓋牌主動回想抽測">
              🎴 蓋牌抽測
            </button>
            <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, false, false)" class="btn-sol" title="直接檢視完整 KaTeX 推導詳解">
              📝 完整詳解
            </button>
            <a href="${pdfLink}" target="_blank" class="btn-pdf" title="在瀏覽器開啟考選部原題 PDF">
              📄 查看原題 PDF
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');

  refreshAnalysisViews();
}
