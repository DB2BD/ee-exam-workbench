// src/components/todayTask.js
// K3 「一鍵開始今天」 (v1.3 動態配速): today's plan from the 41-day schedule via
// src/domain/pacing.js (hours budget, milestones, auto cuts), focused closed-book
// overlay with a phase countdown.  The store and view-model functions are
// pure (no DOM) so they can be tested in a node vm; DOM code is at the bottom.
// Data: DAILY_SCHEDULE (src/data/dailySchedule.generated.js).

const TODAY_TASK_STORAGE_KEY = 'EE_EXAM_TODAY_TASK_V1';
const TODAY_TASK_NEXT_ACTION_TEXT = '寫下一句：下次最先要改的動作（不必回填）。寫完就可以按「完成」。';
const TODAY_TASK_HOLD_TEXT = '先離開，明天核對';
const TODAY_TASK_PART_TEXT = { closed: '閉卷 120 分鐘', review: '核對＋修復', rest: '接續' };

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
    if (typeof a.holdDate === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(a.holdDate)) state.active.holdDate = a.holdDate;
    if (typeof a.heldFrom === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(a.heldFrom)) state.active.heldFrom = a.heldFrom;
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

// Start `code` (an uncompleted scheduled task, normally today's first planned one),
// or the earliest uncompleted task when no code is given.
function todayTaskStart(state, now, code) {
  if (state.active) return state;
  const tasks = DAILY_SCHEDULE.tasks;
  let target = todayTaskCurrentCode(state);
  if (code) {
    if (!tasks[code] || state.completed[code]) return state;
    target = code;
  }
  if (!target) return state;
  const active = { code: target, phaseIndex: 0, phaseStartedAt: now };
  if (todayTaskIsMockKind(tasks[target])) active.mockId = todayTaskMockId(tasks[target], now);
  return { completed: state.completed, active };
}

// 平日模考「先離開，明天核對」: keep the active state (phase index and mock id) and mark the day.
function todayTaskHold(state, todayIso) {
  if (!state.active) return state;
  return { completed: state.completed, active: Object.assign({}, state.active, { holdDate: todayIso }) };
}

