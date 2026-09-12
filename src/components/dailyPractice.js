// src/components/dailyPractice.js
// Daily practice UI. Persistence and selection rules live in practiceStore.js.

let dailyPracticeView = 'question';
let dailyPracticeCategory = null;
let dailyPracticeSubject = 'all';
let dailyPracticeState = null;
let dailyPracticeHomeMode = 'continue';
let dailyPracticeLastSummary = null;

function dailyPracticeEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

// Convert legacy PE/GK tuples at one boundary.  Rendering and interaction
// code below consumes the named QuestionRecord fields only.
function dailyPracticeRecord(question, categoryHint) {
  if (!question) return null;
  if (typeof toQuestionRecord === 'function') {
    const record = toQuestionRecord(question, categoryHint);
    const isGK = record.examFamily === 'GK';
    const crop = isGK
      ? (record.provenance && record.provenance.questionCrop) || ''
      : (typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[record.id] || '' : '');
    record.provenance = Object.assign({}, record.provenance, { questionCrop: crop });
    return record;
  }
  return null;
}

function dailyPracticeQuestions(category) {
  if (category === 'GK') {
    return typeof NATIONAL_EXAMS_DATA !== 'undefined' && Array.isArray(NATIONAL_EXAMS_DATA.questions)
      ? NATIONAL_EXAMS_DATA.questions : [];
  }
  return typeof DB_DATA !== 'undefined' && Array.isArray(DB_DATA.questions) ? DB_DATA.questions : [];
}

function dailyPracticeSubjects(category) {
  const data = category === 'GK'
    ? (typeof NATIONAL_EXAMS_DATA !== 'undefined' ? NATIONAL_EXAMS_DATA : null)
    : (typeof DB_DATA !== 'undefined' ? DB_DATA : null);
  return data && Array.isArray(data.subjects) ? data.subjects : [];
}

function dailyPracticeSubjectLabel(category, subjectId) {
  const subject = dailyPracticeSubjects(category).find(item => String(item.id) === String(subjectId));
  return subject ? (subject.icon || '📘') + ' ' + subject.name : '科目 ' + subjectId;
}

function dailyPracticeFacet(question, kind) {
  const record = dailyPracticeRecord(question);
  if (kind === 'chapter' && typeof getQuestionFacetIds === 'function' && record && String(record.id || '').startsWith('EE-')) {
    const ids = getQuestionFacetIds(question, false, 'PE');
    if (ids.length) return String(ids[0]);
  }
  if (!record) return 'unknown';
  if (kind === 'type') return dailyPracticeTypeFromFormulaTags(record.formulaTags);
  const values = record.tags;
  return Array.isArray(values) && values.length ? String(values[0]) : 'unknown';
}

function dailyPracticeTypeFromFormulaTags(tags) {
  const rules = [
    ['thevenin-equivalent', /戴維寧|Thevenin/i],
    ['complex-power', /S\s*=\s*VI\*|複功率/i],
    ['induction-slip', /s\s*=\s*\(N[sS]\s*-\s*N\)\s*\/\s*N[sS]|轉差率/i],
    ['svd', /A\s*=\s*U\s*[Σ\\Sigma]+\s*V/i],
    ['three-phase-power', /sqrt\(3\)|\\sqrt\{3\}.*VI/i],
  ];
  const values = Array.isArray(tags) ? tags.map(String) : [];
  for (const [id, pattern] of rules) if (values.some(value => pattern.test(value))) return id;
  return 'unknown';
}

function dailyPracticeLoad() {
  if (typeof loadDailyPracticeStore !== 'function') {
    return { state: { activeSession: null, completionByQuestion: {} }, error: '每日練習模組尚未載入。' };
  }
  return loadDailyPracticeStore();
}

function dailyPracticeQuestionImage(record) {
  const crop = record && record.provenance ? record.provenance.questionCrop || '' : '';
  if (!crop) return '';
  const qid = record.id;
  const isGK = record.examFamily === 'GK';
  return typeof resolveImageMapUrl === 'function'
    ? resolveImageMapUrl(crop, isGK, qid)
    : crop;
}

