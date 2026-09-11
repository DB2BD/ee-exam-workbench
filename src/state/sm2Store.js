// -*- coding: utf-8 -*-
/**
 * sm2Store.js
 * ============
 * SuperMemo SM-2 Spaced Repetition Algorithm & Active Recall Manager.
 *
 * Provides:
 * 1. sm2Schedule: Object mapping qid -> { repetitions, interval, easeFactor, lastReviewed, nextReviewDate }
 * 2. recordSM2Review(qid, rating): rating: 1 (Forgot), 3 (Hard), 5 (Easy)
 * 3. getDueQuestionsList(): Returns list of qids due for review today or overdue
 * 4. getReviewBadgeInfo(qid): Returns display badge text and color class
 * 5. exportAllUserDataJSON(): Exports all progress, starred, and SM2 schedule
 * 6. importUserDataJSON(jsonStr): Imports and validates backup
 * 7. Manual topic labels are included so chapter annotations survive backup
 */

const SM2_STORAGE_KEY = 'EE_EXAM_SM2_SCHEDULE_V1';
const USER_BACKUP_SCHEMA = 'ee-exam-user-backup';
const USER_BACKUP_VERSION = '2.1.0';
const USER_BACKUP_SUPPORTED_V2 = ['2.0.0', USER_BACKUP_VERSION];
const BACKUP_META_STORAGE_KEY = 'EE_EXAM_BACKUP_META_V1';
const BACKUP_DAILY_PRACTICE_KEY = 'EE_EXAM_DAILY_PRACTICE_V1';
const BACKUP_MOCK_EXAM_TIMER_KEY = 'EE_MOCK_EXAM_TIMER_V1';
const BACKUP_PROGRESS_KEYS = { PE: 'EE_EXAM_PROGRESS_V1', GK: 'GK_EXAM_PROGRESS_V1' };
const BACKUP_STARRED_KEYS = { PE: 'EE_EXAM_STARRED_V1', GK: 'GK_EXAM_STARRED_V1' };
const BACKUP_CATEGORIES = ['PE', 'GK'];
const BACKUP_RECALL_ERROR_TYPES = ['題型辨識錯', '起手式不會', '公式忘記', '計算錯', '觀念混淆'];

let sm2Schedule = {};
let sm2StoreLoadError = null;

