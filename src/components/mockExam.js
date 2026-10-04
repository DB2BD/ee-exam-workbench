// src/components/mockExam.js — WP5b (模考分頁；無任何計時器，使用者自行手動計時)
/**
 * 流程：選卷（年度 × 科目，或 114 模考／108 盲測捷徑）→ 試卷（官方 PDF、每題裁切圖、配分、
 * 第一輪時間帽）→ 交卷 → 逐題題解連結與結果卡 → 全部保存後出總結與「先修這題」。
 * 模考紀錄存成結果紀錄（mockId 欄位），成績分頁以 latestMockScoreBySubject 取模考實測。
 * 純函式（可在 node 測試）與 DOM 分開；整個 #tab-pane-mock 由本檔於載入時渲染。
 */

const MOCK_EXAM_YEARS = [114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104];
const MOCK_EXAM_TIME_CAP_PER_POINT = 0.9;
const MOCK_EXAM_REMINDER = '5 分鐘掃卷＋90 分鐘第一輪＋17 分鐘搶分＋8 分鐘收尾';
const MOCK_EXAM_LEGACY_HISTORY_KEY = 'EE_MOCK_EXAM_HISTORY_V1';
const MOCK_EXAM_FALLBACK_SUBJECTS = [
  { id: '01', name: '電路學' },
  { id: '02', name: '電子學（含電力電子）' },
  { id: '03', name: '工程數學' },
  { id: '04', name: '電機機械' },
  { id: '05', name: '電力系統' },
  { id: '06', name: '工業配電' }
];
// 只計部分題的試卷（出處：docs/上榜被動模考_114年六科執行包.md、上榜被動複測_108年六科執行包.md）。
// 其餘題只作邊界練習：照樣顯示題目與題解，但不評分、不計入總分。
const MOCK_EXAM_SCORED_SUBSETS = {
  '114-06': {
    qids: ['EE-114-06-1', 'EE-114-06-5'],
    note: '114 年工業配電只計第 1、5 題（各 20 分，合計 40 分）；第 2、3、4 題只作邊界練習，不評分、不計入本卷估計，總分以 40 分為滿分，不換算成 100 分。'
  },
  '108-02': {
    qids: ['EE-108-02-1', 'EE-108-02-2', 'EE-108-02-3', 'EE-108-02-4'],
    note: '108 年電子學只計第 1～4 題（各 20 分，合計 80 分）；第 5 題只作邊界練習，不評分、不計入本卷估計，總分以 80 分為滿分，不換算成 100 分。'
  }
};

let mockExamState = null;

function mockExamEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]
  ));
}

function mockExamRound(value) {
  return Math.round((Number(value) || 0) * 100) / 100;
}

function mockExamFormat(value) {
  const n = mockExamRound(value);
  return Number.isInteger(n) ? String(n) : String(n);
}

/** 第一輪時間帽：0.9 分鐘 × 配分（四捨五入到 0.1 分鐘）。 */
function mockExamTimeCap(points) {
  return Math.round(Number(points) * MOCK_EXAM_TIME_CAP_PER_POINT * 10) / 10;
}

function mockExamQidNumber(qid) {
  const m = /-(\d+)$/.exec(String(qid || ''));
  return m ? Number(m[1]) : 0;
}

function mockExamQidParts(qid) {
  const m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(String(qid || ''));
  return m ? { year: m[1], sid: m[2], num: Number(m[3]) } : null;
}

/** 與 todayTaskPdfUrl 相同：取檔名，指向 data/official_pdfs/pe/。 */
function mockExamPdfUrl(pdf) {
  if (!pdf) return '';
  const name = String(pdf).split('/').pop();
  return name ? 'data/official_pdfs/pe/' + encodeURIComponent(name) : '';
}

function mockExamPoints(qid, pointsTable) {
  const table = pointsTable || (typeof QUESTION_POINTS !== 'undefined' ? QUESTION_POINTS : null);
  const entry = table && table[qid];
  return entry && Number.isFinite(Number(entry.total)) ? Number(entry.total) : 0;
}