function dailyPracticeCurrentQuestion() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session || !Array.isArray(session.questionIds)) return null;
  const qid = session.questionIds[session.currentIndex];
  const raw = dailyPracticeQuestions(session.category).find(question =>
    (Array.isArray(question) ? question[0] : question.id) === qid);
  return raw ? dailyPracticeRecord(raw, session.category) : null;
}

function dailyPracticeSave(state) {
  if (typeof saveDailyPracticeStore !== 'function') return { ok: false, error: '每日練習模組尚未載入。' };
  const result = saveDailyPracticeStore(state);
  if (result.ok) dailyPracticeState = result.state;
  return result;
}

function dailyPracticeSetCategory(category) {
  dailyPracticeCategory = category === 'GK' ? 'GK' : 'PE';
  const select = document.getElementById('daily-practice-subject');
  if (!select) return;
  select.innerHTML = '<option value="all">跨科混合（全部科目）</option>' +
    dailyPracticeSubjects(dailyPracticeCategory).map(subject =>
      '<option value="' + subject.id + '">' + dailyPracticeSubjectLabel(dailyPracticeCategory, subject.id) + '</option>'
    ).join('');
  select.value = dailyPracticeSubjects(dailyPracticeCategory).some(item => String(item.id) === String(dailyPracticeSubject))
    ? dailyPracticeSubject : 'all';
}

function dailyPracticeStart() {
  const categorySelect = document.getElementById('daily-practice-category');
  const subjectSelect = document.getElementById('daily-practice-subject');
  const category = categorySelect ? categorySelect.value : (dailyPracticeCategory || 'PE');
  const subjectId = subjectSelect ? subjectSelect.value : 'all';
  const loaded = dailyPracticeLoad();
  const queue = typeof createDailyPracticeQueue === 'function'
    ? createDailyPracticeQueue(dailyPracticeQuestions(category), {
      subjectId: subjectId,
      count: 3,
      now: Date.now(),
      completionByQuestion: loaded.state.completionByQuestion,
      chapterOf: question => dailyPracticeFacet(question, 'chapter'),
      typeOf: question => dailyPracticeFacet(question, 'type'),
    }) : [];
  if (!queue.length) {
    showToast('目前範圍沒有可安排的每日練習題。');
    return;
  }
  const session = createPracticeSession(category, subjectId, queue, { now: Date.now() });
  const result = typeof savePracticeSession === 'function' ? savePracticeSession(session) : { ok: false };
  if (!result.ok) {
    showToast(result.error || '每日練習進度無法儲存。');
    return;
  }
  dailyPracticeCategory = category;
  dailyPracticeSubject = subjectId;
  dailyPracticeView = 'question';
  dailyPracticeHomeMode = 'continue';
  dailyPracticeLastSummary = null;
  initDailyPracticeHome();
}

function dailyPracticeContinue() {
  dailyPracticeHomeMode = 'continue';
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  const qid = session && session.questionIds[session.currentIndex];
  dailyPracticeView = session && session.viewByQuestion && session.viewByQuestion[qid] === 'solution' ? 'solution' : 'question';
  initDailyPracticeHome();
}

function dailyPracticePrepareNewRound() {
  dailyPracticeHomeMode = 'start';
  dailyPracticeLastSummary = null;
  if (typeof switchTab === 'function') switchTab('practice');
  else initDailyPracticeHome();
  const category = document.getElementById('daily-practice-category');
  if (category && typeof category.focus === 'function') category.focus();
}

function dailyPracticeFindQuestions() {
  if (typeof switchTab === 'function') switchTab('questions');
  const search = document.getElementById('search-input');
  if (search && typeof search.focus === 'function') search.focus();
}

function dailyPracticeStartOver() {
  const loaded = dailyPracticeLoad();
  loaded.state.activeSession = null;
  const result = dailyPracticeSave(loaded.state);
  if (!result.ok) showToast(result.error || '無法清除目前練習。');
  dailyPracticeHomeMode = 'start';
  dailyPracticeLastSummary = null;
  initDailyPracticeHome();
}

function dailyPracticeSetView(view) {
  dailyPracticeView = view === 'solution' ? 'solution' : 'question';
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (session) {
    const qid = session.questionIds[session.currentIndex];
    if (qid) {
      session.viewByQuestion[qid] = dailyPracticeView;
      session.revealedByQuestion[qid] = dailyPracticeView === 'solution';
      dailyPracticeSave(dailyPracticeState);
    }
  }
  initDailyPracticeHome();
}

