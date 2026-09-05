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
let currentRecallAchievedLevel = 0;
let currentRecallErrorType = null;

const CN_NUM_MAP = {
  '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8
};

/**
 * Intelligently extracts the target question from full-paper or single-question markdown files.
 */
function extractQuestionMarkdown(rawMd, targetQNum) {
  if (!rawMd) return { content: '', subParts: [] };

  // Canonical question notes carry YAML provenance frontmatter.  It is data
  // for the audit/compiler, not part of the learner-facing solution.  Strip a
  // leading frontmatter document before splitting/rendering; otherwise the
  // metadata is parsed as a large Markdown heading in the solution pane.
  const frontmatter = /^\uFEFF?---\s*\r?\n[\s\S]*?\r?\n---\s*(?:\r?\n|$)/;
  rawMd = rawMd.replace(frontmatter, '');

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

var currentReviewSessionQueue = currentReviewSessionQueue || null;
var currentReviewSessionIndex = currentReviewSessionIndex || 0;

function advanceReviewSessionItem() {
  if (currentReviewSessionQueue && currentReviewSessionIndex + 1 < currentReviewSessionQueue.length) {
    currentReviewSessionIndex++;
    const nextQ = currentReviewSessionQueue[currentReviewSessionIndex];
    const rec = (typeof getReviewRecord === 'function') ? getReviewRecord(nextQ) : { id: nextQ[0], number: nextQ[3], solutionLink: nextQ[6] };
    openSolutionModal(null, rec.solutionLink, rec.id, rec.number, false, true, {
      sessionQueue: currentReviewSessionQueue,
      sessionIndex: currentReviewSessionIndex
    });
  } else {
    if (typeof showToast === 'function') showToast('🎉 今日到期試題已全數檢閱完畢！');
    if (typeof closeSolutionModal === 'function') closeSolutionModal();
    if (typeof renderReviewPage === 'function') renderReviewPage();
  }
}

function openSolutionModal(event, solLink, qid, qnum, fullView = false, activeRecall = false, options = {}) {
  if (event) event.preventDefault();

  currentModalQid = qid;
  currentModalSolLink = solLink;
  currentModalQNum = qnum;
  currentModalFullView = fullView;
  currentSubQuestionIdx = 0;
  currentRecallAchievedLevel = 0;
  currentRecallErrorType = null;
  if (activeRecall) {
    isActiveRecallMode = true;
  }

  if (options && options.sessionQueue) {
    currentReviewSessionQueue = options.sessionQueue;
    currentReviewSessionIndex = typeof options.sessionIndex === 'number' ? options.sessionIndex : 0;
  } else if (!options || !options.keepSession) {
    currentReviewSessionQueue = null;
    currentReviewSessionIndex = 0;
  }

  const modal = document.getElementById('solution-modal');
  if (!modal) return;

  // 0. Update Review Session Header (if inside an active review queue)
  let sessionBar = document.getElementById('modal-session-progress-bar');
  if (!sessionBar) {
    sessionBar = document.createElement('div');
    sessionBar.id = 'modal-session-progress-bar';
    sessionBar.className = 'session-progress-header';
    const modalContent = modal.querySelector('.modal-content') || modal;
    const modalBody = modal.querySelector('.modal-body');
    if (modalBody && modalContent) {
      modalContent.insertBefore(sessionBar, modalBody);
    }
  }
  if (currentReviewSessionQueue && currentReviewSessionQueue.length > 1) {
    const curStep = currentReviewSessionIndex + 1;
    const totalStep = currentReviewSessionQueue.length;
    const pct = Math.round((curStep / totalStep) * 100);
    sessionBar.style.display = 'flex';
    sessionBar.innerHTML = `
      <span>🎴 沉浸複習中 · 第 ${curStep} / ${totalStep} 題</span>
      <div class="session-progress-track">
        <div class="session-progress-fill" style="width: ${pct}%;"></div>
      </div>
      ${curStep < totalStep
        ? `<button class="btn-session-next" type="button" onclick="advanceReviewSessionItem()">⏩ 下一題</button>`
        : `<span style="color: var(--success); font-weight: 700;">🌟 本輪最後一題</span>`}
    `;
  } else if (sessionBar) {
    sessionBar.style.display = 'none';
  }

  const qRecord = findQuestionRecord(qid);
  const [curQid, sid, yr, curQnum, topic, tags, curSolLink, pdfLink, diff] = qRecord || [qid, '01', 114, qnum, '', [], solLink, '', 3];
  const meta = getSubjectMeta(sid);
  // Prefer an attested question-level crop for the stem preview.  GK crops
  // are stored on the question record; PE crops are compiled into the map
  // alongside the legacy page-image map.  Keep the official PDF link below
  // as the source-of-truth fallback/access path.
  const isGK = Boolean(qid && qid.startsWith('GK-'));
  const questionCrop = isGK
    ? (qRecord && qRecord[14])
    : (typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[qid] : '');
  const questionCropSrc = questionCrop ? resolveImageMapUrl(questionCrop, isGK, qid) : '';

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

  // 3. Load Left Pane (question crop + official PDF access)
  const leftPane = document.getElementById('modal-pane-left');
  const leftContent = document.getElementById('modal-left-content');
  if (leftContent) {
    const sourcePreview = questionCropSrc
      ? `<div class="question-crop-wrap">
          <img class="question-crop-preview" src="${questionCropSrc}" alt="${qid} 本題裁切圖" loading="eager" />
        </div>`
      : `<div class="question-crop-fallback">尚未建立本題裁切圖，以下保留官方 PDF 預覽。</div>
         <div class="question-pdf-frame"><iframe src="${pdfLink}#toolbar=0" title="官方原始考卷 PDF" loading="lazy"></iframe></div>`;
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
        <div>${renderQuestionTopic(topic)}</div>
      </div>

      ${sourcePreview}
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

function getSolutionReviewMetadata(qid) {
  if (typeof SOLUTION_REVIEW_METADATA === 'undefined' || !qid) return null;
  return SOLUTION_REVIEW_METADATA[qid] || null;
}

function getSolutionAuditPresentation(status, metadata, qRecord) {
  const knownStatuses = ['verified', 'reference_book_verified', 'needs_manual_review', 'suspected_error', 'not_attempted'];
  const normalizedStatus = knownStatuses.includes(status)
    ? status
    : ['pending', 'in_progress', 'ambiguous', 'unavailable'].includes(status) ? 'not_attempted' : 'unknown';
  const statusCopy = {
    verified: {
      label: '✅ 題解已校驗',
      description: '題解目前標記為已校驗；這是工作庫的校驗狀態，不等同官方公布解答。',
    },
    reference_book_verified: {
      label: '📘 參考書解已校驗',
      description: '本題依使用者提供的參考書慣例完成可重現校驗；不等同官方題面已補齊或官方公布解答。',
    },
    needs_manual_review: {
      label: '🟡 題解保留人工覆核',
      description: '本題保留可讀的條件式推導，但尚未完成足以定稿的人工覆核。',
    },
    suspected_error: {
      label: '🔴 題解疑似有誤',
      description: '本題不可直接視為定稿答案，請依來源題面重新核對。',
    },
    not_attempted: {
      label: '⚪ 題解尚未校驗',
      description: '目前沒有足夠校驗紀錄，頁面不宣稱此題解已被確認。',
    },
    unknown: {
      label: '⚪ 題解校驗狀態未知',
      description: '缺少可辨識的題解校驗狀態，頁面不宣稱校驗範圍或官方背書。',
    },
  }[normalizedStatus];
  const meta = metadata || {};
  const qid = qRecord && qRecord[0];
  const isGK = Boolean(qid && String(qid).startsWith('GK-'));
  const questionCrop = isGK
    ? (qRecord && qRecord[14]) || ''
    : (typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[qid] : '') || '';
  const isHttps = value => typeof value === 'string' && /^https:\/\//i.test(value);
  const publicReferenceUrls = Array.isArray(meta.publicReferenceUrls)
    ? meta.publicReferenceUrls.filter(isHttps)
    : [];
  const hasReviewDetails = Boolean(meta.blocker || meta.action || meta.evidence || meta.disposition);
  const referenceBookEvidence = String(meta.referenceBookEvidence || '');
  return {
    status: normalizedStatus,
    statusLabel: statusCopy.label,
    description: statusCopy.description,
    statusDescription: statusCopy.description,
    disposition: String(meta.disposition || ''),
    blocker: String(meta.blocker || (normalizedStatus === 'needs_manual_review'
      ? '未提供人工覆核備註；目前無法宣稱已校驗。' : '')),
    action: String(meta.action || (normalizedStatus === 'needs_manual_review'
      ? '請補充可重現的校驗步驟與可核對來源。' : '')),
    evidence: String(meta.evidence || ''),
    referenceBookEvidence,
    issueType: String(meta.blocker || normalizedStatus),
    conservative: normalizedStatus !== 'verified' && !hasReviewDetails,
    sources: {
      officialQuestionUrl: qRecord && qRecord[7] ? String(qRecord[7]) : '',
      solutionLink: qRecord && qRecord[6] ? String(qRecord[6]) : '',
      questionCrop: String(questionCrop || ''),
      officialSourceUrl: isHttps(meta.officialSourceUrl) ? meta.officialSourceUrl : '',
      publicReferenceUrls,
      publicReferenceNote: String(meta.publicReferenceNote || ''),
    },
  };
}

function getLearningStatusPresentation(status) {
  const labels = {
    0: { status: 0, label: '⚪ 我的學習狀態：未開始' },
    1: { status: 1, label: '🟢 我的學習狀態：已掌握' },
    2: { status: 2, label: '🔴 我的學習狀態：需二刷' },
  };
  return labels[Number(status)] || labels[0];
}

function buildSolutionIssueReport(qRecord, issueType, options) {
  const record = Array.isArray(qRecord) ? qRecord : [];
  const opts = options || {};
  const auditStatus = opts.auditStatus || record[9] || 'unknown';
  const version = opts.version || (typeof QUESTION_SCHEMA_VERSION !== 'undefined' ? QUESTION_SCHEMA_VERSION : '目前工作庫版本');
  const examFamily = opts.examFamily || (String(record[0] || '').startsWith('GK-') ? 'GK' : 'PE');
  const subjectMeta = typeof getSubjectMeta === 'function' ? getSubjectMeta(record[1]) : null;
  const subject = opts.subjectName || (subjectMeta && subjectMeta.name ? `${record[1]}. ${subjectMeta.name}` : record[1]) || '未提供';
  const problemType = issueType || '未指定';
  const presentation = opts.presentation || getSolutionAuditPresentation(auditStatus, opts.metadata || null, record);
  return [
    '回報題解問題（僅產生文字，不會自動送出）',
    `QID：${record[0] || '未提供'}`,
    `工作庫版本：${version}`,
    `考別：${examFamily}`,
    `年度：${record[2] || '未提供'}`,
    `考科：${subject}`,
    `題解校驗狀態：${auditStatus}｜${presentation.statusLabel}`,
    `問題類型：${problemType}`,
    `官方原題連結：${record[7] || '未提供'}`,
    `題解連結：${record[6] || '未提供'}`,
  ].join('\n');
}

function prepareSolutionIssueReport(qid) {
  const record = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  if (!record) return '';
  const metadata = getSolutionReviewMetadata(qid);
  const presentation = getSolutionAuditPresentation(record[9], metadata, record);
  const textarea = document.getElementById('solution-report-textarea');
  const report = buildSolutionIssueReport(record, presentation.issueType, {
    auditStatus: record[9],
    metadata,
    presentation,
    examFamily: String(qid).startsWith('GK-') ? 'GK' : 'PE',
    version: typeof QUESTION_SCHEMA_VERSION !== 'undefined' ? QUESTION_SCHEMA_VERSION : '目前工作庫版本',
  });
  if (textarea) textarea.value = report;
  return report;
}

function copySolutionIssueReport() {
  const textarea = document.getElementById('solution-report-textarea');
  if (!textarea) return;
  const text = textarea.value || '';
  if (!text) return;
  if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      if (typeof showToast === 'function') showToast('📋 回報文字已複製，尚未傳送');
    }).catch(() => {
      textarea.focus();
      textarea.select();
      if (typeof showToast === 'function') showToast('📋 已選取回報文字，請手動複製');
    });
    return;
  }
  textarea.focus();
  textarea.select();
  if (typeof showToast === 'function') showToast('📋 已選取回報文字，請手動複製');
}

