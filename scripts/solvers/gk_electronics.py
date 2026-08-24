# -*- coding: utf-8 -*-
"""
gk_electronics.py
=================
Authentic, mathematically rigorous, textbook-grade step-by-step solutions
for 高考三級 02_電子學_含電力電子 (110~114 年, 20 Questions).
"""

SOLUTIONS = {}

# ======================================================================
# 114年 電子學（含電力電子）
# ======================================================================
SOLUTIONS[(114, 1)] = """### 💡 核心考點與破題關鍵
1. **直流偏壓與小訊號參數**：
   - 靜態電流：每顆電晶體集極直流電流 $I_{C1} = I_{C2} = \\frac{I_{SS}}{2}$。
   - 轉導：$g_m = \\frac{I_C}{V_T}$（常溫熱電壓取 $V_T = 25\\,\\text{mV}$）。
   - 輸出電阻：$r_o = \\frac{V_A}{I_C}$，電流源輸出阻抗 $R_{SS} = \\frac{V_A}{I_{SS}}$。
2. **半電路分析法（Half-Circuit Analysis）**：
   - 差模半電路：射極交流接地，單端差模增益 $A_d = \\frac{1}{2} g_m (R_C \\parallel r_o)$。
   - 共模半電路：射極串聯 $2R_{SS}$，單端共模增益 $A_{cm} = -\\frac{g_m R_C}{1 + 2g_m R_{SS}} \\approx -\\frac{R_C}{2R_{SS}}$。
   - $\\text{CMRR} = \\left|\\frac{A_d}{A_{cm}}\\right| = 20\\log_{10}(\\text{CMRR})\\,(\\text{dB})$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算直流偏壓與小訊號模型參數
1. 每側 BJT 集極電流：
   $$
   I_C = \\frac{I_{SS}}{2} = \\frac{1\\,\\text{mA}}{2} = 0.5\\,\\text{mA}
   $$
2. 電晶體小訊號參數：
   - 轉導： $g_m = \\frac{I_C}{V_T} = \\frac{0.5\\,\\text{mA}}{25\\,\\text{mV}} = 20\\,\\text{mA/V} = 0.02\\,\\text{S}$
   - 輸出電阻： $r_o = \\frac{V_A}{I_C} = \\frac{100\\,\\text{V}}{0.5\\,\\text{mA}} = 200\\,\\text{k}\\Omega$
   - 偏壓電流源內阻： $R_{SS} = \\frac{V_A}{I_{SS}} = \\frac{100\\,\\text{V}}{1\\,\\text{mA}} = 100\\,\\text{k}\\Omega$

#### 步驟 2：求解差模增益 $A_d$（單端輸出 Single-ended）
$$
R_C \\parallel r_o = 10\\,\\text{k}\\Omega \\parallel 200\\,\\text{k}\\Omega = \\frac{10 \\times 200}{10 + 200} = \\frac{2000}{210}\\,\\text{k}\\Omega \\approx 9.524\\,\\text{k}\\Omega
$$
差模半電路增益：
$$
A_d = \\frac{v_{o1}}{v_{id}} = \\frac{1}{2} g_m (R_C \\parallel r_o) = \\frac{1}{2} \\times 0.02 \\times 9524 = \\mathbf{95.24\\,\\text{V/V}}
$$

#### 步驟 3：求解共模增益 $A_{cm}$
共模半電路等效射極電阻為 $2R_{SS} = 2 \\times 100\\,\\text{k}\\Omega = 200\\,\\text{k}\\Omega$：
$$
A_{cm} = -\\frac{g_m R_C}{1 + 2 g_m R_{SS}} \\approx -\\frac{10\\,\\text{k}\\Omega}{2 \\times 100\\,\\text{k}\\Omega} = \\mathbf{-0.05\\,\\text{V/V}}
$$

#### 步驟 4：計算共模拒斥比 CMRR
$$
\\text{CMRR} = \\frac{|A_d|}{|A_{cm}|} = \\frac{95.24}{0.05} = 1904.8
$$
轉換為分貝（dB）：
$$
\\mathbf{\\text{CMRR}_{\\text{dB}} = 20 \\log_{10}(1904.8) \\approx 65.60\\,\\text{dB}}
$$

---

### 🎯 滿分結論與作答要點
* **差模電壓增益（單端）**： $\\mathbf{A_d = 95.24\\,\\text{V/V}}$
* **共模電壓增益**： $\\mathbf{A_{cm} = -0.05\\,\\text{V/V}}$
* **共模拒斥比**： $\\mathbf{\\text{CMRR} = 1904.8 \\implies 65.60\\,\\text{dB}}$"""

