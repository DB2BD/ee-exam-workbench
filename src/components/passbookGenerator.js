// src/components/passbookGenerator.js
/**
 * 15-Day Personal Exam Passbook Generator (考前 15 天專屬奪榜衝刺手冊)
 * ======================================================================
 * Synthesizes examinee's individual progress, wrong questions, SM-2 decay,
 * and high-yield anchor problems into an A4 printable cram passbook.
 */

function generatePassbookData(questions, progressState = {}, sm2Store = {}, recallStore = {}) {
  const readiness = typeof calculateExamReadiness === 'function'
    ? calculateExamReadiness(questions, progressState, sm2Store, recallStore)
    : { projectedAverage: 55, passingProbability: 40, subjectResults: {}, topRoiBoosters: [] };

  // Identify Top 15 High-Yield Anchor Questions
  // Priority: 1) In review (wrong), 2) High difficulty in weak subjects, 3) Recent years (>=110)
  const allQ = (questions || []).slice();
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
    modal.className = 'modal-backdrop';
    document.body.appendChild(modal);
  }

  const subjSummaryHtml = Object.values(passbook.readiness.subjectResults || {}).map(s => `
    <div style="border: 1px solid var(--line); border-radius: 6px; padding: 10px; background: var(--surface);">
      <div style="font-weight: 700; color: var(--accent-dark);">${s.icon || ''} ${s.name}</div>
      <div style="font-size: 1.1rem; font-weight: 800; color: ${s.isDanger ? 'var(--warn)' : 'var(--ink)'}; margin: 4px 0;">
        預估：${s.estimatedScore} 分
      </div>
      <div style="font-size: 0.78rem; color: var(--muted);">掌握率：${Math.round(s.effectiveMasteryRate * 100)}%</div>
    </div>
  `).join('');

  const anchorQuestionsHtml = passbook.topAnchorQuestions.map((item, idx) => {
    const meta = typeof getSubjectMeta === 'function' ? getSubjectMeta(item.subjectId) : { name: item.subjectId };
    return `
      <div class="passbook-item" style="border-bottom: 1px solid var(--line); padding: 12px 0;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
          <span style="font-weight: 800; color: var(--accent-dark); font-family: var(--font-mono);">
            #${idx + 1} · ${item.qid} (${item.year} 年 ${meta.name} 第 ${item.number} 題)
          </span>
          <span style="font-size: 0.8rem; background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px;">
            ${(item.tags || []).slice(0, 3).join(' · ')}
          </span>
        </div>
        <div style="font-size: 0.86rem; color: var(--ink); line-height: 1.5;">${item.topic}</div>
      </div>
    `;
  }).join('');

  modal.innerHTML = `
    <div class="modal-content passbook-modal-content" style="max-width: 840px; max-height: 92vh; overflow-y: auto;">
      <div class="modal-header passbook-hide-print">
        <h3>📕 個人專屬 15 天考前奪榜衝刺手冊 (Custom Passbook)</h3>
        <button type="button" class="btn-close" onclick="closePassbookModal()">✕</button>
      </div>
      <div class="modal-body passbook-printable-area" style="padding: 24px;">
        <!-- Header Banner -->
        <div style="border-bottom: 2px solid var(--accent); padding-bottom: 14px; margin-bottom: 18px;">
          <h2 style="color: var(--accent-dark); margin: 0 0 6px 0;">專門職業及技術人員高等考試：電機工程技師</h2>
          <h4 style="color: var(--ink-light); margin: 0; font-weight: 600;">考前 15 天個人化高頻母題與死穴急救衝刺手冊</h4>
          <p style="font-size: 0.8rem; color: var(--muted); margin-top: 6px;">
            生成時間：${new Date().toLocaleDateString('zh-TW')}
          </p>
        </div>

        <!-- Section 1: Subject Readiness Radar -->
        <div style="margin-bottom: 24px;">
          <h4 style="color: var(--accent-dark); margin-bottom: 10px;">📊 壹、個人六科戰力分佈與及格安全線</h4>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px;">
            ${subjSummaryHtml}
          </div>
        </div>

        <!-- Section 2: Pacing Strategy -->
        <div style="margin-bottom: 24px; background: var(--bg-secondary); padding: 14px; border-radius: var(--radius-sm);">
          <h4 style="color: var(--accent-dark); margin-bottom: 8px;">⏱️ 貳、考場 120 分鐘黃金配速四階段守則</h4>
          <ul style="font-size: 0.85rem; line-height: 1.8; margin-left: 20px; color: var(--ink);">
            <li><strong>0 ~ 25 分鐘</strong>：第 1 大題作答（先瀏覽全卷 2 分鐘，選最有把握之題目優先作答）</li>
            <li><strong>25 ~ 50 分鐘</strong>：第 2 大題作答（嚴格控管時間，每題上限 25 分鐘）</li>
            <li><strong>50 ~ 75 分鐘</strong>：第 3 大題作答（遇繁複推導先寫出等效電路與主方程式保底）</li>
            <li><strong>75 ~ 100 分鐘</strong>：第 4 大題作答（切勿交白卷，依步驟列出符號式仍能拿 50% 步驟分）</li>
            <li><strong>100 ~ 120 分鐘</strong>：🚨 <strong>全局黃金檢查期</strong>（檢查正負號、相角、單位、計算機模式 DEG）</li>
          </ul>
        </div>

        <!-- Section 3: fx-82 Keystroke Quick Reference -->
        <div style="margin-bottom: 24px;">
          <h4 style="color: var(--accent-dark); margin-bottom: 8px;">🧮 參、考選部指定計算機（Casio fx-82SOLAR II）必背按鍵流</h4>
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
          <h4 style="color: var(--accent-dark); margin-bottom: 10px;">🎯 肆、考前 15 天個人專屬核心必殺母題清單（Top 15）</h4>
          <div style="font-size: 0.82rem; color: var(--muted); margin-bottom: 10px;">
            基於您的做題錯誤紀錄、弱項科目與近 5 年高頻考點精選，考前務必在白紙上蓋牌獨立重算一次：
          </div>
          ${anchorQuestionsHtml}
        </div>
      </div>
      <div class="modal-footer passbook-hide-print" style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.85rem; color: var(--muted);">提示：可使用鍵盤快捷鍵 Cmd + P 列印或另存為 PDF</span>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn-pdf" onclick="closePassbookModal()">關閉</button>
          <button type="button" class="btn-sol" onclick="printPassbook()">🖨️ 一鍵列印衝刺手冊 (A4 / PDF)</button>
        </div>
      </div>
    </div>
  `;

  modal.classList.add('show');
}

function closePassbookModal() {
  const modal = document.getElementById('passbook-modal');
  if (modal) modal.classList.remove('show');
}

function printPassbook() {
  window.print();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generatePassbookData
  };
}
