// src/components/homeStatus.js
/**
 * v1.4.0 首頁像素風「狀態視窗」: an original pixel-art night-substation scene (drawn here from character
 * grids, no external art or fonts) plus a game-style status window that shows real study numbers.
 *
 * Everything the window shows is derived from stores that already exist; this file adds NO localStorage
 * key and the backup format is untouched:
 *   - 今日任務 state (todayTask.js)                    -> completed schedule tasks
 *   - 作答結果卡 records (resultCardStore.js)                -> result-card count, EXP, active days
 *   - SM-2 schedule (sm2Store.js, lastReviewed)              -> extra active days
 *   - scoreboardCompute (scoreboard.js)                      -> estimated total / target / six subjects
 *   - DAILY_SCHEDULE.order                                   -> total task count
 *
 * ---- Stat formulas (homeStatusModel is pure; the DOM glue is at the bottom) ----
 * EXP
 *   task EXP        = 100 per completed schedule task (HOME_STATUS_TASK_EXP)
 *   result-card EXP = 10 per record, plus up to 10 more by score: round(10 * estimate / total)
 *                     (a legacy self-rating record, migrated from the old practice rating, gives a flat 5)
 *   totalExp        = sum of the above
 * Level
 *   EXP needed to go from Lv n to Lv n+1 = 150 + 30 * (n - 1)       (Lv1 -> 2: 150, Lv2 -> 3: 180, ...)
 *   cumulative EXP to reach Lv L          = 150 (L-1) + 15 (L-1)(L-2)
 *   level = the largest L whose cumulative EXP <= totalExp (min 1); the bar shows (totalExp - cumulative(L)) / need(L).
 * Title (稱號) by level: 1-4 見習巡線員, 5-8 配電學徒, 9-12 變電值班員, 13-16 保護電驛師, 17-20 系統調度員,
 *   21-24 電網守護者, 25+ 榜上技師.
 * Streak (連續學習)
 *   an "active day" is a local calendar date on which a schedule task was completed, a result card was saved
 *   or an SM-2 review happened.  Streak = number of consecutive active days ending today; if today has no
 *   activity yet the run may still end yesterday (the streak is only broken after a whole empty day).
 * Days to exam (距考試) = local calendar days from today to 2026-11-14 (never negative).
 * Tasks = completed schedule tasks / DAILY_SCHEDULE.order.length.
 * Result cards = number of stored result-card records (same count the backup summary shows).
 * Score = scoreboardCompute(...).estimateTotal / (estimateTargetTotal, else the 380 goal), with N / 6 subjects.
 * Attributes = the six scoreboard subjects: estimate (mock score when a full mock exists, else practice
 *   projection), the subject target, and a state: goal (>= target), pass (>= 60), low (< 60), none (no data).
 */

const HOME_STATUS_EXAM_DATE = '2026-11-14';
const HOME_STATUS_TASK_EXP = 100;
const HOME_STATUS_CARD_EXP = 10;
const HOME_STATUS_CARD_BONUS_EXP = 10;
const HOME_STATUS_LEGACY_CARD_EXP = 5;
const HOME_STATUS_LEVEL_BASE = 150;
const HOME_STATUS_LEVEL_STEP = 30;
const HOME_STATUS_PASS_SUBJECT = 60;
const HOME_STATUS_TITLES = [
  { min: 1, name: '見習巡線員' },
  { min: 5, name: '配電學徒' },
  { min: 9, name: '變電值班員' },
  { min: 13, name: '保護電驛師' },
  { min: 17, name: '系統調度員' },
  { min: 21, name: '電網守護者' },
  { min: 25, name: '榜上技師' }
];
const HOME_STATUS_SUBJECT_SHORT = { '01': '電路', '02': '電子', '03': '工數', '04': '電機', '05': '電力', '06': '配電' };