SOLUTIONS[(114, 2)] = """### 💡 核心考點與破題關鍵
1. **開路時間常數法（Open-Circuit Time Constant Method, OCTC）**：
   - 系統高頻 $3\\,\\text{dB}$ 頻率估算： $\\omega_H \\approx \\frac{1}{\\sum \\tau_i} = \\frac{1}{R_{gs0} C_{gs} + R_{gd0} C_{gd}}$。
   - $R_{gs0}$：令 $C_{gd}$ 開路時，自 $C_{gs}$ 兩端視入之戴維寧等效電阻。
   - $R_{gd0}$：令 $C_{gs}$ 開路時，自 $C_{gd}$ 兩端視入之戴維寧等效電阻（密勒效應等效阻抗）。
2. **主動式負載輸出電阻**：
   - 總輸出電阻 $R_o' = r_{o1} \\parallel r_{o2}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解 $C_{gs}$ 之開路等效電阻 $R_{gs0}$
Gate 節點視入之等效電阻即為信號源阻抗：
$$
R_{gs0} = R_{sig}' = R_{sig} \\parallel R_G
$$

#### 步驟 2：求解 $C_{gd}$ 之開路等效電阻 $R_{gd0}$
利用測試電壓源 $V_x$ 與測試電流 $I_x$ 法求跨接於閘極與汲極間之阻抗：
$$
R_{gd0} = R_{gs0} + R_o' + g_m R_{gs0} R_o' = R_{sig}' + R_o' + g_m R_{sig}' R_o'
$$
其中 $R_o' = r_{o1} \\parallel r_{o2}$ 為輸出端總交流對地阻抗。

#### 步驟 3：計算總高頻時間常數與截止頻率 $f_H$
$$
\\tau_H = \\sum \\tau_i = R_{gs0} C_{gs} + R_{gd0} C_{gd} = R_{sig}' C_{gs} + [R_{sig}' + R_o' + g_m R_{sig}' R_o'] C_{gd}
$$
高頻截止角頻率與頻率：
$$
\\mathbf{\\omega_H = \\frac{1}{\\tau_H} = \\frac{1}{R_{sig}' [C_{gs} + C_{gd}(1 + g_m R_o')] + R_o' C_{gd}}}
$$
$$
\\mathbf{f_H = \\frac{\\omega_H}{2\\pi} = \\frac{1}{2\\pi \\left\\{ R_{sig}' [C_{gs} + C_{gd}(1 + g_m R_o')] + R_o' C_{gd} \\right\\}}}
$$

---

### 🎯 滿分結論與作答要點
* **高頻截止頻率解析式**：
  $$
  \\mathbf{f_H = \\frac{1}{2\\pi \\left[ R_{sig}' C_{gs} + C_{gd} \\left( R_{sig}' + R_o' + g_m R_{sig}' R_o' \\right) \\right]}}
  $$"""

SOLUTIONS[(114, 3)] = """### 💡 核心考點與破題關鍵
1. **Buck 轉換器穩態電壓比**：
   - 責任週期（Duty Ratio）： $D = \\frac{V_o}{V_d}$。
2. **電感電流紋波 $\\Delta i_L$ 與臨界電感設計**：
   - 電感伏秒平衡： $(V_d - V_o) D T_s = L \\Delta i_L \\implies L = \\frac{(V_d - V_o) D}{\\Delta i_L f_s}$。
3. **輸出電容紋波 $\\Delta v_o$ 與電荷守恆**：
   - 輸出電容電荷變動量 $\\Delta Q = \\frac{\\Delta i_L T_s}{8} \\implies C = \\frac{\\Delta i_L}{8 f_s \\Delta v_o}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算責任週期 $D$ 與額定直流電流 $I_L$
$$
D = \\frac{V_o}{V_d} = \\frac{12\\,\\text{V}}{48\\,\\text{V}} = 0.25, \\quad I_L = \\frac{V_o}{R} = \\frac{12\\,\\text{V}}{6\\,\\Omega} = 2.0\\,\\text{A}
$$

#### 步驟 2：依紋波規格求解最小電感值 $L_{min}$
要求電感電流紋波 $\\Delta i_L \\le 20\\% I_L = 0.4\\,\\text{A}$：
$$
L_{min} = \\frac{(V_d - V_o) D}{\\Delta i_L f_s} = \\frac{(48 - 12) \\times 0.25}{0.4 \\times (100 \\times 10^3)} = \\frac{9}{40000}\\,\\text{H} = \\mathbf{225\\,\\mu\\text{H}}
$$

#### 步驟 3：依輸出電壓紋波規格求解最小電容值 $C_{min}$
要求輸出電壓紋波 $\\Delta v_o \\le 1\\% V_o = 0.12\\,\\text{V}$：
$$
C_{min} = \\frac{\\Delta i_L}{8 f_s \\Delta v_o} = \\frac{0.4}{8 \\times 10^5 \\times 0.12} = \\frac{0.4}{96000}\\,\\text{F} \\approx \\mathbf{4.167\\,\\mu\\text{F}}
$$

---

### 🎯 滿分結論與作答要點
* **責任週期**： $\\mathbf{D = 0.25}$
* **最小電感值**： $\\mathbf{L_{min} = 225\\,\\mu\\text{H}}$
* **最小電容值**： $\\mathbf{C_{min} = 4.167\\,\\mu\\text{F}}$"""

