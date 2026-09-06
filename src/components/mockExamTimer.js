// src/components/mockExamTimer.js
/**
 * 120-Minute Full Mock Exam System & Countdown Timer.
 */

const MOCK_EXAM_TIMER_DURATION_SECONDS = 120 * 60;
const MOCK_EXAM_TIMER_STORAGE_KEY = 'EE_MOCK_EXAM_TIMER_V1';

let examTimerSeconds = MOCK_EXAM_TIMER_DURATION_SECONDS;
let examTimerInterval = null;
let examTimerRunning = false;
let examTimerDeadlineMs = null;
let examTimerCompleted = false;
let examTimerWarningShown = false;
let examTimerExamKey = null;

function formatTime(secs) {
  const safeSecs = Math.max(0, Math.floor(Number(secs) || 0));
  const m = Math.floor(safeSecs / 60);
  const s = safeSecs % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const el = document.getElementById('exam-timer');
  if (el) el.innerText = formatTime(examTimerSeconds);
}

function getMockExamTimerStorage() {
  return typeof localStorage === 'undefined' ? null : localStorage;
}

function persistMockExamTimerState() {
  const storage = getMockExamTimerStorage();
  if (!storage) return;
  try {
    storage.setItem(MOCK_EXAM_TIMER_STORAGE_KEY, JSON.stringify({
      seconds: examTimerSeconds,
      deadline: examTimerDeadlineMs,
      running: examTimerRunning,
      completed: examTimerCompleted,
      warningShown: examTimerWarningShown,
      examKey: examTimerExamKey,
      savedAt: Date.now(),
    }));
  } catch (_) {
    // 私密瀏覽或儲存空間不足時，計時仍可在目前頁面繼續。
  }
}

function setExamTimerToggleButton() {
  const toggleBtn = document.getElementById('btn-timer-toggle');
  if (toggleBtn) {
    if (examTimerCompleted) {
      toggleBtn.innerText = '⏰ 時間已到';
      toggleBtn.className = 'btn-timer reset';
      toggleBtn.onclick = null;
    } else if (examTimerRunning) {
      toggleBtn.innerText = '⏸️ 暫停計時';
      toggleBtn.className = 'btn-timer pause';
      toggleBtn.onclick = pauseExamTimer;
    } else {
      toggleBtn.innerText = examTimerSeconds === MOCK_EXAM_TIMER_DURATION_SECONDS ? '▶️ 開始計時' : '▶️ 繼續計時';
      toggleBtn.className = 'btn-timer start';
      toggleBtn.onclick = startExamTimer;
    }
  }
}

function scheduleExamTimerInterval() {
  if (examTimerInterval !== null) clearInterval(examTimerInterval);
  examTimerInterval = setInterval(() => updateExamTimerFromClock(), 1000);
}

function completeExamTimer() {
  if (examTimerCompleted) return;
  examTimerSeconds = 0;
  examTimerDeadlineMs = null;
  examTimerRunning = false;
  examTimerCompleted = true;
  clearInterval(examTimerInterval);
  examTimerInterval = null;
  updateTimerDisplay();
  persistMockExamTimerState();
  setExamTimerToggleButton();
  showToast('⏰ 考試時間結束！請停止作答。');
}

function updateExamTimerFromClock(now = Date.now()) {
  if (!examTimerRunning || examTimerDeadlineMs === null) return examTimerSeconds;
  examTimerSeconds = Math.max(0, Math.ceil((examTimerDeadlineMs - now) / 1000));
  updateTimerDisplay();
  if (examTimerSeconds <= 0) {
    completeExamTimer();
    return examTimerSeconds;
  }
  if (examTimerSeconds <= 300 && !examTimerWarningShown) {
    examTimerWarningShown = true;
    showToast('⚠️ 提醒：距離考試結束僅剩 5 分鐘！請準備收卷核算。');
  }
  persistMockExamTimerState();
  return examTimerSeconds;
}

