// src/components/reviewPage.js
/** Review Center: shared progress pool with subject and taxonomy filters. */

let reviewFilter = 'due';
let reviewTypeFilter = 'all';

function reviewHtmlEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function setReviewFilter(filter) {
  reviewFilter = ['due', 'wrong', 'starred', 'all'].includes(filter) ? filter : 'due';
  const scope = document.getElementById('review-scope');
  if (scope) scope.value = reviewFilter;
  renderReviewPage();
}

function setReviewTypeFilter(type) {
  reviewTypeFilter = type || 'all';
  renderReviewPage();
}

function getReviewTypeLabel(q) {
  const sid = q[1];
  const topic = String(q[4] || '');
  const tags = Array.isArray(q[5]) ? q[5] : [];
  const formulaTags = Array.isArray(q[10]) ? q[10] : [];
  const haystack = `${topic} ${tags.join(' ')} ${formulaTags.join(' ')}`;
  const keywordTypes = [
    ['電路定理／等效', ['戴維寧', '諾頓', '等效定理', '最大功率轉移']],
    ['暫態與拉氏分析', ['暫態', '拉氏', '開關', '一階電路', '二階電路']],
    ['交流與頻率響應', ['交流', '相量', '頻率響應', '正弦穩態', '諧振']],
    ['三相電路', ['三相', '三線', '三線式']],
    ['功率與功率因數', ['功率因數', '無效功率', '視在功率', '功率']],
    ['半導體與二極體', ['二極體', '二極管', '半導體', '整流']],
    ['放大器與回授', ['放大器', '運算放大', '回授', '差動對']],
    ['數位與邏輯', ['數位', '邏輯閘', '布林', '正反器', '計數器']],
    ['微積分與微分方程', ['微積分', '微分方程', '常微分', '偏微分']],
    ['傅立葉與級數', ['傅立葉', '傅氏', '級數', '拉格朗日']],
    ['線性代數', ['矩陣', '特徵值', '特徵向量', '線性代數']],
    ['控制與系統', ['控制系統', '根軌跡', '奈奎斯特', '波德圖', '狀態空間']],
    ['電機機械', ['變壓器', '感應機', '同步機', '直流機', '電動機']],
    ['電力系統', ['潮流', '短路', '功角', '保護電驛', '電力系統', '穩定度']],
  ];
  const matched = keywordTypes.find(([, words]) => words.some(word => haystack.includes(word)));
  if (matched) return matched[0];
  const subjectName = typeof getSubjectMeta === 'function' ? (getSubjectMeta(sid).name || '') : '';
  const tag = [...tags, ...formulaTags].find(item => item && item !== subjectName && item !== subjectName.split('（')[0]);
  if (tag) return String(tag);
  if (sid === '03') return '工程數學綜合';
  if (sid === '04') return '電機機械綜合';
  if (sid === '05') return '電力系統綜合';
  return '綜合題';
}

function getReviewQuestions() {
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const due = new Set(typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : []);
  const subject = document.getElementById('review-subject');
  const subjectFilter = subject ? subject.value : 'all';
  return questions.filter(q => {
    const qid = q[0];
    const status = typeof progressState !== 'undefined' ? (progressState[qid] || 0) : 0;
    const starred = typeof starredState !== 'undefined' && !!starredState[qid];
    const inScope = reviewFilter === 'due' ? due.has(qid) : reviewFilter === 'wrong' ? status === 2 : reviewFilter === 'starred' ? starred : true;
    return inScope && (subjectFilter === 'all' || q[1] === subjectFilter) && (reviewTypeFilter === 'all' || getReviewTypeLabel(q) === reviewTypeFilter);
  });
}

function populateReviewSubjects() {
  const select = document.getElementById('review-subject');
  if (!select) return;
  const current = select.value || 'all';
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const ids = [...new Set(questions.map(q => q[1]))].sort();
  select.innerHTML = '<option value="all">所有考科</option>' + ids.map(sid => {
    const meta = getSubjectMeta(sid);
    return `<option value="${reviewHtmlEscape(sid)}">${meta.icon || ''} ${reviewHtmlEscape(meta.name)}</option>`;
  }).join('');
  select.value = ids.includes(current) ? current : 'all';
}