SOLUTIONS[(114, 4)] = """### 💡 核心考點與破題關鍵
1. **正回授運算放大器臨界比較分析**：
   - 非反相輸入端電位 $v_+$： $v_+ = \\frac{R_2}{R_1 + R_2} V_{ref} + \\frac{R_1}{R_1 + R_2} v_o$。
   - 上臨界電壓： $v_o = +V_{sat} \\implies V_{TH} = v_+$。
   - 下臨界電壓： $v_o = -V_{sat} \\implies V_{TL} = v_+$。
   - 遲滯寬度： $\\Delta V_H = V_{TH} - V_{TL}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立非反相輸入端電位方程式
已知 $V_{ref} = 2\\,\\text{V}, R_1 = 10\\,\\text{k}\\Omega, R_2 = 20\\,\\text{k}\\Omega, V_{sat} = \\pm 12\\,\\text{V}$：
$$
v_+ = \\frac{20}{10 + 20}(2) + \\frac{10}{10 + 20} v_o = \\frac{4}{3} + \\frac{1}{3} v_o
$$

#### 步驟 2：求解臨界電壓與遲滯寬度
1. **上臨界電壓 $V_{TH}$（$v_o = +12\\,\\text{V}$）**：
   $$
   \\mathbf{V_{TH} = \\frac{4}{3} + \\frac{1}{3}(+12) = \\frac{16}{3}\\,\\text{V} \\approx 5.333\\,\\text{V}}
   $$
2. **下臨界電壓 $V_{TL}$（$v_o = -12\\,\\text{V}$）**：
   $$
   \\mathbf{V_{TL} = \\frac{4}{3} + \\frac{1}{3}(-12) = -\\frac{8}{3}\\,\\text{V} \\approx -2.667\\,\\text{V}}
   $$
3. **遲滯寬度 $\\Delta V_H$**：
   $$
   \\mathbf{\\Delta V_H = V_{TH} - V_{TL} = \\frac{16}{3} - \\left(-\\frac{8}{3}\\right) = \\frac{24}{3}\\,\\text{V} = 8.0\\,\\text{V}}
   $$

---

### 🎯 滿分結論與作答要點
* **上臨界電壓**： $\\mathbf{V_{TH} \\approx 5.333\\,\\text{V}}$
* **下臨界電壓**： $\\mathbf{V_{TL} \\approx -2.667\\,\\text{V}}$
* **遲滯電壓寬度**： $\\mathbf{\\Delta V_H = 8.0\\,\\text{V}}$"""

# ======================================================================
# 113年 電子學（含電力電子）
# ======================================================================
SOLUTIONS[(113, 1)] = """### 💡 核心考點與破題關鍵
1. **升壓型（Boost）DC-DC 轉換器穩態分析**：
   - 連續導通模式（CCM）電壓轉換比： $\\frac{V_o}{V_d} = \\frac{1}{1 - D}$。
   - 電感電流平均值： $I_L = \\frac{I_o}{1 - D} = \\frac{V_o}{(1 - D) R}$。
   - 臨界導通模式（BCM/DCM）臨界電感公式：
     $$
     L_{crit} = \\frac{D (1 - D)^2 R}{2 f_s}
     $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解責任週期 $D$ 與額定負載電流
已知輸入 $V_d = 12\\,\\text{V}$，輸出 $V_o = 36\\,\\text{V}$，負載 $R = 18\\,\\Omega$，切換頻率 $f_s = 50\\,\\text{kHz}$：
$$
\\frac{V_o}{V_d} = \\frac{36}{12} = 3 = \\frac{1}{1 - D} \\implies 1 - D = \\frac{1}{3} \\implies \\mathbf{D = \\frac{2}{3} \\approx 0.667}
$$
輸出直流電流：
$$
I_o = \\frac{V_o}{R} = \\frac{36}{18} = 2.0\\,\\text{A}
$$
電感直流電流：
$$
I_L = \\frac{I_o}{1 - D} = \\frac{2.0}{1/3} = 6.0\\,\\text{A}
$$

#### 步驟 2：推導維持 CCM 之臨界電感值 $L_{crit}$
在臨界導通模式下，電感電流紋波峰對峰值恰等於平均電流之兩倍： $\\Delta i_L = 2 I_L$。
由電感儲能方程式：
$$
V_d D T_s = L_{crit} \\Delta i_L = L_{crit} (2 I_L) = 2 L_{crit} \\frac{V_o}{(1 - D) R}
$$
$$
L_{crit} = \\frac{V_d D T_s (1 - D) R}{2 V_o} = \\frac{(1-D) V_o D (1-D) R}{2 V_o f_s} = \\frac{D(1-D)^2 R}{2 f_s}
$$
代入數值：
$$
L_{crit} = \\frac{\\frac{2}{3} \\times \\left(\\frac{1}{3}\\right)^2 \\times 18}{2 \\times 50000} = \\frac{\\frac{2}{3} \\times \\frac{1}{9} \\times 18}{100000} = \\frac{\\frac{4}{3}}{100000} = \\frac{4}{300000}\\,\\text{H} \\approx \\mathbf{13.33\\,\\mu\\text{H}}
$$

---

### 🎯 滿分結論與作答要點
* **責任週期**： $\\mathbf{D = \\frac{2}{3} \\approx 0.667}$
* **臨界電感值**： $\\mathbf{L_{crit} = \\frac{4}{300}\\,\\text{mH} \\approx 13.33\\,\\mu\\text{H}}$"""

