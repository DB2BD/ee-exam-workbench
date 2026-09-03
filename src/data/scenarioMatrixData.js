// src/data/scenarioMatrixData.js
// -*- coding: utf-8 -*-
/**
 * scenarioMatrixData.js
 * =====================
 * Structured Scenario Matrix (參數敏感度情境分支卡) for questions requiring
 * manual review, parameter clarification, or multi-branch derivation.
 */

const SCENARIO_MATRIX_DATA = {
  'EE-109-02-3': {
    qid: 'EE-109-02-3',
    subject: '電子學（含電力電子）',
    year: 109,
    qnum: 3,
    title: '返馳式轉換器 CCM / DCM 導通模式與平均電流分支',
    coreConflict: '題目未明定導通模式；官方電感數值與佔空比剛好落在 DCM／臨界導通模式（CrCM）邊界。',
    scenarioA: {
      name: '情境 A：DCM／臨界導通邊界 (首選標準解)',
      condition: '依給定參數回算消磁時間 $t_{\\text{demag}} = t_{\\text{off}} = 166.7\\,\\mu\\text{s}$，電感電流於週期末降至 0',
      keyValues: [
        { param: '一次側峰值電流 $I_{p,\\max}$', val: '$60.00\\text{ A}$' },
        { param: '一次側導通平均電流 $I_{p,\\text{avg}|\\text{on}}$', val: '$30.00\\text{ A}$ (三角形面積)' },
        { param: '全週期平均輸入電流 $I_{p,\\text{avg}}$', val: '$22.50\\text{ A}$ ($D \\times 30\\text{ A}$)' },
        { param: '輸入功率 $P_{\\text{in}}$', val: '$1.08\\text{ kW}$' }
      ],
      examAdvice: '優先書寫此分支：先檢驗消磁時間確認其位於 DCM 邊界，推導過程嚴密無破綻。'
    },
    scenarioB: {
      name: '情境 B：CCM 連續導通假設 (傳統近似解)',
      condition: '若題意隱含電感極大值或採連續波形，假設電流漣波未降至 0',
      keyValues: [
        { param: '一次側電流漣波 $\\Delta I_L$', val: '$60.00\\text{ A}$' },
        { param: '若給定額定負載電流', val: '平均電流依輸出功率 $P_o$ 反推 $I_{p,\\text{avg}} = P_o / (\\eta V_{\\text{in}})$' },
        { param: '開關耐壓 $V_{\\text{switch}}$', val: '$V_{\\text{in}} + \\frac{N_p}{N_s} V_o = 144\\text{ V}$' }
      ],
      examAdvice: '在考卷補充備註：「若閱卷委員採連續導通模式假設，則平均電流由負載功率決定，開關耐壓仍為 144 V」。'
    }
  },

  'EE-111-02-3': {
    qid: 'EE-111-02-3',
    subject: '電子學（含電力電子）',
    year: 111,
    qnum: 3,
    title: 'MOSFET 共源極源極退化增益與平方律偏壓矛盾',
    coreConflict: '題目同時給定 $|A_v|=5$、偏壓電流 $I_D=3.17\\text{ mA}$ 與 $R_S=30\\,\\Omega$；但由平方律推導之 $g_m$ 與增益公式產生數值衝突。',
    scenarioA: {
      name: '情境 A：保留指定增益 $|A_v|=5$ (設計導向解)',
      condition: '以 $|A_v| = \\frac{g_m R_D}{1 + g_m R_S} = 5$ 為準，修正 $R_S$ 為自洽值',
      keyValues: [
        { param: '修正後源極電阻 $R_S$', val: '$26.67\\,\\Omega$' },
        { param: '小訊號轉導 $g_m$', val: '$0.075\\text{ S}$ ($75.0\\text{ mS}$)' },
        { param: '過驅電壓 $V_{OV}$', val: '$0.0845\\text{ V}$' },
        { param: '寬長比 $W/L$', val: '$4436.12$' }
      ],
      examAdvice: '第一步先寫出標準增益公式，計算若增益嚴格為 5 時所需的 $R_S$ 與 $W/L$。'
    },
    scenarioB: {
      name: '情境 B：嚴格保留題面 $R_S=30\\,\\Omega$ (參數回算解)',
      condition: '嚴格代入題面 $R_S=30\\,\\Omega$ 與 $I_D=3.17\\text{ mA}$，由平方律決定 $g_m$',
      keyValues: [
        { param: '轉導 $g_m = 2/R_S$', val: '$0.0667\\text{ S}$ ($66.7\\text{ mS}$)' },
        { param: '實際閉迴路增益 $|A_v|$', val: '$4.4444\\text{ V/V}$ (誤差約 11.1%)' },
        { param: '寬長比 $W/L$', val: '$3522.22$' }
      ],
      examAdvice: '緊接著註明：「若直接採用題設 $R_S=30\\,\\Omega$，由偏壓條件回算實際增益為 4.44 V/V」，展現通透的分析能力。'
    }
  },

  'EE-113-02-2': {
    qid: 'EE-113-02-2',
    subject: '電子學（含電力電子）',
    year: 113,
    qnum: 2,
    title: 'BJT 共基極放大器熱電壓 $V_T$ 參數分支',
    coreConflict: '原題圖未明示操作溫度或熱電壓 $V_T$ 取值（25 mV、25.85 mV 亦或 26 mV）。',
    scenarioA: {
      name: '情境 A：常溫標準 $V_T = 25\\text{ mV}$ ($300\\text{ K}$ 實用值)',
      condition: '國考電子學最常用近似 $V_T = 25\\text{ mV}$',
      keyValues: [
        { param: '動態射極電阻 $r_e$', val: '$50.00\\,\\Omega$ ($V_T / I_E$)' },
        { param: '交流輸入阻抗 $R_{\\text{in}}$', val: '$50.00\\,\\Omega$' },
        { param: '電壓增益 $A_v = v_o / v_{\\text{sig}}$', val: '$47.52\\text{ V/V}$' },
        { param: '輸出電阻 $R_o$', val: '$12.0\\text{ k}\\Omega$' }
      ],
      examAdvice: '在作答第一行明確標示：「假設熱電壓 $V_T = 25\\text{ mV}$」，計算數值乾淨整齊。'
    },
    scenarioB: {
      name: '情境 B：物理標準 $V_T = 25.85\\text{ mV} \\approx 26\\text{ mV}$',
      condition: '教科書 Sedra/Smith 標準常溫 $T=300\\text{ K}$ 理論值',
      keyValues: [
        { param: '動態射極電阻 $r_e$', val: '$51.70\\,\\Omega \\sim 52.00\\,\\Omega$' },
        { param: '交流輸入阻抗 $R_{\\text{in}}$', val: '$51.70\\,\\Omega$' },
        { param: '電壓增益 $A_v = v_o / v_{\\text{sig}}$', val: '$46.88\\text{ V/V} \\sim 46.68\\text{ V/V}$' },
        { param: '相對誤差', val: '與 25 mV 分支僅差 $1.3\\%$' }
      ],
      examAdvice: '末尾備註：「若採 $V_T=26\\text{ mV}$，則 $A_v=46.68\\text{ V/V}$」，兩種分支皆可完全得分。'
    }
  },

  'EE-110-06-5': {
    qid: 'EE-110-06-5',
    subject: '工業配電',
    year: 110,
    qnum: 5,
    title: '自備變電所短路容量與非對稱倍率 $K=1.6$ 定義',
    coreConflict: '題目未提供三台電動機個別功因與效率，且 $K=1.6$ 存在「RMS 非對稱係數」與「ANSI 峰值倍率」兩種工程規範解釋。',
    scenarioA: {
      name: '情境 A：$K=1.6$ 為對稱成分轉 RMS 非對稱係數',
      condition: '依 CNS / 經濟部屋內線路裝置規則，瞬時斷路電流包含直流分量有效值',
      keyValues: [
        { param: '系統對稱短路容量 $S_{\\text{sym}}$', val: '以母線等效阻抗求出三相對稱容量' },
        { param: '非對稱短路容量 $S_{\\text{asym}}$', val: '$1.6 \\times S_{\\text{sym}}$ (RMS 視在容量)' },
        { param: '馬達次暫態貢獻', val: '以參數化 $k_i = \\eta_i \\cdot \\text{pf}_i$ 統一表達' }
      ],
      examAdvice: '主推此分支，公式寫為 $I_{\\text{asym, rms}} = 1.6 \\times I_{\\text{sym}}$。'
    },
    scenarioB: {
      name: '情境 B：$K=1.6$ 採 ANSI/IEEE 瞬時峰值倍率',
      condition: '用於檢驗斷路器投入容量（Making capacity）或母線動態應力',
      keyValues: [
        { param: '首週期非對稱峰值 $I_{\\text{peak}}$', val: '$1.6 \\times \\sqrt{2} \\times I_{\\text{sym}}$ 或直接以 $1.6$ 乘峰值' },
        { param: '斷路器投入容量額定', val: '需大於瞬時衝擊電流峰值' }
      ],
      examAdvice: '補充說明：「若 $K=1.6$ 代表峰值動態倍率，則斷路器閉合投入額定需相應提高」。'
    }
  },

  'EE-107-06-2': {
    qid: 'EE-107-06-2',
    subject: '工業配電',
    year: 107,
    qnum: 2,
    title: '100 HP 馬達滿載電流查表值 vs 經驗反算值',
    coreConflict: '107 年度試題未附查表附件，現行屋內線路裝置規則表 258-3 與歷史傳統試題常用值存在差異。',
    scenarioA: {
      name: '情境 A：現行法規表 258-3 標準查表值 ($I_{FLC} = 238\\text{ A}$)',
      condition: '依經濟部《用戶用電設備裝置規則》表 258-3（三相 220V 感應電動機滿載電流表）',
      keyValues: [
        { param: '滿載電流 $I_{\\text{FLC}}$', val: '$238.0\\text{ A}$' },
        { param: '分路導線安培容量 (125%)', val: '$297.5\\text{ A}$' },
        { param: '線路電壓降 $V_{\\text{drop}}$', val: '以 $238\\text{ A}$ 與功率因數計算' }
      ],
      examAdvice: '首選此標準解，並明確引註法條名稱：「依用戶用電設備裝置規則表 258-3 查得 100HP/220V 為 238A」。'
    },
    scenarioB: {
      name: '情境 B：銘牌經驗反算值 ($I_{FLC} \\approx 250\\text{ A}$)',
      condition: '若未背法規表，以標準馬達效率 $\\eta=0.9$、$\\text{pf}=0.85$ 經驗反算',
      keyValues: [
        { param: '反算額定電流 $I_{\\text{calc}}$', val: '$\\frac{100 \\times 746}{\\sqrt{3} \\times 220 \\times 0.85 \\times 0.9} \\approx 256.4\\text{ A} \\sim 250\\text{ A}$' },
        { param: '導線安培容量 (125%)', val: '約 $312.5\\text{ A} \\sim 320.5\\text{ A}$' }
      ],
      examAdvice: '若忘記 238A 數字，可用「設效率 90%、功因 85% 反算約 250A」續解，步驟分數仍可穩拿 80% 以上。'
    }
  },

  'EE-106-06-2': {
    qid: 'EE-106-06-2',
    subject: '工業配電',
    year: 106,
    qnum: 2,
    title: '單相短路故障導體阻抗往返迴路定義',
    coreConflict: '題面給定每導體阻抗，未明確說明是否已包含線間往返迴路。',
    scenarioA: {
      name: '情境 A：往返雙導線完整迴路 (工程物理標準解)',
      condition: '短路電流由相線流出、經中性線或另一相線返回，故障迴路阻抗為 $2 \\times Z_{\\text{conductor}}$',
      keyValues: [
        { param: '總故障阻抗 $Z_{\\text{fault}}$', val: '$2 \\times (R + jX)$' },
        { param: '短路電流 $I_{\\text{sc}}$', val: '$V_{\\text{line}} / (2 \\times |Z|)$' }
      ],
      examAdvice: '列為首選：「故障電流必形成封閉迴路，故障阻抗取往返兩導體之和 $2Z$」。'
    },
    scenarioB: {
      name: '情境 B：給定阻抗已為單向等效',
      condition: '若命題者將標示阻抗視為全迴路等效阻抗',
      keyValues: [
        { param: '總故障阻抗 $Z_{\\text{fault}}$', val: '$1 \\times (R + jX)$' },
        { param: '短路電流 $I_{\\text{sc}}$', val: '$V_{\\text{line}} / |Z|$ (數值為情境 A 之 2 倍)' }
      ],
      examAdvice: '在解答末尾以一行提示補充：「若給定阻抗已含往返迴路，則故障電流為上述計算值之 2 倍」。'
    }
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SCENARIO_MATRIX_DATA };
}
