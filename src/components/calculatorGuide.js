// src/components/calculatorGuide.js
/**
 * Casio fx-82SOLAR II Exam Calculator Keystroke Guide & Phasor Converter
 * ======================================================================
 * Designed specifically for Taiwan National Electrical Engineering Examinations
 * (where only non-programmable, memory-less calculators are approved).
 *
 * Provides:
 * 1. Step-by-step keystroke sequences for R<->P, Parallel Impedances, 3-Phase sqrt(3)
 * 2. DEG vs RAD trap warnings (Transmission lines & Wave equations)
 * 3. In-browser Phasor / Complex number quick verification tool
 */

const FX82_RECIPES = [
  {
    id: 'r_to_p',
    title: '直角座標轉極座標 (R ➔ P)',
    formula: 'A + jB \\implies R\\angle \\theta^\\circ',
    example: '3 + j4 \\implies 5\\angle 53.13^\\circ',
    keystrokes: [
      { key: '3', desc: '輸入實部 A' },
      { key: 'INV', desc: '功能切換鍵' },
      { key: 'R➔P', desc: '按 [+] 鍵上方黃色字 (R➔P)' },
      { key: '4', desc: '輸入虛部 B' },
      { key: '=', desc: '顯示大小 R (得 5)' },
      { key: 'b', desc: '按 [b] 鍵 (或 a b/c) 顯示角度 θ (得 53.13°)' }
    ],
    trap: '若虛部為負（如 3 - j4），輸入 4 之後需按 [+/-] 變號，再按 [=]。'
  },
  {
    id: 'p_to_r',
    title: '極座標轉直角座標 (P ➔ R)',
    formula: 'R\\angle \\theta^\\circ \\implies A + jB',
    example: '100\\angle 30^\\circ \\implies 86.60 + j50.00',
    keystrokes: [
      { key: '100', desc: '輸入大小 R' },
      { key: 'INV', desc: '功能切換鍵' },
      { key: 'P➔R', desc: '按 [-] 鍵上方黃色字 (P➔R)' },
      { key: '30', desc: '輸入角度 θ' },
      { key: '=', desc: '顯示實部 A (得 86.60)' },
      { key: 'b', desc: '按 [b] 鍵顯示虛部 B (得 50.00)' }
    ],
    trap: '請確認螢幕頂端顯示 [D] (Degree 角度制)。若顯示 [R] 或 [G] 算出來數值全錯！'
  },
  {
    id: 'parallel_z',
    title: '並聯阻抗倒數鏈算法',
    formula: 'Z_{eq} = \\frac{1}{\\frac{1}{Z_1} + \\frac{1}{Z_2}}',
    example: '20\\ \\Omega \\parallel 30\\ \\Omega = 12\\ \\Omega',
    keystrokes: [
      { key: '20', desc: '輸入 Z1' },
      { key: '1/x', desc: '取倒數 (得 0.05)' },
      { key: '+', desc: '加' },
      { key: '30', desc: '輸入 Z2' },
      { key: '1/x', desc: '取倒數 (得 0.0333)' },
      { key: '=', desc: '求和 (得 0.0833)' },
      { key: '1/x', desc: '再取倒數 (得 12 Ω)' }
    ],
    trap: '複數阻抗並聯時，建議先用 R➔P 轉極座標計算，或分步先算分母。'
  },
  {
    id: 'three_phase_p',
    title: '三相功率根號三常數鏈',
    formula: 'P = \\sqrt{3} V_L I_L \\cos\\theta',
    example: 'V_L=380\\text{V}, I_L=15\\text{A}, \\text{pf}=0.85 \\implies 8391.8\\text{ W}',
    keystrokes: [
      { key: '3', desc: '輸入 3' },
      { key: '√', desc: '開根號 (得 1.73205)' },
      { key: '×', desc: '乘' },
      { key: '380', desc: '線電壓 VL' },
      { key: '×', desc: '乘' },
      { key: '15', desc: '線電流 IL' },
      { key: '×', desc: '乘' },
      { key: '0.85', desc: '功率因數 pf' },
      { key: '=', desc: '得 8391.8 W (8.39 kW)' }
    ],
    trap: '題目若給相電壓 V_p，公式為 3 V_p I_p，切勿再乘根號三！'
  }
];

/**
 * Pure calculation functions for quick verification.
 */
function convertRectToPolar(real, imag) {
  const r = Math.sqrt(real * real + imag * imag);
  let thetaDeg = (Math.atan2(imag, real) * 180) / Math.PI;
  return {
    magnitude: Math.round(r * 1000) / 1000,
    angleDeg: Math.round(thetaDeg * 100) / 100
  };
}

function convertPolarToRect(magnitude, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  const real = magnitude * Math.cos(rad);
  const imag = magnitude * Math.sin(rad);
  return {
    real: Math.round(real * 1000) / 1000,
    imag: Math.round(imag * 1000) / 1000
  };
}

/**
 * Renders the Calculator Guide Modal.
 */