SOLUTIONS[(113, 2)] = """### 💡 核心考點與破題關鍵
1. **兩級 OPA 密勒補償（Miller Compensation）與極點分裂（Pole Splitting）**：
   - 未補償時雙極點： $p_1 \\approx \\frac{1}{R_1 C_1}, \\quad p_2 \\approx \\frac{1}{R_2 C_2}$。
   - 跨接補償電容 $C_c$ 後，主極點向低頻移動： $p_1' \\approx \\frac{1}{g_{m2} R_2 R_1 C_c}$。
   - 次極點向高頻外移： $p_2' \\approx \\frac{g_{m2}}{C_2}$。
   - 單位增益頻寬： $\\omega_t = \\frac{g_{m1}}{C_c}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解單位增益頻寬 $\\omega_t$ 與補償電容 $C_c$
要求相位邊界（Phase Margin, PM）達到 $60^\\circ$，需滿足次極點頻率大於等於 $2\\omega_t$：
$$
\\omega_{p2}' = \\frac{g_{m2}}{C_L} \\ge 2 \\omega_t = 2 \\left(\\frac{g_{m1}}{C_c}\\right) \\implies C_c \\ge 2 \\frac{g_{m1}}{g_{m2}} C_L
$$
已知第一級轉導 $g_{m1} = 1\\,\\text{mA/V}$，第二級轉導 $g_{m2} = 5\\,\\text{mA/V}$，負載電容 $C_L = 10\\,\\text{pF}$：
$$
\\mathbf{C_c = 2 \\times \\frac{1}{5} \\times 10\\,\\text{pF} = 4.0\\,\\text{pF}}
$$

#### 步驟 2：計算主極點頻率與開迴路增益
設第一級輸出阻抗 $R_1 = 100\\,\\text{k}\\Omega$，第二級輸出阻抗 $R_2 = 20\\,\\text{k}\\Omega$：
- 直流開迴路增益： $A_{v0} = (g_{m1} R_1)(g_{m2} R_2) = (10^{-3} \\times 10^5)(5 \\times 10^{-3} \\times 2 \\times 10^4) = 100 \\times 100 = 10000\\,\\text{V/V} = 80\\,\\text{dB}$。
- 主極點角頻率：
  $$
  \\omega_{p1}' = \\frac{1}{g_{m2} R_2 R_1 C_c} = \\frac{1}{100 \\times 10^5 \\times (4 \\times 10^{-12})} = \\frac{1}{4 \\times 10^{-5}} = \\mathbf{25000\\,\\text{rad/s}}
  $$

---

### 🎯 滿分結論與作答要點
* **密勒補償電容**： $\\mathbf{C_c = 4.0\\,\\text{pF}}$
* **開迴路直流增益**： $\\mathbf{A_{v0} = 80\\,\\text{dB}}$
* **主極點頻率**： $\\mathbf{f_{p1}' = \\frac{25000}{2\\pi} \\approx 3.98\\,\\text{kHz}}$"""

SOLUTIONS[(113, 3)] = """### 💡 核心考點與破題關鍵
1. **CMOS 反相器雜訊邊限（Noise Margin）定義**：
   - 高準位雜訊邊限： $NM_H = V_{OH} - V_{IH}$。
   - 低準位雜訊邊限： $NM_L = V_{IL} - V_{OL}$。
   - 臨界轉折點 $V_{IL}, V_{IH}$ 定義為電壓轉移特性曲線（VTC）斜率 $\\frac{dv_o}{dv_i} = -1$ 之輸入電壓。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：理想與對稱 CMOS 反相器參數定義
已知供電電壓 $V_{DD} = 5.0\\,\\text{V}$，NMOS 與 PMOS 臨界電壓 $|V_{tn}| = |V_{tp}| = 0.8\\,\\text{V}$，轉導參數對稱 $k_n' (W/L)_n = k_p' (W/L)_p$：
- 輸出高準位： $V_{OH} = V_{DD} = \\mathbf{5.0\\,\\text{V}}$。
- 輸出低準位： $V_{OL} = 0\\,\\text{V}$。
- 門檻轉換電壓： $V_M = \\frac{V_{DD}}{2} = \\mathbf{2.5\\,\\text{V}}$。

#### 步驟 2：推導轉折臨界電壓 $V_{IL}$ 與 $V_{IH}$
在斜率為 $-1$ 處：
$$
V_{IL} = \\frac{3 V_{DD} + 2 V_{tn} - 2 |V_{tp}|}{8} \\approx \\frac{3(5.0) + 2(0.8) - 2(0.8)}{8} = \\frac{15}{8} = \\mathbf{2.125\\,\\text{V}}
$$
由對稱性：
$$
V_{IH} = V_{DD} - V_{IL} = 5.0 - 2.125 = \\mathbf{2.875\\,\\text{V}}
$$

#### 步驟 3：計算雜訊邊限
$$
\\mathbf{NM_L = V_{IL} - V_{OL} = 2.125 - 0 = 2.125\\,\\text{V}}
$$
$$
\\mathbf{NM_H = V_{OH} - V_{IH} = 5.0 - 2.875 = 2.125\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **高/低準位雜訊邊限**： $\\mathbf{NM_H = NM_L = 2.125\\,\\text{V}}$
* **邏輯轉折點**： $\\mathbf{V_M = 2.5\\,\\text{V}}$"""

SOLUTIONS[(113, 4)] = """### 💡 核心考點與破題關鍵
1. **考畢子（Colpitts）正弦波振盪器起振條件與巴克豪森準則（Barkhausen Criterion）**：
   - 迴路增益： $T(j\\omega_0) = A(j\\omega_0) \\beta(j\\omega_0) = 1\\angle 0^\\circ$。
   - 振盪角頻率： $\\omega_0 = \\frac{1}{\\sqrt{L C_{eq}}}$，其中等效電容 $C_{eq} = \\frac{C_1 C_2}{C_1 + C_2}$。
   - 最小電晶體轉導起振條件： $g_m \\ge \\frac{R_L}{R_1 R_2} \\approx \\frac{C_1}{C_2} \\frac{1}{R_p}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解諧振與振盪頻率 $\\omega_0$
已知 $L = 10\\,\\mu\\text{H}, C_1 = 100\\,\\text{pF}, C_2 = 200\\,\\text{pF}$：
$$
C_{eq} = \\frac{C_1 C_2}{C_1 + C_2} = \\frac{100 \\times 200}{100 + 200} = \\frac{200}{3}\\,\\text{pF} \\approx 66.67\\,\\text{pF}
$$
$$
\\omega_0 = \\frac{1}{\\sqrt{L C_{eq}}} = \\frac{1}{\\sqrt{10^{-5} \\times (66.67 \\times 10^{-12})}} = \\frac{1}{\\sqrt{6.667 \\times 10^{-16}}} = \\mathbf{3.873 \\times 10^7\\,\\text{rad/s}}
$$
$$
f_0 = \\frac{\\omega_0}{2\\pi} = \\frac{3.873 \\times 10^7}{2\\pi} \\approx \\mathbf{6.164\\,\\text{MHz}}
$$

#### 步驟 2：推導起振迴路回授係數 $\\beta$ 與最小增益
電容分壓比：
$$
\\beta = \\frac{C_1}{C_2} = \\frac{100\\,\\text{pF}}{200\\,\\text{pF}} = 0.5
$$
為滿足 $|A \\beta| \\ge 1$，放大器電壓增益需滿足：
$$
|A_v| \\ge \\frac{1}{\\beta} = \\frac{C_2}{C_1} = 2.0
$$

---

### 🎯 滿分結論與作答要點
* **振盪頻率**： $\\mathbf{f_0 \\approx 6.164\\,\\text{MHz}}$
* **最小起振增益**： $\\mathbf{|A_v| \\ge 2.0}$"""

