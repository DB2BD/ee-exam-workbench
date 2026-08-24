// src/main.js
/**
 * Main Application Orchestrator & Entry Point.
 */

function switchTab(tabId) {
  document.querySelectorAll('.main-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.style.display = 'none');

  const activeBtn = document.getElementById('tab-btn-' + tabId);
  const activePane = document.getElementById('tab-pane-' + tabId);

  if (activeBtn) activeBtn.classList.add('active');
  if (activePane) activePane.style.display = 'block';

  if (tabId === 'dag' && typeof renderDagGraphVisualizer === 'function') {
    renderDagGraphVisualizer();
  }
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
      if (typeof openSolutionModal === 'function') openSolutionModal(null, solLink, qid, qnum);
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

// Global DOM Content Loaded Bootstrap
document.addEventListener('DOMContentLoaded', () => {
  // Theme initialization
  const savedTheme = localStorage.getItem('ee_theme_preference');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.innerText = savedTheme === 'dark' ? '☀️ 亮色模式' : '🌙 暗色模式';
  }

  // Restore filters
  const savedSub = localStorage.getItem('filter-subject');
  const savedYr = localStorage.getItem('filter-year');
  const savedStatus = localStorage.getItem('filter-status');
  const savedDiff = localStorage.getItem('filter-diff');

  if (savedSub && document.getElementById('filter-subject')) document.getElementById('filter-subject').value = savedSub;
  if (savedYr && document.getElementById('filter-year')) document.getElementById('filter-year').value = savedYr;
  if (savedStatus && document.getElementById('filter-status')) document.getElementById('filter-status').value = savedStatus;
  if (savedDiff && document.getElementById('filter-diff')) document.getElementById('filter-diff').value = savedDiff;

  // Restore category
  const savedCat = localStorage.getItem('exam_category_tab') || 'PE';
  switchExamCategory(savedCat);

  // Render initial components
  updateFilterDropdownsForCategory();
  updateStatsAndBar();
  renderQuestions();
  renderLayers();
  renderTopTopics();
  initPaneResizer();
  handleUrlHashRouting();
});

window.addEventListener('hashchange', handleUrlHashRouting);