// Pressing 開始/繼續 on a held task: drop the hold and restart the phase clock.  `heldFrom`
// remembers the split was used, so the 核對 day does not offer 「先離開，明天核對」 again.
function todayTaskResumeHeld(state, now) {
  const a = state.active;
  if (!a || !a.holdDate) return state;
  const active = Object.assign({}, a, { phaseStartedAt: now, heldFrom: a.holdDate });
  delete active.holdDate;
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
  // Done on paper before today: stamp the end of yesterday (local) so they do not count as today's hours.
  const d = new Date(now);
  const stamp = new Date(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() - 1).toISOString();
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

// Hours of tasks completed on `todayIso` (local date).  A weekday paper is split over two days, so
// finishing it on a weekday counts only its 核對＋修復 phases (the closed phase was the day before).
function todayTaskSpentToday(state, todayIso) {
  const tasks = DAILY_SCHEDULE.tasks;
  const weekend = pacingIsWeekend(todayIso);
  return Object.keys(state.completed).reduce((n, code) => {
    const t = tasks[code];
    if (!t || todayTaskLocalDate(Date.parse(state.completed[code])) !== todayIso) return n;
    return n + pacingMinutesFrom(t, pacingIsPaper(t) && !weekend ? 1 : 0) / 60;
  }, 0);
}

// Today's pacing result (pure): plan, milestones, cuts.  `partial` lets a started weekday mock count its remaining hours only.
function todayTaskPacing(state, todayIso) {
  const a = state.active;
  return pacingPlan({
    schedule: DAILY_SCHEDULE, completed: state.completed, today: todayIso,
    partial: a ? { code: a.code, phaseIndex: a.phaseIndex } : null,
    spentToday: todayTaskSpentToday(state, todayIso),
  });
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

// 'WEAK-03','WEAK-04','WEAK-06' -> 'WEAK-03～04、WEAK-06' (runs of consecutive numbers per prefix, original order).
function todayTaskCompressCodes(codes) {
  const out = [];
  let run = [];
  const flush = () => { if (run.length) out.push(todayTaskCodeRange(run)); run = []; };
  codes.forEach(c => {
    const m = /^(.*?)(\d+)$/.exec(c);
    const prev = run.length ? /^(.*?)(\d+)$/.exec(run[run.length - 1]) : null;
    if (m && prev && m[1] === prev[1] && Number(m[2]) === Number(prev[2]) + 1) run.push(c);
    else { flush(); run = [c]; }
  });
  flush();
  return out.join('、');
}

function todayTaskMonthDay(iso) {
  const m = /^\d{4}-(\d{2})-(\d{2})$/.exec(String(iso));
  return m ? Number(m[1]) + '/' + Number(m[2]) : String(iso);
}

function todayTaskFormatHours(h) {
  return String(Math.round(h * 4) / 4);
}

function todayTaskPartText(item) {
  return TODAY_TASK_PART_TEXT[item.part] || '';
}

function todayTaskPlanItem(item) {
  const t = DAILY_SCHEDULE.tasks[item.code];
  return {
    code: item.code, title: t.title, part: item.part, partText: todayTaskPartText(item),
    hours: item.hours, minutes: Math.round(item.hours * 60), launch: t.launch || '',
  };
}

// 「距 10/31 模考截止還有 N 天｜剩 X 份卷」 (hard milestone) or the next milestone's hours; a missed hard milestone says so.
function todayTaskMilestoneText(pacing) {
  const hard = pacing.hardMilestone;
  const next = pacing.nextMilestone;
  const hardLine = h => '距 ' + todayTaskMonthDay(h.date) + ' ' + h.label + (h.daysLeft === 0 ? '就是今天' : '還有 ' + h.daysLeft + ' 天') + '｜剩 ' + h.remainingPapers + ' 份卷';
  if (hard && hard.missed) {
    return '已過 ' + todayTaskMonthDay(hard.date) + ' ' + hard.label + '｜仍剩 ' + hard.remainingPapers + ' 份卷，優先補完（不可刪減）';
  }
  if (!next) return '';
  if (next.hard) return hardLine(next);
  const head = '距 ' + todayTaskMonthDay(next.date) + ' ' + next.label + (next.daysLeft === 0 ? '就是今天' : '還有 ' + next.daysLeft + ' 天') +
    '｜剩 ' + todayTaskFormatHours(next.remainingHours) + ' 小時';
  const tail = hard && !hard.passed ? head + '｜' + todayTaskMonthDay(hard.date) + ' ' + hard.label + '剩 ' + hard.remainingPapers + ' 份卷' : head;
  return next.atRisk ? tail + '｜彈性關卡：做不完就順延，不影響模考' : tail;
}

// One-line schedule position: 「落後約 N 小時（M 項未按日程完成）」／「照日程」／「超前約 N 小時」.
// Behind = tasks due before today and not done (pacing.behindHours); ahead = done tasks that were due after today.
function todayTaskPaceLine(pacing) {
  if (!pacing) return '';
  if (pacing.behindCount > 0) {
    return '落後約 ' + todayTaskFormatHours(pacing.behindHours || 0) + ' 小時（' + pacing.behindCount + ' 項未按日程完成）';
  }
  if (pacing.aheadCount > 0 && pacing.aheadHours > 0) return '超前約 ' + todayTaskFormatHours(pacing.aheadHours) + ' 小時';
  return '照日程';
}

// SM-2 due questions today; 0 when the store is not loaded.
function todayTaskDueCount(now) {
  if (typeof getDueQuestionsList !== 'function') return 0;
  try { return getDueQuestionsList(now).length; } catch (e) { return 0; }
}

// The single status line: 已完成 N／總數｜milestone｜pace｜到期複習 N 題 (empty parts are skipped).
function todayTaskStatusLine(vm) {
  const parts = [];
  if (vm.total) parts.push('已完成 ' + vm.doneCount + '／' + vm.total);
  if (vm.milestoneText) parts.push(vm.milestoneText);
  if (vm.paceText) parts.push(vm.paceText);
  if (vm.dueCount > 0) parts.push('到期複習 ' + vm.dueCount + ' 題');
  return parts.join('｜');
}

function todayTaskCutNote(pacing) {
  return pacing.overload
    ? '時數仍短缺約 ' + todayTaskFormatHours(pacing.shortHours) + ' 小時：模考卷照順序做，做不完的排到 11/01 緩衝日補考' : '';
}

function todayTaskCutText(pacing) {
  if (!pacing.cut.length) return '';
  const note = todayTaskCutNote(pacing);
  return '已自動刪減：' + todayTaskCompressCodes(pacing.cut) + '（有空再做）' + (note ? '；' + note : '');
}

// Card html for the cut line: few ranges stay inline; a long list collapses into a <details> under a short summary.
function todayTaskCutHtml(vm) {
  const pacing = vm.pacing;
  if (vm.freshStart) return '';
  if (!pacing || !pacing.cut || !pacing.cut.length) return vm.cutText ? '<p class="today-pacing-cut">' + todayTaskEscape(vm.cutText) + '</p>' : '';
  const ranges = todayTaskCompressCodes(pacing.cut);
  if (ranges.split('、').length <= 3) return '<p class="today-pacing-cut">' + todayTaskEscape(vm.cutText) + '</p>';
  const note = todayTaskCutNote(pacing);
  return '<div class="today-pacing-cut"><details><summary>已自動刪減 ' + pacing.cut.length + ' 項（有空再做）</summary><p>' + todayTaskEscape(ranges) + '</p></details>' +
    (note ? '<p>' + todayTaskEscape(note) + '</p>' : '') + '</div>';
}

function todayTaskPlanLine(pacing, hasDoneToday) {
  const spent = pacing.spentHours ? '已做約 ' + todayTaskFormatHours(pacing.spentHours) + ' 小時｜' : '';
  const head = '今天預算 ' + pacing.budgetHours + ' 小時（' + (pacing.weekend ? '週末' : '平日') + '）｜' + spent;
  if (!pacing.planHours && hasDoneToday) return '今天的份量已完成';
  return head + '還要做約 ' + todayTaskFormatHours(pacing.planHours) + ' 小時';
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
    // Optional captions for questionQids (三題對照: 母題／同型／變式).
    questionLabels: Array.isArray(phase.qidLabels) ? phase.qidLabels.slice() : [],
    // Solution entry points. Empty (and never rendered) while a closed-book phase runs.
    solutionQids: closed ? [] : task.qids.slice(),
    isReview,
    // 作答結果卡: one card per QID, recorded right after checking.
    resultQids: isReview ? todayTaskScoredQids(task) : [],
    resultSource: todayTaskIsMockKind(task) ? 'mock' : 'today',
    // Generated once per task run and stored with the active task, so a reload keeps it.
    resultMockId: todayTaskIsMockKind(task) ? (a.mockId || todayTaskMockId(task, a.phaseStartedAt)) : '',
    skipped: Array.isArray(a.skipped) ? a.skipped.slice() : [],
    phaseStartedAt: a.phaseStartedAt,
    pdfUrl: closed ? todayTaskPdfUrl(task) : '',
    scoringNote: task.scoringNote || '',
    // One-line instruction for phases that otherwise show nothing (docs/01_備考計畫/預設24時段_核心題路徑.md: 5 分鐘只留一句下次動作).
    instruction: phase.note || (phase.label === '下次動作' ? TODAY_TASK_NEXT_ACTION_TEXT : ''),
    // 隨機練習 launcher for WEAK／REINF／BUFFER phases ('random-balanced' | 'random-reinforce').
    launch: phase.launch || '',
    // Weekday mock: after the closed phase the learner may stop and continue the next day.
    canHold: todayTaskIsMockKind(task) && a.phaseIndex === 1 && !a.holdDate && !a.heldFrom && !pacingIsWeekend(todayTaskLocalDate(now)),
    holdDate: a.holdDate || '',
  };
}

function todayTaskViewModel(state, now, options) {
  const todayIso = todayTaskLocalDate(now);
  const pacing = todayTaskPacing(state, todayIso);
  const tasks = DAILY_SCHEDULE.tasks;
  const activeTask = state.active ? tasks[state.active.code] : null;
  const view = activeTask ? todayTaskPhaseView(activeTask, state.active, now) : null;
  const row = DAILY_SCHEDULE.days.find(d => d.date === todayIso) || null;
  const rowCodes = row ? row.codes : [];
  const items = pacing.plan.map(todayTaskPlanItem);
  const total = DAILY_SCHEDULE.order.length;
  const doneCount = DAILY_SCHEDULE.order.filter(c => state.completed[c]).length;
  const doneToday = DAILY_SCHEDULE.order.some(c => state.completed[c] && todayTaskLocalDate(Date.parse(state.completed[c])) === todayIso);
  // Nothing completed and no start point set: the cut list would only reflect CORE-01～06 (done on paper) not being marked yet.
  const freshStart = doneCount === 0 && !state.active;
  let mode;
  if (rowCodes.indexOf('EXAM-CHECK') >= 0) mode = 'exam-check';
  else if (rowCodes.indexOf('STOP') >= 0 || pacing.afterEnd) mode = 'stop';
  else if (pacing.allDone && !view) mode = 'done';
  else if (!items.length && !view && pacing.spentHours > 0) mode = 'day-done';
  else if (!items.length && !view) mode = 'idle';
  else mode = 'task';
  // Today's budget is used up: the next task stays available as optional extra work.
  const extraCode = mode === 'day-done' ? (DAILY_SCHEDULE.order.find(c => !state.completed[c] && pacing.cut.indexOf(c) < 0 &&
    !(tasks[c].notBefore && tasks[c].notBefore > todayIso)) || null) : null;
  // The card's primary task: the one in flight, else today's first planned task (or the optional extra one).
  const primary = view
    ? todayTaskPlanItem({ code: state.active.code, part: state.active.phaseIndex > 0 && todayTaskIsMockKind(activeTask) ? 'review' : 'full', hours: pacingRemainingHours(activeTask, { code: state.active.code, phaseIndex: state.active.phaseIndex }) })
    : (items[0] || (extraCode ? todayTaskPlanItem(Object.assign({ code: extraCode }, pacingCost(tasks[extraCode], null, pacing.weekend))) : null));
  const rest = view ? items.filter(i => i.code !== state.active.code) : items.slice(1);
  const held = state.active && state.active.holdDate ? {
    date: state.active.holdDate, sameDay: state.active.holdDate >= todayIso,
    // 「接續 MOCK114-0N：核對＋修復」 shows from the next day; the same day offers 現在就核對.
    text: (state.active.holdDate >= todayIso ? '今天的閉卷已完成，明天接續 ' : '接續 ') + state.active.code + '：核對＋修復',
  } : null;
  const restText = rest.length
    ? '今天還有：' + rest.map(i => i.code + (i.partText ? '（' + i.partText + '）' : '') + '｜' + i.title).join('；') : '';
  return {
    mode,
    todayIso,
    pacing,
    planText: todayTaskPlanLine(pacing, doneToday),
    plan: pacing,
    items,
    rest,
    restText,
    milestoneText: todayTaskMilestoneText(pacing),
    paceText: freshStart ? '' : todayTaskPaceLine(pacing),
    dueCount: options && Number.isInteger(options.dueCount) ? options.dueCount : todayTaskDueCount(now),
    freshStart,
    cutText: freshStart ? '' : todayTaskCutText(pacing),
    suggestion: pacing.suggestion,
    status: pacing.status,
    held,
    completedMap: state.completed,
    // `code` is the card's current task (the one in flight, else today's first planned task).
    code: primary ? primary.code : null,
    part: primary ? primary.part : '',
    launch: primary ? primary.launch : '',
    title: primary ? primary.title : '',
    totalMinutes: primary ? primary.minutes : 0,
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
let todayTaskRenderedDate = null;
let todayTaskDayWatchInstalled = false;

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

// Pure: the card's inner HTML for a view model (tested without a DOM).
function todayTaskCardHtml(vm) {
  const esc = todayTaskEscape;
  // 11/12 考前確認、11/13 起停止: no study hours, so no budget / milestone / cut lines (they would read 「今天預算 2 小時」 or 「仍剩 N 份卷」).
  const restDay = vm.mode === 'exam-check' || vm.mode === 'stop';
  const plan = restDay ? '' : '<p class="today-task-plan">' + esc(vm.planText) + '</p>';
  const pacingLines = restDay ? '' :
    (todayTaskStatusLine(vm) ? '<p class="today-pacing-milestone' + (vm.pacing && vm.pacing.hardMilestone && vm.pacing.hardMilestone.missed ? ' is-missed' : '') + '">' + esc(todayTaskStatusLine(vm)) + '</p>' : '') +
    todayTaskCutHtml(vm) +
    (vm.suggestion ? '<p class="today-pacing-suggestion">' + esc(vm.suggestion) + '</p>' : '');
  let body;
  if (vm.mode === 'exam-check') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">考前最後確認</span><strong>今天不開新題</strong><p class="today-task-note">只做考務與用品確認：准考證、證件、文具與計算機、交通與時間。</p></div>';
  } else if (vm.mode === 'stop') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">停止新增練習</span><strong>好好休息</strong><p class="today-task-note">只整理睡眠、交通與已備妥的用品；不再開新題。</p></div>';
  } else if (vm.mode === 'done') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">全部完成</span><strong>日程的 ' + vm.total + ' 個任務都完成了</strong><p class="today-task-note">可改用下方「隨機練習 3 題」或到期複習，維持手感即可。</p></div>';
  } else if (vm.mode === 'day-done') {
    const extra = vm.code
      ? '<div class="today-task-actions"><button type="button" class="today-task-start" id="today-task-start" onclick="todayTaskOnStart()">' + uiIcon('play') + ' 選做下一個：' + esc(vm.code) + '</button></div>' : '';
    body = '<div class="today-task-main"><span class="today-task-eyebrow">今天</span><strong>今天的份量已完成，可以收工</strong>' +
      '<p class="today-task-note">還有餘力可選做下一個（' + esc(vm.code ? vm.code + '｜' + vm.title + ' · ' + vm.totalMinutes + ' 分鐘' : '') + '），會讓之後的日程變鬆。</p></div>' + extra;
  } else if (vm.mode === 'idle') {
    body = '<div class="today-task-main"><span class="today-task-eyebrow">今天</span><strong>今天沒有待做的必做任務</strong><p class="today-task-note">進度已超前日程；下一階段的任務到期才會排入。可用下方「隨機練習 3 題」維持手感。</p></div>';
  } else {
    const resume = vm.primaryAction === 'resume';
    const dayNote = vm.part === 'closed' ? '（今天閉卷，明天核對＋修復）' : '';
    let label;
    if (resume && vm.held) label = vm.held.text;
    else if (resume) label = '進行中：' + vm.active.code + '｜' + vm.activeTitle + '（' + vm.active.label + '）';
    else label = '下一個任務：' + vm.code + '｜' + vm.title + ' · ' + vm.totalMinutes + ' 分鐘' + dayNote;
    const rest = vm.restText ? '<p class="today-pacing-rest">' + esc(vm.restText) + '</p>' : '';
    const buttonText = resume ? (vm.held ? (vm.held.sameDay ? '現在就核對' : '開始核對') : '繼續') : '開始';
    body = '<div class="today-task-main"><span class="today-task-eyebrow">一鍵開始今天</span><strong>' + esc(label) + '</strong>' +
      rest + '</div>' +
      '<div class="today-task-actions"><button type="button" class="today-task-start" id="today-task-start" onclick="todayTaskOnStart()">' + uiIcon('play') + ' ' + buttonText + '</button></div>';
  }
  const dropped = restDay && vm.active ? '<p class="today-task-note">先前未完成的任務（' + esc(vm.active.code) + '）不再繼續，也不會開新題。</p>' : '';
  return '<section class="today-task-card" aria-label="今天的任務">' + body + dropped + plan + pacingLines + todayTaskStartFromHtml(vm, vm.completedMap) + '</section>';
}

