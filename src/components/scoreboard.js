// src/components/scoreboard.js — WP6 (成績 tab)
/**
 * 成績看板：每科「模考實測／練習估計／目標」、距離 360／380、錯因分布＋一行下一步、主攻／基本分得分率。
 * 純函式（scoreboardCompute 等）＋ renderScoreboard(container)。
 * Depends on: QUESTION_POINTS, TARGET_ALLOCATION, studyPlan.js, resultCardStore.js (getResultRecords).
 */

const SCOREBOARD_WINDOW_DAYS = 21;
const SCOREBOARD_MIN_QUESTIONS = 3;
const SCOREBOARD_MIN_ERRORS = 3;
const SCOREBOARD_MIN_SAME_ERRORS = 2;
const SCOREBOARD_SUBJECTS = ['01', '02', '03', '04', '05', '06'];
const SCOREBOARD_ROLE_LABELS = { high: '衝高分', combined: '合併準備', basic: '基本分' };
const SCOREBOARD_ERROR_CODES = ['R', 'S', 'F', 'C', 'K', 'U', 'T'];
const SCOREBOARD_ERROR_NAMES = { R: '題型', S: '起手式', F: '公式', C: '計算', K: '觀念', U: '單位方向', T: '時間' };
// Tie-break priority when several codes share the top count.
const SCOREBOARD_NEXT_PRIORITY = ['S', 'C', 'F', 'K', 'T', 'U', 'R'];
const SCOREBOARD_NEXT_STEPS = {
  S: '卡在起手式：先用四段蓋牌第②段與起手式急救卡',
  C: '計算錯：每題留 1 分鐘回代驗算',
  F: '公式或觀念：回到本章主攻題的核心公式',
  K: '公式或觀念：回到本章主攻題的核心公式',
  T: '時間不夠：照配分時間帽換題',
  U: '單位方向：結論前檢查單位、正負與相角',
  R: '題型判錯：先寫已知、所求、適用章節再動筆'
};
// Mock phase starts 2026-10-15 (local date); from then a subject with a mock score shows only the mock number.
const SCOREBOARD_MOCK_PHASE_KEY = 20261015;
const SCOREBOARD_PASS_SUBJECT = 60;
const SCOREBOARD_PASS_RULE_TEXT = '及格 360；若當年及格人數不足 16%，前 16% 且平均 ≥50、無零分者亦及格（110／111 年錄取線 57.3／56.8）';
const SCOREBOARD_EMPTY_TEXT = '還沒有作答結果。到「今天」或「模考」完成題目後，用作答結果卡保存，分數就會出現在這裡。';

function scoreboardEscape_(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]
  ));
}

function scoreboardRound1_(n) { return Math.round(n * 10) / 10; }

function scoreboardSubjectOf_(qid) {
  const m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(String(qid || ''));
  return m ? m[2] : null;
}

function scoreboardYearOf_(qid) {
  const m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(String(qid || ''));
  return m ? m[1] : null;
}

function scoreboardPoints_() {
  return typeof QUESTION_POINTS !== 'undefined' && QUESTION_POINTS ? QUESTION_POINTS : {};
}

function scoreboardTierOf_(qid, fallback) {
  try {
    if (typeof studyTierFor === 'function') {
      const t = studyTierFor(qid);
      if (t === 'main' || t === 'basic') return t;
    }
  } catch (_) { /* fall through */ }
  return fallback === 'basic' ? 'basic' : 'main';
}

function scoreboardTargetOf_(subjectId) {
  try { if (typeof targetFor === 'function') return targetFor(subjectId); } catch (_) { /* none */ }
  return null;
}

function scoreboardRoleOf_(subjectId) {
  try { if (typeof studyRoleFor === 'function') return studyRoleFor(subjectId); } catch (_) { /* none */ }
  return null;
}

function scoreboardNameOf_(subjectId) {
  try {
    if (typeof TARGET_ALLOCATION !== 'undefined' && TARGET_ALLOCATION.subjects[subjectId]) {
      return TARGET_ALLOCATION.subjects[subjectId].name;
    }
  } catch (_) { /* none */ }
  return '科目' + subjectId;
}

