// src/state/store.js
/**
 * Global State Store for EE Exam Workbench.
 * Manages category, progress, starred state, and dual-database bindings.
 */

const STORAGE_KEY = 'EE_EXAM_PROGRESS_V1';
const STARRED_KEY = 'EE_EXAM_STARRED_V1';

let currentExamCategory = localStorage.getItem('exam_category_tab') || 'PE';
let progressState = {};
let starredState = {};
let nationalExamsLoaded = false;

function reloadProgressState() {
  const sKey = currentExamCategory === 'PE' ? STORAGE_KEY : `${currentExamCategory}_EXAM_PROGRESS_V1`;
  const stKey = currentExamCategory === 'PE' ? STARRED_KEY : `${currentExamCategory}_EXAM_STARRED_V1`;
  try {
    progressState = JSON.parse(localStorage.getItem(sKey)) || {};
    starredState = JSON.parse(localStorage.getItem(stKey)) || {};
  } catch (e) {
    progressState = {};
    starredState = {};
  }
}

function saveProgress() {
  const sKey = currentExamCategory === 'PE' ? STORAGE_KEY : `${currentExamCategory}_EXAM_PROGRESS_V1`;
  const stKey = currentExamCategory === 'PE' ? STARRED_KEY : `${currentExamCategory}_EXAM_STARRED_V1`;
  try {
    localStorage.setItem(sKey, JSON.stringify(progressState));
    localStorage.setItem(stKey, JSON.stringify(starredState));
  } catch (e) {
    console.error('Failed to save progress to localStorage', e);
  }
}

function toggleStarred(qid, event) {
  if (event) event.stopPropagation();
  starredState[qid] = !starredState[qid];
  saveProgress();
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  if (typeof renderQuestions === 'function') renderQuestions();
  if (typeof renderReviewPage === 'function') renderReviewPage();
  if (typeof updateModalStatusButtons === 'function') updateModalStatusButtons(qid);
  showToast(starredState[qid] ? '⭐ 已加入重點收藏' : '⚪ 已移除收藏');
}

function toggleStatus(qid, event) {
  if (event) event.stopPropagation();
  const cur = progressState[qid] || 0;
  const nxt = (cur + 1) % 3; // 0 -> 1 -> 2 -> 0
  progressState[qid] = nxt;
  saveProgress();
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
  if (typeof renderQuestions === 'function') renderQuestions();
  if (typeof renderReviewPage === 'function') renderReviewPage();
  if (typeof updateModalStatusButtons === 'function') updateModalStatusButtons(qid);

  const msgs = ['⚪ 狀態重設：未開始', '🟢 狀態更新：已掌握', '🔴 狀態更新：需二刷 (加入錯題本)'];
  showToast(msgs[nxt]);
}

function getActiveQuestionsList() {
  if (currentExamCategory === 'PE') {
    return (typeof DB_DATA !== 'undefined' && DB_DATA.questions) ? DB_DATA.questions : [];
  } else if (currentExamCategory === 'GK') {
    return (typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.questions) ? NATIONAL_EXAMS_DATA.questions : [];
  }
  return [];
}

function findQuestionRecord(qid) {
  if (typeof DB_DATA !== 'undefined' && DB_DATA.questions) {
    const q = DB_DATA.questions.find(item => item[0] === qid);
    if (q) return q;
  }
  if (typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.questions) {
    const q = NATIONAL_EXAMS_DATA.questions.find(item => item[0] === qid);
    if (q) return q;
  }
  return null;
}

function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

// Initial state load
reloadProgressState();