function startExamTimer(now = Date.now()) {
  if (examTimerCompleted || examTimerSeconds <= 0) return;
  if (!examTimerRunning || examTimerInterval === null) {
    if (examTimerDeadlineMs === null || examTimerDeadlineMs <= now) {
      examTimerDeadlineMs = now + examTimerSeconds * 1000;
    }
    examTimerRunning = true;
    persistMockExamTimerState();
    setExamTimerToggleButton();
    scheduleExamTimerInterval();
  }
}

function pauseExamTimer(now = Date.now()) {
  if (!examTimerRunning) return;
  updateExamTimerFromClock(now);
  if (examTimerCompleted) return;
  clearInterval(examTimerInterval);
  examTimerInterval = null;
  examTimerRunning = false;
  examTimerDeadlineMs = null;
  persistMockExamTimerState();
  setExamTimerToggleButton();
}

function resetExamTimer(examKey = null) {
  if (examTimerInterval !== null) clearInterval(examTimerInterval);
  examTimerInterval = null;
  examTimerSeconds = MOCK_EXAM_TIMER_DURATION_SECONDS;
  examTimerDeadlineMs = null;
  examTimerRunning = false;
  examTimerCompleted = false;
  examTimerWarningShown = false;
  examTimerExamKey = examKey;
  updateTimerDisplay();
  persistMockExamTimerState();
  setExamTimerToggleButton();
}

function getMockExamTimerState() {
  return {
    seconds: examTimerSeconds,
    deadline: examTimerDeadlineMs,
    running: examTimerRunning,
    completed: examTimerCompleted,
    examKey: examTimerExamKey,
  };
}

function loadMockExamTimerState(now = Date.now()) {
  const storage = getMockExamTimerStorage();
  if (!storage) {
    updateTimerDisplay();
    setExamTimerToggleButton();
    return false;
  }
  let saved;
  try {
    const raw = storage.getItem(MOCK_EXAM_TIMER_STORAGE_KEY);
    saved = raw ? JSON.parse(raw) : null;
  } catch (_) {
    saved = null;
  }
  if (!saved || !Number.isFinite(Number(saved.seconds))) {
    updateTimerDisplay();
    setExamTimerToggleButton();
    return false;
  }

  examTimerSeconds = Math.max(0, Math.min(MOCK_EXAM_TIMER_DURATION_SECONDS, Math.floor(Number(saved.seconds))));
  examTimerDeadlineMs = Number.isFinite(Number(saved.deadline)) ? Number(saved.deadline) : null;
  examTimerCompleted = Boolean(saved.completed) || examTimerSeconds === 0;
  examTimerWarningShown = Boolean(saved.warningShown);
  examTimerExamKey = saved.examKey || null;
  examTimerRunning = !examTimerCompleted && Boolean(saved.running) && examTimerDeadlineMs !== null;
  if (examTimerRunning) updateExamTimerFromClock(now);
  updateTimerDisplay();
  setExamTimerToggleButton();
  if (examTimerRunning && !examTimerCompleted) scheduleExamTimerInterval();
  return true;
}

function prepareExamTimerForExam(examKey) {
  if (examTimerExamKey !== examKey) {
    resetExamTimer(examKey);
  } else {
    updateTimerDisplay();
    setExamTimerToggleButton();
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
            <div class="qtopic">${renderQuestionTopic(topic)}</div>
            <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
              <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, {mode: 'browse'})" class="btn-sol">📝 檢視標準推導解答</button>
              <a href="${pdfLink}" target="_blank" class="btn-pdf">📄 查看官方 PDF</a>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
  const category = typeof currentExamCategory === 'undefined' ? 'PE' : currentExamCategory;
  prepareExamTimerForExam(`${category}:${sid}:${yr}`);
  showToast('📑 模考試卷已載入，準備好後點擊開始計時！');
}

loadMockExamTimerState();