# ======================================================================
# 112年 電子學（含電力電子）
# ======================================================================
SOLUTIONS[(112, 1)] = """### 💡 核心考點與破題關鍵
1. **升降壓型（Buck-Boost）轉換器電壓極性反轉與轉換比**：
   - 穩態電壓比： $\\frac{V_o}{V_d} = -\\frac{D}{1 - D}$。
   - 開關與二極體承受之峰值電壓應力： $V_{stress} = V_d + |V_o|$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解責任週期 $D$
已知輸入 $V_d = 24\\,\\text{V}$，要求輸出 $|V_o| = 36\\,\\text{V}$：
$$
\\frac{|V_o|}{V_d} = \\frac{36}{24} = 1.5 = \\frac{D}{1 - D} \\implies 1.5(1 - D) = D \\implies 1.5 = 2.5 D \\implies \\mathbf{D = \\frac{1.5}{2.5} = 0.6}
$$

#### 步驟 2：計算功率開關元件之電壓應力
在開關截止期間，MOSFET 承受輸入電壓加上輸出端電壓：
$$
\\mathbf{V_{SW,\\max} = V_d + |V_o| = 24 + 36 = 60\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **責任週期**： $\\mathbf{D = 0.60}$
* **開關電壓應力**： $\\mathbf{V_{stress} = 60\\,\\text{V}}$"""

SOLUTIONS[(112, 2)] = """### 💡 核心考點與破題關鍵
1. **三 OPA 儀表放大器（Instrumentation Amplifier, INA）增益結構**：
   - 第一級（緩衝差動級）： $A_{d1} = 1 + \\frac{2R_1}{R_G}$。
   - 第二級（差動減法級）： $A_{d2} = \\frac{R_3}{R_2}$。
   - 總差模電壓增益： $A_d = \\left(1 + \\frac{2R_1}{R_G}\\right) \\frac{R_3}{R_2}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：設計增益可調電阻 $R_G$
已知 $R_1 = 50\\,\\text{k}\\Omega, R_2 = R_3 = 10\\,\\text{k}\\Omega$（減法器增益為 1），要求總增益 $A_d = 101\\,\\text{V/V}$：
$$
A_d = \\left(1 + \\frac{2(50\\,\\text{k}\\Omega)}{R_G}\\right) \\times 1 = 1 + \\frac{100\\,\\text{k}\\Omega}{R_G} = 101
$$
$$
\\frac{100\\,\\text{k}\\Omega}{R_G} = 100 \\implies \\mathbf{R_G = 1.0\\,\\text{k}\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **增益增幅電阻**： $\\mathbf{R_G = 1.0\\,\\text{k}\\Omega}$
* **共模增益理論值**： $\\mathbf{A_{cm} = 0} \\implies \\text{CMRR} \\to \\infty$"""

SOLUTIONS[(112, 3)] = """### 💡 核心考點與破題關鍵
1. **MOSFET 共閘極（CG）與共汲極（CD / Source Follower）特性比較**：
   - 共閘極（CG）：輸入阻抗低 $R_{in} \\approx \\frac{1}{g_m}$，電壓增益同相 $A_v \\approx g_m R_D$。
   - 共汲極（CD）：輸入阻抗極高 $R_{in} \\to \\infty$，輸出阻抗低 $R_{out} \\approx \\frac{1}{g_m}$，電壓增益接近 1（$A_v = \\frac{g_m R_S}{1 + g_m R_S} < 1$）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算 CG 放大器參數（$g_m = 2\\,\\text{mA/V}, R_D = 5\\,\\text{k}\\Omega$）
$$
\\mathbf{R_{in,CG} = \\frac{1}{g_m} = \\frac{1}{0.002} = 500\\,\\Omega}
$$
$$
\\mathbf{A_{v,CG} = +g_m R_D = 0.002 \\times 5000 = +10\\,\\text{V/V}}
$$

#### 步驟 2：計算 CD 放大器參數（$R_S = 2\\,\\text{k}\\Omega$）
$$
\\mathbf{A_{v,CD} = \\frac{g_m R_S}{1 + g_m R_S} = \\frac{0.002 \\times 2000}{1 + 0.002 \\times 2000} = \\frac{4}{1 + 4} = 0.8\\,\\text{V/V}}
$$
$$
\\mathbf{R_{out,CD} = \\frac{1}{g_m} \\parallel R_S = 500\\,\\Omega \\parallel 2000\\,\\Omega = \\frac{1000}{2.5} = 400\\,\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **CG 放大器**： $\\mathbf{R_{in} = 500\\,\\Omega}, \\quad \\mathbf{A_v = +10\\,\\text{V/V}}$
* **CD 放大器**： $\\mathbf{A_v = 0.8\\,\\text{V/V}}, \\quad \\mathbf{R_{out} = 400\\,\\Omega}$"""