function homeStatusEscape_(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function homeStatusNum_(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

/** Local calendar date 'YYYY-MM-DD' of a timestamp (ms) or Date. */
function homeStatusDateKey(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (!Number.isFinite(d.getTime())) return '';
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}

function homeStatusParseDay_(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null;
}

/** EXP needed to go from level n to n + 1. */
function homeStatusExpNeed(level) {
  return HOME_STATUS_LEVEL_BASE + HOME_STATUS_LEVEL_STEP * (Math.max(1, level) - 1);
}

/** Cumulative EXP needed to reach `level` (Lv1 = 0). */
function homeStatusExpToReach(level) {
  const n = Math.max(1, level) - 1;
  return HOME_STATUS_LEVEL_BASE * n + HOME_STATUS_LEVEL_STEP * n * (n - 1) / 2;
}

/** { level, into, need, pct } for a total EXP. */
function homeStatusLevelFor(totalExp) {
  const exp = Math.max(0, Math.floor(homeStatusNum_(totalExp, 0)));
  let level = 1;
  while (homeStatusExpToReach(level + 1) <= exp) level += 1;
  const into = exp - homeStatusExpToReach(level);
  const need = homeStatusExpNeed(level);
  return { level, into, need, pct: Math.max(0, Math.min(100, Math.floor(into * 100 / need))) };
}

function homeStatusTitleFor(level) {
  let name = HOME_STATUS_TITLES[0].name;
  HOME_STATUS_TITLES.forEach(t => { if (level >= t.min) name = t.name; });
  return name;
}

/** EXP of one stored result-card record. */
function homeStatusCardExp(record) {
  if (!record || typeof record !== 'object') return 0;
  if (record.legacy) return HOME_STATUS_LEGACY_CARD_EXP;
  const total = homeStatusNum_(record.total, 0);
  const estimate = homeStatusNum_(record.estimate, 0);
  const ratio = total > 0 ? Math.max(0, Math.min(1, estimate / total)) : 0;
  return HOME_STATUS_CARD_EXP + Math.round(HOME_STATUS_CARD_BONUS_EXP * ratio);
}

/** Consecutive active days ending today (or yesterday while today is still empty). `days` = Set/array of 'YYYY-MM-DD'. */
function homeStatusStreak(days, now) {
  const set = new Set(Array.isArray(days) ? days : Array.from(days || []));
  const today = new Date(homeStatusNum_(now, Date.now()));
  let cursor = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const activeToday = set.has(homeStatusDateKey(cursor));
  if (!activeToday) cursor = new Date(cursor.getFullYear(), cursor.getMonth(), cursor.getDate() - 1);
  let count = 0;
  while (set.has(homeStatusDateKey(cursor))) {
    count += 1;
    cursor = new Date(cursor.getFullYear(), cursor.getMonth(), cursor.getDate() - 1);
  }
  return { days: count, activeToday };
}

/** Local calendar days from today to `examDate` (0 on the day itself or after). */
function homeStatusDaysUntil(examDate, now) {
  const exam = homeStatusParseDay_(examDate);
  if (!exam) return { days: 0, passed: false, today: false };
  const t = new Date(homeStatusNum_(now, Date.now()));
  const today = new Date(t.getFullYear(), t.getMonth(), t.getDate());
  const diff = Math.round((exam.getTime() - today.getTime()) / 86400000);
  return { days: Math.max(0, diff), passed: diff < 0, today: diff === 0 };
}

function homeStatusAttrState_(estimate, target) {
  if (estimate === null || estimate === undefined || !Number.isFinite(Number(estimate))) return 'none';
  const v = Number(estimate);
  if (target !== null && target !== undefined && Number.isFinite(Number(target)) && v >= Number(target)) return 'goal';
  return v >= HOME_STATUS_PASS_SUBJECT ? 'pass' : 'low';
}

/**
 * Pure stat model.  inputs = {
 *   now,                    // ms
 *   completed,              // { 'CORE-01': ISO string } (todayTaskState.completed)
 *   totalTasks,             // DAILY_SCHEDULE.order.length
 *   records,                // result-card records
 *   reviewDates,            // ['YYYY-MM-DD'] SM-2 lastReviewed values
 *   scoreboard,             // scoreboardCompute(records, now) result (may be omitted)
 *   examDate                // 'YYYY-MM-DD' (default HOME_STATUS_EXAM_DATE)
 * }
 */
function homeStatusModel(inputs) {
  const input = inputs || {};
  const now = homeStatusNum_(input.now, Date.now());
  const completed = input.completed && typeof input.completed === 'object' ? input.completed : {};
  const doneCodes = Object.keys(completed);
  const records = Array.isArray(input.records) ? input.records : [];
  const taskExp = doneCodes.length * HOME_STATUS_TASK_EXP;
  const cardExp = records.reduce((n, r) => n + homeStatusCardExp(r), 0);
  const totalExp = taskExp + cardExp;
  const lv = homeStatusLevelFor(totalExp);

  const active = new Set();
  doneCodes.forEach(code => { const k = homeStatusDateKey(Date.parse(completed[code])); if (k) active.add(k); });
  records.forEach(r => { const k = r && Number.isFinite(Number(r.at)) ? homeStatusDateKey(Number(r.at)) : ''; if (k) active.add(k); });
  (Array.isArray(input.reviewDates) ? input.reviewDates : []).forEach(d => { if (/^\d{4}-\d{2}-\d{2}$/.test(String(d))) active.add(String(d)); });
  const todayKey = homeStatusDateKey(now);
  active.forEach(k => { if (k > todayKey) active.delete(k); });

  const sb = input.scoreboard || null;
  const subjects = sb && Array.isArray(sb.subjects) ? sb.subjects : [];
  const hasScore = !!(sb && sb.hasData && sb.estimateTotal !== null && sb.estimateTotal !== undefined);
  const goal = sb && Number.isFinite(Number(sb.goal)) ? Number(sb.goal) : 380;
  const scoreTarget = sb && sb.estimateTargetTotal !== null && sb.estimateTargetTotal !== undefined ? Number(sb.estimateTargetTotal) : goal;
  const pct = v => Math.max(0, Math.min(100, Math.round(Number(v))));
  const attrs = subjects.map(s => {
    const has = s.estimate !== null && s.estimate !== undefined && Number.isFinite(Number(s.estimate));
    const target = s.target !== null && s.target !== undefined && Number.isFinite(Number(s.target)) ? Number(s.target) : null;
    return {
      id: s.id,
      name: HOME_STATUS_SUBJECT_SHORT[s.id] || String(s.name || s.id),
      estimate: has ? Math.round(Number(s.estimate)) : null,
      target: target === null ? null : Math.round(target),
      pct: has ? pct(s.estimate) : 0,
      targetPct: target === null ? 0 : pct(target),
      state: homeStatusAttrState_(has ? Number(s.estimate) : null, target)
    };
  });

  return {
    level: lv.level,
    title: homeStatusTitleFor(lv.level),
    exp: { total: totalExp, into: lv.into, need: lv.need, pct: lv.pct, fromTasks: taskExp, fromCards: cardExp },
    streak: homeStatusStreak(active, now),
    exam: Object.assign({ date: input.examDate || HOME_STATUS_EXAM_DATE }, homeStatusDaysUntil(input.examDate || HOME_STATUS_EXAM_DATE, now)),
    tasks: { done: doneCodes.length, total: Math.max(doneCodes.length, Math.floor(homeStatusNum_(input.totalTasks, doneCodes.length))) },
    cards: { count: records.length },
    score: {
      hasData: hasScore,
      total: hasScore ? Math.round(Number(sb.estimateTotal)) : null,
      target: Math.round(scoreTarget),
      count: sb ? homeStatusNum_(sb.estimateCount, 0) : 0,
      subjectCount: sb ? homeStatusNum_(sb.subjectCount, 6) : 6,
      passLine: sb && Number.isFinite(Number(sb.passLine)) ? Number(sb.passLine) : 360
    },
    attrs
  };
}

// ---- Pixel digits (3x5 bitmap font, original) ---------------------------------

const HOME_STATUS_GLYPHS = {
  '0': ['111', '101', '101', '101', '111'],
  '1': ['010', '110', '010', '010', '111'],
  '2': ['111', '001', '111', '100', '111'],
  '3': ['111', '001', '111', '001', '111'],
  '4': ['101', '101', '111', '001', '001'],
  '5': ['111', '100', '111', '001', '111'],
  '6': ['111', '100', '111', '101', '111'],
  '7': ['111', '001', '010', '010', '010'],
  '8': ['111', '101', '111', '101', '111'],
  '9': ['111', '101', '111', '001', '111'],
  '/': ['001', '001', '010', '100', '100'],
  '-': ['000', '000', '111', '000', '000'],
  '+': ['000', '010', '111', '010', '000']
};

function homeStatusGlyphPath_(text) {
  let d = '';
  let x = 0;
  Array.from(text).forEach(ch => {
    const glyph = HOME_STATUS_GLYPHS[ch === '／' ? '/' : (ch === '—' ? '-' : ch)];
    if (glyph) {
      glyph.forEach((row, y) => {
        let run = 0;
        for (let i = 0; i <= 3; i++) {
          if (i < 3 && row[i] === '1') run += 1;
          else if (run) { d += 'M' + (x + i - run) + ' ' + y + 'h' + run + 'v1h-' + run + 'z'; run = 0; }
        }
      });
    }
    x += 4;
  });
  return { d, width: Math.max(3, x - 1) };
}

/** Number / short text drawn with the pixel font.  `unit` = CSS px per font pixel. */
function homeStatusPixelText(text, unit) {
  const value = String(text);
  const g = homeStatusGlyphPath_(value);
  const u = unit || 3;
  return '<span class="hs-num" role="img" aria-label="' + homeStatusEscape_(value) + '" style="--u:' + u + 'px">'
    + '<svg viewBox="0 0 ' + g.width + ' 5" width="' + g.width * u + '" height="' + 5 * u + '" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'
    + '<path class="hs-num-sh" transform="translate(.45 .45)" d="' + g.d + '"/><path class="hs-num-fg" d="' + g.d + '"/></svg></span>';
}

// ---- Status window HTML -------------------------------------------------------

function homeStatusAttrHtml_(a, index) {
  const value = a.estimate === null ? homeStatusPixelText('-', 2) : homeStatusPixelText(String(a.estimate), 2);
  const target = a.target === null ? '' : '<small>／' + homeStatusEscape_(a.target) + '</small>';
  const label = a.name + (a.estimate === null ? '：尚無資料' : '：' + a.estimate + (a.target === null ? '' : '／' + a.target));
  return '<li class="hs-row hs-attr hs-attr--' + a.state + '" style="--i:' + index + ';--v:' + a.pct + '%;--t:' + a.targetPct + '%" data-hs-attr="' + homeStatusEscape_(a.id) + '" title="' + homeStatusEscape_(label) + '">'
    + '<span class="hs-attr-k">' + homeStatusEscape_(a.name) + '</span>'
    + '<span class="hs-bar hs-bar--attr" aria-hidden="true"><i></i><u></u></span>'
    + '<span class="hs-attr-v">' + value + target + '</span></li>';
}

function homeStatusTileHtml_(key, label, valueHtml, unit, index, extraClass) {
  return '<li class="hs-row hs-tile' + (extraClass ? ' ' + extraClass : '') + '" style="--i:' + index + '" data-hs="' + key + '">'
    + '<span class="hs-k">' + label + '</span>'
    + '<span class="hs-v">' + valueHtml + (unit ? '<small>' + unit + '</small>' : '') + '</span></li>';
}

/** The window's inner HTML for a model (pure string; collapsed state is a class on the host, not part of this). */
function homeStatusHtml(m) {
  const sc = m.score;
  const scoreValue = sc.hasData ? homeStatusPixelText(sc.total + '／' + sc.target, 3) : homeStatusPixelText('-', 3);
  const scoreUnit = sc.hasData ? sc.count + '／' + sc.subjectCount + ' 科' : '';
  const examValue = homeStatusPixelText(String(m.exam.days), 3);
  const head = '<div class="hs-head hs-row" style="--i:0">'
    + '<div class="hs-lv" data-hs="level"><span class="hs-lv-tag">Lv</span>' + homeStatusPixelText(String(m.level), 5) + '</div>'
    + '<div class="hs-id">'
    + '<div class="hs-title" data-hs="title">' + homeStatusEscape_(m.title) + '<b class="hs-caret" aria-hidden="true"></b></div>'
    + '<div class="hs-exp" data-hs="exp" role="img" aria-label="EXP ' + m.exp.into + '／' + m.exp.need + '">'
    + '<span class="hs-bar hs-bar--exp" style="--v:' + m.exp.pct + '%" aria-hidden="true"><i></i></span>'
    + '<span class="hs-exp-num">EXP ' + m.exp.into + '／' + m.exp.need + '</span></div>'
    + '</div>'
    + '<button type="button" class="hs-toggle" id="hs-toggle" aria-expanded="true" aria-controls="hs-body" onclick="homeStatusToggle()">收合</button>'
    + '</div>';
  const tiles = '<ul class="hs-tiles">'
    + homeStatusTileHtml_('streak', '連續學習', homeStatusPixelText(String(m.streak.days), 3), '天', 1)
    + homeStatusTileHtml_('exam', '距考試', examValue, '天', 2)
    + homeStatusTileHtml_('tasks', '任務', homeStatusPixelText(m.tasks.done + '／' + m.tasks.total, 3), '', 3)
    + homeStatusTileHtml_('cards', '結果卡', homeStatusPixelText(String(m.cards.count), 3), '', 4)
    + homeStatusTileHtml_('score', '預估總分', scoreValue, scoreUnit, 5, 'hs-tile--wide')
    + '</ul>';
  const attrs = '<ul class="hs-attrs">' + m.attrs.map((a, i) => homeStatusAttrHtml_(a, 6 + i)).join('') + '</ul>';
  return '<div class="hs-frame"><div class="hs-inner">' + head
    + '<div class="hs-body" id="hs-body">' + tiles + attrs + '</div></div></div>';
}

// ---- Pixel scene (original art, drawn from grids) -----------------------------

const HOME_STATUS_SCENE_W = 480;
const HOME_STATUS_SCENE_H = 144;
const HOME_STATUS_GROUND_Y = 128;

function homeStatusRng_(seed) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function homeStatusGrid_() {
  const rows = [];
  for (let y = 0; y < HOME_STATUS_SCENE_H; y++) rows.push(new Array(HOME_STATUS_SCENE_W).fill(''));
  return rows;
}

function homeStatusPut_(g, x, y, c) {
  x = Math.round(x); y = Math.round(y);
  if (y >= 0 && y < g.length && x >= 0 && x < g[0].length) g[y][x] = c;
}

function homeStatusRect_(g, x, y, w, h, c) {
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) homeStatusPut_(g, x + i, y + j, c);
}

function homeStatusLine_(g, x0, y0, x1, y1, c) {
  x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
  const dx = Math.abs(x1 - x0);
  const dy = -Math.abs(y1 - y0);
  const sx = x0 < x1 ? 1 : -1;
  const sy = y0 < y1 ? 1 : -1;
  let err = dx + dy;
  for (;;) {
    homeStatusPut_(g, x0, y0, c);
    if (x0 === x1 && y0 === y1) break;
    const e2 = 2 * err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
}

/** Stamp a character sprite (rows of equal-length strings; '.' = transparent) with a palette. */
function homeStatusStamp_(g, rows, palette, ox, oy) {
  rows.forEach((row, y) => {
    Array.from(row).forEach((ch, x) => { if (ch !== '.' && palette[ch]) homeStatusPut_(g, ox + x, oy + y, palette[ch]); });
  });
}

/** Grid -> one <path> per colour made of horizontal runs. */
function homeStatusGridPaths_(g) {
  const byColor = {};
  g.forEach((row, y) => {
    let x = 0;
    while (x < row.length) {
      const c = row[x];
      if (!c) { x += 1; continue; }
      let run = 1;
      while (x + run < row.length && row[x + run] === c) run += 1;
      byColor[c] = (byColor[c] || '') + 'M' + x + ' ' + y + 'h' + run + 'v1h-' + run + 'z';
      x += run;
    }
  });
  return Object.keys(byColor).map(c => '<path fill="' + c + '" d="' + byColor[c] + '"/>').join('');
}

function homeStatusSvg_(inner, w, h) {
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" shape-rendering="crispEdges" aria-hidden="true" focusable="false">' + inner + '</svg>';
}

/** Three groups of stars; each group is its own layer so the twinkle is a cheap whole-layer opacity animation. */
function homeStatusStarsSvg_() {
  const rnd = homeStatusRng_(1407);
  const groups = ['', '', ''];
  for (let i = 0; i < 84; i++) {
    const x = Math.floor(rnd() * HOME_STATUS_SCENE_W);
    const y = Math.floor(rnd() * 96);
    groups[i % 3] += 'M' + x + ' ' + y + 'h1v1h-1z';
    if (i % 9 === 0) groups[i % 3] += 'M' + (x - 1) + ' ' + y + 'h3v1h-3zM' + x + ' ' + (y - 1) + 'h1v3h-1z';
  }
  const colors = ['#cfe4ff', '#fff1d0', '#9fd3ff'];
  return groups.map((d, i) => '<div class="hs-layer hs-stars hs-tw-' + 'abc'[i] + '">'
    + homeStatusSvg_('<path fill="' + colors[i] + '" d="' + d + '"/>', HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H) + '</div>').join('');
}

function homeStatusMoonSvg_() {
  const g = homeStatusGrid_();
  const cx = 92, cy = 84, r = 8;
  for (let y = -r; y <= r; y++) {
    for (let x = -r; x <= r; x++) {
      if (x * x + y * y > r * r + 1) continue;
      const shade = (x + 3) * (x + 3) + (y - 2) * (y - 2) > 70 || x > 4;
      homeStatusPut_(g, cx + x, cy + y, shade ? '#d9cfa6' : '#f6edcb');
    }
  }
  [[-3, -2], [2, 3], [3, -4], [-4, 3]].forEach(p => homeStatusPut_(g, cx + p[0], cy + p[1], '#c2b68c'));
  return homeStatusSvg_(homeStatusGridPaths_(g), HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H);
}

function homeStatusFarSvg_() {
  const g = homeStatusGrid_();
  const gy = HOME_STATUS_GROUND_Y;
  const hill = (base, a1, p1, a2, p2, ph) => x => Math.round(base + a1 * Math.sin(x / p1 + ph) + a2 * Math.sin(x / p2 + ph * 2.3));
  const back = hill(102, 7, 41, 3, 13, 0.6);
  const front = hill(111, 5, 29, 2.5, 11, 2.1);
  for (let x = 0; x < HOME_STATUS_SCENE_W; x++) {
    for (let y = back(x); y < gy; y++) homeStatusPut_(g, x, y, '#1d2a4a');
    for (let y = front(x); y < gy; y++) homeStatusPut_(g, x, y, '#16213c');
  }
  // distant pylons on the back ridge with sagging lines between them
  const pylons = [210, 292, 372, 452];
  pylons.forEach(px => {
    const top = back(px) - 15;
    homeStatusLine_(g, px - 4, back(px), px, top + 4, '#3a4d74');
    homeStatusLine_(g, px + 4, back(px), px, top + 4, '#3a4d74');
    homeStatusLine_(g, px, top + 4, px, top, '#3a4d74');
    homeStatusRect_(g, px - 4, top + 5, 9, 1, '#3a4d74');
    homeStatusRect_(g, px - 3, top + 9, 7, 1, '#2f4066');
  });
  for (let i = 0; i + 1 < pylons.length; i++) {
    const a = pylons[i], b = pylons[i + 1];
    const ya = back(a) - 10, yb = back(b) - 10;
    for (let x = a; x < b; x++) {
      const t = (x - a) / (b - a);
      homeStatusPut_(g, x, ya + (yb - ya) * t + 5 * 4 * t * (1 - t), '#3a4d74');
    }
  }
  // windows of a far village and a yard light
  [[236, 117], [243, 119], [251, 116], [330, 118], [338, 116], [346, 119], [410, 117], [418, 118]].forEach((p, i) => {
    homeStatusPut_(g, p[0], p[1], i % 3 === 0 ? '#7fd4ff' : '#ffd27a');
  });
  return homeStatusSvg_(homeStatusGridPaths_(g), HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H);
}

function homeStatusTower_(g, cx, base, p) {
  const legW = 14, kneeY = base - 40, mastY = base - 62;
  // legs (2 px steel + a lit left edge), mast and peak
  [-1, 1].forEach(side => {
    homeStatusLine_(g, cx + side * legW, base, cx + side * 3, kneeY, p.steel);
    homeStatusLine_(g, cx + side * legW + side, base, cx + side * 3 + side, kneeY, p.steelDark);
    homeStatusLine_(g, cx + side * 3, kneeY, cx + side * 1, mastY, p.steel);
    homeStatusLine_(g, cx + side * 3 + side, kneeY, cx + side * 1 + side, mastY, p.steelDark);
  });
  homeStatusLine_(g, cx - 1, mastY, cx, mastY - 5, p.steel);
  homeStatusLine_(g, cx + 1, mastY, cx, mastY - 5, p.steel);
  homeStatusLine_(g, cx - legW, base, cx - 3, kneeY, p.rim);
  // horizontal braces and X braces between the legs
  const halfAt = y => y >= kneeY ? 3 + (legW - 3) * (y - kneeY) / (base - kneeY) : 1 + 2 * (y - mastY) / (kneeY - mastY);
  const levels = [];
  for (let y = base - 6; y > mastY; y -= 8) levels.push(y);
  levels.forEach(y => homeStatusRect_(g, cx - halfAt(y), y, Math.round(halfAt(y) * 2) + 1, 1, p.steelDark));
  for (let i = 0; i + 1 < levels.length; i++) {
    const lo = levels[i], hi = levels[i + 1];
    homeStatusLine_(g, cx - halfAt(lo), lo, cx + halfAt(hi), hi, p.brace);
    homeStatusLine_(g, cx + halfAt(lo), lo, cx - halfAt(hi), hi, p.brace);
  }
  // two cross-arms with hanging insulator strings
  const arms = [{ y: base - 58, hw: 15 }, { y: base - 46, hw: 19 }];
  const tips = [];
  arms.forEach(arm => {
    homeStatusRect_(g, cx - arm.hw, arm.y, arm.hw * 2 + 1, 2, p.steel);
    homeStatusRect_(g, cx - arm.hw, arm.y, arm.hw * 2 + 1, 1, p.rim);
    [-1, 1].forEach(side => {
      const x = cx + side * (arm.hw - 1);
      homeStatusRect_(g, x, arm.y + 2, 1, 5, p.glass);
      homeStatusPut_(g, x, arm.y + 2, p.cap);
      homeStatusPut_(g, x, arm.y + 7, p.cap);
      tips.push({ x, y: arm.y + 8, side });
    });
  });
  tips.push({ x: cx, y: mastY - 5, side: 1 }, { x: cx, y: mastY - 5, side: -1 });
  return tips;
}

function homeStatusWire_(g, x0, y0, x1, y1, sag, color) {
  let px = x0, py = y0;
  const steps = Math.abs(x1 - x0);
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const x = x0 + (x1 - x0) * t;
    const y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t);
    homeStatusLine_(g, px, py, x, y, color);
    px = x; py = y;
  }
}

