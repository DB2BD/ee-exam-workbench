// src/main.js
/**
 * Main Application Orchestrator & Entry Point.
 */

function switchTab(tabId) {
  // Only the panes that still exist in the shell are routable (今天 / 模考 / 成績 / 題庫瀏覽).
  const activePane = document.getElementById('tab-pane-' + tabId);
  if (!activePane) return;
  document.querySelectorAll('.main-tab-btn').forEach(btn => { btn.classList.remove('active'); btn.removeAttribute('aria-current'); });
  document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');

  // A tool selected from the compact 更多 menu should leave the menu closed, so
  // the selected pane (not the menu overlay) gets the user's focus.
  const moreToolsMenu = document.getElementById('more-tools-menu');
  if (moreToolsMenu) {
    moreToolsMenu.open = false;
    moreToolsMenu.classList.toggle('has-active', tabId === 'questions');
  }

  const activeBtn = document.getElementById('tab-btn-' + tabId);
  if (activeBtn) { activeBtn.classList.add('active'); activeBtn.setAttribute('aria-current', 'page'); }
  activePane.style.display = 'block';
  if (document.body) document.body.dataset.tab = tabId;

  if (tabId === 'scoreboard' && typeof renderScoreboard === 'function') {
    renderScoreboard(document.getElementById('scoreboard-container'));
  }
  if (tabId === 'practice') {
    if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
    if (typeof initTodayTask === 'function') initTodayTask();
    if (typeof renderAnswerCorrectionReviewSection === 'function') {
      try { renderAnswerCorrectionReviewSection(); } catch (_) { /* optional section */ }
    }
  }
  if (typeof updateHeaderSummary === 'function') updateHeaderSummary();
  appHistoryPushTab(tabId);
}

// ---------- 返回鍵／滑動返回 ----------
// Tab switches and the solution modal each leave one history entry (same URL, state only), so the
// browser's back closes the modal first and then walks back through the tabs instead of leaving the
// workbench. A programmatic close steps back over the modal entry; if the modal reopens before that
// step lands (保存並下一題), the entry is pushed again once it has.
let appHistoryApplying = false;
let appHistoryBackPending = false;
let appHistoryReopenPending = false;

function appHistoryAvailable() {
  return typeof history !== 'undefined' && typeof history.pushState === 'function';
}

function appHistoryCurrentTab() {
  const btn = typeof document !== 'undefined' ? document.querySelector('.main-tab-btn.active') : null;
  return btn && btn.id ? btn.id.replace('tab-btn-', '') : 'practice';
}

function appHistoryPushTab(tabId) {
  if (appHistoryApplying || !appHistoryAvailable()) return;
  const state = history.state || {};
  if (state.eeModal || state.eeTab === tabId) return;
  history.pushState({ eeTab: tabId }, '');
}

function appHistoryModalOpened() {
  if (appHistoryApplying || !appHistoryAvailable()) return;
  if (appHistoryBackPending) { appHistoryReopenPending = true; return; }
  if (history.state && history.state.eeModal) return;
  history.pushState({ eeTab: appHistoryCurrentTab(), eeModal: true }, '');
}

function appHistoryModalClosed() {
  if (appHistoryApplying || !appHistoryAvailable()) return;
  if (history.state && history.state.eeModal) {
    appHistoryBackPending = true;
    history.back();
  }
}

function appHistoryOnPopState(event) {
  const state = (event && event.state) || {};
  const modal = document.getElementById('solution-modal');
  const modalOpen = !!(modal && modal.classList.contains('show'));
  if (appHistoryBackPending) {
    appHistoryBackPending = false;
    if (appHistoryReopenPending && modalOpen) history.pushState({ eeTab: appHistoryCurrentTab(), eeModal: true }, '');
    appHistoryReopenPending = false;
    return;
  }
  appHistoryApplying = true;
  try {
    if (modalOpen && !state.eeModal && typeof closeModal === 'function') closeModal();
    if (state.eeTab && state.eeTab !== appHistoryCurrentTab()) switchTab(state.eeTab);
  } finally {
    appHistoryApplying = false;
  }
}

