// src/components/mockExamTimer.js
/**
 * 120-Minute Full Mock Exam System & Countdown Timer.
 */

let examTimerSeconds = 120 * 60;
let examTimerInterval = null;
let examTimerRunning = false;

function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const el = document.getElementById('exam-timer');
  if (el) el.innerText = formatTime(examTimerSeconds);
}

function startExamTimer() {
  if (examTimerRunning) return;
  examTimerRunning = true;
  const toggleBtn = document.getElementById('btn-timer-toggle');
  if (toggleBtn) {
    toggleBtn.innerText = '⏸️ 暫停計時';
    toggleBtn.className = 'btn-timer pause';
    toggleBtn.onclick = pauseExamTimer;
  }
  examTimerInterval = setInterval(() => {
    if (examTimerSeconds > 0) {
      examTimerSeconds--;
      updateTimerDisplay();
      if (examTimerSeconds === 300) {
        showToast('⚠️ 提醒：距離考試結束僅剩 5 分鐘！請準備收卷核算。');
      }
    } else {
      clearInterval(examTimerInterval);
      examTimerRunning = false;
      showToast('⏰ 考試時間結束！請停止作答。');
    }
  }, 1000);
}

function pauseExamTimer() {
  if (!examTimerRunning) return;
  clearInterval(examTimerInterval);
  examTimerRunning = false;
  const toggleBtn = document.getElementById('btn-timer-toggle');
  if (toggleBtn) {
    toggleBtn.innerText = '▶️ 繼續計時';
    toggleBtn.className = 'btn-timer start';
    toggleBtn.onclick = startExamTimer;
  }
}

function resetExamTimer() {
  pauseExamTimer();
  examTimerSeconds = 120 * 60;
  updateTimerDisplay();
  const toggleBtn = document.getElementById('btn-timer-toggle');
  if (toggleBtn) {
    toggleBtn.innerText = '▶️ 開始計時';
    toggleBtn.className = 'btn-timer start';
    toggleBtn.onclick = startExamTimer;
  }
}

function loadMockExam() {
  const sid = document.getElementById('exam-select-subj').value;
  const yr = document.getElementById('exam-select-yr').value;
  const container = document.getElementById('mock-exam-questions');
  if (!container) return;

  const activeList = getActiveQuestionsList();
  if (!activeList || activeList.length === 0) return;

  let targetQuestions = [];
  if (yr === 'random') {
    const subjQuestions = activeList.filter(q => q[1] === sid);
    const shuffled = [...subjQuestions].sort(() => 0.5 - Math.random());
    targetQuestions = shuffled.slice(0, 4);
  } else {
    targetQuestions = activeList.filter(q => q[1] === sid && String(q[2]) === yr);
  }

  if (targetQuestions.length === 0) {
    container.innerHTML = '<div style="text-align:center; padding: 30px; color: var(--muted);">查無符合的試卷題目</div>';
    return;
  }

  const meta = getSubjectMeta(sid);
  container.innerHTML = `
    <div style="background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 18px; margin-bottom: 16px;">
      <h3 style="color: var(--accent-dark); margin-bottom: 6px;">📋 模考試卷：${meta.icon} ${meta.name}（${yr === 'random' ? '隨機抽 4 題模考' : yr + ' 年全卷'}）</h3>
      <p style="font-size: 0.85rem; color: var(--muted);">共 ${targetQuestions.length} 道大題 · 滿分 100 分 · 請於 120 分鐘內獨立白紙推導</p>
    </div>
    <div class="qlist">
      ${targetQuestions.map((q, idx) => {
        const [qid, qsid, qyr, qnum, topic, tags, solLink, pdfLink] = q;
        return `
          <div class="qcard" style="border-left: 4px solid var(--accent);">
            <div class="qhead">
              <span class="qid">第 ${idx + 1} 大題 (${qid})</span>
              <span style="font-weight: 700; color: var(--accent-dark);">配分：25 分</span>
            </div>
            <div class="qtopic">${topic}</div>
            <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
              <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum})" class="btn-sol">📝 檢視標準推導解答</button>
              <a href="${pdfLink}" target="_blank" class="btn-pdf">📄 查看官方 PDF</a>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
  resetExamTimer();
  showToast('📑 模考試卷已載入，準備好後點擊開始計時！');
}