function dailyPracticeScroll(event) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return;
  const qid = session.questionIds[session.currentIndex];
  if (!qid) return;
  const position = session.scrollByQuestion[qid] || { question: 0, solution: 0 };
  position[dailyPracticeView] = Math.max(0, Number(event.currentTarget.scrollTop) || 0);
  session.scrollByQuestion[qid] = position;
  if (typeof saveDailyPracticeStore === 'function') saveDailyPracticeStore(dailyPracticeState);
}

function dailyPracticeDefer() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return;
  const result = dailyPracticeSave(dailyPracticeState);
  if (!result.ok) {
    showToast(result.error || '本題進度無法儲存。');
    return;
  }
  showToast('已保留本題進度；完成詳解自評後才會進入下一題。');
}

// Compatibility guard for old bookmarks: this never advances or completes.
function dailyPracticeAdvance() { dailyPracticeDefer(); return false; }

function dailyPracticeRecordRecallProgress(level) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return;
  const qid = session.questionIds[session.currentIndex];
  if (!qid) return;
  session.revealLevelByQuestion[qid] = Math.max(session.revealLevelByQuestion[qid] || 0, Math.min(4, Number(level) || 0));
  session.revealedByQuestion[qid] = session.revealLevelByQuestion[qid] > 0;
  dailyPracticeSave(dailyPracticeState);
}

function dailyPracticeGetRecallProgress(qid) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  return session && session.revealLevelByQuestion && session.revealLevelByQuestion[qid]
    ? session.revealLevelByQuestion[qid] : 0;
}

function dailyPracticeGetCurrentQuestionId() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  return session && session.questionIds ? session.questionIds[session.currentIndex] || null : null;
}

function dailyPracticeGetModalState(qid) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  const value = session && session.modalByQuestion && session.modalByQuestion[qid];
  return value || { leftScroll: 0, rightScroll: 0, subQuestion: 0, revealStep: 0, pane: 'question', open: false };
}

function dailyPracticeRecordModalState(qid, patch) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session || !session.questionIds.includes(qid)) return false;
  if (!session.modalByQuestion) session.modalByQuestion = {};
  session.modalByQuestion[qid] = Object.assign({}, dailyPracticeGetModalState(qid), patch || {});
  const result = dailyPracticeSave(dailyPracticeState);
  if (!result.ok && typeof showToast === 'function') showToast(result.error || '閱讀位置無法儲存。');
  return result.ok;
}

function dailyPracticeRestoreOpenModal(question) {
  if (!question || typeof openSolutionModal !== 'function') return;
  const saved = dailyPracticeGetModalState(question.id);
  const modal = typeof document !== 'undefined' ? document.getElementById('solution-modal') : null;
  if (saved.open && modal && !modal.classList.contains('show')) {
    openSolutionModal(null, question.solutionLink, question.id, question.number, { mode: 'daily-practice', recall: true });
  }
}

function dailyPracticeCompleteFromModal(rating, achievedLevel, modalQid) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return false;
  const qid = session.questionIds[session.currentIndex];
  if (!qid || String(modalQid || '') !== String(qid)) {
    showToast('目前詳解題號與每日練習題號不一致，未完成本題。');
    return false;
  }
  if ((Number(achievedLevel) || 0) < 4) {
    showToast('請先完成第 ④ 段完整推導，再進行自評。');
    return false;
  }
  const nextIndex = session.currentIndex + 1;
  const nextSession = nextIndex >= session.questionIds.length ? null : JSON.parse(JSON.stringify(session));
  if (nextSession) nextSession.currentIndex = nextIndex;
  const result = typeof commitPracticeProgress === 'function'
    ? commitPracticeProgress(nextSession, qid, Date.now())
    : { ok: false, error: '每日練習進度模組尚未載入。' };
  if (!result.ok) { showToast(result.error || '每日練習進度無法儲存。'); return false; }
  dailyPracticeState = result.state;
  if (!nextSession) {
    dailyPracticeLastSummary = { category: session.category, subjectId: session.subjectId, total: session.questionIds.length, completed: session.questionIds.length };
    dailyPracticeHomeMode = 'summary';
    showToast('🎉 本輪每日練習已完成！');
  } else {
    dailyPracticeView = 'question';
    dailyPracticeHomeMode = 'continue';
  }
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  if (typeof closeSolutionModal === 'function') closeSolutionModal();
  initDailyPracticeHome();
  return true;
}

