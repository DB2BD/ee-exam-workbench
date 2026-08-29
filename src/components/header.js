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

  const barMastered = document.getElementById('bar-mastered');
  const barReview = document.getElementById('bar-review');
  const barUnstarted = document.getElementById('bar-unstarted');
  const barPct = document.getElementById('stat-pct');

  if (barMastered && total > 0) barMastered.style.width = `${(mastered / total) * 100}%`;
  if (barReview && total > 0) barReview.style.width = `${(review / total) * 100}%`;
  if (barUnstarted && total > 0) barUnstarted.style.width = `${(unstarted / total) * 100}%`;
  if (barPct) barPct.innerText = `${pct}%`;
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
}

function closeBackupModal() {
  const modal = document.getElementById('backup-modal');
  if (modal) modal.classList.remove('show');
}

function copyBackupToClipboard() {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea) return;
  textarea.select();
  navigator.clipboard.writeText(textarea.value).then(() => {
    showToast("📋 已複製 JSON 備份代碼至剪貼簿！");
  });
}

function applyImportedBackupJSON() {
  const textarea = document.getElementById('backup-json-textarea');
  if (!textarea || !textarea.value.trim()) return;

  const res = typeof importUserDataJSON === 'function' ? importUserDataJSON(textarea.value.trim()) : { success: false, error: 'import handler unavailable' };
  if (res.success) {
    updateStatsAndBar();
    renderQuestions();
    closeBackupModal();
    showToast(`📥 成功還原 ${res.count} 筆進度與 SM-2 複習週期！`);
  } else {
    alert(`❌ 匯入失敗：${res.error || '無效的 JSON 格式'}`);
  }
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
      try {
        const res = typeof importUserDataJSON === 'function' ? importUserDataJSON(event.target.result) : null;
        if (!res || res.success) {
          updateStatsAndBar();
          renderQuestions();
          showToast("📥 備考進度與 SM-2 排程已成功匯入還原！");
        } else {
          alert(`❌ 匯入失敗：${res.error}`);
        }
      } catch (err) {
        alert("❌ 匯入失敗：檔案格式不正確！");
      }
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