function homeStatusMidSvg_() {
  const g = homeStatusGrid_();
  const gy = HOME_STATUS_GROUND_Y;
  const pal = { steel: '#3c5170', steelDark: '#2a3a55', brace: '#22304a', rim: '#6d89ae', glass: '#a8cfe3', cap: '#5f748f' };
  const tx = 150;
  const tips = homeStatusTower_(g, tx, gy, pal);
  tips.forEach((t, i) => {
    if (t.side < 0) homeStatusWire_(g, t.x, t.y, 0, t.y + 6 + (i % 3) * 2, 7, '#31466d');
    else homeStatusWire_(g, t.x, t.y, HOME_STATUS_SCENE_W - 1, t.y + 20 + (i % 3) * 2, 10, '#31466d');
  });
  // substation: gantry, transformer with conservator tank and three bushings, radiator, control hut, fence
  const sx = 62;
  homeStatusRect_(g, sx, gy - 24, 2, 24, '#33445f');
  homeStatusRect_(g, sx + 58, gy - 24, 2, 24, '#33445f');
  homeStatusRect_(g, sx, gy - 24, 60, 2, '#3f5373');
  [10, 29, 48].forEach(o => { homeStatusRect_(g, sx + o, gy - 22, 1, 4, '#a8cfe3'); homeStatusPut_(g, sx + o, gy - 18, '#5f748f'); });
  homeStatusRect_(g, sx + 12, gy - 14, 24, 14, '#2a3b57');
  homeStatusRect_(g, sx + 12, gy - 14, 24, 2, '#4a6285');
  for (let x = sx + 14; x < sx + 35; x += 3) homeStatusRect_(g, x, gy - 11, 1, 10, '#1c2840');
  homeStatusRect_(g, sx + 14, gy - 19, 18, 5, '#34496a');
  homeStatusRect_(g, sx + 14, gy - 19, 18, 1, '#58739b');
  [17, 22, 27].forEach(o => {
    homeStatusRect_(g, sx + o, gy - 26, 2, 7, '#b88f63');
    for (let y = gy - 25; y < gy - 20; y += 2) homeStatusRect_(g, sx + o - 1, y, 4, 1, '#8c6a49');
  });
  homeStatusRect_(g, sx + 37, gy - 12, 8, 12, '#263653');
  for (let x = sx + 38; x < sx + 45; x += 2) homeStatusRect_(g, x, gy - 11, 1, 10, '#18233a');
  homeStatusRect_(g, sx + 47, gy - 15, 13, 15, '#2c3d5b');
  homeStatusRect_(g, sx + 47, gy - 16, 13, 2, '#445b80');
  homeStatusRect_(g, sx + 50, gy - 11, 4, 4, '#ffd27a');
  homeStatusRect_(g, sx + 50, gy - 11, 4, 1, '#fff0c0');
  homeStatusRect_(g, sx + 56, gy - 8, 3, 8, '#1a263d');
  for (let x = 4; x < 130; x += 9) if (x < sx - 2 || x > sx + 62) homeStatusRect_(g, x, gy - 8, 1, 8, '#26344f');
  homeStatusRect_(g, 4, gy - 7, 126, 1, '#26344f');
  homeStatusRect_(g, 4, gy - 3, 126, 1, '#26344f');
  return homeStatusSvg_(homeStatusGridPaths_(g), HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H);
}

