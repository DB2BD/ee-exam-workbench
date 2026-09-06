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

function practiceValidSession(session) {
  if (session === null) return true;
  if (!practiceIsPlainObject(session)) return false;
  if (typeof session.category !== 'string' || typeof session.subjectId !== 'string') return false;
  if (!Array.isArray(session.questionIds) || session.questionIds.some(qid => typeof qid !== 'string' || !qid)) return false;
  if (new Set(session.questionIds).size !== session.questionIds.length) return false;
  if (!Number.isInteger(session.currentIndex) || session.currentIndex < 0) return false;
  if (session.questionIds.length && session.currentIndex >= session.questionIds.length) return false;
  if (!practiceIsPlainObject(session.revealedByQuestion) || !practiceIsPlainObject(session.scrollByQuestion)) return false;
  const queue = new Set(session.questionIds);
  if (Object.entries(session.revealedByQuestion).some(([qid, revealed]) => !queue.has(qid) || typeof revealed !== 'boolean')) return false;
  if (Object.entries(session.scrollByQuestion).some(([qid, positions]) => {
    if (!queue.has(qid) || !practiceIsPlainObject(positions)) return true;
    return ['question', 'solution'].some(name => positions[name] !== undefined
      && (typeof positions[name] !== 'number' || !Number.isFinite(positions[name]) || positions[name] < 0));
  })) return false;
  return practiceTimestamp(session.createdAt) !== null;
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
    const parsed = JSON.parse(raw);
    if (!practiceValidState(parsed)) throw new Error('資料格式或版本不符合目前契約');
    return { state: practiceClone(parsed), error: null };
  } catch (error) {
    // Reading bad data never writes the fallback back to the original key.
    return { state: fallback, error: `每日練習資料損壞，已使用空白狀態：${error.message || error}` };
  }
}

function saveDailyPracticeStore(state, options = {}) {
  const storage = practiceStorageFrom(options);
  if (!storage || typeof storage.setItem !== 'function') return { ok: false, error: '找不到每日練習的本機儲存空間。' };
  if (!practiceValidState(state)) return { ok: false, error: '每日練習資料不符合目前契約，未寫入。' };
  try {
    storage.setItem(DAILY_PRACTICE_STORAGE_KEY, JSON.stringify(state));
    return { ok: true, state: practiceClone(state), error: null };
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
