// src/components/answerCorrectionNotice.js
// K1 答案更正提醒.  Pure functions (no DOM, testable in a node vm) plus small
// DOM helpers at the bottom.  Data: ANSWER_CORRECTIONS
// (src/data/answerCorrections.generated.js).
//
// "做過" (decision A) means an attempt/review record only; merely opening a
// solution never counts.  Sources: committed attempt envelopes, SM-2 schedule,
// daily-practice completions, progress status mastered(1)/review(2), and
// completed today-task codes mapped to their qids.

const ANSWER_CORRECTION_KEYS = {
  attempts: 'EE_EXAM_ATTEMPT_ENVELOPES_V1',
  sm2: 'EE_EXAM_SM2_SCHEDULE_V1',
  practice: 'EE_EXAM_DAILY_PRACTICE_V1',
  progress: ['EE_EXAM_PROGRESS_V1', 'GK_EXAM_PROGRESS_V1'],
  todayTask: 'EE_EXAM_TODAY_TASK_V1',
  seen: 'EE_EXAM_ANSWER_CORRECTION_SEEN_V1',
};

function answerCorrectionEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function answerCorrectionFor(qid) {
  if (typeof ANSWER_CORRECTIONS === 'undefined' || !ANSWER_CORRECTIONS || typeof qid !== 'string') return null;
  return Object.prototype.hasOwnProperty.call(ANSWER_CORRECTIONS, qid) ? ANSWER_CORRECTIONS[qid] : null;
}

function answerCorrectionBannerHtml(qid) {
  const c = answerCorrectionFor(qid);
  if (!c) return '';
  return `<details class="answer-correction-banner" data-answer-correction="${answerCorrectionEscape(qid)}">`
    + `<summary>${uiIcon('alert-triangle',{class:'warn-ico'})} 本題答案已更正　舊：${answerCorrectionEscape(c.old_answer)} → 新：${answerCorrectionEscape(c.new_answer)}</summary>`
    + `<div class="answer-correction-detail">`
    + `<div class="answer-correction-reason">原因：${answerCorrectionEscape(c.reason)}（${answerCorrectionEscape(c.decided_at)} 更正）</div>`
    + `</div></details>`;
}

function answerCorrectionBadgeHtml(qid) {
  const c = answerCorrectionFor(qid);
  if (!c) return '';
  return `<span class="qtag answer-correction-badge" title="本題答案已於 ${answerCorrectionEscape(c.decided_at)} 更正，做過的話請重看題解">${uiIcon('alert-triangle',{class:'warn-ico'})} 答案已更正</span>`;
}

// ---- Learner records -------------------------------------------------------

function answerCorrectionStorage(storage) {
  if (storage) return storage;
  try { return typeof localStorage !== 'undefined' ? localStorage : null; } catch (_) { return null; }
}

function answerCorrectionReadJson(storage, key) {
  try {
    const raw = storage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

function answerCorrectionIsObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

// A string "YYYY-MM-DD" is read as the START of that local day (so a
// date-only SM-2 review on the correction day is conservatively kept);
// everything else goes through Date.parse / number.
function answerCorrectionTimestamp(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value !== 'string' || value.trim() === '') return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value.trim());
  if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).getTime();
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function answerCorrectionDayEnd(dateText) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateText || ''));
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]) + 1).getTime() : null;
}

