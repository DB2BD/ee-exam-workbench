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
  const candidates = (Array.isArray(questions) ? questions : [])
    .map(question => practiceCandidate(question, options))
    .filter(candidate => {
      if (!candidate || seenIds.has(candidate.id)) return false;
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

  if (Object.entries(next.revealedByQuestion).some(([qid, revealed]) => !queue.has(qid) || typeof revealed !== 'boolean')) return null;
  if (Object.entries(next.viewByQuestion).some(([qid, view]) => !queue.has(qid) || !['question', 'solution'].includes(view))) return null;
  if (Object.entries(next.revealLevelByQuestion).some(([qid, level]) => !queue.has(qid) || !Number.isInteger(level) || level < 0 || level > 4)) return null;
  if (Object.keys(next.scrollByQuestion).some(qid => !queue.has(qid))) return null;

  for (const qid of next.questionIds) {
    if (!next.viewByQuestion[qid]) next.viewByQuestion[qid] = 'question';
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
  if (Object.keys(next.completionByQuestion).some(qid => !qid || practiceTimestamp(next.completionByQuestion[qid]) === null)) return null;
  return next;
}

function practiceValidSession(session) {
  if (session === null) return true;
  return practiceNormalizeSession(session) !== null;
}

function practiceValidState(state) {
  if (!practiceIsPlainObject(state) || state.version !== DAILY_PRACTICE_STORE_VERSION) return false;
  if (!practiceIsPlainObject(state.completionByQuestion)) return false;
  if (Object.keys(state.completionByQuestion).some(qid => !qid || practiceTimestamp(state.completionByQuestion[qid]) === null)) return false;
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
    createDailyPracticeQueue,
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
