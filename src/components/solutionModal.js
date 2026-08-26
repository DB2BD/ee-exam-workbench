// src/components/solutionModal.js
/**
 * Robust Solution Viewer Modal Component.
 * Features:
 * 1. Intelligent Question Extraction (Full-paper or single-question)
 * 2. Navigation toolbar: [← 上一題] / [下一題 →]
 * 3. Same Exam Year Question Selector (該年度考卷選題)
 * 4. Split / Solution-only / Exam-only layout toggle
 * 5. Sub-question pill switcher, KaTeX formula renderer, image map resolver, and DAG Weakness Tracer.
 */

let currentModalQid = null;
let currentModalSolLink = null;
let currentModalQNum = null;
let currentModalFullView = false;
let currentSubQuestionIdx = 0;
let modalHistoryStack = [];

const CN_NUM_MAP = {
  '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8
};

/**
 * Intelligently extracts the target question from full-paper or single-question markdown files.
 */
function extractQuestionMarkdown(rawMd, targetQNum) {
  if (!rawMd) return { content: '', subParts: [] };

  const qNumInt = parseInt(targetQNum, 10) || 1;

  // Split by major question headers: e.g. "## 一、", "## 二、", "## 第 1 題", "## 1."
  const majorSplitRegex = /(?=\n##\s+(?:第\s*[一二三四五六七八九十\d]+\s*[大題題]|(?:[一二三四五六七八九十]|\d+)\s*[、\.\:]))/gi;
  const sections = rawMd.split(majorSplitRegex);

  let targetSection = rawMd;

  if (sections.length > 1) {
    // Multi-question full paper file
    let found = false;
    for (let i = 1; i < sections.length; i++) {
      const sec = sections[i];
      const hMatch = sec.match(/##\s+(?:第\s*([一二三四五六七八九十\d]+)\s*[大題題]|([一二三四五六七八九十]|\d+)\s*[、\.\:])/i);
      if (hMatch) {
        const token = (hMatch[1] || hMatch[2] || '').trim();
        const parsedNum = CN_NUM_MAP[token];
        if (parsedNum === qNumInt) {
          targetSection = sec;
          found = true;
          break;
        }
      }
    }
    // Fallback by array index if heading regex missed
    if (!found && sections[qNumInt]) {
      targetSection = sections[qNumInt];
    }
  }

  // Check for sub-parts within the question: e.g. "### (一)", "### (二)", "#### (1)"
  const subPartRegex = /(?=\n###\s+(?:\([一二三四五六七八九十\d]+\)|(?:[一二三四五六七八九十]|\d+)\s*[\.、\)]))/gi;
  const subParts = targetSection.split(subPartRegex);

  return {
    fullContent: targetSection,
    subParts: subParts.length > 1 ? subParts : []
  };
}

function openSolutionModal(event, solLink, qid, qnum, fullView = false, activeRecall = false) {
  if (event) event.preventDefault();

  currentModalQid = qid;
  currentModalSolLink = solLink;
  currentModalQNum = qnum;
  currentModalFullView = fullView;
  currentSubQuestionIdx = 0;
  if (activeRecall) {
    isActiveRecallMode = true;
  }

  const modal = document.getElementById('solution-modal');
  if (!modal) return;

  const qRecord = findQuestionRecord(qid);
  const [curQid, sid, yr, curQnum, topic, tags, curSolLink, pdfLink, diff] = qRecord || [qid, '01', 114, qnum, '', [], solLink, '', 3];
  const meta = getSubjectMeta(sid);

  // 1. Update Title
  const titleEl = document.getElementById('modal-title');
  if (titleEl) {
    titleEl.innerHTML = `
      <span style="color: var(--accent-dark); font-weight: 800; font-family: var(--font-mono);">${qid}</span>
      <span style="font-size: 0.9rem; color: var(--muted); font-weight: 500;">
        · ${meta.icon} ${meta.name}（${yr} 年第 ${curQnum} 大題）
      </span>
    `;
  }

  // 2. Update Same Exam Dropdown & Prev/Next Buttons
  updateSameExamDropdown(sid, yr, qid);
  updateModalNavButtons(qid);
  syncActiveRecallButtonState();

  // 3. Load Left Pane (Space-efficient collapsible stem + Full Height PDF embed)
  const leftPane = document.getElementById('modal-pane-left');
  const leftContent = document.getElementById('modal-left-content');
  if (leftContent) {
    leftContent.innerHTML = `
      <div style="padding: 8px 14px; background: var(--surface); border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 0.85rem; font-weight: 700; color: var(--accent-dark);">📄 官方原始考卷 PDF</span>
          <button class="btn-stem-toggle" onclick="toggleStemDescription()" id="btn-stem-toggle" style="padding: 3px 8px; font-size: 0.76rem; font-weight: 600; border-radius: 4px; border: 1px solid var(--line); background: var(--bg-secondary); color: var(--ink-light); cursor: pointer; display: inline-flex; align-items: center; gap: 4px;">
            🔍 展開題幹文字
          </button>
        </div>
        <a href="${pdfLink}" target="_blank" class="btn-pdf" style="font-size: 0.78rem; padding: 3px 8px;">
          新分頁開啟 ⬈
        </a>
      </div>

      <div id="modal-stem-collapse" style="display: none; padding: 12px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--line); font-size: 0.88rem; line-height: 1.6; color: var(--ink); max-height: 180px; overflow-y: auto;">
        <div style="font-weight: 700; font-size: 0.78rem; color: var(--accent-dark); margin-bottom: 4px;">📌 原題題幹文字描述：</div>
        <div>${topic}</div>
      </div>

      <div style="flex: 1; width: 100%; height: 100%; min-height: 500px; background: #525659;">
        <iframe src="${pdfLink}#toolbar=0" style="width: 100%; height: 100%; min-height: 500px; border: none; display: block;"></iframe>
      </div>
    `;
  }

  // 4. Load Right Pane (Extracted Question Solution + KaTeX + Sub-part Navigation + DAG)
  const rightPane = document.getElementById('modal-right-content');
  const subQPillsBar = document.getElementById('modal-sub-q-pills');

  const rawMd = resolveSolutionMarkdown(solLink, qid);

  if (rawMd) {
    const { fullContent, subParts } = extractQuestionMarkdown(rawMd, curQnum);

    // If sub-parts exist, render pills for quick navigation
    if (subParts.length > 1 && subQPillsBar) {
      subQPillsBar.style.display = 'flex';
      let pillsHtml = `<button class="sub-q-pill active" onclick="switchSubQuestion(0)">📖 完整全題推導</button>`;
      for (let i = 0; i < subParts.length; i++) {
        const titleMatch = subParts[i].match(/###\s+([^\n]+)/);
        const title = titleMatch ? titleMatch[1].trim() : `第 (${i + 1}) 小題`;
        pillsHtml += `<button class="sub-q-pill" onclick="switchSubQuestion(${i + 1})">${title}</button>`;
      }
      subQPillsBar.innerHTML = pillsHtml;
    } else if (subQPillsBar) {
      subQPillsBar.style.display = 'none';
    }

    // Default to rendering full content of this question
    renderSubQuestionContent(fullContent, qRecord);
  } else {
    if (subQPillsBar) subQPillsBar.style.display = 'none';
    if (rightPane) {
      rightPane.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
          <h3 style="color: var(--warn); margin-bottom: 10px;">📑 詳解收錄於題解知識庫中</h3>
          <p style="color: var(--muted); margin-bottom: 20px;">點擊下方按鈕前往知識庫檢視本題完整解答：</p>
          <a href="${solLink}" target="_blank" class="btn-sol">🔗 前往考科詳解庫</a>
        </div>
      `;
    }
  }

  updateModalStatusButtons(qid);
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function updateSameExamDropdown(sid, yr, currentQid) {
  const select = document.getElementById('modal-same-exam-select');
  if (!select) return;

  const activeList = getActiveQuestionsList();
  const sameExamQs = activeList.filter(q => q[1] === sid && q[2] === yr);

  if (sameExamQs.length === 0) {
    select.style.display = 'none';
    return;
  }

  select.style.display = 'inline-block';
  select.innerHTML = sameExamQs.map(q => {
    const qid = q[0];
    const qnum = q[3];
    const s = progressState[qid] || 0;
    const sIcon = s === 1 ? '🟢' : s === 2 ? '🔴' : '⚪';
    const isCur = qid === currentQid;
    return `<option value="${qid}" ${isCur ? 'selected' : ''}>${sIcon} 第 ${qnum} 大題 (${qid})</option>`;
  }).join('');
}

function onSameExamSelectChange(selectElem) {
  const targetQid = selectElem.value;
  if (!targetQid || targetQid === currentModalQid) return;
  const qRecord = findQuestionRecord(targetQid);
  if (qRecord) {
    const [qid, sid, yr, qnum, topic, tags, solLink] = qRecord;
    openSolutionModal(null, solLink, qid, qnum);
  }
}

function updateModalNavButtons(qid) {
  const btnPrev = document.getElementById('btn-modal-prev');
  const btnNext = document.getElementById('btn-modal-next');
  if (!btnPrev || !btnNext) return;

  const activeList = getActiveQuestionsList();
  const curIdx = activeList.findIndex(q => q[0] === qid);

  btnPrev.disabled = curIdx <= 0;
  btnNext.disabled = curIdx < 0 || curIdx >= activeList.length - 1;
}

function navModalQuestion(direction) {
  const activeList = getActiveQuestionsList();
  if (activeList.length === 0 || !currentModalQid) return;

  const curIdx = activeList.findIndex(q => q[0] === currentModalQid);
  if (curIdx === -1) return;

  const targetIdx = curIdx + direction;
  if (targetIdx >= 0 && targetIdx < activeList.length) {
    const targetQ = activeList[targetIdx];
    const [qid, sid, yr, qnum, topic, tags, solLink] = targetQ;
    openSolutionModal(null, solLink, qid, qnum);
  }
}

function setModalLayout(mode) {
  const leftPane = document.getElementById('modal-pane-left');
  const rightPane = document.getElementById('modal-pane-right');
  const resizer = document.getElementById('modal-resizer');
  if (!leftPane || !rightPane) return;

  document.querySelectorAll('.view-layout-toggle .btn-layout').forEach(b => b.classList.remove('active'));

  if (mode === 'solution-only') {
    leftPane.style.display = 'none';
    if (resizer) resizer.style.display = 'none';
    rightPane.style.flex = '1 1 100%';
    const btn = document.getElementById('btn-layout-solution');
    if (btn) btn.classList.add('active');
  } else if (mode === 'exam-only') {
    leftPane.style.display = 'flex';
    leftPane.style.flex = '1 1 100%';
    if (resizer) resizer.style.display = 'none';
    rightPane.style.display = 'none';
    const btn = document.getElementById('btn-layout-exam');
    if (btn) btn.classList.add('active');
  } else {
    // Split 50/50
    leftPane.style.display = 'flex';
    leftPane.style.flex = '0 0 45%';
    if (resizer) resizer.style.display = 'block';
    rightPane.style.display = 'flex';
    rightPane.style.flex = '1';
    const btn = document.getElementById('btn-layout-split');
    if (btn) btn.classList.add('active');
  }
}

function switchSubQuestion(idx) {
  currentSubQuestionIdx = idx;
  document.querySelectorAll('.sub-q-pill').forEach((p, i) => {
    p.classList.toggle('active', i === idx);
  });

  const rawMd = resolveSolutionMarkdown(currentModalSolLink, currentModalQid);
  const qRecord = findQuestionRecord(currentModalQid);
  if (!rawMd) return;

  const { fullContent, subParts } = extractQuestionMarkdown(rawMd, currentModalQNum);

  if (idx === 0 || subParts.length === 0) {
    renderSubQuestionContent(fullContent, qRecord);
  } else if (subParts[idx - 1]) {
    renderSubQuestionContent(subParts[idx - 1], qRecord);
  }
}

let isActiveRecallMode = false;

function syncActiveRecallButtonState() {
  const btns = [document.getElementById('btn-active-recall'), document.getElementById('btn-modal-active-recall')];
  btns.forEach(btn => {
    if (!btn) return;
    btn.classList.toggle('active', isActiveRecallMode);
    btn.style.background = isActiveRecallMode ? 'var(--warn)' : 'var(--surface)';
    btn.style.color = isActiveRecallMode ? '#ffffff' : 'var(--ink)';
    btn.style.borderColor = isActiveRecallMode ? 'var(--warn)' : 'var(--line)';
    btn.innerHTML = isActiveRecallMode ? '🎴 蓋牌思考中 (點此全開)' : '🎴 主動回想蓋牌';
  });
}

function toggleActiveRecallMode() {
  isActiveRecallMode = !isActiveRecallMode;
  syncActiveRecallButtonState();
  showToast(isActiveRecallMode ? '🎴 已開啟主動回想模式 (三階蓋牌)' : '📖 已切換為全開放詳解模式');

  // Re-render current question with or without active recall masking
  const rawMd = resolveSolutionMarkdown(currentModalSolLink, currentModalQid);
  const qRecord = findQuestionRecord(currentModalQid);
  if (rawMd) {
    const { fullContent, subParts } = extractQuestionMarkdown(rawMd, currentModalQNum);
    if (currentSubQuestionIdx === 0 || subParts.length === 0) {
      renderSubQuestionContent(fullContent, qRecord);
    } else if (subParts[currentSubQuestionIdx - 1]) {
      renderSubQuestionContent(subParts[currentSubQuestionIdx - 1], qRecord);
    }
  }
}

function revealRecallHint() {
  const hintEl = document.getElementById('recall-hint-section');
  if (hintEl) {
    hintEl.style.display = 'block';
    hintEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function revealRecallFull() {
  const fullEl = document.getElementById('recall-full-section');
  const ratingEl = document.getElementById('recall-rating-bar');
  const boxEl = document.getElementById('recall-step-box');
  if (fullEl) fullEl.style.display = 'block';
  if (ratingEl) ratingEl.style.display = 'flex';
  if (boxEl) boxEl.style.display = 'none';

  // Render any hidden math in full section
  const rightPane = document.getElementById('modal-right-content');
  if (rightPane && typeof renderMathInElement !== 'undefined') {
    renderMathInElement(fullEl, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ],
      throwOnError: false
    });
  }
}

function submitSM2Rating(rating) {
  if (!currentModalQid) return;
  const result = recordSM2Review(currentModalQid, rating);
  const ratingTexts = { 1: '🔴 遺忘 (明日二刷)', 3: '🟡 勉強 (3天後複習)', 5: '🟢 完美秒殺 (已延長間隔)' };
  showToast(`🎯 已排程：${ratingTexts[rating]} (下次：${result.nextReviewDate})`);

  // Refresh badges in question list
  if (typeof renderQuestions === 'function') renderQuestions();
  updateModalStatusButtons(currentModalQid);

  // Auto transition to next question if rating 5
  if (rating === 5) {
    setTimeout(() => {
      navModalQuestion(1);
    }, 600);
  }
}

function renderSubQuestionContent(markdownChunk, qRecord) {
  const rightPane = document.getElementById('modal-right-content');
  if (!rightPane) return;

  if (isActiveRecallMode) {
    // Robust split for question stem, hints, and derivations across all 2-4 level headers
    const hintSplitRegex = /(?=\n#{2,4}\s+(?:💡|核心考點|破題關鍵|解題思路|考點剖析|破題思路|觀念分析))/i;
    const stepSplitRegex = /(?=\n#{2,4}\s+(?:✏️|步驟|詳細推導|完整解答|推導|計算步驟|解題步驟|詳細數學推導|滿分解答|標準解答|詳解|解法|解答|求解|\([一二三四五六七八九十\d]+\)|(?:第\s*[一二三四五六七八九十\d]+\s*小題))|\n\*\*(?:【解】|解：|解答：|推導：)\*\*)/i;

    let stemPart = markdownChunk;
    let hintPart = '';
    let derivationPart = '';

    if (hintSplitRegex.test(markdownChunk)) {
      const parts = markdownChunk.split(hintSplitRegex);
      stemPart = parts[0];
      const rest = parts.slice(1).join('\n');
      if (stepSplitRegex.test(rest)) {
        const restParts = rest.split(stepSplitRegex);
        hintPart = restParts[0];
        derivationPart = restParts.slice(1).join('\n');
      } else {
        hintPart = rest;
        derivationPart = '';
      }
    } else if (stepSplitRegex.test(markdownChunk)) {
      const parts = markdownChunk.split(stepSplitRegex);
      stemPart = parts[0];
      derivationPart = parts.slice(1).join('\n');
    }

    // Safety fallback: if no header matched, mask everything after initial stem paragraph
    if (!derivationPart && !hintPart && markdownChunk.includes('\n\n')) {
      const paras = markdownChunk.split(/\n\n+/);
      if (paras.length > 2) {
        stemPart = paras.slice(0, 2).join('\n\n');
        derivationPart = paras.slice(2).join('\n\n');
      }
    }

    const isGK = currentModalQid && currentModalQid.startsWith('GK-');

    let stemHtml = processMarkdownWithMath(stemPart).replace(/src=["'](.*?)["']/g, (m, src) => `src="${resolveImageMapUrl(src, isGK)}"`);
    let hintHtml = hintPart ? processMarkdownWithMath(hintPart).replace(/src=["'](.*?)["']/g, (m, src) => `src="${resolveImageMapUrl(src, isGK)}"`) : '';
    let derivationHtml = derivationPart ? processMarkdownWithMath(derivationPart).replace(/src=["'](.*?)["']/g, (m, src) => `src="${resolveImageMapUrl(src, isGK)}"`) : '';

    let dagHtml = '';
    if (qRecord) {
      const [qid, sid, yr, qnum, topic] = qRecord;
      dagHtml = renderDagTracerCard(qid, sid, topic);
    }

    rightPane.innerHTML = `
      <div class="solution-content">
        ${stemHtml}

        <div class="active-recall-box" id="recall-step-box">
          <div class="active-recall-title">🧠 主動回想閃卡模式 (Active Recall)</div>
          <p style="font-size: 0.85rem; color: var(--muted); margin: 0;">白紙蓋牌獨立思考，列出破題公式與關鍵步驟後再揭曉：</p>
          <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
            ${hintHtml ? '<button class="btn-reveal-hint" onclick="revealRecallHint()">💡 提示核心考點與思路</button>' : ''}
            <button class="btn-reveal-full" onclick="revealRecallFull()">📖 揭曉完整步驟推導</button>
          </div>
        </div>

        <div id="recall-hint-section" style="display: none; margin: 16px 0; padding: 14px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 4px solid var(--warn);">
          ${hintHtml}
        </div>

        <div id="recall-full-section" style="display: none;">
          ${derivationHtml}
          ${dagHtml}
        </div>

        <div id="recall-rating-bar" class="sm2-rating-bar" style="display: none;">
          <div class="sm2-rating-title">🎯 本題作答自評（自動寫入 SM-2 智能遺忘曲線排程）：</div>
          <div class="sm2-rating-buttons">
            <button class="btn-sm2 btn-sm2-1" onclick="submitSM2Rating(1)">
              <span>🔴 遺忘卡關</span>
              <span class="subtext">明日立即二刷 (EF-0.2)</span>
            </button>
            <button class="btn-sm2 btn-sm2-3" onclick="submitSM2Rating(3)">
              <span>🟡 勉強推導</span>
              <span class="subtext">3 天後再次複習</span>
            </button>
            <button class="btn-sm2 btn-sm2-5" onclick="submitSM2Rating(5)">
              <span>🟢 完美秒殺</span>
              <span class="subtext">延長複習間隔 (EF+0.1)</span>
            </button>
          </div>
        </div>
      </div>
    `;
  } else {
    // Normal Full Open Mode
    let html = processMarkdownWithMath(markdownChunk);
    const isGK = currentModalQid && currentModalQid.startsWith('GK-');
    html = html.replace(/src=["'](.*?)["']/g, (match, src) => `src="${resolveImageMapUrl(src, isGK)}"`);

    if (qRecord) {
      const [qid, sid, yr, qnum, topic] = qRecord;
      html += renderDagTracerCard(qid, sid, topic);
    }

    // Add SM-2 quick rating footer in normal mode as well!
    html += `
      <div class="sm2-rating-bar">
        <div class="sm2-rating-title">🎯 複習自評反饋（SM-2 智能間隔排程）：</div>
        <div class="sm2-rating-buttons">
          <button class="btn-sm2 btn-sm2-1" onclick="submitSM2Rating(1)">
            <span>🔴 遺忘卡關</span>
            <span class="subtext">明日二刷</span>
          </button>
          <button class="btn-sm2 btn-sm2-3" onclick="submitSM2Rating(3)">
            <span>🟡 勉強推導</span>
            <span class="subtext">3天後複習</span>
          </button>
          <button class="btn-sm2 btn-sm2-5" onclick="submitSM2Rating(5)">
            <span>🟢 完美秒殺</span>
            <span class="subtext">間隔延長</span>
          </button>
        </div>
      </div>
    `;

    rightPane.innerHTML = `
      <div class="solution-content">
        ${html}
      </div>
    `;
  }

  // Auto-render any remaining math formulas
  if (typeof renderMathInElement !== 'undefined') {
    renderMathInElement(rightPane, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ],
      throwOnError: false
    });
  }
}

function closeModal() {
  const modal = document.getElementById('solution-modal');
  if (modal) modal.classList.remove('show');
  document.body.style.overflow = '';
  currentModalQid = null;
}

function updateModalStatusButtons(qid) {
  const statusBtn = document.getElementById('modal-status-btn');
  const starBtn = document.getElementById('modal-star-btn');
  if (!qid || !statusBtn || !starBtn) return;

  const curStatus = progressState[qid] || 0;
  const isStarred = !!starredState[qid];

  const statusLabels = ['⚪ 未開始', '🟢 已掌握', '🔴 需二刷'];
  statusBtn.className = `status-badge s-${curStatus}`;
  statusBtn.innerText = statusLabels[curStatus];
  statusBtn.onclick = (e) => toggleStatus(qid, e);

  starBtn.className = `btn-star ${isStarred ? 'active' : ''}`;
  starBtn.innerHTML = isStarred ? '★ 已收藏' : '☆ 收藏本題';
  starBtn.onclick = (e) => toggleStarred(qid, e);
}

function toggleStemDescription() {
  const collapseEl = document.getElementById('modal-stem-collapse');
  const btn = document.getElementById('btn-stem-toggle');
  if (!collapseEl) return;

  const isHidden = collapseEl.style.display === 'none';
  collapseEl.style.display = isHidden ? 'block' : 'none';
  if (btn) {
    btn.innerHTML = isHidden ? '▲ 收合題幹文字' : '🔍 展開題幹文字';
    btn.style.background = isHidden ? 'var(--accent)' : 'var(--bg-secondary)';
    btn.style.color = isHidden ? '#ffffff' : 'var(--ink-light)';
  }
}

// Global Keyboard Navigation
window.addEventListener('keydown', (e) => {
  const modal = document.getElementById('solution-modal');
  if (!modal || !modal.classList.contains('show')) return;

  if (e.key === 'Escape') {
    closeModal();
  } else if (e.key === 'ArrowLeft') {
    navModalQuestion(-1);
  } else if (e.key === 'ArrowRight') {
    navModalQuestion(1);
  }
});