function openCalculatorGuideModal(defaultRecipeId = null) {
  let modal = document.getElementById('calculator-guide-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'calculator-guide-modal';
    modal.className = 'modal-backdrop';
    document.body.appendChild(modal);
  }

  const recipesHtml = FX82_RECIPES.map(item => `
    <div class="calc-recipe-card ${item.id === defaultRecipeId ? 'highlight' : ''}" id="recipe-${item.id}">
      <div class="calc-recipe-header">
        <h4>${item.title}</h4>
        <span class="calc-tag">${item.example}</span>
      </div>
      <div class="calc-keystroke-row">
        ${item.keystrokes.map(k => `
          <div class="key-step">
            <span class="calc-key">${k.key}</span>
            <span class="key-desc">${k.desc}</span>
          </div>
        `).join('<span class="key-arrow">➔</span>')}
      </div>
      <div class="calc-trap-alert">
        <strong>${uiIcon('alert-triangle',{class:'warn-ico'})} 考場防坑：</strong>${item.trap}
      </div>
    </div>
  `).join('');

  modal.innerHTML = `
    <div class="modal-content calc-modal-content">
      <div class="modal-header">
        <h3>考選部核定計算機（Casio fx-82SOLAR II）考場按法與速算驗證</h3>
        <button type="button" class="btn-close" onclick="closeCalculatorGuideModal()" aria-label="關閉">${uiIcon('x')}</button>
      </div>
      <div class="modal-body calc-modal-body">
        <!-- Interactive Verification Tool -->
        <div class="phasor-converter-box">
          <h4>相量與極座標即時速查器（考前對答案專用）</h4>
          <div class="converter-grid">
            <div class="converter-col">
              <label>直角座標 (A + jB)</label>
              <div class="input-duo">
                <input type="number" id="calc-in-real" placeholder="實部 A (例: 3)" step="any" oninput="runInteractiveConverter('rect')">
                <span>+ j</span>
                <input type="number" id="calc-in-imag" placeholder="虛部 B (例: 4)" step="any" oninput="runInteractiveConverter('rect')">
              </div>
            </div>
            <div class="converter-center">
              <span class="exchange-icon">⇄</span>
            </div>
            <div class="converter-col">
              <label>極座標 (R ∠ θ°)</label>
              <div class="input-duo">
                <input type="number" id="calc-in-mag" placeholder="大小 R" step="any" oninput="runInteractiveConverter('polar')">
                <span>∠</span>
                <input type="number" id="calc-in-ang" placeholder="角度 θ°" step="any" oninput="runInteractiveConverter('polar')">
              </div>
            </div>
          </div>
          <div id="converter-feedback" class="converter-feedback">請輸入數值進行雙向即時換算</div>
        </div>

        <!-- Recipe Keystroke Cards -->
        <h4 style="margin: 18px 0 10px 0; color: var(--accent-dark);">考場核心公式按鍵順序圖解</h4>
        <div class="calc-recipes-grid">
          ${recipesHtml}
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn-sol" onclick="closeCalculatorGuideModal()">關閉指南</button>
      </div>
    </div>
  `;

  modal.classList.add('show');
}

function closeCalculatorGuideModal() {
  const modal = document.getElementById('calculator-guide-modal');
  if (modal) modal.classList.remove('show');
}

function runInteractiveConverter(source) {
  const fb = document.getElementById('converter-feedback');
  if (source === 'rect') {
    const real = parseFloat(document.getElementById('calc-in-real').value);
    const imag = parseFloat(document.getElementById('calc-in-imag').value);
    if (!isNaN(real) && !isNaN(imag)) {
      const p = convertRectToPolar(real, imag);
      document.getElementById('calc-in-mag').value = p.magnitude;
      document.getElementById('calc-in-ang').value = p.angleDeg;
      if (fb) fb.innerHTML = `${uiIcon('check')} 換算完成：<strong>${real} + j${imag}</strong> = <strong>${p.magnitude} ∠ ${p.angleDeg}°</strong>（fx-82: 按 ${real} ➔ INV ➔ R➔P ➔ ${imag} ➔ = ➔ b）`;
    }
  } else if (source === 'polar') {
    const mag = parseFloat(document.getElementById('calc-in-mag').value);
    const ang = parseFloat(document.getElementById('calc-in-ang').value);
    if (!isNaN(mag) && !isNaN(ang)) {
      const r = convertPolarToRect(mag, ang);
      document.getElementById('calc-in-real').value = r.real;
      document.getElementById('calc-in-imag').value = r.imag;
      if (fb) fb.innerHTML = `${uiIcon('check')} 換算完成：<strong>${mag} ∠ ${ang}°</strong> = <strong>${r.real} + j${r.imag}</strong>（fx-82: 按 ${mag} ➔ INV ➔ P➔R ➔ ${ang} ➔ = ➔ b）`;
    }
  }
}

/**
 * Checks if question stem or solution involves phasor / AC / polar operations.
 */
function shouldShowCalculatorTip(stem, tags, topic) {
  const str = String(stem || '') + ' ' + (tags || []).join(' ') + ' ' + String(topic || '');
  return /交流|阻抗|相量|功率因數|虛功|實功|視在功率|短路容量|變壓器|感應機|相角|極座標|三相|正相|負相|零相|傳輸線|RLC|暫態/i.test(str);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    FX82_RECIPES,
    convertRectToPolar,
    convertPolarToRect,
    shouldShowCalculatorTip
  };
}