function renderTodayTaskCard() {
  const host = document.getElementById('today-task-card');
  if (!host) return;
  const state = todayTaskState || todayTaskRefresh();
  const now = Date.now();
  todayTaskRenderedDate = todayTaskLocalDate(now);
  host.innerHTML = todayTaskCardHtml(todayTaskViewModel(state, now));
  if (typeof updateHeaderSummary === 'function') updateHeaderSummary();
}

// A page left open past midnight still shows yesterday's budget and countdown: re-render once the local date moves on.
// Returns true when it re-rendered.
function todayTaskCheckDayChange(now) {
  if (!todayTaskRenderedDate || todayTaskLocalDate(now) === todayTaskRenderedDate) return false;
  todayTaskRefresh();
  renderTodayTaskCard();
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  return true;
}

function todayTaskWatchDayChange() {
  if (todayTaskDayWatchInstalled || typeof document === 'undefined') return;
  todayTaskDayWatchInstalled = true;
  const check = () => { if (document.visibilityState !== 'hidden') todayTaskCheckDayChange(Date.now()); };
  document.addEventListener('visibilitychange', check);
  window.addEventListener('focus', check);
  window.addEventListener('pageshow', check);
  setInterval(check, 60000);
}

// 「已在紙本做過前面的任務？」 lists the current codes; the default is CORE-07 while CORE-01 is still open (CORE-01～06 were done on paper), else today's task.
function todayTaskStartFromHtml(vm, completed) {
  if (vm.mode !== 'task' || vm.primaryAction === 'resume') return '';
  const open = completed || {};
  const preferred = !open['CORE-01'] && !open['CORE-07'] ? 'CORE-07' : vm.code;
  const options = DAILY_SCHEDULE.order.map(c => {
    const t = DAILY_SCHEDULE.tasks[c];
    return '<option value="' + todayTaskEscape(c) + '"' + (c === preferred ? ' selected' : '') + '>' +
      todayTaskEscape(c + '｜' + t.title) + '</option>';
  }).join('');
  const fresh = !!vm.freshStart;
  const prompt = fresh ? '<p class="today-task-from-prompt" role="note"><strong>先設定已在紙本做過的任務，再排今天。</strong></p>' : '';
  return prompt + '<details class="today-task-from' + (fresh ? ' is-prompt' : '') + '"' + (fresh ? ' open' : '') + '><summary>已在紙本做過前面的任務？</summary>' +
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
  let state = todayTaskRefresh();
  if (!state.active) {
    const vm = todayTaskViewModel(state, Date.now());
    const next = todayTaskStart(state, Date.now(), vm.code);
    if (next === state) return;
    todayTaskCommit(next);
  } else if (state.active.holdDate) {
    todayTaskCommit(todayTaskResumeHeld(state, Date.now()));
  }
  renderTodayTaskCard();
  openTodayTaskOverlay();
}

