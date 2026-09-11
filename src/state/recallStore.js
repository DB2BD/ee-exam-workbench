// Active-recall progression and error taxonomy.
// This state is intentionally separate from the legacy 0/1/2 progress flag.

const RECALL_STORAGE_KEY = 'EE_EXAM_RECALL_V1';
const RECALL_ERROR_TYPES = {
  recognition: '題型辨識錯',
  activation: '起手式不會',
  formula: '公式忘記',
  calculation: '計算錯',
  concept: '觀念混淆',
};

let recallState = {};
let recallStoreLoadError = null;

function recallStoreIsPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function recallStoreIsValidState(value) {
  if (!recallStoreIsPlainObject(value)) return false;
  return Object.values(value).every(item => recallStoreIsPlainObject(item)
    && Number.isInteger(Number(item.level)) && Number(item.level) >= 1 && Number(item.level) <= 4
    && Number.isInteger(Number(item.streak)) && Number(item.streak) >= 0
    && Number.isInteger(Number(item.attempts)) && Number(item.attempts) >= 0
    && Number.isFinite(Number(item.lastAchieved)) && Number(item.lastAchieved) >= 0 && Number(item.lastAchieved) <= 4
    && (item.streakVersion === undefined || item.streakVersion === 1)
    && (item.lastErrorType === null || item.lastErrorType === undefined || typeof item.lastErrorType === 'string')
    && (item.lastReviewed === null || item.lastReviewed === undefined || Number.isFinite(Date.parse(item.lastReviewed))));
}

function initRecallStore() {
  if (typeof localStorage === 'undefined') return;
  try {
    const raw = localStorage.getItem(RECALL_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    if (!recallStoreIsValidState(parsed)) throw new Error('回想紀錄格式無效');
    recallState = Object.fromEntries(Object.entries(parsed).map(([qid, item]) => [qid,
      Object.assign({}, item, item.streakVersion === 1 ? {} : { streak: 0 }, { streakVersion: 1 })
    ]));
    recallStoreLoadError = null;
  } catch (e) {
    recallState = {};
    recallStoreLoadError = e;
  }
}

function saveRecallStore(nextState) {
  if (typeof localStorage === 'undefined') return { ok: false, error: '找不到本機儲存空間。' };
  const value = nextState || recallState;
  try {
    localStorage.setItem(RECALL_STORAGE_KEY, JSON.stringify(value));
    return { ok: true, error: null };
  } catch (error) {
    return { ok: false, error: error.message || String(error) };
  }
}

function getRecallState(qid) {
  const item = recallState[qid] || {};
  return {
    level: Math.min(4, Math.max(1, Number(item.level) || 1)),
    streak: Math.max(0, Number(item.streak) || 0),
    attempts: Math.max(0, Number(item.attempts) || 0),
    lastAchieved: Math.max(0, Number(item.lastAchieved) || 0),
    lastErrorType: item.lastErrorType || null,
    lastReviewed: item.lastReviewed || null,
    streakVersion: 1,
  };
}

function calculateRecallAttemptState(currentValue, achievedLevel, errorType, reviewedAt) {
  const current = currentValue || { level: 1, streak: 0, attempts: 0, lastAchieved: 0, lastErrorType: null, lastReviewed: null };
  const achieved = Math.min(4, Math.max(0, Number(achievedLevel) || 0));
  const next = Object.assign({}, current, {
    attempts: current.attempts + 1,
    lastAchieved: achieved,
    lastErrorType: errorType || null,
    lastReviewed: reviewedAt || new Date().toISOString(),
    streakVersion: 1,
  });
  if (achieved >= current.level) {
    next.streak = current.streak + 1;
    if (next.streak >= 2 && current.level < 4) {
      next.level = current.level + 1;
      next.streak = 0;
    }
  } else {
    next.level = Math.max(1, current.level - 1);
    next.streak = 0;
  }
  return next;
}

function recordRecallAttempt(qid, achievedLevel, errorType) {
  if (!qid) return getRecallState(qid);
  const current = getRecallState(qid);
  const next = calculateRecallAttemptState(current, achievedLevel, errorType);
  const nextAll = Object.assign({}, recallState, { [qid]: next });
  const saved = saveRecallStore(nextAll);
  if (!saved.ok) return Object.assign({}, current, { ok: false, error: saved.error });
  recallState = nextAll;
  recallStoreLoadError = null;
  return Object.assign(getRecallState(qid), { ok: true, error: null });
}

function resetRecallState(qid) {
  if (!qid) return;
  delete recallState[qid];
  saveRecallStore();
}

function getRecallHintBundle(qid, qRecord) {
  const chapter = typeof getReviewTypeLabel === 'function' ? getReviewTypeLabel(qRecord) : '待人工複核';
  const key = typeof getReviewChapterKey === 'function' ? getReviewChapterKey(qRecord) : null;
  const node = key && typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[key] : null;
  return {
    chapter,
    activation: node ? `先畫出已知／未知量，依「${node.name}」的標準解法建立第一條方程式。` : '先列出已知量、未知量與要求量，再寫出第一條關係式。',
    formula: node && node.coreFormula ? node.coreFormula : '先寫出本章節的核心公式，再代入題目條件。',
    trap: node && node.keyTrap ? node.keyTrap : '檢查單位、極性、參考方向與邊界條件。',
  };
}

initRecallStore();
