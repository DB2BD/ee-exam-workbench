// src/features/breakdownDrill/component.js
/**
 * 破題訓練 (optional feature — delete src/features/breakdownDrill/ to remove it): look at a stem for at most 2 minutes, pick its type (chapter) from four options of the same
 * subject, optionally write the first step, then reveal the chapter, its core formula and the note's 「解題邏輯」
 * and self-rate the first step.  Records, spacing and round selection live in store.js next to this file.
 *
 * Depends (call time): BREAKDOWN_DRILL, KNOWLEDGE_DAG, TARGET_ALLOCATION, QUESTION_CROP_MAP, anchorBankFromGlobals_,
 * anchorContext / anchorChapterStats (mastery for weak-first selection), resolveImageMapUrl, openImageLightbox,
 * processMarkdownWithMath, renderCoreFormulaHtml, homeStatusRefresh, uiIcon.
 */

const BREAKDOWN_DRILL_CONTAINER_ID = 'breakdown-drill-container';

// In-memory state of the round on screen; the round itself (qids, index, results) is persisted as `active`.
let breakdownDrillView = null;
let breakdownDrillTimer = null;

function breakdownDrillEscape_(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function breakdownDrillChapterName(chapterId) {
  const node = typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG ? KNOWLEDGE_DAG[chapterId] : null;
  return node && node.name ? node.name : String(chapterId || '');
}

function breakdownDrillSubjectName(subjectId) {
  const alloc = typeof TARGET_ALLOCATION !== 'undefined' && TARGET_ALLOCATION && TARGET_ALLOCATION.subjects;
  return alloc && alloc[subjectId] && alloc[subjectId].name ? alloc[subjectId].name : String(subjectId || '');
}

function breakdownDrillHeldQids_() {
  const held = new Set();
  const add = value => {
    if (!value) return;
    if (typeof value.forEach === 'function') value.forEach(q => held.add(String(q)));
    else Object.keys(value).forEach(q => held.add(q));
  };
  try { if (typeof practiceLockedQids === 'function') add(practiceLockedQids({})); } catch (_) { /* nothing locked */ }
  try { if (typeof practiceReservedQids === 'function') add(practiceReservedQids({})); } catch (_) { /* nothing reserved */ }
  return held;
}

/** 'YYY-SS' papers of unfinished MOCK / BLIND schedule tasks: none of their questions is drilled. */
function breakdownDrillHeldPapers_() {
  const papers = new Set();
  try {
    const order = typeof DAILY_SCHEDULE !== 'undefined' && DAILY_SCHEDULE && Array.isArray(DAILY_SCHEDULE.order) ? DAILY_SCHEDULE.order : [];
    const state = typeof todayTaskState !== 'undefined' && todayTaskState ? todayTaskState
      : (typeof loadTodayTaskState === 'function' ? loadTodayTaskState() : null);
    const done = state && state.completed ? state.completed : {};
    order.forEach(code => {
      const m = /^(?:MOCK|BLIND)(\d{3})-(\d{2})$/.exec(String(code));
      if (m && !done[code]) papers.add(m[1] + '-' + m[2]);
    });
  } catch (_) { /* no schedule */ }
  return papers;
}

/**
 * Drillable questions: PE questions with a crop, a 解題邏輯 paragraph and a named chapter, minus the questions held
 * back for unfinished mock / blind-test papers and fixed schedule tasks (seeing their stems would spoil them).
 */
function breakdownDrillBank() {
  const data = typeof BREAKDOWN_DRILL !== 'undefined' && BREAKDOWN_DRILL ? BREAKDOWN_DRILL : {};
  const rows = typeof anchorBankFromGlobals_ === 'function' ? anchorBankFromGlobals_() : [];
  const dag = typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG ? KNOWLEDGE_DAG : {};
  const held = breakdownDrillHeldQids_();
  const papers = breakdownDrillHeldPapers_();
  return rows.filter(q => q.crop && !held.has(q.id) && !papers.has(q.year + '-' + q.subject) && data[q.id] && data[q.id].logicMd && data[q.id].chapter && dag[data[q.id].chapter])
    .map(q => ({ id: q.id, subject: q.subject, year: q.year, chapter: data[q.id].chapter }));
}

function breakdownDrillMastery_() {
  const out = {};
  try {
    if (typeof anchorChapterStats === 'function' && typeof anchorContext === 'function') {
      const stats = anchorChapterStats(anchorContext());
      Object.keys(stats || {}).forEach(ch => { out[ch] = stats[ch].m; });
    }
  } catch (_) { /* every chapter counts as weak */ }
  return out;
}

function breakdownDrillContainer_() {
  return typeof document !== 'undefined' ? document.getElementById(BREAKDOWN_DRILL_CONTAINER_ID) : null;
}

function breakdownDrillStopTimer_() {
  if (breakdownDrillTimer) clearInterval(breakdownDrillTimer);
  breakdownDrillTimer = null;
}

function breakdownDrillSaveActive_(active) {
  const state = loadBreakdownDrillState();
  state.active = active;
  saveBreakdownDrillState(state);
}

/** Start a new round (or resume the saved one when `resume` is true and it is unfinished). */
function breakdownDrillStart(resume) {
  const bank = breakdownDrillBank();
  if (!bank.length) return;
  const state = loadBreakdownDrillState();
  let active = resume && state.active && state.active.index < state.active.qids.length ? state.active : null;
  if (!active) {
    const qids = breakdownDrillBuildRound({ bank, records: state.records, now: Date.now(), mastery: breakdownDrillMastery_() });
    active = { qids, index: 0, startedAt: Date.now(), results: [] };
    breakdownDrillSaveActive_(active);
  }
  breakdownDrillView = { bank, active, phase: 'ask' };
  breakdownDrillBeginQuestion_();
  const host = breakdownDrillContainer_();
  if (host && typeof host.scrollIntoView === 'function') host.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function breakdownDrillBeginQuestion_() {
  const v = breakdownDrillView;
  if (!v) return;
  if (v.active.index >= v.active.qids.length) { breakdownDrillFinish_(); return; }
  const qid = v.active.qids[v.active.index];
  const question = v.bank.find(q => q.id === qid);
  if (!question) { v.active.index += 1; breakdownDrillBeginQuestion_(); return; }  // held back since the round began
  Object.assign(v, {
    phase: 'ask', question, options: breakdownDrillOptions(question, v.bank),
    picked: '', firstStep: '', startMs: Date.now(), remaining: BREAKDOWN_DRILL_SECONDS, timedOut: false, typeOk: false
  });
  breakdownDrillRender();
  breakdownDrillStopTimer_();
  breakdownDrillTimer = setInterval(breakdownDrillTick, 1000);
}

function breakdownDrillTick() {
  const v = breakdownDrillView;
  if (!v || v.phase !== 'ask') { breakdownDrillStopTimer_(); return; }
  v.remaining = Math.max(0, BREAKDOWN_DRILL_SECONDS - Math.floor((Date.now() - v.startMs) / 1000));
  const el = typeof document !== 'undefined' ? document.getElementById('bd-timer') : null;
  if (el) {
    el.textContent = breakdownDrillClock_(v.remaining);
    el.classList.toggle('bd-timer--low', v.remaining <= 20);
  }
  if (v.remaining <= 0) breakdownDrillReveal(true);
}

function breakdownDrillClock_(seconds) {
  return Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2, '0');
}

function breakdownDrillPick(index) {
  const v = breakdownDrillView;
  if (!v || v.phase !== 'ask') return;
  v.picked = v.options[index] || '';
  document.querySelectorAll('.bd-option').forEach((btn, i) => {
    btn.classList.toggle('bd-option--picked', i === index);
    btn.setAttribute('aria-pressed', i === index ? 'true' : 'false');
  });
  const reveal = document.getElementById('bd-reveal');
  if (reveal) reveal.textContent = '翻答案';
}

function breakdownDrillReveal(timedOut) {
  const v = breakdownDrillView;
  if (!v || v.phase !== 'ask') return;
  breakdownDrillStopTimer_();
  const note = document.getElementById('bd-first-step');
  v.firstStep = note ? note.value.trim() : '';
  v.timedOut = timedOut === true;
  v.typeOk = v.picked === v.question.chapter;
  v.secs = Math.min(BREAKDOWN_DRILL_SECONDS, Math.round((Date.now() - v.startMs) / 1000));
  v.phase = 'reveal';
  breakdownDrillRender();
}

function breakdownDrillRate(startOk) {
  const v = breakdownDrillView;
  if (!v || v.phase !== 'reveal') return;
  const at = Date.now();
  const record = {
    id: 'bd-' + at + '-' + v.question.id + '-' + Math.random().toString(36).slice(2, 8),
    qid: v.question.id, at, chapter: v.question.chapter, picked: v.picked,
    typeOk: v.typeOk, startOk: startOk === true, timedOut: v.timedOut, secs: v.secs
  };
  const state = loadBreakdownDrillState();
  state.records.push(record);
  v.active.results.push(record.id);
  v.active.index += 1;
  state.active = v.active.index < v.active.qids.length ? v.active : null;
  saveBreakdownDrillState(state);
  if (typeof homeStatusRefresh === 'function') { try { homeStatusRefresh(); } catch (_) { /* status window is optional */ } }
  breakdownDrillBeginQuestion_();
}

function breakdownDrillFinish_() {
  const v = breakdownDrillView;
  breakdownDrillStopTimer_();
  if (!v) return;
  const ids = {};
  v.active.results.forEach(id => { ids[id] = true; });
  v.summary = loadBreakdownDrillState().records.filter(r => ids[r.id]);
  v.phase = 'summary';
  breakdownDrillRender();
}

function breakdownDrillQuit() {
  breakdownDrillStopTimer_();
  breakdownDrillView = null;
  breakdownDrillRender();
}

// ---- HTML -----------------------------------------------------------------------------------

function breakdownDrillCropHtml_(qid) {
  const crop = typeof QUESTION_CROP_MAP !== 'undefined' && QUESTION_CROP_MAP ? QUESTION_CROP_MAP[qid] || '' : '';
  const src = crop && typeof resolveImageMapUrl === 'function' ? resolveImageMapUrl(crop, false, qid) : crop;
  if (!src) return '<p class="bd-empty">這題沒有題目截圖。</p>';
  const safe = breakdownDrillEscape_(src);
  return '<img class="bd-crop" src="' + safe + '" alt="' + breakdownDrillEscape_(qid) + ' 題目；點擊放大" tabindex="0" role="button"'
    + ' onclick="breakdownDrillZoom(this)" onkeydown="if(event.key===\'Enter\')breakdownDrillZoom(this)">';
}

function breakdownDrillZoom(img) {
  if (typeof openImageLightbox === 'function') openImageLightbox(img.getAttribute('src'), img.getAttribute('alt'), img);
}

function breakdownDrillHeadHtml_(v) {
  const q = v.question;
  const n = v.active.index + 1;
  const total = v.active.qids.length;
  const timer = v.phase === 'ask'
    ? '<span class="bd-timer" id="bd-timer" role="timer" aria-label="剩餘時間">' + breakdownDrillClock_(v.remaining) + '</span>' : '';
  return '<div class="bd-head">'
    + '<div class="bd-title"><strong>破題訓練</strong><span>第 ' + n + '／' + total + ' 題 · ' + breakdownDrillEscape_(breakdownDrillSubjectName(q.subject))
    + ' · ' + q.year + ' 年</span></div>' + timer
    + '<button type="button" class="bd-quit" onclick="breakdownDrillQuit()" aria-label="結束破題訓練">' + (typeof uiIcon === 'function' ? uiIcon('x') : '×') + '</button>'
    + '</div>';
}

function breakdownDrillAskHtml_(v) {
  const options = v.options.map((ch, i) => '<button type="button" class="bd-option" aria-pressed="false" onclick="breakdownDrillPick(' + i + ')">'
    + '<span class="bd-option-key">' + 'ABCD'.charAt(i) + '</span>' + breakdownDrillEscape_(breakdownDrillChapterName(ch)) + '</button>').join('');
  return breakdownDrillHeadHtml_(v)
    + '<div class="bd-stem">' + breakdownDrillCropHtml_(v.question.id) + '</div>'
    + '<p class="bd-step-label">① 這題是哪一型？</p><div class="bd-options">' + options + '</div>'
    + '<label class="bd-step-label" for="bd-first-step">② 第一步寫什麼？（公式、要畫的圖；選填）</label>'
    + '<textarea id="bd-first-step" class="bd-first-step" rows="2" placeholder="例：畫等效電路，P = 3VE sinδ / Xs"></textarea>'
    + '<div class="bd-actions"><button type="button" class="bd-primary" id="bd-reveal" onclick="breakdownDrillReveal(false)">不確定，直接翻答案</button></div>';
}

function breakdownDrillRevealHtml_(v) {
  const q = v.question;
  const node = typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG ? KNOWLEDGE_DAG[q.chapter] : null;
  const formula = node && node.coreFormula && typeof renderCoreFormulaHtml === 'function' ? renderCoreFormulaHtml(node.coreFormula, true) : '';
  const logicMd = BREAKDOWN_DRILL[q.id].logicMd;
  const logic = typeof processMarkdownWithMath === 'function' ? processMarkdownWithMath(logicMd) : breakdownDrillEscape_(logicMd);
  const verdict = v.typeOk
    ? '<p class="bd-verdict bd-verdict--ok">' + (typeof uiIcon === 'function' ? uiIcon('check') : '') + ' 題型正確：' + breakdownDrillEscape_(breakdownDrillChapterName(q.chapter)) + '</p>'
    : '<p class="bd-verdict bd-verdict--miss">題型：' + breakdownDrillEscape_(breakdownDrillChapterName(q.chapter))
      + (v.picked ? '<small>你選：' + breakdownDrillEscape_(breakdownDrillChapterName(v.picked)) + '</small>' : '<small>' + (v.timedOut ? '時間到，未選題型' : '未選題型') + '</small>') + '</p>';
  const mine = v.firstStep ? '<div class="bd-block"><h4>你寫的第一步</h4><p class="bd-mine">' + breakdownDrillEscape_(v.firstStep) + '</p></div>' : '';
  return breakdownDrillHeadHtml_(v)
    + '<details class="bd-stem-again"><summary>再看一次題目</summary>' + breakdownDrillCropHtml_(q.id) + '</details>'
    + verdict
    + (formula ? '<div class="bd-block"><h4>核心公式</h4><div class="bd-formula">' + formula + '</div></div>' : '')
    + '<div class="bd-block"><h4>解題邏輯</h4><div class="bd-logic">' + logic + '</div></div>'
    + mine
    + '<p class="bd-step-label">③ 你的起手方向對嗎？</p>'
    + '<div class="bd-actions bd-actions--rate">'
    + '<button type="button" class="bd-primary" onclick="breakdownDrillRate(true)">方向對</button>'
    + '<button type="button" class="bd-secondary" onclick="breakdownDrillRate(false)">方向錯／沒想到</button></div>';
}

function breakdownDrillSummaryHtml_(v) {
  const recs = v.summary || [];
  const typeHits = recs.filter(r => r.typeOk).length;
  const startHits = recs.filter(r => r.startOk).length;
  const exp = breakdownDrillExp(recs);
  const misses = recs.filter(r => !r.typeOk || !r.startOk).map(r => '<li><span class="bd-qid">' + breakdownDrillEscape_(r.qid) + '</span>'
    + breakdownDrillEscape_(breakdownDrillChapterName(r.chapter))
    + '<small>' + (r.typeOk ? '' : '題型錯') + (!r.typeOk && !r.startOk ? '、' : '') + (r.startOk ? '' : '起手式錯') + '</small></li>').join('');
  return '<div class="bd-head"><div class="bd-title"><strong>破題訓練完成</strong><span>' + recs.length + ' 題</span></div>'
    + '<button type="button" class="bd-quit" onclick="breakdownDrillQuit()" aria-label="關閉">' + (typeof uiIcon === 'function' ? uiIcon('x') : '×') + '</button></div>'
    + '<ul class="bd-stats">'
    + '<li><b>' + typeHits + '／' + recs.length + '</b><span>題型命中</span></li>'
    + '<li><b>' + startHits + '／' + recs.length + '</b><span>起手式命中</span></li>'
    + '<li><b>+' + exp + '</b><span>EXP</span></li></ul>'
    + (misses ? '<div class="bd-block"><h4>要再練的題（隔天會再出現）</h4><ul class="bd-misses">' + misses + '</ul></div>'
      : '<p class="bd-verdict bd-verdict--ok">全部命中，這些題會在 3 天後再複習一次。</p>')
    + '<div class="bd-actions"><button type="button" class="bd-primary" onclick="breakdownDrillStart(false)">再一輪</button>'
    + '<button type="button" class="bd-secondary" onclick="breakdownDrillQuit()">結束</button></div>';
}

/** Idle card: today's due count and the last-7-days hit rate, with the start / resume button. */
function breakdownDrillIdleHtml_() {
  const state = loadBreakdownDrillState();
  const due = breakdownDrillDueQids(state.records, Date.now()).length;
  const resumable = state.active && state.active.index < state.active.qids.length;
  const week = state.records.filter(r => r.at >= Date.now() - 7 * 86400000);
  const rate = week.length ? Math.round(100 * week.filter(r => r.typeOk && r.startOk).length / week.length) : null;
  if (!resumable && !state.records.length) return '';
  return '<div class="bd-idle">'
    + '<span>破題訓練：' + (due ? '今天有 ' + due + ' 題要再練' : '今天沒有到期題')
    + (rate === null ? '' : '｜近 7 天命中 ' + rate + '%（' + week.length + ' 題）') + '</span>'
    + (resumable ? '<button type="button" class="bd-secondary" onclick="breakdownDrillStart(true)">繼續上一輪（第 ' + (state.active.index + 1) + '／' + state.active.qids.length + ' 題）</button>' : '')
    + '</div>';
}

function breakdownDrillRender() {
  const host = breakdownDrillContainer_();
  if (!host) return;
  const v = breakdownDrillView;
  if (!v) {
    host.className = '';
    host.innerHTML = breakdownDrillIdleHtml_();
    return;
  }
  host.className = 'bd-card';
  if (v.phase === 'summary') host.innerHTML = breakdownDrillSummaryHtml_(v);
  else if (v.phase === 'reveal') host.innerHTML = breakdownDrillRevealHtml_(v);
  else host.innerHTML = breakdownDrillAskHtml_(v);
  if (v.phase === 'ask') {
    const picked = v.options.indexOf(v.picked);
    if (picked >= 0) breakdownDrillPick(picked);
  }
}

// ---- Self-mounting (the core shell and main.js know nothing about this feature) ----------------------------

const BREAKDOWN_DRILL_ICON = '<svg class="ui-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="1em" height="1em" fill="none"'
  + ' stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
  + '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>';

/** Adds the 「破題訓練 8 題」 entry to the home primary actions and the drill panel below them (idempotent). */
function breakdownDrillMount() {
  if (typeof document === 'undefined') return;
  const actions = document.querySelector('.home-primary-actions');
  if (!actions || document.getElementById('home-action-drill')) return;
  actions.classList.add('home-primary-actions--drill');
  actions.insertAdjacentHTML('beforeend', '<button id="home-action-drill" class="home-random-button home-drill-button" type="button"'
    + ' onclick="breakdownDrillStart(false)"><span class="ui-ico">' + BREAKDOWN_DRILL_ICON + '</span><strong>破題訓練 8 題</strong>'
    + '<small>2 分鐘內定題型、寫第一步</small></button>');
  actions.insertAdjacentHTML('afterend', '<div id="' + BREAKDOWN_DRILL_CONTAINER_ID + '"></div>');
  breakdownDrillRender();
}

if (typeof registerHomeStatusExpSource === 'function') {
  registerHomeStatusExpSource({
    id: 'breakdownDrill',
    read: () => {
      const records = getBreakdownDrillRecords();
      return { exp: breakdownDrillExp(records), days: records.map(r => breakdownDrillDayKey_(r.at)) };
    }
  });
}

if (typeof document !== 'undefined' && typeof document.addEventListener === 'function') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', breakdownDrillMount);
  else breakdownDrillMount();
  document.addEventListener('ee:data-merged', () => { if (!breakdownDrillView) breakdownDrillRender(); });
}