/** Share of exam points by tier for a subject over all past papers (QUESTION_POINTS + tiers). */
function scoreboardTierShares(subjectId) {
  const points = scoreboardPoints_();
  const sums = { main: 0, basic: 0 };
  Object.keys(points).forEach(qid => {
    if (scoreboardSubjectOf_(qid) !== subjectId) return;
    const total = Number(points[qid] && points[qid].total) || 0;
    sums[scoreboardTierOf_(qid)] += total;
  });
  const all = sums.main + sums.basic;
  return all > 0 ? { main: sums.main / all, basic: sums.basic / all } : { main: 0, basic: 0 };
}

function scoreboardLatestPerQuestion_(records) {
  const latest = {};
  records.forEach(r => {
    if (!latest[r.qid] || r.at >= latest[r.qid].at) latest[r.qid] = r;
  });
  return latest;
}

/**
 * Latest complete mock for one subject. When mockExam.js is loaded, completeness and the 0–100 scaling
 * come from latestMockScoreBySubject (a paper whose SCORED subset is fully answered counts; e.g. 114 配電
 * scores only 40 points and is scaled to 100). Otherwise falls back to grouping by mockId and requiring
 * every QUESTION_POINTS question of that paper. Returns { mockId, estimate (0–100), raw, rawTotal, at } or null.
 */
function scoreboardMockForSubject(records, subjectId) {
  const mockRecords = records.filter(r => r.source === 'mock' && r.mockId);
  const mockRows = typeof mockExamActiveRows === 'function' ? mockExamActiveRows() : null;
  if (typeof latestMockScoreBySubject === 'function' && mockRows) {
    try {
      const byId = latestMockScoreBySubject(mockRecords, mockRows);
      const hit = byId && byId[subjectId];
      return hit ? {
        mockId: hit.mockId, estimate: scoreboardRound1_(Number(hit.scaled) || 0),
        raw: hit.estimate, rawTotal: hit.total, at: hit.at
      } : null;
    } catch (_) { /* fall back to the local rule below */ }
  }
  const points = scoreboardPoints_();
  const groups = {};
  mockRecords.forEach(r => {
    if (scoreboardSubjectOf_(r.qid) !== subjectId) return;
    (groups[r.mockId] = groups[r.mockId] || []).push(r);
  });
  let best = null;
  Object.keys(groups).forEach(mockId => {
    const list = groups[mockId];
    const year = scoreboardYearOf_(list[0].qid);
    const expected = Object.keys(points).filter(q => scoreboardYearOf_(q) === year && scoreboardSubjectOf_(q) === subjectId);
    if (!expected.length) return;
    const latest = scoreboardLatestPerQuestion_(list);
    if (!expected.every(q => latest[q])) return;
    const estimate = expected.reduce((s, q) => s + (Number(latest[q].estimate) || 0), 0);
    const at = Math.max.apply(null, expected.map(q => latest[q].at));
    if (!best || at > best.at) best = { mockId, estimate: scoreboardRound1_(estimate), at };
  });
  return best;
}

/** Practice projection (0–100) from non-mock, non-legacy records of the window; null when < 3 questions. */
function scoreboardPracticeForSubject(windowRecords, subjectId) {
  const list = windowRecords.filter(r => r.source !== 'mock' && !r.legacy && scoreboardSubjectOf_(r.qid) === subjectId);
  const latest = scoreboardLatestPerQuestion_(list);
  const qids = Object.keys(latest);
  if (qids.length < SCOREBOARD_MIN_QUESTIONS) return { projection: null, questions: qids.length };
  const shares = scoreboardTierShares(subjectId);
  const agg = { main: { sum: 0, n: 0 }, basic: { sum: 0, n: 0 } };
  qids.forEach(q => {
    const r = latest[q];
    const total = Number(r.total) || 0;
    if (total <= 0) return;
    const tier = scoreboardTierOf_(q, r.tier);
    agg[tier].sum += (Number(r.estimate) || 0) / total;
    agg[tier].n += 1;
  });
  // Renormalise over tiers that have data so a missing tier does not drag the projection to 0.
  let weight = 0;
  let acc = 0;
  ['main', 'basic'].forEach(t => {
    if (!agg[t].n) return;
    weight += shares[t];
    acc += shares[t] * (agg[t].sum / agg[t].n);
  });
  if (weight <= 0) return { projection: null, questions: qids.length };
  return { projection: scoreboardRound1_(100 * acc / weight), questions: qids.length };
}

function scoreboardErrorsForSubject(windowRecords, subjectId) {
  const counts = {};
  SCOREBOARD_ERROR_CODES.forEach(c => { counts[c] = 0; });
  windowRecords.forEach(r => {
    if (r.legacy || scoreboardSubjectOf_(r.qid) !== subjectId) return;
    (r.errors || []).forEach(c => { if (c in counts) counts[c] += 1; });
  });
  return counts;
}

