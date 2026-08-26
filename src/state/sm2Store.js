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
 */

const SM2_STORAGE_KEY = 'EE_EXAM_SM2_SCHEDULE_V1';

let sm2Schedule = {};

function initSM2Store() {
  try {
    const raw = localStorage.getItem(SM2_STORAGE_KEY);
    sm2Schedule = raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.error('Failed to load SM-2 schedule from localStorage:', e);
    sm2Schedule = {};
  }
}

function saveSM2Store() {
  try {
    localStorage.setItem(SM2_STORAGE_KEY, JSON.stringify(sm2Schedule));
  } catch (e) {
    console.error('Failed to save SM-2 schedule to localStorage:', e);
  }
}

/**
 * SuperMemo SM-2 Core Algorithm
 * @param {string} qid - Question ID (e.g., 'EE-114-05-1')
 * @param {number} rating - 1: Forgot (🔴), 3: Hard (🟡), 5: Easy/Mastered (🟢)
 */
function recordSM2Review(qid, rating) {
  const now = new Date();
  const todayStr = now.toISOString().split('T')[0];

  let item = sm2Schedule[qid] || {
    repetitions: 0,
    interval: 0,
    easeFactor: 2.5,
    lastReviewed: null,
    nextReviewDate: todayStr
  };

  let { repetitions, interval, easeFactor } = item;

  if (rating < 3) {
    // 🔴 Failed to recall: Reset repetition count and schedule for tomorrow
    repetitions = 0;
    interval = 1;
    easeFactor = Math.max(1.3, easeFactor - 0.2);
  } else if (rating === 3) {
    // 🟡 Hard recall: Slightly increase interval, small EF penalty
    if (repetitions === 0) {
      interval = 1;
    } else if (repetitions === 1) {
      interval = 3;
    } else {
      interval = Math.max(1, Math.round(interval * 1.2));
    }
    repetitions += 1;
    easeFactor = Math.max(1.3, easeFactor - 0.05);
  } else {
    // 🟢 Perfect recall: Standard SM-2 progression
    if (repetitions === 0) {
      interval = 1;
    } else if (repetitions === 1) {
      interval = 4;
    } else {
      interval = Math.round(interval * easeFactor);
    }
    repetitions += 1;
    easeFactor = Math.min(3.0, easeFactor + 0.1);
  }

  // Calculate next review date
  const nextDate = new Date();
  nextDate.setDate(nextDate.getDate() + interval);
  const nextReviewDateStr = nextDate.toISOString().split('T')[0];

  sm2Schedule[qid] = {
    repetitions,
    interval,
    easeFactor: parseFloat(easeFactor.toFixed(2)),
    lastReviewed: todayStr,
    nextReviewDate: nextReviewDateStr
  };

  saveSM2Store();

  // Also sync with progressState (1: Mastered if rating 5, 2: Review if rating 1)
  if (typeof progressState !== 'undefined') {
    if (rating === 5) progressState[qid] = 1;
    else if (rating === 1) progressState[qid] = 2;
    if (typeof saveProgress === 'function') saveProgress();
  }

  return sm2Schedule[qid];
}

/**
 * Returns list of question IDs due today or overdue
 */
function getDueQuestionsList() {
  const todayStr = new Date().toISOString().split('T')[0];
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
function getReviewBadgeInfo(qid) {
  const item = sm2Schedule[qid];
  if (!item || !item.nextReviewDate) {
    return { text: '⚪ 尚未排程', cssClass: 'due-none', isDue: false };
  }

  const todayStr = new Date().toISOString().split('T')[0];
  if (item.nextReviewDate <= todayStr) {
    return { text: '🔔 今日待複習', cssClass: 'due-today', isDue: true };
  }

  const diffMs = new Date(item.nextReviewDate) - new Date(todayStr);
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays >= 14) {
    return { text: `🔥 已穩固 (${diffDays}天後)`, cssClass: 'due-far', isDue: false };
  } else {
    return { text: `⏳ ${diffDays} 天後複習`, cssClass: 'due-soon', isDue: false };
  }
}

/**
 * Export All User Data to JSON
 */
function exportAllUserDataJSON() {
  const data = {
    version: '1.0.0',
    exportedAt: new Date().toISOString(),
    progressState: typeof progressState !== 'undefined' ? progressState : {},
    starredState: typeof starredState !== 'undefined' ? starredState : {},
    sm2Schedule: sm2Schedule
  };
  return JSON.stringify(data, null, 2);
}

/**
 * Import User Data from JSON string
 */
function importUserDataJSON(jsonStr) {
  try {
    const data = JSON.parse(jsonStr);
    if (data.progressState) {
      progressState = data.progressState;
      if (typeof saveProgress === 'function') saveProgress();
    }
    if (data.starredState) {
      starredState = data.starredState;
      if (typeof saveProgress === 'function') saveProgress();
    }
    if (data.sm2Schedule) {
      sm2Schedule = data.sm2Schedule;
      saveSM2Store();
    }
    return { success: true, count: Object.keys(data.progressState || {}).length };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Auto-initialize on load
initSM2Store();
