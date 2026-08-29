// -*- coding: utf-8 -*-
/**
 * knowledge-dag.js
 * =================
 * Comprehensive Knowledge Dependency DAG (Directed Acyclic Graph)
 * across 6 Electrical Engineering Core Subjects (60+ Nodes).
 *
 * Provides:
 * 1. KNOWLEDGE_DAG: Topological nodes with prerequisite links, level, formulas, and traps.
 * 2. QUESTION_DAG_MAPPER: Automated mapping rules from question content/tags to DAG nodes.
 * 3. tracePrerequisiteWeaknesses(nodeId, progressState): Traces prerequisite bottleneck nodes.
 */

const KNOWLEDGE_DAG = {
  // -------------------------------------------------------------
  // 01. 電路學 (Circuit Theory)
  // -------------------------------------------------------------
  'ct-ohm-kcl-kvl': {
    id: 'ct-ohm-kcl-kvl',
    subject: '01',
    subjectName: '電路學',
    name: '歐姆定律與基本 KCL/KVL',
    level: 1,
    prereqs: [],
    coreFormula: 'V = I R, \\sum I_{\\text{in}} = \\sum I_{\\text{out}}, \\sum V = 0',
    keyTrap: '注意參考方向與極性正負號設定。'
  },
  'ct-divider-equiv': {
    id: 'ct-divider-equiv',
    subject: '01',
    subjectName: '電路學',
    name: '分壓分流與電阻等效化簡',
    level: 1,
    prereqs: ['ct-ohm-kcl-kvl'],
    coreFormula: 'V_x = V_s \\frac{R_x}{R_1 + R_2}, I_x = I_s \\frac{R_{\\text{other}}}{R_1 + R_2}',
    keyTrap: '並聯分流公式分子為「對方電阻」。'
  },
  'ct-node-mesh': {
    id: 'ct-node-mesh',
    subject: '01',
    subjectName: '電路學',
    name: '節點電壓法與網目電流法',
    level: 2,
    prereqs: ['ct-ohm-kcl-kvl'],
    coreFormula: '\\frac{V_1 - V_2}{R} + I_s = 0',
    keyTrap: '含相依電源與超節點 (Supernode) 時需額外建立輔助約束方程式。'
  },
  'ct-thevenin-norton': {
    id: 'ct-thevenin-norton',
    subject: '01',
    subjectName: '電路學',
    name: '戴維寧與諾頓等效定理',
    level: 2,
    prereqs: ['ct-node-mesh', 'ct-divider-equiv'],
    coreFormula: 'V_{th} = V_{oc}, R_{th} = \\frac{V_{oc}}{I_{sc}} = \\frac{v_{\\text{test}}}{i_{\\text{test}}}',
    keyTrap: '含受控源時嚴禁用「獨立源關閉直接求電阻」，必須加測試電壓源法。'
  },
  'ct-max-power': {
    id: 'ct-max-power',
    subject: '01',
    subjectName: '電路學',
    name: '最大功率轉移定理',
    level: 2,
    prereqs: ['ct-thevenin-norton'],
    coreFormula: 'R_L = R_{th} \\implies P_{\\max} = \\frac{V_{th}^2}{4 R_{th}}, Z_L = Z_{th}^*',
    keyTrap: '交流最大功率傳輸負載阻抗為戴維寧阻抗的「共軛複數」。'
  },
  'ct-superposition': {
    id: 'ct-superposition',
    subject: '01',
    subjectName: '電路學',
    name: '重疊定理',
    level: 2,
    prereqs: ['ct-node-mesh'],
    coreFormula: 'x(t) = \\sum x_k(t) \\text{ (獨立電源單獨作用響應之和)}',
    keyTrap: '受控源不可關閉；功率計算不適用重疊定理（需算完總電壓/電流後再算功率）。'
  },
  'ct-first-order-rc-rl': {
    id: 'ct-first-order-rc-rl',
    subject: '01',
    subjectName: '電路學',
    name: '一階 RC/RL 暫態與三要素法',
    level: 2,
    prereqs: ['ct-thevenin-norton'],
    coreFormula: 'x(t) = x(\\infty) + [x(0^+) - x(\\infty)] e^{-t/\\tau}, \\tau_{RC} = R_{th}C, \\tau_{RL} = \\frac{L}{R_{th}}',
    keyTrap: '電感電流與電容電壓在換位瞬間連續：i_L(0^+) = i_L(0^-), v_C(0^+) = v_C(0^-)。'
  },
  'ct-phasor-ac': {
    id: 'ct-phasor-ac',
    subject: '01',
    subjectName: '電路學',
    name: '交流穩態相量與阻抗分析',
    level: 2,
    prereqs: ['ct-node-mesh'],
    coreFormula: 'Z_L = j\\omega L, Z_C = \\frac{1}{j\\omega C} = -j \\frac{1}{\\omega C}, \\mathbf{V} = \\mathbf{I} \\mathbf{Z}',
    keyTrap: '相量運算需注意角頻率 \\omega (rad/s) 與頻率 f (Hz) 轉換 (\\omega = 2\\pi f)。'
  },
  'ct-complex-power': {
    id: 'ct-complex-power',
    subject: '01',
    subjectName: '電路學',
    name: '複數功率與功率因數改善',
    level: 2,
    prereqs: ['ct-phasor-ac'],
    coreFormula: 'S = P + j Q = \\mathbf{V}_{\\text{rms}} \\mathbf{I}_{\\text{rms}}^*, Q_C = P(\\tan\\theta_1 - \\tan\\theta_2)',
    keyTrap: '複數功率公式電流相量必須取「共軛複數 (Conjugate)」。'
  },
  'ct-mutual-inductance': {
    id: 'ct-mutual-inductance',
    subject: '01',
    subjectName: '電路學',
    name: '互感耦合與同名端分析',
    level: 3,
    prereqs: ['ct-phasor-ac'],
    coreFormula: 'v_1 = L_1 \\frac{di_1}{dt} \\pm M \\frac{di_2}{dt}',
    keyTrap: '電流同時流入（或流出）同名端時互感項取正號，否則取負號。'
  },
  'ct-three-phase': {
    id: 'ct-three-phase',
    subject: '01',
    subjectName: '電路學',
    name: '三相平衡電路 (Y-Δ 轉換)',
    level: 3,
    prereqs: ['ct-complex-power'],
    coreFormula: 'V_{L-L} = \\sqrt{3} V_{\\phi} \\angle +30^\\circ (Y), I_L = \\sqrt{3} I_{\\phi} \\angle -30^\\circ (\\Delta), P_{3\\phi} = \\sqrt{3} V_L I_L \\cos\\theta',
    keyTrap: '線電壓超前相電壓 30 度；單相化等效時必須全部換成 Y-Y 連接。'
  },
  'ct-two-port': {
    id: 'ct-two-port',
    subject: '01',
    subjectName: '電路學',
    name: '雙埠網路參數 (ABCD, Z, Y, H)',
    level: 3,
    prereqs: ['ct-thevenin-norton', 'ct-phasor-ac'],
    coreFormula: '\\begin{bmatrix} V_1 \\\\ I_1 \\end{bmatrix} = \\begin{bmatrix} A & B \\\\ C & D \\end{bmatrix} \\begin{bmatrix} V_2 \\\\ -I_2 \\end{bmatrix}, AD - BC = 1',
    keyTrap: 'ABCD 傳輸矩陣二次側電流方向定義為「流出」端口。'
  },
  'ct-second-order-rlc': {
    id: 'ct-second-order-rlc',
    subject: '01',
    subjectName: '電路學',
    name: '二階 RLC 暫態分析',
    level: 3,
    prereqs: ['ct-first-order-rc-rl'],
    coreFormula: 's^2 + 2\\alpha s + \\omega_0^2 = 0 \\implies \\alpha > \\omega_0 \\text{ (過阻尼)}, \\alpha = \\omega_0 \\text{ (臨界)}, \\alpha < \\omega_0 \\text{ (欠阻尼)}',
    keyTrap: '串聯 \\alpha = R/(2L)，並聯 \\alpha = 1/(2RC)，兩者公式完全相反！'
  },
  'ct-laplace-circuit': {
    id: 'ct-laplace-circuit',
    subject: '01',
    subjectName: '電路學',
    name: 'S 域拉氏轉換電路求解',
    level: 3,
    prereqs: ['ct-second-order-rlc', 'ct-first-order-rc-rl'],
    coreFormula: 'L \\to sL - L i(0^-), C \\to \\frac{1}{sC} + \\frac{v(0^-)}{s}',
    keyTrap: '包含初始儲能時，電感初始電流源為 i(0^-)/s（並聯），電容初始電壓源為 v(0^-)/s（串聯）。'
  },

  // -------------------------------------------------------------
  // 02. 電子學（含電力電子）(Electronics & Power Electronics)
  // -------------------------------------------------------------
  'el-diode-rectifier': {
    id: 'el-diode-rectifier',
    subject: '02',
    subjectName: '電子學',
    name: '二極體整流與濾波電路',
    level: 1,
    prereqs: [],
    coreFormula: 'V_{dc} = \\frac{2 V_m}{\\pi}, V_{r(p-p)} = \\frac{V_m}{2 f R_L C}',
    keyTrap: '全波橋式整流二極體 PIV = V_m，中點抽頭 PIV = 2V_m。'
  },
  'el-zener-regulator': {
    id: 'el-zener-regulator',
    subject: '02',
    subjectName: '電子學',
    name: '齊納二極體穩壓電路',
    level: 2,
    prereqs: ['el-diode-rectifier'],
    coreFormula: 'V_L = V_Z, I_Z = I_S - I_L \\ge I_{ZK}',
    keyTrap: '檢驗最小輸入電壓或最大負載電流時，齊納電流不得小於膝點電流 I_ZK。'
  },
  'el-bjt-bias-small-signal': {
    id: 'el-bjt-bias-small-signal',
    subject: '02',
    subjectName: '電子學',
    name: 'BJT 偏壓分析與小訊號模型',
    level: 2,
    prereqs: [],
    coreFormula: 'I_C = \\beta I_B = I_S e^{V_{BE}/V_T}, g_m = \\frac{I_C}{V_T}, r_\\pi = \\frac{\\beta}{g_m}, r_o = \\frac{V_A}{I_C}',
    keyTrap: '工作在主動區必須滿足：V_BE = 0.7V 且 V_CE > V_CE(sat) ~ 0.2V。'
  },
  'el-mosfet-bias-small-signal': {
    id: 'el-mosfet-bias-small-signal',
    subject: '02',
    subjectName: '電子學',
    name: 'MOSFET 飽和偏壓與小訊號模型',
    level: 2,
    prereqs: [],
    coreFormula: 'I_D = \\frac{1}{2} k_n\' \\frac{W}{L} (V_{GS} - V_{th})^2 (1 + \\lambda V_{DS}), g_m = \\sqrt{2 k_n I_D}',
    keyTrap: '飽和區夾止條件：V_DS >= V_GS - V_th 且 V_GS > V_th。'
  },
  'el-opamp-ideal': {
    id: 'el-opamp-ideal',
    subject: '02',
    subjectName: '電子學',
    name: '理想 OPA 與基本運算放大電路',
    level: 2,
    prereqs: [],
    coreFormula: 'v_+ = v_- \\text{ (虛短路)}, i_+ = i_- = 0 \\text{ (虛斷路)}, A_v = -\\frac{R_f}{R_1} \\text{ (反相)}',
    keyTrap: '虛短路僅在「負回授 (Negative Feedback)」且未飽和時成立。'
  },
  'el-diff-amp': {
    id: 'el-diff-amp',
    subject: '02',
    subjectName: '電子學',
    name: '差動放大器 (Ad, Acm, CMRR)',
    level: 3,
    prereqs: ['el-bjt-bias-small-signal', 'el-mosfet-bias-small-signal'],
    coreFormula: 'A_d = g_m R_D, A_{cm} = -\\frac{g_m R_D}{1 + 2 g_m R_{SS}}, \\text{CMRR} = \\left|\\frac{A_d}{A_{cm}}\\right|',
    keyTrap: 'CMRR 取 dB 值時需取 20 log10(CMRR)。'
  },
  'el-active-filter': {
    id: 'el-active-filter',
    subject: '02',
    subjectName: '電子學',
    name: '主動濾波器與頻率響應',
    level: 3,
    prereqs: ['el-opamp-ideal'],
    coreFormula: 'H(s) = \\frac{\\omega_0^2}{s^2 + \\frac{\\omega_0}{Q} s + \\omega_0^2}, \\omega_c = \\frac{1}{R C}',
    keyTrap: '高頻極點透過米勒效應 (Miller Effect) 將 C_gd 放大為 C_in = C_gd(1 + |Av|)。'
  },
  'el-feedback-stability': {
    id: 'el-feedback-stability',
    subject: '02',
    subjectName: '電子學',
    name: '負回授放大器與相位邊限',
    level: 4,
    prereqs: ['el-diff-amp', 'el-active-filter'],
    coreFormula: 'A_f = \\frac{A}{1 + A\\beta}, \\text{PM} = 180^\\circ + \\angle A\\beta(\\omega_{0\\text{dB}})',
    keyTrap: '閉迴路穩定條件為環路增益 |A\\beta| = 1 時，相位延遲不得達到 180 度 (PM > 0)。'
  },
  'el-pe-buck-boost': {
    id: 'el-pe-buck-boost',
    subject: '02',
    subjectName: '電力電子',
    name: 'DC-DC Buck/Boost 轉換器 (CCM/DCM)',
    level: 3,
    prereqs: ['el-diode-rectifier'],
    coreFormula: 'V_o = D V_d \\text{ (Buck)}, V_o = \\frac{D}{1-D} V_d \\text{ (Buck-Boost)}, \\Delta I_L = \\frac{V_d - V_o}{L} D T_s',
    keyTrap: '穩態分析立論基礎為「電感伏秒平衡 (Volt-Second Balance)」與「電容電荷平衡」。'
  },
  'el-pe-inverter-spwm': {
    id: 'el-pe-inverter-spwm',
    subject: '02',
    subjectName: '電力電子',
    name: '全橋變流器與 SPWM 調變',
    level: 4,
    prereqs: ['el-pe-buck-boost'],
    coreFormula: 'm_a = \\frac{V_{\\text{control}}}{V_{\\text{tri}}}, V_{o1} = m_a V_d',
    keyTrap: 'SPWM 調變指標 m_a <= 1.0 為線性區；上下臂切換需設置死區時間 (Dead-time)。'
  },
  'el-pe-thyristor-rectifier': {
    id: 'el-pe-thyristor-rectifier',
    subject: '02',
    subjectName: '電力電子',
    name: '閘流體 (Thyristor) 相控整流',
    level: 4,
    prereqs: ['el-diode-rectifier'],
    coreFormula: 'V_{dc} = \\frac{2 V_m}{\\pi} \\cos\\alpha \\text{ (全控橋)}, V_{dc} = \\frac{V_m}{\\pi}(1 + \\cos\\alpha) \\text{ (半控橋)}',
    keyTrap: '感性負載下若無續流二極體，輸出電壓會在電感放電期間出現負電壓區。'
  },

  // -------------------------------------------------------------
  // 03. 工程數學 (Engineering Mathematics)
  // -------------------------------------------------------------
  'em-first-order-ode': {
    id: 'em-first-order-ode',
    subject: '03',
    subjectName: '工程數學',
    name: '一階可分離與線性 ODE',
    level: 1,
    prereqs: [],
    coreFormula: 'y\' + P(x)y = Q(x) \\implies y(x) = \\frac{1}{I(x)} \\int I(x) Q(x) dx + \\frac{C}{I(x)}, I(x) = e^{\\int P(x) dx}',
    keyTrap: '積分因子法展開時別忘了積分常數 C 也必須除以 I(x)。'
  },
  'em-second-order-ode-homogeneous': {
    id: 'em-second-order-ode-homogeneous',
    subject: '03',
    subjectName: '工程數學',
    name: '二階常係數齊次 ODE',
    level: 2,
    prereqs: ['em-first-order-ode'],
    coreFormula: 'a r^2 + b r + c = 0 \\implies y_h = c_1 e^{r_1 x} + c_2 e^{r_2 x} \\text{ 或 } e^{\\alpha x}(c_1 \\cos\\beta x + c_2 \\sin\\beta x)',
    keyTrap: '重根 r 時，第二特解必須乘以 x：c_2 x e^{r x}。'
  },
  'em-second-order-ode-nonhomogeneous': {
    id: 'em-second-order-ode-nonhomogeneous',
    subject: '03',
    subjectName: '工程數學',
    name: '二階非齊次 ODE (未定係數/參數變更法)',
    level: 3,
    prereqs: ['em-second-order-ode-homogeneous'],
    coreFormula: 'y_p = -y_1 \\int \\frac{y_2 r(x)}{W(y_1, y_2)} dx + y_2 \\int \\frac{y_1 r(x)}{W(y_1, y_2)} dx',
    keyTrap: '未定係數法若假設之形式與齊次解重複時，必須乘以 x（修正法則）。'
  },
  'em-laplace-transform': {
    id: 'em-laplace-transform',
    subject: '03',
    subjectName: '工程數學',
    name: '拉氏轉換與反轉換 (部分分式法)',
    level: 3,
    prereqs: ['em-first-order-ode'],
    coreFormula: '\\mathcal{L}\\{f(t)\\} = \\int_0^\\infty e^{-st} f(t) dt, \\mathcal{L}\\{y\'\'\\} = s^2 Y(s) - s y(0) - y\'(0)',
    keyTrap: '位移定理 \\mathcal{L}\\{e^{at} f(t)\\} = F(s-a)；t-位移需乘階梯函數 u(t-a)。'
  },
  'em-fourier-series': {
    id: 'em-fourier-series',
    subject: '03',
    subjectName: '工程數學',
    name: '傅立葉級數與週期函數展開',
    level: 3,
    prereqs: [],
    coreFormula: 'f(x) = a_0 + \\sum (a_n \\cos\\frac{n\\pi x}{L} + b_n \\sin\\frac{n\\pi x}{L}), a_n = \\frac{1}{L}\\int_{-L}^L f(x)\\cos\\frac{n\\pi x}{L} dx',
    keyTrap: '偶函數 b_n = 0，奇函數 a_0 = a_n = 0；利用對稱性可節省一半積分時間。'
  },
  'em-matrix-det-inv': {
    id: 'em-matrix-det-inv',
    subject: '03',
    subjectName: '工程數學',
    name: '矩陣代數、行列式與反矩陣',
    level: 1,
    prereqs: [],
    coreFormula: 'A^{-1} = \\frac{1}{\\det(A)} \\text{adj}(A)',
    keyTrap: '克拉瑪法則 (Cramer\'s Rule) 僅適用於 det(A) != 0 之非奇異方陣。'
  },
  'em-eigen-diagonal': {
    id: 'em-eigen-diagonal',
    subject: '03',
    subjectName: '工程數學',
    name: '特徵值、特徵向量與矩陣對角化',
    level: 3,
    prereqs: ['em-matrix-det-inv'],
    coreFormula: '\\det(A - \\lambda I) = 0, A v = \\lambda v, A = P D P^{-1}',
    keyTrap: '矩陣可對角化的充要條件為具有 n 個線性獨立的特徵向量（幾何重數等於代數重數）。'
  },
  'em-complex-cauchy-residue': {
    id: 'em-complex-cauchy-residue',
    subject: '03',
    subjectName: '工程數學',
    name: '複變分析、柯西定理與留數定理',
    level: 4,
    prereqs: [],
    coreFormula: '\\oint_C f(z) dz = 2\\pi j \\sum \\text{Res}(f, z_k), \\text{Res}(f, z_0) = \\lim_{z\\to z_0} (z-z_0) f(z)',
    keyTrap: '留數計算僅納入圍道 C 內部（Inside the contour）的奇異點！'
  },
  'em-pde-separation': {
    id: 'em-pde-separation',
    subject: '03',
    subjectName: '工程數學',
    name: '偏微分方程 (分離變數法)',
    level: 4,
    prereqs: ['em-second-order-ode-nonhomogeneous', 'em-fourier-series'],
    coreFormula: 'u(x,t) = X(x) T(t) \\implies \\frac{X\'\'}{X} = \\frac{\\dot{T}}{c^2 T} = -\\lambda^2',
    keyTrap: '邊界條件決定特徵值 \\lambda_n 與特徵函數 X_n(x)；初始條件決定傅立葉級數係數。'
  },
  'em-svd-linear-systems': {
    id: 'em-svd-linear-systems',
    subject: '03',
    subjectName: '工程數學',
    name: '奇異值分解 (SVD) 與零空間分析',
    level: 5,
    prereqs: ['em-eigen-diagonal'],
    coreFormula: 'A = U \\Sigma V^T, \\sigma_i = \\sqrt{\\lambda_i(A^T A)}, A^+ = V \\Sigma^+ U^T',
    keyTrap: '奇異值依大小降序排列 \\sigma_1 \\ge \\sigma_2 \\ge \\dots \\ge 0；右奇異向量 V 為 A^T A 之特徵向量。'
  },
  'em-probability-statistics': {
    id: 'em-probability-statistics',
    subject: '03',
    subjectName: '工程數學',
    name: '機率與統計',
    level: 2,
    prereqs: [],
    coreFormula: 'E[X] = \\sum_x x p(x), \\operatorname{Var}(X) = E[(X-E[X])^2]',
    keyTrap: '期望值、變異數與標準差的定義不可混用。'
  },
  'em-vector-analysis': {
    id: 'em-vector-analysis',
    subject: '03',
    subjectName: '工程數學',
    name: '向量分析與向量微積分',
    level: 2,
    prereqs: [],
    coreFormula: '\\nabla f, \\nabla\\cdot\\mathbf{F}, \\nabla\\times\\mathbf{F}',
    keyTrap: '梯度、散度與旋度的運算對象及結果型態不同。'
  },

  // -------------------------------------------------------------
  // 04. 電機機械 (Electrical Machines)
  // -------------------------------------------------------------
  'emach-magnetic-circuits': {
    id: 'emach-magnetic-circuits',
    subject: '04',
    subjectName: '電機機械',
    name: '磁路定律與磁滯飽和',
    level: 1,
    prereqs: [],
    coreFormula: '\\mathcal{F} = N i = \\phi \\mathcal{R}, \\mathcal{R} = \\frac{l}{\\mu A}',
    keyTrap: '氣隙磁阻遠大於鐵心磁阻；磁通連續性在氣隙需考慮邊緣效應。'
  },
  'emach-single-phase-transformer': {
    id: 'emach-single-phase-transformer',
    subject: '04',
    subjectName: '電機機械',
    name: '單相變壓器等效電路與開短路試驗',
    level: 2,
    prereqs: ['emach-magnetic-circuits'],
    coreFormula: 'a = \\frac{N_1}{N_2} = \\frac{V_1}{V_2}, R_{eq1} = R_1 + a^2 R_2, X_{eq1} = X_1 + a^2 X_2, \\text{VR} = \\frac{V_{NL} - V_{FL}}{V_{FL}}',
    keyTrap: '開路試驗（低壓側加額定電壓）測激磁支路 R_c, X_m；短路試驗（高壓側加額定電流）測等效阻抗 R_eq, X_eq。'
  },
  'emach-autotransformer': {
    id: 'emach-autotransformer',
    subject: '04',
    subjectName: '電機機械',
    name: '自耦變壓器容量提升比',
    level: 3,
    prereqs: ['emach-single-phase-transformer'],
    coreFormula: 'S_{\\text{auto}} = \\frac{V_H}{V_H - V_X} S_{\\text{2-wnd}} = (1 + a) S_{\\text{2-wnd}}',
    keyTrap: '共用繞組電流為高壓側與低壓側電流之差值 (I_X - I_H)；注意共用端接線極性。'
  },
  'emach-three-phase-transformer': {
    id: 'emach-three-phase-transformer',
    subject: '04',
    subjectName: '電機機械',
    name: '三相變壓器組接線 (Y-Y, Y-Δ, Δ-Δ, V-V)',
    level: 3,
    prereqs: ['emach-single-phase-transformer'],
    coreFormula: 'S_{V-V} = \\sqrt{3} V_L I_L = \\sqrt{3} S_{\\text{1\\phi}} = \\frac{\\sqrt{3}}{3} S_{\\Delta-\\Delta} \\approx 57.7\\% S_{\\Delta-\\Delta}',
    keyTrap: 'Y-Δ 接法高壓側線電壓超前低壓側線電壓 30 度 (ANSI 標準)。'
  },
  'emach-dc-motor-generator': {
    id: 'emach-dc-motor-generator',
    subject: '04',
    subjectName: '電機機械',
    name: '直流電機 (分激/串激特性與調速)',
    level: 2,
    prereqs: ['emach-magnetic-circuits'],
    coreFormula: 'E_a = K_a \\phi \\omega_m, T_e = K_a \\phi I_a, V_t = E_a + I_a R_a',
    keyTrap: '分激電機降磁通調速時，轉速上升但轉矩容量下降；串激電機嚴禁空載運轉（會飛車！）。'
  },
  'emach-induction-motor-equiv': {
    id: 'emach-induction-motor-equiv',
    subject: '04',
    subjectName: '電機機械',
    name: '感應電動機等效電路與戴維寧化簡',
    level: 3,
    prereqs: ['emach-single-phase-transformer'],
    coreFormula: 's = \\frac{n_s - n_r}{n_s}, R_2\'/s = R_2\' + R_2\'\\frac{1-s}{s}, V_{th} = V_1 \\frac{X_m}{\\sqrt{R_1^2 + (X_1 + X_m)^2}}',
    keyTrap: '轉子電阻 R2/s 包含銅損電阻 R2 與等效機械負載電阻 R2(1-s)/s。'
  },
  'emach-induction-motor-torque': {
    id: 'emach-induction-motor-torque',
    subject: '04',
    subjectName: '電機機械',
    name: '感應電動機轉矩-轉差率曲線與最大轉矩',
    level: 3,
    prereqs: ['emach-induction-motor-equiv'],
    coreFormula: 's_{\\max} = \\frac{R_2\'}{\\sqrt{R_{th}^2 + (X_{th} + X_2\')^2}}, T_{\\max} = \\frac{3 V_{th}^2}{2 \\omega_s [R_{th} + \\sqrt{R_{th}^2 + (X_{th} + X_2\')^2}]}',
    keyTrap: '最大轉矩 T_max 與轉子電阻 R2 無關！增大轉子電阻只會讓產生最大轉矩的轉差率 s_max 變大。'
  },
  'emach-synchronous-generator-round': {
    id: 'emach-synchronous-generator-round',
    subject: '04',
    subjectName: '電機機械',
    name: '隱極同步發電機功角與相量圖',
    level: 3,
    prereqs: ['emach-single-phase-transformer'],
    coreFormula: '\\mathbf{E}_f = \\mathbf{V}_t + j I_a X_s, P = \\frac{E_f V_t}{X_s} \\sin\\delta',
    keyTrap: '滯後功因時 E_f > V_t (過激發提供虛功)；超前功因時 E_f < V_t (欠激發吸收虛功)。'
  },
  'emach-synchronous-salient-pole': {
    id: 'emach-synchronous-salient-pole',
    subject: '04',
    subjectName: '電機機械',
    name: '凸極同步電機雙反應理論 (Xd, Xq)',
    level: 4,
    prereqs: ['emach-synchronous-generator-round'],
    coreFormula: 'P = \\frac{E_f V_t}{X_d} \\sin\\delta + \\frac{V_t^2}{2} \\left(\\frac{1}{X_q} - \\frac{1}{X_d}\\right) \\sin 2\\delta',
    keyTrap: '第二項為磁阻轉矩 (Reluctance Torque)，即使激磁失去 (Ef=0) 仍可輸出磁阻功率。'
  },

  // -------------------------------------------------------------
  // 05. 電力系統 (Power Systems)
  // -------------------------------------------------------------
  'ps-per-unit': {
    id: 'ps-per-unit',
    subject: '05',
    subjectName: '電力系統',
    name: '標么值 (Per-Unit) 系統換算',
    level: 1,
    prereqs: [],
    coreFormula: 'Z_{\\text{base}} = \\frac{V_{\\text{base, L-L}}^2}{S_{\\text{base, 3\\phi}}}, Z_{\\text{pu, new}} = Z_{\\text{pu, old}} \\left(\\frac{V_{\\text{old}}}{V_{\\text{new}}}\\right)^2 \\left(\\frac{S_{\\text{new}}}{S_{\\text{old}}}\\right)',
    keyTrap: '三相標么公式中，基準阻抗為線電壓平方除以三相總容量！'
  },
  'ps-load-flow-admittance': {
    id: 'ps-load-flow-admittance',
    subject: '05',
    subjectName: '電力系統',
    name: '電力潮流與導納矩陣',
    level: 2,
    prereqs: ['ps-per-unit'],
    coreFormula: 'P_i = \\sum_j |V_i||V_j||Y_{ij}|\\cos(\\theta_i-\\theta_j-\\angle Y_{ij})',
    keyTrap: 'PV、PQ 與 swing 匯流排的已知量不同，反覆計算時不可混用。'
  },
  'ps-power-analysis': {
    id: 'ps-power-analysis',
    subject: '05',
    subjectName: '電力系統',
    name: '電力系統功率與相量分析',
    level: 1,
    prereqs: ['ps-per-unit'],
    coreFormula: 'S = P + jQ = \\sqrt{3}V_L I_L^*, \\quad \\cos\\phi = P/|S|',
    keyTrap: '三相功率使用線電壓與線電流時才乘以 \\sqrt{3}，相量角度需保持一致。'
  },
  'ps-economic-dispatch': {
    id: 'ps-economic-dispatch',
    subject: '05',
    subjectName: '電力系統',
    name: '經濟調度與發電協調方程式',
    level: 2,
    prereqs: ['ps-per-unit'],
    coreFormula: '\\frac{dC_1}{dP_1} = \\frac{dC_2}{dP_2} = \\lambda, \\quad \\sum_i P_i = P_D',
    keyTrap: '忽略損耗時以增量成本相等求解；有上下限時需檢查邊界機組。'
  },
  'ps-transmission-line-params': {
    id: 'ps-transmission-line-params',
    subject: '05',
    subjectName: '電力系統',
    name: '輸電線參數計算 (GMD/GMR)',
    level: 2,
    prereqs: [],
    coreFormula: 'L = 2 \\times 10^{-7} \\ln\\frac{\\text{GMD}}{\\text{GMR}_L} \\text{ (H/m)}, C = \\frac{2\\pi\\epsilon}{\\ln(\\text{GMD}/\\text{GMR}_C)} \\text{ (F/m)}',
    keyTrap: '電感 GMR 包含導體內部磁鏈因子 r\' = r e^{-1/4} = 0.7788r；電容 GMR 直接使用外半徑 r。'
  },
  'ps-transmission-line-models': {
    id: 'ps-transmission-line-models',
    subject: '05',
    subjectName: '電力系統',
    name: '輸電線路中長程模型 (ABCD 參數)',
    level: 3,
    prereqs: ['ps-transmission-line-params'],
    coreFormula: 'A = D = 1 + \\frac{Y Z}{2}, B = Z, C = Y \\left(1 + \\frac{Y Z}{4}\\right) \\text{ (中程 } \\pi \\text{ 模型)}',
    keyTrap: '輕載或空載時受電端電壓高於送電端電壓之現象稱為費蘭梯效應 (Ferranti Effect)。'
  },
  'ps-three-phase-fault': {
    id: 'ps-three-phase-fault',
    subject: '05',
    subjectName: '電力系統',
    name: '對稱三相短路計算',
    level: 2,
    prereqs: ['ps-per-unit'],
    coreFormula: 'I_f = \\frac{V_f}{Z_1} \\text{ (pu)}, S_{sc} = \\frac{S_{\\text{base}}}{Z_1} = \\sqrt{3} V_L I_f',
    keyTrap: '計算斷路器容量時，需明確區分次暫態電抗 X"d（瞬間）與暫態電抗 X\'d（啟斷）。'
  },
  'ps-symmetrical-components': {
    id: 'ps-symmetrical-components',
    subject: '05',
    subjectName: '電力系統',
    name: '對稱分量法 (正序、負序、零序網)',
    level: 3,
    prereqs: ['ps-per-unit'],
    coreFormula: '\\begin{bmatrix} I_{a0} \\\\ I_{a1} \\\\ I_{a2} \\end{bmatrix} = \\frac{1}{3} \\begin{bmatrix} 1 & 1 & 1 \\\\ 1 & a & a^2 \\\\ 1 & a^2 & a \\end{bmatrix} \\begin{bmatrix} I_a \\\\ I_b \\\\ I_c \\end{bmatrix}, a = e^{j 120^\\circ}',
    keyTrap: '整個系統中只有「正序網絡」含有發電機內部感應電動勢 E_a！'
  },
  'ps-unsymmetrical-faults': {
    id: 'ps-unsymmetrical-faults',
    subject: '05',
    subjectName: '電力系統',
    name: '不對稱故障分析 (SLG, L-L, 2LG)',
    level: 4,
    prereqs: ['ps-symmetrical-components'],
    coreFormula: 'I_f = \\frac{3 V_f}{Z_1 + Z_2 + Z_0 + 3 Z_n} \\text{ (SLG: 三序串聯)}, I_f = \\frac{\\sqrt{3} V_f}{Z_1 + Z_2} \\text{ (L-L: 正負反向並聯)}',
    keyTrap: '單相接地故障中性點接地阻抗需乘以 3 (即 3Z_n) 加入零序網。'
  },
  'ps-transient-stability-equal-area': {
    id: 'ps-transient-stability-equal-area',
    subject: '05',
    subjectName: '電力系統',
    name: '暫態穩定度與等面積準則 (Equal-Area)',
    level: 3,
    prereqs: ['ps-transmission-line-models'],
    coreFormula: 'M \\frac{d^2\\delta}{dt^2} = P_m - P_e, \\int_{\\delta_0}^{\\delta_{cr}} (P_m - P_{e\\text{, fault}}) d\\delta = \\int_{\\delta_{cr}}^{\\delta_{\\max}} (P_{e\\text{, post}} - P_m) d\\delta',
    keyTrap: '臨界清除角 \\delta_cr 滿足加速面積 A1 等於最大可減速面積 A2。'
  },
  'ps-system-protection-relay': {
    id: 'ps-system-protection-relay',
    subject: '05',
    subjectName: '電力系統',
    name: '距離保護電驛三段式規劃',
    level: 4,
    prereqs: ['ps-unsymmetrical-faults'],
    coreFormula: 'Z_{R1} = 0.8 \\sim 0.85 Z_L (0\\text{s}), Z_{R2} = Z_L + 0.5 Z_{\\text{next}} (0.3\\text{s}), Z_{R3} = Z_L + 1.2 Z_{\\text{next}} (0.8\\text{s})',
    keyTrap: 'Zone 1 嚴禁設置 100% 線路以避免超越 (Overreach)；Zone 2/3 需配合延時保護相鄰線路。'
  },
  'ps-state-estimation-wls': {
    id: 'ps-state-estimation-wls',
    subject: '05',
    subjectName: '電力系統',
    name: '電力系統狀態估計 (WLS 與壞資料檢測)',
    level: 5,
    prereqs: ['ps-three-phase-fault'],
    coreFormula: 'z = h(x) + e, \\hat{x} = (H^T R^{-1} H)^{-1} H^T R^{-1} z, J(\\hat{x}) = r^T R^{-1} r \\sim \\chi^2(m-n)',
    keyTrap: '殘差 J(x) 大於卡方分布臨界值時判定存在壞資料 (Bad Data)，透過標準化殘差法剔除。'
  },

  // -------------------------------------------------------------
  // 06. 工業配電 (Industrial Power Distribution)
  // -------------------------------------------------------------
  'dist-load-characteristics': {
    id: 'dist-load-characteristics',
    subject: '06',
    subjectName: '工業配電',
    name: '負載特性與需量因數/參差因數',
    level: 1,
    prereqs: [],
    coreFormula: 'f_D = \\frac{P_{\\max}}{\\text{Connected Load}}, \\text{DF} = \\frac{\\sum P_{\\max, i}}{P_{\\max, \\text{sys}}} \\ge 1.0, f_L = \\frac{P_{\\text{avg}}}{P_{\\max}}',
    keyTrap: '參差因數 (Diversity Factor) 恆大於或等於 1.0；需量因數與負載因數恆小於等於 1.0。'
  },
  'dist-grounding-system': {
    id: 'dist-grounding-system',
    subject: '06',
    subjectName: '工業配電',
    name: '系統接地與設備接地',
    level: 1,
    prereqs: [],
    coreFormula: 'R_g = V_g/I_g, \\quad E_{touch}, E_{step} \\le E_{allow}',
    keyTrap: '系統接地穩定電位，設備接地則提供故障電流回路，兩者目的不可混淆。'
  },
  'dist-lighting-design': {
    id: 'dist-lighting-design',
    subject: '06',
    subjectName: '工業配電',
    name: '照明設計與照度計算',
    level: 2,
    prereqs: ['dist-load-characteristics'],
    coreFormula: 'E = \\frac{N F CU MF}{A}',
    keyTrap: '照度計算須同時考慮照明率 CU、維護係數 MF 與工作面面積。'
  },
  'dist-distribution-equipment': {
    id: 'dist-distribution-equipment',
    subject: '06',
    subjectName: '工業配電',
    name: '配電變壓器與供電接線',
    level: 2,
    prereqs: ['dist-load-characteristics'],
    coreFormula: 'S_{V-V} = \\sqrt{3} S_{1\\phi}, \\quad V_{LL} = \\sqrt{3} V_\\phi',
    keyTrap: 'V-V（開三角）容量約為完整 Δ-Δ 組的 57.7%，且須核對相序與接線極性。'
  },
  'dist-motor-installation': {
    id: 'dist-motor-installation',
    subject: '06',
    subjectName: '工業配電',
    name: '電動機配線與啟動',
    level: 2,
    prereqs: ['dist-load-characteristics'],
    coreFormula: 'I_{start} = k I_{FL}, \\quad S_{motor} = \\frac{P_{out}}{\\eta \\cos\\phi}',
    keyTrap: '導線安培容量與啟動壓降需按連續運轉及啟動電流分別校核。'
  },
  'dist-voltage-drop': {
    id: 'dist-voltage-drop',
    subject: '06',
    subjectName: '工業配電',
    name: '配電線路電壓降與導線選用',
    level: 2,
    prereqs: ['dist-load-characteristics'],
    coreFormula: '\\Delta V_{3\\phi} = \\sqrt{3} I (R \\cos\\theta + X \\sin\\theta), \\%\\Delta V = \\frac{\\Delta V}{V_n} \\times 100\\%',
    keyTrap: '超前功因時 \\sin\\theta 為負值，線路電壓降可能為負（即受電端電壓升高）。'
  },
  'dist-power-factor-correction': {
    id: 'dist-power-factor-correction',
    subject: '06',
    subjectName: '工業配電',
    name: '功率因數改善與電容器組容量',
    level: 2,
    prereqs: [],
    coreFormula: 'Q_C = P (\\tan\\theta_1 - \\tan\\theta_2), I_{\\text{line, new}} = I_{\\text{line, old}} \\frac{\\cos\\theta_1}{\\cos\\theta_2}',
    keyTrap: '改善功因可釋放變壓器容量與減少線路損失：\\Delta P_{\\text{loss}} \\propto (1/\\cos\\theta)^2。'
  },
  'dist-short-circuit-capacity': {
    id: 'dist-short-circuit-capacity',
    subject: '06',
    subjectName: '工業配電',
    name: '短路容量計算 (MVA 法)',
    level: 3,
    prereqs: [],
    coreFormula: '\\frac{1}{\\text{MVA}_{sc, \\text{total}}} = \\frac{1}{\\text{MVA}_1} + \\frac{1}{\\text{MVA}_2} \\text{ (串聯)}, \\text{MVA}_{\\text{parallel}} = \\sum \\text{MVA}_k',
    keyTrap: 'MVA 法中元件「串聯」計算方式類似電阻並聯；「並聯」直接相加！'
  },
  'dist-protection-coordination': {
    id: 'dist-protection-coordination',
    subject: '06',
    subjectName: '工業配電',
    name: '過電流電驛與保護協調 (TCC 曲線)',
    level: 4,
    prereqs: ['dist-short-circuit-capacity'],
    coreFormula: 't = \\text{TMS} \\times \\left( \\frac{A}{(I/I_s)^p - 1} + B \\right) \\text{ (IEC 60255 標準反時限)}',
    keyTrap: '上下游保護電驛之協調時間間隔 (Coordination Time Interval, CTI) 通常需維持 0.3 ~ 0.4 秒。'
  },
  'dist-harmonics-mitigation': {
    id: 'dist-harmonics-mitigation',
    subject: '06',
    subjectName: '工業配電',
    name: '非線性負載諧波分析與抑制 (IEEE 519)',
    level: 4,
    prereqs: ['dist-power-factor-correction'],
    coreFormula: '\\text{THD}_V = \\frac{\\sqrt{\\sum_{h=2}^\\infty V_h^2}}{V_1} \\times 100\\%, X_L = \\frac{1}{h^2} X_C \\text{ (串聯電抗器防止諧振)}',
    keyTrap: '改善功因電容器串聯 6% 抗流圈可消除 5 次以上諧波，串聯 13% 抗流圈可消除 3 次諧波。'
  },
  'dist-arc-flash-ieee80': {
    id: 'dist-arc-flash-ieee80',
    subject: '06',
    subjectName: '工業配電',
    name: 'IEEE Std 80 變電所接地網跨步/接觸安全電壓',
    level: 5,
    prereqs: ['dist-short-circuit-capacity'],
    coreFormula: 'E_{\\text{touch}} = (1000 + 1.5 C_s \\rho_s) \\frac{0.116}{\\sqrt{t_s}}, E_{\\text{step}} = (1000 + 6.0 C_s \\rho_s) \\frac{0.116}{\\sqrt{t_s}}',
    keyTrap: '地表鋪設高電阻率碎石層 (\\rho_s ~ 3000 \\Omega\\cdot\\text{m}) 可大幅提升人體安全耐受電壓。'
  }
};

