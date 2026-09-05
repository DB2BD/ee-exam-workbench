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
  const examYrSelect = document.getElementById('exam-select-yr');
  const examSubSelect = document.getElementById('exam-select-subj');

  const currentYr = yrSelect ? yrSelect.value : 'all';
  const currentSub = subSelect ? subSelect.value : 'all';
  const currentExamYr = examYrSelect ? examYrSelect.value : '114';
  const currentExamSub = examSubSelect ? examSubSelect.value : '01';

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
    if (examYrSelect) {
      examYrSelect.innerHTML = `
        <option value="114">114 年全卷</option>
        <option value="113">113 年全卷</option>
        <option value="112">112 年全卷</option>
        <option value="111">111 年全卷</option>
        <option value="110">110 年全卷</option>
        <option value="random">🎲 隨機抽 4 題模考</option>
      `;
    }
    if (examSubSelect) {
      examSubSelect.innerHTML = `
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
    if (examYrSelect) {
      examYrSelect.innerHTML = `
        <option value="114">114 年全卷</option>
        <option value="113">113 年全卷</option>
        <option value="112">112 年全卷</option>
        <option value="111">111 年全卷</option>
        <option value="110">110 年全卷</option>
        <option value="109">109 年全卷</option>
        <option value="108">108 年全卷</option>
        <option value="107">107 年全卷</option>
        <option value="106">106 年全卷</option>
        <option value="105">105 年全卷</option>
        <option value="104">104 年全卷</option>
        <option value="random">🎲 隨機抽 4 題模考</option>
      `;
    }
    if (examSubSelect) {
      examSubSelect.innerHTML = `
        <option value="01">⚡ 01. 電路學</option>
        <option value="02">🔌 02. 電子學（含電力電子）</option>
        <option value="03">📐 03. 工程數學</option>
        <option value="04" selected>⚙️ 04. 電機機械</option>
        <option value="05">🏢 05. 電力系統</option>
        <option value="06">🏭 06. 工業配電</option>
      `;
    }
  }

  // Restore previous values if valid in the new options
  if (yrSelect && Array.from(yrSelect.options).some(o => o.value === currentYr)) yrSelect.value = currentYr;
  if (subSelect && Array.from(subSelect.options).some(o => o.value === currentSub)) subSelect.value = currentSub;
  if (examYrSelect && Array.from(examYrSelect.options).some(o => o.value === currentExamYr)) examYrSelect.value = currentExamYr;
  if (examSubSelect && Array.from(examSubSelect.options).some(o => o.value === currentExamSub)) examSubSelect.value = currentExamSub;
}

function switchExamCategory(catId) {
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
    showToast(`🏆 已切換至「電機工程技師」核心題庫 (${categoryCount} 題)`);
  } else {
    if (typeof updateStatsAndBar === 'function') updateStatsAndBar();
    if (typeof renderQuestions === 'function') renderQuestions();
    if (typeof renderReviewPage === 'function') renderReviewPage();
    showToast(`🏛️ 已切換至「公務人員高考三級」參考題庫 (${categoryCount} 題)`);
  }
}
