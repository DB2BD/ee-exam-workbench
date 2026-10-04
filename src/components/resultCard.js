// src/components/resultCard.js
/**
 * 統一作答結果卡: pure view-model (resultCardViewModel) + DOM (openResultCard).
 * Depends on resultCardStore.js (buildResultModel, scoreResult, saveResultRecord, labels).
 */

const RESULT_CARD_MARK_BUTTONS = [
  { mark: 'o', symbol: '○', text: '全對' },
  { mark: 'tri', symbol: '△', text: '部分' },
  { mark: 'x', symbol: '×', text: '沒寫出' }
];

function resultCardEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function resultCardChapterTitle(qid) {
  try {
    const map = typeof QUESTION_TAXONOMY_MAP !== 'undefined' ? QUESTION_TAXONOMY_MAP : null;
    const evidence = map && map[qid];
    if (evidence) {
      if (typeof evidence === 'object' && evidence.canonicalChapter) return evidence.canonicalChapter;
      const chapterId = typeof evidence === 'string' ? evidence : evidence.primaryChapter;
      const node = chapterId && typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[chapterId] : null;
      if (node && (node.title || node.name)) return node.title || node.name;
      if (chapterId) return chapterId;
    }
  } catch (_) { /* fall through */ }
  return '';
}

function resultCardFormatNumber(value) {
  return String(Math.round(value * 100) / 100);
}

// ○ wording: mock exams score 100/50/0 (○＝全對); basic-tier practice keeps 「骨架寫完」.
function resultCardMarkButtons(tier, source) {
  const basicPractice = tier === 'basic' && source !== 'mock';
  return RESULT_CARD_MARK_BUTTONS.map(b => ({
    mark: b.mark, symbol: b.symbol,
    text: b.mark === 'o' && basicPractice ? '骨架寫完' : b.text
  }));
}

function resultCardViewModel(qid, marks, errors, source) {
  const model = buildResultModel(qid);
  const list = Array.isArray(marks) ? marks : [];
  const score = scoreResult(model, list, source);
  const tierLabel = model.tier === 'basic' ? '基本分' : '主攻';
  const chapter = resultCardChapterTitle(qid);
  const selectedErrors = Array.isArray(errors) ? errors : [];
  const showErrors = model.parts.some((_, i) => list[i] === 'tri' || list[i] === 'x');
  return {
    qid,
    tier: model.tier,
    tierLabel,
    chapter,
    header: [qid, chapter, tierLabel].filter(Boolean).join('｜'),
    markButtons: resultCardMarkButtons(model.tier, source),
    hint: source === 'mock' ? '模考按 100／50／0 計分' : (model.tier === 'basic' ? '○＝骨架寫完' : ''),
    rows: model.parts.map((part, i) => ({
      index: i,
      label: part.label,
      points: part.points,
      pointsText: `${resultCardFormatNumber(part.points)} 分`,
      mark: RESULT_CARD_MARK_BUTTONS.some(b => b.mark === list[i]) ? list[i] : null
    })),
    showErrors,
    errorChips: showErrors
      ? RESULT_CARD_ERROR_CODES.map(code => ({
        code, label: RESULT_CARD_ERROR_LABELS[code], selected: selectedErrors.indexOf(code) >= 0
      }))
      : [],
    estimate: score.estimate,
    total: score.total,
    estimateText: `估計 ${resultCardFormatNumber(score.estimate)}／${resultCardFormatNumber(score.total)} 分`,
    canSave: score.complete
  };
}

function resultCardRemoveExisting() {
  Array.prototype.forEach.call(typeof document !== 'undefined' ? document.querySelectorAll('.result-card-saved-notice') : [], el => el.remove());
  const old = typeof document !== 'undefined' ? document.querySelectorAll('.result-card[data-result-card-docked="1"]') : [];
  Array.prototype.forEach.call(old, el => { if (el.__resultCardClose) el.__resultCardClose(); else el.remove(); });
}