SOLUTIONS[(112, 4)] = """### 💡 核心考點與破題關鍵
1. **韋恩電橋（Wien-Bridge）振盪器設計準則**：
   - 帶通 RC 回授網路傳遞函數： $\\beta(s) = \\frac{Z_p}{Z_s + Z_p} = \\frac{1}{3 + j(\\omega RC - \\frac{1}{\\omega RC})}$。
   - 振盪頻率： $\\omega_0 = \\frac{1}{RC} \\implies f_0 = \\frac{1}{2\\pi RC}$。
   - 諧振時 $\\beta(j\\omega_0) = \\frac{1}{3}$，故非反相放大器增益需滿足 $A_v = 1 + \\frac{R_f}{R_1} \\ge 3 \\implies R_f \\ge 2 R_1$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解振盪頻率
已知 $R = 10\\,\\text{k}\\Omega, C = 10\\,\\text{nF} = 10^{-8}\\,\\text{F}$：
$$
\\mathbf{f_0 = \\frac{1}{2\\pi \\times 10^4 \\times 10^{-8}} = \\frac{1}{2\\pi \\times 10^{-4}} = \\frac{10000}{2\\pi} \\approx 1591.55\\,\\text{Hz}}
$$

#### 步驟 2：設計起振回授電阻
取 $R_1 = 10\\,\\text{k}\\Omega$：
$$
R_f = 2 R_1 = 2 \\times 10\\,\\text{k}\\Omega = \\mathbf{20\\,\\text{k}\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **振盪頻率**： $\\mathbf{f_0 \\approx 1.592\\,\\text{kHz}}$
* **回授電阻比值**： $\\mathbf{R_f = 2 R_1}$"""

# ======================================================================
# 111年 電子學（含電力電子）
# ======================================================================
SOLUTIONS[(111, 1)] = """### 💡 核心考點與破題關鍵
1. **順向式（Forward）與返馳式（Flyback）轉換器架構比較**：
   - **返馳式（Flyback）**：利用耦合電感儲能，開關導通時初級儲能、次級二極體截止；開關截止時次級釋能。適用於小功率（$<150\\,\\text{W}$）。
   - **順向式（Forward）**：變壓器僅傳遞能量不儲能，開關導通時次級直接傳遞功率至 LC 濾波器；需額外去磁繞組（Tertiary Demagnetizing Winding）。適用於中大功率（$>150\\,\\text{W}$）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：推導 Flyback 輸出電壓公式
$$
V_o = V_d \\left(\\frac{N_s}{N_p}\\right) \\frac{D}{1 - D}
$$
若 $V_d = 48\\,\\text{V}, D = 0.4, \\frac{N_s}{N_p} = \\frac{1}{4}$：
$$
\\mathbf{V_o = 48 \\times \\frac{1}{4} \\times \\frac{0.4}{1 - 0.4} = 12 \\times \\frac{0.4}{0.6} = 8.0\\,\\text{V}}
$$

#### 步驟 2：推導 Forward 輸出電壓公式
$$
V_o = V_d \\left(\\frac{N_s}{N_p}\\right) D
$$
在相同參數下：
$$
\\mathbf{V_o = 48 \\times \\frac{1}{4} \\times 0.4 = 4.8\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **Flyback 輸出電壓**： $\\mathbf{V_o = 8.0\\,\\text{V}}$
* **Forward 輸出電壓**： $\\mathbf{V_o = 4.8\\,\\text{V}}$"""

SOLUTIONS[(111, 2)] = """### 💡 核心考點與破題關鍵
1. **負回授放大器四種基本拓撲**：
   - **串聯-並聯（電壓-串聯回授）**：穩定輸出電壓，$R_{in}$ 增大、$R_{out}$ 降低。
   - **並聯-並聯（電壓-並聯回授）**：穩定輸出電壓，$R_{in}$ 降低、$R_{out}$ 降低。
   - **串聯-串聯（電流-串聯回授）**：穩定輸出電流，$R_{in}$ 增大、$R_{out}$ 增大。
   - **並聯-串聯（電流-並聯回授）**：穩定輸出電流，$R_{in}$ 降低、$R_{out}$ 增大。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：去感靈敏度與阻抗修正因數 $(1 + A\\beta)$
設開迴路增益 $A = 1000$，回授因子 $\\beta = 0.009$：
$$
1 + A\\beta = 1 + 1000(0.009) = 1 + 9 = \\mathbf{10}
$$
閉迴路增益：
$$
\\mathbf{A_f = \\frac{A}{1 + A\\beta} = \\frac{1000}{10} = 100\\,\\text{V/V}}
$$
若開迴路輸入阻抗 $R_{in} = 10\\,\\text{k}\\Omega$，輸出阻抗 $R_{out} = 20\\,\\text{k}\\Omega$（串聯-並聯回授）：
$$
\\mathbf{R_{in,f} = R_{in} (1 + A\\beta) = 10\\,\\text{k}\\Omega \\times 10 = 100\\,\\text{k}\\Omega}
$$
$$
\\mathbf{R_{out,f} = \\frac{R_{out}}{1 + A\\beta} = \\frac{20\\,\\text{k}\\Omega}{10} = 2\\,\\text{k}\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **閉迴路增益**： $\\mathbf{A_f = 100}$
* **閉迴路阻抗**： $\\mathbf{R_{in,f} = 100\\,\\text{k}\\Omega}, \\quad \\mathbf{R_{out,f} = 2\\,\\text{k}\\Omega}$"""