// 開啟隨機練習 for WEAK／REINF／BUFFER: the random-practice owner exposes dailyPracticeStartWithMode(mode); fall back to a fresh round.
function todayTaskLaunchPractice(launch) {
  const mode = launch === 'random-reinforce' ? 'reinforce' : 'balanced';
  closeTodayTaskOverlay();
  if (typeof switchTab === 'function' && typeof document !== 'undefined' && document.getElementById('tab-pane-practice')) switchTab('practice');
  if (typeof dailyPracticeStartWithMode === 'function') dailyPracticeStartWithMode(mode);
  else if (typeof dailyPracticePrepareNewRound === 'function') dailyPracticePrepareNewRound();
  if (typeof dailyPracticeScrollRoundIntoView === 'function') dailyPracticeScrollRoundIntoView();
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

// Closed-book stop asks for a second tap while more than 5 minutes remain.
const TODAY_TASK_STOP_CONFIRM_MS = 5 * 60000;
function todayTaskStopNeedsConfirm(view) {
  return !!(view && view.closed && !view.expired && view.remainingMs > TODAY_TASK_STOP_CONFIRM_MS);
}

function todayTaskOverlayHtml(vm) {
  const v = vm.active;
  const figures = v.questionQids.map((qid, i) => {
    const src = todayTaskQuestionImage(qid);
    const img = src
      ? '<img src="' + todayTaskEscape(src) + '" alt="' + todayTaskEscape(qid) + ' 官方題目裁切圖" loading="eager" data-today-zoom tabindex="0" role="button" aria-label="點擊放大題目圖">' +
        '<p class="today-task-zoom-hint">點圖可放大</p>'
      : '<p class="today-task-note">本題沒有裁切圖。</p>';
    return '<figure class="today-task-figure"><figcaption>' + (v.questionLabels[i] ? '<span class="today-task-figlabel">' + todayTaskEscape(v.questionLabels[i]) + '</span> ' : '') + '<code>' + todayTaskEscape(qid) + '</code></figcaption>' + img + '</figure>';
  }).join('');
  const pdf = v.pdfUrl
    ? '<a class="btn-pdf" href="' + todayTaskEscape(v.pdfUrl) + '" target="_blank" rel="noopener">官方原卷 PDF</a>' : '';
  const note = v.scoringNote ? '<p class="today-task-note">計分範圍：' + todayTaskEscape(v.scoringNote) + '</p>' : '';
  const instruction = v.instruction ? '<p class="today-task-instruction" role="note">' + todayTaskEscape(v.instruction) + '</p>' : '';
  let check = '';
  if (!v.closed && v.solutionQids.length) {
    check = '<div class="today-task-check"><span>核對題解（開啟後可邊讀邊記錄）：</span>' + v.solutionQids.map(qid =>
      '<button type="button" class="btn-pdf" data-today-check="' + todayTaskEscape(qid) + '">核對 ' + todayTaskEscape(qid) + '</button>').join('') + '</div>';
  }
  const launchText = v.launch === 'random-reinforce' ? '開啟補強練習' : '開啟隨機練習（各科輪流）';
  const launch = v.launch ? '<div class="today-task-launch"><button type="button" class="today-task-start" data-today-launch="' + todayTaskEscape(v.launch) + '">' + launchText + '</button></div>' : '';
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
    controls = '<button type="button" class="today-task-start" data-today-act="next">停筆，開始核對</button>';
  } else if (progress) {
    controls = '<button type="button" class="today-task-start" id="today-task-finish" data-today-act="next"' + (progress.canFinish ? '' : ' disabled') + '>' + (v.isLast ? '完成核對並結束' : '完成核對 →') + '</button>' +
      '<span class="today-task-reason" id="today-task-reason" role="status">' + todayTaskEscape(progress.reason) + '</span>';
  } else {
    controls = '<button type="button" class="today-task-start" data-today-act="next">' + (v.isLast ? '完成' : '下一步') + '</button>';
  }
  const foot = '<footer class="today-task-foot">' + controls +
    (v.canHold
      ? '<button type="button" class="btn-pdf" data-today-act="hold" title="閉卷已完成；明天打開時直接接續核對＋修復">' + TODAY_TASK_HOLD_TEXT + '</button>'
      : '<button type="button" class="btn-pdf" data-today-act="leave">先離開</button>') +
    '<button type="button" class="btn-pdf today-task-abandon" data-today-act="abandon">放棄本次</button></footer>';
  return '<div class="today-task-panel' + (progress ? ' today-task-panel--review' : '') + '" role="dialog" aria-modal="true" aria-label="今天的任務">' +
    '<header class="today-task-head"><div><span class="today-task-eyebrow">' + todayTaskEscape(v.code) + '｜' + todayTaskEscape(vm.activeTitle) + '</span>' +
    '<strong>' + (v.phaseIndex + 1) + '／' + v.phaseCount + ' ' + todayTaskEscape(v.label) + (v.closed ? '（閉卷）' : '') + ' · ' + v.minutes + ' 分鐘</strong></div>' +
    '<div class="' + timerClass + '" id="today-task-timer" role="timer">' + timerText + '</div></header>' +
    '<div class="today-task-body">' + instruction + note + launch + figures + pdf + check + resultSlot + foot + '</div></div>';
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
    if (title) title.textContent = '全部記錄完成，按「完成核對」結束';
    if (nextButton) nextButton.hidden = true;
    mount.innerHTML = '';
    const finish = document.getElementById('today-task-finish');
    if (finish && !finish.disabled) {
      if (typeof finish.scrollIntoView === 'function') finish.scrollIntoView({ block: 'center' });
      if (typeof finish.focus === 'function') finish.focus();
    }
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
  const primary = overlay.querySelector('.today-task-start:not([disabled])');
  if (primary && typeof primary.focus === 'function') primary.focus();
}

