// src/components/quickReviewSheet.js
// -*- coding: utf-8 -*-
/**
 * quickReviewSheet.js
 * ====================
 * 考前 30 分鐘考點陷阱急救速覽表 (Last 30-Minute High-Yield Cheat Sheet)
 * Extracts core formulas and key traps from KNOWLEDGE_DAG across all 6 core subjects.
 * Provides:
 * 1. Categorized collapsible subject accordions.
 * 2. High-definition KaTeX formula display.
 * 3. Highlighted key exam pitfalls (keyTrap).
 * 4. Print & PDF-friendly export styling for physical paper review.
 */

let quickReviewSelectedSubject = 'all';

function setQuickReviewSubject(sid) {
  quickReviewSelectedSubject = sid;
  renderQuickReviewSheet();
}

function toggleAllQuickCards(expand) {
  const details = document.querySelectorAll('.quicksheet-subject-section details');
  details.forEach(d => {
    d.open = expand;
  });
}

function renderQuickReviewSheet() {
  const container = document.getElementById('quicksheet-container');
  if (!container) return;

  if (typeof KNOWLEDGE_DAG === 'undefined') {
    container.innerHTML = `<div class="quicksheet-empty">知識圖譜資料載入中...</div>`;
    return;
  }

  const subjects = [
    { id: '01', name: '電路學', icon: '⚡', color: '#4a7c8f' },
    { id: '02', name: '電子學（含電力電子）', icon: '🔬', color: '#686b8f' },
    { id: '03', name: '工程數學', icon: '📐', color: '#54826b' },
    { id: '04', name: '電機機械', icon: '⚙️', color: '#a17846' },
    { id: '05', name: '電力系統', icon: '🗼', color: '#a85858' },
    { id: '06', name: '工業配電', icon: '🏭', color: '#7d6382' }
  ];

  // 1. Controls Header
  const subjectPillsHtml = [
    `<button class="pill ${quickReviewSelectedSubject === 'all' ? 'active' : ''}" onclick="setQuickReviewSubject('all')">全科合輯 (60+ 考點)</button>`
  ].concat(subjects.map(s => {
    const activeClass = quickReviewSelectedSubject === s.id ? 'active' : '';
    return `<button class="pill ${activeClass}" onclick="setQuickReviewSubject('${s.id}')">${s.icon} ${s.name}</button>`;
  })).join('');

  // 2. Build Sections
  let sectionsHtml = '';

  subjects.forEach(s => {
    if (quickReviewSelectedSubject !== 'all' && quickReviewSelectedSubject !== s.id) return;

    // Filter nodes for this subject
    const nodes = Object.values(KNOWLEDGE_DAG).filter(n => n.subject === s.id);
    if (nodes.length === 0) return;

    const cardsHtml = nodes.map(n => {
      const levelBadge = `<span class="qsheet-lvl-badge lvl-${n.level || 1}">L${n.level || 1} 核心</span>`;
      const formulaMath = n.coreFormula ? `<div class="qsheet-formula">$$${n.coreFormula}$$</div>` : '<div class="qsheet-no-formula">定性分析 / 概念題型</div>';
      const trapText = n.keyTrap ? `<div class="qsheet-trap">⚠️ <strong>常考陷阱與防坑突破：</strong>${n.keyTrap}</div>` : '';

      return `
        <div class="qsheet-card" id="qsheet-node-${n.id}">
          <div class="qsheet-card-header">
            <div class="qsheet-card-title">
              <span class="qsheet-node-id">${n.id}</span>
              <strong>${n.name}</strong>
            </div>
            ${levelBadge}
          </div>
          <div class="qsheet-formula-wrap">
            <div class="qsheet-label">📐 核心必背推導公式：</div>
            ${formulaMath}
          </div>
          ${trapText}
        </div>
      `;
    }).join('');

    sectionsHtml += `
      <div class="quicksheet-subject-section" id="qsheet-sec-${s.id}">
        <details open>
          <summary class="qsheet-sec-header">
            <div class="qsheet-sec-title">
              <span class="qsheet-sec-icon">${s.icon}</span>
              <h3 style="display:inline;font-size:1.15rem;margin:0;color:var(--ink);">${s.name}</h3>
              <span class="qsheet-count-tag">${nodes.length} 個高頻核心考點</span>
            </div>
            <span class="qsheet-arrow">▾</span>
          </summary>
          <div class="qsheet-cards-grid">
            ${cardsHtml}
          </div>
        </details>
      </div>
    `;
  });

  container.innerHTML = `
    <div class="quicksheet-shell">
      <div class="quicksheet-top-bar">
        <div class="quicksheet-header-text">
          <h2>⚡ 考前 30 分鐘考點陷阱急救速覽手冊</h2>
          <p>全科 60+ 核心考點定理、必背公式、考選部歷屆易錯陷阱提煉；支援 A4 列印排版帶入考場速讀。</p>
        </div>
        <div class="quicksheet-actions">
          <button class="pill" onclick="toggleAllQuickCards(true)">展開全部</button>
          <button class="pill" onclick="toggleAllQuickCards(false)">收合全部</button>
          <button class="pill btn-print-sheet" onclick="window.print()">🖨️ 列印/匯出 PDF</button>
        </div>
      </div>

      <div class="quicksheet-sub-filters">
        ${subjectPillsHtml}
      </div>

      <div class="quicksheet-content">
        ${sectionsHtml}
      </div>
    </div>
  `;

  // Render KaTeX in the container
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(container, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false }
      ],
      throwOnError: false
    });
  }
}
