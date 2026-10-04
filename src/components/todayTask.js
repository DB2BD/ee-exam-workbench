// src/components/todayTask.js
// K3 「一鍵開始今天」: next task from the 52-day plan, focused closed-book
// overlay with a phase countdown.  The store and view-model functions are
// pure (no DOM) so they can be tested in a node vm; DOM code is at the bottom.
// Data: DAILY_SCHEDULE (src/data/dailySchedule.generated.js).

const TODAY_TASK_STORAGE_KEY = 'EE_EXAM_TODAY_TASK_V1';
const TODAY_TASK_NEXT_ACTION_TEXT = '寫下一句：下次最先要改的動作（不必回填）。寫完就可以按「完成」。';
const TODAY_TASK_NON_WORK_CODES = ['RECOVERY', 'EXAM-CHECK', 'STOP'];

function todayTaskEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function todayTaskEmptyState() {
  return { completed: {}, active: null };
}

// ---- Store ---------------------------------------------------------------

function todayTaskNormalizeState(raw) {
  const state = todayTaskEmptyState();
  if (!raw || typeof raw !== 'object') return state;
  const tasks = (typeof DAILY_SCHEDULE !== 'undefined' && DAILY_SCHEDULE.tasks) || {};
  if (raw.completed && typeof raw.completed === 'object') {
    Object.keys(raw.completed).forEach(code => {
      if (tasks[code] && typeof raw.completed[code] === 'string') state.completed[code] = raw.completed[code];
    });
  }
  const a = raw.active;
  if (a && typeof a === 'object' && tasks[a.code] && !state.completed[a.code]
      && Number.isInteger(a.phaseIndex) && a.phaseIndex >= 0
      && a.phaseIndex < tasks[a.code].phases.length
      && typeof a.phaseStartedAt === 'number' && isFinite(a.phaseStartedAt)) {
    state.active = { code: a.code, phaseIndex: a.phaseIndex, phaseStartedAt: a.phaseStartedAt };
    const mockId = todayTaskIsMockKind(tasks[a.code]) ? (todayTaskValidMockId(a.mockId) ? a.mockId : todayTaskMockId(tasks[a.code], a.phaseStartedAt)) : '';
    if (mockId) state.active.mockId = mockId;
    if (Array.isArray(a.skipped)) {
      const own = tasks[a.code].qids;
      state.active.skipped = a.skipped.filter(q => typeof q === 'string' && own.indexOf(q) >= 0);
    }
  }
  return state;
}

// ---- Scheduled mock / blind tasks are real mocks (source 'mock' + mockId) --

function todayTaskIsMockKind(task) {
  return !!task && (task.kind === 'mock114' || task.kind === 'blind108');
}

function todayTaskValidMockId(value) {
  return typeof value === 'string' && /^\d+-\d+-\d+$/.test(value);
}

// Same format as mockExam.js: `${year}-${subjectId}-${timestamp}`.
function todayTaskMockId(task, timestamp) {
  const m = /^EE-(\d+)-(\d+)-\d+$/.exec(String(((task && task.qids) || [])[0] || ''));
  return m ? `${m[1]}-${m[2]}-${Number.isFinite(Number(timestamp)) ? Number(timestamp) : Date.now()}` : '';
}

// Scored questions of a scheduled mock (same subset rules as mockExam.js).
function todayTaskScoredQids(task) {
  const qids = task.qids.slice();
  const m = /^EE-(\d+)-(\d+)-\d+$/.exec(String(qids[0] || ''));
  if (!m || typeof MOCK_EXAM_SCORED_SUBSETS === 'undefined') return qids;
  const subset = MOCK_EXAM_SCORED_SUBSETS[m[1] + '-' + m[2]];
  return subset ? qids.filter(q => subset.qids.indexOf(q) >= 0) : qids;
}

// Mock tab finished a full scored paper: complete the matching scheduled MOCK114/BLIND108 task.
// Returns { state, code } (code is null when nothing changed).  Order rules are untouched:
// earlier tasks stay as they are; the current task is still the earliest uncompleted.
function todayTaskCompleteMock(state, year, subjectId, now) {
  const tasks = DAILY_SCHEDULE.tasks;
  const code = DAILY_SCHEDULE.order.find(c => {
    const t = tasks[c];
    if (!todayTaskIsMockKind(t) || state.completed[c]) return false;
    const m = /^EE-(\d+)-(\d+)-\d+$/.exec(String(t.qids[0] || ''));
    return !!m && m[1] === String(year) && m[2] === String(subjectId);
  });
  if (!code) return { state, code: null };
  const completed = Object.assign({}, state.completed);
  completed[code] = new Date(now).toISOString();
  const active = state.active && state.active.code === code ? null : state.active;
  return { state: { completed, active }, code };
}

function todayTaskStorage(storage) {
  if (storage) return storage;
  try { return typeof localStorage !== 'undefined' ? localStorage : null; } catch (_) { return null; }
}

