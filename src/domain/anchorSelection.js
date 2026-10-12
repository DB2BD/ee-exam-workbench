// src/domain/anchorSelection.js
/**
 * v1.3.8 「基本分拿好拿滿」選題演算法：每科 2 個錨章（穩拿題型）、錨章內分層佇列、
 * FOCUS 動態挑題、到期複習排序、科目優先值。
 *
 * 純函式：無 DOM、無儲存、無亂數。所有輸入經 `anchorContext(overrides)` 收集，測試可整包覆寫。
 * 同一份 ctx 必得同一結果（所有排序都有固定的最後鍵，與輸入順序無關）。
 *
 * ctx 欄位（皆可覆寫）：
 *   now                  毫秒時間戳
 *   questions            [{ id, subject, year, chapter, points, status, crop }]（預設取 DB_DATA 等全域）
 *   allocation           TARGET_ALLOCATION 形狀：{ subjects: { '01': { target, mainChapters, sharedChapters } } }
 *   records              作答結果卡紀錄（含 legacy）
 *   dueQids              SM-2 到期題
 *   dueDates             { qid: 'YYYY-MM-DD' }（SM-2 下次複習日，排序用）
 *   locked / reserved    未完成模考卷保留題／未完成 CORE、MAIN 的固定題（陣列或具 has() 的物件）
 *   completionByQuestion { qid: 時間戳 }（只用於冷卻，不當作掌握度證據）
 *   estimates            { subjectId: 估計分 }（科目優先值用）
 *   schedule             DAILY_SCHEDULE 形狀（FOCUS 輪數用）
 *
 * Depends (call time only, all optional): DB_DATA, QUESTION_TAXONOMY_MAP, QUESTION_POINTS, QUESTION_CROP_MAP,
 * TARGET_ALLOCATION, getResultRecords, getDueQuestionsList, sm2Schedule, practiceLockedQids,
 * practiceReservedQids, scoreboardCompute, DAILY_SCHEDULE.
 */

// ---- Parameters (WORKPLAN v1.3.8「參數」) ---------------------------------------
const ANCHORS_PER_SUBJECT = 2;
const PRIOR_M0 = 0.2;
const PRIOR_K = 0.5;
const LEGACY_WEIGHT = 0.6;
const HALF_LIFE_DAYS = 21;
const CF_BONUS = 0.15;
const KRS_PENALTY = 0.10;
const G = { untested: 0.5, cf: 0.7, mixed: 0.55, krs: 0.4, none: 0.55 };
const SHARED_BONUS = 1.1;
const HOLD_M = 0.9;
const COOLDOWN_REDO_DAYS = 2;
const COOLDOWN_SCORED_DAYS = 7;
const IDLE_WEIGHT = 3;
const IDLE_CAP_DAYS = 7;

// Fixed by the exam: 104–114 is 11 years; a missing QUESTION_POINTS entry counts as 20.
const ANCHOR_EXAM_YEARS = 11;
const ANCHOR_DEFAULT_POINTS = 20;
const ANCHOR_DAY_MS = 24 * 60 * 60 * 1000;
const ANCHOR_CF_CODES = ['C', 'F', 'U', 'T'];
const ANCHOR_KRS_CODES = ['K', 'R', 'S'];
const ANCHOR_MARK_FACTOR = { o: 1, tri: 0.5, x: 0 };
const ANCHOR_TIERS = ['P1', 'P2', 'P3', 'P4'];
const ANCHOR_MARK_RANK = { x: 0, tri: 1, none: 2, o: 3 };

// ---- Small helpers -----------------------------------------------------------------

function anchorCompareText_(a, b) {
  return a < b ? -1 : (a > b ? 1 : 0);
}