// Returns Map qid -> {times: number[], untimed: boolean} for corrected qids only.
function answerCorrectionCollectRecords(storage) {
  const records = new Map();
  const touch = (qid, time) => {
    if (typeof qid !== 'string' || !answerCorrectionFor(qid)) return;
    let r = records.get(qid);
    if (!r) { r = { times: [], untimed: false }; records.set(qid, r); }
    if (typeof time === 'number' && Number.isFinite(time)) r.times.push(time);
    else r.untimed = true;
  };
  const K = ANSWER_CORRECTION_KEYS;

  // 1. Attempt envelopes: only committed / acknowledged (active = just opened).
  try {
    const store = answerCorrectionReadJson(storage, K.attempts);
    if (answerCorrectionIsObject(store) && answerCorrectionIsObject(store.attempts)) {
      Object.values(store.attempts).forEach(env => {
        if (!answerCorrectionIsObject(env) || (env.status !== 'committed' && env.status !== 'acknowledged')) return;
        const t = [env.committedAt, env.acknowledgedAt, env.updatedAt, env.createdAt]
          .map(answerCorrectionTimestamp).find(x => x !== null);
        touch(env.qid, t === undefined ? null : t);
      });
    }
  } catch (_) { /* skip */ }

  // 2. SM-2 schedule: any entry; lastReviewed may be date, timestamp or null.
  try {
    const sm2 = answerCorrectionReadJson(storage, K.sm2);
    if (answerCorrectionIsObject(sm2)) {
      Object.keys(sm2).forEach(qid => {
        const item = sm2[qid];
        if (!answerCorrectionIsObject(item)) return;
        touch(qid, answerCorrectionTimestamp(item.lastReviewed));
      });
    }
  } catch (_) { /* skip */ }

  // 3. Daily practice: completionByQuestion[qid] = ms | {completedAt}.
  try {
    const practice = answerCorrectionReadJson(storage, K.practice);
    if (answerCorrectionIsObject(practice) && answerCorrectionIsObject(practice.completionByQuestion)) {
      Object.keys(practice.completionByQuestion).forEach(qid => {
        const v = practice.completionByQuestion[qid];
        touch(qid, answerCorrectionTimestamp(answerCorrectionIsObject(v) ? v.completedAt : v));
      });
    }
  } catch (_) { /* skip */ }

  // 4. Progress map: 1 = mastered, 2 = needs second pass; 0 = untouched.  No timestamp.
  K.progress.forEach(key => {
    try {
      const progress = answerCorrectionReadJson(storage, key);
      if (!answerCorrectionIsObject(progress)) return;
      Object.keys(progress).forEach(qid => {
        const s = Number(progress[qid]);
        if (s === 1 || s === 2) touch(qid, null);
      });
    } catch (_) { /* skip */ }
  });

  // 5. Today-task: completed code -> ISO stamp; qids from DAILY_SCHEDULE.
  try {
    const task = answerCorrectionReadJson(storage, K.todayTask);
    const tasks = (typeof DAILY_SCHEDULE !== 'undefined' && DAILY_SCHEDULE && DAILY_SCHEDULE.tasks) || {};
    if (answerCorrectionIsObject(task) && answerCorrectionIsObject(task.completed)) {
      Object.keys(task.completed).forEach(code => {
        const def = tasks[code];
        if (!def || !Array.isArray(def.qids)) return;
        const t = answerCorrectionTimestamp(task.completed[code]);
        def.qids.forEach(qid => touch(qid, t));
      });
    }
  } catch (_) { /* skip */ }

  return records;
}

// Seen = the solution was shown with the correction banner (the learner has read the new answer).
// qid -> ms of the latest viewing.
function answerCorrectionSeenMap(storage) {
  const map = answerCorrectionReadJson(storage, ANSWER_CORRECTION_KEYS.seen);
  return answerCorrectionIsObject(map) ? map : {};
}

function answerCorrectionMarkSeen(qid, now, storage) {
  const s = answerCorrectionStorage(storage);
  if (!s || typeof s.setItem !== 'function' || !answerCorrectionFor(qid)) return false;
  try {
    const map = answerCorrectionSeenMap(s);
    map[qid] = typeof now === 'number' ? now : Date.now();
    s.setItem(ANSWER_CORRECTION_KEYS.seen, JSON.stringify(map));
    return true;
  } catch (_) {
    return false;
  }
}