function renderSolutionReviewCard(qid, qRecord) {
  const record = qRecord || (typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null);
  const meta = getSolutionReviewMetadata(qid);
  const presentation = getSolutionAuditPresentation(record && record[9] || 'unknown', meta, record);
  const learning = getLearningStatusPresentation(typeof progressState !== 'undefined' ? progressState[qid] || 0 : 0);
  const esc = typeof reviewHtmlEscape === 'function' ? reviewHtmlEscape : (value) => String(value || '');
  const publicLinks = presentation.sources.publicReferenceUrls.length
    ? `<div><strong>公開參考：</strong>${presentation.sources.publicReferenceUrls.map((url, index) =>
        `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">來源 ${index + 1}</a>`
      ).join('、')}${presentation.sources.publicReferenceNote ? `<div class="review-public-note">${esc(presentation.sources.publicReferenceNote)}</div>` : ''}</div>`
    : '';
  const report = buildSolutionIssueReport(record || [qid], presentation.issueType, {
    auditStatus: presentation.status,
    metadata: meta,
    presentation,
    examFamily: String(qid || '').startsWith('GK-') ? 'GK' : 'PE',
    version: typeof QUESTION_SCHEMA_VERSION !== 'undefined' ? QUESTION_SCHEMA_VERSION : '目前工作庫版本',
  });
  return `
    <aside class="solution-review-card solution-audit-summary solution-audit-card-${presentation.status}" aria-label="題解可信度與來源">
      <div class="review-title">${esc(presentation.statusLabel)}</div>
      <div class="review-description">${esc(presentation.description)}</div>
      <div class="review-meta">
        ${presentation.disposition ? `<div><strong>目前可用分支：</strong>${esc(presentation.disposition)}</div>` : ''}
        ${presentation.blocker ? `<div><strong>阻擋原因：</strong>${esc(presentation.blocker)}</div>` : ''}
        ${presentation.action ? `<div><strong>收斂所需動作：</strong>${esc(presentation.action)}</div>` : ''}
        ${presentation.evidence ? `<div><strong>交叉證據：</strong>${esc(presentation.evidence)}</div>` : ''}
        ${presentation.referenceBookEvidence ? `<div><strong>參考書 evidence：</strong>${esc(presentation.referenceBookEvidence)}</div>` : ''}
        ${presentation.sources.officialQuestionUrl ? `<div><strong>官方原題：</strong><a href="${esc(presentation.sources.officialQuestionUrl)}" target="_blank" rel="noopener noreferrer">開啟原始試題</a></div>` : '<div><strong>官方原題：</strong>未提供可開啟連結</div>'}
        ${presentation.sources.solutionLink ? `<div><strong>題解來源：</strong><a href="${esc(presentation.sources.solutionLink)}" target="_blank" rel="noopener noreferrer">開啟題解檔</a></div>` : '<div><strong>題解來源：</strong>未提供</div>'}
        ${presentation.sources.questionCrop ? `<div><strong>原題裁切：</strong><code>${esc(presentation.sources.questionCrop)}</code></div>` : ''}
        ${presentation.sources.officialSourceUrl ? `<div><strong>官方外部索引：</strong><a href="${esc(presentation.sources.officialSourceUrl)}" target="_blank" rel="noopener noreferrer">開啟官方來源</a></div>` : ''}
        ${publicLinks}
      </div>
      <div class="solution-learning-status"><strong>${esc(learning.label)}</strong>（與題解校驗狀態分開）</div>
      <div class="solution-report-box">
        <label for="solution-report-textarea"><strong>回報文字（可複製，不會自動送出）</strong></label>
        <textarea id="solution-report-textarea" class="solution-report-textarea" rows="7">${esc(report)}</textarea>
        <div class="solution-report-actions">
          <button type="button" class="btn-sol" onclick="prepareSolutionIssueReport('${esc(qid)}')">重新產生回報文字</button>
          <button type="button" class="btn-sol" onclick="copySolutionIssueReport()">📋 複製回報文字</button>
        </div>
      </div>
    </aside>
  `;
}

function renderScenarioMatrix(qid) {
  if (typeof SCENARIO_MATRIX_DATA === 'undefined' || !qid) return '';
  const matrix = SCENARIO_MATRIX_DATA[qid];
  if (!matrix) return '';
  const esc = typeof reviewHtmlEscape === 'function' ? reviewHtmlEscape : (v) => String(v || '');

  const renderScenarioSide = (sc, badgeClass) => {
    const keyValsHtml = sc.keyValues.map(kv => `
      <tr>
        <td class="matrix-param-name">${kv.param}</td>
        <td class="matrix-param-val">${kv.val}</td>
      </tr>
    `).join('');

    return `
      <div class="matrix-column ${badgeClass}">
        <div class="matrix-col-header">
          <span class="matrix-badge">${esc(sc.name)}</span>
        </div>
        <div class="matrix-condition">📌 <strong>假設條件：</strong>${esc(sc.condition)}</div>
        <table class="matrix-table">
          <thead>
            <tr><th>關鍵參數 / 物理量</th><th>推導數值</th></tr>
          </thead>
          <tbody>${keyValsHtml}</tbody>
        </table>
        <div class="matrix-advice">💡 <strong>考場應對防坑對策：</strong>${esc(sc.examAdvice)}</div>
      </div>
    `;
  };

  return `
    <div class="scenario-matrix-card" id="scenario-matrix-${esc(qid)}">
      <div class="scenario-matrix-header">
        <span class="scenario-icon">⚖️</span>
        <div>
          <h4 class="scenario-title">參數敏感度情境分支矩陣 (Scenario Matrix)</h4>
          <p class="scenario-conflict">${esc(matrix.coreConflict)}</p>
        </div>
      </div>
      <div class="scenario-matrix-grid">
        ${renderScenarioSide(matrix.scenarioA, 'scenario-a')}
        ${renderScenarioSide(matrix.scenarioB, 'scenario-b')}
      </div>
    </div>
  `;
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
  showToast(isActiveRecallMode ? '🎴 已開啟主動回想模式（四步驟蓋牌）' : '📖 已切換為全開放詳解模式');

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
  revealRecallLayer(2);
}

function revealRecallFull() {
  const fullEl = document.getElementById('recall-full-section');
  const ratingEl = document.getElementById('recall-rating-bar');
  const boxEl = document.getElementById('recall-step-box');
  if (fullEl) fullEl.style.display = 'block';
  if (ratingEl) ratingEl.style.display = 'flex';
  if (boxEl) boxEl.style.display = 'none';
  currentRecallAchievedLevel = 4;

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

function revealRecallLayer(layer) {
  const target = document.getElementById(`recall-layer-${layer}`);
  if (target) {
    target.style.display = 'block';
    target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  currentRecallAchievedLevel = Math.max(currentRecallAchievedLevel, Number(layer) || 0);
  const full = document.getElementById('recall-full-section');
  const rating = document.getElementById('recall-rating-bar');
  if (layer >= 4) {
    if (full) full.style.display = 'block';
    if (rating) rating.style.display = 'flex';
  }
}

function chooseRecallError(errorType) {
  currentRecallErrorType = errorType || null;
  document.querySelectorAll('[data-recall-error]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.recallError === currentRecallErrorType);
  });
}

function submitSM2Rating(rating) {
  if (!currentModalQid) return;
  const achieved = rating === 5 ? 4 : rating === 3 ? Math.max(2, currentRecallAchievedLevel) : 0;
  if (typeof recordRecallAttempt === 'function') {
    recordRecallAttempt(currentModalQid, achieved, currentRecallErrorType);
  }
  const result = recordSM2Review(currentModalQid, rating);
  const ratingTexts = { 1: '🔴 遺忘 (明日二刷)', 3: '🟡 勉強 (3天後複習)', 5: '🟢 完美秒殺 (已延長間隔)' };
  showToast(`🎯 已排程：${ratingTexts[rating]} (下次：${result.nextReviewDate})`);

  // Refresh badges in question list
  if (typeof renderQuestions === 'function') renderQuestions();
  if (typeof renderReviewPage === 'function') renderReviewPage();
  updateModalStatusButtons(currentModalQid);

  // Auto transition to next question if rating 5
  if (rating === 5) {
    setTimeout(() => {
      if (currentReviewSessionQueue && currentReviewSessionQueue.length > 1) {
        advanceReviewSessionItem();
      } else {
        navModalQuestion(1);
      }
    }, 600);
  }
}

function renderSubQuestionContent(markdownChunk, qRecord) {
  const rightPane = document.getElementById('modal-right-content');
  if (!rightPane) return;

  if (isActiveRecallMode) {
    const isGK = currentModalQid && currentModalQid.startsWith('GK-');
    const recallHints = typeof getRecallHintBundle === 'function'
      ? getRecallHintBundle(currentModalQid, qRecord)
      : { chapter: '待人工複核', activation: '先列出已知量、未知量與要求量。', formula: '寫出本章節核心公式。', trap: '檢查單位、極性與邊界條件。' };

    // In active-recall mode the right pane must not leak any solution text.
    // The question crop is already visible in the left pane, so keep the
    // entire rendered Markdown in the fourth-step reveal section instead of
    // heuristically exposing a "stem" prefix (which could contain equations
    // when a note has no conventional solution heading).
    const fullSolutionHtml = resolveRenderedImageSources(processMarkdownWithMath(markdownChunk), isGK, currentModalQid);
    const reviewCardHtml = renderSolutionReviewCard(currentModalQid);
    const scenarioMatrixHtml = renderScenarioMatrix(currentModalQid);

    let dagHtml = '';
    if (qRecord) {
      const [qid, sid, yr, qnum, topic] = qRecord;
      dagHtml = renderDagTracerCard(qid, sid, topic);
    }

    rightPane.innerHTML = `
      <div class="solution-content active-recall-active">
        <!-- Keep the four-step workflow immediately above the hidden solution. -->
        <div class="active-recall-box" id="recall-step-box">
          <div class="active-recall-title">🧠 主動回想閃卡模式 (Active Recall)</div>
          <p style="font-size: 0.85rem; color: var(--muted); margin: 0;">先在白紙寫下答案，再依序揭露章節、起手式、公式與陷阱：</p>
          <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
            <button class="btn-reveal-hint" onclick="revealRecallLayer(1)">① 顯示章節</button>
            <button class="btn-reveal-hint" onclick="revealRecallLayer(2)">② 顯示起手式</button>
            <button class="btn-reveal-hint" onclick="revealRecallLayer(3)">③ 顯示公式／陷阱</button>
            <button class="btn-reveal-full" onclick="revealRecallFull()">④ 揭曉完整推導</button>
          </div>
        </div>

        <div id="recall-layer-1" style="display: none; margin: 16px 0; padding: 12px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 4px solid var(--accent);">
          <strong>章節：</strong> ${reviewHtmlEscape(recallHints.chapter)}
        </div>
        <div id="recall-layer-2" style="display: none; margin: 16px 0; padding: 12px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 4px solid var(--warn);">
          <strong>起手式：</strong> ${reviewHtmlEscape(recallHints.activation)}
        </div>
        <div id="recall-layer-3" style="display: none; margin: 16px 0; padding: 12px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 4px solid var(--warn);">
          <strong>核心公式：</strong> <span class="math-inline">$${recallHints.formula}$</span><br><strong>常見陷阱：</strong> ${reviewHtmlEscape(recallHints.trap)}
        </div>

        <div id="recall-full-section" style="display: none;">
          ${fullSolutionHtml}
          ${dagHtml}
        </div>

        ${reviewCardHtml}
        ${scenarioMatrixHtml}

        <div id="recall-rating-bar" class="sm2-rating-bar" style="display: none;">
          <div class="sm2-rating-title">🎯 本題作答自評（自動寫入 SM-2 智能遺忘曲線排程）：</div>
          <div class="recall-error-buttons" style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:8px 0;">
            <button type="button" class="pill" data-recall-error="題型辨識錯" onclick="chooseRecallError('題型辨識錯')">題型辨識錯</button>
            <button type="button" class="pill" data-recall-error="起手式不會" onclick="chooseRecallError('起手式不會')">起手式不會</button>
            <button type="button" class="pill" data-recall-error="公式忘記" onclick="chooseRecallError('公式忘記')">公式忘記</button>
            <button type="button" class="pill" data-recall-error="計算錯" onclick="chooseRecallError('計算錯')">計算錯</button>
            <button type="button" class="pill" data-recall-error="觀念混淆" onclick="chooseRecallError('觀念混淆')">觀念混淆</button>
          </div>
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
    html = resolveRenderedImageSources(html, isGK, currentModalQid);
    html = renderSolutionReviewCard(currentModalQid) + renderScenarioMatrix(currentModalQid) + html;

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
