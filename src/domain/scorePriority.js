// src/domain/scorePriority.js
/**
 * 依上榜效益選題: rank practice candidates by expected exam points gained per minute.
 *
 * The exam asks NEW questions, so the target is each chapter's new-question rate m (first attempts on
 * questions not seen before, shrunk toward the subject mean).  A chapter is worth share × (1 − m) points
 * per unit of practice, where share is its share of the subject's 104–114 papers.  Solving a new question
 * or redoing a missed one counts fully; a due review counts half (it mostly firms up the same question).
 * Each pick lowers the chapter's remaining gap, so one round spreads over chapters.
 * Rules: at most one question per chapter and two per subject in a round; a subject untouched for
 * 3 days gets the last slot; from 7 days before the exam no new questions.
 * Pure functions, no storage access.
 */

const PRIORITY_EXAM_DATE = '2026-11-14';
const PRIORITY_PRIOR_RATE = 0.45;          // new-question rate before any record
const PRIORITY_PRIOR_STRENGTH = 3;         // first attempts that weigh as much as the subject mean
const PRIORITY_LEARN_RATE = 0.03;          // rate gained per solved question at m = 0.45 (fitted on result cards)
const PRIORITY_REDO_BELOW = 0.5;           // latest score ratio below this -> redo
const PRIORITY_EFFECT = { redo: 1, new: 1, review: 0.5 };
const PRIORITY_KIND_ORDER = { redo: 0, new: 1, review: 2 };
const PRIORITY_MAINTAIN_MS = 3 * 24 * 60 * 60 * 1000;
const PRIORITY_NO_NEW_DAYS = 7;

function priorityRatio_(record) {
  const total = Number(record && record.total);
  const estimate = Number(record && record.estimate);
  return total > 0 && Number.isFinite(estimate) ? Math.max(0, Math.min(1, estimate / total)) : null;
}

function priorityDaysToExam_(now, examDate) {
  const exam = new Date(`${examDate || PRIORITY_EXAM_DATE}T00:00:00`);
  const d = new Date(now);
  const today = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  return Math.round((exam - today) / 86400000);
}

// Chapter share of each subject's papers and the chapter new-question rates.
// questions: [{ id, subjectId, chapter }] (the whole PE bank); records: result cards.
function priorityModel(questions, records) {
  const subjectCount = {};
  const chapterCount = {};
  const subjectOf = {};
  const chapterOf = {};
  (questions || []).forEach(q => {
    if (!q || !q.id || !q.subjectId || !q.chapter || q.chapter === 'unknown') return;
    subjectOf[q.id] = q.subjectId;
    chapterOf[q.id] = q.chapter;
    subjectCount[q.subjectId] = (subjectCount[q.subjectId] || 0) + 1;
    const key = `${q.subjectId}|${q.chapter}`;
    chapterCount[key] = (chapterCount[key] || 0) + 1;
  });
  const first = {};
  const latest = {};
  (records || []).forEach(r => {
    if (!r || !(r.qid in chapterOf) || priorityRatio_(r) === null) return;
    const at = Number(r.at) || 0;
    if (!first[r.qid] || at < (Number(first[r.qid].at) || 0)) first[r.qid] = r;
    if (!latest[r.qid] || at >= (Number(latest[r.qid].at) || 0)) latest[r.qid] = r;
  });
  const subjectFirst = {};
  const chapterFirst = {};
  Object.keys(first).forEach(qid => {
    const x = priorityRatio_(first[qid]);
    const s = subjectOf[qid];
    const key = `${s}|${chapterOf[qid]}`;
    (subjectFirst[s] = subjectFirst[s] || []).push(x);
    (chapterFirst[key] = chapterFirst[key] || []).push(x);
  });
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  const share = {};
  const rate = {};
  Object.keys(chapterCount).forEach(key => {
    const s = key.split('|')[0];
    share[key] = chapterCount[key] / subjectCount[s];
    const prior = subjectFirst[s] ? mean(subjectFirst[s]) : PRIORITY_PRIOR_RATE;
    const xs = chapterFirst[key] || [];
    rate[key] = (PRIORITY_PRIOR_STRENGTH * prior + xs.reduce((a, b) => a + b, 0)) / (PRIORITY_PRIOR_STRENGTH + xs.length);
  });
  return { share, rate, latest, subjectOf, chapterOf };
}