/**
 * 組卷。rows 為 DB_DATA.questions 的列 [qid, sid, year, num, topic, tags, solLink, pdfLink, ...]。
 * 回傳題目（依題號）、配分、時間帽、是否計分，以及總分／計分總分。
 */
function mockExamPaper(rows, year, subjectId, pointsTable) {
  const y = String(year);
  const sid = String(subjectId);
  const list = (rows || []).filter(r => r && String(r[1]) === sid && String(r[2]) === y)
    .sort((a, b) => Number(a[3]) - Number(b[3]));
  const subset = MOCK_EXAM_SCORED_SUBSETS[`${y}-${sid}`] || null;
  const items = list.map(r => {
    const points = mockExamPoints(r[0], pointsTable);
    const scored = !subset || subset.qids.indexOf(r[0]) >= 0;
    return {
      qid: r[0], num: Number(r[3]), points, timeCap: mockExamTimeCap(points), scored,
      topic: r[4], solLink: r[6], pdfLink: r[7]
    };
  });
  const total = items.reduce((s, it) => s + it.points, 0);
  const scoredTotal = items.filter(it => it.scored).reduce((s, it) => s + it.points, 0);
  return {
    key: `${y}-${sid}`, year: y, subjectId: sid, items, total, scoredTotal,
    scoredQids: items.filter(it => it.scored).map(it => it.qid),
    scoringNote: subset ? subset.note : '',
    pdfUrl: list.length ? mockExamPdfUrl(list[0][7]) : '',
    reminder: MOCK_EXAM_REMINDER
  };
}

function mockExamNewId(year, subjectId, timestamp) {
  return `${year}-${subjectId}-${Number.isFinite(Number(timestamp)) ? Number(timestamp) : Date.now()}`;
}

function mockExamParseId(mockId) {
  const m = /^(\d+)-(\d+)-(\d+)$/.exec(String(mockId || ''));
  return m ? { year: m[1], subjectId: m[2], timestamp: Number(m[3]) } : null;
}

/** 同一題多筆紀錄取最新一筆。 */
function mockExamLatestPerQid(records) {
  const byQid = {};
  (records || []).forEach(r => {
    if (!r || !r.qid) return;
    if (!byQid[r.qid] || Number(r.at) >= Number(byQid[r.qid].at)) byQid[r.qid] = r;
  });
  return byQid;
}

/**
 * 單一模考（同 mockId）的紀錄 → 總結。
 * 先修這題＝△／× 的題目中配分最高者；同分取題號最早者。
 */
function mockExamSummary(records) {
  const byQid = mockExamLatestPerQid(records);
  const qids = Object.keys(byQid).sort((a, b) => mockExamQidNumber(a) - mockExamQidNumber(b));
  const perQuestion = qids.map(qid => {
    const r = byQid[qid];
    const marks = (r.parts || []).map(p => p.mark);
    const parts = (r.parts || []).map(p => ({ label: String(p.label == null ? '' : p.label), mark: p.mark }));
    const total = Number.isFinite(Number(r.total)) ? Number(r.total) : (r.parts || []).reduce((s, p) => s + Number(p.points || 0), 0);
    const weak = marks.some(m => m === 'x' || m === 'tri');
    return {
      qid, num: mockExamQidNumber(qid), estimate: mockExamRound(r.estimate), total, marks, parts,
      weak, errors: (r.errors || []).slice(), at: Number(r.at) || 0
    };
  });
  const errorTally = {};
  perQuestion.forEach(q => q.errors.forEach(code => { errorTally[code] = (errorTally[code] || 0) + 1; }));
  let fixFirst = null;
  perQuestion.forEach(q => {
    if (!q.weak) return;
    if (!fixFirst || q.total > fixFirst.total) fixFirst = q;
  });
  return {
    questionCount: perQuestion.length,
    estimate: mockExamRound(perQuestion.reduce((s, q) => s + q.estimate, 0)),
    total: perQuestion.reduce((s, q) => s + q.total, 0),
    perQuestion, errorTally,
    fixFirst: fixFirst ? { qid: fixFirst.qid, num: fixFirst.num, total: fixFirst.total, estimate: fixFirst.estimate } : null,
    at: perQuestion.reduce((m, q) => Math.max(m, q.at), 0)
  };
}

