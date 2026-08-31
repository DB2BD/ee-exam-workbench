// Versioned aliases shared by the textbook classifier and future import tools.
// Longer aliases are applied first to avoid partial replacements.
const TAXONOMY_VERSION = '2026.08.30';
const TAXONOMY_ALIASES = {
  'th[eéè]venin': '戴維寧',
  'thevenin': '戴維寧',
  'norton': '諾頓',
  's[- ]?domain': 's域',
  'laplace transform': '拉氏轉換',
  'laplace': '拉氏轉換',
  'fourier series': '傅立葉',
  'fourier': '傅立葉',
  'per[- ]?unit|p\\.u\\.': '標么',
  'power factor': '功率因數',
  'induction motor': '感應電動機',
  '外激式直流電動機|直流電動機': '直流電機',
  'transformer': '變壓器',
  'fortescue|sequence components': '對稱分量',
  'op[- ]?amp|operational amplifier': '運算放大器',
  'two[- ]?port': '雙埠',
  'three[- ]?phase': '三相',
  '金氧半場效電晶體|增強型\\s*n[-－]通道': 'MOSFET',
  '返馳式轉換器|返馳轉換器': 'Flyback',
};

// Manual corrections are intentionally empty in the base distribution. A
// generated override file can populate this map without changing classifier
// code, while preserving the immutable QID audit trail.
const TAXONOMY_OVERRIDES = {};