if (typeof window !== 'undefined' && appHistoryAvailable()) {
  if (!history.state || !history.state.eeTab) history.replaceState({ eeTab: 'practice' }, '');
  window.addEventListener('popstate', appHistoryOnPopState);
}


function handleUrlHashRouting() {
  const hash = window.location.hash;
  if (hash && hash.startsWith('#q=')) {
    const targetQid = decodeURIComponent(hash.substring(3)).trim();
    const qRecord = findQuestionRecord(targetQid);
    if (qRecord) {
      const [qid, sid, yr, qnum, topic, tags, solLink] = qRecord;
      const subSelect = document.getElementById('filter-subject');
      const yrSelect = document.getElementById('filter-year');
      if (subSelect) subSelect.value = sid;
      if (yrSelect) yrSelect.value = String(yr);
      if (typeof renderQuestions === 'function') renderQuestions();
      if (typeof openSolutionModal === 'function') openSolutionModal(null, solLink, qid, qnum, { mode: 'browse' });
    }
  }
}

function initPaneResizer() {
  const resizer = document.getElementById('modal-resizer');
  const leftPane = document.getElementById('modal-pane-left');
  if (!resizer || !leftPane) return;

  let isDragging = false;

  resizer.addEventListener('mousedown', (e) => {
    isDragging = true;
    resizer.classList.add('dragging');
    document.body.style.userSelect = 'none';
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const modalContainer = document.querySelector('.modal-container');
    if (!modalContainer) return;
    const rect = modalContainer.getBoundingClientRect();
    const offsetLeft = e.clientX - rect.left;
    const pct = Math.max(25, Math.min(75, (offsetLeft / rect.width) * 100));
    leftPane.style.flex = `0 0 ${pct}%`;
    // The split body is a grid: its left column width follows --modal-left (see modal.css).
    const splitBody = document.getElementById('modal-split-body');
    if (splitBody) splitBody.style.setProperty('--modal-left', `${pct}%`);
  });

  window.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      resizer.classList.remove('dragging');
      document.body.style.userSelect = '';
    }
  });
}

function themeButtonLabel(theme) {
  return theme === 'dark' ? '<span class="theme-ico" aria-hidden="true">' + uiIcon('sun') + '</span><span class="theme-label"> 亮色模式</span>' : '<span class="theme-ico" aria-hidden="true">' + uiIcon('moon') + '</span><span class="theme-label"> 暗色模式</span>';
}

function applyThemeAttribute(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) btn.innerHTML = themeButtonLabel(theme);
}

function readThemePreference() {
  try { return localStorage.getItem('ee_theme_preference'); } catch (_) { return null; }
}

function applyInitialTheme() {
  const saved = readThemePreference();
  if (saved === 'dark' || saved === 'light') { applyThemeAttribute(saved); return; }
  if (typeof window.matchMedia !== 'function') return;
  const query = window.matchMedia('(prefers-color-scheme: dark)');
  applyThemeAttribute(query.matches ? 'dark' : 'light');
  const onChange = event => {
    const manual = readThemePreference();
    if (manual === 'dark' || manual === 'light') return;
    applyThemeAttribute(event.matches ? 'dark' : 'light');
  };
  if (typeof query.addEventListener === 'function') query.addEventListener('change', onChange);
  else if (typeof query.addListener === 'function') query.addListener(onChange);
}