function formatLocalCalendarDate(dateValue) {
  const date = dateValue instanceof Date ? dateValue : new Date(dateValue || Date.now());
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function parseLocalCalendarDate(value) {
  const parts = String(value || '').split('-').map(Number);
  return parts.length === 3 ? new Date(parts[0], parts[1] - 1, parts[2]) : new Date(NaN);
}

function initSM2Store() {
  try {
    const raw = localStorage.getItem(SM2_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    if (!backupIsPlainObject(parsed) || !Object.values(parsed).every(backupValidateSM2)) throw new Error('SM-2 排程格式無效');
    sm2Schedule = parsed;
    sm2StoreLoadError = null;
  } catch (e) {
    console.error('Failed to load SM-2 schedule from localStorage:', e);
    sm2Schedule = {};
    sm2StoreLoadError = e;
  }
}

function saveSM2Store(nextSchedule) {
  const value = nextSchedule || sm2Schedule;
  try {
    localStorage.setItem(SM2_STORAGE_KEY, JSON.stringify(value));
    return { ok: true, error: null };
  } catch (e) {
    console.error('Failed to save SM-2 schedule to localStorage:', e);
    return { ok: false, error: e.message || String(e) };
  }
}

function calculateSM2ReviewItem(currentItem, rating, nowValue) {
  const now = nowValue instanceof Date ? new Date(nowValue.getTime()) : new Date(nowValue || Date.now());
  const todayStr = formatLocalCalendarDate(now);
  const item = currentItem || { repetitions: 0, interval: 0, easeFactor: 2.5, lastReviewed: null, nextReviewDate: todayStr };
  let { repetitions, interval, easeFactor } = item;
  if (rating < 3) {
    repetitions = 0; interval = 1; easeFactor = Math.max(1.3, easeFactor - 0.2);
  } else if (rating === 3) {
    if (repetitions === 0) interval = 1;
    else if (repetitions === 1) interval = 3;
    else interval = Math.max(1, Math.round(interval * 1.2));
    repetitions += 1; easeFactor = Math.max(1.3, easeFactor - 0.05);
  } else {
    if (repetitions === 0) interval = 1;
    else if (repetitions === 1) interval = 4;
    else interval = Math.round(interval * easeFactor);
    repetitions += 1; easeFactor = Math.min(3.0, easeFactor + 0.1);
  }
  const nextDate = new Date(now.getTime());
  nextDate.setDate(nextDate.getDate() + interval);
  return { repetitions, interval, easeFactor: parseFloat(easeFactor.toFixed(2)), lastReviewed: todayStr, nextReviewDate: formatLocalCalendarDate(nextDate) };
}

/**
 * SuperMemo SM-2 Core Algorithm
 * @param {string} qid - Question ID (e.g., 'EE-114-05-1')
 * @param {number} rating - 1: Forgot (🔴), 3: Hard (🟡), 5: Easy/Mastered (🟢)
 */
function recordSM2Review(qid, rating) {
  const now = new Date();
  const nextItem = calculateSM2ReviewItem(sm2Schedule[qid], rating, now);
  const nextSchedule = Object.assign({}, sm2Schedule, { [qid]: nextItem });
  const saved = saveSM2Store(nextSchedule);
  if (!saved.ok) return Object.assign({}, sm2Schedule[qid] || {}, { ok: false, error: saved.error });
  sm2Schedule = nextSchedule;
  sm2StoreLoadError = null;

  // Also sync with progressState (1: Mastered if rating 5, 2: Review if rating 1)
  if (typeof progressState !== 'undefined') {
    if (rating === 5) progressState[qid] = 1;
    else if (rating === 1) progressState[qid] = 2;
    if (typeof saveProgress === 'function') saveProgress();
  }

  return Object.assign({}, sm2Schedule[qid], { ok: true, error: null });
}

/**
 * Returns list of question IDs due today or overdue
 */
function getDueQuestionsList(nowValue) {
  const todayStr = formatLocalCalendarDate(nowValue instanceof Date ? nowValue : new Date(nowValue || Date.now()));
  const dueQids = [];

  for (const [qid, data] of Object.entries(sm2Schedule)) {
    if (data.nextReviewDate && data.nextReviewDate <= todayStr) {
      dueQids.push(qid);
    }
  }
  return dueQids;
}

/**
 * Returns badge info for a question card
 */
function getReviewBadgeInfo(qid, nowValue) {
  const item = sm2Schedule[qid];
  if (!item || !item.nextReviewDate) {
    return { text: '⚪ 尚未排程', cssClass: 'due-none', isDue: false };
  }

  const todayStr = formatLocalCalendarDate(nowValue instanceof Date ? nowValue : new Date(nowValue || Date.now()));
  if (item.nextReviewDate <= todayStr) {
    return { text: '🔔 今日待複習', cssClass: 'due-today', isDue: true };
  }

  const diffMs = parseLocalCalendarDate(item.nextReviewDate) - parseLocalCalendarDate(todayStr);
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays >= 14) {
    return { text: `🔥 已穩固 (${diffDays}天後)`, cssClass: 'due-far', isDue: false };
  } else {
    return { text: `⏳ ${diffDays} 天後複習`, cssClass: 'due-soon', isDue: false };
  }
}

function backupIsPlainObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

function backupClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function backupReadJSON(storage, key, fallback) {
  try {
    const raw = storage && storage.getItem(key);
    if (!raw) return backupClone(fallback);
    const parsed = JSON.parse(raw);
    return backupIsPlainObject(parsed) ? parsed : backupClone(fallback);
  } catch (_) {
    return backupClone(fallback);
  }
}

function backupQuestionRecords(options) {
  const supplied = options && options.recordsByCategory;
  if (supplied && backupIsPlainObject(supplied)) {
    return {
      PE: Array.isArray(supplied.PE) ? supplied.PE : [],
      GK: Array.isArray(supplied.GK) ? supplied.GK : [],
    };
  }
  return {
    PE: typeof DB_DATA !== 'undefined' && Array.isArray(DB_DATA.questions) ? DB_DATA.questions : [],
    GK: typeof NATIONAL_EXAMS_DATA !== 'undefined' && Array.isArray(NATIONAL_EXAMS_DATA.questions) ? NATIONAL_EXAMS_DATA.questions : [],
  };
}

function backupQuestionIds(options) {
  const supplied = options && options.questionIdsByCategory;
  if (supplied && backupIsPlainObject(supplied)) {
    return {
      PE: new Set(Array.isArray(supplied.PE) ? supplied.PE : []),
      GK: new Set(Array.isArray(supplied.GK) ? supplied.GK : []),
    };
  }
  const records = backupQuestionRecords(options);
  return {
    PE: new Set(records.PE.map(item => item && item[0]).filter(Boolean)),
    GK: new Set(records.GK.map(item => item && item[0]).filter(Boolean)),
  };
}

function backupIsDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function backupIsTimestamp(value) {
  return typeof value === 'string' && Number.isFinite(Date.parse(value));
}

function backupError(errors, message) {
  errors.push(`匯入失敗：${message}`);
}

function backupValidateMap(map, allowedIds, valueValidator, name, errors) {
  if (!backupIsPlainObject(map)) {
    backupError(errors, `${name} 必須是物件。`);
    return {};
  }
  const normalized = {};
  Object.entries(map).forEach(([qid, value]) => {
    if (!allowedIds.has(qid)) {
      backupError(errors, `${name} 含未知題號「${qid}」。`);
      return;
    }
    if (!valueValidator(value)) {
      backupError(errors, `${name} 的題號「${qid}」資料格式無效。`);
      return;
    }
    normalized[qid] = value;
  });
  return normalized;
}

function backupValidateSM2(value) {
  return backupIsPlainObject(value)
    && Number.isInteger(value.repetitions) && value.repetitions >= 0
    && Number.isInteger(value.interval) && value.interval >= 0
    && typeof value.easeFactor === 'number' && Number.isFinite(value.easeFactor)
    && value.easeFactor >= 1.3 && value.easeFactor <= 3
    && (value.lastReviewed === null || backupIsDate(value.lastReviewed))
    && backupIsDate(value.nextReviewDate);
}

function backupValidateRecall(value) {
  return backupIsPlainObject(value)
    && Number.isInteger(value.level) && value.level >= 1 && value.level <= 4
    && Number.isInteger(value.streak) && value.streak >= 0
    && Number.isInteger(value.attempts) && value.attempts >= 0
    && Number.isInteger(value.lastAchieved) && value.lastAchieved >= 0 && value.lastAchieved <= 4
    && (value.streakVersion === undefined || value.streakVersion === 1)
    && (value.lastErrorType === null || BACKUP_RECALL_ERROR_TYPES.includes(value.lastErrorType))
    && (value.lastReviewed === null || backupIsTimestamp(value.lastReviewed) || backupIsDate(value.lastReviewed));
}

function backupIsPracticeTimestamp(value) {
  if ((typeof value === 'number' && Number.isFinite(value) && value >= 0) || backupIsTimestamp(value)) return true;
  return backupIsPlainObject(value) && backupIsPracticeTimestamp(value.completedAt)
    && [1, 3, 5].includes(value.rating)
    && (value.errorType === null || BACKUP_RECALL_ERROR_TYPES.includes(value.errorType));
}

function backupValidateDailyPractice(value, ids, errors) {
  if (!backupIsPlainObject(value) || value.version !== 1
      || !backupIsPlainObject(value.completionByQuestion)
      || (value.activeSession !== undefined && !(value.activeSession === null || backupIsPlainObject(value.activeSession)))) {
    backupError(errors, 'dailyPractice 資料格式無效。');
    return null;
  }
  const unionIds = new Set([...ids.PE, ...ids.GK]);
  Object.entries(value.completionByQuestion).forEach(([qid, timestamp]) => {
    if (!unionIds.has(qid) || !backupIsPracticeTimestamp(timestamp)) {
      backupError(errors, `dailyPractice 的完成紀錄「${qid}」無效。`);
    }
  });
  const session = value.activeSession === undefined ? null : value.activeSession;
  if (session === null) return backupClone(value);
  const categoryIds = ids[session.category];
  const questionIds = Array.isArray(session.questionIds) ? session.questionIds : [];
  const sessionShapeValid = BACKUP_CATEGORIES.includes(session.category)
    && typeof session.subjectId === 'string'
    && questionIds.length > 0
    && questionIds.every(qid => typeof qid === 'string' && categoryIds && categoryIds.has(qid))
    && new Set(questionIds).size === questionIds.length
    && Number.isInteger(session.currentIndex) && session.currentIndex >= 0 && session.currentIndex < questionIds.length
    && (session.revealedByQuestion === undefined || backupIsPlainObject(session.revealedByQuestion))
    && (session.scrollByQuestion === undefined || backupIsPlainObject(session.scrollByQuestion))
    && (session.modalByQuestion === undefined || backupIsPlainObject(session.modalByQuestion))
    && backupIsTimestamp(session.createdAt);
  if (!sessionShapeValid) {
    backupError(errors, 'dailyPractice.activeSession 資料格式、考別或題號無效。');
    return null;
  }
  const queueIds = new Set(questionIds);
  const revealedByQuestion = session.revealedByQuestion || {};
  const scrollByQuestion = session.scrollByQuestion || {};
  let invalidSessionState = false;
  Object.entries(revealedByQuestion).forEach(([qid, revealed]) => {
    if (!queueIds.has(qid) || typeof revealed !== 'boolean') {
      backupError(errors, `dailyPractice.activeSession 的詳解揭示狀態「${qid}」無效。`);
      invalidSessionState = true;
    }
  });
  Object.entries(scrollByQuestion).forEach(([qid, positions]) => {
    const validPositions = (typeof positions === 'number' && Number.isFinite(positions) && positions >= 0)
      || (backupIsPlainObject(positions)
        && ['question', 'solution'].every(name => positions[name] === undefined
          || (typeof positions[name] === 'number' && Number.isFinite(positions[name]) && positions[name] >= 0)));
    if (!queueIds.has(qid) || !validPositions) {
      backupError(errors, `dailyPractice.activeSession 的閱讀位置「${qid}」無效。`);
      invalidSessionState = true;
    }
  });
  const viewByQuestion = session.viewByQuestion || {};
  const revealLevelByQuestion = session.revealLevelByQuestion || {};
  const modalByQuestion = session.modalByQuestion || {};
  Object.entries(viewByQuestion).forEach(([qid, view]) => {
    if (!queueIds.has(qid) || !['question', 'solution'].includes(view)) {
      backupError(errors, `dailyPractice.activeSession 的目前視圖「${qid}」無效。`);
      invalidSessionState = true;
    }
  });
  Object.entries(revealLevelByQuestion).forEach(([qid, level]) => {
    if (!queueIds.has(qid) || !Number.isInteger(level) || level < 0 || level > 4) {
      backupError(errors, `dailyPractice.activeSession 的揭露層級「${qid}」無效。`);
      invalidSessionState = true;
    }
  });
  Object.entries(modalByQuestion).forEach(([qid, state]) => {
    const valid = backupIsPlainObject(state)
      && ['leftScroll', 'rightScroll'].every(name => Number.isFinite(state[name]) && state[name] >= 0)
      && Number.isInteger(state.subQuestion) && state.subQuestion >= 0
      && Number.isInteger(state.revealStep) && state.revealStep >= 0 && state.revealStep <= 4
      && ['question', 'solution'].includes(state.pane)
      && typeof state.open === 'boolean';
    if (!queueIds.has(qid) || !valid) {
      backupError(errors, `dailyPractice.activeSession 的詳解閱讀狀態「${qid}」無效。`);
      invalidSessionState = true;
    }
  });
  if (invalidSessionState) return null;

  const normalized = backupClone(value);
  const normalizedSession = normalized.activeSession;
  normalizedSession.revealedByQuestion = revealedByQuestion;
  normalizedSession.viewByQuestion = viewByQuestion;
  normalizedSession.revealLevelByQuestion = revealLevelByQuestion;
  normalizedSession.scrollByQuestion = scrollByQuestion;
  normalizedSession.modalByQuestion = modalByQuestion;
  questionIds.forEach(qid => {
    if (!normalizedSession.viewByQuestion[qid]) normalizedSession.viewByQuestion[qid] = 'question';
    if (!normalizedSession.modalByQuestion[qid]) normalizedSession.modalByQuestion[qid] = { leftScroll: 0, rightScroll: 0, subQuestion: 0, revealStep: 0, pane: 'question', open: false };
    if (normalizedSession.revealLevelByQuestion[qid] === undefined) {
      // Legacy revealedByQuestion is only a view-history flag, not proof of
      // completing the four-step recall workflow.
      normalizedSession.revealLevelByQuestion[qid] = 0;
    }
    const position = normalizedSession.scrollByQuestion[qid];
    normalizedSession.scrollByQuestion[qid] = typeof position === 'number'
      ? { question: position, solution: 0 }
      : { question: Number.isFinite(position && position.question) ? position.question : 0,
          solution: Number.isFinite(position && position.solution) ? position.solution : 0 };
  });
  return normalized;
}

function backupValidateMockExamTimer(value, errors) {
  if (value === null) return null;
  const valid = backupIsPlainObject(value)
    && Number.isInteger(value.seconds) && value.seconds >= 0 && value.seconds <= 7200
    && (value.deadline === null || (typeof value.deadline === 'number' && Number.isFinite(value.deadline) && value.deadline >= 0))
    && typeof value.running === 'boolean'
    && typeof value.completed === 'boolean'
    && typeof value.warningShown === 'boolean'
    && (value.examKey === null || typeof value.examKey === 'string')
    && typeof value.savedAt === 'number' && Number.isFinite(value.savedAt) && value.savedAt >= 0
    && (!value.running || (value.deadline !== null && !value.completed && value.seconds > 0))
    && (!value.completed || value.seconds === 0);
  if (!valid) backupError(errors, 'mockExamTimer 資料格式或計時狀態無效。');
  return valid ? backupClone(value) : null;
}

function backupManualLabelIsValid(qid, value, category, records) {
  if (!backupIsPlainObject(value) || typeof value.chapterId !== 'string' || !value.chapterId) return false;
  if (category !== 'PE' || typeof KNOWLEDGE_DAG === 'undefined' || !KNOWLEDGE_DAG[value.chapterId]) return false;
  const record = records.PE.find(item => item && item[0] === qid);
  if (!record) return false;
  const subjectId = typeof getReviewRecord === 'function' ? getReviewRecord(record).subjectId : record[1];
  const node = KNOWLEDGE_DAG[value.chapterId];
  if (node.subject !== subjectId) return false;
  if (value.updatedAt !== undefined && !backupIsTimestamp(value.updatedAt)) return false;
  if (value.source !== undefined && typeof value.source !== 'string') return false;
  if (value.secondaryTopicIds !== undefined && (!Array.isArray(value.secondaryTopicIds)
      || value.secondaryTopicIds.some(id => typeof id !== 'string' || !KNOWLEDGE_DAG[id]
        || KNOWLEDGE_DAG[id].subject !== subjectId))) return false;
  return true;
}

function validateUserDataBackup(payload, options) {
  const errors = [];
  const opts = options || {};
  if (!backupIsPlainObject(payload)) {
    return { success: false, valid: false, error: '匯入失敗：備份內容必須是 JSON 物件。', errors: ['匯入失敗：備份內容必須是 JSON 物件。'] };
  }
  const isLegacy = payload.version === '1.0.0' && payload.schema === undefined;
  const isSupportedV2 = payload.schema === USER_BACKUP_SCHEMA && USER_BACKUP_SUPPORTED_V2.includes(payload.version);
  if (!isLegacy && !isSupportedV2) {
    backupError(errors, `不支援的備份格式或版本（支援 ${USER_BACKUP_SUPPORTED_V2.join('、')}）。`);
  }
  if (!isLegacy && payload.progressByCategory === undefined) backupError(errors, '缺少 progressByCategory 分類進度資料。');
  if (!isLegacy && payload.starredByCategory === undefined) backupError(errors, '缺少 starredByCategory 分類收藏資料。');
  if (!isLegacy && opts.mode !== 'merge' && opts.allowPartialCategories !== true) {
    BACKUP_CATEGORIES.forEach(category => {
      if (!payload.progressByCategory || payload.progressByCategory[category] === undefined) {
        backupError(errors, `progressByCategory 缺少 ${category} 分類資料。`);
      }
      if (!payload.starredByCategory || payload.starredByCategory[category] === undefined) {
        backupError(errors, `starredByCategory 缺少 ${category} 分類資料。`);
      }
    });
  }
  const ids = backupQuestionIds(opts);
  const records = backupQuestionRecords(opts);
  const unionIds = new Set([...ids.PE, ...ids.GK]);
  const progressByCategory = { PE: {}, GK: {} };
  const starredByCategory = { PE: {}, GK: {} };
  const providedCategories = { PE: false, GK: false };

  const categoryMap = (field, fallbackField, valueType) => {
    const source = payload[field];
    if (source !== undefined && !backupIsPlainObject(source)) {
      backupError(errors, `${field} 必須是物件。`);
      return;
    }
    if (source !== undefined) {
      Object.keys(source).forEach(category => {
        if (!BACKUP_CATEGORIES.includes(category)) backupError(errors, `${field} 含不支援的分類「${category}」。`);
      });
    }
    BACKUP_CATEGORIES.forEach(category => {
      if (source && source[category] !== undefined) {
        providedCategories[category] = true;
        const valid = valueType === 'progress'
          ? value => Number.isInteger(value) && value >= 0 && value <= 2
          : value => typeof value === 'boolean';
        const target = backupValidateMap(source[category], ids[category], valid, `${field}.${category}`, errors);
        if (valueType === 'progress') progressByCategory[category] = target;
        else starredByCategory[category] = target;
      }
    });
    if (isLegacy && payload[fallbackField] !== undefined) {
      const category = BACKUP_CATEGORIES.includes(opts.currentCategory) ? opts.currentCategory
        : (typeof currentExamCategory !== 'undefined' && BACKUP_CATEGORIES.includes(currentExamCategory) ? currentExamCategory : 'PE');
      providedCategories[category] = true;
      const valid = valueType === 'progress'
        ? value => Number.isInteger(value) && value >= 0 && value <= 2
        : value => typeof value === 'boolean';
      const target = backupValidateMap(payload[fallbackField], ids[category], valid, fallbackField, errors);
      if (valueType === 'progress') progressByCategory[category] = target;
      else starredByCategory[category] = target;
    }
  };
  categoryMap('progressByCategory', 'progressState', 'progress');
  categoryMap('starredByCategory', 'starredState', 'starred');

  const sm2Schedule = backupValidateMap(
    payload.sm2Schedule === undefined ? {} : payload.sm2Schedule,
    unionIds,
    backupValidateSM2,
    'sm2Schedule',
    errors
  );
  const recallState = backupValidateMap(
    payload.recallState === undefined ? {} : payload.recallState,
    unionIds,
    backupValidateRecall,
    'recallState',
    errors
  );
  Object.entries(recallState).forEach(([qid, value]) => {
    recallState[qid] = Object.assign({}, value, value.streakVersion === 1 ? {} : { streak: 0 }, { streakVersion: 1 });
  });
  const manualTopicLabels = backupValidateMap(
    payload.manualTopicLabels === undefined ? {} : payload.manualTopicLabels,
    unionIds,
    value => backupIsPlainObject(value),
    'manualTopicLabels',
    errors
  );
  Object.entries(payload.manualTopicLabels || {}).forEach(([qid, value]) => {
    const category = ids.PE.has(qid) ? 'PE' : 'GK';
    if (!backupManualLabelIsValid(qid, value, category, records)) {
      backupError(errors, `manualTopicLabels 的題號「${qid}」章節標籤無效或與科目不符。`);
      delete manualTopicLabels[qid];
    }
  });

  const phase2Required = payload.version === USER_BACKUP_VERSION;
  const dailyPracticeProvided = Object.prototype.hasOwnProperty.call(payload, 'dailyPractice');
  const mockExamTimerProvided = Object.prototype.hasOwnProperty.call(payload, 'mockExamTimer');
  if (phase2Required && !dailyPracticeProvided) backupError(errors, '缺少 dailyPractice 每日練習資料。');
  if (phase2Required && !mockExamTimerProvided) backupError(errors, '缺少 mockExamTimer 模考計時資料。');
  const dailyPractice = dailyPracticeProvided
    ? backupValidateDailyPractice(payload.dailyPractice, ids, errors) : null;
  const mockExamTimer = mockExamTimerProvided
    ? backupValidateMockExamTimer(payload.mockExamTimer, errors) : null;

  if (errors.length) {
    return { success: false, valid: false, error: errors[0], errors };
  }
  const normalized = {
    schema: USER_BACKUP_SCHEMA,
    version: isLegacy ? '1.0.0' : USER_BACKUP_VERSION,
    progressByCategory,
    starredByCategory,
    sm2Schedule,
    recallState,
    manualTopicLabels,
    dailyPractice,
    mockExamTimer,
    dailyPracticeProvided,
    mockExamTimerProvided,
    providedCategories,
    legacy: isLegacy,
  };
  const summary = {
    schema: USER_BACKUP_SCHEMA,
    version: normalized.version,
    progress: Object.values(progressByCategory).reduce((n, map) => n + Object.keys(map).length, 0),
    progressByCategory: Object.fromEntries(BACKUP_CATEGORIES.map(category => [category, Object.keys(progressByCategory[category]).length])),
    starred: Object.values(starredByCategory).reduce((n, map) => n + Object.values(map).filter(Boolean).length, 0),
    starredByCategory: Object.fromEntries(BACKUP_CATEGORIES.map(category => [category, Object.values(starredByCategory[category]).filter(Boolean).length])),
    sm2: Object.keys(sm2Schedule).length,
    recall: Object.keys(recallState).length,
    manualLabels: Object.keys(manualTopicLabels).length,
    practiceCompleted: dailyPractice ? Object.keys(dailyPractice.completionByQuestion).length : 0,
    practiceSession: !!(dailyPractice && dailyPractice.activeSession),
    mockTimer: !!mockExamTimer,
  };
  return { success: true, valid: true, normalized, summary };
}

function getBackupMetadata() {
  return backupReadJSON(typeof localStorage !== 'undefined' ? localStorage : null, BACKUP_META_STORAGE_KEY, {});
}

function backupWriteMetadata(next) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(BACKUP_META_STORAGE_KEY, JSON.stringify(next));
}

