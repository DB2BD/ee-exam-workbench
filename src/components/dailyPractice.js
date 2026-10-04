// src/components/dailyPractice.js
// Daily practice UI. Persistence and selection rules live in practiceStore.js.

let dailyPracticeView = 'question';
let dailyPracticeCategory = null;
let dailyPracticeSubject = 'all';
let dailyPracticeState = null;
let dailyPracticeHomeMode = 'continue';
let dailyPracticeLastSummary = null;

// 選題方式: 'balanced' (各科輪流) | 'weighted' (依目標分配) | 'reinforce' (補強) | 'all' (全部隨機) | a PE subject id.
// 預設依日期（本機）：10/18 前各科輪流、10/18–11/01 依目標分配、11/02 起補強；
// 使用者在選單的選擇連同當時階段一起存，階段一換就回到該階段的預設。
const DAILY_PRACTICE_MODE_KEY = 'EE_EXAM_DAILY_PRACTICE_MODE_V1';
const DAILY_PRACTICE_MODE_PHASE_KEY = 'EE_EXAM_DAILY_PRACTICE_MODE_PHASE_V1';

function dailyPracticePhaseNow() {
  return typeof practicePhaseFor === 'function' ? practicePhaseFor(new Date()) : 'p1';
}

function dailyPracticeDefaultMode() {
  return typeof practiceDefaultModeFor === 'function' ? practiceDefaultModeFor(new Date()) : 'weighted';
}

function dailyPracticeValidMode(value) {
  return value === 'all' || value === 'weighted' || value === 'balanced' || value === 'reinforce'
    || (!!value && dailyPracticeSubjects('PE').some(item => String(item.id) === value));
}

function dailyPracticeLoadMode() {
  try {
    if (typeof localStorage !== 'undefined') {
      const value = localStorage.getItem(DAILY_PRACTICE_MODE_KEY);
      const phase = localStorage.getItem(DAILY_PRACTICE_MODE_PHASE_KEY);
      if (dailyPracticeValidMode(value) && phase === dailyPracticePhaseNow()) return value;
    }
  } catch (_) { /* fall back to the date default */ }
  return dailyPracticeDefaultMode();
}

function dailyPracticeSaveMode(mode) {
  try {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(DAILY_PRACTICE_MODE_KEY, String(mode));
    localStorage.setItem(DAILY_PRACTICE_MODE_PHASE_KEY, dailyPracticePhaseNow());
  } catch (_) { /* optional */ }
}

function dailyPracticeSetMode(mode) {
  dailyPracticeSaveMode(mode);
  dailyPracticeSyncModeSubtitle();
  if (typeof document !== 'undefined' && typeof document.getElementById === 'function') {
    const hint = document.getElementById('daily-practice-mode-hint');
    if (hint) hint.textContent = dailyPracticeModeHint(mode);
  }
}

// Short phrase describing how the next round is drawn (follows the chosen mode).
function dailyPracticeModeLabel(mode) {
  const value = mode || dailyPracticeLoadMode();
  if (value === 'all') return '全部隨機';
  if (value === 'weighted') return '依目標分配';
  if (value === 'balanced') return '各科輪流';
  if (value === 'reinforce') return '補強（模考錯題）';
  return '只練 ' + dailyPracticeSubjectLabel('PE', value);
}

// The 今天 pane button subtitle must name the mode actually chosen.
function dailyPracticeSyncModeSubtitle() {
  if (typeof document === 'undefined' || typeof document.querySelector !== 'function') return;
  const small = document.querySelector('#home-action-start small');
  if (small) small.textContent = dailyPracticeModeLabel() + '抽題，按一次就開始';
}

