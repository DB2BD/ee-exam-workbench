// src/components/topTopics.js
/**
 * Seven Layers & High Frequency Topics Analysis Component.
 */

let currentStatsSubject = 'all';

const STATS_DATA = {
  'all': [
    { name: '戴維寧/諾頓等效與最大功率', count: '48 題', pct: 95, star: '⭐⭐⭐⭐⭐', note: '電路學/電子學/機械核心必考' },
    { name: '三相短路與對稱分量故障', count: '42 題', pct: 88, star: '⭐⭐⭐⭐⭐', note: '電力系統/工配計算核心' },
    { name: '一階/二階 RLC 暫態分析', count: '39 題', pct: 82, star: '⭐⭐⭐⭐', note: '電路學/工數三要素法' },
    { name: '變壓器等效電路與開短路試驗', count: '36 題', pct: 75, star: '⭐⭐⭐⭐', note: '電機機械/工配必考基石' },
    { name: '差動放大器與 CMRR 分析', count: '32 題', pct: 68, star: '⭐⭐⭐⭐', note: '電子學高分必備' },
    { name: '二階 ODE 與拉氏轉換求解', count: '30 題', pct: 62, star: '⭐⭐⭐⭐', note: '工程數學及格門檻' }
  ],
  '01': [
    { name: '戴維寧與諾頓等效電路', count: '18 題', pct: 90, star: '⭐⭐⭐⭐⭐', note: '含相依源測試源法' },
    { name: '一階/二階電路暫態分析', count: '16 題', pct: 82, star: '⭐⭐⭐⭐⭐', note: '開關換位與三要素' },
    { name: '三相平衡電路 (Y-Δ)', count: '14 題', pct: 70, star: '⭐⭐⭐⭐', note: '線相電壓電流轉換' }
  ],
  '02': [
    { name: '差動放大器 (Ad, Acm, CMRR)', count: '16 題', pct: 88, star: '⭐⭐⭐⭐⭐', note: '半電路分析法' },
    { name: 'DC-DC Buck/Boost 轉換器', count: '14 題', pct: 78, star: '⭐⭐⭐⭐', note: '伏秒平衡與電荷平衡' },
    { name: 'BJT/MOSFET 單級放大器', count: '12 題', pct: 65, star: '⭐⭐⭐⭐', note: '小訊號參數計算' }
  ],
  '03': [
    { name: '二階非齊次常微分方程 ODE', count: '16 題', pct: 85, star: '⭐⭐⭐⭐⭐', note: '參數變更法與未定係數' },
    { name: '拉氏轉換與反轉換求解', count: '14 題', pct: 75, star: '⭐⭐⭐⭐', note: '部分分式法與摺積' },
    { name: '矩陣特徵值與對角化', count: '12 題', pct: 68, star: '⭐⭐⭐⭐', note: '相似轉換與幾何重數' }
  ],
  '04': [
    { name: '單相/三相變壓器開短路試驗', count: '18 題', pct: 92, star: '⭐⭐⭐⭐⭐', note: '等效電路與效率計算' },
    { name: '感應電動機轉矩-轉差率曲線', count: '15 題', pct: 80, star: '⭐⭐⭐⭐', note: '戴維寧簡化與最大轉矩' },
    { name: '凸極同步發電機雙反應理論', count: '12 題', pct: 65, star: '⭐⭐⭐⭐', note: 'Xd, Xq 功角特性' }
  ],
  '05': [
    { name: '對稱分量法與不對稱故障 (SLG)', count: '20 題', pct: 95, star: '⭐⭐⭐⭐⭐', note: '正負零序網串聯' },
    { name: '輸電線路中長程模型 (ABCD)', count: '15 題', pct: 76, star: '⭐⭐⭐⭐', note: 'π 型等效與電壓調整率' },
    { name: '單機無窮母線等面積準則', count: '12 題', pct: 64, star: '⭐⭐⭐⭐', note: '臨界清除角推導' }
  ],
  '06': [
    { name: '短路容量計算 (MVA 法)', count: '16 題', pct: 88, star: '⭐⭐⭐⭐⭐', note: '串並聯容量化簡' },
    { name: '功率因數改善與電容器組', count: '14 題', pct: 78, star: '⭐⭐⭐⭐', note: '釋放容量與降損' },
    { name: '保護協調 (TCC 曲線) 定值', count: '12 題', pct: 66, star: '⭐⭐⭐⭐', note: 'CTI 時間階差設定' }
  ]
};