function dailyPracticeApplyCompletedAttempt(qid, nextAction) {
  const action = nextAction && typeof nextAction === 'object' ? nextAction : {};
  const state = typeof loadDailyPracticeStore === 'function' ? loadDailyPracticeStore() : { state: dailyPracticeState, error: null };
  if (state.error) { showToast(state.error); return false; }
  dailyPracticeState = state.state;
  if (action.finished) {
    dailyPracticeLastSummary = { category: action.category || 'PE', subjectId: action.subjectId || 'all', total: action.total || 1, completed: action.total || 1, results: action.results || [] };
    dailyPracticeHomeMode = 'summary';
    showToast('🎉 本輪每日練習已完成！');
  } else {
    dailyPracticeView = 'question';
    dailyPracticeHomeMode = 'continue';
  }
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  if (typeof closeSolutionModal === 'function') closeSolutionModal();
  initDailyPracticeHome();
  return true;
}

function dailyPracticeQuestionLabel(qid) {
  const raw = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  const record = raw && typeof toQuestionRecord === 'function' ? toQuestionRecord(raw, String(qid).startsWith('GK-') ? 'GK' : 'PE') : null;
  if (!record) return qid;
  const meta = typeof getSubjectMeta === 'function' ? getSubjectMeta(record.subjectId) : null;
  return `${meta ? meta.name : record.subjectId}・民國${record.year}年・第${record.number}題`;
}

function dailyPracticeScheduleFollowUp(qid, button) {
  if (typeof scheduleDailyPracticeFollowUp !== 'function') return;
  if (button) button.disabled = true;
  const result = scheduleDailyPracticeFollowUp(qid);
  if (!result.ok && button) button.disabled = false;
  if (result.ok && button) button.textContent = `已排入 ${result.nextReviewDate}`;
  if (typeof showToast === 'function') showToast(result.ok ? `${result.message} 下次：${result.nextReviewDate}` : result.message);
}

function dailyPracticeSummaryRows(results) {
  if (!Array.isArray(results) || !results.length) return '<p class="daily-practice-muted">本輪沒有可顯示的逐題自評。</p>';
  const labels = { 1: '🔴 無法完成', 3: '🟡 需要提示', 5: '🟢 獨立完成' };
  return '<div class="daily-practice-result-list">' + results.map(item => '<article class="daily-practice-result-item"><div><strong>' + dailyPracticeEscape(dailyPracticeQuestionLabel(item.qid)) + '</strong><code>' + dailyPracticeEscape(item.qid) + '</code></div><span>' + labels[item.rating] + (item.errorType ? '・' + dailyPracticeEscape(item.errorType) : '') + '</span>' + (item.rating === 1 ? '<button class="btn-pdf" type="button" onclick="dailyPracticeScheduleFollowUp(\'' + dailyPracticeEscape(item.qid) + '\', this)">加入到期複習</button>' : '') + '</article>').join('') + '</div>';
}

function dailyPracticeOpenErrorList() {
  if (typeof switchTab === 'function') switchTab('review');
  if (typeof setReviewFilter === 'function') setReviewFilter('errors');
}

function dailyPracticeSolutionButton() {
  return '<div class="daily-practice-solution-note"><p>先用上方蓋牌模式回想，再依序揭露章節、起手式、公式與完整推導。</p>' +
    '<div class="daily-practice-solution-actions">' +
    '<button class="btn-pdf" type="button" data-daily-open-solution="browse">📝 直接看完整詳解</button>' +
    '</div></div>';
}

function dailyPracticeGetCompletionPrompt() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  const isLast = session && session.currentIndex >= session.questionIds.length - 1;
  return isLast ? '自評即完成本題，並查看本輪摘要' : '自評即完成本題，並進入下一題';
}