function renderReviewPage() {
  const container = document.getElementById('review-container');
  if (!container) return;
  populateReviewSubjects();
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const due = new Set(typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : []);
  const wrong = questions.filter(q => typeof progressState !== 'undefined' && (progressState[q[0]] || 0) === 2).length;
  const starred = questions.filter(q => typeof starredState !== 'undefined' && starredState[q[0]]).length;
  const stats = document.getElementById('review-stats');
  if (stats) stats.innerHTML = [['今日到期', questions.filter(q => due.has(q[0])).length], ['錯題本', wrong], ['收藏', starred], ['目前題庫', questions.length]].map(item => `<div class="review-stat"><span class="label">${item[0]}</span><span class="value">${item[1]}</span></div>`).join('');

  const allTypes = [...new Set(questions.map(getReviewTypeLabel))].sort((a, b) => a.localeCompare(b, 'zh-Hant'));
  if (reviewTypeFilter !== 'all' && !allTypes.includes(reviewTypeFilter)) reviewTypeFilter = 'all';
  const typeFilter = document.getElementById('review-type-filter');
  if (typeFilter) {
    const counts = questions.reduce((map, q) => { const type = getReviewTypeLabel(q); map[type] = (map[type] || 0) + 1; return map; }, {});
    const buttons = [['all', '全部題型', questions.length]].concat(allTypes.map(type => [type, type, counts[type]]));
    typeFilter.innerHTML = buttons.map(([value, label, count]) => `<button type="button" class="pill ${reviewTypeFilter === value ? 'active' : ''}" data-review-type-filter="${reviewHtmlEscape(value)}">${reviewHtmlEscape(label)} (${count})</button>`).join('');
    typeFilter.querySelectorAll('[data-review-type-filter]').forEach(button => button.addEventListener('click', () => setReviewTypeFilter(button.dataset.reviewTypeFilter)));
  }

  const filtered = getReviewQuestions();
  const count = document.getElementById('review-filter-count');
  if (count) count.innerText = `目前 ${filtered.length} 題`;
  if (!filtered.length) {
    const title = reviewFilter === 'due' ? '今天沒有到期複習題' : '目前沒有符合條件的題目';
    container.innerHTML = `<div class="review-empty"><strong>${title}</strong><span>可切換複習範圍或題型，完成題目後再回來集中複習。</span></div>`;
    return;
  }

  const groups = {};
  filtered.forEach(q => { const type = getReviewTypeLabel(q); (groups[type] ||= []).push(q); });
  container.innerHTML = `<div class="review-type-grid">${Object.entries(groups).map(([type, list]) => `<section class="review-type-section" data-review-type="${reviewHtmlEscape(type)}"><div class="review-type-title"><span>📚 ${reviewHtmlEscape(type)}</span><span>${list.length} 題</span></div>${list.map(q => {
    const [qid, sid, year, qnum, topic, tags, solLink] = q;
    const meta = getSubjectMeta(sid);
    const status = typeof progressState !== 'undefined' ? (progressState[qid] || 0) : 0;
    const statusText = status === 2 ? '錯題' : status === 1 ? '已掌握' : '未開始';
    const dueText = due.has(qid) ? '<span class="due-badge due-today">今日到期</span>' : '';
    return `<article class="review-card" data-review-type="${reviewHtmlEscape(type)}"><div class="review-card-meta"><span class="qid">${reviewHtmlEscape(qid)}</span><span class="qtag">${year} 年 · 第 ${qnum} 題</span><span class="qtag">${meta.icon || ''} ${reviewHtmlEscape(meta.name)}</span><span class="qtag">${statusText}</span>${dueText}</div><div class="review-card-topic">${renderQuestionTopic(topic)}</div><div class="review-card-actions"><button class="btn-sol" type="button" data-review-open="${reviewHtmlEscape(qid)}">📝 開啟標準解題</button><button class="btn-sol" type="button" data-review-status="${reviewHtmlEscape(qid)}">循環狀態</button></div></article>`;
  }).join('')}</section>`).join('')}</div>`;
  container.querySelectorAll('[data-review-open]').forEach(button => button.addEventListener('click', () => {
    const q = filtered.find(item => item[0] === button.dataset.reviewOpen);
    if (q && typeof openSolutionModal === 'function') openSolutionModal(null, q[6], q[0], q[3], false, false);
  }));
  container.querySelectorAll('[data-review-status]').forEach(button => button.addEventListener('click', () => {
    if (typeof toggleStatus === 'function') toggleStatus(button.dataset.reviewStatus);
  }));
}

function startReviewSession() {
  setReviewFilter('due');
  const first = getReviewQuestions()[0];
  if (first && typeof openSolutionModal === 'function') openSolutionModal(null, first[6], first[0], first[3], false, true);
}