// Global DOM Content Loaded Bootstrap
document.addEventListener('DOMContentLoaded', () => {
  uiIconHydrate(document);
  // 0. The 更多 menu closes after picking an item or clicking elsewhere.
  document.addEventListener('click', event => {
    const menu = document.getElementById('more-tools-menu');
    if (!menu || !menu.open) return;
    if (!menu.contains(event.target) || event.target.closest('.more-tools-panel button')) menu.open = false;
  });

  // 1. Theme initialization: a manual choice wins; otherwise follow the system setting live.
  applyInitialTheme();

  // 2. Restore category & populate category dropdown options first
  // PE only: the GK switcher is gone and its data is not preloaded.
  switchExamCategory('PE', true);
  // 2b. One-time: 學習狀態 follows the latest result card (△ now counts as 需二刷; legacy cards included).
  if (typeof reconcileProgressWithResultCards === 'function') reconcileProgressWithResultCards();

  // 3. Restore persisted filter selections
  const savedSub = localStorage.getItem('filter-subject');
  const savedYr = localStorage.getItem('filter-year');
  const savedStatus = localStorage.getItem('filter-status');
  const savedDiff = localStorage.getItem('filter-diff');

  const subSelect = document.getElementById('filter-subject');
  const yrSelect = document.getElementById('filter-year');
  const statusSelect = document.getElementById('filter-status');
  const diffSelect = document.getElementById('filter-diff');

  if (savedSub && subSelect && Array.from(subSelect.options).some(o => o.value === savedSub)) {
    subSelect.value = savedSub;
  }
  if (savedYr && yrSelect && Array.from(yrSelect.options).some(o => o.value === savedYr)) {
    yrSelect.value = savedYr;
  }
  if (savedStatus && statusSelect && Array.from(statusSelect.options).some(o => o.value === savedStatus)) {
    statusSelect.value = savedStatus;
  }
  if (savedDiff && diffSelect && Array.from(diffSelect.options).some(o => o.value === savedDiff)) {
    diffSelect.value = savedDiff;
  }

  // 4. Render initial components
  updateStatsAndBar();
  if (typeof homeStatusInit === 'function') homeStatusInit();
  renderQuestions();
  if (typeof renderAnswerCorrectionReviewSection === 'function') {
    try { renderAnswerCorrectionReviewSection(); } catch (_) { /* optional section */ }
  }
  if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
  if (typeof initTodayTask === 'function') initTodayTask();
  if (typeof renderBackupNudge === 'function') renderBackupNudge();
  initPaneResizer();
  handleUrlHashRouting();

  // 5. v1.3.10: ask the browser to keep our storage, and take today's automatic snapshot (async, never blocks).
  if (typeof snapshotInitAuto === 'function') {
    try { snapshotInitAuto(); } catch (_) { /* snapshots never break startup */ }
  }

  // 6. v1.6.0: cloud sync (only when a token was connected on this device): pull on open, debounced push after changes.
  if (typeof cloudSyncInit === 'function') {
    try { cloudSyncInit(); } catch (_) { /* sync never breaks startup */ }
  }
});

// Another tab changed shared data: reload the in-memory copy so this tab never writes stale state back over it.
// key === null means the storage was cleared, so every store is reloaded.
function syncStoresFromStorageEvent(event) {
  try {
    if (event && event.storageArea && typeof localStorage !== 'undefined' && event.storageArea !== localStorage) return;
    const key = event ? event.key : null;
    const all = key === null || key === undefined;
    let touched = false;
    if ((all || key === 'EE_EXAM_TODAY_TASK_V1') && typeof todayTaskRefresh === 'function') {
      todayTaskRefresh();
      if (typeof renderTodayTaskCard === 'function') renderTodayTaskCard();
      touched = true;
    }
    if ((all || key === 'EE_EXAM_RECALL_V1') && typeof initRecallStore === 'function') {
      initRecallStore();
    }
    if ((all || key === SM2_STORAGE_KEY) && typeof initSM2Store === 'function') {
      initSM2Store();
      touched = true;
    }
    if ((all || key === STORAGE_KEY || key === STARRED_KEY || /_EXAM_(PROGRESS|STARRED)_V1$/.test(String(key)))
      && typeof reloadProgressState === 'function') {
      reloadProgressState();
      touched = true;
    }
    if (touched && typeof updateStatsAndBar === 'function') updateStatsAndBar();
  } catch (_) { /* cross-tab sync is best effort */ }
}

window.addEventListener('storage', syncStoresFromStorageEvent);
// (cloudSyncInit registers its own storage listener for the sync key.)

window.addEventListener('hashchange', handleUrlHashRouting);

// Keep the header one-liner current after any saved result card.
window.addEventListener('result-card-saved', () => {
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
});