// 「已記錄 ✓」: a short confirmation in the docked card's place; removed after ~1.8s or on the next card.
function resultCardShowSavedNotice(host) {
  try {
    const old = document.querySelectorAll('.result-card-saved-notice');
    Array.prototype.forEach.call(old, el => el.remove());
    const note = document.createElement('div');
    note.className = 'result-card-saved-notice' + (host === document.body ? ' result-card--viewport' : '');
    note.setAttribute('role', 'status');
    note.textContent = '已記錄 ✓';
    (host || document.body).appendChild(note);
    setTimeout(() => note.remove(), 1800);
  } catch (_) { /* cosmetic only */ }
}

// A card docked in the solution window starts as a small bar so it does not
// cover the solution while the learner is still working; inline cards open.
function resultCardStartsCollapsed(options) {
  const opts = options || {};
  return !opts.mount && !opts.expanded;
}

function openResultCard(options) {
  const opts = options || {};
  const qid = String(opts.qid || '');
  const source = opts.source || 'today';
  const model = buildResultModel(qid);
  const marks = model.parts.map(() => null);
  let errors = [];
  let note = '';
  let noteOpen = false;
  let saving = false;

  const docked = !opts.mount;
  if (docked) resultCardRemoveExisting();
  const host = opts.mount || (document.querySelector('#solution-modal .modal-container')) || document.body;
  const root = document.createElement('section');
  root.className = 'result-card' + (docked ? ' result-card--docked' : '');
  root.setAttribute('role', 'group');
  root.setAttribute('aria-label', '作答結果卡');
  if (docked) root.setAttribute('data-result-card-docked', '1');
  if (docked && host === document.body) root.classList.add('result-card--viewport');
  let collapsed = resultCardStartsCollapsed(opts);

  const rowsHtml = model.parts.map((part, i) => `
    <div class="result-card-row" data-row="${i}">
      <div class="result-card-row-label">${resultCardEscape(part.label)} <span class="result-card-row-points">${resultCardEscape(resultCardFormatNumber(part.points))} 分</span></div>
      <div class="result-card-marks" role="group" aria-label="${resultCardEscape(part.label)}結果">
        ${RESULT_CARD_MARK_BUTTONS.map(b => `<button type="button" class="result-card-mark" data-row="${i}" data-mark="${b.mark}" aria-pressed="false">${b.symbol} ${b.text}</button>`).join('')}
      </div>
    </div>`).join('');

  root.innerHTML = `
    <button type="button" class="result-card-expand">✍️ 做完了？記錄作答結果 ▲</button>
    <div class="result-card-head"><span class="result-card-title"></span><span class="result-card-hint"></span>${docked ? '<button type="button" class="result-card-collapse" aria-label="收合作答結果卡">▼ 收合</button>' : ''}</div>
    <div class="result-card-rows">${rowsHtml}</div>
    <div class="result-card-errors" hidden>
      <span class="result-card-errors-label">錯在哪（可多選，可不選）</span>
      <div class="result-card-chips"></div>
    </div>
    <div class="result-card-note">
      <button type="button" class="result-card-note-toggle" aria-expanded="false">＋ 加註（選用）</button>
      <textarea class="result-card-note-input" rows="2" maxlength="2000" aria-label="加註" hidden></textarea>
    </div>
    <div class="result-card-foot">
      <span class="result-card-estimate" aria-live="polite"></span>
      <span class="result-card-msg" role="alert"></span>
      <button type="button" class="result-card-save" disabled>保存並下一題</button>
    </div>`;

  const q = sel => root.querySelector(sel);
  const baseline = new Map();

  function syncPadding() {
    if (!docked) return;
    ['modal-pane-right', 'modal-pane-left'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (!baseline.has(id)) baseline.set(id, el.style.paddingBottom);
      el.style.paddingBottom = `${root.offsetHeight + 16}px`;
    });
  }

  function sync() {
    root.classList.toggle('is-collapsed', collapsed);
    const vm = resultCardViewModel(qid, marks, errors, source);
    q('.result-card-title').textContent = vm.header;
    q('.result-card-hint').textContent = vm.hint;
    vm.markButtons.forEach(b => {
      Array.prototype.forEach.call(root.querySelectorAll(`.result-card-mark[data-mark="${b.mark}"]`), btn => { btn.textContent = `${b.symbol} ${b.text}`; });
    });
    vm.rows.forEach(row => {
      Array.prototype.forEach.call(root.querySelectorAll(`.result-card-mark[data-row="${row.index}"]`), btn => {
        const on = btn.getAttribute('data-mark') === row.mark;
        btn.classList.toggle('on', on);
        btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    });
    const errBox = q('.result-card-errors');
    errBox.hidden = !vm.showErrors;
    if (!vm.showErrors) errors = [];
    q('.result-card-chips').innerHTML = vm.errorChips.map(c => `<button type="button" class="result-card-chip${c.selected ? ' on' : ''}" data-code="${resultCardEscape(c.code)}" aria-pressed="${c.selected}">${resultCardEscape(c.code)} ${resultCardEscape(c.label)}</button>`).join('');
    q('.result-card-estimate').textContent = vm.estimateText;
    q('.result-card-save').disabled = !vm.canSave || saving;
    syncPadding();
  }

  function close() {
    if (observer) observer.disconnect();
    baseline.forEach((value, id) => {
      const el = document.getElementById(id);
      if (el) el.style.paddingBottom = value;
    });
    baseline.clear();
    root.remove();
  }
  root.__resultCardClose = close;

  root.addEventListener('click', event => {
    const target = event.target.closest ? event.target.closest('button') : null;
    if (!target || !root.contains(target)) return;
    if (target.classList.contains('result-card-expand') || target.classList.contains('result-card-collapse')) {
      collapsed = target.classList.contains('result-card-collapse');
      sync();
      return;
    }
    if (target.classList.contains('result-card-mark')) {
      marks[Number(target.getAttribute('data-row'))] = target.getAttribute('data-mark');
      sync();
    } else if (target.classList.contains('result-card-chip')) {
      const code = target.getAttribute('data-code');
      errors = errors.indexOf(code) >= 0 ? errors.filter(c => c !== code) : errors.concat([code]);
      sync();
    } else if (target.classList.contains('result-card-note-toggle')) {
      noteOpen = !noteOpen;
      const input = q('.result-card-note-input');
      input.hidden = !noteOpen;
      target.setAttribute('aria-expanded', noteOpen ? 'true' : 'false');
      target.textContent = noteOpen ? '－ 收合加註' : '＋ 加註（選用）';
      syncPadding();
    } else if (target.classList.contains('result-card-save')) {
      const vm = resultCardViewModel(qid, marks, errors, source);
      if (!vm.canSave || saving) return;
      saving = true;
      const record = {
        qid, at: Date.now(), source, tier: model.tier,
        parts: model.parts.map((p, i) => ({ label: p.label, points: p.points, mark: marks[i] })),
        errors: vm.showErrors ? errors.slice() : [], note, total: model.total
      };
      if (opts.mockId) record.mockId = opts.mockId;
      const result = saveResultRecord(record);
      saving = false;
      if (!result.ok) {
        q('.result-card-msg').textContent = '無法保存，請稍後再試（本機儲存空間不可用或資料損壞）。';
        sync();
        return;
      }
      close();
      // Docked card: no next question to move to, so confirm briefly where the card was and keep the solution open.
      if (docked && typeof document !== 'undefined') resultCardShowSavedNotice(host);
      if (typeof opts.onSaved === 'function') opts.onSaved(result.record, result);
    }
  });
  q('.result-card-note-input').addEventListener('input', event => { note = event.target.value; });

  host.appendChild(root);
  let observer = null;
  if (docked && typeof MutationObserver !== 'undefined') {
    const modal = document.getElementById('solution-modal');
    if (modal) {
      observer = new MutationObserver(() => { if (!modal.classList.contains('show')) close(); });
      observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
    }
  }
  sync();
  return { el: root, close, getState: () => ({ marks: marks.slice(), errors: errors.slice(), note }) };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resultCardViewModel, resultCardMarkButtons, resultCardEscape, openResultCard, resultCardStartsCollapsed };
}