function homeStatusGroundSvg_() {
  const g = homeStatusGrid_();
  const gy = HOME_STATUS_GROUND_Y;
  const rnd = homeStatusRng_(88);
  homeStatusRect_(g, 0, gy, HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H - gy, '#151d31');
  homeStatusRect_(g, 0, gy, HOME_STATUS_SCENE_W, 1, '#2b3b58');
  homeStatusRect_(g, 0, gy + 1, HOME_STATUS_SCENE_W, 1, '#1d2842');
  for (let i = 0; i < 150; i++) homeStatusPut_(g, Math.floor(rnd() * HOME_STATUS_SCENE_W), gy + 2 + Math.floor(rnd() * 14), rnd() < 0.5 ? '#202c48' : '#0f1626');
  // gravel path in front of the hero
  for (let i = 0; i < 38; i++) homeStatusPut_(g, 6 + Math.floor(rnd() * 70), gy + 2 + Math.floor(rnd() * 5), '#34456a');
  // lantern post
  homeStatusRect_(g, 11, 92, 2, gy - 92, '#2b3550');
  homeStatusRect_(g, 11, 92, 1, gy - 92, '#43547a');
  homeStatusRect_(g, 9, gy - 3, 6, 3, '#222c45');
  homeStatusRect_(g, 11, 91, 9, 2, '#2b3550');
  homeStatusPut_(g, 19, 93, '#2b3550');
  homeStatusRect_(g, 15, 94, 6, 1, '#3b2f2a');
  homeStatusRect_(g, 15, 95, 6, 7, '#ffbf66');
  homeStatusRect_(g, 16, 96, 4, 5, '#ffe3a0');
  homeStatusRect_(g, 17, 97, 2, 3, '#fff6d6');
  homeStatusRect_(g, 15, 95, 1, 7, '#3b2f2a');
  homeStatusRect_(g, 20, 95, 1, 7, '#3b2f2a');
  homeStatusRect_(g, 15, 102, 6, 1, '#3b2f2a');
  return homeStatusSvg_(homeStatusGridPaths_(g), HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H);
}