/** One 「下一步」 line from the dominant error code, or null when fewer than 3 errors and no code twice. */
function scoreboardNextStep(counts) {
  const total = SCOREBOARD_ERROR_CODES.reduce((s, c) => s + (counts[c] || 0), 0);
  const maxSame = SCOREBOARD_ERROR_CODES.reduce((m, c) => Math.max(m, counts[c] || 0), 0);
  if (total < SCOREBOARD_MIN_ERRORS && maxSame < SCOREBOARD_MIN_SAME_ERRORS) return null;
  let top = null;
  SCOREBOARD_NEXT_PRIORITY.forEach(c => {
    if (counts[c] > 0 && (top === null || counts[c] > counts[top])) top = c;
  });
  return top ? SCOREBOARD_NEXT_STEPS[top] : null;
}

function scoreboardTierRates(windowRecords, subjectId) {
  const acc = { main: { got: 0, total: 0 }, basic: { got: 0, total: 0 } };
  windowRecords.forEach(r => {
    if (r.legacy || scoreboardSubjectOf_(r.qid) !== subjectId) return;
    const total = Number(r.total) || 0;
    if (total <= 0) return;
    const tier = scoreboardTierOf_(r.qid, r.tier);
    acc[tier].got += Number(r.estimate) || 0;
    acc[tier].total += total;
  });
  const rate = a => (a.total > 0 ? Math.round(100 * a.got / a.total) : null);
  return { main: rate(acc.main), basic: rate(acc.basic) };
}

function scoreboardDangerThreshold_() {
  return typeof DANGER_SCORE_THRESHOLD !== 'undefined' ? DANGER_SCORE_THRESHOLD : 40;
}

/** Pure: should the 練習估計 be shown? Hidden only when the subject has a mock score and `now` is in the mock phase. */
function scoreboardShowPractice(hasMock, now) {
  if (!hasMock) return true;
  const d = new Date(Number.isFinite(now) ? now : Date.now());
  const key = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  return key < SCOREBOARD_MOCK_PHASE_KEY;
}

/** Pure: risk flag for a subject estimate. level 'zero' (< 40), 'low' (< 60) or null. */
function scoreboardRisk(estimate) {
  if (estimate === null || estimate === undefined || !Number.isFinite(Number(estimate))) return null;
  const v = Number(estimate);
  if (v >= SCOREBOARD_PASS_SUBJECT) return null;
  return { level: v < scoreboardDangerThreshold_() ? 'zero' : 'low', gap: scoreboardRound1_(SCOREBOARD_PASS_SUBJECT - v) };
}

/** Pure: subject with the largest (target - estimate) shortfall among rows with data; null when none is below target. */
function scoreboardDragSubject(rows) {
  let best = null;
  (rows || []).forEach(r => {
    if (!r || r.estimate === null || r.estimate === undefined) return;
    if (r.target === null || r.target === undefined) return;
    const shortfall = scoreboardRound1_(Number(r.target) - Number(r.estimate));
    if (shortfall > 0 && (!best || shortfall > best.shortfall)) best = { id: r.id, name: r.name, shortfall };
  });
  return best;
}

/** Pure: papers = [{at, scaled}] (complete mocks of one subject). Two latest by date -> {prev, cur, delta}, else null. */
function scoreboardTrend(papers) {
  const list = (papers || []).filter(p => p && Number.isFinite(Number(p.scaled)) && Number.isFinite(Number(p.at)))
    .slice().sort((a, b) => a.at - b.at);
  if (list.length < 2) return null;
  const prev = scoreboardRound1_(Number(list[list.length - 2].scaled));
  const cur = scoreboardRound1_(Number(list[list.length - 1].scaled));
  return { prev, cur, delta: scoreboardRound1_(cur - prev) };
}

function scoreboardSignedText_(n) { return (n > 0 ? '+' : (n < 0 ? '−' : '±')) + Math.abs(n); }

function scoreboardTrendText(trend) {
  return trend ? `前次 ${trend.prev} → 本次 ${trend.cur}（${scoreboardSignedText_(trend.delta)}）` : '';
}