function anchorToMs_(value) {
  const candidate = typeof value === 'function' ? value() : value;
  if (candidate instanceof Date) return candidate.getTime();
  if (typeof candidate === 'number' && Number.isFinite(candidate)) return candidate;
  if (typeof candidate === 'string' && candidate.trim() !== '') {
    const parsed = Date.parse(candidate);
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function anchorNow_(ctx) {
  const ms = ctx ? anchorToMs_(ctx.now) : null;
  return ms === null ? Date.now() : ms;
}

function anchorMembership_(source) {
  if (!source) return () => false;
  if (typeof source === 'function') return qid => !!source(qid);
  if (typeof source.has === 'function') return qid => !!source.has(qid);
  if (Array.isArray(source)) {
    const set = new Set(source.map(String));
    return qid => set.has(qid);
  }
  return () => false;
}

function anchorParseQid_(qid) {
  const m = /^EE-(\d+)-(\d+)-(\d+)$/.exec(String(qid || ''));
  return m ? { year: Number(m[1]), subject: m[2], number: Number(m[3]) } : null;
}

function anchorChapterIdOf_(entry) {
  if (typeof entry === 'string') return entry;
  return entry && typeof entry.id === 'string' ? entry.id : null;
}

function anchorSubjectIds(ctx) {
  const alloc = ctx && ctx.allocation && ctx.allocation.subjects;
  if (alloc && typeof alloc === 'object') {
    const ids = Object.keys(alloc).sort();
    if (ids.length) return ids;
  }
  const seen = {};
  anchorBank(ctx).forEach(q => { seen[q.subject] = true; });
  return Object.keys(seen).sort();
}

function anchorTargetOf_(ctx, subjectId) {
  const alloc = ctx && ctx.allocation && ctx.allocation.subjects;
  const entry = alloc && alloc[subjectId];
  return entry && Number.isFinite(Number(entry.target)) ? Number(entry.target) : 0;
}

// ---- Context --------------------------------------------------------------------------

function anchorBankFromGlobals_() {
  const rows = typeof DB_DATA !== 'undefined' && DB_DATA && Array.isArray(DB_DATA.questions) ? DB_DATA.questions : [];
  const taxonomy = typeof QUESTION_TAXONOMY_MAP !== 'undefined' && QUESTION_TAXONOMY_MAP ? QUESTION_TAXONOMY_MAP : {};
  const points = typeof QUESTION_POINTS !== 'undefined' && QUESTION_POINTS ? QUESTION_POINTS : {};
  const crops = typeof QUESTION_CROP_MAP !== 'undefined' && QUESTION_CROP_MAP ? QUESTION_CROP_MAP : {};
  const out = [];
  rows.forEach(row => {
    const id = Array.isArray(row) ? row[0] : (row && (row.id || row.qid));
    if (typeof id !== 'string' || id.indexOf('EE-') !== 0) return;
    const tax = taxonomy[id];
    const pts = points[id];
    out.push({
      id,
      subject: Array.isArray(row) ? String(row[1]) : String(row.subjectId || ''),
      year: Array.isArray(row) ? Number(row[2]) : Number(row.year),
      chapter: tax && typeof tax.primaryChapter === 'string' ? tax.primaryChapter : '',
      points: pts && Number.isFinite(Number(pts.total)) ? Number(pts.total) : ANCHOR_DEFAULT_POINTS,
      status: Array.isArray(row) ? row[9] : row.status,
      crop: !!crops[id]
    });
  });
  return out;
}

function anchorRecordsFromGlobals_() {
  try {
    if (typeof getResultRecords === 'function') return getResultRecords({}) || [];
  } catch (_) { /* no records */ }
  return [];
}

function anchorDueFromGlobals_(now) {
  try {
    if (typeof getDueQuestionsList === 'function') return getDueQuestionsList(now).map(String);
  } catch (_) { /* nothing due */ }
  return [];
}

function anchorDueDatesFromGlobals_() {
  const out = {};
  try {
    if (typeof sm2Schedule !== 'undefined' && sm2Schedule && typeof sm2Schedule === 'object') {
      Object.keys(sm2Schedule).forEach(qid => {
        const item = sm2Schedule[qid];
        if (item && typeof item.nextReviewDate === 'string') out[qid] = item.nextReviewDate;
      });
    }
  } catch (_) { /* no dates */ }
  return out;
}

function anchorEstimatesFromGlobals_(records, now) {
  const out = {};
  try {
    if (typeof scoreboardCompute === 'function') {
      const model = scoreboardCompute(records, now);
      (model.subjects || []).forEach(s => {
        out[String(s.id)] = Number.isFinite(Number(s.estimate)) && s.estimate !== null ? Number(s.estimate) : null;
      });
    }
  } catch (_) { /* no estimates */ }
  return out;
}

function anchorContext(overrides) {
  const o = overrides && typeof overrides === 'object' ? overrides : {};
  const ctx = {};
  const nowMs = anchorToMs_(o.now);
  ctx.now = nowMs === null ? Date.now() : nowMs;
  ctx.questions = Array.isArray(o.questions) ? o.questions : anchorBankFromGlobals_();
  ctx.allocation = o.allocation || (typeof TARGET_ALLOCATION !== 'undefined' ? TARGET_ALLOCATION : null);
  ctx.records = Array.isArray(o.records) ? o.records : anchorRecordsFromGlobals_();
  ctx.dueQids = Array.isArray(o.dueQids) ? o.dueQids.map(String) : anchorDueFromGlobals_(ctx.now);
  ctx.dueDates = o.dueDates && typeof o.dueDates === 'object' ? o.dueDates : anchorDueDatesFromGlobals_();
  ctx.locked = o.locked !== undefined ? o.locked
    : (typeof practiceLockedQids === 'function' ? practiceLockedQids({}) : []);
  ctx.reserved = o.reserved !== undefined ? o.reserved
    : (typeof practiceReservedQids === 'function' ? practiceReservedQids({}) : []);
  ctx.completionByQuestion = o.completionByQuestion && typeof o.completionByQuestion === 'object' ? o.completionByQuestion : {};
  ctx.estimates = o.estimates && typeof o.estimates === 'object' ? o.estimates
    : anchorEstimatesFromGlobals_(ctx.records, ctx.now);
  ctx.schedule = o.schedule || (typeof DAILY_SCHEDULE !== 'undefined' ? DAILY_SCHEDULE : null);
  return ctx;
}

/** Normalised question bank sorted by qid: [{ id, subject, year, chapter, points, status, crop }]. */
function anchorBank(ctx) {
  const rows = ctx && Array.isArray(ctx.questions) ? ctx.questions : [];
  const seen = {};
  const out = [];
  rows.forEach(row => {
    const id = row && (row.id || row.qid);
    if (typeof id !== 'string' || id.indexOf('EE-') !== 0 || seen[id]) return;
    seen[id] = true;
    const parsed = anchorParseQid_(id) || {};
    out.push({
      id,
      subject: String(row.subject !== undefined && row.subject !== null && row.subject !== '' ? row.subject : (row.subjectId || parsed.subject || '')),
      year: Number.isFinite(Number(row.year)) ? Number(row.year) : (parsed.year || 0),
      chapter: typeof row.chapter === 'string' ? row.chapter : '',
      points: Number.isFinite(Number(row.points)) ? Number(row.points) : ANCHOR_DEFAULT_POINTS,
      status: row.status === undefined ? 'verified' : row.status,
      crop: row.crop === undefined ? true : !!row.crop
    });
  });
  return out.sort((a, b) => anchorCompareText_(a.id, b.id));
}

// ---- Records -> r, worst, weight ---------------------------------------------------------

function anchorLatestRecords_(records) {
  const latest = {};
  (Array.isArray(records) ? records : []).forEach(rec => {
    if (!rec || typeof rec.qid !== 'string') return;
    const at = Number(rec.at);
    const stamp = Number.isFinite(at) ? at : 0;
    const cur = latest[rec.qid];
    if (!cur || stamp > cur.at || (stamp === cur.at && String(rec.id || '') > String(cur.rec.id || ''))) {
      latest[rec.qid] = { rec, at: stamp };
    }
  });
  return latest;
}

/** r (0–1) with the 主攻 coefficients, worst mark, error codes and decay weight of one record. */
function anchorRecordInfo_(rec, now) {
  const parts = Array.isArray(rec && rec.parts) ? rec.parts : [];
  let points = 0;
  let got = 0;
  let valid = 0;
  let factors = 0;
  let worst = 'o';
  parts.forEach(part => {
    const factor = part ? ANCHOR_MARK_FACTOR[part.mark] : undefined;
    if (factor === undefined) return;
    const pts = Number(part.points);
    valid += 1;
    factors += factor;
    if (Number.isFinite(pts) && pts > 0) { points += pts; got += pts * factor; }
    if (part.mark === 'x') worst = 'x';
    else if (part.mark === 'tri' && worst !== 'x') worst = 'tri';
  });
  if (!valid) return null;
  const r0 = points > 0 ? got / points : factors / valid;
  const errors = [];
  (Array.isArray(rec.errors) ? rec.errors : []).forEach(code => {
    if ((ANCHOR_CF_CODES.indexOf(code) >= 0 || ANCHOR_KRS_CODES.indexOf(code) >= 0) && errors.indexOf(code) < 0) errors.push(code);
  });
  let r = r0;
  if (r0 < 1 && errors.length) {
    if (errors.some(code => ANCHOR_KRS_CODES.indexOf(code) >= 0)) r -= KRS_PENALTY;
    else r += CF_BONUS;
  }
  r = Math.max(0, Math.min(1, r));
  const at = Number(rec.at);
  const ageDays = Math.max(0, (now - (Number.isFinite(at) ? at : now)) / ANCHOR_DAY_MS);
  const weight = (rec.legacy === true ? LEGACY_WEIGHT : 1) * Math.pow(0.5, ageDays / HALF_LIFE_DAYS);
  return { r, r0, worst, errors, weight, ageDays };
}

function anchorTierOf_(info, isDue) {
  if (!info) return 'P3';
  if (info.worst === 'o') return isDue ? 'P4' : null;
  const hasKRS = info.errors.some(code => ANCHOR_KRS_CODES.indexOf(code) >= 0);
  if (hasKRS) return 'P2';
  if (info.worst === 'tri') return 'P1';
  return info.errors.length ? 'P1' : 'P2';
}

function anchorEntryCompare_(a, b) {
  return (b.year - a.year) || (b.points - a.points) || anchorCompareText_(a.qid, b.qid);
}

function anchorChapterSets_(ctx) {
  const main = {};
  const shared = {};
  const subjects = ctx && ctx.allocation && ctx.allocation.subjects;
  if (subjects && typeof subjects === 'object') {
    Object.keys(subjects).forEach(id => {
      const entry = subjects[id] || {};
      (entry.mainChapters || []).forEach(c => { const cid = anchorChapterIdOf_(c); if (cid) main[cid] = id; });
      (entry.sharedChapters || []).forEach(c => { const cid = anchorChapterIdOf_(c); if (cid) shared[cid] = true; });
      (entry.mainChapters || []).forEach(c => { if (c && typeof c === 'object' && c.shared) shared[c.id] = true; });
    });
  }
  return { main, shared };
}

// ---- Analysis: pool entries + chapter statistics -----------------------------------------

function anchorAnalyze_(ctx) {
  const now = anchorNow_(ctx);
  const bank = anchorBank(ctx);
  const latest = anchorLatestRecords_(ctx.records);
  const isDue = anchorMembership_(ctx.dueQids);
  const isLocked = anchorMembership_(ctx.locked);
  const isReserved = anchorMembership_(ctx.reserved);
  const done = ctx.completionByQuestion || {};
  const sets = anchorChapterSets_(ctx);
  const chapters = {};
  const pool = [];

  bank.forEach(q => {
    if (!q.chapter) return;
    const c = chapters[q.chapter] || (chapters[q.chapter] = {
      subject: q.subject, years: {}, points: [], infos: [], lists: { P1: [], P2: [], P3: [], P4: [] }
    });
    c.years[q.year] = true;
    c.points.push(q.points);
    const last = latest[q.id];
    const info = last ? anchorRecordInfo_(last.rec, now) : null;
    if (info) c.infos.push(info);

    if (q.status !== 'verified' || !q.crop || isLocked(q.id) || isReserved(q.id)) return;
    let lastAt = last ? last.at : null;
    const completedAt = anchorCompletionMs_(done[q.id]);
    if (completedAt !== null && (lastAt === null || completedAt > lastAt)) lastAt = completedAt;
    if (lastAt !== null && now - lastAt < COOLDOWN_REDO_DAYS * ANCHOR_DAY_MS) return;
    const tier = anchorTierOf_(info, isDue(q.id));
    if (!tier) return;
    const entry = {
      qid: q.id, subject: q.subject, chapter: q.chapter, year: q.year, points: q.points,
      tier, worst: info ? info.worst : null, errors: info ? info.errors : [],
      lastAt, ageDays: lastAt === null ? null : (now - lastAt) / ANCHOR_DAY_MS
    };
    pool.push(entry);
    c.lists[tier].push(entry);
  });

  const stats = {};
  Object.keys(chapters).sort().forEach(chapterId => {
    const c = chapters[chapterId];
    let sumW = 0;
    let sumWR = 0;
    c.infos.forEach(info => { sumW += info.weight; sumWR += info.weight * info.r; });
    const m = (sumWR + PRIOR_K * PRIOR_M0) / (sumW + PRIOR_K);
    const untested = c.infos.length === 0;
    let g = null;
    if (untested) {
      g = G.untested;
    } else {
      const nonO = c.infos.filter(info => info.worst !== 'o');
      if (nonO.length) {
        let cf = 0;
        let krs = 0;
        nonO.forEach(info => info.errors.forEach(code => {
          if (ANCHOR_KRS_CODES.indexOf(code) >= 0) krs += 1; else cf += 1;
        }));
        if (cf + krs === 0) g = G.none;
        else if (krs === 0) g = G.cf;
        else if (krs >= cf) g = G.krs;
        else g = G.mixed;
      }
    }
    const readiness = g === null ? m : m + (1 - m) * g;
    const years = Object.keys(c.years).length;
    const freq = years / ANCHOR_EXAM_YEARS;
    const avgPts = c.points.reduce((s, p) => s + p, 0) / c.points.length;
    const shared = !!sets.shared[chapterId];
    const lists = {};
    const tiers = {};
    ANCHOR_TIERS.forEach(tier => {
      c.lists[tier].sort(anchorEntryCompare_);
      lists[tier] = c.lists[tier].map(e => e.qid);
      tiers[tier] = lists[tier].length;
    });
    stats[chapterId] = {
      subject: c.subject,
      main: sets.main[chapterId] !== undefined,
      shared,
      freq, avgPts, m, g, readiness,
      score: freq * avgPts * readiness * (shared ? SHARED_BONUS : 1),
      tiers,
      drillable: tiers.P1 + tiers.P2 + tiers.P3,
      untested,
      lists
    };
  });
  pool.sort(anchorEntryCompare_);
  return { now, bank, stats, pool };
}

function anchorCompletionMs_(value) {
  if (value && typeof value === 'object') return anchorToMs_(value.completedAt);
  return anchorToMs_(value);
}

/** Per-chapter statistics (see WORKPLAN 輸出); `lists` holds the pool qids of each tier in queue order. */
function anchorChapterStats(ctx) {
  return anchorAnalyze_(ctx).stats;
}

/** Eligible pool entries { qid, subject, chapter, year, points, tier, worst, errors, lastAt, ageDays }. */
function anchorPool(ctx) {
  return anchorAnalyze_(ctx).pool;
}

// ---- Anchors -------------------------------------------------------------------------------

function anchorRankedMain_(subjectId, stats) {
  const id = String(subjectId);
  return Object.keys(stats || {}).filter(ch => stats[ch].subject === id && stats[ch].main).sort((a, b) =>
    (stats[b].score - stats[a].score) || (stats[b].freq - stats[a].freq) || (stats[b].m - stats[a].m)
    || anchorCompareText_(a, b));
}

/** The (up to) 2 anchor chapters of a subject, best score first. */
function anchorChaptersFor(subjectId, stats) {
  return anchorRankedMain_(subjectId, stats)
    .filter(ch => stats[ch].drillable >= 1 || stats[ch].m >= HOLD_M)
    .slice(0, ANCHORS_PER_SUBJECT);
}

/** FOCUS order of the anchors: mastery m ascending (tie: score descending, then chapter id). */
function anchorFocusOrder(subjectId, stats) {
  return anchorChaptersFor(subjectId, stats).sort((a, b) =>
    (stats[a].m - stats[b].m) || (stats[b].score - stats[a].score) || anchorCompareText_(a, b));
}

/** The first main chapter that is not an anchor (the 3rd by score), used when both anchors are drained. */
function anchorSpillChapter(subjectId, stats) {
  const anchors = anchorChaptersFor(subjectId, stats);
  const rest = anchorRankedMain_(subjectId, stats).filter(ch => anchors.indexOf(ch) < 0);
  return rest.length ? rest[0] : null;
}

function anchorInterleave_(lists) {
  const out = [];
  const longest = lists.reduce((n, l) => Math.max(n, l.length), 0);
  for (let i = 0; i < longest; i += 1) lists.forEach(l => { if (i < l.length) out.push(l[i]); });
  return out;
}

/** Ordered qids of one subject: P1, P2, P3 of the anchors (interleaved A1/A2) then P4; spills to the 3rd chapter if P1–P3 are empty. */
function anchorSubjectQueue(subjectId, ctx, stats) {
  const st = stats || anchorChapterStats(ctx);
  const anchors = anchorChaptersFor(subjectId, st);
  const out = [];
  const tierList = (chapters, tier) => anchorInterleave_(chapters.map(ch => st[ch].lists[tier]));
  ['P1', 'P2', 'P3'].forEach(tier => out.push(...tierList(anchors, tier)));
  if (!out.length) {
    const spill = anchorSpillChapter(subjectId, st);
    if (spill) ['P1', 'P2', 'P3'].forEach(tier => out.push(...tierList([spill], tier)));
  }
  out.push(...tierList(anchors, 'P4'));
  return out;
}

// ---- Subject priority (出口 4) ----------------------------------------------------------------

/** [{ id, priority, shortfall, idleDays }] sorted by priority descending (tie: subject id). */
function anchorSubjectPriority(ctx) {
  const now = anchorNow_(ctx);
  const lastBySubject = {};
  (Array.isArray(ctx.records) ? ctx.records : []).forEach(rec => {
    if (!rec || rec.legacy === true) return;
    const parsed = anchorParseQid_(rec.qid);
    const at = Number(rec.at);
    if (!parsed || !Number.isFinite(at)) return;
    if (lastBySubject[parsed.subject] === undefined || at > lastBySubject[parsed.subject]) lastBySubject[parsed.subject] = at;
  });
  const estimates = ctx.estimates || {};
  return anchorSubjectIds(ctx).map(id => {
    const estimate = Number.isFinite(Number(estimates[id])) && estimates[id] !== null ? Number(estimates[id]) : 0;
    const shortfall = Math.max(0, anchorTargetOf_(ctx, id) - estimate);
    const idleDays = lastBySubject[id] === undefined ? IDLE_CAP_DAYS : Math.max(0, (now - lastBySubject[id]) / ANCHOR_DAY_MS);
    return { id, shortfall, idleDays, priority: shortfall + IDLE_WEIGHT * Math.min(idleDays, IDLE_CAP_DAYS) };
  }).sort((a, b) => (b.priority - a.priority) || anchorCompareText_(a.id, b.id));
}

// ---- Exits -------------------------------------------------------------------------------------

/** 出口 2: round-robin over `subjects` (priority order), each taking its next anchor-queue item. */
function anchorQueue(args) {
  const opts = args || {};
  const ctx = opts.ctx || anchorContext();
  const count = Number.isInteger(opts.count) && opts.count > 0 ? opts.count : (opts.count === Infinity ? Infinity : 3);
  const subjects = Array.isArray(opts.subjects) && opts.subjects.length
    ? opts.subjects.map(String) : anchorSubjectPriority(ctx).map(s => s.id);
  const stats = anchorChapterStats(ctx);
  const queues = subjects.map(id => anchorSubjectQueue(id, ctx, stats));
  const chosen = [];
  const taken = {};
  for (let round = 0; chosen.length < count; round += 1) {
    let any = false;
    for (let i = 0; i < queues.length && chosen.length < count; i += 1) {
      if (round >= queues[i].length) continue;
      any = true;
      const qid = queues[i][round];
      if (!taken[qid]) { taken[qid] = true; chosen.push(qid); }
    }
    if (!any) break;
  }
  return chosen;
}

function anchorTaskSubjectId_(task, ctx) {
  if (!task) return null;
  if (task.subjectId !== undefined && task.subjectId !== null && task.subjectId !== '') return String(task.subjectId);
  const subjects = ctx && ctx.allocation && ctx.allocation.subjects;
  if (subjects && typeof task.subject === 'string' && task.subject) {
    const hit = Object.keys(subjects).sort().find(id => {
      const name = subjects[id] && subjects[id].name;
      return typeof name === 'string' && name && (name === task.subject || name.indexOf(task.subject) >= 0 || task.subject.indexOf(name) >= 0);
    });
    if (hit) return hit;
  }
  const first = Array.isArray(task.qids) ? anchorParseQid_(task.qids[0]) : null;
  return first ? first.subject : null;
}

function anchorCompletedFocusRounds_(subjectId, task, state, ctx) {
  const tasks = ctx && ctx.schedule && ctx.schedule.tasks;
  const completed = state && state.completed && typeof state.completed === 'object' ? state.completed : {};
  if (!tasks) return 0;
  return Object.keys(completed).filter(code => {
    const t = tasks[code];
    return t && t.kind === 'focus' && completed[code] && (!task || code !== task.code)
      && anchorTaskSubjectId_(t, ctx) === subjectId;
  }).length;
}

function anchorFocusFor_(list, st, chapterId, minAgeDays) {
  const lists = st[chapterId].lists;
  const byQid = {};
  list.forEach(e => { byQid[e.qid] = e; });
  const p1 = lists.P1;
  const p2 = lists.P2;
  const p3 = lists.P3;
  let example = p2.length ? p2[0] : (p1.length ? p1[0] : null);
  let fresh = null;
  if (example !== null) {
    fresh = p3.length ? p3[0] : null;
    if (fresh === null) {
      const old = p1.concat(p2).filter(qid => qid !== example && byQid[qid] && byQid[qid].ageDays !== null && byQid[qid].ageDays >= minAgeDays);
      fresh = old.length ? old[0] : null;
    }
  } else if (p3.length >= 2) {
    example = p3[0];
    fresh = p3[1];
  }
  return example !== null && fresh !== null ? { chapter: chapterId, qids: [example, fresh], scoredQids: [fresh] } : null;
}

/**
 * 出口 1: dynamic FOCUS question pair at the moment a FOCUS task starts.
 * Returns { chapter, qids: [example, fresh], scoredQids: [fresh] } or null (caller falls back to the fixed table).
 */
function anchorFocusPick(args) {
  const opts = args || {};
  const task = opts.task || null;
  const ctx = opts.ctx || anchorContext();
  const subjectId = anchorTaskSubjectId_(task, ctx);
  if (!subjectId) return null;
  const analysis = anchorAnalyze_(ctx);
  const st = analysis.stats;
  const order = anchorFocusOrder(subjectId, st);
  const k = anchorCompletedFocusRounds_(subjectId, task, opts.state, ctx);
  const candidates = [];
  if (order.length) {
    candidates.push(order[k % order.length]);
    if (order.length > 1) candidates.push(order[(k + 1) % order.length]);
  }
  const spill = anchorSpillChapter(subjectId, st);
  if (spill) candidates.push(spill);
  for (let i = 0; i < candidates.length; i += 1) {
    const pick = anchorFocusFor_(analysis.pool, st, candidates[i], COOLDOWN_SCORED_DAYS);
    if (pick) return pick;
  }
  return null;
}

/** 出口 3: due-review order — anchor chapters first, worst mark x > tri > o, earlier due date (then earlier last answer), qid. */
function anchorSortDue(qids, ctx) {
  const context = ctx || anchorContext();
  const list = Array.isArray(qids) ? qids.slice() : [];
  const st = anchorChapterStats(context);
  const bank = anchorBank(context);
  const chapterOf = {};
  const subjectOf = {};
  bank.forEach(q => { chapterOf[q.id] = q.chapter; subjectOf[q.id] = q.subject; });
  const anchorOf = {};
  anchorSubjectIds(context).forEach(id => { anchorOf[id] = anchorChaptersFor(id, st); });
  const latest = anchorLatestRecords_(context.records);
  const now = anchorNow_(context);
  const dates = context.dueDates || {};
  const key = qid => {
    const subject = subjectOf[qid] || (anchorParseQid_(qid) || {}).subject;
    const inAnchor = !!(subject && chapterOf[qid] && (anchorOf[subject] || []).indexOf(chapterOf[qid]) >= 0);
    const info = latest[qid] ? anchorRecordInfo_(latest[qid].rec, now) : null;
    return {
      anchor: inAnchor ? 0 : 1,
      mark: info ? ANCHOR_MARK_RANK[info.worst] : ANCHOR_MARK_RANK.none,
      date: typeof dates[qid] === 'string' ? dates[qid] : '9999-99-99',
      at: latest[qid] ? latest[qid].at : Infinity
    };
  };
  const keyed = {};
  list.forEach(qid => { keyed[qid] = key(qid); });
  return list.sort((a, b) => (keyed[a].anchor - keyed[b].anchor) || (keyed[a].mark - keyed[b].mark)
    || anchorCompareText_(keyed[a].date, keyed[b].date)
    || (keyed[a].at === keyed[b].at ? 0 : (keyed[a].at < keyed[b].at ? -1 : 1)) || anchorCompareText_(a, b));
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ANCHORS_PER_SUBJECT, PRIOR_M0, PRIOR_K, LEGACY_WEIGHT, HALF_LIFE_DAYS, CF_BONUS, KRS_PENALTY, G,
    SHARED_BONUS, HOLD_M, COOLDOWN_REDO_DAYS, COOLDOWN_SCORED_DAYS, IDLE_WEIGHT, IDLE_CAP_DAYS,
    anchorContext, anchorBank, anchorSubjectIds, anchorChapterStats, anchorPool, anchorChaptersFor,
    anchorFocusOrder, anchorSpillChapter, anchorSubjectQueue, anchorSubjectPriority, anchorQueue,
    anchorFocusPick, anchorSortDue
  };
}
