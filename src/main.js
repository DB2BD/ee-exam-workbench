// src/main.js
/**
 * Main Application Orchestrator & Entry Point.
 */

function switchTab(tabId) {
  // Only the panes that still exist in the shell are routable (今天 / 模考 / 成績 / 題庫瀏覽).
  const activePane = document.getElementById('tab-pane-' + tabId);
  if (!activePane) return;
  document.querySelectorAll('.main-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');

  // A tool selected from the compact 更多 menu should leave the menu closed, so
  // the selected pane (not the menu overlay) gets the user's focus.
  const moreToolsMenu = document.getElementById('more-tools-menu');
  if (moreToolsMenu) {
    moreToolsMenu.open = false;
    moreToolsMenu.classList.toggle('has-active', tabId === 'questions');
  }

  const activeBtn = document.getElementById('tab-btn-' + tabId);
  if (activeBtn) activeBtn.classList.add('active');
  activePane.style.display = 'block';

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
  renderQuestions();
  if (typeof renderAnswerCorrectionReviewSection === 'function') {
    try { renderAnswerCorrectionReviewSection(); } catch (_) { /* optional section */ }
  }
  if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
  if (typeof initTodayTask === 'function') initTodayTask();
  if (typeof renderBackupNudge === 'function') renderBackupNudge();
  initPaneResizer();
  handleUrlHashRouting();
});

window.addEventListener('hashchange', handleUrlHashRouting);

// Keep the header one-liner current after any saved result card.
window.addEventListener('result-card-saved', () => {
  if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
});
