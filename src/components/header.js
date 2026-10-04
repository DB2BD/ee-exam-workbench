// src/components/header.js
/**
 * Header Stats & Progress Exporter/Importer Component.
 */

function getQuestionCountForCategory(category) {
  if (category === 'PE') {
    return typeof DB_DATA !== 'undefined' && Array.isArray(DB_DATA.questions) ? DB_DATA.questions.length : 0;
  }
  if (category === 'GK') {
    return typeof NATIONAL_EXAMS_DATA !== 'undefined' && Array.isArray(NATIONAL_EXAMS_DATA.questions) ? NATIONAL_EXAMS_DATA.questions.length : 0;
  }
  return 0;
}

// Hero subtitle is PE-only; the GK count is no longer part of the default UI.
function updateQuestionCountLabels() {
  const peCount = getQuestionCountForCategory('PE');
  const totalLabel = document.getElementById('hero-total-count');
  if (totalLabel) totalLabel.innerText = `${peCount} 題`;
  return peCount;
}

/** 「今天：<今天任務代碼或 已完成>｜到期 N 題｜<成績一行>」 */
function headerTodayLabel() {
  try {
    if (typeof todayTaskViewModel !== 'function' || typeof loadTodayTaskState !== 'function') return '—';
    const vm = todayTaskViewModel(loadTodayTaskState(), Date.now());
    if (vm.mode === 'done') return '已完成';
    if (vm.mode === 'exam-check') return '考前確認';
    if (vm.mode === 'stop') return '停止新增練習';
    return vm.code || '已完成';
  } catch (_) {
    return '—';
  }
}

function headerSummaryText() {
  let due = 0;
  try { due = typeof getDueQuestionsList === 'function' ? getDueQuestionsList().length : 0; } catch (_) { due = 0; }
  let score = '估計總分：尚無資料';
  try { if (typeof scoreboardSummaryLine === 'function') score = scoreboardSummaryLine(); } catch (_) { /* keep default */ }
  return `今天：${headerTodayLabel()}｜到期 ${due} 題｜${score}`;
}

function updateHeaderSummary() {
  const line = document.getElementById('header-summary-line');
  if (line) line.innerText = headerSummaryText();
}

// Kept under its old name: many callers refresh the header after progress changes.
function updateStatsAndBar() {
  updateQuestionCountLabels();
  updateHeaderSummary();
  if (typeof homeDueReviewRefresh === 'function') homeDueReviewRefresh();
}