function closeTodayTaskOverlay() {
  if (todayTaskConfirmState) todayTaskDisarmConfirm();
  todayTaskStopTimer();
  todayTaskCloseResultCard();
  if (typeof document === 'undefined') return;
  const overlay = document.getElementById('today-task-overlay');
  if (overlay) { overlay.style.display = 'none'; overlay.innerHTML = ''; }
  renderTodayTaskCard();
}

// Two-step inline confirm: the button turns into a confirm label plus 取消 and reverts by itself.
let todayTaskConfirmState = null;
function todayTaskDisarmConfirm() {
  const st = todayTaskConfirmState;
  if (!st) return;
  todayTaskConfirmState = null;
  clearTimeout(st.timer);
  if (st.cancel && st.cancel.remove) st.cancel.remove();
  if (st.button) { st.button.textContent = st.label; st.button.removeAttribute('data-confirming'); }
}

function todayTaskArmConfirm(button, text, ms) {
  todayTaskDisarmConfirm();
  const cancel = document.createElement('button');
  cancel.type = 'button';
  cancel.className = 'btn-pdf today-task-confirm-cancel';
  cancel.setAttribute('data-today-act', 'cancel-confirm');
  cancel.textContent = '取消';
  const st = { button, cancel, label: button.textContent, timer: setTimeout(todayTaskDisarmConfirm, ms) };
  button.setAttribute('data-confirming', '1');
  button.textContent = text;
  button.insertAdjacentElement('afterend', cancel);
  todayTaskConfirmState = st;
}

