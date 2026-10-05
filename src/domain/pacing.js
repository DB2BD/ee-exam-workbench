// src/domain/pacing.js
// v1.3 動態配速: pure functions (no DOM, no storage) that turn the dated schedule
// (DAILY_SCHEDULE), the completed map and today's local date into today's plan,
// the next milestone, an hours-vs-budget check and, when behind, an automatic cut list.
//
//   pacingPlan({ schedule, completed, today:'YYYY-MM-DD', budget?, partial?, spentToday? })
//
// `spentToday` = hours of tasks already completed today (they use up today's budget,
// so finishing a task does not pull a fresh 2 h of work into the same day).
//
// `partial` = { code, phaseIndex } of a started task (a weekday mock whose closed
// phase is already done counts only its remaining 核對＋修復 hours).

const PACING_DAY_TOLERANCE = 0.25;   // a later task may overshoot today's remaining hours by this much
const PACING_MIN_ROOM = 0.25;        // stop adding tasks once this little (or less) of the budget is left (room ~0)
const PACING_FEASIBILITY_SLACK = 0.5; // hours of rounding allowed before a milestone counts as unreachable
const PACING_NON_WORK = ['EXAM-CHECK', 'STOP'];

function pacingParseIso(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
  return m ? { y: Number(m[1]), m: Number(m[2]), d: Number(m[3]) } : null;
}

function pacingDayNumber(iso) {
  const p = pacingParseIso(iso);
  return p ? Math.round(Date.UTC(p.y, p.m - 1, p.d) / 86400000) : NaN;
}

function pacingDaysBetween(fromIso, toIso) {
  return pacingDayNumber(toIso) - pacingDayNumber(fromIso);
}

function pacingAddDays(iso, n) {
  const p = pacingParseIso(iso);
  const t = new Date(Date.UTC(p.y, p.m - 1, p.d + n));
  const pad = v => String(v).padStart(2, '0');
  return t.getUTCFullYear() + '-' + pad(t.getUTCMonth() + 1) + '-' + pad(t.getUTCDate());
}

function pacingIsWeekend(iso) {
  const p = pacingParseIso(iso);
  const dow = new Date(Date.UTC(p.y, p.m - 1, p.d)).getUTCDay();
  return dow === 0 || dow === 6;
}

function pacingBudgetFor(iso, budget) {
  return pacingIsWeekend(iso) ? Number(budget.weekend) : Number(budget.weekday);
}

function pacingIsPaper(task) {
  return !!task && (task.kind === 'mock114' || task.kind === 'blind108');
}

function pacingGroup(code) {
  return String(code).replace(/-\d+$/, '');
}

function pacingMinutesFrom(task, phaseIndex) {
  return task.phases.slice(Math.max(0, phaseIndex || 0)).reduce((n, p) => n + p.minutes, 0);
}

// Hours a task still needs (full task, or the remaining phases of a started one).
function pacingRemainingHours(task, partial) {
  const idx = partial && partial.code === task.code ? partial.phaseIndex : 0;
  return pacingMinutesFrom(task, idx) / 60;
}

// What the task costs on a given day.  A weekday paper is split: closed phase on day 1,
// 核對＋修復 on day 2; on a weekend it is done in one sitting.
function pacingCost(task, partial, weekend) {
  const started = partial && partial.code === task.code ? partial.phaseIndex : 0;
  if (pacingIsPaper(task)) {
    if (started > 0) return { hours: pacingMinutesFrom(task, started) / 60, part: 'review', phaseIndex: started };
    if (weekend) return { hours: pacingMinutesFrom(task, 0) / 60, part: 'full', phaseIndex: 0 };
    return { hours: task.phases[0].minutes / 60, part: 'closed', phaseIndex: 0 };
  }
  return { hours: pacingMinutesFrom(task, started) / 60, part: started > 0 ? 'rest' : 'full', phaseIndex: started };
}

function pacingAvailableHours(fromIso, toIso, budget, firstIso) {
  let total = 0;
  const start = pacingDayNumber(fromIso) < pacingDayNumber(firstIso) ? firstIso : fromIso;
  for (let iso = start; pacingDaysBetween(iso, toIso) >= 0; iso = pacingAddDays(iso, 1)) total += pacingBudgetFor(iso, budget);
  return total;
}

