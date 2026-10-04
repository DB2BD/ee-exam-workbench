// src/state/filterStore.js
/**
 * Filter State Management & Dropdown Controller
 */

let activeQuickFilter = 'all';

function setQuickFilter(type, btn) {
  activeQuickFilter = type;
  document.querySelectorAll('.pills-bar .pill').forEach(p => p.classList.remove('active'));
  if (btn) btn.classList.add('active');
  if (typeof renderQuestions === 'function') renderQuestions();
}

function updateFilterDropdownsForCategory() {
  const yrSelect = document.getElementById('filter-year');
  const subSelect = document.getElementById('filter-subject');

  const currentYr = yrSelect ? yrSelect.value : 'all';
  const currentSub = subSelect ? subSelect.value : 'all';

  if (currentExamCategory === 'GK') {
    if (yrSelect) {
      yrSelect.innerHTML = `
        <option value="all">所有年度 (110 ~ 114 年)</option>
        <option value="114">114 年 (最新)</option>
        <option value="113">113 年</option>
        <option value="112">112 年</option>
        <option value="111">111 年</option>
        <option value="110">110 年</option>
      `;
    }
    if (subSelect) {
      subSelect.innerHTML = `
        <option value="all">所有考科 (5 大考科)</option>
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04">⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
      `;
    }
  } else {
    if (yrSelect) {
      yrSelect.innerHTML = `
        <option value="all">所有年度 (104 ~ 114 年)</option>
        <option value="114">114 年 (最新)</option>
        <option value="113">113 年</option>
        <option value="112">112 年</option>
        <option value="111">111 年</option>
        <option value="110">110 年</option>
        <option value="109">109 年</option>
        <option value="108">108 年</option>
        <option value="107">107 年</option>
        <option value="106">106 年</option>
        <option value="105">105 年</option>
        <option value="104">104 年</option>
      `;
    }
    if (subSelect) {
      subSelect.innerHTML = `
        <option value="all">所有考科 (6 大考科)</option>
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04">⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
        <option value="06">🏭 06. 工業配電</option>
      `;
    }
  }

  // Restore previous values if valid in the new options
  if (yrSelect && Array.from(yrSelect.options).some(o => o.value === currentYr)) yrSelect.value = currentYr;
  if (subSelect && Array.from(subSelect.options).some(o => o.value === currentSub)) subSelect.value = currentSub;
}

// GK data (national-exams-data.js / national-solutions-bundle.js) is not preloaded.
// Any GK code path must go through ensureGkData() first.
let gkDataPromise = null;

function gkDataLoaded() {
  return typeof NATIONAL_EXAMS_DATA !== 'undefined';
}

function ensureGkData() {
  if (gkDataLoaded() && typeof NATIONAL_BUNDLED_MD !== 'undefined') return Promise.resolve(true);
  if (gkDataPromise) return gkDataPromise;
  if (typeof document === 'undefined') return Promise.resolve(false);
  const load = src => new Promise((resolve, reject) => {
    const el = document.createElement('script');
    el.src = src;
    el.onload = () => resolve();
    el.onerror = () => reject(new Error('load failed: ' + src));
    document.head.appendChild(el);
  });
  gkDataPromise = load('./national-exams-data.js')
    .then(() => load('./national-solutions-bundle.js'))
    .then(() => true)
    .catch(() => { gkDataPromise = null; return false; });
  return gkDataPromise;
}

function switchExamCategory(catId, silent) {
  if (catId === 'GK' && !gkDataLoaded() && typeof document !== 'undefined') {
    ensureGkData().then(ok => { if (ok) switchExamCategory('GK', silent); });
    return;
  }
  currentExamCategory = catId;
  if (typeof resetQuestionFacetState === 'function') resetQuestionFacetState();
  localStorage.setItem('exam_category_tab', catId);
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('on'));
  const targetTab = document.getElementById('cat-tab-' + catId);
  if (targetTab) targetTab.classList.add('on');

  updateFilterDropdownsForCategory();
  reloadProgressState();
  const categoryCount = typeof getQuestionCountForCategory === 'function'
    ? getQuestionCountForCategory(catId)
    : (catId === 'PE' ? 321 : 161);

  if (catId === 'PE') {
    if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
    if (typeof renderQuestions === 'function') renderQuestions();
    if (typeof renderReviewPage === 'function') renderReviewPage();
    if (!silent) showToast(`🏆 已切換至「電機工程技師」核心題庫 (${categoryCount} 題)`);
  } else {
    if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
    if (typeof renderQuestions === 'function') renderQuestions();
    if (typeof renderReviewPage === 'function') renderReviewPage();
    if (!silent) showToast(`🏛️ 已切換至「公務人員高考三級」參考題庫 (${categoryCount} 題)`);
  }
}
