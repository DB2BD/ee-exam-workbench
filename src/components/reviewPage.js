// src/components/reviewPage.js
/** Review Center: shared progress pool with subject and taxonomy filters. */

let reviewFilter = 'due';
let reviewTypeFilter = 'all';

const REVIEW_CLASSIFIER_MIN_CONFIDENCE = 0.65;
const REVIEW_CLASSIFIER_MIN_MARGIN = 0.15;
const REVIEW_CLASSIFIER_MIN_SCORE = 3;
const MANUAL_TOPIC_LABELS_STORAGE_KEY = 'EE_MANUAL_TOPIC_LABELS_V1';

function getManualTopicSeed() {
  if (typeof MANUAL_TOPIC_LABEL_SEED === 'undefined') return {};
  return Object.fromEntries(Object.entries(MANUAL_TOPIC_LABEL_SEED).map(([qid, value]) => [qid, Object.assign({}, value)]));
}

function loadManualTopicLabels() {
  const seed = getManualTopicSeed();
  if (typeof localStorage === 'undefined') return seed;
  try {
    const raw = localStorage.getItem(MANUAL_TOPIC_LABELS_STORAGE_KEY);
    // Seed labels represent the user's latest explicit "全部採用建議"
    // confirmation.  Once a browser has saved anything, its local copy is
    // authoritative so a deliberate clear/edit remains persistent.
    return raw ? JSON.parse(raw) : seed;
  } catch (_) {
    return seed;
  }
}

let manualTopicLabels = loadManualTopicLabels();

function normalizeManualTopicValue(value) {
  const chapterId = typeof value === 'string' ? value : value && value.chapterId;
  if (typeof chapterId !== 'string' || !chapterId) return null;
  const normalized = { chapterId };
  if (value && typeof value === 'object') {
    if (typeof value.updatedAt === 'string' && value.updatedAt) normalized.updatedAt = value.updatedAt;
    if (typeof value.source === 'string' && value.source) normalized.source = value.source;
  }
  return normalized;
}

function saveManualTopicLabels() {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(MANUAL_TOPIC_LABELS_STORAGE_KEY, JSON.stringify(manualTopicLabels));
  } catch (e) {
    console.error('Failed to save manual topic labels', e);
  }
}

function getManualTopicLabel(qid) {
  const normalized = normalizeManualTopicValue(manualTopicLabels && manualTopicLabels[qid]);
  return normalized ? normalized.chapterId : '';
}

function getManualTopicLabels() {
  const labels = {};
  Object.entries(manualTopicLabels || {}).forEach(([qid, value]) => {
    const normalized = normalizeManualTopicValue(value);
    if (normalized) labels[qid] = normalized;
  });
  return labels;
}

function isValidManualTopicLabel(qid, chapterId) {
  if (!qid || !chapterId || typeof KNOWLEDGE_DAG === 'undefined') return false;
  const record = findQuestionRecord(qid);
  if (!record) return false;
  const subjectId = getReviewRecord(record).subjectId;
  const node = KNOWLEDGE_DAG[chapterId];
  return !!node && node.subject === subjectId;
}

function setManualTopicLabel(qid, chapterId) {
  if (!qid) return false;
  if (!chapterId) {
    delete manualTopicLabels[qid];
    saveManualTopicLabels();
    return true;
  }
  if (!isValidManualTopicLabel(qid, chapterId)) return false;
  manualTopicLabels[qid] = { chapterId, source: 'user', updatedAt: new Date().toISOString() };
  saveManualTopicLabels();
  return true;
}

function replaceManualTopicLabels(payload) {
  const next = {};
  if (payload && typeof payload === 'object') {
    Object.entries(payload).forEach(([qid, value]) => {
      const normalized = normalizeManualTopicValue(value);
      if (normalized && isValidManualTopicLabel(qid, normalized.chapterId)) {
        next[qid] = Object.assign({ updatedAt: new Date().toISOString() }, normalized);
      }
    });
  }
  manualTopicLabels = next;
  saveManualTopicLabels();
  if (typeof renderReviewPage === 'function') renderReviewPage();
  return getManualTopicLabels();
}