function dailyPracticeModeSelectHtml() {
  const mode = dailyPracticeLoadMode();
  const opts = [['weighted', '依目標分配'], ['balanced', '各科輪流'], ['reinforce', '補強（模考錯題）'], ['all', '全部隨機']].concat(
    dailyPracticeSubjects('PE').map(subject => [String(subject.id), '只練 ' + subject.name]));
  return '<label class="daily-practice-mode">選題方式<select id="daily-practice-mode" onchange="dailyPracticeSetMode(this.value)">' +
    opts.map(([value, label]) => '<option value="' + dailyPracticeEscape(value) + '"' + (value === mode ? ' selected' : '') + '>' + dailyPracticeEscape(label) + '</option>').join('') +
    '</select><small class="daily-practice-mode-hint" id="daily-practice-mode-hint">' + dailyPracticeEscape(dailyPracticeModeHint(mode)) + '</small></label>';
}

function dailyPracticeModeHint(mode) {
  if (mode === 'balanced') return '每輪 3 題來自 3 個不同科目，近 14 天練得少的科目優先。';
  if (mode === 'reinforce') return '先抽模考標 △／× 的題與同章題，其次是近 21 天錯因最多的章；沒有模考紀錄時改為各科輪流。';
  if (mode === 'weighted') return '依目標配分抽題，主攻章多抽。';
  if (mode === 'all') return '不分科目與章節，全部隨機。';
  return '只從這一科抽題。';
}

function dailyPracticeTierBadge(qid) {
  const tier = typeof studyTierFor === 'function' ? studyTierFor(qid) : null;
  if (tier !== 'main' && tier !== 'basic') return '';
  return '<span class="tier-badge tier-' + tier + '" title="' + (tier === 'main' ? '主攻：此章要拿滿分' : '基本分：寫出骨架即可拿分') + '">' + (tier === 'main' ? '主攻' : '基本分') + '</span>';
}

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
  if (data && Array.isArray(data.subjects)) return data.subjects;
  // Production PE bundle keeps the subject list under DB_DATA.meta.subjects.
  return data && data.meta && Array.isArray(data.meta.subjects) ? data.meta.subjects : [];
}

