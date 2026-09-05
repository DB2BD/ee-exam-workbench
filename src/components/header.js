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

function updateQuestionCountLabels() {
  const peCount = getQuestionCountForCategory('PE');
  const gkCount = getQuestionCountForCategory('GK');
  const total = peCount + gkCount;
  const peLabel = document.getElementById('cat-count-PE');
  const gkLabel = document.getElementById('cat-count-GK');
  const totalLabel = document.getElementById('hero-total-count');
  const statsTotalLabel = document.getElementById('stats-total-count');
  if (peLabel) peLabel.innerText = `${peCount} 題 · 66 卷`;
  if (gkLabel) gkLabel.innerText = `${gkCount} 題 · 25 卷`;
  if (totalLabel) totalLabel.innerText = `${total} 道試題`;
  if (statsTotalLabel) statsTotalLabel.innerText = total;
  return total;
}

function updateStatsAndBar() {
  updateQuestionCountLabels();
  const qList = getActiveQuestionsList();
  const total = qList.length;
  let mastered = 0, review = 0, starred = 0;

  qList.forEach(q => {
    const qid = q[0];
    const s = progressState[qid] || 0;
    if (s === 1) mastered++;
    if (s === 2) review++;
    if (starredState[qid]) starred++;
  });

  const unstarted = total - mastered - review;
  const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;

  const statTotal = document.getElementById('stat-total');
  const statMastered = document.getElementById('stat-mastered');
  const statReview = document.getElementById('stat-review');
  const statUnstarted = document.getElementById('stat-unstarted');
  const statStarred = document.getElementById('stat-starred');
  const statExams = document.getElementById('stat-exams');

  if (statTotal) statTotal.innerText = total;
  if (statMastered) statMastered.innerText = mastered;
  if (statReview) statReview.innerText = review;
  if (statUnstarted) statUnstarted.innerText = unstarted;
  if (statStarred) statStarred.innerText = starred;
  if (statExams) statExams.innerText = currentExamCategory === 'PE' ? 66 : 25;

  // SM-2 Due Flashcards count
  const dueList = typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : [];
  const statDue = document.getElementById('stat-due-flashcards');
  const statDueCard = document.getElementById('stat-due-card');
  if (statDue) statDue.innerText = dueList.length;
  if (statDueCard) {
    if (dueList.length > 0) {
      statDueCard.classList.add('has-due');
    } else {
      statDueCard.classList.remove('has-due');
    }
  }

  const barMastered = document.getElementById('bar-mastered');
  const barReview = document.getElementById('bar-review');
  const barUnstarted = document.getElementById('bar-unstarted');
  const barPct = document.getElementById('stat-pct');

  if (barMastered && total > 0) barMastered.style.width = `${(mastered / total) * 100}%`;
  if (barReview && total > 0) barReview.style.width = `${(review / total) * 100}%`;
  if (barUnstarted && total > 0) barUnstarted.style.width = `${(unstarted / total) * 100}%`;
  if (barPct) barPct.innerText = `${pct}%`;
}

function onDueFlashcardsClick() {
  if (typeof switchTab === 'function') {
    switchTab('review');
    const reviewScope = document.getElementById('review-scope');
    if (reviewScope) {
      reviewScope.value = 'due';
      if (typeof setReviewFilter === 'function') setReviewFilter('due');
    }
  }
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

function previewImportedBackupJSON() {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea || !textarea.value.trim()) {
    renderBackupPreview({ success: false, error: '請先貼上或載入備份 JSON。' });
    return { success: false, error: '請先貼上或載入備份 JSON。' };
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
  const res = typeof applyUserDataBackup === 'function'
    ? applyUserDataBackup(textarea.value.trim(), selectedMode)
    : { success: false, error: '備份還原功能尚未載入。' };
  if (res.success) {
    updateStatsAndBar();
    renderQuestions();
    if (typeof renderReviewPage === 'function') renderReviewPage();
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
  localStorage.setItem('ee_theme_preference', next);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) btn.innerText = next === 'dark' ? '☀️ 亮色模式' : '🌙 暗色模式';
}