/**
 * Maps question content / keywords to matching DAG Node IDs.
 */
function mapQuestionToDagNodes(sid, topic, qBody) {
  const fullText = `${topic} ${qBody}`.toLowerCase();
  const matchedNodes = [];

  for (const [nodeId, node] of Object.entries(KNOWLEDGE_DAG)) {
    if (node.subject !== sid) continue;

    // Direct name or keywords matching
    const nameKeywords = node.name.toLowerCase().split(/[\s與、（）()\/]+/);
    const hit = nameKeywords.some(kw => kw.length >= 2 && fullText.includes(kw));

    // Specific domain rules
    if (nodeId === 'ct-thevenin-norton' && (fullText.includes('戴維寧') || fullText.includes('諾頓') || fullText.includes('等效電阻'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ct-first-order-rc-rl' && (fullText.includes('開關') || fullText.includes('t=0') || fullText.includes('暫態') || fullText.includes('三要素'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ct-second-order-rlc' && (fullText.includes('二階') || fullText.includes('欠阻尼') || fullText.includes('臨界阻尼'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ct-laplace-circuit' && (fullText.includes('拉氏') || fullText.includes('s域') || fullText.includes('laplace'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ct-three-phase' && (fullText.includes('三相') || fullText.includes('y-') || fullText.includes('delta') || fullText.includes('線電壓'))) matchedNodes.push(nodeId);
    else if (nodeId === 'el-diff-amp' && (fullText.includes('差動') || fullText.includes('cmrr') || fullText.includes('共模'))) matchedNodes.push(nodeId);
    else if (nodeId === 'el-pe-buck-boost' && (fullText.includes('buck') || fullText.includes('boost') || fullText.includes('轉換器') || fullText.includes('伏秒'))) matchedNodes.push(nodeId);
    else if (nodeId === 'em-svd-linear-systems' && (fullText.includes('svd') || fullText.includes('奇異值') || fullText.includes('零空間') || fullText.includes('偽逆'))) matchedNodes.push(nodeId);
    else if (nodeId === 'em-complex-cauchy-residue' && (fullText.includes('留數') || fullText.includes('複變') || fullText.includes('柯西') || fullText.includes('residue'))) matchedNodes.push(nodeId);
    else if (nodeId === 'emach-synchronous-salient-pole' && (fullText.includes('凸極') || fullText.includes('雙反應') || fullText.includes('xd') || fullText.includes('xq'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ps-unsymmetrical-faults' && (fullText.includes('接地故障') || fullText.includes('slg') || fullText.includes('線間短路') || fullText.includes('2lg') || fullText.includes('對稱分量'))) matchedNodes.push(nodeId);
    else if (nodeId === 'ps-transient-stability-equal-area' && (fullText.includes('等面積') || fullText.includes('搖擺') || fullText.includes('臨界清除') || fullText.includes('smib'))) matchedNodes.push(nodeId);
    else if (nodeId === 'dist-protection-coordination' && (fullText.includes('保護協調') || fullText.includes('tcc') || fullText.includes('反時限') || fullText.includes('電驛'))) matchedNodes.push(nodeId);
    else if (hit) {
      matchedNodes.push(nodeId);
    }
  }

  // Fallback to first level-1/2 node of subject if empty
  if (matchedNodes.length === 0) {
    const defaultNode = Object.keys(KNOWLEDGE_DAG).find(k => KNOWLEDGE_DAG[k].subject === sid);
    if (defaultNode) matchedNodes.push(defaultNode);
  }

  return [...new Set(matchedNodes)];
}

/**
 * Traces the complete prerequisite chain for a given node,
 * evaluating user mastery states.
 */
function tracePrerequisiteChain(targetNodeId) {
  const visited = new Set();
  const chain = [];

  function dfs(currId) {
    if (!KNOWLEDGE_DAG[currId] || visited.has(currId)) return;
    visited.add(currId);
    const node = KNOWLEDGE_DAG[currId];
    for (const pId of node.prereqs) {
      dfs(pId);
    }
    chain.push(node);
  }

  dfs(targetNodeId);
  return chain;
}

// Export for Node / Browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    KNOWLEDGE_DAG,
    mapQuestionToDagNodes,
    tracePrerequisiteChain
  };
}