function reviewHtmlEscape(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function getReviewRecord(q) {
  if (typeof toQuestionRecord === 'function') return toQuestionRecord(q);
  return {
    id: q[0], subjectId: q[1], year: q[2], number: q[3], stem: q[4],
    tags: q[5], solutionLink: q[6], formulaTags: q[10],
  };
}

function isManualReviewQuestion(q) {
  const record = getReviewRecord(q);
  return !!record && record.solutionStatus === 'needs_manual_review';
}

function getReviewSubjectFilterValues(questions) {
  return [...new Set((questions || []).map(q => getReviewRecord(q).subjectId).filter(Boolean))].sort();
}

function getReviewChapterFilterValues(questions, subjectId) {
  const selected = subjectId || 'all';
  return [...new Set((questions || [])
    .filter(q => selected === 'all' || getReviewRecord(q).subjectId === selected)
    .map(getReviewTypeLabel))]
    .sort((a, b) => a.localeCompare(b, 'zh-Hant'));
}

function setReviewFilter(filter) {
  reviewFilter = ['due', 'wrong', 'starred', 'manual', 'all'].includes(filter) ? filter : 'due';
  const scope = document.getElementById('review-scope');
  if (scope) scope.value = reviewFilter;
  renderReviewPage();
}

function setReviewTypeFilter(type) {
  reviewTypeFilter = type || 'all';
  renderReviewPage();
}

function setReviewSubjectFilter(subject) {
  // A chapter belongs to one textbook/subject. Never carry a chapter
  // selection across subjects where it does not exist.
  reviewTypeFilter = 'all';
  const select = document.getElementById('review-subject');
  if (select && select.value !== subject) select.value = subject;
  renderReviewPage();
}

/*
 * Textbook taxonomy.  IDs and names intentionally mirror KNOWLEDGE_DAG so
 * review groups and the prerequisite graph use one canonical chapter name.
 * A tag hit is weighted above a generic prose hit; rules are scoped by
 * subject, preventing terms such as「功率」or「變壓器」from crossing subjects.
 */
const REVIEW_CHAPTER_RULES = {
  '01': [
    ['ct-thevenin-norton', ['戴維寧', '諾頓', '等效定理', '等效電阻']],
    ['ct-max-power', ['最大功率', '最大平均功率']],
    ['ct-laplace-circuit', ['拉普拉斯', '拉氏', 'laplace', 's域']],
    ['ct-second-order-rlc', ['二階', '欠阻尼', '過阻尼', '臨界阻尼', 'rlc']],
    ['ct-first-order-rc-rl', ['暫態', '開關', '單位步階', '一階', '時間常數', '初始能量', '狀態方程']],
    ['ct-mutual-inductance', ['互感', '耦合電路', '耦合電感', '同名端']],
    ['ct-two-port', ['雙埠', '二埠', 'z-參數', 'y-參數', 'h 參數', '傳輸參數']],
    ['ct-three-phase', ['三相', 'y-δ', 'y-y', 'delta', '線電壓']],
    ['ct-superposition', ['重疊定理', '疊加定理', '對偶網路']],
    ['ct-complex-power', ['複數功率', '功率因數', '無效功率', '視在功率']],
    ['ct-phasor-ac', ['相量', '交流穩態', '弦波穩態', '阻抗', '頻率']],
    ['ct-node-mesh', ['節點電壓', '節點分析', '網目電流', '網目分析']],
    ['ct-divider-equiv', ['分壓', '分流', '電阻組合', '電阻等效', 'δ 至 y']],
    ['ct-ohm-kcl-kvl', ['歐姆', 'kcl', 'kvl', '基本電路']]
  ],
  '02': [
    ['el-pe-inverter-spwm', ['全橋變流器', '全橋轉換器', '全橋式變頻器', '方波變頻器', '逆變器', 'spwm', '脈寬調變']],
    ['el-pe-thyristor-rectifier', ['閘流體', 'thyristor', '相控整流', '半波整流', '續流二極體']],
    ['el-pe-buck-boost', ['buck', 'boost', 'flyback', '返馳', '降壓', '升壓', '降升壓', '電源轉換器', '責任週期', '理想開關', 'pwm', '連續導通']],
    ['el-feedback-stability', ['負回授', '回授因素', '相位邊限', '穩定度']],
    ['el-active-filter', ['主動濾波器', '濾波器', '頻率響應', '米勒', '增益函數', '高頻', '極點', '3 db']],
    ['el-diff-amp', ['差動放大器', '差動對', '共模', 'cmrr']],
    ['el-opamp-ideal', ['運算放大器', 'opa', '反相', '非反相', '虛短']],
    ['el-mosfet-bias-small-signal', ['mosfet', 'mos', '場效電晶體', 'vth', 'ids']],
    ['el-bjt-bias-small-signal', ['bjt', '電晶體', '電晶體小訊號', 'β', '偏壓']],
    ['el-zener-regulator', ['齊納', '穩壓二極體', 'zener']],
    ['el-diode-rectifier', ['二極體', '二極管', '整流', 'piv']]
  ],
  '03': [
    ['em-complex-cauchy-residue', ['留數', '複變', '複數平面', '柯西', 'residue', '解析函數', '複數積分']],
    ['em-pde-separation', ['偏微分方程', '分離變數', '熱傳導', '波動方程']],
    ['em-svd-linear-systems', ['奇異值', 'svd', '零空間', '偽逆']],
    ['em-probability-statistics', ['機率', '統計', '隨機變數', '常態分布', '期望值']],
    ['em-vector-analysis', ['向量分析', '向量微積分', '梯度', '散度', '旋度', '曲率', '切線向量', '位置向量', '線積分']],
    ['em-eigen-diagonal', ['特徵值', '特徵向量', '對角化']],
    ['em-matrix-det-inv', ['矩陣', '行列式', '反矩陣', '克拉瑪', '線性轉換', '最小平方', 'least squares']],
    ['em-fourier-series', ['傅立葉', '傅氏', '級數', '週期函數']],
    ['em-laplace-transform', ['拉氏轉換', '拉普拉斯轉換', '反轉換', '部分分式']],
    ['em-second-order-ode-nonhomogeneous', ['非齊次', '參數變更法', '未定係數', '降階法', '特解']],
    ['em-second-order-ode-homogeneous', ['二階常係數', '齊次微分方程', '重根', "y''", '初始值問題']],
    ['em-first-order-ode', ['一階微分方程', '常微分方程', '可分離', '積分因子', '伯努利', 'bernoulli', '通解']]
  ],
  '04': [
    ['emach-synchronous-salient-pole', ['凸極', '雙反應', 'xq', 'xd']],
    ['emach-synchronous-generator-round', ['同步發電機', '同步機', '功角', '激磁', '定子繞組', '同步速度']],
    ['emach-induction-motor-torque', ['最大轉矩', '轉矩', '轉差率']],
    ['emach-induction-motor-equiv', ['感應電動機', '感應馬達', '等效電路']],
    ['emach-three-phase-transformer', ['三相變壓器', 'y-δ', 'δ-δ', 'v-v']],
    ['emach-autotransformer', ['自耦變壓器', '自耦']],
    ['emach-single-phase-transformer', ['單相變壓器', '開路試驗', '短路試驗', '電壓調整率']],
    ['emach-dc-motor-generator', ['直流電機', '直流馬達', '直流發電機']],
    ['emach-magnetic-circuits', ['磁路', '磁滯', '飽和', '磁通', '電磁鐵', '環形電感', '氣隙', '磁化曲線', '電磁系統']]
  ],
  '05': [
    ['ps-state-estimation-wls', ['狀態估計', 'wls', '壞資料']],
    ['ps-economic-dispatch', ['經濟調度', '發電協調', '燃料成本', '最佳發電量']],
    ['ps-load-flow-admittance', ['電力潮流', '導納矩陣', '牛頓拉福森', '高斯賽德', '潮流計算', '匯流排', 'pv bus', 'pq bus', 'swing bus']],
    ['ps-power-analysis', ['實功率', '虛功率', '複數功率', '功率因數', '負載阻抗']],
    ['ps-system-protection-relay', ['距離電驛', '保護電驛', '保護協調', 'zone 1', 'zone 2']],
    ['ps-unsymmetrical-faults', ['不對稱故障', '單相接地', '線間短路', '2lg', 'slg']],
    ['ps-transient-stability-equal-area', ['暫態穩定', '等面積', '搖擺方程', '臨界清除', '失去同步', '轉子加速度', '加速度', '同步速度', '負載突然移除', '突然被移除', '功角曲線']],
    ['ps-symmetrical-components', ['對稱分量', '正序', '負序', '零序']],
    ['ps-three-phase-fault', ['三相短路', '短路容量', '故障電流']],
    ['ps-transmission-line-models', ['輸電線模型', '長程線', '短程線', 'abcd', '費蘭梯', '串聯補償', '最大傳送實功率']],
    ['ps-transmission-line-params', ['輸電線', 'gmd', 'gmr', '導線幾何', '電感電容']],
    ['ps-per-unit', ['標么', 'pu', '基準容量', '基準電壓']]
  ],
  '06': [
    ['dist-arc-flash-ieee80', ['跨步電壓', '接觸電壓', '接地網', 'ieee 80', '弧閃']],
    ['dist-grounding-system', ['系統接地', '設備接地', '接地系統', '接地方式', '接地電阻']],
    ['dist-lighting-design', ['照明設計', '照度', '照明率', '燈具配置', 'lux']],
    ['dist-distribution-equipment', ['配電設備', '變壓器組接線', '開三角', 'v-v 接線', '受電方式', '責任分界點', '高壓供電', '複線圖']],
    ['dist-motor-installation', ['電動機配線', '馬達配線', '全壓啟動', 'y-δ 啟動', '啟動電流', 'hp']],
    ['dist-harmonics-mitigation', ['諧波', '諧波共振', 'thd', '濾波器', '電壓閃爍', '閃爍電壓', '閃爍電壓變動率', '電力品質']],
    ['dist-protection-coordination', ['過電流電驛', '過電流保護電驛', '保護協調', '反時限', 'tcc', '比流器', '動作特性曲線', 'time dial', '電流分接頭', 'co-7']],
    ['dist-short-circuit-capacity', ['短路容量', '短路電流', 'mva 法', '故障點']],
    ['dist-power-factor-correction', ['功率因數改善', '功因改善', '並聯電容', '無效功率補償', 'kvar']],
    ['dist-voltage-drop', ['電壓降', '電壓突降', '百分壓降', '導線選用', '線路損失', '線到線']],
    ['dist-load-characteristics', ['需量因數', '參差因數', '負載因數', '最高需量', '契約容量', '裝置容量', '時間電價', '日負載曲線']]
  ]
};

// Public integrity seam: the classifier's rule IDs must remain resolvable in
// the canonical knowledge DAG (the DAG owns the display chapter names).
function getReviewChapterRuleIds(subjectId) {
  return (REVIEW_CHAPTER_RULES[subjectId] || []).map(([id]) => id);
}

function getReviewChapterKey(q, options = {}) {
  const record = getReviewRecord(q);
  const sid = record.subjectId;
  const normalize = value => {
    let normalized = String(value || '').toLowerCase();
    if (typeof TAXONOMY_ALIASES !== 'undefined') {
      Object.entries(TAXONOMY_ALIASES)
        .sort((a, b) => b[0].length - a[0].length)
        .forEach(([alias, canonical]) => { normalized = normalized.replace(new RegExp(alias, 'gi'), canonical); });
    }
    return normalized;
  };
  // A learner's explicit chapter label is the strongest signal.  It is kept
  // in localStorage and intentionally applied before automatic keyword rules;
  // passing ``ignoreManualLabel`` lets the annotation dialog show the raw
  // classifier suggestion beside the human decision.
  const manualLabel = !options.ignoreManualLabel && typeof getManualTopicLabel === 'function'
    ? getManualTopicLabel(record.id)
    : '';
  if (manualLabel && typeof KNOWLEDGE_DAG !== 'undefined'
      && KNOWLEDGE_DAG[manualLabel] && KNOWLEDGE_DAG[manualLabel].subject === sid) {
    return manualLabel;
  }
  const override = typeof TAXONOMY_OVERRIDES !== 'undefined' ? TAXONOMY_OVERRIDES[record.id] : null;
  if (override && override.primaryChapter && typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG[override.primaryChapter]) return override.primaryChapter;
  const topic = normalize(record.stem);
  const tags = Array.isArray(record.tags) ? record.tags.map(normalize) : [];
  const formulaTags = Array.isArray(record.formulaTags) ? record.formulaTags.map(normalize) : [];
  const text = `${topic} ${tags.join(' ')} ${formulaTags.join(' ')}`;
  // OCR can leave a generic「電晶體」token in converter questions.  Prefer
  // the explicit converter/device marker before generic BJT rules so a
  // Flyback or MOSFET item never falls into a neighbouring chapter.
  if (sid === '02' && /flyback|返馳/.test(text)) return 'el-pe-buck-boost';
  if (sid === '02' && /mosfet|金氧半場效/.test(text)) return 'el-mosfet-bias-small-signal';
  const rules = REVIEW_CHAPTER_RULES[sid] || [];
  const matches = [];
  rules.forEach(([id, terms], order) => {
    let score = 0;
    terms.forEach(term => {
      const needle = term.toLowerCase();
      if (topic.includes(needle)) score += needle.length >= 4 ? 4 : 3;
      if (tags.some(tag => tag.includes(needle))) score += 1;
      if (formulaTags.some(tag => tag.includes(needle))) score += 2;
    });
    // Keep rule order as a deterministic tie-breaker for overlapping terms,
    // but never turn a no-hit into a false positive.
    if (score > 0) matches.push({ id, score, order });
  });
  matches.sort((a, b) => b.score - a.score || a.order - b.order);
  const best = matches[0];
  const second = matches[1];
  if (!best || best.score < REVIEW_CLASSIFIER_MIN_SCORE) return null;
  const denominator = best.score + (second ? second.score : 0);
  const confidence = denominator ? best.score / denominator : 0;
  const margin = confidence - (second ? second.score / denominator : 0);
  if (confidence < REVIEW_CLASSIFIER_MIN_CONFIDENCE || margin < REVIEW_CLASSIFIER_MIN_MARGIN) return null;
  return best.id;
}

function getReviewTypeLabel(q) {
  const key = getReviewChapterKey(q);
  if (key && typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG[key]) return KNOWLEDGE_DAG[key].name;
  return '待人工複核';
}

function getReviewQuestions() {
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const due = new Set(typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : []);
  const subject = document.getElementById('review-subject');
  const subjectFilter = subject ? subject.value : 'all';
  return questions.filter(q => {
    const qid = getReviewRecord(q).id;
    const status = typeof progressState !== 'undefined' ? (progressState[qid] || 0) : 0;
    const starred = typeof starredState !== 'undefined' && !!starredState[qid];
    const inScope = reviewFilter === 'due' ? due.has(qid) : reviewFilter === 'wrong' ? status === 2 : reviewFilter === 'starred' ? starred : reviewFilter === 'manual' ? isManualReviewQuestion(q) : true;
    return inScope && (subjectFilter === 'all' || getReviewRecord(q).subjectId === subjectFilter) && (reviewTypeFilter === 'all' || getReviewTypeLabel(q) === reviewTypeFilter);
  });
}

// ---------------------------------------------------------------------------
// Manual topic annotation queue
// ---------------------------------------------------------------------------

let manualLabelQueue = [];
let manualLabelIndex = 0;

function getManualReviewQuestions() {
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const subjectSelect = typeof document !== 'undefined' ? document.getElementById('review-subject') : null;
  const subjectFilter = subjectSelect && subjectSelect.value ? subjectSelect.value : 'all';
  return questions.filter(q => {
    if (!isManualReviewQuestion(q)) return false;
    return subjectFilter === 'all' || getReviewRecord(q).subjectId === subjectFilter;
  });
}

function getManualLabelOptions(subjectId) {
  const rules = REVIEW_CHAPTER_RULES[subjectId] || [];
  return rules
    .map(([id]) => {
      const node = typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG[id] : null;
      return node ? { id, name: node.name } : null;
    })
    .filter(Boolean);
}

function getManualLabelDisplayName(chapterId) {
  if (!chapterId) return '尚未標注';
  if (typeof KNOWLEDGE_DAG !== 'undefined' && KNOWLEDGE_DAG[chapterId]) return KNOWLEDGE_DAG[chapterId].name;
  return chapterId;
}

function getManualQuestionCrop(q, qid) {
  const isGK = Boolean(qid && qid.startsWith('GK-'));
  const crop = isGK ? q[14] : (typeof QUESTION_CROP_MAP !== 'undefined' ? QUESTION_CROP_MAP[qid] : '');
  if (!crop) return '';
  return typeof resolveImageMapUrl === 'function' ? resolveImageMapUrl(crop, isGK, qid) : crop;
}

function openManualLabelModal(startQid) {
  manualLabelQueue = getManualReviewQuestions();
  if (!manualLabelQueue.length) {
    showToast('目前沒有待人工覆核題目');
    return;
  }
  const requestedIndex = manualLabelQueue.findIndex(q => getReviewRecord(q).id === startQid);
  manualLabelIndex = requestedIndex >= 0 ? requestedIndex : 0;
  const modal = document.getElementById('manual-label-modal');
  if (!modal) return;
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
  renderManualLabelModal();
}

function closeManualLabelModal() {
  const modal = document.getElementById('manual-label-modal');
  if (modal) modal.classList.remove('show');
  document.body.style.overflow = '';
  if (typeof renderReviewPage === 'function') renderReviewPage();
}

function getCurrentManualLabelQuestion() {
  return manualLabelQueue[manualLabelIndex] || null;
}

function renderManualLabelModal() {
  const body = document.getElementById('manual-label-body');
  const progress = document.getElementById('manual-label-progress');
  const prev = document.getElementById('manual-label-prev');
  const next = document.getElementById('manual-label-next');
  if (!body) return;
  const q = getCurrentManualLabelQuestion();
  if (!q) {
    body.innerHTML = '<div class="manual-label-empty">目前沒有待人工覆核題目。</div>';
    if (progress) progress.innerText = '0 / 0';
    return;
  }
  const record = getReviewRecord(q);
  const qid = record.id;
  const autoKey = getReviewChapterKey(q, { ignoreManualLabel: true });
  const autoName = getManualLabelDisplayName(autoKey);
  const selected = getManualTopicLabel(qid);
  const options = getManualLabelOptions(record.subjectId);
  const cropSrc = getManualQuestionCrop(q, qid);
  const meta = typeof getSolutionReviewMetadata === 'function' ? getSolutionReviewMetadata(qid) : null;
  const sourceUrl = record.sourceLink && /^https:\/\//i.test(record.sourceLink) ? record.sourceLink : '';
  const solutionLink = record.solutionLink || '';
  const selectOptions = [`<option value="">尚未標注（保留自動候選）</option>`]
    .concat(options.map(option => `<option value="${reviewHtmlEscape(option.id)}" ${option.id === selected ? 'selected' : ''}>${reviewHtmlEscape(option.name)}</option>`));
  if (progress) progress.innerText = `${manualLabelIndex + 1} / ${manualLabelQueue.length}`;
  if (prev) prev.disabled = manualLabelIndex <= 0;
  if (next) next.disabled = manualLabelIndex >= manualLabelQueue.length - 1;
  body.innerHTML = `
    <div class="manual-label-question-head">
      <div>
        <div class="manual-label-qid">${reviewHtmlEscape(qid)}</div>
        <div class="manual-label-subject">${reviewHtmlEscape(getSubjectMeta(record.subjectId).name)} · ${record.year} 年第 ${record.number} 題</div>
      </div>
      <span class="qtag solution-audit s-audit-needs_manual_review">🟡 待人工覆核</span>
    </div>
    <div class="manual-label-grid">
      <section class="manual-label-question-pane">
        <h4>題目裁切圖</h4>
        ${cropSrc
          ? `<img class="manual-label-crop" src="${reviewHtmlEscape(cropSrc)}" alt="${reviewHtmlEscape(qid)} 本題裁切圖" loading="eager" />`
          : `<div class="manual-label-no-crop">尚未建立本題裁切圖</div>`}
        <div class="manual-label-stem">${renderQuestionTopic(record.stem)}</div>
        ${sourceUrl ? `<a class="btn-pdf manual-label-source" href="${reviewHtmlEscape(sourceUrl)}" target="_blank" rel="noopener noreferrer">開啟官方原卷</a>` : ''}
      </section>
      <section class="manual-label-decision-pane">
        <h4>題型標注</h4>
        <label for="manual-label-select">請選擇本題最符合的教科書章節</label>
        <select id="manual-label-select" class="manual-label-select">${selectOptions.join('')}</select>
        <div class="manual-label-auto"><strong>自動候選：</strong>${reviewHtmlEscape(autoName)}</div>
        ${selected ? `<div class="manual-label-saved">✅ 已保存：${reviewHtmlEscape(getManualLabelDisplayName(selected))}</div>` : '<div class="manual-label-saved">尚未保存人工標注</div>'}
        ${meta && meta.blocker ? `<div class="manual-label-blocker"><strong>覆核阻擋：</strong>${reviewHtmlEscape(meta.blocker)}<br>${reviewHtmlEscape(meta.action || '')}</div>` : ''}
        ${solutionLink ? `<button type="button" class="btn-sol manual-label-solution" data-manual-open-solution="${reviewHtmlEscape(qid)}">📝 開啟本題詳解</button>` : ''}
      </section>
    </div>
  `;
  const solutionButton = body.querySelector('[data-manual-open-solution]');
  if (solutionButton) solutionButton.addEventListener('click', () => {
    if (typeof openSolutionModal === 'function') openSolutionModal(null, solutionLink, qid, record.number, false, false);
  });
}

function saveCurrentManualLabel(showMessage = true) {
  const q = getCurrentManualLabelQuestion();
  const select = document.getElementById('manual-label-select');
  if (!q || !select) return false;
  const qid = getReviewRecord(q).id;
  const ok = setManualTopicLabel(qid, select.value);
  if (!ok) {
    showToast('標注無效：請選擇本考科的教科書章節');
    return false;
  }
  if (showMessage) showToast(select.value ? '✅ 題型標注已保存' : '已清除本題人工標注');
  return true;
}

function saveManualLabel() {
  saveCurrentManualLabel(true);
  renderManualLabelModal();
}

function moveManualLabel(delta, saveFirst = false) {
  if (saveFirst && !saveCurrentManualLabel(true)) return;
  const nextIndex = manualLabelIndex + delta;
  if (nextIndex < 0 || nextIndex >= manualLabelQueue.length) return;
  manualLabelIndex = nextIndex;
  renderManualLabelModal();
}

function saveManualLabelAndNext() {
  if (!saveCurrentManualLabel(true)) return;
  moveManualLabel(1, false);
}

function populateReviewSubjects() {
  const select = document.getElementById('review-subject');
  if (!select) return;
  const current = select.value || 'all';
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const ids = getReviewSubjectFilterValues(questions);
  select.innerHTML = '<option value="all">所有考科</option>' + ids.map(sid => {
    const meta = getSubjectMeta(sid);
    return `<option value="${reviewHtmlEscape(sid)}">${meta.icon || ''} ${reviewHtmlEscape(meta.name)}</option>`;
  }).join('');
  select.value = ids.includes(current) ? current : 'all';
}

function renderReviewPage() {
  const container = document.getElementById('review-container');
  if (!container) return;
  populateReviewSubjects();
  const questions = typeof getActiveQuestionsList === 'function' ? getActiveQuestionsList() : [];
  const subject = document.getElementById('review-subject');
  const subjectFilter = subject ? subject.value : 'all';
  const subjectQuestions = questions.filter(q => subjectFilter === 'all' || getReviewRecord(q).subjectId === subjectFilter);
  const due = new Set(typeof getDueQuestionsList === 'function' ? getDueQuestionsList() : []);
  const wrong = subjectQuestions.filter(q => typeof progressState !== 'undefined' && (progressState[getReviewRecord(q).id] || 0) === 2).length;
  const starred = subjectQuestions.filter(q => typeof starredState !== 'undefined' && starredState[getReviewRecord(q).id]).length;
  const manual = subjectQuestions.filter(isManualReviewQuestion).length;
  const manualLabeled = subjectQuestions.filter(q => isManualReviewQuestion(q) && getManualTopicLabel(getReviewRecord(q).id)).length;
  const stats = document.getElementById('review-stats');
  if (stats) stats.innerHTML = [['今日到期', subjectQuestions.filter(q => due.has(getReviewRecord(q).id)).length], ['錯題本', wrong], ['收藏', starred], ['待人工', manual], ['目前題庫', subjectQuestions.length]].map(item => `<div class="review-stat"><span class="label">${item[0]}</span><span class="value">${item[1]}</span></div>`).join('');
  const manualButton = document.getElementById('manual-label-open');
  if (manualButton) {
    manualButton.disabled = manual === 0;
    manualButton.innerText = manual === 0
      ? '🧭 暫無人工標注題'
      : `🧭 逐題標注題型 (${manualLabeled}/${manual})`;
    manualButton.title = manual === 0 ? '目前考科沒有待人工覆核題' : '逐題檢視裁切圖並標注教科書章節';
  }

  // Only chapters that actually occur in the selected subject are offered.
  // This also removes empty/unmatched textbook chapters from the dropdown.
  const allTypes = getReviewChapterFilterValues(subjectQuestions, 'all');
  if (reviewTypeFilter !== 'all' && !allTypes.includes(reviewTypeFilter)) reviewTypeFilter = 'all';
  const typeFilter = document.getElementById('review-type-filter');
  if (typeFilter) {
    const scopeQuestions = subjectQuestions.filter(q => {
      const qid = getReviewRecord(q).id;
      const status = typeof progressState !== 'undefined' ? (progressState[qid] || 0) : 0;
      const starred = typeof starredState !== 'undefined' && !!starredState[qid];
      return reviewFilter === 'due' ? due.has(qid) : reviewFilter === 'wrong' ? status === 2 : reviewFilter === 'starred' ? starred : reviewFilter === 'manual' ? isManualReviewQuestion(q) : true;
    });
    const counts = scopeQuestions.reduce((map, q) => { const type = getReviewTypeLabel(q); map[type] = (map[type] || 0) + 1; return map; }, {});
    const buttons = [['all', '全部章節', scopeQuestions.length]].concat(allTypes.map(type => [type, type, counts[type] || 0]));
    typeFilter.innerHTML = buttons.map(([value, label, count]) => `<button type="button" class="pill ${reviewTypeFilter === value ? 'active' : ''}" data-review-type-filter="${reviewHtmlEscape(value)}">${reviewHtmlEscape(label)} (${count})</button>`).join('');
    typeFilter.querySelectorAll('[data-review-type-filter]').forEach(button => button.addEventListener('click', () => setReviewTypeFilter(button.dataset.reviewTypeFilter)));
  }

  const filtered = getReviewQuestions();
  const count = document.getElementById('review-filter-count');
  if (count) count.innerText = `目前 ${filtered.length} 題`;
  if (!filtered.length) {
    const title = reviewFilter === 'due' ? '今天沒有到期複習題' : reviewFilter === 'manual' ? '目前沒有待人工覆核題' : '目前沒有符合條件的題目';
    container.innerHTML = `<div class="review-empty"><strong>${title}</strong><span>可切換複習範圍或教科書章節，完成題目後再回來集中複習。</span></div>`;
    return;
  }

  const groups = {};
  filtered.forEach(q => { const type = getReviewTypeLabel(q); (groups[type] ||= []).push(q); });
  container.innerHTML = `<div class="review-type-grid">${Object.entries(groups).map(([type, list]) => `<section class="review-type-section" data-review-type="${reviewHtmlEscape(type)}"><div class="review-type-title"><span>📚 ${reviewHtmlEscape(type)}</span><span>${list.length} 題</span></div><div class="review-card-grid">${list.map(q => {
    const record = getReviewRecord(q);
    const { id: qid, subjectId: sid, year, number: qnum, stem: topic, solutionLink: solLink } = record;
    const meta = getSubjectMeta(sid);
    const status = typeof progressState !== 'undefined' ? (progressState[qid] || 0) : 0;
    const recall = typeof getRecallState === 'function' ? getRecallState(qid) : { level: 1 };
    const statusText = status === 2 ? '錯題' : status === 1 ? '已掌握' : '未開始';
    const dueText = due.has(qid) ? '<span class="due-badge due-today">今日到期</span>' : '';
    const auditText = isManualReviewQuestion(q) ? '<span class="qtag solution-audit s-audit-needs_manual_review">🟡 待人工</span>' : '';
    const manualLabel = getManualTopicLabel(qid);
    const manualLabelText = manualLabel ? `<span class="qtag manual-label-chip">✅ ${reviewHtmlEscape(getManualLabelDisplayName(manualLabel))}</span>` : '';
    const manualLabelButton = isManualReviewQuestion(q) ? `<button class="btn-sol" type="button" data-review-label="${reviewHtmlEscape(qid)}">🧭 標注題型</button>` : '';
    return `<article class="review-card" data-review-type="${reviewHtmlEscape(type)}"><div class="review-card-meta"><span class="qid">${reviewHtmlEscape(qid)}</span><span class="qtag">${year} 年 · 第 ${qnum} 題</span><span class="qtag">${meta.icon || ''} ${reviewHtmlEscape(meta.name)}</span><span class="qtag">${statusText}</span><span class="qtag">提取 L${recall.level}</span>${auditText}${manualLabelText}${dueText}</div><div class="review-card-topic">${renderQuestionTopic(topic)}</div><div class="review-card-actions"><button class="btn-sol" type="button" data-review-recall="${reviewHtmlEscape(qid)}">🎴 開始提取訓練</button><button class="btn-sol" type="button" data-review-open="${reviewHtmlEscape(qid)}">📝 開啟標準解題</button>${manualLabelButton}<button class="btn-sol" type="button" data-review-status="${reviewHtmlEscape(qid)}">循環狀態</button></div></article>`;
  }).join('')}</div></section>`).join('')}</div>`;
  container.querySelectorAll('[data-review-open]').forEach(button => button.addEventListener('click', () => {
    const q = filtered.find(item => getReviewRecord(item).id === button.dataset.reviewOpen);
    if (q && typeof openSolutionModal === 'function') {
      const record = getReviewRecord(q);
      openSolutionModal(null, record.solutionLink, record.id, record.number, false, false);
    }
  }));
  container.querySelectorAll('[data-review-recall]').forEach(button => button.addEventListener('click', () => {
    const q = filtered.find(item => getReviewRecord(item).id === button.dataset.reviewRecall);
    if (q && typeof openSolutionModal === 'function') {
      const record = getReviewRecord(q);
      openSolutionModal(null, record.solutionLink, record.id, record.number, false, true);
    }
  }));
  container.querySelectorAll('[data-review-status]').forEach(button => button.addEventListener('click', () => {
    if (typeof toggleStatus === 'function') toggleStatus(button.dataset.reviewStatus);
  }));
  container.querySelectorAll('[data-review-label]').forEach(button => button.addEventListener('click', () => {
    openManualLabelModal(button.dataset.reviewLabel);
  }));
}

function startReviewSession() {
  setReviewFilter('due');
  const first = getReviewQuestions()[0];
  if (first && typeof openSolutionModal === 'function') {
    const record = getReviewRecord(first);
    openSolutionModal(null, record.solutionLink, record.id, record.number, false, true);
  }
}