function renderDailyPractice(container, error) {
  if (!container) return;
  if (!dailyPracticeCategory) dailyPracticeCategory = typeof currentExamCategory !== 'undefined' ? currentExamCategory : 'PE';
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  const question = dailyPracticeCurrentQuestion();
  if (error) {
    container.innerHTML = '<div class="daily-practice-empty"><h3>每日練習資料暫時無法讀取</h3><p>' + error + '</p><button class="btn-sol" type="button" onclick="dailyPracticeStartOver()">重新開始</button></div>';
    return;
  }
  if (dailyPracticeLastSummary && dailyPracticeHomeMode === 'summary') {
    const summary = dailyPracticeLastSummary;
    container.innerHTML = '<section class="daily-practice-shell daily-practice-summary" aria-live="polite">' +
      '<span class="eyebrow">本輪完成摘要</span><h2>🎉 完成 ' + summary.completed + ' / ' + summary.total + ' 題</h2>' +
      '<p>' + dailyPracticeEscape(summary.category) + ' · ' + (summary.subjectId === 'all' ? '跨科混合' : dailyPracticeEscape(dailyPracticeSubjectLabel(summary.category, summary.subjectId))) + '</p>' +
      dailyPracticeSummaryRows(summary.results) +
      '<div class="daily-practice-actions"><button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticePrepareNewRound()">再練 3 題</button>' +
      ((summary.results || []).some(item => item.rating < 5) ? '<button class="btn-pdf" type="button" onclick="dailyPracticeOpenErrorList()">查看需二刷題目</button>' : '') +
      '<button class="btn-pdf" type="button" onclick="dailyPracticeFindQuestions()">找其他題目</button></div></section>';
    return;
  }
  if (!session || !question || dailyPracticeHomeMode === 'start') {
    const activeNote = session
      ? '<p class="daily-practice-note">目前另有進行中的練習；按下開始後才會以新題組取代，或使用上方「繼續上次」。</p>'
      : '';
    container.innerHTML = '<section class="daily-practice-shell">' +
      '<div class="daily-practice-heading"><div><span class="eyebrow">第二階段練習入口</span><h2>🎯 今日練習</h2><p>每輪 3 題，優先分散章節與題型，避開 7 天內已完成的題目。</p></div></div>' +
      '<div class="daily-practice-start-card"><label>考別<select id="daily-practice-category" onchange="dailyPracticeSetCategory(this.value)"><option value="PE">電機工程技師（PE）</option><option value="GK">國考同級題庫（GK）</option></select></label>' +
      '<label>範圍<select id="daily-practice-subject"></select></label><button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticeStart()">▶ 開始 3 題練習</button></div>' +
      activeNote + '<p class="daily-practice-note">查看題目或詳解不會算完成；必須完成第 ④ 段並自評後，才會進入 7 天避重紀錄。</p></section>';
    const categorySelect = document.getElementById('daily-practice-category');
    if (categorySelect) categorySelect.value = dailyPracticeCategory;
    dailyPracticeSetCategory(dailyPracticeCategory);
    return;
  }
  const qid = question.id;
  const topic = question.stem || '本題';
  const sourceLink = question.sourceLink || '';
  const imageSrc = dailyPracticeQuestionImage(question);
  const imageHtml = imageSrc
    ? '<figure class="daily-practice-source-figure"><img class="daily-practice-source-image" data-daily-zoom-image src="' + dailyPracticeEscape(imageSrc) + '" alt="' + dailyPracticeEscape(qid) + ' 原題截圖；按 Enter 或空白鍵放大" loading="eager" tabindex="0" role="button"><figcaption>原題截圖；點擊、觸控或按 Enter／空白鍵可放大查看。</figcaption></figure>'
    : '<div class="daily-practice-source-missing"><strong>原題截圖尚未建立</strong><span>先以文字題幹練習，並可開啟官方 PDF 查看原圖。</span></div>';
  const progress = (session.currentIndex + 1) + ' / ' + session.questionIds.length;
  const scrollPosition = session.scrollByQuestion[qid] || { question: 0, solution: 0 };
  const scrollTop = Number(scrollPosition[dailyPracticeView] || 0);
  container.innerHTML = '<section class="daily-practice-shell">' +
    '<div class="daily-practice-heading"><div><span class="eyebrow">' + session.category + ' · ' + (session.subjectId === 'all' ? '跨科混合' : dailyPracticeSubjectLabel(session.category, session.subjectId)) + '</span><h2>🎯 今日練習 <span class="daily-practice-progress">' + progress + '</span></h2></div><div class="daily-practice-heading-actions"><button class="btn-sol daily-practice-primary" type="button" data-daily-open-solution="recall">🎴 開始四段蓋牌</button><button class="btn-pdf" type="button" onclick="dailyPracticeStartOver()">結束本輪</button></div></div>' +
    '<div class="daily-practice-tabs" role="tablist" aria-label="每日練習內容切換"><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'question' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'question\')">📄 原題</button><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'solution' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'solution\')">📝 詳解</button></div>' +
    '<div class="daily-practice-scroll" onscroll="dailyPracticeScroll(event)" tabindex="0">' +
      (dailyPracticeView === 'question'
        ? '<div class="daily-practice-question"><span class="qid">' + dailyPracticeEscape(qid) + '</span>' + imageHtml + '<div class="daily-practice-topic"><span class="eyebrow">題幹文字</span>' + (typeof renderQuestionTopic === 'function' ? renderQuestionTopic(topic) : dailyPracticeEscape(topic)) + '</div><p>先自行列式；準備好後可按上方「🎴 開始四段蓋牌」。</p><div class="daily-practice-solution-actions"><button class="btn-pdf" type="button" onclick="dailyPracticeSetView(\'solution\')">📝 其他詳解選項</button></div>' + (sourceLink ? '<a class="btn-pdf" href="' + dailyPracticeEscape(sourceLink) + '" target="_blank" rel="noopener">📄 開啟官方原題 PDF</a>' : '<p class="daily-practice-muted">本題尚未提供獨立原題連結。</p>') + '</div>'
        : dailyPracticeSolutionButton()) +
    '</div><div class="daily-practice-actions"><button class="btn-pdf" type="button" data-daily-defer>暫存本題進度</button></div></section>';
  const scroll = container.querySelector('.daily-practice-scroll');
  if (scroll) scroll.scrollTop = scrollTop;
  if (typeof container.querySelectorAll === 'function') container.querySelectorAll('[data-daily-open-solution]').forEach(button => button.addEventListener('click', event => {
    if (typeof openSolutionModal !== 'function') return;
    openSolutionModal(event, question.solutionLink, question.id, question.number, {
      mode: 'daily-practice', recall: button.dataset.dailyOpenSolution === 'recall'
    });
  }));
  if (typeof container.querySelector === 'function') {
    const deferButton = container.querySelector('[data-daily-defer]');
    if (deferButton) deferButton.addEventListener('click', dailyPracticeDefer);
  }
  const image = typeof container.querySelector === 'function' ? container.querySelector('[data-daily-zoom-image]') : null;
  if (image) {
    if (typeof openImageLightbox === 'function') image.addEventListener('click', () => openImageLightbox(image.src, image.alt, image));
    if (typeof openImageLightbox === 'function') image.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openImageLightbox(image.src, image.alt, image);
      }
    });
    image.addEventListener('error', () => {
      const figure = image.closest('.daily-practice-source-figure');
      if (!figure) return;
      figure.outerHTML = '<div class="daily-practice-source-missing" role="status"><strong>原題截圖載入失敗</strong><span>已切換為官方 PDF，請用原卷核對電路圖與題目配置。</span>' +
        (sourceLink ? '<a class="btn-pdf" href="' + dailyPracticeEscape(sourceLink) + '" target="_blank" rel="noopener">📄 開啟官方原題 PDF</a>' : '<span>本題尚未提供獨立原題連結。</span>') + '</div>';
    }, { once: true });
  }
  dailyPracticeRestoreOpenModal(question);
}

function initDailyPracticeHome() {
  const loaded = dailyPracticeLoad();
  dailyPracticeState = loaded.state;
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (session) {
    const qid = session.questionIds[session.currentIndex];
    dailyPracticeView = session.viewByQuestion && session.viewByQuestion[qid] === 'solution' ? 'solution' : 'question';
  }
  const continueButton = document.getElementById('home-action-continue');
  if (continueButton) {
    const hasSession = !!(dailyPracticeState && dailyPracticeState.activeSession);
    continueButton.disabled = !hasSession;
    continueButton.setAttribute && continueButton.setAttribute('aria-disabled', hasSession ? 'false' : 'true');
  }
  const container = document.getElementById('daily-practice-container');
  if (container) renderDailyPractice(container, loaded.error);
}