// Cut candidates for one milestone, in the order they are dropped.
//   1. WEAK quota (earliest first)  2. CORE: 同型＋變式 then 母題, latest first, keeping each
//   subject's 母題 session  3. REINF (latest first).  Papers, BUFFER and WRAP are never cut.
function pacingCutCandidates(codes, schedule, completed, partial, alreadyCut) {
  const tasks = schedule.tasks;
  const order = schedule.order;
  const idx = c => order.indexOf(c);
  const live = codes.filter(c => !completed[c] && !alreadyCut.has(c) && !(partial && partial.code === c));
  const weak = live.filter(c => pacingGroup(c) === 'WEAK').sort((a, b) => idx(a) - idx(b))
    .map(c => ({ code: c, reason: 'weak' }));
  const core = live.filter(c => tasks[c].kind === 'core');
  const subjectsWithDoneBase = {};
  Object.keys(tasks).forEach(c => {
    const t = tasks[c];
    if (t.kind === 'core' && !t.variant && completed[c]) subjectsWithDoneBase[t.subject] = true;
  });
  const protectedCodes = {};
  const seenSubject = {};
  order.forEach(c => {
    const t = tasks[c];
    if (!t || t.kind !== 'core' || t.variant || completed[c]) return;
    if (subjectsWithDoneBase[t.subject] || seenSubject[t.subject]) return;
    seenSubject[t.subject] = true;
    protectedCodes[c] = true;
  });
  const byLatest = (a, b) => idx(b) - idx(a);
  const variants = core.filter(c => tasks[c].variant).sort(byLatest).map(c => ({ code: c, reason: 'core-variant' }));
  const bases = core.filter(c => !tasks[c].variant && !protectedCodes[c]).sort(byLatest).map(c => ({ code: c, reason: 'core' }));
  const reinf = live.filter(c => pacingGroup(c) === 'REINF').sort(byLatest).map(c => ({ code: c, reason: 'reinforce' }));
  return weak.concat(variants, bases, reinf);
}