function exportProgressJSON() {
  const jsonStr = typeof exportAllUserDataJSON === 'function' ? exportAllUserDataJSON() : JSON.stringify({
    version: "2.0",
    exportTime: new Date().toISOString(),
    category: currentExamCategory,
    progressState: progressState,
    starredState: starredState
  }, null, 2);

  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `電機國考備考進度_${currentExamCategory}_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("💾 備考與 SM-2 排程進度已成功匯出備份！");
}

function openBackupModal() {
  const modal = document.getElementById('backup-modal');
  const textarea = document.getElementById('backup-json-textarea');
  if (!modal) return;

  const jsonStr = typeof exportAllUserDataJSON === 'function' ? exportAllUserDataJSON() : JSON.stringify({ progressState, starredState }, null, 2);
  if (textarea) textarea.value = jsonStr;
  modal.classList.add('show');
  previewImportedBackupJSON();
}

function closeBackupModal() {
  const modal = document.getElementById('backup-modal');
  if (modal) modal.classList.remove('show');
}

function copyBackupToClipboard() {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea) return;
  textarea.select();
  const copyPromise = navigator.clipboard && navigator.clipboard.writeText
    ? navigator.clipboard.writeText(textarea.value)
    : Promise.reject(new Error('clipboard unavailable'));
  copyPromise.then(() => {
    showToast("📋 已複製 JSON 備份代碼至剪貼簿！");
  }).catch(() => {
    try {
      document.execCommand('copy');
      showToast("📋 已複製 JSON 備份代碼至剪貼簿！");
    } catch (_) {
      alert('請手動選取並複製備份內容。');
    }
  });
}

function formatBackupSummary(summary) {
  if (!summary) return '';
  const byCategory = summary.progressByCategory || {};
  const starredByCategory = summary.starredByCategory || {};
  return [
    `格式 ${summary.version || '未知'} · PE 做題 ${byCategory.PE || 0} · GK 做題 ${byCategory.GK || 0}`,
    `收藏 ${summary.starred || 0}（PE ${starredByCategory.PE || 0}／GK ${starredByCategory.GK || 0}）`,
    `SM-2 ${summary.sm2 || 0} · 主動回想 ${summary.recall || 0} · 人工章節 ${summary.manualLabels || 0}`,
    `作答結果卡紀錄 ${summary.resultCardRecords || 0} 筆 · 排程任務已完成 ${summary.todayTaskDone || 0} 項${summary.todayTaskActive ? '（含進行中任務）' : ''}`,
    `每日練習完成 ${summary.practiceCompleted || 0} 題 · ${summary.practiceSession ? '含續做進度' : '無進行中練習'} · ${summary.mockTimer ? '含模考計時' : '無模考計時'}`,
  ].join('\n');
}

function renderBackupHistory() {
  const history = document.getElementById('backup-history');
  if (!history || typeof getBackupMetadata !== 'function') return;
  const metadata = getBackupMetadata() || {};
  const format = value => value ? new Date(value).toLocaleString('zh-TW') : '尚無紀錄';
  history.innerText = `最近備份：${format(metadata.lastBackupAt)}　最近匯入：${format(metadata.lastImportAt)}`;
}

function renderBackupPreview(result) {
  const preview = document.getElementById('backup-preview');
  if (!preview) return;
  preview.classList.remove('is-valid', 'is-invalid');
  if (!result || !result.success) {
    preview.classList.add('is-invalid');
    preview.innerText = (result && result.errors ? result.errors.join('\n') : (result && result.error)) || '尚未驗證備份內容。';
    renderBackupHistory();
    return;
  }
  preview.classList.add('is-valid');
  preview.innerText = `✅ 備份可還原\n${formatBackupSummary(result.summary)}`;
  renderBackupHistory();
}

// Backup validation checks PE and GK question ids, so the lazily loaded GK data
// must be present first (no-op outside the browser and once loaded).
function backupDeferUntilGkLoaded(retry) {
  if (typeof document === 'undefined' || typeof gkDataLoaded !== 'function' || typeof ensureGkData !== 'function') return false;
  if (gkDataLoaded()) return false;
  ensureGkData().then(ok => { if (ok) retry(); else renderBackupPreview({ success: false, error: '無法載入 GK 題庫資料，暫時無法驗證備份。' }); });
  return true;
}

function previewImportedBackupJSON() {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea || !textarea.value.trim()) {
    renderBackupPreview({ success: false, error: '請先貼上或載入備份 JSON。' });
    return { success: false, error: '請先貼上或載入備份 JSON。' };
  }
  if (backupDeferUntilGkLoaded(previewImportedBackupJSON)) {
    renderBackupPreview({ success: false, error: '正在載入題庫資料以驗證備份…' });
    return { success: false, pending: true };
  }
  let result;
  try {
    const payload = JSON.parse(textarea.value.trim());
    result = typeof validateUserDataBackup === 'function'
      ? validateUserDataBackup(payload)
      : { success: false, error: '備份驗證功能尚未載入。' };
  } catch (_) {
    result = { success: false, error: '匯入失敗：JSON 格式無效，未修改任何資料。' };
  }
  renderBackupPreview(result);
  return result;
}

function applyImportedBackupJSON(mode) {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea || !textarea.value.trim()) {
    renderBackupPreview({ success: false, error: '請先貼上或載入備份 JSON。' });
    return;
  }
  const selectedMode = mode === 'merge' || mode === 'replace' ? mode : 'replace';
  if (backupDeferUntilGkLoaded(() => applyImportedBackupJSON(selectedMode))) return { success: false, pending: true };
  const res = typeof applyUserDataBackup === 'function'
    ? applyUserDataBackup(textarea.value.trim(), selectedMode)
    : { success: false, error: '備份還原功能尚未載入。' };
  if (res.success) {
    if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
    updateStatsAndBar();
    renderQuestions();
    if (typeof renderReviewPage === 'function') renderReviewPage();
    if (typeof renderAnswerCorrectionReviewSection === 'function') renderAnswerCorrectionReviewSection();
    renderBackupHistory();
    closeBackupModal();
    showToast(`📥 已${selectedMode === 'merge' ? '合併' : '取代'}還原 ${res.summary ? res.summary.progress : 0} 筆做題進度。`);
  } else {
    renderBackupPreview(res);
    alert(`❌ ${res.error || '匯入失敗：無效的 JSON 格式'}`);
  }
  return res;
}

function importProgressJSON() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".json";
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const modal = document.getElementById('backup-modal');
      const textarea = document.getElementById('backup-json-textarea');
      if (textarea) textarea.value = event.target.result;
      if (modal) modal.classList.add('show');
      previewImportedBackupJSON();
    };
    reader.readAsText(file);
  };
  input.click();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('ee_theme_preference', next); } catch (_) { /* theme still applies this session */ }
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) btn.innerText = next === 'dark' ? '☀️ 亮色模式' : '🌙 暗色模式';
}
