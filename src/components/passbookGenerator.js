// src/components/passbookGenerator.js
/**
 * 15-Day Personal Exam Passbook Generator (考前 15 天專屬奪榜衝刺手冊)
 * ======================================================================
 * Synthesizes examinee's individual progress, wrong questions, SM-2 decay,
 * and high-yield anchor problems into an A4 printable cram passbook.
 */

function generatePassbookData(questions, progressState = {}, sm2Store = {}, recallStore = {}, options = {}) {
  const readiness = typeof calculateExamReadiness === 'function'
    ? calculateExamReadiness(questions, progressState, sm2Store, recallStore)
    : { projectedAverage: 55, passingProbability: 40, subjectResults: {}, topRoiBoosters: [] };

  // Identify Top 15 High-Yield Anchor Questions
  // Priority: 1) In review (wrong), 2) High difficulty in weak subjects, 3) Recent years (>=110)
  // 尚未完成的 114 模考／108 盲測題不進奪榜本，避免提前看到。
  let locked = new Set();
  try {
    if (options && options.lockedQids) locked = new Set(Array.from(options.lockedQids));
    else if (typeof practiceLockedQids === 'function') locked = practiceLockedQids();
  } catch (_) { locked = new Set(); }
  const allQ = (questions || []).filter(q => !locked.has(Array.isArray(q) ? q[0] : q.id));
  const scoredQuestions = allQ.map(q => {
    const qid = Array.isArray(q) ? q[0] : q.id;
    const sid = Array.isArray(q) ? q[1] : q.subjectId;
    const yr = Number(Array.isArray(q) ? q[2] : q.year) || 104;
    const diff = Number(Array.isArray(q) ? q[8] : q.difficulty) || 3;
    const pVal = progressState[qid] || 0;

    let priorityScore = 0;
    if (pVal === 2) priorityScore += 50; // Wrong / in-review
    else if (pVal === 0) priorityScore += 20; // Unstarted

    // Higher weight for weak subjects
    const subjRes = readiness.subjectResults && readiness.subjectResults[sid];
    if (subjRes && subjRes.isDanger) priorityScore += 25;
    else if (subjRes && subjRes.estimatedScore < 60) priorityScore += 15;

    // Recency weight
    if (yr >= 110) priorityScore += 15;
    priorityScore += diff * 2;

    return {
      q,
      qid,
      subjectId: sid,
      year: yr,
      number: Array.isArray(q) ? q[3] : q.number,
      topic: Array.isArray(q) ? q[4] : (q.stem || ''),
      tags: Array.isArray(q) ? q[5] : (q.tags || []),
      solLink: Array.isArray(q) ? q[6] : q.solutionLink,
      priorityScore
    };
  });

  scoredQuestions.sort((a, b) => b.priorityScore - a.priorityScore);
  const topAnchorQuestions = scoredQuestions.slice(0, 15);

  return {
    generatedAt: new Date().toISOString(),
    readiness,
    topAnchorQuestions
  };
}

function escapePassbookHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// K6: 失分點速查卡. Returns '' when no curated data exists. Plain text only
// (the passbook does not run KaTeX), every string is HTML-escaped.
// Keep the 114 模考／108 盲測 lock: QIDs locked by practiceLockedQids are dropped from an item's
// QID list, and an item whose QIDs are all locked is dropped (its text would reveal the paper).
function cheatsheetUnlockedQids(qids, locked) {
  return (qids || []).filter(q => !locked.has(q));
}

function cheatsheetFilterLocked(data, locked) {
  const keep = item => !item || !(item.qids || []).length || cheatsheetUnlockedQids(item.qids, locked).length > 0;
  const clean = item => Object.assign({}, item, { qids: cheatsheetUnlockedQids(item.qids, locked) });
  const subjects = (data.subjects || []).map(s => Object.assign({}, s, {
    categories: (s.categories || []).map(c => Object.assign({}, c, {
      items: (c.items || []).filter(keep).map(clean)
    })).filter(c => c.items.length)
  })).filter(s => s.categories.length);
  const templates = (data.assumption_templates || []).filter(keep).map(clean);
  return Object.assign({}, data, { subjects, assumption_templates: templates });
}