function dailyPracticeSubjectLabel(category, subjectId) {
  const subject = dailyPracticeSubjects(category).find(item => String(item.id) === String(subjectId));
  return subject ? subject.name : '科目 ' + subjectId;
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

function dailyPracticeBuildQueue(mode, questions, loaded) {
  const base = {
    count: 3,
    now: Date.now(),
    completionByQuestion: loaded.state.completionByQuestion,
    chapterOf: question => dailyPracticeFacet(question, 'chapter'),
    typeOf: question => dailyPracticeFacet(question, 'type'),
  };
  if (mode === 'weighted' && typeof createWeightedPracticeQueue === 'function') {
    return createWeightedPracticeQueue(questions, base);
  }
  if (mode === 'balanced' && typeof createBalancedPracticeQueue === 'function') {
    return createBalancedPracticeQueue(questions, base);
  }
  if (mode === 'reinforce' && typeof createReinforcePracticeQueue === 'function') {
    return createReinforcePracticeQueue(questions, base);
  }
  if (typeof createDailyPracticeQueue !== 'function') return [];
  const broad = mode === 'all' || mode === 'weighted' || mode === 'balanced' || mode === 'reinforce';
  return createDailyPracticeQueue(questions, Object.assign({ subjectId: broad ? 'all' : mode }, base));
}

// One click: pick 3 questions by the remembered mode and open the first one.
function dailyPracticeStart() {
  // The selector saves its value on change, so the remembered mode is the single source.
  dailyPracticeStartWithMode(dailyPracticeLoadMode());
}

// Start a round now in the given mode (schedule WEAK／REINF tasks use this). The saved
// selector choice is left alone; the session remembers the mode it was drawn with.
function dailyPracticeStartWithMode(mode) {
  mode = dailyPracticeValidMode(String(mode)) ? String(mode) : dailyPracticeLoadMode();
  const category = 'PE';
  const broad = mode === 'all' || mode === 'weighted' || mode === 'balanced' || mode === 'reinforce';
  const subjectId = broad ? 'all' : mode;
  const loaded = dailyPracticeLoad();
  const queue = dailyPracticeBuildQueue(mode, dailyPracticeQuestions(category), loaded);
  if (!queue.length) {
    showToast('目前範圍沒有可安排的隨機練習題。');
    return;
  }
  const session = createPracticeSession(category, subjectId, queue, { now: Date.now() });
  session.mode = mode;
  const result = typeof savePracticeSession === 'function' ? savePracticeSession(session) : { ok: false };
  if (!result.ok) {
    showToast(result.error || '練習進度無法儲存。');
    return;
  }
  dailyPracticeCategory = category;
  dailyPracticeSubject = subjectId;
  dailyPracticeView = 'question';
  dailyPracticeHomeMode = 'continue';
  dailyPracticeLastSummary = null;
  if (typeof switchTab === 'function') switchTab('practice');
  initDailyPracticeHome();
  dailyPracticeScrollRoundIntoView();
  dailyPracticeOpenCurrentRecall();
}

function dailyPracticeSessionModeLabel(session) {
  if (session && session.mode && dailyPracticeValidMode(String(session.mode))) return dailyPracticeModeLabel(session.mode);
  return dailyPracticeModeLabel(session && session.subjectId !== 'all' ? session.subjectId : dailyPracticeLoadMode());
}

// The round card can sit below the fold (390px); bring it into view so it is
// visible as soon as the cover is closed.
function dailyPracticeScrollRoundIntoView() {
  if (typeof document === 'undefined') return;
  const container = document.getElementById('daily-practice-container');
  if (!container || typeof container.scrollIntoView !== 'function') return;
  const rect = container.getBoundingClientRect ? container.getBoundingClientRect() : null;
  const viewport = typeof window !== 'undefined' ? window.innerHeight || 0 : 0;
  // Only move the page when part of the round sits below the fold (or above the top).
  if (rect && viewport && rect.top >= 0 && rect.bottom <= viewport) return;
  try { container.scrollIntoView({ block: 'start', behavior: 'auto' }); } catch (_) { container.scrollIntoView(); }
}

// Called when the solution window closes: a paused round must be visible and resumable.
function dailyPracticeAfterModalClose() {
  homeMorePracticeSync();
  if (dailyPracticeState && dailyPracticeState.activeSession && dailyPracticeHomeMode !== 'summary') {
    if (typeof requestAnimationFrame === 'function') requestAnimationFrame(dailyPracticeScrollRoundIntoView);
    else dailyPracticeScrollRoundIntoView();
  }
}

// One click opens the current question straight on the four-stage cover (recall mode).
function dailyPracticeOpenCurrentRecall() {
  const question = dailyPracticeCurrentQuestion();
  if (!question || typeof openSolutionModal !== 'function') return false;
  openSolutionModal(null, question.solutionLink, question.id, question.number, { mode: 'daily-practice', recall: true });
  if (typeof homeMorePracticeSync === 'function') homeMorePracticeSync();
  return true;
}

function dailyPracticeContinue() {
  dailyPracticeHomeMode = 'continue';
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  dailyPracticeView = 'question';
  initDailyPracticeHome();
  dailyPracticeScrollRoundIntoView();
  if (session) dailyPracticeOpenCurrentRecall();
}

function dailyPracticePrepareNewRound() {
  // No intermediate screen: start a round straight away with the remembered mode.
  dailyPracticeLastSummary = null;
  dailyPracticeStart();
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
  const current = dailyPracticeGetCurrentQuestionId();
  dailyPracticeView = view === 'solution' && current && dailyPracticeSolutionUnlocked(current) ? 'solution' : 'question';
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
  showToast('已保留本題進度；記錄作答結果後才會進入下一題。');
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

function dailyPracticeFinishQuestion(session, qid) {
  const nextIndex = session.currentIndex + 1;
  const nextSession = nextIndex >= session.questionIds.length ? null : JSON.parse(JSON.stringify(session));
  if (nextSession) nextSession.currentIndex = nextIndex;
  const result = typeof commitPracticeProgress === 'function'
    ? commitPracticeProgress(nextSession, qid, Date.now())
    : { ok: false, error: '每日練習進度模組尚未載入。' };
  if (!result.ok) { showToast(result.error || '每日練習進度無法儲存。'); return false; }
  dailyPracticeState = result.state;
  if (!nextSession) {
    dailyPracticeLastSummary = {
      category: session.category, subjectId: session.subjectId, total: session.questionIds.length,
      completed: session.questionIds.length, qids: session.questionIds.slice(),
      modeLabel: '隨機練習・' + dailyPracticeSessionModeLabel(session)
    };
    dailyPracticeHomeMode = 'summary';
    showToast('本輪隨機練習已完成！');
  } else {
    dailyPracticeView = 'question';
    dailyPracticeHomeMode = 'continue';
  }
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  if (typeof closeSolutionModal === 'function') closeSolutionModal();
  initDailyPracticeHome();
  if (nextSession) dailyPracticeOpenCurrentRecall();
  return true;
}

// Called by the 作答結果卡 (source 'random') after a successful save at stage ④.
function dailyPracticeCompleteFromResultCard(record, achievedLevel) {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  if (!session) return false;
  const qid = session.questionIds[session.currentIndex];
  if (!qid || !record || String(record.qid || '') !== String(qid)) {
    showToast('目前詳解題號與練習題號不一致，未完成本題。');
    return false;
  }
  const level = achievedLevel === undefined ? dailyPracticeGetRecallProgress(qid) : Number(achievedLevel) || 0;
  if (level < 4) {
    showToast('請先完成第 ④ 段完整推導，再記錄結果。');
    return false;
  }
  return dailyPracticeFinishQuestion(session, qid);
}

// Legacy entry (1/3/5 self-rating); the result card replaced it in the default flow.
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
  return dailyPracticeFinishQuestion(session, qid);
}

function dailyPracticeApplyCompletedAttempt(qid, nextAction) {
  const action = nextAction && typeof nextAction === 'object' ? nextAction : {};
  const state = typeof loadDailyPracticeStore === 'function' ? loadDailyPracticeStore() : { state: dailyPracticeState, error: null };
  if (state.error) { showToast(state.error); return false; }
  dailyPracticeState = state.state;
  if (action.finished) {
    dailyPracticeLastSummary = { category: action.category || 'PE', subjectId: action.subjectId || 'all', total: action.total || 1, completed: action.total || 1, results: action.results || [] };
    dailyPracticeHomeMode = 'summary';
    showToast('本輪每日練習已完成！');
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

// Round summary built from the saved 作答結果卡 records (estimate per question).
function dailyPracticeSummaryItems(qids) {
  return (Array.isArray(qids) ? qids : []).map(qid => {
    const record = typeof latestRecordFor === 'function' ? latestRecordFor(qid) : null;
    const tier = typeof studyTierFor === 'function' ? studyTierFor(qid) : null;
    return {
      qid, tier,
      recorded: !!record,
      estimate: record ? record.estimate : null,
      total: record ? record.total : null,
      text: record ? '估計 ' + (Math.round(record.estimate * 100) / 100) + '／' + (Math.round(record.total * 100) / 100) + ' 分' : '未記錄',
      full: !!record && record.estimate >= record.total
    };
  });
}

function dailyPracticeRound2(value) { return Math.round(Number(value) * 100) / 100; }

function dailyPracticeSummaryEstimateRows(qids) {
  const items = dailyPracticeSummaryItems(qids);
  if (!items.length) return '<p class="daily-practice-muted">本輪沒有可顯示的作答結果。</p>';
  const sum = items.reduce((n, item) => n + (item.estimate || 0), 0);
  const total = items.reduce((n, item) => n + (item.total || 0), 0);
  // Tier is a small badge; the estimate is a plain "估計 x／y 分" figure with a
  // meter-free layout so it cannot be mistaken for a score bar.
  return '<ul class="daily-practice-result-list daily-practice-result-list--plain">' + items.map(item =>
    '<li class="daily-practice-result-item"><div class="daily-practice-result-main"><strong>' + dailyPracticeEscape(dailyPracticeQuestionLabel(item.qid)) + '</strong>' +
    '<span class="daily-practice-result-meta">' + dailyPracticeTierBadge(item.qid) + '<code>' + dailyPracticeEscape(item.qid) + '</code></span></div>' +
    '<span class="daily-practice-estimate' + (item.recorded ? '' : ' is-empty') + '">' + dailyPracticeEscape(item.text) + '</span></li>'
  ).join('') + '</ul><p class="daily-practice-total">本輪合計：估計 ' + dailyPracticeRound2(sum) + '／' + dailyPracticeRound2(total) + ' 分（自評估計，非實測）</p>';
}

function dailyPracticeSummaryRows(results) {
  if (!Array.isArray(results) || !results.length) return '<p class="daily-practice-muted">本輪沒有可顯示的逐題自評。</p>';
  const labels = { 1: '無法完成', 3: '需要提示', 5: '獨立完成' };
  return '<div class="daily-practice-result-list">' + results.map(item => '<article class="daily-practice-result-item"><div><strong>' + dailyPracticeEscape(dailyPracticeQuestionLabel(item.qid)) + '</strong><code>' + dailyPracticeEscape(item.qid) + '</code></div><span>' + labels[item.rating] + (item.errorType ? '・' + dailyPracticeEscape(item.errorType) : '') + '</span>' + (item.rating === 1 ? '<button class="btn-pdf" type="button" onclick="dailyPracticeScheduleFollowUp(\'' + dailyPracticeEscape(item.qid) + '\', this)">加入到期複習</button>' : '') + '</article>').join('') + '</div>';
}

function dailyPracticeOpenErrorList() {
  // 複習中心入口已移除：改到題庫瀏覽的「我的錯題本」篩選。
  if (typeof switchTab === 'function') switchTab('questions');
  if (typeof setQuickFilter === 'function') {
    const pill = typeof document !== 'undefined'
      ? Array.from(document.querySelectorAll('.pills-bar .pill')).find(el => /setQuickFilter\('review'/.test(el.getAttribute('onclick') || '')) : null;
    setQuickFilter('review', pill || null);
  }
}

// Full solution entries stay hidden until stage ④ has been revealed.
function dailyPracticeSolutionUnlocked(qid) {
  return dailyPracticeGetRecallProgress(qid) >= 4;
}

function dailyPracticeSolutionButton() {
  return '<div class="daily-practice-solution-note"><p>先用上方蓋牌模式回想，再依序揭露章節、起手式、公式與完整推導。</p>' +
    '<div class="daily-practice-solution-actions">' +
    '<button class="btn-pdf" type="button" data-daily-open-solution="browse">直接看完整詳解</button>' +
    '</div></div>';
}

function dailyPracticeGetCompletionPrompt() {
  const session = dailyPracticeState && dailyPracticeState.activeSession;
  const isLast = session && session.currentIndex >= session.questionIds.length - 1;
  return isLast ? '記錄作答結果即完成本題，並查看本輪摘要' : '記錄作答結果即完成本題，並進入下一題';
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
    const items = summary.qids ? dailyPracticeSummaryItems(summary.qids) : [];
    container.innerHTML = '<section class="daily-practice-shell daily-practice-summary" aria-live="polite">' +
      '<span class="eyebrow">本輪完成摘要</span><h2>完成 ' + summary.completed + ' / ' + summary.total + ' 題</h2>' +
      '<p>' + dailyPracticeEscape(summary.category) + ' · ' + dailyPracticeEscape(summary.modeLabel || (summary.subjectId === 'all' ? '隨機練習' : dailyPracticeSubjectLabel(summary.category, summary.subjectId))) + '</p>' +
      (summary.qids ? dailyPracticeSummaryEstimateRows(summary.qids) : dailyPracticeSummaryRows(summary.results)) +
      '<div class="daily-practice-actions">' + dailyPracticeModeSelectHtml() + '<button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticePrepareNewRound()">再練 3 題</button>' +
      ((summary.qids ? items.some(item => !item.full) : (summary.results || []).some(item => item.rating < 5)) ? '<button class="btn-pdf" type="button" onclick="dailyPracticeOpenErrorList()">查看需二刷題目</button>' : '') +
      '<button class="btn-pdf" type="button" onclick="dailyPracticeFindQuestions()">找其他題目</button></div></section>';
    return;
  }
  if (!session) {
    // The 今天 pane already has the primary 「隨機練習 3 題」 button; idle only
    // shows how questions will be drawn.
    container.innerHTML = '<section class="daily-practice-idle">' + dailyPracticeModeSelectHtml() + '</section>';
    return;
  }
  if (!question || dailyPracticeHomeMode === 'start') {
    const activeNote = session
      ? '<p class="daily-practice-note">目前另有進行中的練習；按下開始後才會以新題組取代，或使用上方「繼續上次」。</p>'
      : '';
    container.innerHTML = '<section class="daily-practice-shell">' +
      '<div class="daily-practice-heading"><div><span class="eyebrow">隨機練習</span><h2>隨機練習 3 題</h2><p>目前選題方式：' + dailyPracticeEscape(dailyPracticeModeLabel()) + '；避開 7 天內已完成與尚未模考的題目。</p></div></div>' +
      '<div class="daily-practice-start-card">' + dailyPracticeModeSelectHtml() + '<button class="btn-sol daily-practice-primary" type="button" onclick="dailyPracticeStart()">▶ 開始 3 題練習</button></div>' +
      activeNote + '<p class="daily-practice-note">查看題目或詳解不算完成；做完第 ④ 段並記錄作答結果後，才會進入 7 天避重紀錄。</p></section>';
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
  const solutionUnlocked = dailyPracticeSolutionUnlocked(qid);
  if (!solutionUnlocked) dailyPracticeView = 'question';
  const startLabel = dailyPracticeGetRecallProgress(qid) > 0 ? '回到四段蓋牌' : '開始四段蓋牌';
  const scrollPosition = session.scrollByQuestion[qid] || { question: 0, solution: 0 };
  const scrollTop = Number(scrollPosition[dailyPracticeView] || 0);
  container.innerHTML = '<section class="daily-practice-shell">' +
    '<div class="daily-practice-heading"><div><span class="eyebrow">' + session.category + ' · ' + dailyPracticeSessionModeLabel(session) + '</span><h2>隨機練習 <span class="daily-practice-progress">' + progress + '</span> ' + dailyPracticeTierBadge(qid) + '</h2></div><div class="daily-practice-heading-actions"><button class="btn-sol daily-practice-primary" type="button" data-daily-open-solution="recall">' + startLabel + '</button><button class="btn-pdf" type="button" onclick="dailyPracticeStartOver()">結束本輪</button></div></div>' +
    (solutionUnlocked
      ? '<div class="daily-practice-tabs" role="tablist" aria-label="每日練習內容切換"><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'question' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'question\')">原題</button><button type="button" class="daily-practice-tab ' + (dailyPracticeView === 'solution' ? 'active' : '') + '" onclick="dailyPracticeSetView(\'solution\')">詳解</button></div>'
      : '') +
    '<div class="daily-practice-scroll" onscroll="dailyPracticeScroll(event)" tabindex="0">' +
      (dailyPracticeView === 'question'
        ? '<div class="daily-practice-question"><span class="qid">' + dailyPracticeEscape(qid) + '</span>' + imageHtml + '<div class="daily-practice-topic"><span class="eyebrow">題幹文字</span>' + (typeof renderQuestionTopic === 'function' ? renderQuestionTopic(topic) : dailyPracticeEscape(topic)) + '</div><p>先自行列式；準備好後可按上方「' + startLabel + '」。</p>' + (solutionUnlocked ? '<div class="daily-practice-solution-actions"><button class="btn-pdf" type="button" onclick="dailyPracticeSetView(\'solution\')">其他詳解選項</button></div>' : '') + (sourceLink ? '<a class="btn-pdf" href="' + dailyPracticeEscape(sourceLink) + '" target="_blank" rel="noopener">開啟官方原題 PDF</a>' : '<p class="daily-practice-muted">本題尚未提供獨立原題連結。</p>') + '</div>'
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
        (sourceLink ? '<a class="btn-pdf" href="' + dailyPracticeEscape(sourceLink) + '" target="_blank" rel="noopener">開啟官方原題 PDF</a>' : '<span>本題尚未提供獨立原題連結。</span>') + '</div>';
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
    dailyPracticeView = session.viewByQuestion && session.viewByQuestion[qid] === 'solution' && dailyPracticeSolutionUnlocked(qid) ? 'solution' : 'question';
  }
  dailyPracticeSyncModeSubtitle();
  const continueButton = document.getElementById('home-action-continue');
  if (continueButton) {
    const hasSession = !!(dailyPracticeState && dailyPracticeState.activeSession);
    continueButton.disabled = !hasSession;
    continueButton.setAttribute && continueButton.setAttribute('aria-disabled', hasSession ? 'false' : 'true');
  }
  const container = document.getElementById('daily-practice-container');
  if (container) renderDailyPractice(container, loaded.error);
  homeMorePracticeSync();
  homeDueReviewRefresh();
}

// v1.2: 排程任務、隨機練習 3 題與到期複習都直接放在今天分頁；「繼續上次」只在有進行中的回合時出現。
let homeMorePracticeObserver = null;
// Keep 「繼續上次」 in step with the solution window: hide when it opens, show when it closes.
function homeMorePracticeWatchModal() {
  if (homeMorePracticeObserver || typeof document === 'undefined' || typeof MutationObserver === 'undefined') return;
  const modal = document.getElementById('solution-modal');
  if (!modal) return;
  homeMorePracticeObserver = new MutationObserver(() => homeMorePracticeSync());
  homeMorePracticeObserver.observe(modal, { attributes: true, attributeFilter: ['class'] });
}

function homeMorePracticeSync() {
  homeMorePracticeWatchModal();
  const row = typeof document !== 'undefined' && document.querySelector ? document.querySelector('.practice-home-secondary') : null;
  if (!row) return;
  const hasSession = !!(dailyPracticeState && dailyPracticeState.activeSession);
  // 「繼續上次」 only while the round is paused (cover closed mid-round).
  const modal = document.getElementById('solution-modal');
  const modalOpen = !!(modal && modal.classList && modal.classList.contains('show'));
  row.hidden = !(hasSession && !modalOpen);
}

function homeDueReviewRefresh() {
  const button = document.getElementById('home-action-due');
  if (!button) return;
  const due = typeof getDueQuestionsList === 'function' ? getDueQuestionsList().length : 0;
  button.disabled = due <= 0;
  if (button.setAttribute) button.setAttribute('aria-disabled', due > 0 ? 'false' : 'true');
  button.innerHTML = '<span class="ui-ico">' + uiIcon('rotate-ccw') + '</span><strong>' + (due > 0 ? '到期複習（' + due + ' 題）' : '到期複習') + '</strong><small>' + (due > 0 ? '用間隔重複複習今天到期的題目' : '今天沒有到期題') + '</small>';
}

function homeStartDueReview() {
  // The 複習中心 pane is gone; the due-review session runs straight from the 今天 pane.
  if (typeof switchTab === 'function') switchTab('practice');
  if (typeof setReviewSubjectFilter === 'function') setReviewSubjectFilter('all');
  if (typeof startReviewSession === 'function') startReviewSession();
}