function mockExamExpectedQids(year, subjectId, rows, pointsTable) {
  if (!rows) return null;
  const paper = mockExamPaper(rows, year, subjectId, pointsTable);
  return paper.items.length ? paper.scoredQids : null;
}

function mockExamActiveRows() {
  return typeof DB_DATA !== 'undefined' && DB_DATA && DB_DATA.questions ? DB_DATA.questions : null;
}

/** 依 mockId 分組所有模考紀錄，回傳每份模考的總結與完成度。 */
function mockExamGroups(records, rows, pointsTable) {
  const groups = {};
  (records || []).forEach(r => {
    if (!r || !r.mockId) return;
    (groups[r.mockId] = groups[r.mockId] || []).push(r);
  });
  return Object.keys(groups).map(mockId => {
    const parsed = mockExamParseId(mockId);
    const summary = mockExamSummary(groups[mockId]);
    const parts = mockExamQidParts(groups[mockId][0].qid);
    const year = parsed ? parsed.year : (parts ? parts.year : '');
    const subjectId = parsed ? parsed.subjectId : (parts ? parts.sid : '');
    const expected = mockExamExpectedQids(year, subjectId, rows, pointsTable);
    const saved = summary.perQuestion.map(q => q.qid);
    const complete = expected ? expected.every(q => saved.indexOf(q) >= 0) : true;
    return {
      mockId, year, subjectId, at: summary.at || (parsed ? parsed.timestamp : 0),
      summary, complete, expectedCount: expected ? expected.length : saved.length
    };
  }).sort((a, b) => b.at - a.at);
}

/** 歷史清單（新到舊）；未評完的標記 complete:false。 */
function mockExamHistory(records, rows, pointsTable) {
  return mockExamGroups(records, rows, pointsTable);
}

/**
 * 給成績分頁：每科最近一次「評完」的整卷模考。
 * 回傳 { [subjectId]: { mockId, year, estimate, total, scaled(0-100), at } }。
 * 只計分子集（如 114 配電 40 分）時 total 為 40，scaled 已換算成百分制供與其他科比較。
 */
function latestMockScoreBySubject(records, rows, pointsTable) {
  const out = {};
  const groups = mockExamGroups(records, rows === undefined ? mockExamActiveRows() : rows, pointsTable);
  groups.forEach(g => {
    if (!g.complete || !g.summary.questionCount) return;
    const cur = out[g.subjectId];
    if (cur && cur.at >= g.at) return;
    out[g.subjectId] = {
      mockId: g.mockId, year: g.year, estimate: g.summary.estimate, total: g.summary.total,
      scaled: g.summary.total ? mockExamRound(g.summary.estimate / g.summary.total * 100) : 0,
      at: g.at
    };
  });
  return out;
}

/** 114 模考／108 盲測捷徑：由排程代碼導出（MOCK114-0x、BLIND108-0x → 年度、科目）。 */
function mockExamShortcuts(schedule) {
  const tasks = schedule && schedule.tasks ? schedule.tasks : {};
  const make = (kind, label, year) => ({
    kind, label, year,
    items: Object.keys(tasks).filter(code => tasks[code].kind === kind).map(code => {
      const p = mockExamQidParts((tasks[code].qids || [])[0]);
      return { code, year: p ? p.year : String(year), sid: p ? p.sid : '', title: tasks[code].subject || tasks[code].title || code };
    })
  });
  return [make('mock114', '114 年模考', 114), make('blind108', '108 年盲測', 108)];
}

