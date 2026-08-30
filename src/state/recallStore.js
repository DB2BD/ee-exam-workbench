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

function initRecallStore() {
  if (typeof localStorage === 'undefined') return;
  try {
    recallState = JSON.parse(localStorage.getItem(RECALL_STORAGE_KEY)) || {};
  } catch (e) {
    recallState = {};
  }
}

function saveRecallStore() {
  if (typeof localStorage === 'undefined') return;
  try { localStorage.setItem(RECALL_STORAGE_KEY, JSON.stringify(recallState)); } catch (e) { /* private mode */ }
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
  };
}

function recordRecallAttempt(qid, achievedLevel, errorType) {
  if (!qid) return getRecallState(qid);
  const current = getRecallState(qid);
  const achieved = Math.min(4, Math.max(0, Number(achievedLevel) || 0));
  const next = Object.assign({}, current, {
    attempts: current.attempts + 1,
    lastAchieved: achieved,
    lastErrorType: errorType || null,
    lastReviewed: new Date().toISOString(),
  });
  if (achieved >= current.level) {
    next.streak = current.streak + 1;
    if (next.streak >= 2 && current.level < 4) next.level = current.level + 1;
  } else {
    next.level = Math.max(1, current.level - 1);
    next.streak = 0;
  }
  recallState[qid] = next;
  saveRecallStore();
  return getRecallState(qid);
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