/** Complete mock papers of a subject as [{at, scaled}] (needs mockExam.js; otherwise empty). */
function scoreboardMockPapers_(records, subjectId) {
  const rows = typeof mockExamActiveRows === 'function' ? mockExamActiveRows() : null;
  if (typeof mockExamHistory !== 'function' || !rows) return [];
  try {
    return mockExamHistory(records.filter(r => r.source === 'mock' && r.mockId), rows)
      .filter(g => g.subjectId === subjectId && g.complete && g.summary.questionCount && g.summary.total)
      .map(g => ({ at: g.at, scaled: g.summary.estimate / g.summary.total * 100 }));
  } catch (_) { return []; }
}

function scoreboardDistanceText(total, line) {
  const diff = scoreboardRound1_(line - total);
  return diff > 0 ? `還差 ${diff} 分` : `已超過 ${scoreboardRound1_(-diff)} 分`;
}

function scoreboardCompute(records, now) {
  const all = Array.isArray(records) ? records : [];
  const nowMs = Number.isFinite(now) ? now : Date.now();
  const since = nowMs - SCOREBOARD_WINDOW_DAYS * 86400000;
  const windowRecords = all.filter(r => r.at >= since && r.at <= nowMs + 86400000);
  const subjects = SCOREBOARD_SUBJECTS.map(id => {
    const mock = scoreboardMockForSubject(all, id);
    const practice = scoreboardPracticeForSubject(windowRecords, id);
    const errors = scoreboardErrorsForSubject(windowRecords, id);
    const role = scoreboardRoleOf_(id);
    return {
      id, name: scoreboardNameOf_(id), role, roleLabel: SCOREBOARD_ROLE_LABELS[role] || '',
      target: scoreboardTargetOf_(id), mock, practice: practice.projection, practiceQuestions: practice.questions,
      errors, nextStep: scoreboardNextStep(errors), rates: scoreboardTierRates(windowRecords, id),
      trend: scoreboardTrend(scoreboardMockPapers_(all, id)),
      showPractice: scoreboardShowPractice(!!mock, nowMs)
    };
  });
  const mocked = subjects.filter(s => s.mock);
  const mockTotal = mocked.length ? scoreboardRound1_(mocked.reduce((s, x) => s + x.mock.estimate, 0)) : null;
  let estTotal = 0;
  let estCount = 0;
  subjects.forEach(s => {
    const v = s.mock ? s.mock.estimate : s.practice;
    s.estimate = v;
    s.risk = scoreboardRisk(v);
    s.estimateFrom = s.mock ? 'mock' : (s.practice !== null ? 'practice' : null);
    if (v !== null && v !== undefined) { estTotal += v; estCount += 1; }
  });
  estTotal = estCount ? scoreboardRound1_(estTotal) : null;
  const withData = subjects.filter(s => s.estimate !== null && s.estimate !== undefined);
  const noData = subjects.filter(s => s.estimate === null || s.estimate === undefined);
  const targetSum = withData.reduce((n, s) => n + (Number(s.target) || 0), 0);
  const passLine = typeof PASS_LINE !== 'undefined' ? PASS_LINE : 360;
  const goal = typeof TOTAL_TARGET !== 'undefined' ? TOTAL_TARGET : 380;
  return {
    empty: all.length === 0,
    hasData: estCount > 0,
    subjects, mockTotal, mockCount: mocked.length,
    mockDistance: mocked.length === subjects.length ? { pass: scoreboardDistanceText(mockTotal, passLine), goal: scoreboardDistanceText(mockTotal, goal) } : null,
    estimateTotal: estTotal, estimateCount: estCount,
    estimateTargetTotal: targetSum > 0 ? scoreboardRound1_(targetSum) : null,
    missingNames: noData.map(s => s.name), missingCount: noData.length, subjectCount: subjects.length,
    estimateDistance: estCount === subjects.length ? { pass: scoreboardDistanceText(estTotal, passLine), goal: scoreboardDistanceText(estTotal, goal) } : null,
    drag: scoreboardDragSubject(withData),
    passLine, goal
  };
}

/** 「估計總分 X／Y（N／6 科）」: Y is the sum of the targets of the subjects that have data. */
function scoreboardSummaryFromModel_(model) {
  if (!model.hasData) return '估計總分：尚無資料';
  const y = model.estimateTargetTotal !== null && model.estimateTargetTotal !== undefined ? model.estimateTargetTotal : model.goal;
  return `估計總分 ${Math.round(model.estimateTotal)}／${Math.round(y)}（${model.estimateCount}／${model.subjectCount} 科）`;
}

function scoreboardReadRecords_(options) {
  if (options && Array.isArray(options.records)) return options.records;
  try { return typeof getResultRecords === 'function' ? getResultRecords() : []; } catch (_) { return []; }
}