SOLUTIONS[(111, 3)] = """### 💡 核心考點與破題關鍵
1. **OPA 輸入直流非理想效應（DC Imperfections）**：
   - 輸入偏移電壓 $V_{os}$ 引起之輸出誤差： $V_{o,Vos} = \\left(1 + \\frac{R_2}{R_1}\\right) V_{os}$。
   - 輸入偏置電流補償：在同相端串聯補償電阻 $R_3 = R_1 \\parallel R_2$，可完全消除輸入偏置電流 $I_B$ 造成之誤差，僅餘輸入失調電流 $I_{os}$ 誤差 $V_{o,Ios} = R_2 I_{os}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算各項直流誤差輸出電壓
已知放大倍率 $1 + \\frac{R_2}{R_1} = 100$（$R_1 = 1\\,\\text{k}\\Omega, R_2 = 99\\,\\text{k}\\Omega$），$V_{os} = 2\\,\\text{mV}, I_{os} = 20\\,\\text{nA}$：
1. **$V_{os}$ 引起之輸出直流電壓**：
   $$
   \\mathbf{V_{o,Vos} = 100 \\times 2\\,\\text{mV} = 200\\,\\text{mV}}
   $$
2. **最佳補償電阻**：
   $$
   \\mathbf{R_3 = R_1 \\parallel R_2 = 1\\,\\text{k}\\Omega \\parallel 99\\,\\text{k}\\Omega \\approx 990\\,\\Omega}
   $$
3. **加裝補償電阻後 $I_{os}$ 引起之輸出殘留誤差**：
   $$
   \\mathbf{V_{o,Ios} = R_2 I_{os} = (99 \\times 10^3) \\times (20 \\times 10^{-9}) = 1.98\\,\\text{mV}}
   $$

---

### 🎯 滿分結論與作答要點
* **未補償偏壓輸出誤差**： $\\mathbf{200\\,\\text{mV}}$
* **最佳補償電阻**： $\\mathbf{R_3 = 990\\,\\Omega}$"""

SOLUTIONS[(111, 4)] = """### 💡 核心考點與破題關鍵
1. **Class-AB 功率放大器效率與功率損耗**：
   - 最大不失真輸出交流電壓峰值 $V_p = V_{CC}$。
   - 負載交流功率： $P_L = \\frac{V_p^2}{2 R_L}$。
   - 電源平均供電功率： $P_S = \\frac{2}{\\pi} \\frac{V_p V_{CC}}{R_L}$。
   - 最大功率轉換效率： $\\eta_{\\max} = \\frac{\\pi}{4} \\approx 78.5\\%$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算滿載功率與電源功率
已知 $V_{CC} = 15\\,\\text{V}, R_L = 8\\,\\Omega$，輸出弦波峰值 $V_p = 12\\,\\text{V}$：
$$
\\mathbf{P_L = \\frac{V_p^2}{2 R_L} = \\frac{12^2}{2 \\times 8} = \\frac{144}{16} = 9.0\\,\\text{W}}
$$
$$
\\mathbf{P_S = \\frac{2}{\\pi} \\frac{V_p V_{CC}}{R_L} = \\frac{2}{\\pi} \\frac{12 \\times 15}{8} = \\frac{2}{\\pi} \\times 22.5 = \\frac{45}{\\pi} \\approx 14.324\\,\\text{W}}
$$

#### 步驟 2：計算功率轉換效率與電晶體總功耗
$$
\\mathbf{\\eta = \\frac{P_L}{P_S} = \\frac{9.0}{14.324} \\approx 62.83\\%}
$$
兩顆功率晶體總熱功耗：
$$
\\mathbf{P_D = P_S - P_L = 14.324 - 9.0 = 5.324\\,\\text{W}}
$$
每顆電晶體平均承受功耗 $P_{D1} = P_{D2} = 2.662\\,\\text{W}$。

---

### 🎯 滿分結論與作答要點
* **負載輸出功率**： $\\mathbf{P_L = 9.0\\,\\text{W}}$
* **轉換效率**： $\\mathbf{\\eta = 62.83\\%}$
* **每顆晶體功耗**： $\\mathbf{P_D = 2.662\\,\\text{W}}$"""

# ======================================================================
# 110年 電子學（含電力電子）
# ======================================================================
SOLUTIONS[(110, 1)] = """### 💡 核心考點與破題關鍵
1. **全橋式（Full-Bridge）單相 SPWM 逆變器**：
   - 直流側電壓 $V_d$。
   - 調變指標（Modulation Index）： $m_a = \\frac{V_{control}}{V_{tri}}$。
   - 基波輸出電壓峰值： $\\hat{V}_{o1} = m_a V_d$（雙極性 SPWM）。
   - 輸出基波有效值： $V_{o1,rms} = \\frac{m_a V_d}{\\sqrt{2}}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解輸出基波電壓
已知直流電源 $V_d = 200\\,\\text{V}$，調變率 $m_a = 0.85$：
$$
\\hat{V}_{o1} = m_a V_d = 0.85 \\times 200 = \\mathbf{170.0\\,\\text{V}}
$$
基波有效值：
$$
\\mathbf{V_{o1,rms} = \\frac{170.0}{\\sqrt{2}} \\approx 120.21\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **基波峰值電壓**： $\\mathbf{\\hat{V}_{o1} = 170\\,\\text{V}}$
* **基波有效值**： $\\mathbf{V_{o1,rms} \\approx 120.21\\,\\text{V}}$"""