function renderTopTopics() {
  const container = document.getElementById('top-topics-container');
  if (!container) return;

  const list = STATS_DATA[currentStatsSubject] || STATS_DATA['all'];

  container.innerHTML = list.map(t => `
    <div style="background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 14px 18px; margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: baseline; font-size: 0.95rem; margin-bottom: 6px; color: var(--ink);">
        <span style="font-weight: 700;">${t.name}</span>
        <span style="color: var(--accent-dark); font-weight: 700; font-size: 0.9rem;">${t.count}</span>
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

function renderLayers() {
  const container = document.getElementById('layers-container');
  if (!container || typeof DB_DATA === 'undefined' || !DB_DATA.sevenLayers) return;

  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : (DB_DATA.questions || []);
  const state = typeof progressState !== 'undefined' ? progressState : {};
  const dueQids = typeof getDueQuestionsList === 'function' ? new Set(getDueQuestionsList()) : new Set();
  const getPool = (action) => questions.filter(q => {
    const qid = q[0];
    const diff = Number(q[8]) || 0;
    const status = state[qid] || 0;
    const formulaTags = Array.isArray(q[10]) ? q[10] : [];
    const hasDeduction = Boolean(q[11]);
    const tags = Array.isArray(q[5]) ? q[5] : [];
    if (action === 'formula') return formulaTags.length > 0 || tags.length >= 2;
    if (action === 'dedicated') return hasDeduction;
    if (action === 'review') return status === 2 || diff >= 4;
    if (action === 'top10') return diff >= 4 || tags.length >= 4;
    if (action === 'due') return dueQids.has(qid) || status === 2;
    return true;
  });

  container.innerHTML = DB_DATA.sevenLayers.map(layer => `
    ${(() => {
      const pool = getPool(layer.action);
      const unstable = pool.filter(q => (state[q[0]] || 0) !== 1).length;
      const percent = pool.length ? Math.round(((pool.length - unstable) / pool.length) * 100) : 0;
      const isMock = layer.action === 'mock';
      return `<div style="background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 18px 22px; margin-bottom: 14px; box-shadow: var(--shadow);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h4 style="color: var(--accent-dark); font-size: 1.05rem; font-weight: 700;">
          ${layer.id} · ${layer.title || layer.name || '未命名層級'}
        </h4>
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--muted); background: var(--bg-secondary); padding: 2px 8px; border-radius: 4px;">
          ${layer.objective || '考試得分'}
        </span>
      </div>
      <p style="font-size: 0.88rem; color: var(--ink-light); line-height: 1.6; margin-bottom: 10px;">
        ${layer.desc}
      </p>
      <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:0.82rem; color:var(--muted); margin-bottom:8px;">
        <span>${isMock ? '建議以整卷模考驗證' : `範圍 ${pool.length} 題 · 尚未穩定 ${unstable} 題`}</span>
        <span>${isMock ? '輸出訓練' : `目前穩定度 ${percent}%`}</span>
      </div>
      <div style="height:7px; background:var(--line); border-radius:9999px; overflow:hidden; margin-bottom:12px;">
        <div style="width:${isMock ? 0 : percent}%; background:var(--accent); height:100%;"></div>
      </div>
      <button class="btn-sol" type="button" onclick="focusStudyLayer('${layer.action}')">${isMock ? '前往計時模考' : '開始處理這一層'}</button>
    </div>`;
    })()}
  `).join('');
}

function focusStudyLayer(action) {
  if (action === 'mock') {
    if (typeof switchTab === 'function') switchTab('mock');
    return;
  }
  if (typeof switchTab === 'function') switchTab('questions');
  const sub = document.getElementById('filter-subject');
  const year = document.getElementById('filter-year');
  const status = document.getElementById('filter-status');
  const diff = document.getElementById('filter-diff');
  if (sub) sub.value = 'all';
  if (year) year.value = 'all';
  if (status) status.value = 'all';
  if (diff) diff.value = 'all';
  const quick = action === 'dedicated' ? 'dedicated' : action === 'review' ? 'review' : action === 'due' ? 'due' : action === 'top10' ? 'top10' : 'all';
  if (typeof setQuickFilter === 'function') setQuickFilter(quick);
  else if (typeof renderQuestions === 'function') renderQuestions();
}
