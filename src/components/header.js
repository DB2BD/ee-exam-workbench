// src/components/header.js
/**
 * Header Stats & Progress Exporter/Importer Component.
 */

function updateStatsAndBar() {
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
  const data = {
    version: "2.0",
    exportTime: new Date().toISOString(),
    category: currentExamCategory,
    progressState: progressState,
    starredState: starredState
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `電機技師備考進度_${currentExamCategory}_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("💾 備考進度已成功匯出備份！");
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
        const imported = JSON.parse(event.target.result);
        if (imported.progressState) progressState = imported.progressState;
        if (imported.starredState) starredState = imported.starredState;
        saveProgress();
        updateStatsAndBar();
        renderQuestions();
        showToast("📥 備考進度已成功匯入還原！");
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
