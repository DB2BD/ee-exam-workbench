// src/components/mockExamTimer.js
/**
 * 120-Minute Full Mock Exam System 2.0 & Step-Marking Rubric
 * ==========================================================
 * Features:
 * 1. 120-minute Countdown Timer with localStorage persistence & wake-up recovery.
 * 2. Exam Pacing Ribbon (25 mins per question + 20 mins final audit).
 * 3. Step-by-Step Marking Rubric (4-tier scoring for professional essay exams).
 * 4. Mock Exam History Storage & Scorecard generation.
 */

const MOCK_EXAM_TIMER_DURATION_SECONDS = 120 * 60;
const MOCK_EXAM_TIMER_STORAGE_KEY = 'EE_MOCK_EXAM_TIMER_V1';
const MOCK_EXAM_HISTORY_STORAGE_KEY = 'EE_MOCK_EXAM_HISTORY_V1';

let examTimerSeconds = MOCK_EXAM_TIMER_DURATION_SECONDS;
let examTimerInterval = null;
let examTimerRunning = false;
let examTimerDeadlineMs = null;
let examTimerCompleted = false;
let examTimerWarningShown = false;
let examTimerExamKey = null;

let currentLoadedMockExam = null;

function formatTime(secs) {
  const safeSecs = Math.max(0, Math.floor(Number(secs) || 0));
  const m = Math.floor(safeSecs / 60);
  const s = safeSecs % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/**
 * Returns the recommended pacing stage based on remaining seconds.
 */
function getMockExamPacingInfo(secondsRemaining) {
  const s = Math.max(0, Number(secondsRemaining) || 0);
  const elapsed = MOCK_EXAM_TIMER_DURATION_SECONDS - s;
  const elapsedMins = elapsed / 60;

  // Same timeline as docs/上榜考場120分鐘得分節奏.md (5 + 90 + 17 + 8).
  if (elapsedMins < 5) {
    return { stage: 1, label: '掃卷 (0~5分)', hint: '看完全部題目與小題，題號旁標 A／B／C；不開始長算式', color: '#4a7c8f' };
  } else if (elapsedMins < 95) {
    return { stage: 2, label: '第一輪 (5~95分)', hint: '先 A 再 B 後 C；每配分最多 0.9 分鐘，卡 8 分鐘留下起手式就換題', color: '#4a7c8f' };
  } else if (elapsedMins < 112) {
    return { stage: 3, label: '搶分輪 (95~112分)', hint: '補配分最高且下一步已知道的題；不救完全沒有起手式的題', color: '#d49e35' };
  } else {
    return { stage: 4, label: '🚨 收尾 (最後 8 分鐘)', hint: '補題號、小題結論、單位、方向、相角；不開新推導', color: '#b85d58' };
  }
}

function updateTimerDisplay() {
  if (typeof document === 'undefined') return;
  const el = document.getElementById('exam-timer');
  if (el) el.innerText = formatTime(examTimerSeconds);

  const pacingEl = document.getElementById('exam-pacing-indicator');
  if (pacingEl) {
    const pacing = getMockExamPacingInfo(examTimerSeconds);
    pacingEl.innerHTML = `<span style="color: ${pacing.color}; font-weight: 700;">⏱️ 配速建議：${pacing.label}</span> · <small style="color: var(--muted);">${pacing.hint}</small>`;
  }
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
    // Storage quota or private mode fallback
  }
}