function buildUserBackupSnapshot() {
  const storage = typeof localStorage !== 'undefined' ? localStorage : null;
  const progressByCategory = {};
  const starredByCategory = {};
  BACKUP_CATEGORIES.forEach(category => {
    progressByCategory[category] = backupReadJSON(storage, BACKUP_PROGRESS_KEYS[category], {});
    starredByCategory[category] = backupReadJSON(storage, BACKUP_STARRED_KEYS[category], {});
  });
  const currentCategory = typeof currentExamCategory !== 'undefined' && BACKUP_CATEGORIES.includes(currentExamCategory)
    ? currentExamCategory : 'PE';
  if (storage && storage.getItem(BACKUP_PROGRESS_KEYS[currentCategory]) === null && typeof progressState !== 'undefined') {
    progressByCategory[currentCategory] = backupClone(progressState || {});
  }
  if (storage && storage.getItem(BACKUP_STARRED_KEYS[currentCategory]) === null && typeof starredState !== 'undefined') {
    starredByCategory[currentCategory] = backupClone(starredState || {});
  }
  const metadata = getBackupMetadata();
  const exportedAt = new Date().toISOString();
  const loadedPractice = typeof loadDailyPracticeStore === 'function'
    ? loadDailyPracticeStore({ storage })
    : { state: backupReadJSON(storage, BACKUP_DAILY_PRACTICE_KEY, { version: 1, completionByQuestion: {}, activeSession: null }) };
  const timerCandidate = backupReadJSON(storage, BACKUP_MOCK_EXAM_TIMER_KEY, {});
  const timerErrors = [];
  const mockExamTimer = Object.keys(timerCandidate).length
    ? backupValidateMockExamTimer(timerCandidate, timerErrors) : null;
  const snapshot = {
    schema: USER_BACKUP_SCHEMA,
    version: USER_BACKUP_VERSION,
    exportedAt,
    category: currentCategory,
    progressByCategory,
    starredByCategory,
    // Kept for one-version compatibility with older backup consumers.
    progressState: backupClone(progressByCategory[currentCategory]),
    starredState: backupClone(starredByCategory[currentCategory]),
    sm2Schedule: backupClone(sm2Schedule || {}),
    recallState: typeof recallState !== 'undefined' ? backupClone(recallState || {}) : {},
    manualTopicLabels: typeof getManualTopicLabels === 'function' ? backupClone(getManualTopicLabels()) : {},
    dailyPractice: backupClone(loadedPractice.state),
    mockExamTimer,
  };
  try {
    backupWriteMetadata(Object.assign({}, metadata, { lastBackupAt: exportedAt, lastBackupVersion: USER_BACKUP_VERSION }));
  } catch (_) { /* Export remains usable if metadata cannot be written. */ }
  return snapshot;
}