function loadTodayTaskState(storage) {
  try {
    const s = todayTaskStorage(storage);
    const raw = s ? s.getItem(TODAY_TASK_STORAGE_KEY) : null;
    return todayTaskNormalizeState(raw ? JSON.parse(raw) : null);
  } catch (_) {
    return todayTaskEmptyState();
  }
}

function saveTodayTaskState(state, storage) {
  try {
    const s = todayTaskStorage(storage);
    if (!s) return false;
    s.setItem(TODAY_TASK_STORAGE_KEY, JSON.stringify(state));
    return true;
  } catch (_) {
    return false;
  }
}

// ---- Pure transitions (return a new state) -------------------------------

function todayTaskCurrentCode(state) {
  const order = DAILY_SCHEDULE.order;
  for (let i = 0; i < order.length; i++) {
    if (!state.completed[order[i]]) return order[i];
  }
  return null;
}

// Start the current mandatory task, or (optionalCode) one of the optional EXT tasks.
// Optional completion is tracked in `completed` but never moves `order` forward.
function todayTaskStart(state, now, optionalCode) {
  if (state.active) return state;
  let code = todayTaskCurrentCode(state);
  if (optionalCode) {
    const t = DAILY_SCHEDULE.tasks[optionalCode];
    if (!t || !t.optional || state.completed[optionalCode]) return state;
    code = optionalCode;
  }
  if (!code) return state;
  const active = { code, phaseIndex: 0, phaseStartedAt: now };
  const task = DAILY_SCHEDULE.tasks[code];
  if (todayTaskIsMockKind(task)) active.mockId = todayTaskMockId(task, now);
  return { completed: state.completed, active };
}

function todayTaskAdvance(state, now) {
  const a = state.active;
  if (!a) return state;
  const task = DAILY_SCHEDULE.tasks[a.code];
  if (a.phaseIndex + 1 < task.phases.length) {
    const next = { code: a.code, phaseIndex: a.phaseIndex + 1, phaseStartedAt: now };
    if (a.mockId) next.mockId = a.mockId;
    return { completed: state.completed, active: next };
  }
  const completed = Object.assign({}, state.completed);
  completed[a.code] = new Date(now).toISOString();
  return { completed, active: null };
}

function todayTaskAbandon(state) {
  return { completed: state.completed, active: null };
}

// The plan needs no reporting, so learners may have done earlier tasks on
// paper.  Mark every code before `code` done and reopen `code` itself; later
// completions are left alone.
function todayTaskStartFrom(state, code, now) {
  const order = DAILY_SCHEDULE.order;
  const index = order.indexOf(code);
  if (index < 0) return state;
  const completed = Object.assign({}, state.completed);
  const stamp = new Date(now).toISOString();
  order.slice(0, index).forEach(c => { if (!completed[c]) completed[c] = stamp; });
  delete completed[code];
  return { completed, active: null };
}

// ---- View model ----------------------------------------------------------

function todayTaskLocalDate(now) {
  const d = new Date(now);
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}

function todayTaskIsOptional(code) {
  const t = DAILY_SCHEDULE.tasks[code];
  return !!(t && t.optional);
}

// Mandatory work only; optional EXT codes never count toward pace or the day's requirement.
function todayTaskWorkCodes(day) {
  return day.codes.filter(c => TODAY_TASK_NON_WORK_CODES.indexOf(c) < 0 && !todayTaskIsOptional(c));
}

function todayTaskOptionalCodes(day) {
  return day ? day.codes.filter(c => todayTaskIsOptional(c)) : [];
}

function todayTaskPlan(state, todayIso) {
  const days = DAILY_SCHEDULE.days;
  const first = days[0].date;
  const last = days[days.length - 1].date;
  const row = days.find(d => d.date === todayIso) || null;
  let expectedBefore = 0;
  days.forEach(d => { if (d.date < todayIso) expectedBefore += todayTaskWorkCodes(d).length; });
  const done = DAILY_SCHEDULE.order.filter(c => state.completed[c]).length;
  const diff = done - expectedBefore;
  let pace = 'on';
  if (todayIso < first) pace = 'before';
  else if (diff > 0) pace = 'ahead';
  else if (diff < 0) pace = 'behind';
  return { row, diff, pace, currentCode: todayTaskCurrentCode(state), hasOptional: todayTaskOptionalCodes(row).length > 0, beforeStart: todayIso < first, afterEnd: todayIso > last, firstDate: first };
}

// ['CORE-16','CORE-17'] -> 'CORE-16～17'
function todayTaskCodeRange(codes) {
  if (codes.length === 1) return codes[0];
  const first = codes[0];
  const last = codes[codes.length - 1];
  const a = /^(.*?)(\d+)$/.exec(first);
  const b = /^(.*?)(\d+)$/.exec(last);
  if (a && b && a[1] === b[1]) return first + '～' + b[2];
  return first + '～' + last;
}