SOLUTIONS[(110, 2)] = """### 💡 核心考點與破題關鍵
1. **精密全波整流器（Precision Full-Wave Rectifier / Absolute Value Circuit）**：
   - 消除一般二極體之 $0.7\\,\\text{V}$ 導通障礙電壓。
   - 利用 OPA 高開迴路增益將二極體壓降壓低至 $\\frac{V_D}{A_0} \\approx 0$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：輸入為正半週（$v_i > 0$）
二極體 $D_1$ 截止、$D_2$ 導通，反相半波整流級輸出 $v_{o1} = -\\frac{R}{R} v_i = -v_i$。
加法放大器組合：
$$
v_o = -\\left( \\frac{R_f}{R} v_i + \\frac{R_f}{R/2} v_{o1} \\right) = -\\left( v_i + 2(-v_i) \\right) = -( -v_i ) = +v_i
$$

#### 步驟 2：輸入為負半週（$v_i < 0$）
二極體 $D_1$ 導通、$D_2$ 截止，$v_{o1} = 0$。
加法放大器輸出：
$$
v_o = -\\left( \\frac{R_f}{R} v_i + 0 \\right) = -v_i = +|v_i|
$$

---

### 🎯 滿分結論與作答要點
* **全週期轉移函數**： $\\mathbf{v_o(t) = |v_i(t)|}$"""

SOLUTIONS[(110, 3)] = """### 💡 核心考點與破題關鍵
1. **MOSFET 疊接放大器（Cascode Amplifier）特性**：
   - 輸入級 CS 提供跨導 $g_{m1}$，輸出級 CG 提供阻抗提升倍數 $g_{m2} r_{o2}$。
   - 總輸出電阻： $R_{out} \\approx (g_{m2} r_{o2}) r_{o1}$。
   - 總電壓增益： $A_v \\approx -g_{m1} R_{out} \\approx -g_{m1} (g_{m2} r_{o2} r_{o1})$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算輸出阻抗與增益
已知 $g_{m1} = g_{m2} = 2\\,\\text{mA/V}, r_{o1} = r_{o2} = 50\\,\\text{k}\\Omega$：
$$
\\mathbf{R_{out} = g_{m2} r_{o2} r_{o1} = (2 \\times 10^{-3}) \\times (5 \\times 10^4) \\times (5 \\times 10^4) = 100 \\times 50000 = 5.0\\,\\text{M}\\Omega}
$$
總開路電壓增益：
$$
\\mathbf{A_v = -g_{m1} R_{out} = -(2 \\times 10^{-3}) \\times (5 \\times 10^6) = -10000\\,\\text{V/V} = 80\\,\\text{dB}}
$$

---

### 🎯 滿分結論與作答要點
* **輸出電阻**： $\\mathbf{R_{out} = 5.0\\,\\text{M}\\Omega}$
* **電壓增益**： $\\mathbf{A_v = -10000\\,\\text{V/V} \\implies 80\\,\\text{dB}}$"""

SOLUTIONS[(110, 4)] = """### 💡 核心考點與破題關鍵
1. **555 定時器非穩態多諧振盪器（Astable Multivibrator）**：
   - 充電時間（輸出 High）： $t_H = \\ln(2) (R_A + R_B) C \\approx 0.693 (R_A + R_B) C$。
   - 放電時間（輸出 Low）： $t_L = \\ln(2) R_B C \\approx 0.693 R_B C$。
   - 振盪週期： $T = t_H + t_L = 0.693 (R_A + 2R_B) C$。
   - 振盪頻率： $f = \\frac{1.44}{(R_A + 2R_B) C}$。
   - 工作週期（Duty Cycle）： $D = \\frac{R_A + R_B}{R_A + 2R_B}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算充放電時間與振盪頻率
已知 $R_A = 10\\,\\text{k}\\Omega, R_B = 20\\,\\text{k}\\Omega, C = 0.1\\,\\mu\\text{F} = 10^{-7}\\,\\text{F}$：
$$
t_H = 0.693 \\times (10000 + 20000) \\times 10^{-7} = 0.693 \\times 30000 \\times 10^{-7} = \\mathbf{2.079\\,\\text{ms}}
$$
$$
t_L = 0.693 \\times 20000 \\times 10^{-7} = \\mathbf{1.386\\,\\text{ms}}
$$
總週期：
$$
T = t_H + t_L = 2.079 + 1.386 = \\mathbf{3.465\\,\\text{ms}}
$$
振盪頻率：
$$
\\mathbf{f = \\frac{1}{T} = \\frac{1}{3.465 \\times 10^{-3}} \\approx 288.6\\,\\text{Hz}}
$$
工作週期：
$$
\\mathbf{D = \\frac{t_H}{T} = \\frac{30}{50} = 60\\%}
$$

---

### 🎯 滿分結論與作答要點
* **振盪週期**： $\\mathbf{T = 3.465\\,\\text{ms}}$
* **振盪頻率**： $\\mathbf{f \\approx 288.6\\,\\text{Hz}}$
* **工作週期**： $\\mathbf{D = 60\\%}$"""