function homeStatusNearSvg_() {
  const g = homeStatusGrid_();
  const rnd = homeStatusRng_(515);
  const gy = HOME_STATUS_SCENE_H;
  for (let x = 0; x < HOME_STATUS_SCENE_W; x += 2 + Math.floor(rnd() * 3)) {
    const nearHero = x > 14 && x < 62;
    const h = nearHero ? 3 + Math.floor(rnd() * 4) : 6 + Math.floor(rnd() * 12);
    const lean = rnd() < 0.5 ? -1 : 1;
    for (let j = 0; j < h; j++) {
      const off = Math.round(lean * j * 0.25);
      homeStatusPut_(g, x + off, gy - 1 - j, j > h - 3 ? '#0a1020' : '#060a14');
      homeStatusPut_(g, x + off + 1, gy - 1 - j, '#060a14');
    }
  }
  return homeStatusSvg_(homeStatusGridPaths_(g), HOME_STATUS_SCENE_W, HOME_STATUS_SCENE_H);
}

/** The pixel electrical engineer: hard hat, hi-vis vest, navy overalls, a glowing tablet.  22 x 27 pixels. */
const HOME_STATUS_HERO_PALETTE = {
  O: '#0c1322', H: '#ffc533', h: '#e39a1f', S: '#f2bf9a', s: '#cf8f6e', E: '#0c1322', M: '#a8574a', N: '#4a3426',
  V: '#ff7b33', v: '#cc5217', R: '#e9f6ff', W: '#aebfd2', w: '#7f93aa', B: '#34527f', b: '#253c5e', K: '#2b2432',
  G: '#e0cfa6', y: '#ffd36b', L: '#58c6ff', l: '#d6f4ff'
};
const HOME_STATUS_HERO_BODY = [
  '.....OOOOOOOO.....',
  '....OHHHHHHHHO....',
  '...OHHhHHHHHHHO...',
  '...OHhHHHHHHHHO...',
  '.OOHHHHHHHHHHHHOO.',
  '.OOOOOOOOOOOOOOOO.',
  '...ONNssssssssO...',
  '...ONNSSESSSESO...',
  '...ONNSSSSSSSSO...',
  '...OSSSSSSSMMSO...',
  '....OsSSSSSSsO....',
  '.....OOOSSOOO.....',
  '..OVVVVVVVVVVVVO..',
  '.OWWVRVVVVVRVVWWO.',
  '.OWWVRVVVVVRVVWWO.',
  '.OWwVRvvvvvRvvWwO.',
  '.OGGOKKKyKKKKOGGO.',
  '..OBBBBBBBBBBBBO..',
  '..OBBbbBBBBBBBBO..',
  '..OBBBBBBBBBBBBO..',
  '..OBBBBBOOBBBBBO..',
  '..OBBBBbOOBBBBbO..',
  '..OBBBBbOOBBBBbO..',
  '..OBBBBBOOBBBBBO..',
  '..OKKKKKOOKKKKKO..',
  '.OKKKKKKOOKKKKKKO.',
  '.OOOOOOOOOOOOOOOO.'
];
const HOME_STATUS_HERO_TABLET = [
  '.OOOOOO',
  '.OLllLO',
  '.OLLLlO',
  'GOlLLLO',
  'GOLLlLO',
  '.OLLLLO',
  '.OOOOOO'
];