function todayTaskPlanText(plan) {
  let line = '';
  if (plan.row) {
    const work = todayTaskWorkCodes(plan.row);
    if (work.length && plan.pace === 'behind' && plan.currentCode) {
      return '依日程今天應做到 ' + todayTaskCodeRange(work) + '；你目前在 ' + plan.currentCode + '（若紙本已做過，點下方設定進度）';
    }
    if (work.length) line = '今天日程建議：' + work.join('＋');
    else if (plan.hasOptional) line = '今天日程：沒有必做的新題，有餘力再做選做擴章';
    else line = '今天日程：不開新題';
  } else if (plan.beforeStart) {
    line = '日程自 ' + plan.firstDate + ' 開始';
  } else {
    line = '日程已結束';
  }
  if (plan.pace === 'ahead') line += '（領先 ' + plan.diff + ' 個任務）';
  else if (plan.pace === 'behind') line += '（落後 ' + (-plan.diff) + ' 個任務，從最早未完成的接續，不跳題）';
  else if (plan.pace === 'on') line += '（進度與日程同步）';
  return line;
}

function todayTaskPdfUrl(task) {
  if (!task || !task.pdf) return '';
  const name = String(task.pdf).split('/').pop();
  return 'data/official_pdfs/pe/' + encodeURIComponent(name);
}

function todayTaskPhaseView(task, a, now) {
  const phase = task.phases[a.phaseIndex];
  const total = phase.minutes * 60000;
  const elapsed = Math.min(Math.max(0, now - a.phaseStartedAt), total);
  const remainingMs = total - elapsed;
  const closed = !!phase.closed;
  const isReview = !closed && /核對|對照/.test(phase.label);
  return {
    code: task.code,
    phaseIndex: a.phaseIndex,
    phaseCount: task.phases.length,
    label: phase.label,
    minutes: phase.minutes,
    closed,
    totalMs: total,
    remainingMs,
    expired: remainingMs <= 0,
    isLast: a.phaseIndex === task.phases.length - 1,
    // Question images shown in this phase; closed phases show only their own question(s).
    questionQids: (phase.qids || task.qids).slice(),
    // Solution entry points. Empty (and never rendered) while a closed-book phase runs.
    solutionQids: closed ? [] : task.qids.slice(),
    isReview,
    // 作答結果卡: one card per QID, recorded right after checking.
    resultQids: isReview ? todayTaskScoredQids(task) : [],
    resultSource: todayTaskIsMockKind(task) ? 'mock' : (task.optional ? 'ext' : 'today'),
    // Generated once per task run and stored with the active task, so a reload keeps it.
    resultMockId: todayTaskIsMockKind(task) ? (a.mockId || todayTaskMockId(task, a.phaseStartedAt)) : '',
    skipped: Array.isArray(a.skipped) ? a.skipped.slice() : [],
    phaseStartedAt: a.phaseStartedAt,
    pdfUrl: closed ? todayTaskPdfUrl(task) : '',
    scoringNote: task.scoringNote || '',
    // One-line instruction for phases that otherwise show nothing (docs/上榜預設24時段_核心題路徑.md: 5 分鐘只留一句下次動作).
    instruction: phase.label === '下次動作' ? TODAY_TASK_NEXT_ACTION_TEXT : '',
  };
}

function todayTaskViewModel(state, now) {
  const todayIso = todayTaskLocalDate(now);
  const plan = todayTaskPlan(state, todayIso);
  const planText = todayTaskPlanText(plan);
  const activeTask = state.active ? DAILY_SCHEDULE.tasks[state.active.code] : null;
  const view = activeTask ? todayTaskPhaseView(activeTask, state.active, now) : null;
  const rowCodes = plan.row ? plan.row.codes : [];
  const code = todayTaskCurrentCode(state);
  // Optional EXT task of today's row: secondary while earlier mandatory work is
  // outstanding, primary once caught up (or when every mandatory task is done).
  const extCode = todayTaskOptionalCodes(plan.row).find(c => !state.completed[c]) || null;
  const extPrimary = !!extCode && (plan.diff >= 0 || !code);
  let mode;
  if (rowCodes.indexOf('EXAM-CHECK') >= 0) mode = 'exam-check';
  else if (rowCodes.indexOf('STOP') >= 0 || plan.afterEnd) mode = 'stop';
  else if (!code && !extPrimary && !view) mode = 'done';
  else mode = 'task';
  const primaryCode = extPrimary ? extCode : code;
  const task = primaryCode ? DAILY_SCHEDULE.tasks[primaryCode] : null;
  const extTask = extCode ? DAILY_SCHEDULE.tasks[extCode] : null;
  const total = DAILY_SCHEDULE.order.length;
  const doneCount = DAILY_SCHEDULE.order.filter(c => state.completed[c]).length;
  const minutesOf = t => t ? t.phases.reduce((n, p) => n + p.minutes, 0) : 0;
  return {
    mode,
    planText,
    plan,
    // `code` is the card's current task (earliest uncompleted mandatory, or today's EXT when it is primary).
    code: primaryCode,
    mandatoryCode: code,
    primaryIsOptional: !!task && !!task.optional,
    title: task ? task.title : '',
    totalMinutes: minutesOf(task),
    optional: extTask && !extPrimary ? {
      code: extCode, title: extTask.title, topic: String(extTask.title).replace(/^擴章日｜/, ''),
      minutes: minutesOf(extTask), text: '選做：' + extCode + '｜' + String(extTask.title).replace(/^擴章日｜/, '') + '（有餘力再做）'
    } : null,
    doneCount,
    total,
    active: view,
    activeTitle: activeTask ? activeTask.title : '',
    // 'resume' when a phase is in flight, otherwise 'start'.
    primaryAction: view ? 'resume' : 'start',
  };
}