function answerCorrectionsAttempted(storage) {
  const s = answerCorrectionStorage(storage);
  if (!s || typeof s.getItem !== 'function' || typeof ANSWER_CORRECTIONS === 'undefined') return [];
  let records;
  try { records = answerCorrectionCollectRecords(s); } catch (_) { return []; }
  const seen = answerCorrectionSeenMap(s);
  const out = [];
  records.forEach((r, qid) => {
    const c = answerCorrectionFor(qid);
    const boundary = answerCorrectionDayEnd(c.decided_at);
    const latest = r.times.length ? Math.max.apply(null, r.times) : null;
    if (latest !== null && boundary !== null && latest >= boundary) return; // saw the new answer already
    const seenAt = answerCorrectionTimestamp(seen[qid]);
    if (seenAt !== null && boundary !== null && seenAt >= boundary) return; // re-read the solution after the correction
    out.push({
      qid,
      decided_at: c.decided_at,
      lastAttemptAt: latest === null ? null : new Date(latest).toISOString(),
    });
  });
  out.sort((a, b) => String(b.decided_at).localeCompare(String(a.decided_at)) || a.qid.localeCompare(b.qid));
  return out;
}

// ---- DOM helpers -----------------------------------------------------------

function insertAnswerCorrectionBanner(container, qid) {
  try {
    if (!container || typeof container.insertAdjacentHTML !== 'function') return;
    const old = container.querySelector && container.querySelector('.answer-correction-banner');
    if (old) old.remove();
    const html = answerCorrectionBannerHtml(qid);
    if (!html) return;
    container.insertAdjacentHTML('afterbegin', html);
    // Showing the banner means the new answer is on screen: drop the qid from 「答案已更正、而你做過的題」.
    if (answerCorrectionMarkSeen(qid)) renderAnswerCorrectionReviewSection();
  } catch (_) { /* decorative */ }
}

function renderAnswerCorrectionReviewSection() {
  const host = typeof document !== 'undefined' ? document.getElementById('review-corrections') : null;
  if (!host) return;
  let items = [];
  try { items = answerCorrectionsAttempted(); } catch (_) { items = []; }
  if (!items.length) { host.innerHTML = ''; return; }
  const rows = items.map(item => {
    const q = typeof findQuestionRecord === 'function' ? findQuestionRecord(item.qid) : null;
    let label = '';
    if (q) {
      try {
        const rec = typeof getReviewRecord === 'function' ? getReviewRecord(q) : null;
        const meta = rec && typeof getSubjectMeta === 'function' ? getSubjectMeta(rec.subjectId) : null;
        if (rec) label = `${meta ? String(meta.name).split('（')[0] : ''} · ${rec.year} 年第 ${rec.number} 題`;
      } catch (_) { label = ''; }
    }
    const button = q
      ? `<button type="button" class="btn-sol answer-correction-review-btn" data-answer-correction-review="${answerCorrectionEscape(item.qid)}">重看</button>`
      : '';
    return `<li class="answer-correction-row"><span class="qid">${answerCorrectionEscape(item.qid)}</span>`
      + `<span class="answer-correction-row-label">${answerCorrectionEscape(label)}</span>`
      + `<span class="answer-correction-row-date">${answerCorrectionEscape(item.decided_at)} 更正</span>${button}</li>`;
  }).join('');
  host.innerHTML = `<section class="answer-correction-section"><h3>${uiIcon('alert-triangle',{class:'warn-ico'})} 答案已更正、而你做過的題（${items.length}）</h3>`
    + `<ul class="answer-correction-list">${rows}</ul></section>`;
  host.querySelectorAll('[data-answer-correction-review]').forEach(btn => {
    btn.addEventListener('click', () => {
      const qid = btn.getAttribute('data-answer-correction-review');
      const r = typeof findQuestionRecord === 'function' ? findQuestionRecord(qid) : null;
      if (r && typeof openSolutionModal === 'function') openSolutionModal(null, r[6], qid, r[3], { mode: 'browse' });
    });
  });
}
