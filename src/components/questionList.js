// src/components/questionList.js
/**
 * Question List Component.
 * Filters and renders question cards based on category, subject, year, diff, status, search, and quick filter.
 */

function getSubjectMeta(sid) {
  if (currentExamCategory === 'GK' && typeof NATIONAL_EXAMS_DATA !== 'undefined' && NATIONAL_EXAMS_DATA.subjects) {
    const s = NATIONAL_EXAMS_DATA.subjects.find(s => s.id === sid);
    if (s) return s;
  }
  if (typeof DB_DATA === 'undefined' || !DB_DATA.meta || !DB_DATA.meta.subjects) {
    return { name: '考科', icon: '⚡', color: '#4a7c8f' };
  }
  return DB_DATA.meta.subjects.find(s => s.id === sid) || { name: '未知', icon: '📝', color: '#798694' };
}

function renderQuestions() {
  const container = document.getElementById('questions-container');
  if (!container) return;

  const subFilter = document.getElementById('filter-subject').value;
  const yrFilter = document.getElementById('filter-year').value;
  const statusFilter = document.getElementById('filter-status').value;
  const diffFilter = document.getElementById('filter-diff').value;
  const searchText = document.getElementById('search-input').value.trim().toLowerCase();

  // Save filters
  localStorage.setItem('filter-subject', subFilter);
  localStorage.setItem('filter-year', yrFilter);
  localStorage.setItem('filter-status', statusFilter);
  localStorage.setItem('filter-diff', diffFilter);

  const activeQuestions = getActiveQuestionsList();

  const filtered = activeQuestions.filter(q => {
    const [qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, status, ftags, hasDed, cat, rel] = q;

    if (subFilter !== 'all' && sid !== subFilter) return false;
    if (yrFilter !== 'all' && String(yr) !== yrFilter) return false;
    if (diffFilter !== 'all' && String(diff) !== diffFilter) return false;

    const curStatus = progressState[qid] || 0;
    const isStarred = !!starredState[qid];

    if (statusFilter === 'starred' && !isStarred) return false;
    if (statusFilter !== 'all' && statusFilter !== 'starred' && String(curStatus) !== statusFilter) return false;

    // Quick filter pills
    if (activeQuickFilter === 'review' && curStatus !== 2) return false;
    if (activeQuickFilter === 'starred' && !isStarred) return false;
    if (activeQuickFilter === 'dedicated' && !hasDed) return false;
    if (activeQuickFilter === 'due') {
      const dueList = typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : [];
      if (!dueList.includes(qid)) return false;
    }
    if (activeQuickFilter === 'top10') {
      const topKeywords = ['戴維寧', '暫態', '三相', '差動', '微積分', '變壓器', '感應', '短路', '功角', '保護'];
      const matched = topKeywords.some(k => topic.includes(k) || (tags || []).some(t => t.includes(k)));
      if (!matched) return false;
    }

    if (searchText) {
      const tagStr = (tags || []).join(' ').toLowerCase();
      const ftagStr = (ftags || []).join(' ').toLowerCase();
      if (!qid.toLowerCase().includes(searchText) &&
          !topic.toLowerCase().includes(searchText) &&
          !tagStr.includes(searchText) &&
          !ftagStr.includes(searchText)) {
        return false;
      }
    }

    return true;
  });

  const countBadge = document.getElementById('filtered-count');
  if (countBadge) countBadge.innerText = `顯示 ${filtered.length} 題`;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 60px 20px; color: var(--muted); background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius);">
        <div style="font-size: 2.2rem; margin-bottom: 12px;">🔍</div>
        <h3 style="color: var(--ink); margin-bottom: 6px;">查無符合條件的試題</h3>
        <p style="font-size: 0.88rem;">請嘗試調整或重設篩選條件與搜尋關鍵字</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(q => {
    const [qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, status, ftags, hasDed] = q;
    const meta = getSubjectMeta(sid);
    const curStatus = progressState[qid] || 0;
    const isStarred = !!starredState[qid];

    const starIcons = '⭐'.repeat(Math.max(1, Math.min(5, diff || 3)));
    const statusLabels = ['⚪ 未開始', '🟢 已掌握', '🔴 需二刷'];

    const dueInfo = typeof getReviewBadgeInfo === 'function' ? getReviewBadgeInfo(qid) : { text: '', cssClass: 'due-none' };

    return `
      <div class="qcard" id="card-${qid}">
        <div class="qhead">
          <div class="qmeta">
            <span class="qid">${qid}</span>
            <span class="qtag" style="background: ${meta.color}15; color: ${meta.color}; border: 1px solid ${meta.color}30;">
              ${meta.icon} ${meta.name.split('（')[0]}
            </span>
            <span class="diff-badge" title="難度評定：${diff} 星">${starIcons}</span>
            ${(tags || []).slice(1, 3).map(t => `<span class="qtag">${t}</span>`).join('')}
          </div>
          <button class="btn-star ${isStarred ? 'active' : ''}" onclick="toggleStarred('${qid}', event)" title="${isStarred ? '取消收藏' : '加入重點收藏'}">
            ${isStarred ? '★' : '☆'}
          </button>
        </div>

        <div class="qtopic">${topic}</div>

        <div class="qfooter">
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button class="status-badge s-${curStatus}" onclick="toggleStatus('${qid}', event)" title="點擊切換做題掌握狀態">
              ${statusLabels[curStatus]}
            </button>
            ${dueInfo.text ? `<span class="due-badge ${dueInfo.cssClass}" title="SM-2 智能間隔重複排程">${dueInfo.text}</span>` : ''}
          </div>
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, false, true)" class="btn-sol" style="background: var(--warn); border-color: var(--warn); box-shadow: 0 2px 6px rgba(196, 124, 93, 0.25);" title="開啟白紙蓋牌主動回想抽測">
              🎴 蓋牌抽測
            </button>
            <button onclick="openSolutionModal(event, '${solLink}', '${qid}', ${qnum}, false, false)" class="btn-sol" title="直接檢視完整 KaTeX 推導詳解">
              📝 完整詳解
            </button>
            <a href="${pdfLink}" target="_blank" class="btn-pdf" title="在瀏覽器開啟考選部原題 PDF">
              📄 查看原題 PDF
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');
}