// ---- DOM -----------------------------------------------------------------

let todayTaskState = null;
let todayTaskTimerHandle = null;
let todayTaskAutoResumed = false;

function todayTaskRefresh() {
  todayTaskState = loadTodayTaskState();
  return todayTaskState;
}

function todayTaskCommit(next) {
  todayTaskState = next;
  saveTodayTaskState(next);
}

function todayTaskFormatClock(ms) {
  const sec = Math.ceil(Math.max(0, ms) / 1000);
  const p = n => String(n).padStart(2, '0');
  return p(Math.floor(sec / 60)) + ':' + p(sec % 60);
}

function todayTaskQuestionImage(qid) {
  const record = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  const isGK = !!record && String(qid).indexOf('GK') === 0;
  const crop = !isGK && typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[qid] || '' : '';
  if (!crop) return '';
  return typeof resolveImageMapUrl === 'function' ? resolveImageMapUrl(crop, isGK, qid) : crop;
}

function renderTodayTaskCard() {
  const host = document.getElementById('today-task-card');
  if (!host) return;
  const state = todayTaskState || todayTaskRefresh();
  const vm = todayTaskViewModel(state, Date.now());
  const plan = '<p class="today-task-plan">' + todayTaskEscape(vm.planText) + '</p>';
  let body;
  if (vm.mode === 'exam-check') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">考前最後確認</span><strong>今天不開新題</strong><p class="today-task-note">只做考務與用品確認：准考證、證件、文具與計算機、交通與時間。</p></div>';
  } else if (vm.mode === 'stop') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">停止新增練習</span><strong>好好休息</strong><p class="today-task-note">只整理睡眠、交通與已備妥的用品；不再開新題。</p></div>';
  } else if (vm.mode === 'done') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">全部完成</span><strong>52 天路徑的 ' + vm.total + ' 個任務都完成了</strong><p class="today-task-note">可改用下方「開始練習」或到期複習，維持手感即可。</p></div>';
  } else {
    const resume = vm.primaryAction === 'resume';
    const label = resume
      ? '進行中：' + vm.active.code + '｜' + vm.activeTitle + '（' + vm.active.label + '）'
      : (vm.primaryIsOptional ? '今天的選做任務：' : '下一個任務：') + vm.code + '｜' + vm.title + ' · ' + vm.totalMinutes + ' 分鐘';
    const optional = vm.optional && !resume
      ? '<div class="today-task-optional"><span>' + todayTaskEscape(vm.optional.text) + '</span>' +
        '<button type="button" class="btn-pdf today-task-optional-start" id="today-task-optional-start" onclick="todayTaskOnStartOptional(\'' + todayTaskEscape(vm.optional.code) + '\')">開始選做</button></div>'
      : '';
    body = '<div class="today-task-main"><span class="today-task-eyebrow">一鍵開始今天</span><strong>' + todayTaskEscape(label) + '</strong>' +
      '<p class="today-task-note">已完成 ' + vm.doneCount + '／' + vm.total + '</p>' + optional + '</div>' +
      '<div class="today-task-actions"><button type="button" class="today-task-start" id="today-task-start" onclick="todayTaskOnStart()">' + (resume ? '繼續' : '開始') + '</button></div>';
  }
  host.innerHTML = '<section class="today-task-card" aria-label="今天的任務">' + body + plan + todayTaskStartFromHtml(vm) + '</section>';
  if (typeof updateHeaderSummary === 'function') updateHeaderSummary();
}

function todayTaskStartFromHtml(vm) {
  if (vm.mode !== 'task' || vm.primaryAction === 'resume') return '';
  const options = DAILY_SCHEDULE.order.map(c => {
    const t = DAILY_SCHEDULE.tasks[c];
    return '<option value="' + todayTaskEscape(c) + '"' + (c === vm.code ? ' selected' : '') + '>' +
      todayTaskEscape(c + '｜' + t.title) + '</option>';
  }).join('');
  return '<details class="today-task-from"><summary>已在紙本做過前面的任務？</summary>' +
    '<label>從這個任務開始：<select id="today-task-from-select">' + options + '</select></label>' +
    '<button type="button" class="btn-pdf" onclick="todayTaskOnStartFrom()">設定</button>' +
    '<p class="today-task-note">之前的任務會標為完成；不會刪除其他練習紀錄。</p></details>';
}