function renderCheatsheetSectionHtml(data, options) {
  if (!data) return '';
  let locked = new Set();
  try {
    if (options && options.lockedQids) locked = new Set(Array.from(options.lockedQids));
    else if (typeof practiceLockedQids === 'function') locked = practiceLockedQids();
  } catch (_) { locked = new Set(); }
  if (typeof locked.has !== 'function') locked = new Set();
  data = cheatsheetFilterLocked(data, locked);
  const subjects = (data.subjects || []).filter(s => s && (s.categories || []).length);
  const templates = data.assumption_templates || [];
  if (!subjects.length && !templates.length) return '';
  const qidHtml = qids => (qids || []).map(q =>
    `<code style="font-size: 0.8125rem; color: var(--muted);">${escapePassbookHtml(q)}</code>`).join(' ');
  const subjectsHtml = subjects.map((s, idx) => `
    <div class="cheatsheet-subject" style="${idx ? 'page-break-before: always; ' : ''}margin-top: 12px;">
      <div style="font-weight: 800; color: var(--accent-dark); margin-bottom: 6px;">${escapePassbookHtml(s.name)}</div>
      ${s.categories.map(c => `
        <div style="font-weight: 700; font-size: 0.82rem; margin: 6px 0 2px;">${escapePassbookHtml(c.label)}</div>
        <ul style="font-size: 0.8125rem; line-height: 1.6; margin-left: 20px;">
          ${(c.items || []).map(it => `<li>${escapePassbookHtml(it.text)} ${qidHtml(it.qids)}</li>`).join('')}
        </ul>`).join('')}
    </div>`).join('');
  const templatesHtml = templates.length ? `
    <div class="cheatsheet-assumptions" style="${subjects.length ? 'page-break-before: always; ' : ''}margin-top: 12px;">
      <div style="font-weight: 800; color: var(--accent-dark); margin-bottom: 6px;">缺條件時怎麼寫假設</div>
      <ul style="font-size: 0.8125rem; line-height: 1.6; margin-left: 20px;">
        ${templates.map(t => `<li><strong>${escapePassbookHtml(t.subject_name || '')}</strong>：${escapePassbookHtml(t.situation)}。${escapePassbookHtml(t.how_to_write)} ${qidHtml(t.qids)}</li>`).join('')}
      </ul>
    </div>` : '';
  return `
        <div class="cheatsheet-section" style="margin-top: 24px;">
          <h4 style="color: var(--accent-dark); margin-bottom: 10px;">肆、失分點速查卡</h4>
          ${subjectsHtml}${templatesHtml}
        </div>`;
}

// 題幹與其他頁面同一條 Markdown＋KaTeX 管線；管線不存在時退回純文字。
function passbookTopicHtml(topic) {
  const raw = String(topic == null ? '' : topic);
  try {
    if (typeof processMarkdownWithMath === 'function') return processMarkdownWithMath(raw);
  } catch (_) { /* fall back to escaped text */ }
  return escapePassbookHtml(raw);
}

function passbookKeydown_(event) {
  if (event.key === 'Escape') closePassbookModal();
}