function applyUserDataBackup(payloadOrJson, mode, options) {
  const recoveryStorage = options && options.storage ? options.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  try {
    if (recoveryStorage && recoveryStorage.getItem('EE_EXAM_ATTEMPT_RECOVERY_V1')) {
      return { success: false, error: '尚有未完成的學習紀錄回復，請先完成回復再匯入備份。' };
    }
  } catch (_) {
    return { success: false, error: '無法確認學習紀錄回復狀態，未匯入備份。' };
  }
  const selectedMode = mode || 'replace';
  if (selectedMode !== 'merge' && selectedMode !== 'replace') {
    return { success: false, error: '匯入失敗：還原模式必須是「合併」或「取代」，未修改任何資料。' };
  }
  let payload;
  try {
    payload = typeof payloadOrJson === 'string' ? JSON.parse(payloadOrJson) : payloadOrJson;
  } catch (_) {
    return { success: false, error: '匯入失敗：JSON 格式無效，未修改任何資料。' };
  }
  const validation = validateUserDataBackup(payload, Object.assign({}, options || {}, {
    mode: selectedMode,
    allowPartialCategories: selectedMode === 'merge',
  }));
  if (!validation.success) return validation;

  const opts = options || {};
  const storage = opts.storage || (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage || typeof storage.setItem !== 'function') {
    return { success: false, error: '匯入失敗：找不到瀏覽器本機儲存空間，未修改任何資料。' };
  }
  const oldProgress = {};
  const oldStarred = {};
  BACKUP_CATEGORIES.forEach(category => {
    oldProgress[category] = backupReadJSON(storage, BACKUP_PROGRESS_KEYS[category], {});
    oldStarred[category] = backupReadJSON(storage, BACKUP_STARRED_KEYS[category], {});
  });
  const currentCategory = BACKUP_CATEGORIES.includes(opts.currentCategory)
    ? opts.currentCategory : (typeof currentExamCategory !== 'undefined' && BACKUP_CATEGORIES.includes(currentExamCategory) ? currentExamCategory : 'PE');
  if (storage.getItem(BACKUP_PROGRESS_KEYS[currentCategory]) === null && typeof progressState !== 'undefined') oldProgress[currentCategory] = backupClone(progressState || {});
  if (storage.getItem(BACKUP_STARRED_KEYS[currentCategory]) === null && typeof starredState !== 'undefined') oldStarred[currentCategory] = backupClone(starredState || {});
  const oldSM2 = backupReadJSON(storage, SM2_STORAGE_KEY, typeof sm2Schedule !== 'undefined' ? sm2Schedule : {});
  const oldRecall = backupReadJSON(storage, 'EE_EXAM_RECALL_V1', typeof recallState !== 'undefined' ? recallState : {});
  const oldLabels = backupReadJSON(storage, 'EE_MANUAL_TOPIC_LABELS_V1', typeof getManualTopicLabels === 'function' ? getManualTopicLabels() : {});
  const oldPractice = backupReadJSON(storage, BACKUP_DAILY_PRACTICE_KEY, { version: 1, completionByQuestion: {}, activeSession: null });
  const oldTimer = backupReadJSON(storage, BACKUP_MOCK_EXAM_TIMER_KEY, {});
  const nextProgress = backupClone(oldProgress);
  const nextStarred = backupClone(oldStarred);
  BACKUP_CATEGORIES.forEach(category => {
    const hasCategory = validation.normalized.providedCategories[category];
    if (selectedMode === 'replace' && (!validation.normalized.legacy || hasCategory)) nextProgress[category] = {};
    if (selectedMode === 'replace' && (!validation.normalized.legacy || hasCategory)) nextStarred[category] = {};
    if (hasCategory) {
      Object.assign(nextProgress[category], validation.normalized.progressByCategory[category]);
      Object.assign(nextStarred[category], validation.normalized.starredByCategory[category]);
    }
  });
  const nextSM2 = selectedMode === 'merge' ? Object.assign({}, oldSM2, validation.normalized.sm2Schedule) : backupClone(validation.normalized.sm2Schedule);
  const nextRecall = selectedMode === 'merge' ? Object.assign({}, oldRecall, validation.normalized.recallState) : backupClone(validation.normalized.recallState);
  const nextLabels = selectedMode === 'merge' ? Object.assign({}, oldLabels, validation.normalized.manualTopicLabels) : backupClone(validation.normalized.manualTopicLabels);
  let nextPractice = oldPractice;
  if (validation.normalized.dailyPracticeProvided) {
    const importedPractice = validation.normalized.dailyPractice;
    if (selectedMode === 'replace') {
      nextPractice = backupClone(importedPractice);
    } else {
      const localSession = oldPractice.activeSession;
      const importedSession = importedPractice.activeSession;
      const localCreatedAt = localSession ? Date.parse(localSession.createdAt) : -1;
      const importedCreatedAt = importedSession ? Date.parse(importedSession.createdAt) : -1;
      nextPractice = {
        version: 1,
        completionByQuestion: Object.assign({}, oldPractice.completionByQuestion || {}, importedPractice.completionByQuestion || {}),
        activeSession: importedCreatedAt > localCreatedAt ? backupClone(importedSession) : backupClone(localSession),
      };
    }
  }
  const nextTimer = validation.normalized.mockExamTimerProvided
    ? backupClone(validation.normalized.mockExamTimer) : oldTimer;
  const metadataKey = BACKUP_META_STORAGE_KEY;
  const oldRaw = {};
  [BACKUP_PROGRESS_KEYS.PE, BACKUP_PROGRESS_KEYS.GK, BACKUP_STARRED_KEYS.PE, BACKUP_STARRED_KEYS.GK, SM2_STORAGE_KEY, 'EE_EXAM_RECALL_V1', 'EE_MANUAL_TOPIC_LABELS_V1', BACKUP_DAILY_PRACTICE_KEY, BACKUP_MOCK_EXAM_TIMER_KEY, metadataKey].forEach(key => {
    oldRaw[key] = storage.getItem(key);
  });
  const importedAt = new Date().toISOString();
  const nextMeta = Object.assign({}, backupReadJSON(storage, metadataKey, {}), { lastImportAt: importedAt, lastImportVersion: validation.normalized.version, lastImportMode: selectedMode });
  let writes;
  try {
    writes = [
      [BACKUP_PROGRESS_KEYS.PE, JSON.stringify(nextProgress.PE)], [BACKUP_PROGRESS_KEYS.GK, JSON.stringify(nextProgress.GK)],
      [BACKUP_STARRED_KEYS.PE, JSON.stringify(nextStarred.PE)], [BACKUP_STARRED_KEYS.GK, JSON.stringify(nextStarred.GK)],
      [SM2_STORAGE_KEY, JSON.stringify(nextSM2)], ['EE_EXAM_RECALL_V1', JSON.stringify(nextRecall)],
      ['EE_MANUAL_TOPIC_LABELS_V1', JSON.stringify(nextLabels)], [metadataKey, JSON.stringify(nextMeta)],
    ];
    if (validation.normalized.dailyPracticeProvided) writes.splice(writes.length - 1, 0, [BACKUP_DAILY_PRACTICE_KEY, JSON.stringify(nextPractice)]);
    if (validation.normalized.mockExamTimerProvided) writes.splice(writes.length - 1, 0, [BACKUP_MOCK_EXAM_TIMER_KEY, JSON.stringify(nextTimer)]);
  } catch (_) {
    return { success: false, error: '匯入失敗：備份資料無法序列化，未修改任何資料。' };
  }
  const written = [];
  try {
    writes.forEach(([key, value]) => { written.push(key); storage.setItem(key, value); });
  } catch (_) {
    written.reverse().forEach(key => {
      try {
        if (oldRaw[key] === null) storage.removeItem(key);
        else storage.setItem(key, oldRaw[key]);
      } catch (__) { /* Best-effort rollback; memory still remains unchanged. */ }
    });
    return { success: false, error: '匯入失敗：寫入本機儲存空間時發生錯誤，已回復原資料。' };
  }
  if (typeof progressState !== 'undefined') progressState = backupClone(nextProgress[currentCategory]);
  if (typeof starredState !== 'undefined') starredState = backupClone(nextStarred[currentCategory]);
  sm2Schedule = backupClone(nextSM2);
  sm2StoreLoadError = null;
  if (typeof recallState !== 'undefined') recallState = backupClone(nextRecall);
  if (typeof recallStoreLoadError !== 'undefined') recallStoreLoadError = null;
  if (typeof manualTopicLabels !== 'undefined') manualTopicLabels = backupClone(nextLabels);
  const appliedSummary = Object.assign({}, validation.summary, {
    progress: Object.values(nextProgress).reduce((n, map) => n + Object.keys(map).length, 0),
    progressByCategory: Object.fromEntries(BACKUP_CATEGORIES.map(category => [category, Object.keys(nextProgress[category]).length])),
    starred: Object.values(nextStarred).reduce((n, map) => n + Object.values(map).filter(Boolean).length, 0),
    starredByCategory: Object.fromEntries(BACKUP_CATEGORIES.map(category => [category, Object.values(nextStarred[category]).filter(Boolean).length])),
    sm2: Object.keys(nextSM2).length,
    recall: Object.keys(nextRecall).length,
    manualLabels: Object.keys(nextLabels).length,
    practiceCompleted: Object.keys(nextPractice.completionByQuestion || {}).length,
    practiceSession: !!nextPractice.activeSession,
    mockTimer: validation.normalized.mockExamTimerProvided ? !!nextTimer : Object.keys(oldTimer).length > 0,
  });
  return { success: true, mode: selectedMode, summary: appliedSummary };
}

/**
 * Export All User Data to JSON
 */
function exportAllUserDataJSON() {
  return JSON.stringify(buildUserBackupSnapshot(), null, 2);
}

/**
 * Import User Data from JSON string
 */
function importUserDataJSON(jsonStr) {
  return applyUserDataBackup(jsonStr, 'replace');
}

// Auto-initialize on load
initSM2Store();