function todayTaskOverlayKey(event) {
  if (event.key === 'Escape') {
    // Same as 先離開: close only, never change task state.
    event.preventDefault();
    event.stopPropagation();
    closeTodayTaskOverlay();
    return;
  }
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
  const launch = target.getAttribute('data-today-launch');
  if (launch) { todayTaskLaunchPractice(launch); return; }
  const act = target.getAttribute('data-today-act');
  if (act === 'cancel-confirm') { todayTaskDisarmConfirm(); return; }
  const confirming = target.getAttribute('data-confirming') === '1';
  if (!confirming) todayTaskDisarmConfirm();
  if (act === 'abandon' && !confirming) {
    todayTaskArmConfirm(target, '確定放棄？會清掉這次進度', 3000);
    return;
  }
  todayTaskDisarmConfirm();
  if (act === 'next') {
    const cur = todayTaskState || todayTaskRefresh();
    if (cur.active) {
      const cvm = todayTaskViewModel(cur, Date.now());
      if (!confirming && todayTaskStopNeedsConfirm(cvm.active)) {
        todayTaskArmConfirm(target, '還有 ' + Math.ceil(cvm.active.remainingMs / 60000) + ' 分鐘，確定停筆並開始核對？', 4000);
        return;
      }
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
  } else if (act === 'hold') {
    todayTaskCommit(todayTaskHold(todayTaskState || todayTaskRefresh(), todayTaskLocalDate(Date.now())));
    closeTodayTaskOverlay();
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
  box.innerHTML = '<button type="button" aria-label="關閉">' + uiIcon('x') + ' 關閉</button><div><img src="' + todayTaskEscape(img.src) + '" alt="' + todayTaskEscape(img.alt) + '"></div>';
  box.querySelector('button').addEventListener('click', () => box.remove());
  document.body.appendChild(box);
}

function initTodayTask() {
  todayTaskRefresh();
  renderTodayTaskCard();
  todayTaskWatchDayChange();
  if (!todayTaskAutoResumed) {
    todayTaskAutoResumed = true;
    // A held weekday mock waits for the learner (next-day card says 接續); do not pop the overlay open.
    // 11/12 考前確認與 11/13 起停止: never reopen a leftover task; the card shows the rest-day message.
    const vm = todayTaskViewModel(todayTaskState, Date.now());
    const restDay = vm.mode === 'exam-check' || vm.mode === 'stop';
    if (todayTaskState.active && !todayTaskState.active.holdDate && !restDay) openTodayTaskOverlay();
  }
}