function openPassbookModal() {
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const passbook = generatePassbookData(
    questions,
    typeof progressState !== 'undefined' ? progressState : {},
    typeof sm2Data !== 'undefined' ? sm2Data : {},
    typeof recallProgress !== 'undefined' ? recallProgress : {}
  );

  let modal = document.getElementById('passbook-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'passbook-modal';
    modal.className = 'passbook-overlay';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'passbook-title');
    modal.addEventListener('click', event => { if (event.target === modal) closePassbookModal(); });
    document.body.appendChild(modal);
  }

  const anchorQuestionsHtml = passbook.topAnchorQuestions.map((item, idx) => {
    const meta = typeof getSubjectMeta === 'function' ? getSubjectMeta(item.subjectId) : { name: item.subjectId };
    return `
      <div class="passbook-item" style="border-bottom: 1px solid var(--line); padding: 12px 0;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
          <span style="font-weight: 800; color: var(--accent-dark); font-family: var(--font-mono);">
            #${idx + 1} · ${item.qid} (${item.year} 年 ${escapePassbookHtml(meta.name)} 第 ${escapePassbookHtml(item.number)} 題)
          </span>
          <span style="font-size: 0.8125rem; background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px;">
            ${escapePassbookHtml((item.tags || []).slice(0, 3).join(' · '))}
          </span>
        </div>
        <div class="passbook-topic" style="font-size: 0.86rem; color: var(--ink); line-height: 1.5;">${passbookTopicHtml(item.topic)}</div>
      </div>
    `;
  }).join('');

  const cheatsheetHtml = renderCheatsheetSectionHtml(typeof CHEATSHEET_DATA !== 'undefined' ? CHEATSHEET_DATA : null);

  modal.innerHTML = `
    <div class="passbook-dialog passbook-modal-content">
      <div class="passbook-head passbook-hide-print">
        <h3 id="passbook-title">考前速查手冊（列印）</h3>
        <button type="button" class="passbook-close" aria-label="關閉" title="關閉（Esc）" onclick="closePassbookModal()">✕ 關閉</button>
      </div>
      <div class="modal-body passbook-printable-area" style="padding: 24px;">
        <!-- Header Banner -->
        <div style="border-bottom: 2px solid var(--accent); padding-bottom: 14px; margin-bottom: 18px;">
          <h2 style="color: var(--accent-dark); margin: 0 0 6px 0;">專門職業及技術人員高等考試：電機工程技師</h2>
          <h4 style="color: var(--ink-light); margin: 0; font-weight: 600;">考前速查手冊：時間分配、計算機按鍵、高頻母題與失分點</h4>
          <p style="font-size: 0.8125rem; color: var(--muted); margin-top: 6px;">
            生成時間：${new Date().toLocaleDateString('zh-TW')}
          </p>
        </div>

        <!-- 戰力與得分估計以「成績」分頁為準，這裡不重複計算 -->
        <p class="passbook-hide-print" style="margin-bottom: 18px; font-size: 0.85rem; color: var(--muted);">各科得分與距離及格線，請看「成績」分頁；這裡只放考前要帶進考場的速查內容。</p>

        <!-- Section 2: Pacing Strategy -->
        <div style="margin-bottom: 24px; background: var(--bg-secondary); padding: 14px; border-radius: var(--radius-sm);">
          <h4 style="color: var(--accent-dark); margin-bottom: 8px;">壹、考場 120 分鐘得分節奏（5＋90＋17＋8）</h4>
          <ul style="font-size: 0.85rem; line-height: 1.8; margin-left: 20px; color: var(--ink);">
            <li><strong>0 ~ 5 分鐘（掃卷）</strong>：看完所有題目與小題，在題號旁標 A／B／C；不開始長算式</li>
            <li><strong>5 ~ 95 分鐘（第一輪 90 分鐘）</strong>：先做 A，再做 B，最後處理 C；每題依配分設時間帽，每配分最多 0.9 分鐘（20 分題 18 分鐘、25 分題 22.5 分鐘）</li>
            <li><strong>連續 8 分鐘寫不出下一步</strong>：先留下已能確定的定義、起手式或中間量，然後換題，不讓同一題吞掉後面題的可得分時間</li>
            <li><strong>95 ~ 112 分鐘（搶分 17 分鐘）</strong>：從未完成題中選「配分最高且下一步已知道」者補完；完全沒有起手式的題不救</li>
            <li><strong>112 ~ 120 分鐘（收尾 8 分鐘）</strong>：補題號、小題結論、單位、方向、相角與計算機 DEG 模式，只修明顯抄算錯誤，不開新推導</li>
          </ul>
        </div>

        <!-- Section 3: fx-82 Keystroke Quick Reference -->
        <div style="margin-bottom: 24px;">
          <h4 style="color: var(--accent-dark); margin-bottom: 8px;">貳、考選部指定計算機（Casio fx-82SOLAR II）必背按鍵流</h4>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.82rem;">
            <div style="border: 1px solid var(--line); padding: 10px; border-radius: 4px;">
              <strong>直角轉極座標 (R➔P)</strong><br>
              <code>A ➔ INV ➔ R➔P ➔ B ➔ = ➔ b</code><br>
              <small style="color: var(--muted);">(顯示大小 R 與相角 θ)</small>
            </div>
            <div style="border: 1px solid var(--line); padding: 10px; border-radius: 4px;">
              <strong>極座標轉直角 (P➔R)</strong><br>
              <code>R ➔ INV ➔ P➔R ➔ θ ➔ = ➔ b</code><br>
              <small style="color: var(--muted);">(顯示實部 A 與虛部 B)</small>
            </div>
            <div style="border: 1px solid var(--line); padding: 10px; border-radius: 4px;">
              <strong>並聯阻抗倒數鏈</strong><br>
              <code>Z1 ➔ 1/x ➔ + ➔ Z2 ➔ 1/x ➔ = ➔ 1/x</code>
            </div>
            <div style="border: 1px solid var(--line); padding: 10px; border-radius: 4px;">
              <strong>三相功率常數鏈</strong><br>
              <code>3 ➔ √ ➔ × ➔ VL ➔ × ➔ IL ➔ × ➔ pf ➔ =</code>
            </div>
          </div>
        </div>

        <!-- Section 4: Top 15 Anchor Questions -->
        <div>
          <h4 style="color: var(--accent-dark); margin-bottom: 10px;">參、考前個人專屬核心母題清單（Top 15）</h4>
          <div style="font-size: 0.82rem; color: var(--muted); margin-bottom: 10px;">
            依您的做題紀錄、弱項科目與近年高頻考點挑出；尚未完成的 114 模考與 108 盲測題不會出現在這裡。考前在白紙上蓋牌獨立重算一次：
          </div>
          ${anchorQuestionsHtml}
        </div>${cheatsheetHtml}
      </div>
      <div class="modal-footer passbook-hide-print" style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.85rem; color: var(--muted);">提示：可使用鍵盤快捷鍵 Cmd + P 列印或另存為 PDF</span>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn-pdf" onclick="closePassbookModal()">關閉</button>
          <button type="button" class="btn-sol" onclick="printPassbook()">一鍵列印衝刺手冊 (A4 / PDF)</button>
        </div>
      </div>
    </div>
  `;

  // The cheat-sheet items carry inline \( \) LaTeX from the canonical notes.
  if (typeof renderMathInElement === 'function') {
    try {
      renderMathInElement(modal, {
        delimiters: [{ left: '\\(', right: '\\)', display: false }],
        throwOnError: false
      });
    } catch (_) { /* math is best-effort */ }
  }

  modal.classList.add('show');
  document.addEventListener('keydown', passbookKeydown_);
  const closeBtn = modal.querySelector('.passbook-close');
  if (closeBtn) closeBtn.focus();
}

function closePassbookModal() {
  const modal = document.getElementById('passbook-modal');
  if (modal) modal.classList.remove('show');
  document.removeEventListener('keydown', passbookKeydown_);
}

function printPassbook() {
  window.print();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generatePassbookData,
    passbookTopicHtml,
    renderCheatsheetSectionHtml
  };
}