function homeStatusHeroSvg_() {
  const w = 22, h = HOME_STATUS_HERO_BODY.length;
  const grid = [];
  for (let y = 0; y < h; y++) grid.push(new Array(w).fill(''));
  const stamp = (art, ox, oy) => art.forEach((row, y) => Array.from(row).forEach((ch, x) => {
    const c = HOME_STATUS_HERO_PALETTE[ch];
    if (ch !== '.' && c && oy + y < h && ox + x < w) grid[oy + y][ox + x] = c;
  }));
  stamp(HOME_STATUS_HERO_BODY, 0, 0);
  stamp(HOME_STATUS_HERO_TABLET, 15, 12);
  return homeStatusSvg_(homeStatusGridPaths_(grid), w, h);
}

/** The whole scene as HTML (built once, after first paint). */
function homeStatusSceneHtml() {
  const layer = (cls, svg) => '<div class="hs-layer ' + cls + '">' + svg + '</div>';
  const flies = [[40, 108, 0], [88, 96, 1.7], [128, 112, 3.1], [176, 100, 0.9], [22, 118, 2.4]]
    .map(f => '<i class="hs-fly" style="left:calc(var(--px)*' + f[0] + ');bottom:calc(var(--px)*' + (HOME_STATUS_SCENE_H - f[1]) + ');animation-delay:-' + f[2] + 's"></i>').join('');
  const sparks = [0, 1, 2, 3, 4].map(i => '<i class="hs-spark" style="--k:' + i + '"></i>').join('');
  return homeStatusStarsSvg_() + layer('hs-sky', homeStatusMoonSvg_())
    + '<i class="hs-moonglow"></i>'
    + layer('hs-far', homeStatusFarSvg_())
    + layer('hs-mid', homeStatusMidSvg_())
    + '<i class="hs-beacon"></i>'
    + layer('hs-ground', homeStatusGroundSvg_())
    + '<i class="hs-pool"></i><i class="hs-lamp"></i>'
    + '<div class="hs-hero"><div class="hs-hero-body">' + homeStatusHeroSvg_() + '<i class="hs-screen"></i>' + sparks + '</div><i class="hs-shadow"></i></div>'
    + layer('hs-near', homeStatusNearSvg_())
    + flies
    + '<i class="hs-vignette"></i>';
}

