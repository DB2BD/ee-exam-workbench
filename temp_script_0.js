
  // --- LocalStorage State Management ---
  const STORAGE_KEY = 'EE_EXAM_PROGRESS_V1';
  const STARRED_KEY = 'EE_EXAM_STARRED_V1';
  const THEME_KEY = 'EE_EXAM_THEME_V1';

  let currentExamCategory = localStorage.getItem('exam_category_tab') || 'PE';
  let nationalExamsLoaded = false;
  let modalHistoryStack = [];

  let progressState = {};
  let starredState = {};
  let currentFilteredQids = [];
  let currentModalQid = '';

  function reloadProgressState() {
    const sKey = currentExamCategory === 'PE' ? STORAGE_KEY : `${currentExamCategory}_EXAM_PROGRESS_V1`;
    const stKey = currentExamCategory === 'PE' ? STARRED_KEY : `${currentExamCategory}_EXAM_STARRED_V1`;
    try { progressState = JSON.parse(localStorage.getItem(sKey) || '{}'); } catch (e) { progressState = {}; }
    try { starredState = JSON.parse(localStorage.getItem(stKey) || '{}'); } catch (e) { starredState = {}; }
  }
  reloadProgressState();

  // --- Theme Controller ---
  function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(THEME_KEY, next);
    showToast(`🌓 已切換為 ${next === 'dark' ? '深色午夜' : '莫蘭迪亮色'} 主題`);
  }
  initTheme();

  function saveProgress() {
    const sKey = currentExamCategory === 'PE' ? STORAGE_KEY : `${currentExamCategory}_EXAM_PROGRESS_V1`;
    const stKey = currentExamCategory === 'PE' ? STARRED_KEY : `${currentExamCategory}_EXAM_STARRED_V1`;
    try { localStorage.setItem(sKey, JSON.stringify(progressState)); } catch (e) {}
    try { localStorage.setItem(stKey, JSON.stringify(starredState)); } catch (e) {}
    updateStatsAndBar();
  }

  function setStatus(qid, status) {
    progressState[qid] = status;
    saveProgress();
    renderQuestions();
    updateModalStatusButtons(qid);
  }

  function toggleStar(qid, event) {
    if (event) event.stopPropagation();
    if (starredState[qid]) delete starredState[qid];
    else starredState[qid] = true;
    saveProgress();
    renderQuestions();
    updateModalStatusButtons(qid);
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.style.display = 'block';
    setTimeout(() => { t.style.display = 'none'; }, 2600);
  }

  // --- Dynamic Loader for National Exams (TICKET-04) ---
  function loadNationalExamsScript(callback) {
    if (typeof NATIONAL_EXAMS_DATA !== 'undefined' && typeof NATIONAL_BUNDLED_MD !== 'undefined') {
      nationalExamsLoaded = true;
      if (callback) callback();
      return;
    }
    let loadedCount = 0;
    const checkDone = () => {
      loadedCount++;
      if (loadedCount >= 2) {
        nationalExamsLoaded = true;
        if (callback) callback();
      }
    };
    const s1 = document.createElement('script');
    s1.src = './national-exams-data.js';
    s1.onload = checkDone;
    s1.onerror = () => { console.warn("Failed to load national-exams-data.js"); checkDone(); };
    document.head.appendChild(s1);

    const s2 = document.createElement('script');
    s2.src = './national-solutions-bundle.js';
    s2.onload = checkDone;
    s2.onerror = () => { console.warn("Failed to load national-solutions-bundle.js"); checkDone(); };
    document.head.appendChild(s2);
  }

  function getActiveQuestionsList() {
    if (currentExamCategory === 'PE') {
      return (typeof DB_DATA !== 'undefined' && DB_DATA.questions) ? DB_DATA.questions : [];
    } else if (currentExamCategory === 'GK') {
      if (typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.questions) {
        return NATIONAL_EXAMS_DATA.questions.filter(q => q[12] === 'GK');
      }
      return [];
    }
    return [];
  }

  function updateFilterDropdownsForCategory() {
    const yrSelect = document.getElementById('filter-year');
    const subSelect = document.getElementById('filter-subject');
    if (!yrSelect || !subSelect) return;

    if (currentExamCategory === 'GK') {
      yrSelect.innerHTML = `
        <option value="all">所有年度 (110 ~ 114 年)</option>
        <option value="114">114 年 (最新)</option>
        <option value="113">113 年</option>
        <option value="112">112 年</option>
        <option value="111">111 年</option>
        <option value="110">110 年</option>
      `;
      subSelect.innerHTML = `
        <option value="all">所有考科 (5 大考科)</option>
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04">⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
      `;
    } else {
      yrSelect.innerHTML = `
        <option value="all">所有年度 (104 ~ 114 年)</option>
        <option value="114">114 年 (最新)</option>
        <option value="113">113 年</option>
        <option value="112">112 年</option>
        <option value="111">111 年</option>
        <option value="110">110 年</option>
        <option value="109">109 年</option>
        <option value="108">108 年</option>
        <option value="107">107 年</option>
        <option value="106">106 年</option>
        <option value="105">105 年</option>
        <option value="104">104 年</option>
      `;
      subSelect.innerHTML = `
        <option value="all">所有考科 (6 大考科)</option>
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04">⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
        <option value="06">🏭 06. 工業配電</option>
      `;
    }
  }

  function switchExamCategory(catId) {
    currentExamCategory = catId;
    localStorage.setItem('exam_category_tab', catId);
    document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('on'));
    const targetTab = document.getElementById('cat-tab-' + catId);
    if (targetTab) targetTab.classList.add('on');

    updateFilterDropdownsForCategory();
    reloadProgressState();

    if (catId === 'PE') {
      updateStatsAndBar();
      renderQuestions();
      showToast('🏆 已切換至「電機工程技師」核心題庫 (318 題)');
    } else {
      if (!nationalExamsLoaded) {
        loadNationalExamsScript(() => {
          updateStatsAndBar();
          renderQuestions();
          showToast('🏛️ 已切換至「公務人員高考三級」參考題庫 (105 題)');
        });
      } else {
        updateStatsAndBar();
        renderQuestions();
        showToast('🏛️ 已切換至「公務人員高考三級」參考題庫 (105 題)');
      }
    }
  }

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

    document.getElementById('stat-total').innerText = total;
    document.getElementById('stat-mastered').innerText = mastered;
    document.getElementById('stat-review').innerText = review;
    document.getElementById('stat-starred').innerText = starred;
    if (document.getElementById('stat-exams')) {
      document.getElementById('stat-exams').innerText = currentExamCategory === 'PE' ? 66 : 25;
    }
    
    const donePercent = total > 0 ? ((mastered / total) * 100).toFixed(1) : 0;
    const reviewPercent = total > 0 ? ((review / total) * 100).toFixed(1) : 0;

    document.getElementById('bar-done').style.width = donePercent + '%';
    document.getElementById('bar-review').style.width = reviewPercent + '%';
    document.getElementById('progress-text').innerText = mastered + ' / ' + total + ' 題 (' + donePercent + '%)';
  }

  function switchTab(tabId, btn) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('on'));
    document.querySelectorAll('nav.tabs button').forEach(b => b.classList.remove('on'));
    const panel = document.getElementById(tabId);
    if (panel) panel.classList.add('on');
    if (btn) btn.classList.add('on');
  }

  function getSubjectMeta(sid) {
    if (currentExamCategory === 'GK' && typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.subjects) {
      const s = NATIONAL_EXAMS_DATA.subjects.find(s => s.id === sid);
      if (s) return s;
    }
    if (typeof DB_DATA === 'undefined' || !DB_DATA.meta || !DB_DATA.meta.subjects) {
      return { name: '考科', icon: '⚡', color: '#4a7c8f' };
    }
    return DB_DATA.meta.subjects.find(s => s.id === sid) || { name: '未知', icon: '📝', color: '#798694' };
  }

  let activeQuickFilter = 'all';
  function setQuickFilter(type, btn) {
    activeQuickFilter = type;
    document.querySelectorAll('.pills-bar .pill').forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderQuestions();
  }

  function renderQuestions() {
    const qList = getActiveQuestionsList();
    if (!qList) return;

    const query = (document.getElementById('search-box').value || '').trim().toLowerCase();
    const subFilter = document.getElementById('filter-subject').value;
    const yrFilter = document.getElementById('filter-year').value;
    const statusFilter = document.getElementById('filter-status').value;
    const diffFilter = document.getElementById('filter-diff').value;

    localStorage.setItem('filter-subject', subFilter);
    localStorage.setItem('filter-year', yrFilter);
    localStorage.setItem('filter-status', statusFilter);
    localStorage.setItem('filter-diff', diffFilter);

    const container = document.getElementById('qlist-container');
    container.innerHTML = '';

    const filtered = qList.filter(q => {
      const [qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, vstatus, ftags, hasDed] = q;
      const status = progressState[qid] || 0;
      const isStarred = !!starredState[qid];

      if (subFilter !== 'all' && sid !== subFilter) return false;
      if (yrFilter !== 'all' && String(yr) !== yrFilter) return false;
      if (diffFilter !== 'all' && String(diff) !== diffFilter) return false;

      if (statusFilter === 'starred' && !isStarred) return false;
      else if (statusFilter !== 'all' && statusFilter !== 'starred' && String(status) !== statusFilter) return false;

      if (activeQuickFilter === 'review' && status !== 2) return false;
      if (activeQuickFilter === 'starred' && !isStarred) return false;
      if (activeQuickFilter === 'dedicated' && !hasDed) return false;
      if (activeQuickFilter === 'top10') {
        const topKeywords = ['Buck', 'Boost', 'SVD', '特徵值', '對角化', '變壓器', '自耦', '感應', '短路', '故障', '接地', '配電', 'ODE', '留數', '相量', '功率'];
        const matchesTop = topKeywords.some(k => (topic + ' ' + (tags||[]).join(' ')).includes(k));
        if (!matchesTop) return false;
      }

      if (query) {
        const text = (qid + ' ' + topic + ' ' + (tags || []).join(' ') + ' ' + (ftags || []).join(' ')).toLowerCase();
        if (!text.includes(query)) return false;
      }
      return true;
    });

    currentFilteredQids = filtered.map(q => q[0]);

    if (filtered.length === 0) {
      container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--muted); font-weight: 500;">🔍 找不到符合條件的題目</div>';
      return;
    }

    filtered.forEach(q => {
      const [qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, vstatus, ftags, hasDed] = q;
      const meta = getSubjectMeta(sid);
      const curStatus = progressState[qid] || 0;
      const isStarred = !!starredState[qid];

      const card = document.createElement('div');
      card.className = 'qcard';
      
      const tagsHtml = (tags || []).map(t => `<span class="tag" onclick="filterByTag('${t}')">#${t}</span>`).join('');
      const ftagsHtml = (ftags || []).map(f => `<span class="tag" style="color:var(--accent); font-weight:600;">📐 ${f}</span>`).join('');
      const starsStr = '★'.repeat(diff || 3) + '☆'.repeat(5 - (diff || 3));

      card.innerHTML = `
        <div class="qhead">
          <div class="qid-group">
            <button class="btn-star ${isStarred ? 'starred' : ''}" onclick="toggleStar('${qid}', event)" title="收藏題目">${isStarred ? '★' : '☆'}</button>
            <span class="qid">${qid}</span>
            <span class="badge-subj" style="background: ${meta.color}18; color: ${meta.color}; border: 1px solid ${meta.color}40;">
              ${meta.icon} ${meta.name}
            </span>
            <span class="badge-diff">${starsStr}</span>
            ${hasDed ? '<span class="badge-verified">✓ 詳解已驗證</span>' : ''}
            <span style="color: var(--muted); font-size: 0.83rem; font-weight: 500;">民國 ${yr} 年 · 第 ${qnum} 題</span>
          </div>
          
          <div class="status-toggle">
            <button class="status-btn ${curStatus === 0 ? 'active-0' : ''}" onclick="setStatus('${qid}', 0)">⚪ 未開始</button>
            <button class="status-btn ${curStatus === 1 ? 'active-1' : ''}" onclick="setStatus('${qid}', 1)">🟢 已掌握</button>
            <button class="status-btn ${curStatus === 2 ? 'active-2' : ''}" onclick="setStatus('${qid}', 2)">🔴 需二刷</button>
          </div>
        </div>

        <div class="qtopic">${topic}</div>

        <div class="tags">${tagsHtml} ${ftagsHtml}</div>

        <div class="qfooter">
          <div class="btn-group">
            <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum})" class="btn-sol">📝 開啟詳細步驟推導</button>
            <a href="${pdfLink}" target="_blank" class="btn-pdf">📄 官方原題 PDF</a>
            <button onclick="promptAIGrading('${qid}')" class="btn-ai">📸 呼叫 AI 批改手寫解答</button>
            <button onclick="promptAIConcept('${qid}')" class="btn-ai" style="background:var(--accent-bg); color:var(--accent); border-color:var(--line);">💡 觀念剖析</button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  }

  function filterByTag(tag) {
    document.getElementById('search-box').value = tag;
    renderQuestions();
    showToast(`🔍 已過濾標籤: #${tag}`);
  }

  function renderLayers() {
    if (typeof DB_DATA === 'undefined' || !DB_DATA.sevenLayers) return;
    const container = document.getElementById('layers-container');
    container.innerHTML = DB_DATA.sevenLayers.map(l => `
      <div onclick="openSolutionModal(event, '${l.link}')" class="layer-card">
        <div class="layer-title">${l.title}</div>
        <div class="layer-desc">${l.desc}</div>
      </div>
    `).join('');
  }

  // --- Mock Exam Timer System ---
  let examTimerInterval = null;
  let examTimeLeft = 120 * 60; // 120 mins
  let isTimerRunning = false;

  function formatTimer(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  function startExamTimer() {
    const btn = document.getElementById('btn-timer-toggle');
    if (isTimerRunning) {
      clearInterval(examTimerInterval);
      isTimerRunning = false;
      btn.innerText = '▶️ 繼續計時';
      btn.className = 'btn-timer start';
      showToast('⏸️ 模考計時已暫停');
    } else {
      isTimerRunning = true;
      btn.innerText = '⏸️ 暫停計時';
      btn.className = 'btn-timer pause';
      showToast('⏱️ 全真 120 分鐘計時開始！');
      examTimerInterval = setInterval(() => {
        if (examTimeLeft > 0) {
          examTimeLeft--;
          document.getElementById('exam-timer').innerText = formatTimer(examTimeLeft);
        } else {
          clearInterval(examTimerInterval);
          isTimerRunning = false;
          alert('🔔 時間到！120 分鐘全真模考結束，請停筆並開始自評對答案！');
          btn.innerText = '▶️ 開始計時';
          btn.className = 'btn-timer start';
        }
      }, 1000);
    }
  }

  function resetExamTimer() {
    clearInterval(examTimerInterval);
    isTimerRunning = false;
    examTimeLeft = 120 * 60;
    document.getElementById('exam-timer').innerText = '120:00';
    const btn = document.getElementById('btn-timer-toggle');
    btn.innerText = '▶️ 開始計時';
    btn.className = 'btn-timer start';
    showToast('🔄 計時器已重設為 120:00');
  }

  function loadMockExam() {
    const sid = document.getElementById('exam-select-subj').value;
    const yr = document.getElementById('exam-select-yr').value;
    const container = document.getElementById('mock-exam-questions');

    if (typeof DB_DATA === 'undefined' || !DB_DATA.questions) return;

    let targetQuestions = [];
    if (yr === 'random') {
      const subjQuestions = DB_DATA.questions.filter(q => q[1] === sid);
      const shuffled = [...subjQuestions].sort(() => 0.5 - Math.random());
      targetQuestions = shuffled.slice(0, 4);
    } else {
      targetQuestions = DB_DATA.questions.filter(q => q[1] === sid && String(q[2]) === yr);
    }

    if (targetQuestions.length === 0) {
      container.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--muted);">查無試卷題目</div>';
      return;
    }

    const meta = getSubjectMeta(sid);
    container.innerHTML = `
      <div style="background: var(--bg); border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 16px;">
        <h3 style="color: var(--accent); margin-bottom: 6px;">📋 模考試卷：${meta.icon} ${meta.name}（${yr === 'random' ? '隨機 4 題模考' : yr + ' 年全卷'}）</h3>
        <p style="font-size: 0.85rem; color: var(--muted);">共 ${targetQuestions.length} 道大題 · 滿分 100 分 · 請於 120 分鐘內完成</p>
      </div>
      <div class="qlist">
        ${targetQuestions.map((q, idx) => {
          const [qid, qsid, qyr, qnum, topic, tags, solLink, pdfLink] = q;
          return `
            <div class="qcard" style="border-left: 4px solid var(--accent);">
              <div class="qhead">
                <span class="qid">第 ${idx + 1} 大題 (${qid})</span>
                <span style="font-weight: 700; color: var(--accent);">配分：25 分</span>
              </div>
              <div class="qtopic">${topic}</div>
              <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
                <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum})" class="btn-sol">📝 檢視標準解答與步驟</button>
                <a href="${pdfLink}" target="_blank" class="btn-pdf">📄 查看原卷 PDF</a>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
    resetExamTimer();
    showToast('📑 模考試卷已載入，準備好後點擊開始計時！');
  }

  // --- AI Prompt Generators ---
  function promptAIGrading(qid) {
    const text = `@antigravity 幫我批改 ${qid} 的手寫解答：
1. 請對照標準答案，逐小題進行步驟與計算數值核對。
2. 指出任何計算錯誤、符號誤用或單位遺漏。
3. 依國考 25 分給予估計得分與扣分點說明。
4. 提供加分建議與防坑技巧。`;
    copyPromptToClipboard(text, "📸 批改指令已複製！請回對話框貼上並拖入手寫照片！");
  }

  function promptAIConcept(qid) {
    const text = `@antigravity 請針對 ${qid} 進行核心觀念深度白話剖析：
1. 本題背後的核心物理/數學原理是什麼？
2. 考試時如何在 10 秒內識別出解題 SOP 與關鍵公式？
3. 最容易失分的陷阱點在哪裡？如何避免？`;
    copyPromptToClipboard(text, "💡 觀念剖析指令已複製！請回對話框貼上送出！");
  }

  function copyPromptToClipboard(text, successMsg) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        showToast("✨ 指令已複製到剪貼簿！");
        alert(successMsg);
      }).catch(() => { alert(text); });
    } else {
      alert(text);
    }
  }

  // --- Export / Import Progress JSON ---
  function exportProgressJSON() {
    const data = {
      version: "1.0",
      exportTime: new Date().toISOString(),
      progressState: progressState,
      starredState: starredState
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `電機技師備考進度_${new Date().toISOString().slice(0,10)}.json`;
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

  // --- Modal Viewer & Navigation ---
  function updateModalStatusButtons(qid) {
    const bar = document.getElementById('modal-status-actions');
    const navBtns = document.querySelector('.modal-nav-btns');
    if (!bar) return;

    if (!qid) {
      if (navBtns) navBtns.style.display = 'none';
      bar.innerHTML = '';
      return;
    }

    if (navBtns) navBtns.style.display = 'flex';
    const curStatus = progressState[qid] || 0;
    const isStarred = !!starredState[qid];
    const q = findQuestionRecord(qid);
    const pdfLink = q ? q[7] : '';

    const returnBtnHtml = (modalHistoryStack && modalHistoryStack.length > 0) ? `
      <button onclick="popModalHistory()" class="btn-sol" style="padding: 4px 12px; font-size: 0.82rem; background: var(--accent); color: #fff; font-weight: 700; border-radius: 6px; border: none; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" title="返回上一道查看的試題">
        🔙 返回原題 (${modalHistoryStack[modalHistoryStack.length - 1].qid})
      </button>
    ` : '';

    bar.innerHTML = `
      ${returnBtnHtml}
      ${pdfLink ? `<a href="${pdfLink}" target="_blank" class="btn-pdf" style="padding: 4px 10px; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;" title="在新分頁開啟官方考選部原題試卷 PDF">📄 官方原卷 PDF</a>` : ''}
      <button class="btn-star ${isStarred ? 'starred' : ''}" onclick="toggleStar('${qid}', event)" title="收藏題目">${isStarred ? '★' : '☆'}</button>
      <div class="status-toggle">
        <button class="status-btn ${curStatus === 0 ? 'active-0' : ''}" onclick="setStatus('${qid}', 0)">⚪ 未開始</button>
        <button class="status-btn ${curStatus === 1 ? 'active-1' : ''}" onclick="setStatus('${qid}', 1)">🟢 已掌握</button>
        <button class="status-btn ${curStatus === 2 ? 'active-2' : ''}" onclick="setStatus('${qid}', 2)">🔴 需二刷</button>
      </div>
    `;
  }

  function navModalQuestion(direction) {
    if (!currentFilteredQids.length || !currentModalQid) return;
    const idx = currentFilteredQids.indexOf(currentModalQid);
    if (idx === -1) return;
    const nextIdx = idx + direction;
    if (nextIdx >= 0 && nextIdx < currentFilteredQids.length) {
      const nextQid = currentFilteredQids[nextIdx];
      const q = findQuestionRecord(nextQid);
      if (q) {
        openSolutionModal(null, q[6], nextQid);
      }
    } else {
      showToast(direction > 0 ? "已是本清單最後一題" : "已是本清單第一題");
    }
  }

  // --- ◫ Split Screen Workspace & Resizer ---
  let isResizing = false;
  let currentModalLayout = localStorage.getItem('modal_layout_mode') || 'split';
  let currentLeftTab = localStorage.getItem('modal_left_tab_pref') || 'diagram';

  function applySavedPaneSplitRatio() {
    const leftPane = document.getElementById('modal-pane-left');
    if (!leftPane) return;
    const savedRatio = localStorage.getItem('modal_split_ratio') || '45%';
    if (currentModalLayout === 'split') {
      leftPane.style.flex = `0 0 ${savedRatio}`;
      leftPane.style.maxWidth = savedRatio;
      leftPane.style.width = savedRatio;
    } else if (currentModalLayout === 'exam-only') {
      leftPane.style.flex = '1 1 100%';
      leftPane.style.maxWidth = '100%';
      leftPane.style.width = '100%';
    }
  }

  function initPaneResizer() {
    const resizer = document.getElementById('modal-resizer');
    const container = document.getElementById('modal-split-container');
    const leftPane = document.getElementById('modal-pane-left');
    if (!resizer || !container || !leftPane) return;

    applySavedPaneSplitRatio();

    resizer.addEventListener('mousedown', (e) => {
      isResizing = true;
      resizer.classList.add('dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      const containerRect = container.getBoundingClientRect();
      const newWidth = e.clientX - containerRect.left;
      const ratio = newWidth / containerRect.width;
      if (ratio >= 0.20 && ratio <= 0.80) {
        const pct = (ratio * 100).toFixed(1) + '%';
        leftPane.style.flex = `0 0 ${pct}`;
        leftPane.style.maxWidth = pct;
        leftPane.style.width = pct;
        localStorage.setItem('modal_split_ratio', pct);
      }
    });

    document.addEventListener('mouseup', () => {
      if (isResizing) {
        isResizing = false;
        resizer.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }

  function setModalLayout(mode) {
    currentModalLayout = mode;
    localStorage.setItem('modal_layout_mode', mode);
    const content = document.getElementById('modal-content');
    if (!content) return;

    content.classList.remove('layout-split', 'layout-solution-only', 'layout-exam-only');
    content.classList.add(`layout-${mode}`);

    const btns = document.querySelectorAll('#layout-toggle-group .btn-layout');
    btns.forEach(b => b.classList.remove('on'));
    const activeBtn = document.getElementById(`btn-layout-${mode === 'split' ? 'split' : mode === 'solution-only' ? 'solution' : 'exam'}`);
    if (activeBtn) activeBtn.classList.add('on');

    applySavedPaneSplitRatio();
  }

  function switchLeftTab(tabType) {
    currentLeftTab = tabType;
    localStorage.setItem('modal_left_tab_pref', tabType);
    const tabDiag = document.getElementById('tab-left-diagram');
    const tabPdf = document.getElementById('tab-left-pdf');
    const bodyDiag = document.getElementById('left-tab-content-diagram');
    const bodyPdf = document.getElementById('left-tab-content-pdf');

    if (tabDiag && tabPdf && bodyDiag && bodyPdf) {
      if (tabType === 'diagram') {
        tabDiag.classList.add('on');
        tabPdf.classList.remove('on');
        bodyDiag.style.display = 'block';
        bodyPdf.style.display = 'none';
      } else {
        tabPdf.classList.add('on');
        tabDiag.classList.remove('on');
        bodyPdf.style.display = 'block';
        bodyDiag.style.display = 'none';
      }
    }
  }

  let currentMobileTab = 'solution'; // default to solution on mobile

  function setMobileActiveTab(tab) {
    currentMobileTab = tab;
    const container = document.getElementById('modal-split-container');
    const btnExam = document.getElementById('btn-mobile-tab-exam');
    const btnSol = document.getElementById('btn-mobile-tab-solution');
    if (!container) return;

    container.classList.remove('mobile-show-exam', 'mobile-show-solution');
    if (tab === 'exam') {
      container.classList.add('mobile-show-exam');
      if (btnExam) btnExam.classList.add('on');
      if (btnSol) btnSol.classList.remove('on');
    } else {
      container.classList.add('mobile-show-solution');
      if (btnExam) btnExam.classList.remove('on');
      if (btnSol) btnSol.classList.add('on');
    }
  }

  function toggleFx127QuickTip() {
    const drawer = document.getElementById('fx127-quick-drawer');
    if (!drawer) return;
    if (drawer.style.display === 'none' || !drawer.style.display) {
      drawer.style.display = 'block';
      drawer.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <strong style="color:var(--accent); font-size:0.9rem;">🧮 E-MORE fx-127 國考神機極速相量運算 SOP</strong>
          <button onclick="document.getElementById('fx127-quick-drawer').style.display='none'" style="background:none; border:none; cursor:pointer; color:var(--muted); font-size:1rem;">✕</button>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; font-size:0.82rem; line-height:1.6;">
          <div style="background:var(--card); padding:10px 12px; border-radius:8px; border:1px solid var(--line);">
            <strong style="color:var(--accent);">📍 直角座標轉極座標 [→rθ]</strong><br>
            <code>實部 [+] 虛部 [2ndF][i] [2ndF][→rθ]</code><br>
            ➔ 立即出幅值 $r$，按 <code>[2ndF][b]</code> 查看相角 $\theta$。
          </div>
          <div style="background:var(--card); padding:10px 12px; border-radius:8px; border:1px solid var(--line);">
            <strong style="color:var(--accent);">📍 極座標轉直角座標 [→xy]</strong><br>
            <code>幅值 [2ndF][∠] 相角 [2ndF][→xy]</code><br>
            ➔ 立即出實部 $x$，按 <code>[2ndF][b]</code> 查看虛部 $y$。
          </div>
          <div style="background:var(--card); padding:10px 12px; border-radius:8px; border:1px solid var(--line);">
            <strong style="color:var(--accent);">📍 旋轉相量對稱運算</strong><br>
            $a^2 - a = -j\sqrt{3} \approx -j1.732$<br>
            $a - a^2 = +j\sqrt{3} \approx +j1.732$
          </div>
        </div>
      `;
    } else {
      drawer.style.display = 'none';
    }
  }

  function toggleToolsMenu(e) {
    if (e) e.stopPropagation();
    const menu = document.getElementById('tools-dropdown-menu');
    const btn = document.getElementById('btn-tools-trigger');
    if (!menu) return;
    menu.classList.toggle('show');
    if (btn) btn.classList.toggle('on', menu.classList.contains('show'));
  }

  function closeToolsMenu() {
    const menu = document.getElementById('tools-dropdown-menu');
    const btn = document.getElementById('btn-tools-trigger');
    if (menu) menu.classList.remove('show');
    if (btn) btn.classList.remove('on');
  }

  document.addEventListener('click', (e) => {
    const wrap = document.querySelector('.tools-dropdown-wrap');
    if (wrap && !wrap.contains(e.target)) {
      closeToolsMenu();
    }
  });

  function openLightbox(src) {
    const overlay = document.getElementById('lightbox-overlay');
    const img = document.getElementById('lightbox-img');
    img.src = src;
    overlay.style.display = 'flex';
  }
  function closeLightbox() {
    document.getElementById('lightbox-overlay').style.display = 'none';
    document.getElementById('lightbox-img').src = '';
  }

  function closeModalDirect() {
    document.getElementById('modal-overlay').style.display = 'none';
    if (window.location.hash.startsWith('#q=')) {
      try {
        history.replaceState(null, null, window.location.pathname + window.location.search);
      } catch(e) {
        window.location.hash = '';
      }
    }
  }
  function closeModal(e) {
    if (e.target.id === 'modal-overlay') closeModalDirect();
  }

  // Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeLightbox();
      closeModalDirect();
    } else if (document.getElementById('modal-overlay').style.display === 'flex') {
      if (e.key === 'j' || e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        navModalQuestion(1);
      } else if (e.key === 'k' || e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        navModalQuestion(-1);
      } else if (e.key === 's') {
        if (currentModalQid) toggleStar(currentModalQid);
      }
    }
  });

  // --- Lightbox / Image Resolution ---
  function resolveImagePath(rawPath, basePath) {
    if (!rawPath) return '';
    const cleanName = decodeURIComponent(rawPath).replace(/^\.\//, '').trim();
    const basename = cleanName.substring(cleanName.lastIndexOf('/') + 1);

    let finalPath = '';
    if (typeof IMAGE_MAP !== 'undefined') {
      if (IMAGE_MAP[cleanName]) finalPath = IMAGE_MAP[cleanName];
      else if (IMAGE_MAP[basename]) finalPath = IMAGE_MAP[basename];
    }
    if (!finalPath && typeof NATIONAL_IMAGE_MAP !== 'undefined') {
      if (NATIONAL_IMAGE_MAP[cleanName]) finalPath = NATIONAL_IMAGE_MAP[cleanName];
      else if (NATIONAL_IMAGE_MAP[basename]) finalPath = NATIONAL_IMAGE_MAP[basename];
    }
    
    if (!finalPath) {
      if (cleanName.startsWith('依考科分類/') || cleanName.startsWith('images/') || cleanName.startsWith('📝 個人題解與錯題本/')) {
        finalPath = cleanName;
      }
    }
    return finalPath;
  }

  function findQuestionRecord(qid) {
    if (!qid) return null;
    if (typeof DB_DATA !== 'undefined' && DB_DATA.questions) {
      const q = DB_DATA.questions.find(item => item[0] === qid);
      if (q) return q;
    }
    if (typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.questions) {
      const q = NATIONAL_EXAMS_DATA.questions.find(item => item[0] === qid);
      if (q) return q;
    }
    return null;
  }

  function handleImageError(imgEl, src, caption) {
    if (!imgEl.dataset.retryLevel) {
      imgEl.dataset.retryLevel = '1';
      try {
        const encoded = encodeURI(src);
        if (encoded !== src) {
          imgEl.src = encoded;
          return;
        }
      } catch(e) {}
    } else if (imgEl.dataset.retryLevel === '1') {
      imgEl.dataset.retryLevel = '2';
      const clean = decodeURIComponent(src);
      const basename = clean.substring(clean.lastIndexOf('/') + 1);
      if (typeof IMAGE_MAP !== 'undefined' && IMAGE_MAP[basename] && IMAGE_MAP[basename] !== src) {
        imgEl.src = IMAGE_MAP[basename];
        return;
      }
    }

    const frame = imgEl.parentElement;
    if (!frame) return;
    frame.style.cursor = 'default';
    frame.onclick = null;
    frame.innerHTML = `
      <div style="padding: 20px; background: var(--bg-secondary); text-align: center; border-radius: 8px; border: 1px dashed var(--line);">
        <div style="font-size: 1.6rem; margin-bottom: 6px;">🖼️</div>
        <div style="font-weight: 700; color: var(--ink); margin-bottom: 4px;">試卷圖表：${caption}</div>
        <p style="font-size: 0.82rem; color: var(--muted); margin-bottom: 6px;">若瀏覽器受安全性限制無法直接內嵌，請點擊下方按鈕：</p>
        <p style="font-size: 0.75rem; color: var(--muted); margin-bottom: 12px; word-break: break-all;"><code>${src}</code></p>
        <a href="${src}" target="_blank" class="btn-sol" style="font-size: 0.8rem;">📄 於新分頁開啟原始圖檔</a>
      </div>
    `;
  }

  function renderLatexDirect(rawLatex, displayMode) {
    if (typeof katex !== 'undefined' && katex.renderToString) {
      try {
        return katex.renderToString(rawLatex.trim(), { displayMode: displayMode, throwOnError: false, strict: false });
      } catch (e) {
        return displayMode ? `<div class="katex-display">${rawLatex}</div>` : `<span class="katex">${rawLatex}</span>`;
      }
    }
    return rawLatex;
  }

  // --- Smart Question Section Slicer ---
  function extractQuestionSections(rawContent) {
    const lines = rawContent.split('\n');
    const sections = [];
    const numMap = { '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10 };

    // Detect heading level for questions
    let splitRegex = /^##\s+(.+)$/;
    if (lines.some(l => /^##\s+[一二三四五六七八九十]/.test(l))) {
      splitRegex = /^##\s+(.+)$/;
    } else if (lines.some(l => /^####\s+[一二三四五六七八九十]/.test(l))) {
      splitRegex = /^####\s+(.+)$/;
    } else if (lines.some(l => /^###\s+[一二三四五六七八九十]/.test(l))) {
      splitRegex = /^###\s+(.+)$/;
    }

    let currentTitle = '';
    let currentLines = [];
    let preamble = '';
    let foundFirst = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const match = line.match(splitRegex);
      if (match) {
        if (!foundFirst) {
          foundFirst = true;
        } else if (currentLines.length > 0) {
          sections.push({ title: currentTitle, text: currentLines.join('\n') });
        }
        currentTitle = match[1].trim();
        currentLines = [line];
      } else if (!foundFirst) {
        preamble += line + '\n';
      } else {
        currentLines.push(line);
      }
    }
    if (currentLines.length > 0) {
      sections.push({ title: currentTitle, text: currentLines.join('\n') });
    }

    // Filter out non-question sections (e.g. general overview, conclusion tips) if question sections exist
    const questionSections = sections.filter(sec => {
      const firstChar = sec.title.charAt(0);
      return !!numMap[firstChar] || /^(?:第\s*[1-9一二三四五六七八九十]|Q\d|[1-9]\b)/.test(sec.title);
    });

    const finalSections = questionSections.length > 0 ? questionSections : sections;

    finalSections.forEach((sec, idx) => {
      sec.index = idx + 1;
      const firstChar = sec.title.charAt(0);
      if (numMap[firstChar]) {
        sec.num = numMap[firstChar];
      } else {
        const m = sec.title.match(/(?:第\s*([1-9一二三四五六七八九十])\s*大?題|^([1-9])\b)/);
        if (m) {
          const val = m[1] || m[2];
          sec.num = numMap[val] || parseInt(val, 10) || (idx + 1);
        } else {
          sec.num = idx + 1;
        }
      }
    });

    return { sections: finalSections, preamble };
  }

  let currentModalQNum = 1;
  let currentModalFullView = false;
  let currentModalSolLink = '';

  function switchSubQuestion(qid, solLink, qnum, isFullView) {
    openSolutionModal(null, solLink, qid, qnum, isFullView);
  }

  function openSolutionModal(event, targetPath, qid, specificQNum, isFullView) {
    if (event) event.preventDefault();
    currentModalQid = qid || '';
    currentModalSolLink = targetPath;
    currentModalFullView = !!isFullView;

    // Update URL hash without breaking history
    if (currentModalQid) {
      try {
        history.replaceState(null, null, '#q=' + encodeURIComponent(currentModalQid));
      } catch(e) {
        window.location.hash = '#q=' + encodeURIComponent(currentModalQid);
      }
    }

    const overlay = document.getElementById('modal-overlay');
    const body = document.getElementById('modal-body');
    const leftPaneBody = document.getElementById('left-pane-body');
    const layoutToggleGroup = document.getElementById('layout-toggle-group');
    const subQPillsBar = document.getElementById('sub-q-pills-bar');
    const historyBackBtn = document.getElementById('modal-history-back-btn');
    const fxDrawer = document.getElementById('fx127-quick-drawer');
    if (fxDrawer) fxDrawer.style.display = 'none';

    if (!overlay || !body) return;

    // Update History Back Button in Toolbar
    if (historyBackBtn) {
      if (modalNavHistory.length > 0) {
        const prevItem = modalNavHistory[modalNavHistory.length - 1];
        historyBackBtn.style.display = 'inline-flex';
        historyBackBtn.innerHTML = `🔙 返回原題 (${prevItem.qid})`;
      } else {
        historyBackBtn.style.display = 'none';
      }
    }

    // Determine target question number (default from qid if available)
    let targetQ = 1;
    let currentExamCategory = 'ee';
    if (specificQNum === 'all') {
      currentModalFullView = true;
    } else if (typeof specificQNum === 'number') {
      targetQ = specificQNum;
      currentModalQNum = targetQ;
    } else if (qid) {
      const parts = qid.split('-');
      if (parts.length >= 4) {
        targetQ = parseInt(parts[3], 10) || 1;
        currentModalQNum = targetQ;
      }
      if (qid.startsWith('GK-')) {
        currentExamCategory = 'gk';
      }
    }

    // Try finding content from BUNDLED_MD or NATIONAL_BUNDLED_MD
    let rawContent = '';
    let basePath = '';
    const cleanPath = targetPath ? targetPath.split('#')[0] : '';
    const anchor = targetPath && targetPath.includes('#') ? targetPath.split('#')[1] : '';

    if (cleanPath) {
      const idx = cleanPath.lastIndexOf('/');
      basePath = idx !== -1 ? cleanPath.substring(0, idx + 1) : '';
    }

    if (typeof BUNDLED_MD !== 'undefined' && BUNDLED_MD[cleanPath]) {
      rawContent = BUNDLED_MD[cleanPath];
    } else if (typeof NATIONAL_BUNDLED_MD !== 'undefined' && NATIONAL_BUNDLED_MD[cleanPath]) {
      rawContent = NATIONAL_BUNDLED_MD[cleanPath];
    } else {
      for (const k in (typeof BUNDLED_MD !== 'undefined' ? BUNDLED_MD : {})) {
        if (cleanPath && (k.endsWith(cleanPath) || cleanPath.endsWith(k))) {
          rawContent = BUNDLED_MD[k];
          break;
        }
      }
      if (!rawContent && typeof NATIONAL_BUNDLED_MD !== 'undefined') {
        for (const k in NATIONAL_BUNDLED_MD) {
          if (cleanPath && (k.endsWith(cleanPath) || cleanPath.endsWith(k))) {
            rawContent = NATIONAL_BUNDLED_MD[k];
            break;
          }
        }
      }
    }

    const qRecord = findQuestionRecord(currentModalQid);

    if (rawContent) {
      const parsed = extractQuestionSections(rawContent);
      let contentToRender = rawContent;

      if (parsed.sections.length > 0) {
        if (subQPillsBar) {
          subQPillsBar.style.display = 'flex';
          subQPillsBar.innerHTML = `
            ${parsed.sections.map(sec => {
              const qidParts = currentModalQid ? currentModalQid.split('-') : [];
              const nextQid = qidParts.length >= 4 ? `${qidParts[0]}-${qidParts[1]}-${qidParts[2]}-${sec.num}` : currentModalQid;
              const isOn = !currentModalFullView && (currentModalQNum === sec.num);
              return `
                <button class="sub-q-pill ${isOn ? 'on' : ''}" onclick="switchSubQuestion('${nextQid}', '${targetPath}', ${sec.num})">
                  ⚡ 第 ${sec.num} 題
                </button>
              `;
            }).join('')}
            <button class="sub-q-pill ${currentModalFullView ? 'on' : ''}" onclick="switchSubQuestion('${currentModalQid}', '${targetPath}', 'all', true)">
              📜 展開全卷
            </button>
            <div class="tools-dropdown-wrap" style="margin-left:auto;">
              <button class="btn-tools-trigger" id="btn-tools-trigger" onclick="toggleToolsMenu(event)" title="展開/收合輔助工具選單">
                ⚡ 輔助工具 ▾
              </button>
              <div class="tools-dropdown-menu" id="tools-dropdown-menu">
                <button class="tools-menu-item" onclick="toggleFx127QuickTip(); closeToolsMenu();">
                  🧮 考場計算機按鍵 SOP
                </button>
                <button class="tools-menu-item" onclick="promptAIGrading(currentModalQid); closeToolsMenu();">
                  🤖 呼叫 AI 批改手寫解答
                </button>
                <button class="tools-menu-item" onclick="promptAIConcept(currentModalQid); closeToolsMenu();">
                  💡 AI 觀念深度剖析
                </button>
              </div>
            </div>
          `;
        }

        if (!currentModalFullView) {
          const matchedSec = parsed.sections.find(s => s.num === targetQ);
          if (matchedSec) {
            contentToRender = matchedSec.text;
          }
        }
      } else {
        if (subQPillsBar) subQPillsBar.style.display = 'none';
      }

      updateModalStatusButtons(currentModalQid);

      body.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--muted);">⚡ 正在急速載入教科書級解析...</div>';
      if (leftPaneBody) leftPaneBody.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--muted);">📄 載入試卷中...</div>';
      overlay.style.display = 'flex';
      if (window.innerWidth <= 900) {
        setMobileActiveTab(currentMobileTab || 'solution');
      }

      // Handle Non-Question Documents (Full Solution Mode)
      if (!currentModalQid) {
        setModalLayout('solution-only');
        if (layoutToggleGroup) layoutToggleGroup.style.display = 'none';
        if (subQPillsBar) subQPillsBar.style.display = 'none';
      } else {
        if (layoutToggleGroup) layoutToggleGroup.style.display = 'inline-flex';
        setModalLayout(currentModalLayout || 'split');
      }

      applySavedPaneSplitRatio();

      // Extract Images for Left Pane (only include verified existing images)
      const discoveredImages = [];
      const obsMatches = [...contentToRender.matchAll(/!\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]/g)];
      obsMatches.forEach(m => {
        const res = resolveImagePath(m[1], basePath);
        if (res) discoveredImages.push({ raw: m[1], alt: m[1], res: res });
      });
      const stdMatches = [...contentToRender.matchAll(/!\[([^\]]*)\]\(([^\)]+)\)/g)];
      stdMatches.forEach(m => {
        if (!m[2].startsWith('http')) {
          const res = resolveImagePath(m[2], basePath);
          if (res) discoveredImages.push({ raw: m[2], alt: m[1] || '試卷圖表', res: res });
        }
      });

      // Populate Left Pane (Diagrams + PDF)
      if (leftPaneBody && currentModalQid) {
        const pdfLink = qRecord ? qRecord[7] : '';
        const qTitle = qRecord ? `第 ${qRecord[3]} 題 · ${qRecord[4]}` : '考題圖檔對照';

        let diagramHtml = '';
        if (discoveredImages.length > 0) {
          diagramHtml = `
            <div style="margin-bottom:14px; padding:10px 14px; background:var(--bg-secondary); border-radius:8px; border:1px solid var(--line); font-size:0.88rem; font-weight:600; color:var(--accent);">
              📋 本題包含 ${discoveredImages.length} 張原題圖表（點擊可全螢幕放大）
            </div>
            ${discoveredImages.map(img => {
              const res = img.res || resolveImagePath(img.raw, basePath);
              return `
                <div class="textbook-figure" style="margin-top:10px;">
                  <div class="figure-frame" onclick="openLightbox('${res}')" title="點擊放大圖表">
                    <img src="${res}" alt="${img.alt}" onerror="handleImageError(this, '${res}', '${img.alt}')" loading="lazy">
                    <div class="figure-zoom-bar">🔍 點擊原圖放大檢視</div>
                  </div>
                  <figcaption style="margin-top:6px; font-weight:600; color:var(--ink-light);">${img.alt}</figcaption>
                </div>
              `;
            }).join('')}
          `;
        } else {
          diagramHtml = `
            <div style="padding:28px 20px; text-align:center; background:var(--card); border:1px dashed var(--line); border-radius:10px; margin-top:10px;">
              <div style="font-size:2rem; margin-bottom:8px;">📝</div>
              <h4 style="color:var(--ink); margin-bottom:6px;">${qTitle}</h4>
              <p style="font-size:0.83rem; color:var(--muted); margin-bottom:16px;">本題為純文字推導題型，無獨立電路圖檔。請參閱右側詳解，或切換至上方「📄 官方試卷 PDF」對照全卷原題！</p>
              ${pdfLink ? `<button onclick="switchLeftTab('pdf')" class="btn-sol" style="font-size:0.82rem;">📄 切換至官方原卷 PDF</button>` : ''}
            </div>
          `;
        }

        let pdfHtml = '';
        if (pdfLink) {
          if (pdfLink.startsWith('http')) {
            pdfHtml = `
              <div style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:30px 20px; background:var(--card); border:1px solid var(--line); border-radius:10px;">
                <div style="font-size:2.8rem; margin-bottom:12px;">🏛️</div>
                <h4 style="color:var(--ink); margin-bottom:8px;">考選部官方原題試卷平臺</h4>
                <p style="font-size:0.85rem; color:var(--muted); max-width:440px; margin-bottom:18px; line-height:1.6;">
                  本試卷為考選部公務人員高等考試三級考試官方原題。請點擊下方按鈕直接連線考選部官方考畢試題平臺查閱原版試卷！
                </p>
                <a href="${pdfLink}" target="_blank" class="btn-sol" style="font-size:0.9rem; padding:10px 22px; text-decoration:none; display:inline-flex; align-items:center; gap:6px;">
                  🌐 連線考選部考畢試題平臺 ↗
                </a>
              </div>
            `;
          } else {
            pdfHtml = `
              <div style="height:100%; display:flex; flex-direction:column;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; font-size:0.82rem;">
                  <span style="font-weight:600; color:var(--ink);">📄 考選部官方原題試卷</span>
                  <a href="${pdfLink}" target="_blank" class="btn-pdf" style="font-size:0.78rem; text-decoration:none;">在新分頁放大開啟 ↗</a>
                </div>
                <iframe src="${pdfLink}" style="flex:1; width:100%; min-height:550px; border:1px solid var(--line); border-radius:8px; background:#fff;"></iframe>
              </div>
            `;
          }
        } else {
          pdfHtml = `
            <div style="padding:28px 20px; text-align:center; background:var(--card); border:1px dashed var(--line); border-radius:10px; margin-top:10px;">
              <div style="font-size:2rem; margin-bottom:8px;">📄</div>
              <h4 style="color:var(--ink); margin-bottom:6px;">官方試卷線上查閱</h4>
              <p style="font-size:0.83rem; color:var(--muted); margin-bottom:16px;">可直接前往考選部官方平臺查詢本年度完整試題 PDF！</p>
              <a href="https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx" target="_blank" class="btn-sol" style="font-size:0.82rem; text-decoration:none; display:inline-flex; align-items:center; gap:6px;">
                🌐 前往考選部考畢試題平臺 ↗
              </a>
            </div>
          `;
        }

        leftPaneBody.innerHTML = `
          <div id="left-tab-content-diagram">${diagramHtml}</div>
          <div id="left-tab-content-pdf" style="display:none; height:100%;">${pdfHtml}</div>
        `;

        const savedTabPref = localStorage.getItem('modal_left_tab_pref');
        if (savedTabPref === 'pdf' && pdfLink) {
          switchLeftTab('pdf');
        } else if (discoveredImages.length > 0) {
          switchLeftTab('diagram');
        } else {
          switchLeftTab('pdf');
        }
      }

      // 🛡️ Step 1: 提取並以專屬佔位符保護 KaTeX 數學區塊與圖片區塊（徹底杜絕 marked 縮排解析錯誤）
      const mathPlaceholders = [];
      const imagePlaceholders = [];
      
      // 提取獨立區塊公式 ($$...$$)
      contentToRender = contentToRender.replace(/\$\$([\s\S]*?)\$\$/g, (match, rawMath) => {
        const token = `@@KATEX_DISPLAY_${mathPlaceholders.length}@@`;
        mathPlaceholders.push({ type: 'display', math: rawMath });
        return token;
      });

      // 提取行內公式 ($...$) - 忽略轉義之 \$
      contentToRender = contentToRender.replace(/(?<!\\)\$([^\$\n]+?)(?<!\\)\$/g, (match, rawMath) => {
        const token = `@@KATEX_INLINE_${mathPlaceholders.length}@@`;
        mathPlaceholders.push({ type: 'inline', math: rawMath });
        return token;
      });

      // 提取並保護 Obsidian 圖片標籤 (![[...]])
      contentToRender = contentToRender.replace(/!\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]/g, (match, p1, p2) => {
        const resolved = resolveImagePath(p1, basePath);
        if (resolved) {
          const token = `@@IMAGE_BLOCK_${imagePlaceholders.length}@@`;
          const figHtml = `<figure class="textbook-figure"><div class="figure-frame" onclick="openLightbox('${resolved}')" title="點擊放大圖表"><img src="${resolved}" alt="${p1}" onerror="handleImageError(this, '${resolved}', '${p1}')" loading="lazy"><div class="figure-zoom-bar">🔍 點擊原圖可放大高解析度檢視</div></div><figcaption>【試卷圖檔對照】${p1}</figcaption></figure>`;
          imagePlaceholders.push(figHtml);
          return token;
        }
        return '';
      });

      // 提取並保護標準 Markdown 圖片標籤 (![alt](src))
      contentToRender = contentToRender.replace(/!\[([^\]]*)\]\(([^\)]+)\)/g, (match, alt, src) => {
        if (src.startsWith('http')) {
          const token = `@@IMAGE_BLOCK_${imagePlaceholders.length}@@`;
          const figHtml = `<figure class="textbook-figure"><div class="figure-frame" onclick="openLightbox('${src}')"><img src="${src}" alt="${alt}" loading="lazy"></div><figcaption>${alt || '參考圖表'}</figcaption></figure>`;
          imagePlaceholders.push(figHtml);
          return token;
        }
        const resolved = resolveImagePath(src, basePath);
        if (resolved) {
          const token = `@@IMAGE_BLOCK_${imagePlaceholders.length}@@`;
          const figHtml = `<figure class="textbook-figure"><div class="figure-frame" onclick="openLightbox('${resolved}')" title="點擊放大圖表"><img src="${resolved}" alt="${alt}" onerror="handleImageError(this, '${resolved}', '${alt}')" loading="lazy"><div class="figure-zoom-bar">🔍 點擊原圖可放大高解析度檢視</div></div><figcaption>${alt || '試卷圖檔對照'}</figcaption></figure>`;
          imagePlaceholders.push(figHtml);
          return token;
        }
        return '';
      });

      // 🛡️ Step 2: 執行 Markdown 語法轉換（此時公式與圖片完全被純文字佔位符保護）
      let html = marked.parse(contentToRender);

      // 🛡️ Step 3: 將圖片佔位符替換回純淨 HTML 結構（移除 marked 自動包裹的 <p>）
      html = html.replace(/<p>\s*@@IMAGE_BLOCK_(\d+)@@\s*<\/p>/g, (match, idx) => {
        return imagePlaceholders[parseInt(idx, 10)] || match;
      });
      html = html.replace(/@@IMAGE_BLOCK_(\d+)@@/g, (match, idx) => {
        return imagePlaceholders[parseInt(idx, 10)] || match;
      });

      // 🛡️ Step 4: 將數學佔位符替換為 KaTeX 高品質渲染之 HTML
      html = html.replace(/@@KATEX_DISPLAY_(\d+)@@/g, (match, idx) => {
        const item = mathPlaceholders[parseInt(idx, 10)];
        return item ? renderLatexDirect(item.math, true) : match;
      });

      html = html.replace(/@@KATEX_INLINE_(\d+)@@/g, (match, idx) => {
        const item = mathPlaceholders[parseInt(idx, 10)];
        return item ? renderLatexDirect(item.math, false) : match;
      });

      // 🌉 Cross-Exam Topic Bridge (TICKET-05)
      let bridgeHtml = '';
      if (currentModalQid) {
        let candidateList = [];
        if (currentModalQid.startsWith('EE-') && typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.questions) {
          candidateList = NATIONAL_EXAMS_DATA.questions;
        } else if (currentModalQid.startsWith('GK-') && typeof DB_DATA !== 'undefined' && DB_DATA.questions) {
          candidateList = DB_DATA.questions;
        }

        if (candidateList.length > 0 && qRecord) {
          const [curQid, curSid, curYr, curQnum, curTopic, curTags] = qRecord;
          const isFromPE = curQid.startsWith('EE-');
          const matches = candidateList.filter(item => {
            if (isFromPE && item[13] === curQid) return true; // Direct related link
            if (!isFromPE && item[0] === qRecord[13]) return true;
            if (item[1] === curSid) {
              const itemTags = item[5] || [];
              const shared = itemTags.filter(t => (curTags || []).includes(t) && !t.includes('學') && !t.includes('工程') && !t.includes('機械') && !t.includes('系統'));
              return shared.length > 0;
            }
            return false;
          }).slice(0, 3);

          if (matches.length > 0) {
            const targetExamName = isFromPE ? '🏛️ 公務人員高考三級' : '🏆 電機工程技師';
            bridgeHtml = `
              <div class="cross-exam-bridge-card">
                <div class="bridge-title">🔗 國考考點延伸：${targetExamName} 同型真題推薦</div>
                <div class="bridge-desc">此題型與${targetExamName}常考觀念高度交疊，建議點擊下方卡片進行同考點對照演練：</div>
                <div class="bridge-items">
                  ${matches.map(mq => `
                    <div class="bridge-item" onclick="openCrossExamQuestion('${mq[0]}', '${mq[6]}', ${mq[3]})">
                      <span class="bridge-qid">${mq[0]}</span>
                      <span class="bridge-topic">${mq[4]}</span>
                      <span class="bridge-arrow">秒開對照 ➔</span>
                    </div>
                  `).join('')}
                </div>
              </div>
            `;
          }
        }
      }

      body.innerHTML = `<div class="md-content">${html}${bridgeHtml}</div>`;
      body.scrollTop = 0;
      
      // KaTeX auto render fallback
      if (window.renderMathInElement) {
        renderMathInElement(body, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false}
          ],
          throwOnError: false
        });
      }
    }, 40);
  }

  // --- Cross-Exam Modal Navigation (TICKET-05) ---
  function openCrossExamQuestion(targetQid, targetSolLink, targetQNum) {
    if (currentModalQid) {
      modalHistoryStack.push({
        qid: currentModalQid,
        solLink: currentModalSolLink,
        qnum: currentModalQNum,
        fullView: currentModalFullView
      });
    }
    if (!nationalExamsLoaded) {
      loadNationalExamsScript(() => {
        openSolutionModal(null, targetSolLink, targetQid, targetQNum);
      });
    } else {
      openSolutionModal(null, targetSolLink, targetQid, targetQNum);
    }
  }

  function popModalHistory() {
    if (modalHistoryStack.length === 0) return;
    const prev = modalHistoryStack.pop();
    openSolutionModal(null, prev.solLink, prev.qid, prev.qnum, prev.fullView);
  }

  // --- URL Hash Deep Routing ---
  function handleUrlHashRouting() {
    const hash = window.location.hash;
    if (hash && hash.startsWith('#q=')) {
      const targetQid = decodeURIComponent(hash.substring(3)).trim();
      const qRecord = findQuestionRecord(targetQid);
      if (qRecord) {
        const [qid, sid, yr, qnum, topic, tags, solLink] = qRecord;
        currentSubject = sid;
        currentYear = String(yr);
        updateSubjectUI();
        renderQuestions();
        openSolutionModal(null, solLink, qid, qnum);
      }
    }
  }

  window.addEventListener('hashchange', handleUrlHashRouting);

  // --- Stats Frequency Data ---
  let currentStatsSubject = 'all';
  const STATS_DATA = {
    'all': [
      { name: "⚡ 交流穩態相量、複數功率與功因改善 (電路學)", count: "14 次 (25.5%)", pct: 95, star: "⭐⭐⭐⭐⭐", note: "S = VI*, Qc = P(tanθ1 - tanθ2)" },
      { name: "🔌 DC-DC Buck / Boost 轉換器伏秒平衡設計 (電子學)", count: "18 次 (32.7%)", pct: 98, star: "⭐⭐⭐⭐⭐", note: "Buck Vo=D Vd, Boost Vo=Vd/(1-D)" },
      { name: "📐 矩陣特徵值、正交對角化與奇異值分解 SVD (工程數學)", count: "16 次 (29.1%)", pct: 92, star: "⭐⭐⭐⭐⭐", note: "det(A - λI) = 0, A = U Σ V^T" },
      { name: "⚙️ 變壓器等效電路、自耦變壓器與效率 (電機機械)", count: "15 次 (27.3%)", pct: 90, star: "⭐⭐⭐⭐⭐", note: "S_auto = [VH/(VH-VX)] S2w, VR公式" },
      { name: "🏢 對稱成分法與短路故障分析 3P/SLG/L-L (電力系統)", count: "16 次 (29.1%)", pct: 92, star: "⭐⭐⭐⭐⭐", note: "SLG Ia1 = Vf/(Z1+Z2+Z0+3Zn)" },
      { name: "🏭 工廠短路電流計算與斷路器啟斷容量選定 (工業配電)", count: "16 次 (29.1%)", pct: 92, star: "⭐⭐⭐⭐⭐", note: "Ssc = Sbase / Xpu, Isc = Ssc/(√3 VL)" },
      { name: "📐 二階常微分方程 ODE 齊次與特解 (工程數學)", count: "14 次 (25.5%)", pct: 85, star: "⭐⭐⭐⭐⭐", note: "特徵根 yh + 待定係數 yp, 尤拉-柯西" },
      { name: "⚙️ 三相感應電動機轉矩轉差率與戴維寧等效 (電機機械)", count: "14 次 (25.5%)", pct: 85, star: "⭐⭐⭐⭐⭐", note: "s_max = R2'/√(Rth^2+Xeq^2), 功率流向" },
      { name: "🏢 電力潮流計算、Ybus 與牛頓法/FDLF (電力系統)", count: "12 次 (21.8%)", pct: 75, star: "⭐⭐⭐⭐⭐", note: "Ybus 矩陣, Jacobian, Δθ = -[B']^-1 [ΔP/|V|]" },
      { name: "⚡ 一階與二階暫態響應與拉氏轉換 (電路學)", count: "13 次 (23.6%)", pct: 80, star: "⭐⭐⭐⭐⭐", note: "三要素法 x(t) = x(∞) + [x(0+)-x(∞)]e^-t/τ" }
    ],
    '01': [
      { name: "1. 交流穩態、相量、功率與功因改善", count: "14 次 (25.5%)", pct: 95, star: "⭐⭐⭐⭐⭐ 每年必考 1~2 題", note: "S = VI* = P + jQ, Qc = P(tanθ1 - tanθ2)" },
      { name: "2. 一階與二階暫態響應與拉氏轉換", count: "13 次 (23.6%)", pct: 85, star: "⭐⭐⭐⭐⭐ 每年必考 1~2 題", note: "三要素公式、s 域等效模型" },
      { name: "3. 三相平衡/不平衡電路與二瓦特計法", count: "11 次 (20.0%)", pct: 75, star: "⭐⭐⭐⭐ 幾乎年年考", note: "VL = √3 Vφ ∠30°, P3φ = W1+W2" },
      { name: "4. 直流電路分析、節點法與戴維寧等效", count: "9 次 (16.4%)", pct: 60, star: "⭐⭐⭐⭐ 高頻基礎題", note: "KCL 節點電壓矩陣、測試源求 Rth" },
      { name: "5. 雙埠網路矩陣 (Z/Y/h/ABCD) 與諧振", count: "8 次 (14.5%)", pct: 50, star: "⭐⭐⭐ 輪流出現", note: "ω0 = 1/√LC, Q = ω0 L / R" }
    ],
    '02': [
      { name: "1. 電力電子 DC-DC 轉換器 (Buck / Boost)", count: "18 次 (32.7%)", pct: 100, star: "⭐⭐⭐⭐⭐ 近 5 年第一大題型", note: "伏秒平衡, Buck Vo=D Vd, Boost Vo=Vd/(1-D)" },
      { name: "2. 運算放大器應用電路 (Op-Amp)", count: "12 次 (21.8%)", pct: 75, star: "⭐⭐⭐⭐⭐ 送分主力・年年必考", note: "虛接地 v+=v-, 差動放大器, 儀表放大器" },
      { name: "3. 電力電子整流器與換流器 (SPWM / Inverter)", count: "10 次 (18.2%)", pct: 65, star: "⭐⭐⭐⭐ 電力組核心", note: "Vdc = (2Vm/π)cosα, SPWM 調變比 ma" },
      { name: "4. BJT 與 MOSFET 小訊號放大電路", count: "9 次 (16.4%)", pct: 55, star: "⭐⭐⭐ 傳統必修題", note: "gm = IC/VT, Av = -gm RL'" },
      { name: "5. CMOS 數位邏輯、頻率響應與回授安定度", count: "6 次 (10.9%)", pct: 40, star: "⭐⭐ 防守型考點", note: "功耗 P = f C VDD^2, 密勒效應 CM = C(1-Av)" }
    ],
    '03': [
      { name: "1. 線性代數：矩陣、特徵值對角化與 SVD", count: "16 次 (29.1%)", pct: 95, star: "⭐⭐⭐⭐⭐ 近 5 年第一大熱門", note: "det(A - λI) = 0, Null Space, A = U Σ V^T" },
      { name: "2. 常微分方程 ODE (線性ODE, 尤拉-柯西)", count: "14 次 (25.5%)", pct: 85, star: "⭐⭐⭐⭐⭐ 基本盤必拿！每年 1 題", note: "二階特徵根齊次解 yh + 待定係數 yp" },
      { name: "3. 拉氏轉換及其在微分方程/系統之應用", count: "10 次 (18.2%)", pct: 65, star: "⭐⭐⭐⭐ 解系統必備利器", note: "L{f'(t)} = sF(s) - f(0), 步階函數" },
      { name: "4. 複變函數、圍道積分與留數定理 (Residue)", count: "8 次 (14.5%)", pct: 50, star: "⭐⭐⭐ 拉開分數關鍵題", note: "柯西-黎曼 (C-R), ∮ f(z)dz = 2πj ∑Res" },
      { name: "5. 傅立葉級數、向量微積分與 PDE", count: "7 次 (12.7%)", pct: 45, star: "⭐⭐⭐ 輪替出現", note: "傅立葉級數 a0, an, bn, 散度定理" }
    ],
    '04': [
      { name: "1. 變壓器：等效電路、自耦變壓器與效率", count: "15 次 (27.3%)", pct: 95, star: "⭐⭐⭐⭐⭐ 投報率之王・每年必考", note: "自耦容量放大 S_auto=[VH/(VH-VX)]S2w, VR" },
      { name: "2. 三相感應電動機：戴維寧等效與轉矩轉差率", count: "14 次 (25.5%)", pct: 85, star: "⭐⭐⭐⭐⭐ 每年必考 1~2 題", note: "s_max = R2'/√(Rth^2+Xeq^2), 功率流向" },
      { name: "3. 同步電機：相量圖、短路比 SCR 與功角特性", count: "13 次 (23.6%)", pct: 80, star: "⭐⭐⭐⭐⭐ 每年必考 1 題", note: "Ef = Vφ + Ia(Ra + jXs), SCR = 1/Xs(pu)" },
      { name: "4. 直流電機：反電動勢常數、轉矩與調速控制", count: "9 次 (16.4%)", pct: 55, star: "⭐⭐⭐⭐ 標準必修計算", note: "Ea = KΦωm = Vt - Ia Ra, T = KΦ Ia" },
      { name: "5. 磁路基礎定律、電磁吸力與磁阻電動機", count: "4 次 (7.2%)", pct: 30, star: "⭐⭐⭐ 近年新興熱門題", note: "R = l/(μA), L = N^2/R, F = B^2 A/(2μ0)" }
    ],
    '05': [
      { name: "1. 對稱成分法與故障分析 (3-Phase, SLG, L-L)", count: "16 次 (29.1%)", pct: 95, star: "⭐⭐⭐⭐⭐ 第一大題型！每年必考", note: "三相 If=Vf/Z1, SLG Ia1=Vf/(Z1+Z2+Z0+3Zn)" },
      { name: "2. 電力潮流與導納矩陣 (Ybus, N-R & FDLF)", count: "12 次 (21.8%)", pct: 75, star: "⭐⭐⭐⭐⭐ 每年必考 1 題", note: "變壓器 a:1 之 Ybus, 牛頓法 Jacobian" },
      { name: "3. 發電機功角特性、搖擺方程與暫態穩定度", count: "11 次 (20.0%)", pct: 70, star: "⭐⭐⭐⭐⭐ 每年必考 1 題", note: "搖擺方程 M d^2δ/dt^2 = Pm - Pmax sinδ" },
      { name: "4. 發電機最佳經濟調度 (Economic Dispatch)", count: "9 次 (16.4%)", pct: 55, star: "⭐⭐⭐⭐ 送分主力", note: "等微增準則 IC1 L1 = IC2 L2 = λ" },
      { name: "5. 輸電線參數模型 (ABCD) 與負載頻率控制", count: "7 次 (12.7%)", pct: 45, star: "⭐⭐⭐ 輪替出現", note: "ABCD 參數矩陣, SIL = VL^2 / Zc" }
    ],
    '06': [
      { name: "1. 工廠短路電流計算與斷路器容量選定", count: "16 次 (29.1%)", pct: 95, star: "⭐⭐⭐⭐⭐ 絕對必考第 1 名！佔分 30%", note: "標么法 Ssc = Sbase / Xpu, Isc = Ssc/(√3 VL)" },
      { name: "2. 功率因數改善、並聯電容器與諧波抑制", count: "13 次 (23.6%)", pct: 80, star: "⭐⭐⭐⭐⭐ 每年必考 1 題", note: "Qc = P(tanθ1 - tanθ2), 串聯電抗器 6%" },
      { name: "3. 電壓降與導線線徑選定計算 (Voltage Drop)", count: "10 次 (18.2%)", pct: 65, star: "⭐⭐⭐⭐ 實務計算核心", note: "三相壓降 ΔV = √3 I (R cosθ + X sinθ)" },
      { name: "4. 工廠負載特性、契約容量與需量管理", count: "9 次 (16.4%)", pct: 55, star: "⭐⭐⭐⭐ 概念與計算兼備", note: "負載因數 LF = Pavg/Pmax, 參差因數 DF" },
      { name: "5. 保護協調 (CO / LVI) 標置與接地工程", count: "7 次 (12.7%)", pct: 45, star: "⭐⭐⭐ 工程實務關鍵題", note: "反時限電驛方程, CTI = 0.3~0.4s" }
    ]
  };

  function selectStatsSubject(sid, btn) {
    currentStatsSubject = sid;
    const pills = document.querySelectorAll('#stats-subject-pills button');
    pills.forEach(p => p.classList.remove('on'));
    if (btn) btn.classList.add('on');
    renderTopTopics();
  }

  function renderTopTopics() {
    const container = document.getElementById('top-topics-container');
    const list = STATS_DATA[currentStatsSubject] || STATS_DATA['all'];

    container.innerHTML = list.map(t => `
      <div style="background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; transition: transform 0.2s;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; font-size: 0.95rem; margin-bottom: 6px; color: var(--ink);">
          <span style="font-weight: 700;">${t.name}</span>
          <span style="color: var(--accent); font-weight: 700; font-size: 0.9rem;">${t.count}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--muted); margin-bottom: 8px;">
          <span>${t.star}</span>
          <code style="background: var(--bg-secondary); padding: 1px 6px; border-radius: 4px; color: var(--ink-light); font-size: 0.8rem;">${t.note}</code>
        </div>
        <div style="height: 8px; background: var(--line); border-radius: 9999px; overflow: hidden;">
          <div style="width: ${t.pct}%; background: var(--accent); height: 100%; border-radius: 9999px;"></div>
        </div>
      </div>
    `).join('');
  }

  // --- Initial Execution ---
  document.addEventListener('DOMContentLoaded', () => {
    // Restore filters from localStorage
    const savedSubFilter = localStorage.getItem('filter-subject');
    const savedYrFilter = localStorage.getItem('filter-year');
    const savedStatusFilter = localStorage.getItem('filter-status');
    const savedDiffFilter = localStorage.getItem('filter-diff');
    if (savedSubFilter) document.getElementById('filter-subject').value = savedSubFilter;
    if (savedYrFilter) document.getElementById('filter-year').value = savedYrFilter;
    if (savedStatusFilter) document.getElementById('filter-status').value = savedStatusFilter;
    if (savedDiffFilter) document.getElementById('filter-diff').value = savedDiffFilter;

    // Restore and watch exam selection
    const savedExamSubj = localStorage.getItem('exam-select-subj');
    const savedExamYr = localStorage.getItem('exam-select-yr');
    if (savedExamSubj) document.getElementById('exam-select-subj').value = savedExamSubj;
    if (savedExamYr) document.getElementById('exam-select-yr').value = savedExamYr;
    document.getElementById('exam-select-subj').addEventListener('change', e => localStorage.setItem('exam-select-subj', e.target.value));
    document.getElementById('exam-select-yr').addEventListener('change', e => localStorage.setItem('exam-select-yr', e.target.value));

    // Restore exam category selection
    const savedExamCategory = localStorage.getItem('exam_category_tab') || 'PE';
    if (savedExamCategory !== 'PE') {
      switchExamCategory(savedExamCategory);
    } else {
      updateFilterDropdownsForCategory();
      updateStatsAndBar();
      renderQuestions();
    }

    renderLayers();
    renderTopTopics();
    initPaneResizer();
    handleUrlHashRouting();
  });