function setExamTimerToggleButton() {
  if (typeof document === 'undefined') return;
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
  showToast('⏰ 考試時間結束！請停止作答，準備進行步驟自評。');

  // Trigger self-grading rubric if exam questions are loaded
  if (currentLoadedMockExam && currentLoadedMockExam.questions && currentLoadedMockExam.questions.length > 0) {
    setTimeout(() => {
      openMockGradingModal();
    }, 1200);
  }
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

/**
 * Loads mock exam questions and initializes the pacing ribbon.
 */
function loadMockExam() {
  const subjSelect = document.getElementById('exam-select-subj');
  const yrSelect = document.getElementById('exam-select-yr');
  if (!subjSelect || !yrSelect) return;

  const sid = subjSelect.value;
  const yr = yrSelect.value;
  const container = document.getElementById('mock-exam-questions');
  if (!container) return;

  const activeList = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
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

  const meta = typeof getSubjectMeta === 'function' ? getSubjectMeta(sid) : { name: sid, icon: '📋' };
  currentLoadedMockExam = {
    subjectId: sid,
    subjectName: meta.name,
    subjectIcon: meta.icon,
    year: yr,
    questions: targetQuestions,
    loadedAt: Date.now()
  };

  const pacing = getMockExamPacingInfo(examTimerSeconds);

  container.innerHTML = `
    <div class="mock-exam-header-card" style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; margin-bottom: 20px; box-shadow: var(--shadow);">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
          <h3 style="color: var(--accent-dark); margin-bottom: 6px; font-size: 1.25rem;">
            📋 模考試卷：${meta.icon} ${meta.name}（${yr === 'random' ? '隨機 4 題全真模考' : yr + ' 年全卷'}）
          </h3>
          <p style="font-size: 0.9rem; color: var(--muted); margin-bottom: 8px;">
            共 ${targetQuestions.length} 道大題 · 滿分 100 分 · 請於 120 分鐘內於白紙獨立推導作答
          </p>
          <div id="exam-pacing-indicator" style="background: var(--bg-secondary); padding: 6px 12px; border-radius: var(--radius-sm); display: inline-block;">
            <span style="color: ${pacing.color}; font-weight: 700;">⏱️ 配速建議：${pacing.label}</span> · <small style="color: var(--muted);">${pacing.hint}</small>
          </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button type="button" class="btn-sol" style="background: var(--warn); color: white;" onclick="openMockGradingModal()">
            🏁 提前交卷與步驟自評
          </button>
        </div>
      </div>
    </div>

    <div class="qlist">
      ${targetQuestions.map((q, idx) => {
        const [qid, qsid, qyr, qnum, topic, tags, solLink, pdfLink] = q;
        const renderTopic = typeof renderQuestionTopic === 'function' ? renderQuestionTopic(topic) : topic;
        return `
          <div class="qcard" style="border-left: 4px solid var(--accent); margin-bottom: 16px;">
            <div class="qhead">
              <span class="qid">第 ${idx + 1} 大題 (${qid})</span>
              <span style="font-weight: 700; color: var(--accent-dark);">配分以官方題目為準 · 第一輪每配分最多 0.9 分鐘</span>
            </div>
            <div class="qtopic">${renderTopic}</div>
            <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
              <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, {mode: 'browse'})" class="btn-sol">📝 檢視標準推導解答</button>
              <a href="${pdfLink}" target="_blank" class="btn-pdf">📄 查看官方 PDF 原題</a>
            </div>
          </div>
        `;
      }).join('')}
    </div>

    <!-- Past Mock History Section -->
    <div id="mock-history-container" style="margin-top: 36px;">
      ${renderMockExamHistoryListHtml()}
    </div>
  `;

  const category = typeof currentExamCategory === 'undefined' ? 'PE' : currentExamCategory;
  prepareExamTimerForExam(`${category}:${sid}:${yr}`);
  showToast('📑 模考試卷已載入，準備好後點擊開始計時！');
}

/**
 * Standard Step-Marking Rubric for a 25-point essay question.
 */
const DEFAULT_RUBRIC_STEPS = [
  { id: 'step_model', label: '① 系統假設與等效模型建立', maxPts: 6, desc: '畫出正確電路圖/相量圖/系統邊界，列出初始條件' },
  { id: 'step_deriv', label: '② 核心公式列式與符號化簡推導', maxPts: 8, desc: '公式引用無誤，符號推導邏輯嚴謹無跳步' },
  { id: 'step_calc', label: '③ 數值代入、小數精度與正確單位', maxPts: 8, desc: '數值計算無誤，標明單位 (kW/kVA/Ω/A/pu)，相角符號正確' },
  { id: 'step_audit', label: '④ 防坑提醒與合理性檢核', maxPts: 3, desc: '檢核邊界極值、功率因數正負、方向定義一致性' }
];

/**
 * Opens Step-Marking Rubric Modal for self-grading.
 */