function todayTaskOnStartFrom() {
  const select = document.getElementById('today-task-from-select');
  if (!select) return;
  todayTaskCommit(todayTaskStartFrom(todayTaskRefresh(), select.value, Date.now()));
  renderTodayTaskCard();
}

function todayTaskOnStart() {
  const state = todayTaskRefresh();
  if (!state.active) {
    const vm = todayTaskViewModel(state, Date.now());
    const next = todayTaskStart(state, Date.now(), vm.primaryIsOptional ? vm.code : null);
    if (next === state) return;
    todayTaskCommit(next);
  }
  renderTodayTaskCard();
  openTodayTaskOverlay();
}

function todayTaskOnStartOptional(code) {
  const state = todayTaskRefresh();
  if (!state.active) {
    const next = todayTaskStart(state, Date.now(), code);
    if (next === state) return;
    todayTaskCommit(next);
  }
  renderTodayTaskCard();
  openTodayTaskOverlay();
}

function todayTaskStopTimer() {
  if (todayTaskTimerHandle !== null) {
    clearInterval(todayTaskTimerHandle);
    todayTaskTimerHandle = null;
  }
}

// ---- 作答結果卡 at the review phase: one QID at a time ---------------------

let todayTaskResultFlow = { key: '', index: 0, skipped: [], saved: [], init: false };
let todayTaskResultHandle = null;

function todayTaskCloseResultCard() {
  if (todayTaskResultHandle && typeof todayTaskResultHandle.close === 'function') todayTaskResultHandle.close();
  todayTaskResultHandle = null;
}

function todayTaskResultFlowFor(vm) {
  const key = vm.active.code + ':' + vm.active.phaseIndex + ':' + vm.active.phaseStartedAt;
  if (todayTaskResultFlow.key !== key) todayTaskResultFlow = { key, index: 0, skipped: vm.active.skipped.slice(), saved: [], init: false };
  return todayTaskResultFlow;
}

// Skip state survives a reload: it lives on the active task state (reset when the phase advances).
function todayTaskPersistSkipped(flow) {
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active) return;
  const active = Object.assign({}, state.active, { skipped: flow.skipped.slice() });
  todayTaskCommit({ completed: state.completed, active });
}

// Open docked/inline cards for scheduled mocks carry the task's mockId.
function todayTaskCardOptions(vm, qid) {
  const o = { qid, source: vm.active.resultSource };
  if (vm.active.resultMockId) o.mockId = vm.active.resultMockId;
  return o;
}

// Mock tab completed a full scored paper: sync the matching scheduled task.  Returns the code or null.
function todayTaskSyncMockCompletion(year, subjectId, now) {
  const state = todayTaskRefresh();
  const res = todayTaskCompleteMock(state, year, subjectId, now == null ? Date.now() : now);
  if (!res.code) return null;
  todayTaskCommit(res.state);
  if (typeof document !== 'undefined') {
    if (!res.state.active) { const ov = document.getElementById('today-task-overlay'); if (ov && ov.style.display !== 'none') closeTodayTaskOverlay(); }
    if (document.getElementById('today-task-card')) renderTodayTaskCard();
  }
  return res.code;
}

// A QID is handled once it has a record saved since this phase began, or was explicitly skipped.
function todayTaskQidStatus(qid, flow, since) {
  try {
    if (typeof latestRecordFor === 'function') {
      const r = latestRecordFor(qid);
      if (r && Number(r.at) >= since) return 'saved';
    }
  } catch (_) { /* store unavailable: fall back to this session's saves */ }
  if (flow.saved.indexOf(qid) >= 0) return 'saved';
  if (flow.skipped.indexOf(qid) >= 0) return 'skipped';
  return 'pending';
}

// Pure: progress of the review phase (what the footer button and reason line show).
function todayTaskReviewProgress(qids, flow, since) {
  const items = qids.map(qid => ({ qid, status: todayTaskQidStatus(qid, flow, since) }));
  const pending = items.filter(i => i.status === 'pending').map(i => i.qid);
  return {
    items, pending,
    canFinish: pending.length === 0,
    reason: pending.length
      ? '還有 ' + pending.length + ' 題未處理（' + pending.join('、') + '）：請記錄結果，或按「略過不記錄」。'
      : ''
  };
}

function todayTaskNextPendingIndex(vm, flow, from) {
  const qids = vm.active.resultQids;
  const since = vm.active.phaseStartedAt;
  for (let i = from + 1; i < qids.length; i++) if (todayTaskQidStatus(qids[i], flow, since) === 'pending') return i;
  for (let i = 0; i <= from && i < qids.length; i++) if (todayTaskQidStatus(qids[i], flow, since) === 'pending') return i;
  return qids.length;
}

