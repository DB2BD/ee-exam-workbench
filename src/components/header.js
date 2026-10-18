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
  // v1.4.0: the status window follows the same triggers (task card renders, saved result cards, imports, tab switches).
  if (typeof homeStatusRefresh === 'function') homeStatusRefresh();
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
  a.download = `電機國考備考進度_${currentExamCategory}_${formatLocalCalendarDate(new Date())}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("備考與 SM-2 排程進度已成功匯出備份！");
}

function backupDownloadNow() {
  exportProgressJSON();
  renderBackupNudge();
}

function renderBackupNudge() {
  const host = typeof document !== 'undefined' ? document.getElementById('backup-nudge') : null;
  if (!host) return;
  let state = { show: false };
  try {
    const meta = typeof getBackupMetadata === 'function' ? getBackupMetadata() : {};
    let snoozedUntil = 0;
    try { snoozedUntil = Number(JSON.parse(localStorage.getItem(BACKUP_NUDGE_KEY) || '{}').snoozedUntil) || 0; } catch (_) { /* no snooze */ }
    state = backupNudgeState({
      lastBackupAt: meta.lastBackupAt,
      now: Date.now(),
      hasData: backupNudgeHasData(),
      snoozedUntil,
    });
  } catch (_) { /* keep hidden */ }
  if (!state.show) { host.innerHTML = ''; return; }
  host.innerHTML = '<div class="backup-nudge" role="status"><span>' + state.text + '</span>'
    + '<span class="backup-nudge-sep">｜</span>'
    + '<button type="button" class="backup-nudge-btn" onclick="backupDownloadNow()">下載備份</button>'
    + '<button type="button" class="backup-nudge-btn backup-nudge-later" onclick="backupNudgeSnooze()">明天再說</button></div>';
}

function backupNudgeSnooze() {
  try {
    localStorage.setItem(BACKUP_NUDGE_KEY, JSON.stringify({ snoozedUntil: backupNudgeSnoozeUntil(Date.now()) }));
  } catch (_) { /* snooze is best effort */ }
  renderBackupNudge();
}

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  window.addEventListener('focus', renderBackupNudge);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') renderBackupNudge();
  });
}

function openBackupModal() {
  const modal = document.getElementById('backup-modal');
  const textarea = document.getElementById('backup-json-textarea');
  if (!modal) return;

  const jsonStr = typeof exportAllUserDataJSON === 'function' ? exportAllUserDataJSON() : JSON.stringify({ progressState, starredState }, null, 2);
  if (textarea) textarea.value = jsonStr;
  modal.classList.add('show');
  previewImportedBackupJSON();
  renderSnapshotList();
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
    showToast("已複製 JSON 備份代碼至剪貼簿！");
  }).catch(() => {
    try {
      document.execCommand('copy');
      showToast("已複製 JSON 備份代碼至剪貼簿！");
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
  preview.innerText = `備份可還原\n${formatBackupSummary(result.summary)}`;
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

// 選擇檔案匯入: load a downloaded backup .json into the textarea and validate it; nothing is written
// until the user picks 合併還原 or 取代還原.
function loadBackupFile(input) {
  const file = input && input.files && input.files[0];
  if (!file) return Promise.resolve(null);
  const textarea = document.getElementById('backup-json-textarea');
  const nameLabel = document.getElementById('backup-file-name');
  const read = typeof file.text === 'function'
    ? file.text()
    : new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ''));
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  return read.then(text => {
    if (textarea) textarea.value = text;
    if (nameLabel) nameLabel.innerText = `已載入：${file.name}`;
    return previewImportedBackupJSON();
  }).catch(() => {
    const res = { success: false, error: `無法讀取檔案「${file.name}」，未修改任何資料。` };
    if (nameLabel) nameLabel.innerText = '檔案讀取失敗';
    renderBackupPreview(res);
    return res;
  }).finally(() => { input.value = ''; });
}

// The 成績 tab is built when it is opened; after an import it must be redrawn if it is the visible one.
function renderScoreboardIfVisible() {
  try {
    const pane = document.getElementById('tab-pane-scoreboard');
    const host = document.getElementById('scoreboard-container');
    if (!pane || !host || typeof renderScoreboard !== 'function') return;
    if (pane.style.display === 'none') return;
    renderScoreboard(host);
  } catch (_) { /* optional refresh */ }
}

// ---- 自動快照 (v1.3.10) ---------------------------------------------------

const SNAPSHOT_CONFIRM_MS = 3000;
let snapshotArmedId = null;
let snapshotArmTimer = null;

function snapshotDisarm() {
  snapshotArmedId = null;
  if (snapshotArmTimer) { clearTimeout(snapshotArmTimer); snapshotArmTimer = null; }
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.snapshot-restore.is-armed').forEach(btn => {
    btn.classList.remove('is-armed');
    btn.textContent = '還原';
  });
}

function snapshotListHtml(metas) {
  const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  if (!metas.length) return '<p class="snapshot-empty">尚無快照</p>';
  return metas.map(meta => {
    const row = snapshotRowParts(meta);
    return '<div class="snapshot-row" data-snapshot-row="' + esc(meta.id) + '">'
      + '<span class="snapshot-when">' + esc(row.when) + '</span>'
      + '<span class="snapshot-kind snapshot-kind--' + esc(meta.reason) + '">' + esc(row.kind) + '</span>'
      + '<span class="snapshot-counts">' + esc(row.counts) + '</span>'
      + '<button type="button" class="snapshot-restore" data-snapshot-id="' + esc(meta.id) + '" onclick="snapshotRestoreClick(this)">還原</button>'
      + '</div>';
  }).join('');
}

function renderSnapshotList() {
  const host = typeof document !== 'undefined' ? document.getElementById('snapshot-list') : null;
  if (!host || typeof snapshotListMeta !== 'function') return Promise.resolve();
  snapshotDisarm();
  return snapshotListMeta().then(metas => { host.innerHTML = snapshotListHtml(metas); }).catch(() => { host.innerHTML = snapshotListHtml([]); });
}

function snapshotRestoreClick(btn) {
  if (!btn || btn.disabled) return;
  const id = btn.getAttribute('data-snapshot-id');
  const step = snapshotConfirmStep(snapshotArmedId, id);
  if (!step.run) {
    snapshotDisarm();
    snapshotArmedId = step.armed;
    btn.classList.add('is-armed');
    btn.textContent = '再按一次確認還原';
    snapshotArmTimer = setTimeout(snapshotDisarm, SNAPSHOT_CONFIRM_MS);
    return;
  }
  snapshotDisarm();
  btn.disabled = true;
  const fail = res => { btn.disabled = false; renderBackupPreview(res); };
  // Validation checks PE and GK ids, so the lazily loaded GK data must be present first.
  const gkReady = typeof gkDataLoaded === 'function' && typeof ensureGkData === 'function' && !gkDataLoaded()
    ? ensureGkData() : Promise.resolve(true);
  gkReady
    .then(ok => ok ? snapshotRestore(id) : { success: false, error: '無法載入 GK 題庫資料，暫時無法驗證備份。' })
    .then(res => {
      if (res && res.success) { location.reload(); return; }
      fail(res || { success: false, error: '匯入失敗：JSON 格式無效，未修改任何資料。' });
    })
    .catch(() => fail({ success: false, error: '匯入失敗：寫入本機儲存空間時發生錯誤，已回復原資料。' }));
}

function applyImportedBackupJSON(mode) {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea || !textarea.value.trim()) {
    renderBackupPreview({ success: false, error: '請先貼上或載入備份 JSON。' });
    return;
  }
  const selectedMode = mode === 'merge' || mode === 'replace' ? mode : 'replace';
  if (backupDeferUntilGkLoaded(() => applyImportedBackupJSON(selectedMode))) return { success: false, pending: true };
  // v1.3.10: read the current data into a before-import snapshot now (synchronously, before anything is
  // written); it is only saved once the import succeeds.
  let preImport = null;
  try { if (typeof snapshotCapture === 'function') preImport = snapshotCapture('before-import'); } catch (_) { preImport = null; }
  const res = typeof applyUserDataBackup === 'function'
    ? applyUserDataBackup(textarea.value.trim(), selectedMode)
    : { success: false, error: '備份還原功能尚未載入。' };
  if (res.success) {
    try { if (preImport && typeof snapshotSaveCaptured === 'function') snapshotSaveCaptured(preImport).catch(() => {}); } catch (_) { /* snapshots never block an import */ }
    if (typeof initDailyPracticeHome === 'function') initDailyPracticeHome();
    updateStatsAndBar();
    renderQuestions();
    renderScoreboardIfVisible();
    if (typeof renderReviewPage === 'function') renderReviewPage();
    if (typeof renderAnswerCorrectionReviewSection === 'function') renderAnswerCorrectionReviewSection();
    renderBackupHistory();
    closeBackupModal();
    showToast(`已${selectedMode === 'merge' ? '合併' : '取代'}還原 ${res.summary ? res.summary.progress : 0} 筆做題進度。`);
  } else {
    renderBackupPreview(res);
    alert(`${res.error || '匯入失敗：無效的 JSON 格式'}`);
  }
  return res;
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('ee_theme_preference', next); } catch (_) { /* theme still applies this session */ }
  const btn = document.getElementById('theme-toggle-btn');
  if (btn && typeof themeButtonLabel === 'function') btn.innerHTML = themeButtonLabel(next);
}