/** Header one-liner: 「估計總分 X／Y（N／6 科）」 or 「估計總分：尚無資料」. */
function scoreboardSummaryLine(options) {
  return scoreboardSummaryFromModel_(scoreboardCompute(scoreboardReadRecords_(options), options && options.now));
}

function scoreboardDate_(at) {
  const d = new Date(at);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function scoreboardBarHtml_(s) {
  const pct = v => Math.max(0, Math.min(100, v));
  const mockW = s.mock ? pct(s.mock.estimate) : 0;
  const showPr = s.showPractice !== false;
  const prW = s.practice !== null ? pct(s.practice) : 0;
  const tgt = s.target !== null && s.target !== undefined ? pct(s.target) : null;
  const mockV = s.mock ? String(Math.round(s.mock.estimate)) : '—';
  const prV = s.practice !== null ? String(Math.round(s.practice)) : '—';
  return `<div class="sb-bar" aria-hidden="true">
    <div class="sb-tracks">
      <div class="sb-row"><div class="sb-track"><span class="sb-fill sb-fill--mock" style="width:${mockW}%"></span></div></div>
      ${showPr ? `<div class="sb-row"><div class="sb-track sb-track--thin"><span class="sb-fill sb-fill--practice" style="width:${prW}%"></span></div></div>` : ''}
      ${tgt !== null ? `<span class="sb-target" style="left:${tgt}%"></span>` : ''}
    </div>
    <div class="sb-vals"><span class="sb-val sb-val--mock">${mockV}</span>${showPr ? `<span class="sb-val sb-val--practice">${prV}</span>` : ''}</div>
  </div>`;
}

function scoreboardLegendHtml_() {
  return `<p class="sb-legend" aria-label="圖例"><span class="sb-legend-item"><i class="sb-swatch sb-swatch--mock"></i>模考實測</span><span class="sb-legend-item"><i class="sb-swatch sb-swatch--practice"></i>練習估計</span><span class="sb-legend-item"><i class="sb-swatch sb-swatch--target"></i>目標線</span></p>`;
}

function scoreboardSubjectHtml_(s) {
  const e = scoreboardEscape_;
  const mockText = s.mock ? `${s.mock.estimate} 分（${scoreboardDate_(s.mock.at)}）` : '未考';
  const prText = s.practice !== null ? `${Math.round(s.practice)} 分（偏樂觀）` : `再練 ${Math.max(1, SCOREBOARD_MIN_QUESTIONS - s.practiceQuestions)} 題就會顯示（需近 ${SCOREBOARD_WINDOW_DAYS} 天 ${SCOREBOARD_MIN_QUESTIONS} 題）`;
  const tgtText = s.target !== null && s.target !== undefined ? `${s.target} 分` : '—';
  const errTotal = SCOREBOARD_ERROR_CODES.reduce((n, c) => n + s.errors[c], 0);
  const errChips = SCOREBOARD_ERROR_CODES.filter(c => s.errors[c] > 0)
    .map(c => `<span class="sb-chip">${c} ${e(SCOREBOARD_ERROR_NAMES[c])} ${s.errors[c]}</span>`).join('');
  const showPr = s.showPractice !== false;
  const risk = s.risk;
  const riskHtml = risk ? `<span class="sb-risk${risk.level === 'zero' ? ' sb-risk--zero' : ''}">&lt;60</span>${risk.level === 'zero' ? '<span class="sb-risk sb-risk--zero">零分風險</span>' : ''}<span class="sb-gap">差 ${risk.gap} 分到 60</span>` : '';
  const trendText = scoreboardTrendText(s.trend);
  const rateText = r => (r === null ? '—' : `${r}%`);
  return `<article class="sb-subject" data-subject="${e(s.id)}">
    <div class="sb-subject-head"><h3>${e(s.name)}</h3><span class="sb-role sb-role--${e(s.role || '')}">${e(s.roleLabel)}</span></div>
    ${riskHtml ? `<p class="sb-riskline">${riskHtml}</p>` : ''}
    ${scoreboardBarHtml_(s)}
    <dl class="sb-nums">
      <div><dt>模考實測</dt><dd>${e(mockText)}</dd></div>
      ${showPr ? `<div><dt>練習估計</dt><dd>${e(prText)}</dd></div>` : ''}
      <div><dt>目標</dt><dd>${e(tgtText)}</dd></div>
    </dl>
    ${trendText ? `<p class="sb-trend">${e(trendText)}</p>` : ''}
    <p class="sb-rates">近 ${SCOREBOARD_WINDOW_DAYS} 天得分率：主攻 ${rateText(s.rates.main)}｜基本分 ${rateText(s.rates.basic)}</p>
    <p class="sb-errors">${errTotal ? `錯因：${errChips}` : '錯因：近期無記錄'}</p>
    ${s.nextStep ? `<p class="sb-next"><strong>下一步</strong>　${e(s.nextStep)}</p>` : ''}
  </article>`;
}

function scoreboardDragText(drag) {
  return drag ? `最可能拖垮平均的科目：${drag.name}（低於目標 ${drag.shortfall} 分）` : '各科都在目標之上';
}

function scoreboardDragHtml_(m) {
  if (!m.hasData) return '';
  return `<p class="sb-drag">${scoreboardEscape_(scoreboardDragText(m.drag))}</p>`;
}

function scoreboardTotalsHtml_(m) {
  const e = scoreboardEscape_;
  const missing = m.subjects.filter(s => s.mock === null).map(s => s.name);
  const mockLine = m.mockCount
    ? `${m.mockTotal} 分${m.mockCount < m.subjects.length ? `（${m.mockCount}／${m.subjects.length} 科，未考：${missing.join('、')}）` : ''}`
    : '尚無整卷模考';
  const mockDist = m.mockDistance
    ? `距 ${m.passLine}：${m.mockDistance.pass}；距 ${m.goal}：${m.mockDistance.goal}`
    : (m.mockCount ? `尚有 ${m.subjects.length - m.mockCount} 科未考，湊齊六科才算距離` : '');
  let estLine = '尚無資料';
  let estDist = `尚有 ${m.missingCount} 科無資料`;
  if (m.hasData) {
    const y = m.estimateTargetTotal !== null && m.estimateTargetTotal !== undefined ? m.estimateTargetTotal : m.goal;
    estLine = `估計總分 ${m.estimateTotal}／${y}（${m.estimateCount}／${m.subjectCount} 科）`;
    estDist = m.estimateDistance
      ? `距 ${m.passLine}：${m.estimateDistance.pass}；距 ${m.goal}：${m.estimateDistance.goal}`
      : `尚有 ${m.missingCount} 科無資料：${m.missingNames.join('、')}`;
  }
  return `<section class="sb-totals" aria-label="合計">
    <div class="sb-total"><span class="sb-total-label">模考實測合計</span><strong>${e(mockLine)}</strong><small>${e(mockDist)}</small></div>
    <div class="sb-total"><span class="sb-total-label">預估總分（有模考用模考，否則用練習估計）</span><strong>${e(estLine)}</strong><small>${e(estDist)}</small></div>
    ${scoreboardDragHtml_(m)}
  </section>`;
}

function renderScoreboard(container, options) {
  if (!container) return null;
  const model = scoreboardCompute(scoreboardReadRecords_(options), options && options.now);
  const body = model.empty
    ? `<p class="sb-empty">${scoreboardEscape_(SCOREBOARD_EMPTY_TEXT)}</p>`
    : `${scoreboardTotalsHtml_(model)}<div class="sb-grid">${model.subjects.map(scoreboardSubjectHtml_).join('')}</div>
       <p class="sb-note">模考實測為準；練習估計來自近 ${SCOREBOARD_WINDOW_DAYS} 天、自己挑的章節且無時間壓力，偏樂觀。練習中的基本分題 ○ 只計 50%；模考一律照真實考試計分（○ 100%）。</p>`;
  container.innerHTML = `<section class="scoreboard" aria-label="成績看板">
    <h2 class="sb-title">成績</h2>
    <p class="sb-summary">${scoreboardEscape_(scoreboardSummaryFromModel_(model))}</p><p class="sb-rule"><small>${scoreboardEscape_(SCOREBOARD_PASS_RULE_TEXT)}</small></p>${model.empty ? '' : scoreboardLegendHtml_()}${body}</section>`;
  return model;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    scoreboardCompute, scoreboardSummaryLine, scoreboardTierShares, scoreboardMockForSubject,
    scoreboardPracticeForSubject, scoreboardNextStep, scoreboardDragSubject, scoreboardDragText,
    scoreboardTrend, scoreboardTrendText, scoreboardRisk, scoreboardShowPractice, scoreboardEscape_, renderScoreboard
  };
}
