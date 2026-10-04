// Daily practice queue and session storage.
// This module is deliberately independent from the SM-2 review schedule:
// opening a question or revealing its solution never records completion.

const DAILY_PRACTICE_STORAGE_KEY = 'EE_EXAM_DAILY_PRACTICE_V1';
const DAILY_PRACTICE_STORE_VERSION = 1;
const DAILY_PRACTICE_RECENT_WINDOW_MS = 7 * 24 * 60 * 60 * 1000;

function practiceIsPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function practiceClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function practiceStorageFrom(options) {
  if (options && typeof options.getItem === 'function') return options;
  if (options && options.storage && typeof options.storage.getItem === 'function') return options.storage;
  if (typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function') return localStorage;
  return null;
}

function practiceResolveNow(value) {
  const candidate = typeof value === 'function' ? value() : value;
  if (candidate instanceof Date) return candidate.getTime();
  if (typeof candidate === 'number' && Number.isFinite(candidate)) return candidate;
  if (typeof candidate === 'string' && candidate.trim() !== '') {
    const parsed = Date.parse(candidate);
    if (Number.isFinite(parsed)) return parsed;
  }
  return Date.now();
}

function practiceTimestamp(value) {
  if (value instanceof Date) return value.getTime();
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Date.parse(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function practiceCreatedAt(now) {
  const timestamp = practiceResolveNow(now);
  return new Date(timestamp).toISOString();
}

function practiceQuestionId(question) {
  if (question && typeof question === 'object' && !Array.isArray(question)) {
    return String(question.id || question.qid || '').trim();
  }
  return String(Array.isArray(question) ? question[0] : '').trim();
}

function practiceSubjectId(question) {
  if (question && typeof question === 'object' && !Array.isArray(question)) {
    return question.subjectId === undefined || question.subjectId === null ? '' : String(question.subjectId);
  }
  return Array.isArray(question) && question[1] !== undefined ? String(question[1]) : '';
}

function practiceFacet(fn, question) {
  if (typeof fn !== 'function') return 'unknown';
  try {
    const value = fn(question);
    return value === undefined || value === null || String(value).trim() === '' ? 'unknown' : String(value);
  } catch (error) {
    return 'unknown';
  }
}

function practiceRandomValue(random) {
  let value;
  try {
    value = Number(random());
  } catch (error) {
    value = Math.random();
  }
  if (!Number.isFinite(value)) value = Math.random();
  return Math.min(0.9999999999999999, Math.max(0, value));
}

function practiceCompletionTimestamp(completionByQuestion, qid) {
  const value = completionByQuestion && completionByQuestion[qid];
  if (practiceIsPlainObject(value) && value.completedAt !== undefined) return practiceTimestamp(value.completedAt);
  return practiceTimestamp(value);
}

function practiceValidCompletion(value) {
  if (practiceTimestamp(value) !== null && !practiceIsPlainObject(value)) return true;
  return practiceIsPlainObject(value) && practiceTimestamp(value.completedAt) !== null
    && [1, 3, 5].includes(Number(value.rating))
    && (value.errorType === null || value.errorType === undefined || typeof value.errorType === 'string');
}

function practiceCandidate(question, options) {
  const qid = practiceQuestionId(question);
  if (!qid) return null;
  return {
    id: qid,
    question,
    chapter: practiceFacet(options.chapterOf, question),
    type: practiceFacet(options.typeOf, question),
    completedAt: practiceCompletionTimestamp(options.completionByQuestion, qid),
  };
}

// 模考／盲測保留題：MOCK114-*、BLIND108-* 任務尚未完成時，其題目不進隨機練習與奪榜本
// （避免提前看到模考題）。同時出現在 CORE／MIX 任務的題目照常可練。
// options.lockedQids（Set 或陣列）可直接覆寫；否則讀 DAILY_SCHEDULE 與 EE_EXAM_TODAY_TASK_V1.completed。
const PRACTICE_TODAY_TASK_KEY = 'EE_EXAM_TODAY_TASK_V1';
const PRACTICE_RESERVED_KINDS = ['mock114', 'blind108'];
const PRACTICE_PRACTISED_KINDS = ['core', 'mix'];

function practicePaperKey(qid) {
  const m = /^(EE-\d+-\d+)-\d+$/.exec(String(qid || ''));
  return m ? m[1] : null;
}

function practiceLockedQids(options) {
  if (options && options.lockedQids) return new Set(Array.from(options.lockedQids));
  const locked = new Set();
  let schedule = options && options.schedule;
  if (!schedule) {
    try { schedule = typeof DAILY_SCHEDULE !== 'undefined' ? DAILY_SCHEDULE : null; } catch (error) { schedule = null; }
  }
  const tasks = schedule && practiceIsPlainObject(schedule.tasks) ? schedule.tasks : null;
  if (!tasks) return locked;
  let completed = {};
  try {
    const storage = practiceStorageFrom(options);
    const raw = storage ? storage.getItem(PRACTICE_TODAY_TASK_KEY) : null;
    const parsed = raw ? JSON.parse(raw) : null;
    if (parsed && practiceIsPlainObject(parsed.completed)) completed = parsed.completed;
  } catch (error) { completed = {}; }
  const practised = new Set();
  const papers = new Set();
  Object.keys(tasks).forEach(code => {
    const task = tasks[code];
    if (task && PRACTICE_PRACTISED_KINDS.indexOf(task.kind) >= 0) (task.qids || []).forEach(q => practised.add(q));
  });
  Object.keys(tasks).forEach(code => {
    const task = tasks[code];
    if (!task || PRACTICE_RESERVED_KINDS.indexOf(task.kind) < 0 || completed[code]) return;
    (task.qids || []).forEach(q => {
      if (practised.has(q)) return;
      locked.add(q);
      const paper = practicePaperKey(q);
      if (paper) papers.add(paper);
    });
  });
  // 整份試卷一起保留：例如 114 配電只計分 Q1、Q5，但模考畫面會看到 Q2–Q4。
  if (papers.size) {
    const hasExplicit = Set.prototype.has;
    locked.has = qid => hasExplicit.call(locked, qid)
      || (papers.has(practicePaperKey(qid)) && !practised.has(qid));
  }
  return locked;
}

function practiceSelectDiverse(candidates, count, random) {
  const remaining = candidates.map(candidate => Object.assign({}, candidate, {
    tie: practiceRandomValue(random),
  }));
  const selected = [];
  const seenChapters = new Set();
  const seenTypesByChapter = new Map();
  while (selected.length < count && remaining.length) {
    let bestIndex = 0;
    let bestScore = null;
    remaining.forEach((candidate, index) => {
      const chapterIsNew = candidate.chapter !== 'unknown' && !seenChapters.has(candidate.chapter);
      const types = seenTypesByChapter.get(candidate.chapter) || new Set();
      const typeIsNew = candidate.type !== 'unknown' && !types.has(candidate.type);
      // Chapter coverage is the primary objective. Type coverage only breaks
      // ties within an already represented chapter. Unknown is one shared
      // bucket and never earns artificial diversity.
      const score = [chapterIsNew ? 1 : 0, typeIsNew ? 1 : 0, candidate.tie];
      if (!bestScore || score[0] > bestScore[0]
          || (score[0] === bestScore[0] && score[1] > bestScore[1])
          || (score[0] === bestScore[0] && score[1] === bestScore[1] && score[2] > bestScore[2])) {
        bestIndex = index;
        bestScore = score;
      }
    });
    const [chosen] = remaining.splice(bestIndex, 1);
    selected.push(chosen.id);
    if (chosen.chapter !== 'unknown') seenChapters.add(chosen.chapter);
    if (!seenTypesByChapter.has(chosen.chapter)) seenTypesByChapter.set(chosen.chapter, new Set());
    if (chosen.type !== 'unknown') seenTypesByChapter.get(chosen.chapter).add(chosen.type);
  }
  return selected;
}

function createDailyPracticeQueue(questions, options = {}) {
  const count = Number.isInteger(options.count) && options.count > 0 ? options.count : 3;
  const selectedSubject = options.subjectId === undefined || options.subjectId === null ? 'all' : String(options.subjectId);
  const now = practiceResolveNow(options.now);
  const random = typeof options.random === 'function' ? options.random : Math.random;
  const seenIds = new Set();
  const locked = practiceLockedQids(options);
  const candidates = (Array.isArray(questions) ? questions : [])
    .map(question => practiceCandidate(question, options))
    .filter(candidate => {
      if (!candidate || seenIds.has(candidate.id) || locked.has(candidate.id)) return false;
      if (selectedSubject !== 'all' && practiceSubjectId(candidate.question) !== selectedSubject) return false;
      seenIds.add(candidate.id);
      return true;
    });

  const priority = [];
  const recent = [];
  candidates.forEach(candidate => {
    const age = candidate.completedAt === null ? null : now - candidate.completedAt;
    // A completion exactly seven days old is eligible again. Future timestamps
    // are conservatively treated as recent until their seven-day window ends.
    if (age === null || age >= DAILY_PRACTICE_RECENT_WINDOW_MS) priority.push(candidate);
    else recent.push(candidate);
  });

  const target = Math.min(count, candidates.length);
  const chosen = practiceSelectDiverse(priority, Math.min(target, priority.length), random);
  if (chosen.length < target) {
    recent.sort((a, b) => {
      const aTime = a.completedAt === null ? Number.POSITIVE_INFINITY : a.completedAt;
      const bTime = b.completedAt === null ? Number.POSITIVE_INFINITY : b.completedAt;
      return aTime - bTime;
    });
    chosen.push(...recent.slice(0, target - chosen.length).map(candidate => candidate.id));
  }
  return chosen;
}

// 依目標分配: weighted random without replacement over PE candidates that were not
// completed in the last seven days.  Weight comes from options.weightOf(qid) (default
// practiceWeightFor from studyPlan.js); zero-weight questions are never drawn.  With fewer
// than `count` eligible weighted candidates the plain random queue is returned instead.
function createWeightedPracticeQueue(questions, options = {}) {
  const count = Number.isInteger(options.count) && options.count > 0 ? options.count : 3;
  const now = practiceResolveNow(options.now);
  const random = typeof options.random === 'function' ? options.random : Math.random;
  const weightOf = typeof options.weightOf === 'function'
    ? options.weightOf
    : (typeof practiceWeightFor === 'function' ? practiceWeightFor : () => 0);
  const seenIds = new Set();
  const locked = practiceLockedQids(options);
  const pool = [];
  (Array.isArray(questions) ? questions : []).forEach(question => {
    const candidate = practiceCandidate(question, options);
    if (!candidate || seenIds.has(candidate.id)) return;
    seenIds.add(candidate.id);
    if (!candidate.id.startsWith('EE-') || locked.has(candidate.id)) return;
    const age = candidate.completedAt === null ? null : now - candidate.completedAt;
    if (age !== null && age < DAILY_PRACTICE_RECENT_WINDOW_MS) return;
    let weight = 0;
    try { weight = Number(weightOf(candidate.id)); } catch (error) { weight = 0; }
    if (Number.isFinite(weight) && weight > 0) pool.push({ id: candidate.id, weight });
  });
  if (pool.length < count) {
    return createDailyPracticeQueue(questions, Object.assign({}, options, { count, random, now }));
  }
  const chosen = [];
  while (chosen.length < count && pool.length) {
    const total = pool.reduce((sum, item) => sum + item.weight, 0);
    let pick = practiceRandomValue(random) * total;
    let index = 0;
    for (; index < pool.length - 1; index += 1) {
      if (pick < pool[index].weight) break;
      pick -= pool[index].weight;
    }
    chosen.push(pool.splice(index, 1)[0].id);
  }
  return chosen;
}

// ---- v1.3 B: 各科輪流 (balanced) / 補強 (reinforce) / 依日期的預設模式 ----
const PRACTICE_BALANCED_WINDOW_MS = 14 * 24 * 60 * 60 * 1000;
const PRACTICE_ERROR_WINDOW_MS = 21 * 24 * 60 * 60 * 1000;
const PRACTICE_MAIN_PICK_RATE = 0.75;

// Local-date phase: p1 < 2026-10-18 <= p2 <= 2026-11-01 < p3.
function practicePhaseFor(now) {
  const d = new Date(practiceResolveNow(now));
  const key = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  if (key < 20261018) return 'p1';
  if (key <= 20261101) return 'p2';
  return 'p3';
}

function practiceDefaultModeFor(now) {
  const phase = practicePhaseFor(now);
  return phase === 'p1' ? 'balanced' : (phase === 'p2' ? 'weighted' : 'reinforce');
}

function practiceRecordList(options) {
  if (options && Array.isArray(options.records)) return options.records;
  try { if (typeof getResultRecords === 'function') return getResultRecords({}) || []; } catch (error) { /* none */ }
  return [];
}

// Worst mark over the parts of one result-card record: x > tri > o.
function practiceRecordMark(record) {
  const marks = record && Array.isArray(record.parts) ? record.parts.map(p => p && p.mark) : [];
  if (marks.indexOf('x') >= 0) return 'x';
  if (marks.indexOf('tri') >= 0) return 'tri';
  return marks.length ? 'o' : null;
}

function practiceLatestByQid(records, filter) {
  const latest = {};
  records.forEach(record => {
    if (!record || typeof record.qid !== 'string' || (filter && !filter(record))) return;
    const at = Number(record.at) || 0;
    if (!latest[record.qid] || at >= (Number(latest[record.qid].at) || 0)) latest[record.qid] = record;
  });
  return latest;
}

function practiceTierOf(options, qid) {
  try {
    const fn = typeof options.tierOf === 'function' ? options.tierOf : (typeof studyTierFor === 'function' ? studyTierFor : null);
    return fn ? fn(qid) : null;
  } catch (error) { return null; }
}

// Shared pool: PE questions that are not locked, not duplicated and not done in the last 7 days.
function practicePool(questions, options, now) {
  const locked = practiceLockedQids(options);
  const seen = new Set();
  const pool = [];
  (Array.isArray(questions) ? questions : []).forEach(question => {
    const candidate = practiceCandidate(question, options);
    if (!candidate || seen.has(candidate.id)) return;
    seen.add(candidate.id);
    if (!candidate.id.startsWith('EE-') || locked.has(candidate.id)) return;
    const age = candidate.completedAt === null ? null : now - candidate.completedAt;
    if (age !== null && age < DAILY_PRACTICE_RECENT_WINDOW_MS) return;
    candidate.subjectId = practiceSubjectId(question) || (/^EE-\d+-(\d+)-\d+$/.exec(candidate.id) || [])[1] || '';
    candidate.tier = practiceTierOf(options, candidate.id);
    pool.push(candidate);
  });
  return pool;
}

function practiceTakeRandom(list, random) {
  return list.splice(Math.floor(practiceRandomValue(random) * list.length), 1)[0];
}

// Prefer 主攻 (main) candidates; still draw 基本分 (about one in four) when both exist.
function practiceTakeByTier(list, random) {
  const main = list.filter(c => c.tier === 'main');
  const other = list.filter(c => c.tier !== 'main');
  let source = main.length ? main : other;
  if (main.length && other.length && practiceRandomValue(random) >= PRACTICE_MAIN_PICK_RATE) source = other;
  const chosen = practiceTakeRandom(source.slice(), random);
  list.splice(list.indexOf(chosen), 1);
  return chosen;
}

function practiceTopUp(chosen, questions, options, count, random, now) {
  if (chosen.length >= count) return chosen;
  const rest = (Array.isArray(questions) ? questions : []).filter(q => chosen.indexOf(practiceQuestionId(q)) < 0);
  return chosen.concat(createDailyPracticeQueue(rest, Object.assign({}, options, {
    count: count - chosen.length, random, now, subjectId: undefined,
  })));
}

// 各科輪流: least-practised subjects first (result-card records of the last 14 days), one
// question per subject per round, 主攻 chapters preferred.
function createBalancedPracticeQueue(questions, options = {}) {
  const count = Number.isInteger(options.count) && options.count > 0 ? options.count : 3;
  const now = practiceResolveNow(options.now);
  const random = typeof options.random === 'function' ? options.random : Math.random;
  const pool = practicePool(questions, options, now);
  const bySubject = {};
  pool.forEach(c => { (bySubject[c.subjectId] = bySubject[c.subjectId] || []).push(c); });
  const subjectOfQid = {};
  (Array.isArray(questions) ? questions : []).forEach(q => { subjectOfQid[practiceQuestionId(q)] = practiceSubjectId(q); });
  const counts = {};
  practiceRecordList(options).forEach(record => {
    if (!record || record.legacy || (Number(record.at) || 0) < now - PRACTICE_BALANCED_WINDOW_MS) return;
    const subject = subjectOfQid[record.qid] || (/^EE-\d+-(\d+)-\d+$/.exec(String(record.qid)) || [])[1];
    if (subject) counts[subject] = (counts[subject] || 0) + 1;
  });
  const chosen = [];
  while (chosen.length < count) {
    const subjects = Object.keys(bySubject).filter(id => bySubject[id].length)
      .map(id => ({ id, n: counts[id] || 0, tie: practiceRandomValue(random) }))
      .sort((a, b) => a.n - b.n || a.tie - b.tie);
    if (!subjects.length) break;
    for (const subject of subjects) {
      if (chosen.length >= count) break;
      chosen.push(practiceTakeByTier(bySubject[subject.id], random).id);
      counts[subject.id] = (counts[subject.id] || 0) + 1;
    }
  }
  return practiceTopUp(chosen, questions, options, count, random, now);
}

// 補強: (a) mock questions whose latest mock record is △／×, (b) same-chapter questions,
// (c) chapters with the most error codes in the last 21 days.  A question whose latest
// record is all ○ is never repeated.  Empty -> 各科輪流.
function createReinforcePracticeQueue(questions, options = {}) {
  const count = Number.isInteger(options.count) && options.count > 0 ? options.count : 3;
  const now = practiceResolveNow(options.now);
  const random = typeof options.random === 'function' ? options.random : Math.random;
  const records = practiceRecordList(options).filter(r => r && !r.legacy);
  const latestAny = practiceLatestByQid(records);
  const latestMock = practiceLatestByQid(records, r => r.source === 'mock');
  const pool = practicePool(questions, options, now).filter(c => {
    const latest = latestAny[c.id];
    return !(latest && practiceRecordMark(latest) === 'o');
  });
  const byId = {};
  pool.forEach(c => { byId[c.id] = c; });
  const chosen = [];
  const take = list => {
    while (chosen.length < count && list.length) chosen.push(practiceTakeByTier(list, random).id);
  };
  const isUsed = c => chosen.indexOf(c.id) >= 0;

  // (a) mock misses, × before △.
  const seedAll = Object.keys(latestMock).filter(qid => ['x', 'tri'].indexOf(practiceRecordMark(latestMock[qid])) >= 0);
  ['x', 'tri'].forEach(mark => {
    take(seedAll.filter(qid => practiceRecordMark(latestMock[qid]) === mark && byId[qid]).map(qid => byId[qid]));
  });
  // (b) same chapter as any mock miss (main tier first).
  const chapterOfId = {};
  pool.forEach(c => { chapterOfId[c.id] = c.chapter; });
  (Array.isArray(questions) ? questions : []).forEach(q => {
    const id = practiceQuestionId(q);
    if (!(id in chapterOfId)) chapterOfId[id] = practiceFacet(options.chapterOf, q);
  });
  const seedChapters = new Set(seedAll.map(qid => chapterOfId[qid]).filter(ch => ch && ch !== 'unknown'));
  if (chosen.length < count && seedChapters.size) {
    const same = pool.filter(c => !isUsed(c) && seedChapters.has(c.chapter));
    const main = same.filter(c => c.tier === 'main');
    take(main);
    take(same.filter(c => !isUsed(c)));
  }
  // (c) chapters with the most error codes in the last 21 days.
  if (chosen.length < count) {
    const errorCount = {};
    records.forEach(r => {
      if ((Number(r.at) || 0) < now - PRACTICE_ERROR_WINDOW_MS || !Array.isArray(r.errors) || !r.errors.length) return;
      const chapter = chapterOfId[r.qid];
      if (chapter && chapter !== 'unknown') errorCount[chapter] = (errorCount[chapter] || 0) + r.errors.length;
    });
    Object.keys(errorCount).sort((a, b) => errorCount[b] - errorCount[a]).forEach(chapter => {
      if (chosen.length >= count) return;
      const list = pool.filter(c => !isUsed(c) && c.chapter === chapter);
      take(list.filter(c => c.tier === 'main'));
      take(list.filter(c => !isUsed(c)));
    });
  }
  if (!chosen.length) return createBalancedPracticeQueue(questions, Object.assign({}, options, { count, random, now }));
  return practiceTopUpBalanced(chosen, questions, options, count, random, now);
}

function practiceTopUpBalanced(chosen, questions, options, count, random, now) {
  if (chosen.length >= count) return chosen;
  const rest = (Array.isArray(questions) ? questions : []).filter(q => chosen.indexOf(practiceQuestionId(q)) < 0);
  return chosen.concat(createBalancedPracticeQueue(rest, Object.assign({}, options, { count: count - chosen.length, random, now })));
}

function createPracticeStoreState() {
  return {
    version: DAILY_PRACTICE_STORE_VERSION,
    completionByQuestion: {},
    activeSession: null,
  };
}

function practiceNormalizeScrollPositions(value) {
  if (value === undefined) return { question: 0, solution: 0 };
  if (typeof value === 'number' && Number.isFinite(value) && value >= 0) {
    return { question: value, solution: 0 };
  }
  if (!practiceIsPlainObject(value)) return null;
  if (value.question !== undefined && (!Number.isFinite(value.question) || value.question < 0)) return null;
  if (value.solution !== undefined && (!Number.isFinite(value.solution) || value.solution < 0)) return null;
  const question = value.question === undefined ? 0 : value.question;
  const solution = value.solution === undefined ? 0 : value.solution;
  return { question, solution };
}

function practiceNormalizeSession(session) {
  if (session === null) return null;
  if (!practiceIsPlainObject(session)
      || typeof session.category !== 'string'
      || typeof session.subjectId !== 'string'
      || !Array.isArray(session.questionIds)
      || session.questionIds.length === 0
      || session.questionIds.some(qid => typeof qid !== 'string' || !qid)
      || new Set(session.questionIds).size !== session.questionIds.length
      || !Number.isInteger(session.currentIndex)
      || session.currentIndex < 0
      || session.currentIndex >= session.questionIds.length
      || !practiceIsPlainObject(session.revealedByQuestion)
      || !practiceIsPlainObject(session.scrollByQuestion)
      || practiceTimestamp(session.createdAt) === null) return null;

  const next = practiceClone(session);
  const queue = new Set(next.questionIds);
  next.viewByQuestion = practiceIsPlainObject(next.viewByQuestion) ? next.viewByQuestion : {};
  next.revealLevelByQuestion = practiceIsPlainObject(next.revealLevelByQuestion)
    ? next.revealLevelByQuestion : {};
  next.modalByQuestion = practiceIsPlainObject(next.modalByQuestion) ? next.modalByQuestion : {};

  if (Object.entries(next.revealedByQuestion).some(([qid, revealed]) => !queue.has(qid) || typeof revealed !== 'boolean')) return null;
  if (Object.entries(next.viewByQuestion).some(([qid, view]) => !queue.has(qid) || !['question', 'solution'].includes(view))) return null;
  if (Object.entries(next.revealLevelByQuestion).some(([qid, level]) => !queue.has(qid) || !Number.isInteger(level) || level < 0 || level > 4)) return null;
  if (Object.keys(next.scrollByQuestion).some(qid => !queue.has(qid))) return null;
  if (Object.entries(next.modalByQuestion).some(([qid, value]) => !queue.has(qid)
      || !practiceIsPlainObject(value)
      || !Number.isFinite(value.leftScroll) || value.leftScroll < 0
      || !Number.isFinite(value.rightScroll) || value.rightScroll < 0
      || !Number.isInteger(value.subQuestion) || value.subQuestion < 0
      || !Number.isInteger(value.revealStep) || value.revealStep < 0 || value.revealStep > 4
      || !['question', 'solution'].includes(value.pane)
      || typeof value.open !== 'boolean')) return null;

  for (const qid of next.questionIds) {
    if (!next.viewByQuestion[qid]) next.viewByQuestion[qid] = 'question';
    if (!next.modalByQuestion[qid]) next.modalByQuestion[qid] = { leftScroll: 0, rightScroll: 0, subQuestion: 0, revealStep: 0, pane: 'question', open: false };
    if (next.revealLevelByQuestion[qid] === undefined) {
      // Legacy boolean only means that the solution pane was visited; it is
      // not evidence that all four recall layers were completed.
      next.revealLevelByQuestion[qid] = 0;
    }
    next.scrollByQuestion[qid] = practiceNormalizeScrollPositions(next.scrollByQuestion[qid]);
    if (!next.scrollByQuestion[qid]) return null;
  }
  return next;
}

function practiceNormalizeState(state) {
  if (!practiceIsPlainObject(state) || state.version !== DAILY_PRACTICE_STORE_VERSION
      || !practiceIsPlainObject(state.completionByQuestion)) return null;
  const next = practiceClone(state);
  next.activeSession = practiceNormalizeSession(next.activeSession === undefined ? null : next.activeSession);
  if (state.activeSession !== undefined && state.activeSession !== null && next.activeSession === null) return null;
  if (Object.keys(next.completionByQuestion).some(qid => !qid || !practiceValidCompletion(next.completionByQuestion[qid]))) return null;
  return next;
}

function practiceValidSession(session) {
  if (session === null) return true;
  return practiceNormalizeSession(session) !== null;
}

function practiceValidState(state) {
  if (!practiceIsPlainObject(state) || state.version !== DAILY_PRACTICE_STORE_VERSION) return false;
  if (!practiceIsPlainObject(state.completionByQuestion)) return false;
  if (Object.keys(state.completionByQuestion).some(qid => !qid || !practiceValidCompletion(state.completionByQuestion[qid]))) return false;
  return practiceValidSession(state.activeSession);
}

function loadDailyPracticeStore(options = {}) {
  const storage = practiceStorageFrom(options);
  const fallback = createPracticeStoreState();
  if (!storage) return { state: fallback, error: '找不到每日練習的本機儲存空間。' };
  let raw;
  try {
    raw = storage.getItem(DAILY_PRACTICE_STORAGE_KEY);
  } catch (error) {
    return { state: fallback, error: `讀取每日練習資料失敗：${error.message || error}` };
  }
  if (raw === null || raw === '') return { state: fallback, error: null };
  try {
    const parsed = practiceNormalizeState(JSON.parse(raw));
    if (!parsed || !practiceValidState(parsed)) throw new Error('資料格式或版本不符合目前契約');
    return { state: parsed, error: null };
  } catch (error) {
    // Reading bad data never writes the fallback back to the original key.
    return { state: fallback, error: `每日練習資料損壞，已使用空白狀態：${error.message || error}` };
  }
}

function saveDailyPracticeStore(state, options = {}) {
  const storage = practiceStorageFrom(options);
  if (!storage || typeof storage.setItem !== 'function') return { ok: false, error: '找不到每日練習的本機儲存空間。' };
  const normalized = practiceNormalizeState(state);
  if (!normalized || !practiceValidState(normalized)) return { ok: false, error: '每日練習資料不符合目前契約，未寫入。' };
  try {
    storage.setItem(DAILY_PRACTICE_STORAGE_KEY, JSON.stringify(normalized));
    return { ok: true, state: practiceClone(normalized), error: null };
  } catch (error) {
    return { ok: false, error: `寫入每日練習資料失敗：${error.message || error}` };
  }
}

function createPracticeSession(category, subjectId, questionIds, options = {}) {
  const ids = Array.isArray(questionIds) ? questionIds.map(qid => String(qid)).filter(Boolean) : [];
  return {
    category: String(category || ''),
    subjectId: String(subjectId === undefined || subjectId === null ? 'all' : subjectId),
    questionIds: [...new Set(ids)],
    currentIndex: 0,
    revealedByQuestion: {},
    viewByQuestion: {},
    revealLevelByQuestion: {},
    scrollByQuestion: {},
    modalByQuestion: {},
    createdAt: practiceCreatedAt(options.now),
  };
}

function savePracticeSession(session, options = {}) {
  const loaded = loadDailyPracticeStore(options);
  if (loaded.error) return { ok: false, state: loaded.state, error: loaded.error };
  const next = loaded.state;
  next.activeSession = practiceClone(session);
  return saveDailyPracticeStore(next, options);
}

function commitPracticeProgress(session, completedQid, completedAt, options = {}) {
  if (!practiceValidSession(session)) {
    return { ok: false, error: '練習進度不符合目前契約，未寫入。' };
  }
  const id = completedQid === undefined || completedQid === null ? '' : String(completedQid).trim();
  const timestamp = id ? practiceTimestamp(completedAt) : null;
  const loaded = loadDailyPracticeStore(options);
  if (loaded.error) return { ok: false, state: loaded.state, error: loaded.error };
  const sourceSession = session || loaded.state.activeSession;
  if (id && (!sourceSession || !sourceSession.questionIds.includes(id) || timestamp === null)) {
    return { ok: false, error: '完成紀錄必須屬於目前練習，並包含有效時間。' };
  }
  const next = loaded.state;
  next.activeSession = practiceClone(session);
  if (id) next.completionByQuestion[id] = timestamp;
  return saveDailyPracticeStore(next, options);
}

function calculateCompletedPracticeState(state, completedQid, completedAt, assessment) {
  const normalized = practiceNormalizeState(state);
  const qid = String(completedQid || '').trim();
  const timestamp = practiceTimestamp(completedAt);
  const session = normalized && normalized.activeSession;
  if (!normalized || !session || !qid || timestamp === null
      || session.questionIds[session.currentIndex] !== qid) return null;
  const next = practiceClone(normalized);
  const detail = assessment && practiceIsPlainObject(assessment) ? assessment : null;
  next.completionByQuestion[qid] = detail ? {
    completedAt: timestamp,
    rating: [1, 3, 5].includes(Number(detail.rating)) ? Number(detail.rating) : 1,
    errorType: typeof detail.errorType === 'string' && detail.errorType ? detail.errorType : null,
  } : timestamp;
  if (session.currentIndex + 1 >= session.questionIds.length) next.activeSession = null;
  else next.activeSession.currentIndex += 1;
  return next;
}

function clearPracticeSession(options = {}) {
  const loaded = loadDailyPracticeStore(options);
  if (loaded.error) return { ok: false, state: loaded.state, error: loaded.error };
  const next = loaded.state;
  next.activeSession = null;
  return saveDailyPracticeStore(next, options);
}

// Corrupt data is never overwritten during an ordinary read or save.  The UI
// may call this only after it has told the learner that the damaged session
// cannot be restored and offers a safe restart.
function resetDailyPracticeStore(options = {}) {
  return saveDailyPracticeStore(createPracticeStoreState(), options);
}

function loadPracticeSession(options = {}) {
  const loaded = loadDailyPracticeStore(options);
  return { session: loaded.state.activeSession, error: loaded.error };
}

function markPracticeQuestionCompleted(qid, completedAt, options = {}) {
  const id = String(qid || '').trim();
  const timestamp = practiceTimestamp(completedAt);
  if (!id || timestamp === null) return { ok: false, error: '完成紀錄需要有效的 QID 與明確完成時間。' };
  const loaded = loadDailyPracticeStore(options);
  if (loaded.error) return { ok: false, state: loaded.state, error: loaded.error };
  const next = loaded.state;
  next.completionByQuestion[id] = timestamp;
  return saveDailyPracticeStore(next, options);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DAILY_PRACTICE_STORAGE_KEY,
    DAILY_PRACTICE_STORE_VERSION,
    DAILY_PRACTICE_RECENT_WINDOW_MS,
    practiceLockedQids,
    createDailyPracticeQueue,
    createWeightedPracticeQueue,
    createBalancedPracticeQueue,
    createReinforcePracticeQueue,
    practicePhaseFor,
    practiceDefaultModeFor,
    createPracticeStoreState,
    loadDailyPracticeStore,
    saveDailyPracticeStore,
    createPracticeSession,
    savePracticeSession,
    commitPracticeProgress,
    clearPracticeSession,
    resetDailyPracticeStore,
    loadPracticeSession,
    markPracticeQuestionCompleted,
  };
}