const TODAY_TASK_STATUS_TEXT = { saved: '已記錄', skipped: '已略過', pending: '未處理' };

function todayTaskOverlayHtml(vm) {
  const v = vm.active;
  const figures = v.questionQids.map(qid => {
    const src = todayTaskQuestionImage(qid);
    const img = src
      ? '<img src="' + todayTaskEscape(src) + '" alt="' + todayTaskEscape(qid) + ' 官方題目裁切圖" loading="eager" data-today-zoom tabindex="0" role="button" aria-label="點擊放大題目圖">' +
        '<p class="today-task-zoom-hint">點圖可放大</p>'
      : '<p class="today-task-note">本題沒有裁切圖。</p>';
    return '<figure class="today-task-figure"><figcaption><code>' + todayTaskEscape(qid) + '</code></figcaption>' + img + '</figure>';
  }).join('');
  const pdf = v.pdfUrl
    ? '<a class="btn-pdf" href="' + todayTaskEscape(v.pdfUrl) + '" target="_blank" rel="noopener">官方原卷 PDF</a>' : '';
  const note = v.scoringNote ? '<p class="today-task-note">計分範圍：' + todayTaskEscape(v.scoringNote) + '</p>' : '';
  const instruction = v.instruction ? '<p class="today-task-instruction" role="note">' + todayTaskEscape(v.instruction) + '</p>' : '';
  let check = '';
  if (!v.closed) {
    check = '<div class="today-task-check"><span>核對題解（開啟後可邊讀邊記錄）：</span>' + v.solutionQids.map(qid =>
      '<button type="button" class="btn-pdf" data-today-check="' + todayTaskEscape(qid) + '">核對 ' + todayTaskEscape(qid) + '</button>').join('') + '</div>';
  }
  let resultSlot = '';
  let progress = null;
  if (v.isReview && v.resultQids.length) {
    progress = todayTaskReviewProgress(v.resultQids, todayTaskResultFlowFor(vm), v.phaseStartedAt);
    resultSlot = '<div class="today-task-result" id="today-task-result"><div class="today-task-result-head"><span id="today-task-result-title"></span>' +
      '<button type="button" class="today-task-skip" data-today-result-next title="先不記錄這題，看下一題">略過不記錄</button></div>' +
      '<div class="today-task-chips" id="today-task-result-chips"></div>' +
      '<div id="today-task-result-mount"></div></div>';
  }
  const timerClass = v.expired ? 'today-task-timer is-expired' : 'today-task-timer';
  const timerText = v.expired ? '時間到' : todayTaskFormatClock(v.remainingMs);
  let controls;
  if (v.closed && !v.expired) {
    controls = '<button type="button" class="today-task-start" data-today-act="next">停筆</button>';
  } else if (progress) {
    controls = '<button type="button" class="today-task-start" id="today-task-finish" data-today-act="next"' + (progress.canFinish ? '' : ' disabled') + '>' + (v.isLast ? '完成核對並結束' : '完成核對 →') + '</button>' +
      '<span class="today-task-reason" id="today-task-reason" role="status">' + todayTaskEscape(progress.reason) + '</span>';
  } else {
    controls = '<button type="button" class="today-task-start" data-today-act="next">' + (v.isLast ? '完成' : '下一步') + '</button>';
  }
  const foot = '<footer class="today-task-foot">' + controls +
    '<button type="button" class="btn-pdf" data-today-act="leave">先離開</button>' +
    '<button type="button" class="btn-pdf" data-today-act="abandon">放棄本次</button></footer>';
  return '<div class="today-task-panel' + (progress ? ' today-task-panel--review' : '') + '" role="dialog" aria-modal="true" aria-label="今天的任務">' +
    '<header class="today-task-head"><div><span class="today-task-eyebrow">' + todayTaskEscape(v.code) + '｜' + todayTaskEscape(vm.activeTitle) + '</span>' +
    '<strong>' + (v.phaseIndex + 1) + '／' + v.phaseCount + ' ' + todayTaskEscape(v.label) + (v.closed ? '（閉卷）' : '') + ' · ' + v.minutes + ' 分鐘</strong></div>' +
    '<div class="' + timerClass + '" id="today-task-timer" role="timer">' + timerText + '</div></header>' +
    '<div class="today-task-body">' + instruction + note + figures + pdf + check + resultSlot + foot + '</div></div>';
}

function renderTodayTaskOverlay() {
  const overlay = document.getElementById('today-task-overlay');
  if (!overlay) return;
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active) { closeTodayTaskOverlay(); return; }
  const vm = todayTaskViewModel(state, Date.now());
  todayTaskCloseResultCard();
  overlay.innerHTML = todayTaskOverlayHtml(vm);
  if (vm.active.isReview) todayTaskMountResultCard(vm);
}

