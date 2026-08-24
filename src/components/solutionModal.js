// src/components/solutionModal.js
/**
 * Split Solution Viewer Modal Component.
 * Features: Left pane PDF/Raw question, Right pane KaTeX Markdown solution,
 * Sub-question pills navigation, and Knowledge DAG Weakness Tracer integration.
 */

let currentModalQid = null;
let currentModalSolLink = null;
let currentModalQNum = null;
let currentModalFullView = false;
let currentSubQuestionIdx = 0;
let modalHistoryStack = [];

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
      <span>${qid}</span>
      <span style="font-size: 0.85rem; color: var(--muted); font-weight: 500;">
        · ${meta.icon} ${meta.name}（${yr} 年第 ${curQnum} 大題）
      </span>
    `;
  }

  // Load left pane (Raw Question + PDF embed)
  const leftPane = document.getElementById('modal-left-content');
  if (leftPane) {
    leftPane.innerHTML = `
      <div style="padding: 20px; border-bottom: 1px solid var(--line); background: var(--surface);">
        <div style="font-size: 0.82rem; font-weight: 700; color: var(--accent-dark); margin-bottom: 6px;">
          📌 官方原題題幹描述
        </div>
        <div style="font-size: 0.95rem; line-height: 1.6; color: var(--ink);">
          ${topic}
        </div>
        <div style="margin-top: 14px; display: flex; gap: 8px;">
          <a href="${pdfLink}" target="_blank" class="btn-pdf" style="font-size: 0.8rem;">
            📄 開啟官方原始考卷 PDF ⬈
          </a>
        </div>
      </div>
      <div style="flex: 1; min-height: 350px; background: #525659;">
        <iframe src="${pdfLink}#toolbar=0" style="width: 100%; height: 100%; min-height: 400px; border: none;"></iframe>
      </div>
    `;
  }

  // Load right pane (Markdown Solution + KaTeX + DAG Tracer)
  const rightPane = document.getElementById('modal-right-content');
  const subQPillsBar = document.getElementById('modal-sub-q-pills');

  let rawMd = resolveSolutionMarkdown(solLink, qid);

  if (rawMd) {
    // Check for multiple sub-questions in markdown
    const subQRegex = /(?:^|\n)##\s+(?:題號\s*)?(\d+|第[一二三四五六七八九十\d]+[小題大題]*|[一二三四五六七八九十]\s*、|Question\s*\d+)/gi;
    const subSections = rawMd.split(/(?=\n##\s+)/);

    if (subSections.length > 1 && subQPillsBar) {
      subQPillsBar.style.display = 'flex';
      subQPillsBar.innerHTML = subSections.map((sec, idx) => {
        const titleMatch = sec.match(/##\s+([^\n]+)/);
        const title = titleMatch ? titleMatch[1].replace(/【.*?】/, '').trim() : `第 ${idx + 1} 小題`;
        return `
          <button class="sub-q-pill ${idx === 0 ? 'active' : ''}" onclick="switchSubQuestion(${idx})">
            ${title}
          </button>
        `;
      }).join('');
    } else if (subQPillsBar) {
      subQPillsBar.style.display = 'none';
    }

    // Render first sub-question or full markdown
    renderSubQuestionContent(subSections.length > 1 ? subSections[0] : rawMd, qRecord);
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

  const subSections = rawMd.split(/(?=\n##\s+)/);
  if (subSections[idx]) {
    renderSubQuestionContent(subSections[idx], qRecord);
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
