// src/components/dailyPractice.js
// Daily practice UI. Persistence and selection rules live in practiceStore.js.

let dailyPracticeView = 'question';
let dailyPracticeCategory = null;
let dailyPracticeSubject = 'all';
let dailyPracticeState = null;

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
  if (typeof getQuestionFacetIds === 'function' && String(question[0] || '').startsWith('EE-')) {
    const ids = getQuestionFacetIds(question, false, 'PE');
    if (ids.length && typeof getQuestionFacetLabel === 'function') return getQuestionFacetLabel(ids[0]);
  }
  const values = kind === 'type' ? question[10] || question[5] : question[5] || [];
  return Array.isArray(values) && values.length ? String(values[0]) : 'unknown';
}

function dailyPracticeLoad() {
  if (typeof loadDailyPracticeStore !== 'function') {
    return { state: { activeSession: null, completionByQuestion: {} }, error: '每日練習模組尚未載入。' };
  }
  return loadDailyPracticeStore();
}

function dailyPracticeAllQuestions() {
  return dailyPracticeQuestions('PE').concat(dailyPracticeQuestions('GK'));
}

function dailyPracticeCurrentQuestion() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session || !Array.isArray(session.questionIds)) return null;
  const qid = session.questionIds[session.currentIndex];
  return dailyPracticeAllQuestions().find(question => question && question[0] === qid) || null;
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
  select.value = dailyPracticeSubject;
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
  initDailyPracticeHome();
}

function dailyPracticeContinue() {
  dailyPracticeView = 'question';
  initDailyPracticeHome();
}

function dailyPracticeStartOver() {
  const loaded = dailyPracticeLoad();
  loaded.state.activeSession = null;
  const result = dailyPracticeSave(loaded.state);
  if (!result.ok) showToast(result.error || '無法清除目前練習。');
  initDailyPracticeHome();
}

function dailyPracticeSetView(view) {
  dailyPracticeView = view === 'solution' ? 'solution' : 'question';
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (session) {
    const qid = session.questionIds[session.currentIndex];
    if (qid) session.revealedByQuestion[qid] = dailyPracticeView === 'solution';
    dailyPracticeSave(session && dailyPracticeState);
  }
  initDailyPracticeHome();
}

function dailyPracticeScroll(event) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return;
  const qid = session.questionIds[session.currentIndex];
  if (!qid) return;
  session.scrollByQuestion[qid] = event.currentTarget.scrollTop;
  if (typeof saveDailyPracticeStore === 'function') saveDailyPracticeStore(dailyPracticeState);
}

function dailyPracticeAdvance(completed) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return;
  const qid = session.questionIds[session.currentIndex];
  if (!qid) return;
  if (completed && typeof markPracticeQuestionCompleted === 'function') {
    const result = markPracticeQuestionCompleted(qid, Date.now());
    if (!result.ok) {
      showToast(result.error || '本題完成狀態無法儲存。');
      return;
    }
    dailyPracticeState = result.state;
  }
  session.currentIndex += 1;
  dailyPracticeView = 'question';
  if (session.currentIndex >= session.questionIds.length) {
    dailyPracticeState.activeSession = null;
    dailyPracticeSave(dailyPracticeState);
    showToast('🎉 本輪每日練習已完成！');
  } else {
    dailyPracticeSave(dailyPracticeState);
  }
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  initDailyPracticeHome();
}

function dailyPracticeSolutionButton(question) {
  const qid = String(question[0] || '').replace(/'/g, '&#39;');
  const solLink = String(question[6] || '').replace(/'/g, '&#39;');
  const qnum = Number(question[3]) || 1;
  return '<div class="daily-practice-solution-note"><p>點開完整詳解可查看雙欄原題、公式推導、來源與驗算。</p>' +
    '<button class="btn-sol" type="button" onclick="openSolutionModal(event, \'' + solLink + '\', \'' + qid + '\', ' + qnum + ', false, false)">📝 開啟完整詳解</button></div>';
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
  if (!session || !question) {
    container.innerHTML = '<section class="daily-practice-shell">' +
      '<div class="daily-practice-heading"><div><span class="eyebrow">第二階段練習入口</span><h2>🎯 今日練習</h2><p>每輪 3 題，優先分散章節與題型，避開 7 天內已完成的題目。</p></div></div>' +
      '<div class="daily-practice-start-card"><label>考別<select id="daily-practice-category" onchange="dailyPracticeSetCategory(this.value)"><option value="PE">電機工程技師（PE）</option><option value="GK">國考同級題庫（GK）</option></select></label>' +
      '<label>範圍<select id="daily-practice-subject"></select></label><button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticeStart()">▶ 開始 3 題練習</button></div>' +
      '<p class="daily-practice-note">開啟題目或查看詳解不會算完成；按下「完成本題」才會進入 7 天避重紀錄。</p></section>';
    const categorySelect = document.getElementById('daily-practice-category');
    if (categorySelect) categorySelect.value = dailyPracticeCategory;
    dailyPracticeSetCategory(dailyPracticeCategory);
    return;
  }
  const qid = question[0];
  const topic = question[4] || '本題';
  const sourceLink = question[7] || '';
  const progress = (session.currentIndex + 1) + ' / ' + session.questionIds.length;
  const scrollTop = Number(session.scrollByQuestion[qid] || 0);
  container.innerHTML = '<section class="daily-practice-shell">' +
    '<div class="daily-practice-heading"><div><span class="eyebrow">' + session.category + ' · ' + (session.subjectId === 'all' ? '跨科混合' : dailyPracticeSubjectLabel(session.category, session.subjectId)) + '</span><h2>🎯 今日練習 <span class="daily-practice-progress">' + progress + '</span></h2></div><button class="btn-pdf" type="button" onclick="dailyPracticeStartOver()">結束本輪</button></div>' +
    '<div class="daily-practice-tabs" role="tablist" aria-label="每日練習內容切換"><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'question' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'question\')">📄 原題</button><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'solution' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'solution\')">📝 詳解</button></div>' +
    '<div class="daily-practice-scroll" onscroll="dailyPracticeScroll(event)" tabindex="0">' +
      (dailyPracticeView === 'question'
        ? '<div class="daily-practice-question"><span class="qid">' + qid + '</span><h3>' + topic + '</h3><p>先自行列式，再切換到「詳解」核對。</p>' + (sourceLink ? '<a class="btn-pdf" href="' + sourceLink + '" target="_blank" rel="noopener">📄 開啟官方原題</a>' : '<p class="daily-practice-muted">本題尚未提供獨立原題連結。</p>') + '</div>'
        : dailyPracticeSolutionButton(question)) +
    '</div><div class="daily-practice-actions"><button class="btn-pdf" type="button" onclick="dailyPracticeAdvance(false)">稍後再做</button><button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticeAdvance(true)">✓ 完成本題並下一題</button></div></section>';
  const scroll = container.querySelector('.daily-practice-scroll');
  if (scroll) scroll.scrollTop = scrollTop;
}

function initDailyPracticeHome() {
  const loaded = dailyPracticeLoad();
  dailyPracticeState = loaded.state;
  const container = document.getElementById('daily-practice-container');
  if (container) renderDailyPractice(container, loaded.error);
}
