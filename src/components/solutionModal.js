// src/components/solutionModal.js
/**
 * Robust Solution Viewer Modal Component.
 * Intelligent full-paper section extractor, sub-question pill switcher,
 * KaTeX formula renderer, image map resolver, and DAG Weakness Tracer.
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

function openSolutionModal(event, solLink, qid, qnum, fullView = false) {
  if (event) event.preventDefault();

  currentModalQid = qid;
  currentModalSolLink = solLink;
  currentModalQNum = qnum;
  currentModalFullView = fullView;
  currentSubQuestionIdx = 0;

  const modal = document.getElementById('solution-modal');
  if (!modal) return;

  const qRecord = findQuestionRecord(qid);
  const [curQid, sid, yr, curQnum, topic, tags, curSolLink, pdfLink, diff] = qRecord || [qid, '01', 114, qnum, '', [], solLink, '', 3];
  const meta = getSubjectMeta(sid);

  // Update title
  const titleEl = document.getElementById('modal-title');
  if (titleEl) {
    titleEl.innerHTML = `
      <span style="color: var(--accent-dark); font-weight: 800; font-family: var(--font-mono);">${qid}</span>
      <span style="font-size: 0.9rem; color: var(--muted); font-weight: 500;">
        · ${meta.icon} ${meta.name}（${yr} 年第 ${curQnum} 大題）
      </span>
    `;
  }

  // Load left pane (Raw Question + PDF embed)
  const leftPane = document.getElementById('modal-left-content');
  if (leftPane) {
    leftPane.innerHTML = `
      <div style="padding: 20px; border-bottom: 1px solid var(--line); background: var(--surface);">
        <div style="font-size: 0.82rem; font-weight: 700; color: var(--accent-dark); margin-bottom: 8px;">
          📌 官方原題題幹描述
        </div>
        <div style="font-size: 0.95rem; line-height: 1.65; color: var(--ink);">
          ${topic}
        </div>
        <div style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;">
          <a href="${pdfLink}" target="_blank" class="btn-pdf" style="font-size: 0.82rem;">
            📄 開啟考選部原始試卷 PDF ⬈
          </a>
        </div>
      </div>
      <div style="flex: 1; min-height: 380px; background: #525659;">
        <iframe src="${pdfLink}#toolbar=0" style="width: 100%; height: 100%; min-height: 400px; border: none;"></iframe>
      </div>
    `;
  }

  // Load right pane (Extracted Question Solution + KaTeX + Sub-part Navigation + DAG)
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

function renderSubQuestionContent(markdownChunk, qRecord) {
  const rightPane = document.getElementById('modal-right-content');
  if (!rightPane) return;

  // Render KaTeX protected markdown
  let html = processMarkdownWithMath(markdownChunk);

  // Replace image URLs from image maps
  const isGK = currentModalQid && currentModalQid.startsWith('GK-');
  html = html.replace(/src=["'](.*?)["']/g, (match, src) => {
    return `src="${resolveImageMapUrl(src, isGK)}"`;
  });

  // Append Knowledge DAG Weakness Tracer
  if (qRecord) {
    const [qid, sid, yr, qnum, topic] = qRecord;
    const dagCardHtml = renderDagTracerCard(qid, sid, topic);
    html += dagCardHtml;
  }

  rightPane.innerHTML = `
    <div class="solution-content">
      ${html}
    </div>
  `;

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