// ---- DOM glue -----------------------------------------------------------------

let homeStatusCollapsed = null;
let homeStatusLastHtml = '';
let homeStatusSceneBuilt = false;
let homeStatusIntroTimer = null;

/** Gather the model inputs from the existing stores (every read is guarded). */
function homeStatusInputs(now) {
  const t = Number.isFinite(now) ? now : Date.now();
  let state = null;
  try { state = typeof todayTaskState !== 'undefined' && todayTaskState ? todayTaskState : (typeof loadTodayTaskState === 'function' ? loadTodayTaskState() : null); } catch (_) { state = null; }
  let records = [];
  try { records = typeof getResultRecords === 'function' ? getResultRecords() : []; } catch (_) { records = []; }
  let scoreboard = null;
  try { scoreboard = typeof scoreboardCompute === 'function' ? scoreboardCompute(records, t) : null; } catch (_) { scoreboard = null; }
  let reviewDates = [];
  try { reviewDates = typeof sm2Schedule !== 'undefined' && sm2Schedule ? Object.keys(sm2Schedule).map(q => sm2Schedule[q] && sm2Schedule[q].lastReviewed).filter(Boolean) : []; } catch (_) { reviewDates = []; }
  let totalTasks = 0;
  try { totalTasks = typeof DAILY_SCHEDULE !== 'undefined' && DAILY_SCHEDULE.order ? DAILY_SCHEDULE.order.length : 0; } catch (_) { totalTasks = 0; }
  return { now: t, completed: state && state.completed ? state.completed : {}, totalTasks, records, reviewDates, scoreboard, examDate: HOME_STATUS_EXAM_DATE };
}