function mockExamCropUrl(qid) {
  const crop = typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[qid] || '' : '';
  if (!crop) return '';
  return typeof resolveImageMapUrl === 'function' ? resolveImageMapUrl(crop, false, qid) : crop;
}

function mockExamSubjects() {
  const list = typeof DB_DATA !== 'undefined' && DB_DATA && DB_DATA.meta && DB_DATA.meta.subjects;
  return Array.isArray(list) && list.length ? list : MOCK_EXAM_FALLBACK_SUBJECTS;
}

function mockExamSubjectName(sid) {
  const s = mockExamSubjects().find(x => String(x.id) === String(sid));
  return s ? s.name : sid;
}

function mockExamLegacyHistory() {
  try {
    if (typeof localStorage === 'undefined') return [];
    const raw = localStorage.getItem(MOCK_EXAM_LEGACY_HISTORY_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch (_) {
    return [];
  }
}

function mockExamDateText(ms) {
  const d = new Date(ms);
  if (isNaN(d.getTime())) return '';
  const p = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

// ---------------------------------------------------------------- DOM

function mockExamHost() {
  return typeof document !== 'undefined' ? document.getElementById('tab-pane-mock') : null;
}

function mockExamRecords() {
  try { return typeof getResultRecords === 'function' ? getResultRecords({ source: 'mock' }) : []; } catch (_) { return []; }
}

function mockExamSolutionButton(item, label) {
  return `<button type="button" class="mock-btn mock-btn-sol" data-mock-solution="${mockExamEscape(item.qid)}">${label || '看題解'}</button>`;
}

const MOCK_EXAM_MARK_SYMBOL = { o: '○', tri: '△', x: '×' };

/** Same text as mockExamMarksText, each ○△× wrapped in a semantic-colour span (data-mark). */
function mockExamMarksHtml(q) {
  const parts = (q && q.parts) || [];
  if (!parts.length) return '';
  const sym = m => `<span class="mark-sym" data-mark="${MOCK_EXAM_MARK_SYMBOL[m] ? m : ''}">${MOCK_EXAM_MARK_SYMBOL[m] || '？'}</span>`;
  if (parts.length === 1) return sym(parts[0].mark);
  return parts.map(p => (p.label ? mockExamEscape(p.label) + ' ' : '') + sym(p.mark)).join('　');
}

/** 每個子題的實際標記：單一整題只顯示符號，多子題顯示「（一）○ （二）△」。 */
function mockExamMarksText(q) {
  const parts = (q && q.parts) || [];
  if (!parts.length) return '';
  const sym = m => MOCK_EXAM_MARK_SYMBOL[m] || '？';
  if (parts.length === 1) return sym(parts[0].mark);
  return parts.map(p => (p.label ? p.label + ' ' : '') + sym(p.mark)).join('　');
}

let mockExamInlineHandles = {};

function mockExamCloseInline(qid) {
  const h = mockExamInlineHandles[qid];
  if (h && typeof h.close === 'function') h.close();
  delete mockExamInlineHandles[qid];
  const mount = typeof document !== 'undefined' ? document.querySelector(`[data-mock-card="${qid}"]`) : null;
  if (mount) mount.innerHTML = '';
}

/** 打開題解並把這題的結果卡停靠在題解視窗內（交卷後、尚未保存的計分題）。 */
function mockExamOpenSolution(qid) {
  const r = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
  if (!r || typeof openSolutionModal !== 'function') return;
  openSolutionModal(null, r[6], qid, r[3], { mode: 'browse' });
  const st = mockExamState;
  if (!st || st.phase !== 'grading' || !st.mockId || typeof openResultCard !== 'function') return;
  const paper = mockExamPaperNow();
  const item = paper.items.find(it => it.qid === qid);
  if (!item || !item.scored || mockExamLatestPerQid(mockExamSavedRecords())[qid]) return;
  const mockId = st.mockId;
  openResultCard({
    qid, source: 'mock', mockId,
    onSaved: () => { mockExamCloseInline(qid); mockExamUpdateProgress(paper); }
  });
  // 題解關閉後，行內結果卡依已保存的紀錄重新呈現。
  const modal = document.getElementById('solution-modal');
  if (modal && typeof MutationObserver !== 'undefined') {
    const obs = new MutationObserver(() => {
      if (modal.classList.contains('show')) return;
      obs.disconnect();
      paper.items.forEach(it => { if (mockExamLatestPerQid(mockExamSavedRecords())[it.qid]) mockExamCloseInline(it.qid); });
      mockExamUpdateProgress(paper);
    });
    obs.observe(modal, { attributes: true, attributeFilter: ['class'] });
  }
}

function mockExamPickerHtml() {
  const st = mockExamState;
  const subjects = mockExamSubjects();
  const sched = typeof DAILY_SCHEDULE !== 'undefined' ? DAILY_SCHEDULE : null;
  const shortcuts = mockExamShortcuts(sched).filter(s => s.items.length);
  const shortcutHtml = shortcuts.map(s => `
    <div class="mock-shortcut">
      <strong>${mockExamEscape(s.label)}</strong>
      ${s.items.map(it => `<button type="button" class="mock-chip" data-mock-pick="${mockExamEscape(it.year)}:${mockExamEscape(it.sid)}" title="排程代碼 ${mockExamEscape(it.code)}">${mockExamEscape(it.code)} ${mockExamEscape(it.title)}</button>`).join('')}
    </div>`).join('');
  return `
    <div class="mock-picker">
      <label>年度
        <select id="mock-year">${MOCK_EXAM_YEARS.map(y => `<option value="${y}"${String(y) === st.year ? ' selected' : ''}>${y} 年</option>`).join('')}</select>
      </label>
      <label>科目
        <select id="mock-subject">${subjects.map(s => `<option value="${mockExamEscape(s.id)}"${String(s.id) === st.sid ? ' selected' : ''}>${mockExamEscape(s.id)}. ${mockExamEscape(s.name)}</option>`).join('')}</select>
      </label>
      <button type="button" class="mock-btn mock-btn-primary" data-mock-load>載入試卷</button>
    </div>
    <div class="mock-shortcuts">${shortcutHtml}</div>`;
}

function mockExamPaperHtml(paper) {
  const st = mockExamState;
  const graded = st.phase === 'grading';
  const rows = mockExamActiveRows() || [];
  if (!paper.items.length) return '<p class="mock-empty">查無這份試卷的題目。</p>';
  const scoreText = paper.scoredTotal === paper.total ? `${paper.total} 分` : `計分 ${paper.scoredTotal} 分（全卷 ${paper.total} 分）`;
  const head = `
    <div class="mock-paper-head">
      <h3>${mockExamEscape(paper.year)} 年 ${mockExamEscape(mockExamSubjectName(paper.subjectId))}</h3>
      <p class="mock-meta">共 ${paper.items.length} 題 · ${scoreText}</p>
      <p class="mock-reminder">${mockExamEscape(paper.reminder)}（共 120 分鐘；請自行計時）</p>
      ${paper.scoringNote ? `<p class="mock-scoring-note" role="note">${mockExamEscape(paper.scoringNote)}</p>` : ''}
      <div class="mock-paper-actions">
        ${paper.pdfUrl ? `<a class="mock-btn" href="${mockExamEscape(paper.pdfUrl)}" target="_blank" rel="noopener">開啟官方試卷 PDF</a>` : ''}
        ${graded ? '<span class="mock-total" id="mock-running-total" aria-live="polite"></span>' : '<button type="button" class="mock-btn mock-btn-primary" data-mock-submit>交卷</button>'}
      </div>
    </div>`;
  const cards = paper.items.map(it => {
    const crop = mockExamCropUrl(it.qid);
    const cap = `第一輪時間帽 ≈ ${mockExamFormat(it.timeCap)} 分鐘`;
    return `
    <article class="mock-q${it.scored ? '' : ' mock-q-unscored'}" data-mock-q="${mockExamEscape(it.qid)}">
      <div class="mock-q-head">
        <span class="mock-q-title">第 ${it.num} 題 <small>${mockExamEscape(it.qid)}</small></span>
        <span class="mock-q-points">${it.scored ? `${mockExamFormat(it.points)} 分` : '不計分（邊界練習）'}</span>
        <span class="mock-q-cap">${mockExamEscape(cap)}</span>
      </div>
      ${crop ? `<img class="mock-q-crop" src="${mockExamEscape(crop)}" alt="${mockExamEscape(it.qid)} 本題裁切圖" loading="lazy">` : '<p class="mock-empty">尚未建立本題裁切圖，請看官方 PDF。</p>'}
      ${graded ? `<div class="mock-q-after">${mockExamSolutionButton(it)}<span class="mock-q-state" data-mock-state="${mockExamEscape(it.qid)}"></span></div><div class="mock-q-card" data-mock-card="${mockExamEscape(it.qid)}"></div>` : ''}
    </article>`;
  }).join('');
  return head + `<div class="mock-q-list">${cards}</div>` + (graded ? '<div id="mock-summary"></div>' : '');
}

function mockExamHistoryHtml() {
  const rows = mockExamActiveRows();
  const hist = mockExamHistory(mockExamRecords(), rows);
  const legacy = mockExamLegacyHistory();
  let body = '';
  if (!hist.length) body += '<p class="mock-empty">尚無模考紀錄。交卷並評完所有題目後會出現在這裡。</p>';
  else {
    body += '<table class="mock-history-table"><thead><tr><th>日期</th><th>試卷</th><th>本卷估計</th></tr></thead><tbody>' + hist.map(h => `
      <tr><td>${mockExamEscape(mockExamDateText(h.at))}</td>
      <td>${mockExamEscape(h.year)} 年 ${mockExamEscape(mockExamSubjectName(h.subjectId))}</td>
      <td>${h.complete ? `<strong>${mockExamFormat(h.summary.estimate)}／${mockExamFormat(h.summary.total)}</strong>` : `<span class="mock-incomplete">未評完（${h.summary.questionCount}／${h.expectedCount} 題）</span>`}</td></tr>`).join('') + '</tbody></table>';
  }
  if (legacy.length) {
    body += '<h4 class="mock-legacy-title">舊版紀錄（唯讀）</h4><table class="mock-history-table mock-legacy"><thead><tr><th>日期</th><th>試卷</th><th>當時自評</th></tr></thead><tbody>' + legacy.slice(0, 20).map(item => `
      <tr><td>${mockExamEscape(item && item.date ? mockExamDateText(item.date) : '')}</td>
      <td>${mockExamEscape(item && item.year)} 年 ${mockExamEscape(item && item.subjectName)}</td>
      <td>${mockExamEscape(item && item.score)} 分</td></tr>`).join('') + '</tbody></table>';
  }
  return `<section class="mock-history"><h3>模考紀錄</h3>${body}</section>`;
}

function mockExamPaperNow() {
  return mockExamPaper(mockExamActiveRows(), mockExamState.year, mockExamState.sid);
}

function mockExamRender() {
  const host = mockExamHost();
  if (!host) return;
  if (!mockExamState) mockExamState = { year: '114', sid: '01', phase: 'pick', mockId: null, loaded: false };
  const st = mockExamState;
  const paper = st.loaded ? mockExamPaperNow() : null;
  mockExamInlineHandles = {};
  host.innerHTML = `
    <div class="mock-exam-box" id="mock-exam-root">
      <h2 class="mock-title">模考</h2>
      <p class="mock-sub">整卷閉卷、自己手動計時；交卷後逐題標 ○△×，系統只估分、標出先修題。</p>
      ${mockExamPickerHtml()}
      <div id="mock-paper">${paper ? mockExamPaperHtml(paper) : ''}</div>
      <div id="mock-history">${mockExamHistoryHtml()}</div>
    </div>`;
  if (paper && st.phase === 'grading') mockExamMountCards(paper);
}

function mockExamSavedRecords() {
  const st = mockExamState;
  return mockExamRecords().filter(r => r.mockId === st.mockId);
}

function mockExamUpdateProgress(paper) {
  const saved = mockExamLatestPerQid(mockExamSavedRecords());
  paper.items.forEach(it => {
    const stateEl = document.querySelector(`[data-mock-state="${it.qid}"]`);
    if (stateEl) {
      const r = saved[it.qid];
      stateEl.textContent = !it.scored ? '邊界練習：只核對假設與條件式' : (r ? `已保存：${mockExamFormat(r.estimate)}／${mockExamFormat(r.total)} 分` : '尚未評分');
    }
  });
  const sum = mockExamSummary(Object.keys(saved).filter(q => paper.scoredQids.indexOf(q) >= 0).map(q => saved[q]));
  const totalEl = document.getElementById('mock-running-total');
  if (totalEl) totalEl.textContent = `本卷估計 ${mockExamFormat(sum.estimate)}／${mockExamFormat(paper.scoredTotal)}（已評 ${sum.questionCount}／${paper.scoredQids.length} 題）`;
  const done = paper.scoredQids.every(q => saved[q]);
  // A full scored paper also completes the matching scheduled MOCK114-0N / BLIND108-0N task.
  if (done && paper.scoredQids.length && mockExamState && mockExamState.mockId && !mockExamState.syncedCode
      && typeof todayTaskSyncMockCompletion === 'function') {
    try { mockExamState.syncedCode = todayTaskSyncMockCompletion(paper.year, paper.subjectId, Date.now()) || ''; } catch (_) { /* best-effort */ }
  }
  const box = document.getElementById('mock-summary');
  if (box) box.innerHTML = done ? mockExamSummaryHtml(paper, sum) : '';
  const hist = document.getElementById('mock-history');
  if (hist) hist.innerHTML = mockExamHistoryHtml();
}

function mockExamSummaryHtml(paper, sum) {
  const tally = Object.keys(sum.errorTally).sort((a, b) => sum.errorTally[b] - sum.errorTally[a] || a.localeCompare(b));
  const labels = typeof RESULT_CARD_ERROR_LABELS !== 'undefined' ? RESULT_CARD_ERROR_LABELS : {};
  const fix = sum.fixFirst;
  return `
    <section class="mock-summary" aria-label="本卷總結">
      <h3>本卷估計 ${mockExamFormat(sum.estimate)}／${mockExamFormat(paper.scoredTotal)}</h3>
      ${mockExamState && mockExamState.syncedCode ? `<p class="mock-sync-notice" role="status">已同步完成排程任務 ${mockExamEscape(mockExamState.syncedCode)}</p>` : ''}
      <ul class="mock-summary-list">${sum.perQuestion.map(q => `<li>第 ${q.num} 題：${mockExamFormat(q.estimate)}／${mockExamFormat(q.total)} 分 <span class="${q.weak ? 'mock-weak' : 'mock-ok'}">${mockExamMarksHtml(q)}</span></li>`).join('')}</ul>
      <p class="mock-tally"><strong>錯因統計：</strong>${tally.length ? tally.map(c => `${mockExamEscape(c)} ${mockExamEscape(labels[c] || '')} ×${sum.errorTally[c]}`).join('、') : '未選錯因'}</p>
      ${fix ? `<div class="mock-fixfirst"><strong>先修這題：第 ${fix.num} 題（${mockExamEscape(fix.qid)}，${mockExamFormat(fix.total)} 分）</strong><span>△／× 中配分最高；同分取題號最早。</span>${mockExamSolutionButton({ qid: fix.qid }, '開啟這題題解')}</div>` : '<p class="mock-fixfirst mock-fixfirst-none">沒有 △／× 的題目；仍請從最不確定的一題重寫一次。</p>'}
      <button type="button" class="mock-btn" data-mock-reset>換一份試卷</button>
    </section>`;
}

function mockExamMountCards(paper) {
  const st = mockExamState;
  paper.items.forEach(it => {
    if (!it.scored) return;
    const mount = document.querySelector(`[data-mock-card="${it.qid}"]`);
    if (!mount || typeof openResultCard !== 'function') return;
    const saved = mockExamLatestPerQid(mockExamSavedRecords())[it.qid];
    if (saved) return;
    mockExamInlineHandles[it.qid] = openResultCard({
      qid: it.qid, source: 'mock', mockId: st.mockId, mount,
      onSaved: () => { delete mockExamInlineHandles[it.qid]; mockExamUpdateProgress(paper); }
    });
  });
  mockExamUpdateProgress(paper);
}

function mockExamSubmit() {
  const st = mockExamState;
  if (!st || !st.loaded) return;
  const paper = mockExamPaperNow();
  if (!paper.items.length) return;
  st.phase = 'grading';
  st.syncedCode = '';
  st.mockId = mockExamNewId(st.year, st.sid, Date.now());
  mockExamRender();
}

function mockExamLoad(year, sid) {
  if (year) mockExamState.year = String(year);
  if (sid) mockExamState.sid = String(sid);
  mockExamState.phase = 'paper';
  mockExamState.loaded = true;
  mockExamState.mockId = null;
  mockExamRender();
}

function mockExamOnClick(event) {
  const t = event.target && event.target.closest ? event.target.closest('button') : null;
  const host = mockExamHost();
  if (!t || !host || !host.contains(t)) return;
  if (t.hasAttribute('data-mock-load')) {
    const y = document.getElementById('mock-year');
    const s = document.getElementById('mock-subject');
    mockExamLoad(y && y.value, s && s.value);
  } else if (t.hasAttribute('data-mock-pick')) {
    const [y, s] = t.getAttribute('data-mock-pick').split(':');
    mockExamLoad(y, s);
  } else if (t.hasAttribute('data-mock-submit')) {
    mockExamSubmit();
  } else if (t.hasAttribute('data-mock-solution')) {
    mockExamOpenSolution(t.getAttribute('data-mock-solution'));
  } else if (t.hasAttribute('data-mock-reset')) {
    mockExamState.loaded = false;
    mockExamState.phase = 'pick';
    mockExamRender();
    host.scrollIntoView && host.scrollIntoView({ block: 'start' });
  }
}

function initMockExam() {
  const host = mockExamHost();
  if (!host || host.__mockExamReady) return;
  host.__mockExamReady = true;
  host.addEventListener('click', mockExamOnClick);
  mockExamRender();
  // Records can be added elsewhere (scheduled MOCK/BLIND tasks): refresh the history whenever the tab is shown.
  if (typeof MutationObserver !== 'undefined') {
    new MutationObserver(() => {
      if (host.style.display === 'none') return;
      const hist = document.getElementById('mock-history');
      if (hist) hist.innerHTML = mockExamHistoryHtml();
    }).observe(host, { attributes: true, attributeFilter: ['style'] });
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initMockExam);
  else initMockExam();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    MOCK_EXAM_YEARS, MOCK_EXAM_REMINDER, MOCK_EXAM_SCORED_SUBSETS,
    mockExamTimeCap, mockExamPdfUrl, mockExamPaper, mockExamNewId, mockExamParseId,
    mockExamSummary, mockExamMarksText, mockExamHistory, latestMockScoreBySubject, mockExamShortcuts, initMockExam
  };
}