function todayTaskUpdateReviewUi(vm) {
  const flow = todayTaskResultFlowFor(vm);
  const progress = todayTaskReviewProgress(vm.active.resultQids, flow, vm.active.phaseStartedAt);
  const finish = document.getElementById('today-task-finish');
  if (finish) finish.disabled = !progress.canFinish;
  const reason = document.getElementById('today-task-reason');
  if (reason) reason.textContent = progress.reason;
  const chips = document.getElementById('today-task-result-chips');
  if (chips) {
    chips.innerHTML = progress.items.map((it, i) =>
      '<button type="button" class="today-task-chip is-' + it.status + (i === flow.index ? ' is-current' : '') + '" data-today-result-goto="' + i + '">' +
      todayTaskEscape(it.qid) + ' ' + TODAY_TASK_STATUS_TEXT[it.status] + '</button>').join('');
  }
  return progress;
}

function todayTaskMountResultCard(vm) {
  const mount = document.getElementById('today-task-result-mount');
  const title = document.getElementById('today-task-result-title');
  if (!mount) return;
  const flow = todayTaskResultFlowFor(vm);
  const qids = vm.active.resultQids;
  if (!flow.init) { flow.init = true; flow.index = todayTaskNextPendingIndex(vm, flow, -1); }
  const nextButton = document.querySelector('[data-today-result-next]');
  const progress = todayTaskUpdateReviewUi(vm);
  if (flow.index >= qids.length) {
    const savedCount = progress.items.filter(i => i.status === 'saved').length;
    if (title) title.textContent = '作答結果：已處理完 ' + qids.length + ' 題（記錄 ' + savedCount + ' 題）';
    if (nextButton) nextButton.hidden = true;
    mount.innerHTML = '';
    return;
  }
  const qid = qids[flow.index];
  if (title) title.textContent = '記錄作答結果 ' + (flow.index + 1) + '／' + qids.length + '：' + qid;
  if (nextButton) nextButton.hidden = false;
  if (typeof openResultCard !== 'function') return;
  todayTaskResultHandle = openResultCard(Object.assign(todayTaskCardOptions(vm, qid), {
    mount,
    onSaved: () => {
      if (flow.saved.indexOf(qid) < 0) flow.saved.push(qid);
      todayTaskResultHandle = null;
      todayTaskResultAdvance();
    }
  }));
}

function todayTaskResultAdvance(skipCurrent) {
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active) return;
  const vm = todayTaskViewModel(state, Date.now());
  if (!vm.active.isReview) return;
  const flow = todayTaskResultFlowFor(vm);
  const current = vm.active.resultQids[flow.index];
  if (skipCurrent && current && flow.skipped.indexOf(current) < 0) { flow.skipped.push(current); todayTaskPersistSkipped(flow); }
  flow.index = todayTaskNextPendingIndex(vm, flow, flow.index);
  todayTaskCloseResultCard();
  todayTaskMountResultCard(vm);
}

function todayTaskResultGoto(index) {
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active) return;
  const vm = todayTaskViewModel(state, Date.now());
  if (!vm.active.isReview || !(index >= 0 && index < vm.active.resultQids.length)) return;
  const flow = todayTaskResultFlowFor(vm);
  flow.index = index;
  const qid = vm.active.resultQids[index];
  if (flow.skipped.indexOf(qid) >= 0) { flow.skipped = flow.skipped.filter(q => q !== qid); todayTaskPersistSkipped(flow); }
  todayTaskCloseResultCard();
  todayTaskMountResultCard(vm);
}

// After the solution modal closes (or a docked card saved): re-read saved state.  The inline card
// is only replaced when its QID was meanwhile recorded, so half-marked inline input survives.
function todayTaskAfterSolution() {
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active || !document.getElementById('today-task-result-mount')) return;
  const vm = todayTaskViewModel(state, Date.now());
  if (!vm.active.isReview) return;
  const flow = todayTaskResultFlowFor(vm);
  const qid = vm.active.resultQids[flow.index];
  if (!qid || todayTaskQidStatus(qid, flow, vm.active.phaseStartedAt) === 'saved') {
    flow.index = todayTaskNextPendingIndex(vm, flow, flow.index);
    todayTaskCloseResultCard();
  }
  if (todayTaskResultHandle) todayTaskUpdateReviewUi(vm);
  else todayTaskMountResultCard(vm);
}

function todayTaskTick() {
  const state = todayTaskState;
  if (!state || !state.active) { todayTaskStopTimer(); return; }
  const vm = todayTaskViewModel(state, Date.now());
  const el = document.getElementById('today-task-timer');
  if (!el) return;
  if (vm.active.expired) {
    todayTaskStopTimer();
    // A review phase hosts the result card: do not rebuild it (that would drop the marks).
    if (vm.active.closed) renderTodayTaskOverlay();
    else { el.textContent = '時間到'; el.classList.add('is-expired'); }
  } else {
    el.textContent = todayTaskFormatClock(vm.active.remainingMs);
  }
}