function homeStatusApplyCollapsed_(host) {
  const collapsed = !!homeStatusCollapsed;
  host.classList.toggle('hs--collapsed', collapsed);
  const btn = host.querySelector('.hs-toggle');
  const body = host.querySelector('.hs-body');
  if (btn) { btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true'); btn.textContent = collapsed ? '展開' : '收合'; }
  if (body) body.hidden = collapsed;
}

/** Redraw the status window.  Cheap no-op when nothing changed; the typing intro plays on the first draw only. */
function homeStatusRefresh() {
  if (typeof document === 'undefined') return;
  const host = document.getElementById('home-status');
  if (!host) return;
  try {
    const html = homeStatusHtml(homeStatusModel(homeStatusInputs(Date.now())));
    if (html === homeStatusLastHtml) return;
    const first = homeStatusLastHtml === '';
    homeStatusLastHtml = html;
    if (homeStatusCollapsed === null) {
      homeStatusCollapsed = typeof window.matchMedia === 'function' && window.matchMedia('(max-width: 640px)').matches;
    }
    if (!first) host.classList.remove('hs--intro');
    host.innerHTML = html;
    homeStatusApplyCollapsed_(host);
    if (first) {
      host.classList.add('hs--intro');
      homeStatusIntroTimer = setTimeout(() => host.classList.remove('hs--intro'), 5200);
    }
  } catch (_) {
    host.innerHTML = '';
  }
}

function homeStatusToggle() {
  const host = document.getElementById('home-status');
  if (!host) return;
  homeStatusCollapsed = !homeStatusCollapsed;
  host.classList.remove('hs--intro');
  homeStatusApplyCollapsed_(host);
}

function homeStatusBuildScene() {
  if (homeStatusSceneBuilt || typeof document === 'undefined') return;
  const host = document.getElementById('hs-scene');
  if (!host) return;
  homeStatusSceneBuilt = true;
  try { host.innerHTML = homeStatusSceneHtml(); host.classList.add('hs-scene--ready'); } catch (_) { host.innerHTML = ''; }
}

/** Called once from main.js: the window draws now, the scene right after the first frame (never blocks load). */
function homeStatusInit() {
  homeStatusRefresh();
  const build = () => setTimeout(homeStatusBuildScene, 0);
  if (typeof requestAnimationFrame === 'function') requestAnimationFrame(build); else build();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    HOME_STATUS_EXAM_DATE, homeStatusModel, homeStatusLevelFor, homeStatusExpNeed, homeStatusExpToReach,
    homeStatusTitleFor, homeStatusCardExp, homeStatusStreak, homeStatusDaysUntil, homeStatusHtml,
    homeStatusPixelText, homeStatusSceneHtml
  };
}