function pacingPlan(input) {
  const schedule = input.schedule;
  const tasks = schedule.tasks;
  const order = schedule.order;
  const days = schedule.days;
  const completed = input.completed || {};
  const today = input.today;
  const budget = Object.assign({ weekday: 2, weekend: 4 }, schedule.budget || {}, input.budget || {});
  const partial = input.partial && tasks[input.partial.code] ? input.partial : null;
  const first = days[0].date;
  const last = days[days.length - 1].date;
  const row = days.find(d => d.date === today) || null;
  const weekend = pacingIsWeekend(today);
  const dayBudget = pacingBudgetFor(today, budget);
  const spent = Math.max(0, Number(input.spentToday) || 0);
  const roomToday = Math.max(0, dayBudget - spent);
  const milestones = (schedule.milestones || []).slice();
  const uncompleted = order.filter(c => !completed[c]);
  const remainingOf = c => pacingRemainingHours(tasks[c], partial);

  // --- cuts: hours are enforced at the hard (不可延後) milestone and at the milestones after it; earlier milestones
  // are soft (reported with their hours, never a reason to cut by themselves).  Cumulative, so later milestones see earlier cuts.
  const cutSet = new Set();
  const cutDetail = [];
  let overload = false;
  let shortHours = 0;
  const hardRaw0 = milestones.find(m => m.hard) || null;
  const upcoming = milestones.filter(m => pacingDaysBetween(today, m.date) >= 0);
  const binding = upcoming.filter(m => !hardRaw0 || m.hard || pacingDaysBetween(hardRaw0.date, m.date) > 0);
  const hoursFor = (m, skipCut) => uncompleted.filter(c => m.codes.indexOf(c) >= 0 && !(skipCut && cutSet.has(c))).reduce((n, c) => n + remainingOf(c), 0);
  binding.forEach(m => {
    const available = pacingAvailableHours(today, m.date, budget, first) - spent;
    let required = hoursFor(m, true);
    const candidates = pacingCutCandidates(m.codes, schedule, completed, partial, cutSet);
    let k = 0;
    while (required > available + PACING_FEASIBILITY_SLACK && k < candidates.length) {
      const c = candidates[k++];
      cutSet.add(c.code);
      const hours = remainingOf(c.code);
      required -= hours;
      cutDetail.push({ code: c.code, title: tasks[c.code].title, hours, reason: c.reason, milestone: m.date });
    }
    if (required > available + PACING_FEASIBILITY_SLACK) {
      overload = true;
      shortHours = Math.max(shortHours, required - available);
    }
  });
  const perMilestone = {};
  upcoming.forEach(m => {
    perMilestone[m.date] = { required: hoursFor(m, true), available: pacingAvailableHours(today, m.date, budget, first) - spent };
  });
  const cut = order.filter(c => cutSet.has(c));

  // --- today's plan: earliest uncompleted mandatory task first, filling today's hours -------
  const nonWorkToday = !!row && row.codes.some(c => PACING_NON_WORK.indexOf(c) >= 0);
  const plan = [];
  let used = 0;
  if (!nonWorkToday && pacingDaysBetween(last, today) <= 0) {
    const effective = uncompleted.filter(c => !cutSet.has(c));
    for (let i = 0; i < effective.length; i++) {
      const task = tasks[effective[i]];
      if (task.notBefore && pacingDaysBetween(task.notBefore, today) < 0) break;
      const cost = pacingCost(task, partial, weekend);
      const inFlight = !!partial && partial.code === task.code;
      // A task in flight is always shown; otherwise stop once today's budget (after what is already done) is used up.
      if (plan.length || (spent > 0 && !inFlight)) {
        const room = roomToday - used;
        if (!(room > PACING_MIN_ROOM - 1e-9 && cost.hours <= room + PACING_DAY_TOLERANCE + 1e-9)) break;
      }
      plan.push({ code: task.code, part: cost.part, hours: cost.hours, phaseIndex: cost.phaseIndex, partial: inFlight });
      used += cost.hours;
    }
  }

  // --- milestone info -----------------------------------------------------------------------
  const papers = order.filter(c => pacingIsPaper(tasks[c]));
  const milestoneInfo = m => {
    const scope = order.filter(c => m.codes.indexOf(c) >= 0 && !completed[c]);
    const remaining = scope.filter(c => !cutSet.has(c));
    const info = {
      date: m.date, label: m.label, hard: !!m.hard,
      daysLeft: pacingDaysBetween(today, m.date),
      remainingTasks: remaining.length,
      remainingHours: remaining.reduce((n, c) => n + remainingOf(c), 0),
      remainingPapers: scope.filter(c => pacingIsPaper(tasks[c])).length,
      codes: m.codes.slice(),
    };
    const stat = perMilestone[m.date];
    if (stat) { info.requiredHours = stat.required; info.availableHours = stat.available; info.atRisk = stat.required > stat.available + PACING_FEASIBILITY_SLACK; }
    return info;
  };
  const next = upcoming.length ? milestoneInfo(upcoming[0]) : null;
  const hardRaw = milestones.find(m => m.hard) || null;
  const hard = hardRaw ? milestoneInfo(hardRaw) : null;
  if (hard) {
    hard.passed = hard.daysLeft < 0;
    hard.missed = hard.passed && hard.remainingPapers > 0;
  }

  // --- status ---------------------------------------------------------------------------------
  const due = schedule.due || {};
  const behindCodes = order.filter(c => !completed[c] && due[c] && due[c] < today);
  const aheadCodes = order.filter(c => completed[c] && due[c] && due[c] > today);
  const allPapersDone = papers.length > 0 && papers.every(c => completed[c]);
  let status = 'on';
  if (cut.length || overload) status = 'behind';
  else if (!behindCodes.length && aheadCodes.length) status = 'ahead';
  const suggestion = allPapersDone && hard && !hard.passed
    ? '12 份模考卷已全部完成，可加做 113 年整卷（選做，不影響日程）。' : '';

  return {
    today, weekend, budgetHours: dayBudget, spentHours: spent, planHours: used,
    plan, nonWork: nonWorkToday, beforeStart: pacingDaysBetween(first, today) < 0, afterEnd: pacingDaysBetween(last, today) > 0,
    nextMilestone: next, hardMilestone: hard,
    daysLeft: next ? next.daysLeft : null,
    requiredHours: next && next.requiredHours != null ? next.requiredHours : 0,
    availableHours: next && next.availableHours != null ? next.availableHours : 0,
    remainingHours: uncompleted.filter(c => !cutSet.has(c)).reduce((n, c) => n + remainingOf(c), 0),
    status, behindCount: behindCodes.length, aheadCount: aheadCodes.length,
    behindCodes, cut, cutDetail, overload, shortHours,
    suggestion, allDone: uncompleted.length === 0, allPapersDone,
  };
}