// Expected points of each subject (100 per paper) from the chapter rates.
function priorityExpectedScores(model) {
  const out = {};
  Object.keys(model.share).forEach(key => {
    const s = key.split('|')[0];
    out[s] = (out[s] || 0) + 100 * model.share[key] * model.rate[key];
  });
  return out;
}

// candidates: [{ id, subjectId, chapter, tier }] that may be drawn now (locks and repeat window applied).
// options: { questions, records, dueIds, now, examDate, count }.
// Returns [{ id, kind, subjectId, chapter, rate, value }] best first.
function priorityRankCandidates(candidates, options = {}) {
  const count = Number.isInteger(options.count) && options.count > 0 ? options.count : 3;
  const now = Number.isFinite(options.now) ? options.now : Date.now();
  const model = priorityModel(options.questions || candidates, options.records || []);
  const due = new Set((options.dueIds || []).map(String));
  const allowNew = priorityDaysToExam_(now, options.examDate) > PRIORITY_NO_NEW_DAYS;
  const items = [];
  (candidates || []).forEach(c => {
    const key = `${c.subjectId}|${c.chapter}`;
    if (!c || !(key in model.share)) return;
    const last = model.latest[c.id];
    let kind = null;
    if (!last) kind = allowNew ? 'new' : null;
    else if (priorityRatio_(last) < PRIORITY_REDO_BELOW) kind = 'redo';
    else if (due.has(c.id)) kind = 'review';
    if (kind) items.push({ id: c.id, kind, subjectId: c.subjectId, chapter: c.chapter, key, main: c.tier === 'main' });
  });
  const rate = Object.assign({}, model.rate);
  const valueOf = item => model.share[item.key] * PRIORITY_EFFECT[item.kind] * (1 - rate[item.key]);
  const better = (a, b) => valueOf(b) - valueOf(a) || PRIORITY_KIND_ORDER[a.kind] - PRIORITY_KIND_ORDER[b.kind]
    || (b.main - a.main) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  const chosen = [];
  const take = item => {
    chosen.push({ id: item.id, kind: item.kind, subjectId: item.subjectId, chapter: item.chapter,
      rate: rate[item.key], value: valueOf(item) });
    rate[item.key] = Math.min(0.95, rate[item.key]
      + PRIORITY_EFFECT[item.kind] * PRIORITY_LEARN_RATE * (1 - rate[item.key]) / (1 - PRIORITY_PRIOR_RATE));
  };
  const usable = item => !chosen.some(x => x.id === item.id || x.chapter === item.chapter)
    && chosen.filter(x => x.subjectId === item.subjectId).length < 2;

  // A subject with candidates but no result card for 3 days keeps its hand in: it gets the last slot.
  const lastAt = {};
  (options.records || []).forEach(r => {
    const s = r && model.subjectOf[r.qid];
    if (s) lastAt[s] = Math.max(lastAt[s] || 0, Number(r.at) || 0);
  });
  const stale = [...new Set(items.map(i => i.subjectId))]
    .filter(s => now - (lastAt[s] || 0) >= PRIORITY_MAINTAIN_MS)
    .sort((a, b) => (lastAt[a] || 0) - (lastAt[b] || 0))[0];

  while (chosen.length < count) {
    const reserveLast = stale && chosen.length === count - 1 && !chosen.some(x => x.subjectId === stale);
    let pool = items.filter(i => usable(i) && (!reserveLast || i.subjectId === stale));
    if (!pool.length && reserveLast) pool = items.filter(usable);
    if (!pool.length) break;
    take(pool.sort(better)[0]);
  }
  return chosen;
}