function openTodayTaskOverlay() {
  todayTaskRefresh();
  if (!todayTaskState.active) return;
  let overlay = document.getElementById('today-task-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'today-task-overlay';
    overlay.className = 'today-task-overlay';
    overlay.addEventListener('click', todayTaskOverlayClick);
    overlay.addEventListener('keydown', todayTaskOverlayKey);
    document.body.appendChild(overlay);
  }
  overlay.style.display = 'flex';
  renderTodayTaskOverlay();
  todayTaskStopTimer();
  todayTaskTimerHandle = setInterval(todayTaskTick, 1000);
}

function closeTodayTaskOverlay() {
  todayTaskStopTimer();
  todayTaskCloseResultCard();
  const overlay = document.getElementById('today-task-overlay');
  if (overlay) { overlay.style.display = 'none'; overlay.innerHTML = ''; }
  renderTodayTaskCard();
}

function todayTaskOverlayKey(event) {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  const zoom = event.target && event.target.closest ? event.target.closest('[data-today-zoom]') : null;
  if (zoom) { event.preventDefault(); todayTaskZoomImage(zoom); }
}

function todayTaskOverlayClick(event) {
  const zoom = event.target && event.target.closest ? event.target.closest('[data-today-zoom]') : null;
  if (zoom) { todayTaskZoomImage(zoom); return; }
  const target = event.target && event.target.closest ? event.target.closest('button') : null;
  if (!target || target.disabled) return;
  if (target.hasAttribute('data-today-result-next')) { todayTaskResultAdvance(true); return; }
  if (target.hasAttribute('data-today-result-goto')) { todayTaskResultGoto(Number(target.getAttribute('data-today-result-goto'))); return; }
  const check = target.getAttribute('data-today-check');
  if (check) { todayTaskOpenSolution(check); return; }
  const act = target.getAttribute('data-today-act');
  if (act === 'next') {
    const cur = todayTaskState || todayTaskRefresh();
    if (cur.active) {
      const cvm = todayTaskViewModel(cur, Date.now());
      if (cvm.active.isReview && cvm.active.resultQids.length) {
        const prog = todayTaskReviewProgress(cvm.active.resultQids, todayTaskResultFlowFor(cvm), cvm.active.phaseStartedAt);
        if (!prog.canFinish) return;
      }
    }
    todayTaskCommit(todayTaskAdvance(todayTaskState || todayTaskRefresh(), Date.now()));
    if (!todayTaskState.active) { closeTodayTaskOverlay(); return; }
    renderTodayTaskOverlay();
    todayTaskStopTimer();
    todayTaskTimerHandle = setInterval(todayTaskTick, 1000);
  } else if (act === 'leave') {
    closeTodayTaskOverlay();
  } else if (act === 'abandon') {
    todayTaskCommit(todayTaskAbandon(todayTaskState || todayTaskRefresh()));
    closeTodayTaskOverlay();
  }
}

function todayTaskOpenSolution(qid) {
  const r = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  if (!r || typeof openSolutionModal !== 'function') {
    if (typeof showToast === 'function') showToast('找不到 ' + qid + ' 的題解');
    return;
  }
  openSolutionModal(null, r[6], qid, r[3], { mode: 'browse' });
  const state = todayTaskState || todayTaskRefresh();
  if (!state.active) return;
  const vm = todayTaskViewModel(state, Date.now());
  if (!vm.active.isReview) return;
  // Dock the result card inside the solution modal so the learner can mark while reading.
  if (typeof openResultCard === 'function') {
    openResultCard({
      qid, source: vm.active.resultSource, mockId: vm.active.resultMockId || undefined,
      onSaved: () => {
        const flow = todayTaskResultFlowFor(vm);
        if (flow.saved.indexOf(qid) < 0) flow.saved.push(qid);
        todayTaskAfterSolution();
      }
    });
  }
  const modal = document.getElementById('solution-modal');
  if (modal && typeof MutationObserver !== 'undefined') {
    const obs = new MutationObserver(() => {
      if (modal.classList.contains('show')) return;
      obs.disconnect();
      todayTaskAfterSolution();
    });
    obs.observe(modal, { attributes: true, attributeFilter: ['class'] });
  }
}

// Tap-to-zoom for the question image: reuse the solution modal's lightbox, else a simple pinch-zoomable overlay.
function todayTaskZoomImage(img) {
  if (typeof openImageLightbox === 'function') { openImageLightbox(img.src, img.alt, img); return; }
  const box = document.createElement('div');
  box.className = 'today-task-zoom-fallback';
  box.innerHTML = '<button type="button" aria-label="關閉">✕ 關閉</button><div><img src="' + todayTaskEscape(img.src) + '" alt="' + todayTaskEscape(img.alt) + '"></div>';
  box.querySelector('button').addEventListener('click', () => box.remove());
  document.body.appendChild(box);
}

function initTodayTask() {
  todayTaskRefresh();
  renderTodayTaskCard();
  if (!todayTaskAutoResumed) {
    todayTaskAutoResumed = true;
    if (todayTaskState.active) openTodayTaskOverlay();
  }
}