function openMockGradingModal() {
  if (!currentLoadedMockExam || !currentLoadedMockExam.questions || currentLoadedMockExam.questions.length === 0) {
    showToast('⚠️ 請先載入模考試卷');
    return;
  }

  let modal = document.getElementById('mock-grading-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mock-grading-modal';
    modal.className = 'modal-backdrop';
    document.body.appendChild(modal);
  }

  const questions = currentLoadedMockExam.questions;
  const questionsHtml = questions.map((q, qIdx) => {
    const qid = q[0];
    const qnum = q[3];
    return `
      <div class="rubric-question-card" style="border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 16px; background: var(--surface);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h4 style="color: var(--accent-dark); margin: 0;">第 ${qIdx + 1} 大題 (${qid}) · 配分 25 分</h4>
          <span style="font-weight: 700; color: var(--accent);" id="q-subtotal-${qIdx}">得分：25 / 25</span>
        </div>
        <div class="rubric-steps-grid">
          ${DEFAULT_RUBRIC_STEPS.map((step, sIdx) => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px dashed var(--line);">
              <div>
                <strong>${step.label} (${step.maxPts}分)</strong>
                <div style="font-size: 0.8rem; color: var(--muted);">${step.desc}</div>
              </div>
              <div style="display: flex; align-items: center; gap: 6px;">
                <input type="number" min="0" max="${step.maxPts}" value="${step.maxPts}"
                  data-qidx="${qIdx}" data-sidx="${sIdx}" class="rubric-score-input"
                  oninput="updateMockRubricTotalScore()"
                  style="width: 55px; text-align: center; padding: 4px; border: 1px solid var(--line-strong); border-radius: 4px;">
                <span style="font-size: 0.85rem; color: var(--muted);">/ ${step.maxPts}</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');

  modal.innerHTML = `
    <div class="modal-content" style="max-width: 720px; max-height: 90vh; overflow-y: auto;">
      <div class="modal-header">
        <h3>📋 模考成績單與申論步驟分自評尺規（滿分 100 分）</h3>
        <button type="button" class="btn-close" onclick="closeMockGradingModal()">✕</button>
      </div>
      <div class="modal-body">
        <div style="background: var(--bg-secondary); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 0.9rem; color: var(--muted);">本次模考：${currentLoadedMockExam.subjectIcon} ${currentLoadedMockExam.subjectName}（${currentLoadedMockExam.year} 年）</div>
            <div style="font-size: 0.85rem; color: var(--muted);">耗時：${formatTime(MOCK_EXAM_TIMER_DURATION_SECONDS - examTimerSeconds)}</div>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 0.85rem; color: var(--muted);">自評總分</div>
            <div id="rubric-grand-total" style="font-size: 1.8rem; font-weight: 800; color: var(--success);">100 / 100</div>
          </div>
        </div>
        ${questionsHtml}
      </div>
      <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center;">
        <span id="rubric-pass-status" style="font-weight: 700; color: var(--success);">🎉 達到專技高考及格標準 (>= 60 分)</span>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn-pdf" onclick="closeMockGradingModal()">取消</button>
          <button type="button" class="btn-sol" onclick="commitMockGradingResult()">💾 保存成績並結算</button>
        </div>
      </div>
    </div>
  `;

  modal.classList.add('show');
  updateMockRubricTotalScore();
}

function closeMockGradingModal() {
  const modal = document.getElementById('mock-grading-modal');
  if (modal) modal.classList.remove('show');
}

function updateMockRubricTotalScore() {
  if (!currentLoadedMockExam || !currentLoadedMockExam.questions) return 0;
  const numQuestions = currentLoadedMockExam.questions.length;
  let grandTotal = 0;

  for (let q = 0; q < numQuestions; q++) {
    let qSubtotal = 0;
    const inputs = document.querySelectorAll(`.rubric-score-input[data-qidx="${q}"]`);
    inputs.forEach(inp => {
      const val = Math.max(0, Math.min(Number(inp.max) || 25, Number(inp.value) || 0));
      qSubtotal += val;
    });
    const subEl = document.getElementById(`q-subtotal-${q}`);
    if (subEl) subEl.innerText = `得分：${qSubtotal} / 25`;
    grandTotal += qSubtotal;
  }

  const grandEl = document.getElementById('rubric-grand-total');
  if (grandEl) grandEl.innerText = `${grandTotal} / 100`;

  const statusEl = document.getElementById('rubric-pass-status');
  if (statusEl) {
    if (grandTotal >= 60) {
      statusEl.style.color = 'var(--success)';
      statusEl.innerText = '🎉 達到專技高考及格標準 (>= 60 分)';
    } else {
      statusEl.style.color = 'var(--warn)';
      statusEl.innerText = `⚠️ 距離及格門檻還差 ${60 - grandTotal} 分，建議針對失分大題二刷`;
    }
  }

  return grandTotal;
}

/**
 * Commits self-grading result to localStorage history.
 */
function commitMockGradingResult() {
  const grandTotal = updateMockRubricTotalScore();
  const passed = grandTotal >= 60;
  const durationSecs = MOCK_EXAM_TIMER_DURATION_SECONDS - examTimerSeconds;

  const record = {
    id: `MOCK_${Date.now()}`,
    date: new Date().toISOString(),
    subjectId: currentLoadedMockExam.subjectId,
    subjectName: currentLoadedMockExam.subjectName,
    subjectIcon: currentLoadedMockExam.subjectIcon,
    year: currentLoadedMockExam.year,
    durationSeconds: durationSecs,
    score: grandTotal,
    passed,
    questionsCount: currentLoadedMockExam.questions.length,
    qids: currentLoadedMockExam.questions.map(q => q[0])
  };

  saveMockExamResult(record);
  closeMockGradingModal();
  pauseExamTimer();

  // Refresh history UI
  const histContainer = document.getElementById('mock-history-container');
  if (histContainer) {
    histContainer.innerHTML = renderMockExamHistoryListHtml();
  }

  showToast(`💾 模考成績 ${grandTotal} 分已保存！${passed ? '🎉 及格！' : '持續加油！'}`);
}

function getMockExamHistory() {
  const storage = getMockExamTimerStorage();
  if (!storage) return [];
  try {
    const raw = storage.getItem(MOCK_EXAM_HISTORY_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (_) {
    return [];
  }
}

function saveMockExamResult(record) {
  const storage = getMockExamTimerStorage();
  if (!storage || !record) return;
  try {
    const history = getMockExamHistory();
    history.unshift(record);
    storage.setItem(MOCK_EXAM_HISTORY_STORAGE_KEY, JSON.stringify(history.slice(0, 50)));
  } catch (_) {
    // Storage fallback
  }
}

function renderMockExamHistoryListHtml() {
  const history = getMockExamHistory();
  if (!history || history.length === 0) {
    return `
      <div style="background: var(--bg); border: 1px dashed var(--line); border-radius: var(--radius); padding: 24px; text-align: center; color: var(--muted);">
        <h4>📊 尚無全真模考成績紀錄</h4>
        <p style="font-size: 0.85rem; margin-top: 6px;">完成一輪 120 分鐘模考並交卷自評後，此處將自動繪製成績與及格走勢。</p>
      </div>
    `;
  }

  const rowsHtml = history.slice(0, 10).map(item => {
    const passTag = item.passed
      ? '<span style="background: var(--success-light); color: var(--success); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem;">及格通過</span>'
      : '<span style="background: var(--review-light); color: var(--review); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem;">待加強</span>';
    const dateStr = item.date ? new Date(item.date).toLocaleDateString('zh-TW') : '';
    const minsTaken = Math.round(item.durationSeconds / 60);

    return `
      <tr style="border-bottom: 1px solid var(--line);">
        <td style="padding: 10px 12px;">${dateStr}</td>
        <td style="padding: 10px 12px;"><strong>${item.subjectIcon || '📋'} ${item.subjectName}</strong> (${item.year} 年)</td>
        <td style="padding: 10px 12px;">${minsTaken} 分鐘</td>
        <td style="padding: 10px 12px; font-weight: 800; font-size: 1.1rem; color: ${item.passed ? 'var(--success)' : 'var(--warn)'};">${item.score} 分</td>
        <td style="padding: 10px 12px;">${passTag}</td>
      </tr>
    `;
  }).join('');

  return `
    <div style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow);">
      <h4 style="color: var(--accent-dark); margin-bottom: 14px;">📈 歷史模考成績單與實力軌跡（近 10 次）</h4>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
          <thead>
            <tr style="background: var(--bg-secondary); text-align: left; color: var(--muted); border-bottom: 2px solid var(--line);">
              <th style="padding: 8px 12px;">日期</th>
              <th style="padding: 8px 12px;">考科與年度</th>
              <th style="padding: 8px 12px;">作答耗時</th>
              <th style="padding: 8px 12px;">自評總分</th>
              <th style="padding: 8px 12px;">及格狀態</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

loadMockExamTimerState();

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    MOCK_EXAM_TIMER_DURATION_SECONDS,
    MOCK_EXAM_TIMER_STORAGE_KEY,
    MOCK_EXAM_HISTORY_STORAGE_KEY,
    formatTime,
    getMockExamPacingInfo,
    startExamTimer,
    pauseExamTimer,
    resetExamTimer,
    updateExamTimerFromClock,
    getMockExamTimerState,
    loadMockExamTimerState,
    saveMockExamResult,
    getMockExamHistory,
    DEFAULT_RUBRIC_STEPS
  };
}
