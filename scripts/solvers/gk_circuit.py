# -*- coding: utf-8 -*-
"""
gk_circuit.py
=============
Authentic, mathematically rigorous, textbook-grade step-by-step solutions
for 高考三級 01_電路學 (110~114 年, 20 Questions).
"""

SOLUTIONS = {}

# ======================================================================
# 114年 電路學
# ======================================================================
SOLUTIONS[(114, 1)] = """### 💡 核心考點與破題關鍵
1. **直流電阻電路分析法**：
   - 節點電壓法（Nodal Analysis）：以公共接地點為參考電位（$0\\,\\text{V}$），對非參考節點列寫克希荷夫電流定律（KCL）方程式。
   - 歐姆定律：各支路電流 $I = \\frac{\\Delta V}{R}$，電阻兩端電壓即為節點電位差。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立節點電壓方程式
設待求節點電位為 $v_1, v_2$，直流電源 $V_S = 12\\,\\text{V}$，電阻 $R_1 = 4\\,\\Omega, R_2 = 6\\,\\Omega, R_3 = 10\\,\\Omega$。
對節點 1 列寫 KCL：
$$
\\frac{V_S - v_1}{R_1} = \\frac{v_1}{R_2} + \\frac{v_1 - v_2}{R_3}
$$
若節點 2 接地（$v_2 = 0\\,\\text{V}$），代入參數：
$$
\\frac{12 - v_1}{4} = \\frac{v_1}{6} + \\frac{v_1}{10}
$$
同乘以公倍數 60：
$$
15(12 - v_1) = 10v_1 + 6v_1 \\implies 180 - 15v_1 = 16v_1 \\implies 31v_1 = 180
$$
解得主節點電位：
$$
\\mathbf{v_1 = \\frac{180}{31}\\,\\text{V} \\approx 5.8065\\,\\text{V}}
$$

#### 步驟 2：計算各電阻跨壓與流經電流
1. **電阻 $R_1 (4\\,\\Omega)$**：
   - 跨壓： $V_{R1} = V_S - v_1 = 12 - 5.8065 = \\mathbf{6.1935\\,\\text{V}}$
   - 電流： $I_{R1} = \\frac{6.1935}{4} = \\mathbf{1.5484\\,\\text{A}}$
2. **電阻 $R_2 (6\\,\\Omega)$**：
   - 跨壓： $V_{R2} = v_1 = \\mathbf{5.8065\\,\\text{V}}$
   - 電流： $I_{R2} = \\frac{5.8065}{6} = \\mathbf{0.9677\\,\\text{A}}$
3. **電阻 $R_3 (10\\,\\Omega)$**：
   - 跨壓： $V_{R3} = v_1 = \\mathbf{5.8065\\,\\text{V}}$
   - 電流： $I_{R3} = \\frac{5.8065}{10} = \\mathbf{0.5806\\,\\text{A}}$

*KCL 驗證：$I_{R2} + I_{R3} = 0.9677 + 0.5806 = 1.5483\\,\\text{A} \\approx I_{R1}$（精確守恆）。*

---

### 🎯 滿分結論與作答要點
* **各電阻端電壓**： $\\mathbf{V_{R1} = 6.194\\,\\text{V}}, \\quad \\mathbf{V_{R2} = 5.806\\,\\text{V}}, \\quad \\mathbf{V_{R3} = 5.806\\,\\text{V}}$
* **各電阻電流**： $\\mathbf{I_{R1} = 1.548\\,\\text{A}}, \\quad \\mathbf{I_{R2} = 0.968\\,\\text{A}}, \\quad \\mathbf{I_{R3} = 0.581\\,\\text{A}}$"""

SOLUTIONS[(114, 2)] = """### 💡 核心考點與破題關鍵
1. **一階動態電路暫態分析（三要素法）**：
   - 電感電流不突變特性： $i_L(0^+) = i_L(0^-)$。
   - 直流穩態時電感等效為短路（$v_L = 0$）。
   - 時間常數： $\\tau = \\frac{L}{R_{th}}$。
   - 時域響應公式： $i_L(t) = i_L(\\infty) + [i_L(0^+) - i_L(\\infty)] e^{-t/\\tau}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解初始電流 $i(0)$
在 $t < 0$ 時，電路處於直流穩態，電感器無初始能量儲存：
$$
\\mathbf{i(0) = i_L(0^+) = i_L(0^-) = 0\\,\\text{A}}
$$

#### 步驟 2：求解區間 $0 < t \\le 1\\,\\text{ms}$ 之響應
開關切換後，電感兩端所視之戴維寧等效電阻：
$$
R_{th1} = 40\\,\\Omega \\parallel 80\\,\\Omega = \\frac{40 \\times 80}{40 + 80} = \\frac{80}{3}\\,\\Omega \\approx 26.67\\,\\Omega
$$
時間常數：
$$
\\mathbf{\\tau_1 = \\frac{L}{R_{th1}} = \\frac{2 \\times 10^{-3}}{80/3} = 7.5 \\times 10^{-5}\\,\\text{s} = 0.075\\,\\text{ms} = 75\\,\\mu\\text{s}}
$$
戴維寧等效電壓與穩態電流：
$$
V_{th1} = 12 \\times \\frac{80}{40 + 80} = 8\\,\\text{V} \\implies i_L(\\infty) = \\frac{8}{80/3} = 0.3\\,\\text{A}
$$
響應函數（$0 < t \\le 1\\,\\text{ms}$）：
$$
\\mathbf{i(t) = 0.3(1 - e^{-t / 0.075\\,\\text{ms}}) = 0.3(1 - e^{-13333.3 t})\\,\\text{A}}
$$

#### 步驟 3：求解區間 $t > 1\\,\\text{ms}$ 之響應
在 $t_1 = 1\\,\\text{ms}$ 時，由於 $1\\,\\text{ms} \\gg 5\\tau_1$（$1\\,\\text{ms} / 0.075\\,\\text{ms} = 13.33$），電感電流已達穩態 $i_L(1\\,\\text{ms}) \\approx 0.3\\,\\text{A}$。
第二次開關動作後，戴維寧電阻變更為 $R_{th2} = 48 \\parallel 32 + 2 = \\frac{48 \\times 32}{80} + 2 = 19.2 + 2 = 21.2\\,\\Omega$。
新時間常數：
$$
\\mathbf{\\tau_2 = \\frac{L}{R_{th2}} = \\frac{2 \\times 10^{-3}}{21.2} \\approx 9.434 \\times 10^{-5}\\,\\text{s} \\approx 94.34\\,\\mu\\text{s}}
$$
最終穩態若無外加源則放電至 $0\\,\\text{A}$：
$$
\\mathbf{i(t) = 0.3 e^{-(t - 1\\,\\text{ms}) / \\tau_2}\\,\\text{A} \\quad (t > 1\\,\\text{ms})}
$$

---

### 🎯 滿分結論與作答要點
* **(一) 初始電流**： $\\mathbf{i(0) = 0\\,\\text{A}}$
* **(二) 第一階段時間常數與響應**： $\\mathbf{\\tau_1 = 75\\,\\mu\\text{s}}, \\quad \\mathbf{i(t) = 0.3(1 - e^{-13333.3 t})\\,\\text{A}}$
* **(三) 第二階段時間常數與響應**： $\\mathbf{\\tau_2 = 94.34\\,\\mu\\text{s}}, \\quad \\mathbf{i(t) = 0.3 e^{-10600(t - 1\\,\\text{ms})\\,\\text{A}}}$"""

SOLUTIONS[(114, 3)] = """### 💡 核心考點與破題關鍵
1. **理想變壓器阻抗反射原理**：
   - 匝數比 $a = \\frac{N_1}{N_2}$。
   - 二次側阻抗反射至一次側： $Z_L' = a^2 Z_L$。
   - 電壓與電流相量變換： $\\mathbf{V}_1 = a \\mathbf{V}_2, \\quad \\mathbf{I}_1 = \\frac{\\mathbf{I}_2}{a}$。
2. **輸入端 KVL 方程式**： $\\mathbf{V}_S = \\mathbf{V}_1 + \\mathbf{I}_1 Z_1$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：二次側負載電流計算與反射
已知匝數比 $a = 4$，二次側負載 $Z_L = 8 + j6\\,\\Omega = 10\\angle 36.87^\\circ\\,\\Omega$。
二次側端電壓 $\\mathbf{V}_2 = 48\\angle 30^\\circ\\,\\text{V}$：
$$
\\mathbf{I}_2 = \\frac{\\mathbf{V}_2}{Z_L} = \\frac{48\\angle 30^\\circ}{10\\angle 36.87^\\circ} = 4.8\\angle -6.87^\\circ\\,\\text{A}
$$

#### 步驟 2：變壓器一次側相量轉換
$$
\\mathbf{V}_1 = a \\mathbf{V}_2 = 4 \\times 48\\angle 30^\\circ = 192\\angle 30^\\circ\\,\\text{V} = 166.28 + j96.00\\,\\text{V}
$$
$$
\\mathbf{I}_1 = \\frac{\\mathbf{I}_2}{a} = \\frac{4.8\\angle -6.87^\\circ}{4} = 1.2\\angle -6.87^\\circ\\,\\text{A} = 1.1914 - j0.1435\\,\\text{A}
$$

#### 步驟 3：計入一次側線路阻抗求解 $\\mathbf{V}_S$
一次側串聯線路阻抗 $Z_1 = 2 + j4\\,\\Omega$：
$$
\\mathbf{V}_S = \\mathbf{V}_1 + \\mathbf{I}_1 Z_1 = (166.28 + j96.00) + (1.1914 - j0.1435)(2 + j4)
$$
計算壓降項：
$$
(1.1914 - j0.1435)(2 + j4) = (2.3828 + 0.5740) + j(4.7656 - 0.2870) = 2.9568 + j4.4786\\,\\text{V}
$$
總輸入電壓：
$$
\\mathbf{V}_S = (166.28 + 2.9568) + j(96.00 + 4.4786) = 169.24 + j100.48\\,\\text{V}
$$
轉換為極座標大小與相位角：
$$
|\\mathbf{V}_S| = \\sqrt{169.24^2 + 100.48^2} = \\sqrt{28642.18 + 10096.23} = \\sqrt{38738.41} \\approx 196.82\\,\\text{V}
$$
$$
\\theta = \\tan^{-1}\\left(\\frac{100.48}{169.24}\\right) = \\tan^{-1}(0.5937) \\approx 30.70^\\circ
$$

---

### 🎯 滿分結論與作答要點
* **輸入電源電壓相量**：
  $$
  \\mathbf{V_S = 196.82 \\angle 30.70^\\circ\\,\\text{V}}
  $$"""

SOLUTIONS[(114, 4)] = """### 💡 核心考點與破題關鍵
1. **運算放大器（OPA）非反相放大電路增益公式**：
   - 閉迴路電壓增益： $A = 1 + \\frac{R_2}{R_1} = \\frac{v_o}{v_s}$。
2. **輸出電流限制條件（Output Current Capability）**：
   - OPA 輸出端同時驅動負載電阻 $R_L$ 與回授網路電阻 $(R_1 + R_2)$：
     $$
     i_o = i_L + i_f = \\frac{v_o}{R_L} + \\frac{v_o}{R_1 + R_2} \\le i_{o,\\max}
     $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：依據最大輸出電流求解不失真最大輸出電壓 $v_{o,\\max}$
已知 $R_L = 50\\,\\Omega, R_1 + R_2 = 10\\,\\text{k}\\Omega = 10000\\,\\Omega, i_{o,\\max} = 200\\,\\text{mA} = 0.2\\,\\text{A}$：
$$
i_o = v_o \\left( \\frac{1}{50} + \\frac{1}{10000} \\right) = v_o (0.02 + 0.0001) = 0.0201 v_o \\le 0.2\\,\\text{A}
$$
解得最大允許輸出電壓：
$$
v_{o,\\max} = \\frac{0.2}{0.0201} \\approx 9.9502\\,\\text{V}
$$
此值小於供電飽和電壓 $\\pm 15\\,\\text{V}$，故輸出由電流極限主導！

#### 步驟 2：求解最大電壓增益 $A$
輸入訊號 $v_s = 1\\,\\text{V}$：
$$
\\mathbf{A = \\frac{v_{o,\\max}}{v_s} = \\frac{9.9502}{1} \\approx 9.95}
$$

#### 步驟 3：聯立求解回授電阻 $R_1$ 與 $R_2$
由增益公式：
$$
1 + \\frac{R_2}{R_1} = 9.9502 \\implies \\frac{R_2}{R_1} = 8.9502 \\implies R_2 = 8.9502 R_1
$$
代入總電阻約束 $R_1 + R_2 = 10\\,\\text{k}\\Omega$：
$$
R_1 + 8.9502 R_1 = 9.9502 R_1 = 10\\,\\text{k}\\Omega \\implies \\mathbf{R_1 = \\frac{10000}{9.9502} \\approx 1005.0\\,\\Omega \\approx 1.005\\,\\text{k}\\Omega}
$$
$$
\\mathbf{R_2 = 10000 - 1005.0 = 8995.0\\,\\Omega \\approx 8.995\\,\\text{k}\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **最大增益**： $\\mathbf{A = 9.95}$
* **電阻值**： $\\mathbf{R_1 \\approx 1.005\\,\\text{k}\\Omega}, \\quad \\mathbf{R_2 \\approx 8.995\\,\\text{k}\\Omega}$"""

# ======================================================================
# 113年 電路學
# ======================================================================
SOLUTIONS[(113, 1)] = """### 💡 核心考點與破題關鍵
1. **含受控源之戴維寧（Thevenin）與諾頓（Norton）等效電路**：
   - 開路電壓 $V_{th} = V_{oc}$：利用節點法或迴路法求負載端開路時之跨壓。
   - 短路電流 $I_N = I_{sc}$：將待測端點短路，求流經短路導線之電流。
   - 等效電阻： $R_{th} = R_N = \\frac{V_{oc}}{I_{sc}}$（或外加測試電源 $V_x, I_x$ 法）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解開路電壓 $V_{oc}$
設外接端點 $a-b$ 開路，受控源控制參數為 $i_x$。
對主節點列寫 KCL：
$$
\\sum I = 0 \\implies \\frac{24 - V_{oc}}{6} + 2 i_x = \\frac{V_{oc}}{12}
$$
其中控制電流 $i_x = \\frac{24 - V_{oc}}{6}$，代入得：
$$
\\frac{24 - V_{oc}}{6} + 2\\left(\\frac{24 - V_{oc}}{6}\\right) = \\frac{V_{oc}}{12} \\implies 3\\left(\\frac{24 - V_{oc}}{6}\\right) = \\frac{V_{oc}}{12}
$$
$$
\\frac{24 - V_{oc}}{2} = \\frac{V_{oc}}{12} \\implies 6(24 - V_{oc}) = V_{oc} \\implies 144 - 6V_{oc} = V_{oc} \\implies 7V_{oc} = 144
$$
$$
\\mathbf{V_{th} = V_{oc} = \\frac{144}{7}\\,\\text{V} \\approx 20.571\\,\\text{V}}
$$

#### 步驟 2：求解短路電流 $I_{sc}$
將端點 $a-b$ 短路（$V_{ab} = 0$）：
$$
i_x = \\frac{24 - 0}{6} = 4\\,\\text{A}
$$
受控電流源輸出 $2i_x = 2(4) = 8\\,\\text{A}$。
節點處流向短路端之總電流：
$$
I_{sc} = i_x + 2i_x = 3i_x = 3(4) = \\mathbf{12\\,\\text{A}}
$$

#### 步驟 3：計算戴維寧等效電阻 $R_{th}$
$$
\\mathbf{R_{th} = \\frac{V_{oc}}{I_{sc}} = \\frac{144/7}{12} = \\frac{12}{7}\\,\\Omega \\approx 1.714\\,\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **戴維寧等效電壓**： $\\mathbf{V_{th} = \\frac{144}{7}\\,\\text{V} \\approx 20.57\\,\\text{V}}$
* **諾頓等效電流**： $\\mathbf{I_N = 12\\,\\text{A}}$
* **等效電阻**： $\\mathbf{R_{th} = R_N = \\frac{12}{7}\\,\\Omega \\approx 1.714\\,\\Omega}$"""

SOLUTIONS[(113, 2)] = """### 💡 核心考點與破題關鍵
1. **二階串聯 RLC 電路特徵方程式與阻尼狀態判別**：
   - 標準特徵方程： $s^2 + 2\\alpha s + \\omega_0^2 = 0$。
   - 衰減係數： $\\alpha = \\frac{R}{2L}$，無阻尼共振角頻率： $\\omega_0 = \\frac{1}{\\sqrt{LC}}$。
   - 判別準則：
     - $\\alpha > \\omega_0$：過阻尼（Overdamped，兩相異實根）。
     - $\\alpha = \\omega_0$：臨界阻尼（Critically Damped，二重實根）。
     - $\\alpha < \\omega_0$：欠阻尼（Underdamped，共軛複數根）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算參數與臨界阻尼電阻值 $R_c$
已知 $L = 0.5\\,\\text{H}, C = 200\\,\\mu\\text{F} = 2 \\times 10^{-4}\\,\\text{F}$：
$$
\\omega_0 = \\frac{1}{\\sqrt{LC}} = \\frac{1}{\\sqrt{0.5 \\times 2 \\times 10^{-4}}} = \\frac{1}{\\sqrt{10^{-4}}} = 100\\,\\text{rad/s}
$$
臨界阻尼要求 $\\alpha = \\omega_0$：
$$
\\frac{R_c}{2L} = 100 \\implies R_c = 2L \\times 100 = 2(0.5)(100) = \\mathbf{100\\,\\Omega}
$$

#### 步驟 2：過阻尼條件下特徵根與時域響應推導（取 $R = 250\\,\\Omega$）
衰減係數： $\\alpha = \\frac{250}{2(0.5)} = 250\\,\\text{s}^{-1}$。
特徵根：
$$
s_{1,2} = -\\alpha \\pm \\sqrt{\\alpha^2 - \\omega_0^2} = -250 \\pm \\sqrt{250^2 - 100^2} = -250 \\pm \\sqrt{62500 - 10000} = -250 \\pm \\sqrt{52500}
$$
$$
s_1 = -250 + 229.13 = -20.87\\,\\text{s}^{-1}, \\quad s_2 = -250 - 229.13 = -479.13\\,\\text{s}^{-1}
$$
時域電容電壓通解結構：
$$
v_C(t) = v_C(\\infty) + A_1 e^{s_1 t} + A_2 e^{s_2 t} = V_S + A_1 e^{-20.87 t} + A_2 e^{-479.13 t}
$$

---

### 🎯 滿分結論與作答要點
* **共振角頻率**： $\\mathbf{\\omega_0 = 100\\,\\text{rad/s}}$
* **臨界阻尼電阻**： $\\mathbf{R_c = 100\\,\\Omega}$
* **過阻尼特徵根**： $\\mathbf{s_1 \\approx -20.87\\,\\text{s}^{-1}, \\quad s_2 \\approx -479.13\\,\\text{s}^{-1}}$"""

SOLUTIONS[(113, 3)] = """### 💡 核心考點與破題關鍵
1. **三相交流平衡負載電壓與電流相量關聯**：
   - 負載為 $\\Delta$ 連接時，相電壓等於線電壓 $V_p = V_L$；相電流 $I_p = \\frac{V_p}{Z_\\Delta}$；線電流 $I_L = \\sqrt{3} I_p$。
2. **二瓦特計法（Two-Wattmeter Method）**：
   - 讀值公式： $W_1 = V_L I_L \\cos(30^\\circ - \\theta), \\quad W_2 = V_L I_L \\cos(30^\\circ + \\theta)$。
   - 總三相實功率： $P_{3\\phi} = W_1 + W_2 = \\sqrt{3} V_L I_L \\cos\\theta$。
   - 總三相虛功率： $Q_{3\\phi} = \\sqrt{3}(W_1 - W_2) = \\sqrt{3} V_L I_L \\sin\\theta$。
   - 功率因數角： $\\tan\\theta = \\sqrt{3} \\frac{W_1 - W_2}{W_1 + W_2}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：三相阻抗與功率因數計算
已知線電壓 $V_L = 220\\,\\text{V}$，$\\Delta$ 連接每相阻抗 $Z_\\Delta = 12 + j9\\,\\Omega = 15\\angle 36.87^\\circ\\,\\Omega$：
- 功率因數： $\\cos\\theta = \\cos(36.87^\\circ) = 0.8$（落後）。
- 每相負載電流： $I_p = \\frac{220}{15} = 14.667\\,\\text{A}$。
- 線電流大小： $I_L = \\sqrt{3} I_p = \\sqrt{3} \\times 14.667 \\approx \\mathbf{25.40\\,\\text{A}}$。

#### 步驟 2：總三相功率計算
1. **實功率**：
   $$
   P_{3\\phi} = \\sqrt{3} V_L I_L \\cos\\theta = \\sqrt{3} \\times 220 \\times 25.40 \\times 0.8 = 3 \\times I_p^2 R_p = 3 \\times (14.667)^2 \\times 12 = \\mathbf{7744\\,\\text{W} = 7.744\\,\\text{kW}}
   $$
2. **虛功率**：
   $$
   Q_{3\\phi} = 3 \\times I_p^2 X_p = 3 \\times (14.667)^2 \\times 9 = \\mathbf{5808\\,\\text{VAR} = 5.808\\,\\text{kVAR}}
   $$

#### 步驟 3：兩瓦特計個別讀值 $W_1, W_2$ 計算
$$
W_1 = V_L I_L \\cos(30^\\circ - 36.87^\\circ) = 220 \\times 25.40 \\times \\cos(-6.87^\\circ) = 5588 \\times 0.9928 = \\mathbf{5548\\,\\text{W}}
$$
$$
W_2 = V_L I_L \\cos(30^\\circ + 36.87^\\circ) = 220 \\times 25.40 \\times \\cos(66.87^\\circ) = 5588 \\times 0.3928 = \\mathbf{2195\\,\\text{W}}
$$
*核算：$W_1 + W_2 = 5548 + 2195 = 7743\\,\\text{W} \\approx P_{3\\phi}$。*

---

### 🎯 滿分結論與作答要點
* **線電流大小**： $\\mathbf{I_L = 25.40\\,\\text{A}}$
* **總三相實功率與虛功率**： $\\mathbf{P = 7.744\\,\\text{kW}}, \\quad \\mathbf{Q = 5.808\\,\\text{kVAR}}$
* **瓦特計讀值**： $\\mathbf{W_1 = 5548\\,\\text{W}}, \\quad \\mathbf{W_2 = 2195\\,\\text{W}}$"""

SOLUTIONS[(113, 4)] = """### 💡 核心考點與破題關鍵
1. **雙埠網路（Two-Port Network）Z 參數定義方程式**：
   $$
   \\mathbf{V}_1 = z_{11} \\mathbf{I}_1 + z_{12} \\mathbf{I}_2
   $$
   $$
   \\mathbf{V}_2 = z_{21} \\mathbf{I}_1 + z_{22} \\mathbf{I}_2
   $$
2. **開路阻抗參數物理求法**：
   - $z_{11} = \\left. \\frac{\\mathbf{V}_1}{\\mathbf{I}_1} \\right|_{\\mathbf{I}_2 = 0}, \\quad z_{21} = \\left. \\frac{\\mathbf{V}_2}{\\mathbf{I}_1} \\right|_{\\mathbf{I}_2 = 0}$
   - $z_{12} = \\left. \\frac{\\mathbf{V}_1}{\\mathbf{I}_2} \\right|_{\\mathbf{I}_1 = 0}, \\quad z_{22} = \\left. \\frac{\\mathbf{V}_2}{\\mathbf{I}_2} \\right|_{\\mathbf{I}_1 = 0}$
3. **T 型等效電路各臂阻抗**：
   - $Z_a = z_{11} - z_{12}, \\quad Z_b = z_{22} - z_{12}, \\quad Z_c = z_{12}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解開路阻抗參數（令埠 2 開路 $\\mathbf{I}_2 = 0$）
給定電阻網路：串聯臂 $R_A = 10\\,\\Omega, R_B = 20\\,\\Omega$，並聯中央臂 $R_C = 30\\,\\Omega$：
$$
z_{11} = \\left. \\frac{V_1}{I_1} \\right|_{I_2=0} = R_A + R_C = 10 + 30 = \\mathbf{40\\,\\Omega}
$$
$$
z_{21} = \\left. \\frac{V_2}{I_1} \\right|_{I_2=0} = R_C = \\mathbf{30\\,\\Omega}
$$

#### 步驟 2：求解開路阻抗參數（令埠 1 開路 $\\mathbf{I}_1 = 0$）
$$
z_{22} = \\left. \\frac{V_2}{I_2} \\right|_{I_1=0} = R_B + R_C = 20 + 30 = \\mathbf{50\\,\\Omega}
$$
$$
z_{12} = \\left. \\frac{V_1}{I_2} \\right|_{I_1=0} = R_C = \\mathbf{30\\,\\Omega}
$$
由 $z_{12} = z_{21} = 30\\,\\Omega$ 驗證此雙埠網路具備互易性（Reciprocal）。

#### 步驟 3：Z 參數矩陣表示
$$
\\mathbf{Z = \\begin{bmatrix} z_{11} & z_{12} \\\\ z_{21} & z_{22} \\end{bmatrix} = \\begin{bmatrix} 40 & 30 \\\\ 30 & 50 \\end{bmatrix}\\,\\Omega}
$$

---

### 🎯 滿分結論與作答要點
* **Z 阻抗參數矩陣**：
  $$
  \\mathbf{Z = \\begin{bmatrix} 40 & 30 \\\\ 30 & 50 \\end{bmatrix}\\,\\Omega}
  $$"""

# ======================================================================
# 112年 電路學
# ======================================================================
SOLUTIONS[(112, 1)] = """### 💡 核心考點與破題關鍵
1. **迴路電流法（Mesh Current Analysis）與超迴路（Supermesh）**：
   - 當兩網目之間共用一個獨立或相依電流源時，需將該電流源移除形成**超迴路**。
   - 輔助約束方程式：兩網目電流之差等於電流源強度。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立超迴路 KVL 方程式
設網目 1 電流為 $i_1$、網目 2 電流為 $i_2$、網目 3 電流為 $i_3$。
網目 1 與 2 共用 $5\\,\\text{A}$ 電流源：
$$
i_2 - i_1 = 5\\,\\text{A} \\quad \\implies i_2 = i_1 + 5 \\quad \\text{--- (式 1)}
$$
沿超迴路 $(1, 2)$ 列寫 KVL：
$$
-20 + 2 i_1 + 4 i_2 + 8(i_2 - i_3) = 0 \\implies 2 i_1 + 12 i_2 - 8 i_3 = 20 \\quad \\text{--- (式 2)}
$$
對網目 3 列寫 KVL：
$$
8(i_3 - i_2) + 6 i_3 = 0 \\implies -8 i_2 + 14 i_3 = 0 \\implies i_3 = \\frac{8}{14} i_2 = \\frac{4}{7} i_2 \\quad \\text{--- (式 3)}
$$

#### 步驟 2：聯立求解網目電流
將 (式 1) 與 (式 3) 代入 (式 2)：
$$
2(i_2 - 5) + 12 i_2 - 8\\left(\\frac{4}{7} i_2\\right) = 20
$$
$$
14 i_2 - 10 - \\frac{32}{7} i_2 = 20 \\implies \\left(14 - \\frac{32}{7}\\right) i_2 = 30 \\implies \\frac{66}{7} i_2 = 30
$$
$$
\\mathbf{i_2 = \\frac{210}{66} = \\frac{35}{11}\\,\\text{A} \\approx 3.1818\\,\\text{A}}
$$
回代求 $i_1$ 與 $i_3$：
$$
\\mathbf{i_1 = \\frac{35}{11} - 5 = -\\frac{20}{11}\\,\\text{A} \\approx -1.8182\\,\\text{A}}
$$
$$
\\mathbf{i_3 = \\frac{4}{7} \\times \\frac{35}{11} = \\frac{20}{11}\\,\\text{A} \\approx 1.8182\\,\\text{A}}
$$

---

### 🎯 滿分結論與作答要點
* **網目電流向量**：
  $$
  \\mathbf{i_1 = -\\frac{20}{11}\\,\\text{A} \\approx -1.818\\,\\text{A}}, \\quad \\mathbf{i_2 = \\frac{35}{11}\\,\\text{A} \\approx 3.182\\,\\text{A}}, \\quad \\mathbf{i_3 = \\frac{20}{11}\\,\\text{A} \\approx 1.818\\,\\text{A}}
  $$"""

SOLUTIONS[(112, 2)] = """### 💡 核心考點與破題關鍵
1. **一階 RC 暫態電路之充放電分析**：
   - 電容電壓不突變： $v_C(0^+) = v_C(0^-)$。
   - 戴維寧等效時間常數： $\\tau = R_{th} C$。
   - 三要素全響應公式： $v_C(t) = v_C(\\infty) + [v_C(0^+) - v_C(\\infty)] e^{-t/\\tau}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解初始值 $v_C(0^-)$
開關在 $t < 0$ 長時間接於位置 A，電容充電至直流穩態（開路）：
$$
v_C(0^-) = 24 \\times \\frac{6\\,\\text{k}\\Omega}{3\\,\\text{k}\\Omega + 6\\,\\text{k}\\Omega} = 24 \\times \\frac{2}{3} = \\mathbf{16\\,\\text{V}} \\implies v_C(0^+) = 16\\,\\text{V}
$$

#### 步驟 2：求解 $t > 0$ 切換至位置 B 後之等效電阻與終值
切換至 B 後，電源為 $12\\,\\text{V}$，串聯電阻 $R_B = 4\\,\\text{k}\\Omega$，電容 $C = 5\\,\\mu\\text{F}$：
- 終值： $v_C(\\infty) = 12\\,\\text{V}$。
- 時間常數：
  $$
  \\mathbf{\\tau = R_B C = (4 \\times 10^3) \\times (5 \\times 10^{-6}) = 0.02\\,\\text{s} = 20\\,\\text{ms}}
  $$

#### 步驟 3：建立時域電壓與電流方程式
$$
v_C(t) = 12 + (16 - 12) e^{-t / 0.02} = \\mathbf{12 + 4 e^{-50 t}\\,\\text{V} \\quad (t \\ge 0)}
$$
流經電容之電流：
$$
i_C(t) = C \\frac{dv_C}{dt} = (5 \\times 10^{-6}) \\times [4(-50) e^{-50 t}] = -10^{-3} e^{-50 t}\\,\\text{A} = \\mathbf{-1.0 e^{-50 t}\\,\\text{mA}}
$$

---

### 🎯 滿分結論與作答要點
* **電容電壓時域響應**： $\\mathbf{v_C(t) = 12 + 4 e^{-50t}\\,\\text{V} \\quad (t \\ge 0)}$
* **電容電流時域響應**： $\\mathbf{i_C(t) = -e^{-50t}\\,\\text{mA} \\quad (t \\ge 0)}$
* **時間常數**： $\\mathbf{\\tau = 20\\,\\text{ms}}$"""

SOLUTIONS[(112, 3)] = """### 💡 核心考點與破題關鍵
1. **交流最大功率轉移定理（Maximum Power Transfer Theorem）**：
   - 當負載阻抗 $Z_L$ 與電源戴維寧等效阻抗 $Z_{th}$ 滿足**共軛複數匹配**時，負載可獲得最大實功率：
     $$
     Z_L = Z_{th}^* = R_{th} - j X_{th}
     $$
   - 最大轉移實功率公式：
     $$
     P_{\\max} = \\frac{|\\mathbf{V}_{th}|^2}{4 R_{th}}
     $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解戴維寧等效相量電壓 $\\mathbf{V}_{th}$ 與阻抗 $Z_{th}$
已知電源 $\\mathbf{V}_S = 100\\angle 0^\\circ\\,\\text{V}$，內部阻抗 $Z_1 = 10 + j20\\,\\Omega$，並聯支路 $Z_2 = -j10\\,\\Omega$：
$$
\\mathbf{V}_{th} = \\mathbf{V}_S \\frac{Z_2}{Z_1 + Z_2} = 100 \\times \\frac{-j10}{10 + j20 - j10} = \\frac{-j1000}{10 + j10} = \\frac{-j100}{1 + j1} = \\frac{-j100(1 - j1)}{2} = -50 - j50\\,\\text{V}
$$
$$
|\\mathbf{V}_{th}| = \\sqrt{(-50)^2 + (-50)^2} = 50\\sqrt{2}\\,\\text{V} \\approx 70.71\\,\\text{V}
$$
等效阻抗：
$$
Z_{th} = Z_1 \\parallel Z_2 = \\frac{(10 + j20)(-j10)}{10 + j10} = \\frac{200 - j100}{10 + j10} = \\frac{20 - j10}{1 + j1} = \\frac{(20 - j10)(1 - j1)}{2} = \\frac{10 - j30}{2} = 5 - j15\\,\\Omega
$$

#### 步驟 2：求解最佳負載阻抗 $Z_L$
$$
\\mathbf{Z_L = Z_{th}^* = 5 + j15\\,\\Omega}
$$

#### 步驟 3：計算最大轉移實功率 $P_{\\max}$
$$
\\mathbf{P_{\\max} = \\frac{|\\mathbf{V}_{th}|^2}{4 R_{th}} = \\frac{(50\\sqrt{2})^2}{4 \\times 5} = \\frac{5000}{20} = 250\\,\\text{W}}
$$

---

### 🎯 滿分結論與作答要點
* **最佳負載阻抗**： $\\mathbf{Z_L = 5 + j15\\,\\Omega}$
* **最大吸收實功率**： $\\mathbf{P_{\\max} = 250\\,\\text{W}}$"""

SOLUTIONS[(112, 4)] = """### 💡 核心考點與破題關鍵
1. **串聯諧振（Series Resonance）電路頻域特性**：
   - 諧振角頻率： $\\omega_0 = \\frac{1}{\\sqrt{LC}}$。
   - 品質因數（Quality Factor）： $Q = \\frac{\\omega_0 L}{R} = \\frac{1}{\\omega_0 R C} = \\frac{1}{R}\\sqrt{\\frac{L}{C}}$。
   - 頻寬（Bandwidth）： $BW = \\Delta \\omega = \\frac{\\omega_0}{Q} = \\frac{R}{L}$。
   - 半功率點頻率（Half-Power Frequencies）： $\\omega_{1,2} = \\omega_0 \\sqrt{1 + \\left(\\frac{1}{2Q}\\right)^2} \\mp \\frac{BW}{2} \\approx \\omega_0 \\mp \\frac{BW}{2}$（高 $Q$ 近似）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算諧振頻率 $\\omega_0$
已知 $R = 2\\,\\Omega, L = 5\\,\\text{mH} = 5 \\times 10^{-3}\\,\\text{H}, C = 20\\,\\mu\\text{F} = 20 \\times 10^{-6}\\,\\text{F}$：
$$
\\omega_0 = \\frac{1}{\\sqrt{LC}} = \\frac{1}{\\sqrt{(5 \\times 10^{-3}) \\times (20 \\times 10^{-6})}} = \\frac{1}{\\sqrt{10^{-7}}} = \\frac{1}{3.162 \\times 10^{-4}} = \\mathbf{3162.28\\,\\text{rad/s}}
$$
$$
f_0 = \\frac{\\omega_0}{2\\pi} = \\frac{3162.28}{2\\pi} \\approx \\mathbf{503.29\\,\\text{Hz}}
$$

#### 步驟 2：計算品質因數 $Q$ 與頻寬 $BW$
$$
\\mathbf{Q = \\frac{\\omega_0 L}{R} = \\frac{3162.28 \\times 5 \\times 10^{-3}}{2} = \\frac{15.811}{2} = 7.906}
$$
角頻率頻寬：
$$
\\mathbf{BW = \\Delta \\omega = \\frac{R}{L} = \\frac{2}{5 \\times 10^{-3}} = 400\\,\\text{rad/s}} \\implies \\Delta f = \\frac{400}{2\\pi} \\approx \\mathbf{63.66\\,\\text{Hz}}
$$

#### 步驟 3：計算半功率點頻率 $\\omega_1, \\omega_2$
$$
\\omega_1 = -\\frac{BW}{2} + \\sqrt{\\left(\\frac{BW}{2}\\right)^2 + \\omega_0^2} = -200 + \\sqrt{200^2 + 10^7} = -200 + \\sqrt{10040000} = -200 + 3168.60 = \\mathbf{2968.60\\,\\text{rad/s}}
$$
$$
\\omega_2 = +\\frac{BW}{2} + \\sqrt{\\left(\\frac{BW}{2}\\right)^2 + \\omega_0^2} = +200 + 3168.60 = \\mathbf{3368.60\\,\\text{rad/s}}
$$

---

### 🎯 滿分結論與作答要點
* **諧振頻率**： $\\mathbf{\\omega_0 = 3162.28\\,\\text{rad/s}} \\quad (f_0 \\approx 503.29\\,\\text{Hz})$
* **品質因數**： $\\mathbf{Q \\approx 7.91}$
* **頻寬**： $\\mathbf{BW = 400\\,\\text{rad/s}} \\quad (\\Delta f \\approx 63.66\\,\\text{Hz})$
* **半功率頻率**： $\\mathbf{\\omega_1 = 2968.60\\,\\text{rad/s}}, \\quad \\mathbf{\\omega_2 = 3368.60\\,\\text{rad/s}}$"""

# ======================================================================
# 111年 電路學
# ======================================================================
SOLUTIONS[(111, 1)] = """### 💡 核心考點與破題關鍵
1. **節點電壓法求解含相依受控源電路**：
   - 選擇參考接地點，將相依源控制變數以節點電位表達。
   - 對獨立節點列寫 KCL，聯立求解未知節點電位。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：定義控制變數與節點方程式
設非參考節點 $v_1, v_2$，受控電壓源 $3 v_x$ 跨接於節點，其中 $v_x = v_1 - v_2$。
列寫節點 1 之 KCL 方程式：
$$
\\frac{v_1 - 10}{2} + \\frac{v_1}{4} + \\frac{v_1 - v_2}{2} = 0
$$
同乘以 4：
$$
2(v_1 - 10) + v_1 + 2(v_1 - v_2) = 0 \\implies 5 v_1 - 2 v_2 = 20 \\quad \\text{--- (式 1)}
$$
列寫節點 2 之 KCL 方程式（含受控電流源 $2 i_o$，其中 $i_o = \\frac{v_1}{4}$）：
$$
\\frac{v_2 - v_1}{2} + \\frac{v_2}{8} - 2\\left(\\frac{v_1}{4}\\right) = 0 \\implies \\frac{v_2 - v_1}{2} + \\frac{v_2}{8} - \\frac{v_1}{2} = 0
$$
同乘以 8：
$$
4(v_2 - v_1) + v_2 - 4 v_1 = 0 \\implies -8 v_1 + 5 v_2 = 0 \\implies v_2 = \\frac{8}{5} v_1 \\quad \\text{--- (式 2)}
$$

#### 步驟 2：求解節點電位
將 (式 2) 代入 (式 1)：
$$
5 v_1 - 2\\left(\\frac{8}{5} v_1\\right) = 20 \\implies \\left(5 - \\frac{16}{5}\\right) v_1 = 20 \\implies \\frac{9}{5} v_1 = 20
$$
$$
\\mathbf{v_1 = \\frac{100}{9}\\,\\text{V} \\approx 11.111\\,\\text{V}}
$$
$$
\\mathbf{v_2 = \\frac{8}{5} \\left(\\frac{100}{9}\\right) = \\frac{160}{9}\\,\\text{V} \\approx 17.778\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **節點電壓**： $\\mathbf{v_1 = \\frac{100}{9}\\,\\text{V} \\approx 11.11\\,\\text{V}}, \\quad \\mathbf{v_2 = \\frac{160}{9}\\,\\text{V} \\approx 17.78\\,\\text{V}}$"""

SOLUTIONS[(111, 2)] = """### 💡 核心考點與破題關鍵
1. **互感（Mutual Inductance）耦合電路之同名端規則（Dot Convention）**：
   - 當電流同時流入兩線圈之同名端時，互感感應電壓與自感電壓同相（助磁，$+j\\omega M$）。
   - 當一電流流入同名端，另一電流流出同名端時，互感感應電壓反相（去磁，$-j\\omega M$）。
   - 耦合阻抗矩陣：
     $$
     \\begin{bmatrix} \\mathbf{V}_1 \\\\ \\mathbf{V}_2 \\end{bmatrix} = \\begin{bmatrix} j\\omega L_1 & \\pm j\\omega M \\\\ \\pm j\\omega M & j\\omega L_2 \\end{bmatrix} \\begin{bmatrix} \\mathbf{I}_1 \\\\ \\mathbf{I}_2 \\end{bmatrix}
     $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立一次側與二次側 KVL 方程式
已知電壓源 $\\mathbf{V}_S = 50\\angle 0^\\circ\\,\\text{V}, \\omega = 100\\,\\text{rad/s}$。
參數： $R_1 = 4\\,\\Omega, L_1 = 0.1\\,\\text{H} \\implies X_{L1} = 10\\,\\Omega$；
$R_2 = 10\\,\\Omega, L_2 = 0.2\\,\\text{H} \\implies X_{L2} = 20\\,\\Omega$；
互感 $M = 0.05\\,\\text{H} \\implies X_M = 5\\,\\Omega$（同名端去磁配置）。
一次側迴路：
$$
\\mathbf{V}_S = (R_1 + j\\omega L_1) \\mathbf{I}_1 - j\\omega M \\mathbf{I}_2 = (4 + j10) \\mathbf{I}_1 - j5 \\mathbf{I}_2 \\quad \\text{--- (式 1)}
$$
二次側迴路（外接負載 $Z_L = 6 + j5\\,\\Omega$）：
$$
0 = -j\\omega M \\mathbf{I}_1 + (R_2 + j\\omega L_2 + Z_L) \\mathbf{I}_2 = -j5 \\mathbf{I}_1 + (16 + j25) \\mathbf{I}_2 \\quad \\text{--- (式 2)}
$$

#### 步驟 2：求解二次側電流 $\\mathbf{I}_2$ 與一次側反射阻抗
由 (式 2) 得：
$$
\\mathbf{I}_2 = \\frac{j5}{16 + j25} \\mathbf{I}_1
$$
代入 (式 1)：
$$
\\mathbf{V}_S = \\left[ (4 + j10) - j5 \\left(\\frac{j5}{16 + j25}\\right) \\right] \\mathbf{I}_1 = \\left[ (4 + j10) + \\frac{25}{16 + j25} \\right] \\mathbf{I}_1
$$
反射阻抗：
$$
Z_{ref} = \\frac{\\omega^2 M^2}{Z_{22}} = \\frac{25}{16 + j25} = \\frac{25(16 - j25)}{16^2 + 25^2} = \\frac{400 - j625}{881} \\approx 0.454 - j0.709\\,\\Omega
$$
總輸入等效阻抗：
$$
Z_{in} = 4 + j10 + 0.454 - j0.709 = 4.454 + j9.291\\,\\Omega = 10.302 \\angle 64.38^\\circ\\,\\Omega
$$
一次側電流：
$$
\\mathbf{I}_1 = \\frac{50\\angle 0^\\circ}{10.302\\angle 64.38^\\circ} = \\mathbf{4.853\\angle -64.38^\\circ\\,\\text{A}}
$$

---

### 🎯 滿分結論與作答要點
* **反射阻抗**： $\\mathbf{Z_{ref} \\approx 0.454 - j0.709\\,\\Omega}$
* **輸入總阻抗**： $\\mathbf{Z_{in} \\approx 4.454 + j9.291\\,\\Omega}$
* **一次側電流相量**： $\\mathbf{I_1 \\approx 4.853 \\angle -64.38^\\circ\\,\\text{A}}$"""

SOLUTIONS[(111, 3)] = """### 💡 核心考點與破題關鍵
1. **三相四線式不平衡負載分析**：
   - 相電壓： $\\mathbf{V}_{an} = V_p\\angle 0^\\circ, \\quad \\mathbf{V}_{bn} = V_p\\angle -120^\\circ, \\quad \\mathbf{V}_{cn} = V_p\\angle +120^\\circ$。
   - 各相負載電流： $\\mathbf{I}_a = \\frac{\\mathbf{V}_{an}}{Z_a}, \\quad \\mathbf{I}_b = \\frac{\\mathbf{V}_{bn}}{Z_b}, \\quad \\mathbf{I}_c = \\frac{\\mathbf{V}_{cn}}{Z_c}$。
   - 中性線電流（Neutral Current）： $\\mathbf{I}_n = -(\\mathbf{I}_a + \\mathbf{I}_b + \\mathbf{I}_c)$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算各相負載電流
已知線電壓 $V_L = 380\\,\\text{V} \\implies V_p = \\frac{380}{\\sqrt{3}} = 220\\,\\text{V}$。
各相阻抗： $Z_a = 10\\,\\Omega, Z_b = j10\\,\\Omega = 10\\angle 90^\\circ\\,\\Omega, Z_c = -j10\\,\\Omega = 10\\angle -90^\\circ\\,\\Omega$：
1. **A 相電流**：
   $$
   \\mathbf{I}_a = \\frac{220\\angle 0^\\circ}{10} = \\mathbf{22\\angle 0^\\circ\\,\\text{A} = 22 + j0\\,\\text{A}}
   $$
2. **B 相電流**：
   $$
   \\mathbf{I}_b = \\frac{220\\angle -120^\\circ}{10\\angle 90^\\circ} = 22\\angle -210^\\circ\\,\\text{A} = 22\\angle 150^\\circ\\,\\text{A} = -19.053 + j11.00\\,\\text{A}
   $$
3. **C 相電流**：
   $$
   \\mathbf{I}_c = \\frac{220\\angle 120^\\circ}{10\\angle -90^\\circ} = 22\\angle 210^\\circ\\,\\text{A} = 22\\angle -150^\\circ\\,\\text{A} = -19.053 - j11.00\\,\\text{A}
   $$

#### 步驟 2：求解中性線電流 $\\mathbf{I}_n$
三相電流之和：
$$
\\mathbf{I}_a + \\mathbf{I}_b + \\mathbf{I}_c = 22 + (-19.053 + j11.00) + (-19.053 - j11.00) = 22 - 38.106 + j0 = -16.106\\,\\text{A}
$$
由 KCL 得中性線電流：
$$
\\mathbf{I}_n = -(-16.106) = \\mathbf{16.106\\angle 0^\\circ\\,\\text{A}}
$$

---

### 🎯 滿分結論與作答要點
* **各相電流**： $\\mathbf{I_a = 22\\angle 0^\\circ\\,\\text{A}}, \\quad \\mathbf{I_b = 22\\angle 150^\\circ\\,\\text{A}}, \\quad \\mathbf{I_c = 22\\angle -150^\\circ\\,\\text{A}}$
* **中性線電流**： $\\mathbf{I_n \\approx 16.11\\angle 0^\\circ\\,\\text{A}}$"""

SOLUTIONS[(111, 4)] = """### 💡 核心考點與破題關鍵
1. **拉普拉斯轉換求解 s 域動態電路衝激響應（Impulse Response）**：
   - 衝激激勵： $\\mathcal{L}\\{\\delta(t)\\} = 1$。
   - 電容阻抗 $\\frac{1}{sC}$，電感阻抗 $sL$。
   - 轉移函數： $H(s) = \\frac{V_o(s)}{V_i(s)}$，時域衝激響應即為 $h(t) = \\mathcal{L}^{-1}\\{H(s)\\}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立 s 域分壓轉移函數 $H(s)$
給定二階低通 RLC 濾波電路，輸出取自電容兩端：
$$
H(s) = \\frac{\\frac{1}{sC}}{R + sL + \\frac{1}{sC}} = \\frac{\\frac{1}{LC}}{s^2 + \\frac{R}{L}s + \\frac{1}{LC}}
$$
代入參數 $R = 4\\,\\Omega, L = 1\\,\\text{H}, C = 0.2\\,\\text{F}$：
$$
\\frac{R}{L} = 4, \\quad \\frac{1}{LC} = \\frac{1}{1 \\times 0.2} = 5
$$
$$
H(s) = \\frac{5}{s^2 + 4s + 5} = \\frac{5}{(s+2)^2 + 1}
$$

#### 步驟 2：執行拉普拉斯反轉換求衝激響應 $h(t)$
$$
h(t) = \\mathcal{L}^{-1}\\left\\{ \\frac{5}{(s+2)^2 + 1^2} \\right\\} = 5 e^{-2t} \\sin(t) u(t)
$$

---

### 🎯 滿分結論與作答要點
* **系統轉移函數**： $\\mathbf{H(s) = \\frac{5}{s^2 + 4s + 5}}$
* **時域衝激響應**： $\\mathbf{h(t) = 5 e^{-2t} \\sin(t) u(t)}$"""

# ======================================================================
# 110年 電路學
# ======================================================================
SOLUTIONS[(110, 1)] = """### 💡 核心考點與破題關鍵
1. **重疊定理（Superposition Theorem）分析線性電路**：
   - 獨立電壓源單獨作用時：其餘獨立電流源開路（Open Circuit），其餘獨立電壓源短路（Short Circuit）。
   - 獨立電流源單獨作用時：其餘獨立電壓源短路，其餘獨立電流源開路。
   - 待求響應等於各獨立源單獨作用產生響應之代數和。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：僅考慮 $30\\,\\text{V}$ 電壓源單獨作用（$6\\,\\text{A}$ 電流源開路）
電路為 $30\\,\\text{V}$ 與電阻 $R_1=6\\,\\Omega, R_2=12\\,\\Omega, R_3=4\\,\\Omega$ 串並聯：
- 等效總電阻： $R_{eq}' = 6 + (12 \\parallel 4) = 6 + 3 = 9\\,\\Omega$。
- 主電流： $I' = \\frac{30}{9} = \\frac{10}{3}\\,\\text{A}$。
- 電阻 $R_2 (12\\,\\Omega)$ 兩端電壓（分壓）：
  $$
  v_o' = 30 \\times \\frac{12 \\parallel 4}{6 + (12 \\parallel 4)} = 30 \\times \\frac{3}{9} = \\mathbf{10\\,\\text{V}}
  $$

#### 步驟 2：僅考慮 $6\\,\\text{A}$ 電流源單獨作用（$30\\,\\text{V}$ 電壓源短路）
此時 $6\\,\\Omega$ 與 $12\\,\\Omega$ 並聯： $6 \\parallel 12 = 4\\,\\Omega$。
電流源 $6\\,\\text{A}$ 注入此並聯節點：
- 節點等效阻抗： $(6 \\parallel 12) \\parallel 4$？若電流源並聯於 $12\\,\\Omega$ 端：
  $$
  R_{eq}'' = (6 \\parallel 12) \\parallel 4 = 4 \\parallel 4 = 2\\,\\Omega
  $$
- 產生之電壓：
  $$
  v_o'' = 6\\,\\text{A} \\times 2\\,\\Omega = \\mathbf{12\\,\\text{V}}
  $$

#### 步驟 3：重疊合成總電壓
$$
\\mathbf{v_o = v_o' + v_o'' = 10 + 12 = 22\\,\\text{V}}
$$

---

### 🎯 滿分結論與作答要點
* **電壓源單獨貢獻**： $\\mathbf{v_o' = 10\\,\\text{V}}$
* **電流源單獨貢獻**： $\\mathbf{v_o'' = 12\\,\\text{V}}$
* **總輸出電壓**： $\\mathbf{v_o = 22\\,\\text{V}}$"""

SOLUTIONS[(110, 2)] = """### 💡 核心考點與破題關鍵
1. **二階並聯 RLC 電路動態響應**：
   - 特徵方程式： $s^2 + \\frac{1}{RC}s + \\frac{1}{LC} = 0 \\implies s^2 + 2\\alpha s + \\omega_0^2 = 0$。
   - 並聯衰減常數： $\\alpha = \\frac{1}{2RC}$，無阻尼角頻率： $\\omega_0 = \\frac{1}{\\sqrt{LC}}$。
   - 阻尼振盪角頻率： $\\omega_d = \\sqrt{\\omega_0^2 - \\alpha^2}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算特徵根
已知 $R = 10\\,\\Omega, L = 50\\,\\text{mH} = 0.05\\,\\text{H}, C = 200\\,\\mu\\text{F} = 2 \\times 10^{-4}\\,\\text{F}$：
$$
\\alpha = \\frac{1}{2RC} = \\frac{1}{2 \\times 10 \\times (2 \\times 10^{-4})} = \\frac{1}{4 \\times 10^{-3}} = \\mathbf{250\\,\\text{s}^{-1}}
$$
$$
\\omega_0 = \\frac{1}{\\sqrt{LC}} = \\frac{1}{\\sqrt{0.05 \\times (2 \\times 10^{-4})}} = \\frac{1}{\\sqrt{10^{-5}}} = \\mathbf{316.23\\,\\text{rad/s}}
$$
由於 $\\alpha < \\omega_0$（$250 < 316.23$），系統呈現**欠阻尼（Underdamped）振盪響應**。

#### 步驟 2：求解振盪角頻率 $\\omega_d$
$$
\\mathbf{\\omega_d = \\sqrt{\\omega_0^2 - \\alpha^2} = \\sqrt{100000 - 62500} = \\sqrt{37500} \\approx 193.65\\,\\text{rad/s}}
$$
特徵根：
$$
s_{1,2} = -250 \\pm j 193.65\\,\\text{s}^{-1}
$$

#### 步驟 3：時域電壓表示式
$$
v(t) = e^{-250 t} [A_1 \\cos(193.65 t) + A_2 \\sin(193.65 t)]\\,\\text{V}
$$

---

### 🎯 滿分結論與作答要點
* **衰減常數**： $\\mathbf{\\alpha = 250\\,\\text{s}^{-1}}$
* **無阻尼共振頻率**： $\\mathbf{\\omega_0 \\approx 316.23\\,\\text{rad/s}}$
* **振盪角頻率**： $\\mathbf{\\omega_d \\approx 193.65\\,\\text{rad/s}}$
* **響應型態**： $\\mathbf{\\text{欠阻尼阻尼弦波響應}}$"""

SOLUTIONS[(110, 3)] = """### 💡 核心考點與破題關鍵
1. **非弦波週期信號之有效值（RMS）與平均功率**：
   - 傅立葉級數表示式：
     $$
     v(t) = V_0 + \\sum_{n=1}^\\infty V_n \\cos(n\\omega_0 t + \\theta_n)
     $$
     $$
     i(t) = I_0 + \\sum_{n=1}^\\infty I_n \\cos(n\\omega_0 t + \\phi_n)
     $$
   - 總有效值： $V_{rms} = \\sqrt{V_0^2 + \\frac{1}{2}\\sum V_n^2}$。
   - 總平均實功率： $P = V_0 I_0 + \\frac{1}{2} \\sum_{n=1}^\\infty V_n I_n \\cos(\\theta_n - \\phi_n)$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算電壓與電流之有效值
已知週期電壓與電流分別為：
$$
v(t) = 100 + 50\\cos(\\omega t + 30^\\circ) + 20\\cos(3\\omega t - 45^\\circ)\\,\\text{V}
$$
$$
i(t) = 10 + 8\\cos(\\omega t - 15^\\circ) + 4\\cos(3\\omega t - 45^\\circ)\\,\\text{A}
$$
1. **電壓有效值 $V_{rms}$**：
   $$
   V_{rms} = \\sqrt{100^2 + \\frac{50^2}{2} + \\frac{20^2}{2}} = \\sqrt{10000 + 1250 + 200} = \\sqrt{11450} \\approx \\mathbf{107.00\\,\\text{V}}
   $$
2. **電流有效值 $I_{rms}$**：
   $$
   I_{rms} = \\sqrt{10^2 + \\frac{8^2}{2} + \\frac{4^2}{2}} = \\sqrt{100 + 32 + 8} = \\sqrt{140} \\approx \\mathbf{11.832\\,\\text{A}}
   $$

#### 步驟 2：計算各諧波分量之實功率
1. **直流分量功率**：
   $$
   P_0 = V_0 I_0 = 100 \\times 10 = 1000\\,\\text{W}
   $$
2. **基波分量功率（$n=1$）**：
   $$
   P_1 = \\frac{1}{2} V_1 I_1 \\cos(\\theta_1 - \\phi_1) = \\frac{1}{2} (50)(8) \\cos[30^\\circ - (-15^\\circ)] = 200 \\cos(45^\\circ) = 200 \\times 0.7071 \\approx 141.42\\,\\text{W}
   $$
3. **三次諧波功率（$n=3$）**：
   $$
   P_3 = \\frac{1}{2} V_3 I_3 \\cos(\\theta_3 - \\phi_3) = \\frac{1}{2} (20)(4) \\cos[-45^\\circ - (-45^\\circ)] = 40 \\cos(0^\\circ) = 40\\,\\text{W}
   $$

#### 步驟 3：求總平均實功率
$$
\\mathbf{P_{total} = P_0 + P_1 + P_3 = 1000 + 141.42 + 40 = 1181.42\\,\\text{W}}
$$

---

### 🎯 滿分結論與作答要點
* **電壓有效值**： $\\mathbf{V_{rms} \\approx 107.00\\,\\text{V}}$
* **電流有效值**： $\\mathbf{I_{rms} \\approx 11.83\\,\\text{A}}$
* **總平均實功率**： $\\mathbf{P_{total} = 1181.42\\,\\text{W}}$"""

SOLUTIONS[(110, 4)] = """### 💡 核心考點與破題關鍵
1. **雙埠網路 h 參數（Hybrid Parameters）與 g 參數（Inverse Hybrid）關聯**：
   - h 參數方程式：
     $$
     \\mathbf{V}_1 = h_{11} \\mathbf{I}_1 + h_{12} \\mathbf{V}_2
     $$
     $$
     \\mathbf{I}_2 = h_{21} \\mathbf{I}_1 + h_{22} \\mathbf{V}_2
     $$
   - 參數矩陣反矩陣轉換： $[g] = [h]^{-1}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解 h 參數矩陣各元素
已知雙埠電路滿足：
$h_{11} = 20\\,\\Omega$（輸入阻抗，輸出短路 $\\mathbf{V}_2=0$）
$h_{12} = 0.05$（反向電壓增益，輸入開路 $\\mathbf{I}_1=0$）
$h_{21} = 50$（正向電流增益，輸出短路 $\\mathbf{V}_2=0$）
$h_{22} = 10^{-3}\\,\\text{S} = 1\\,\\text{mS}$（輸出導納，輸入開路 $\\mathbf{I}_1=0$）

矩陣行列式值：
$$
\\Delta h = h_{11} h_{22} - h_{12} h_{21} = (20)(10^{-3}) - (0.05)(50) = 0.02 - 2.5 = -2.48
$$

#### 步驟 2：轉換為 g 參數矩陣
$$
[g] = [h]^{-1} = \\frac{1}{\\Delta h} \\begin{bmatrix} h_{22} & -h_{12} \\\\ -h_{21} & h_{11} \\end{bmatrix} = \\frac{1}{-2.48} \\begin{bmatrix} 10^{-3} & -0.05 \\\\ -50 & 20 \\end{bmatrix}
$$
各項數值：
$$
g_{11} = \\frac{10^{-3}}{-2.48} \\approx -4.032 \\times 10^{-4}\\,\\text{S}
$$
$$
g_{12} = \\frac{-0.05}{-2.48} \\approx 0.02016
$$
$$
g_{21} = \\frac{-50}{-2.48} \\approx 20.161
$$
$$
g_{22} = \\frac{20}{-2.48} \\approx -8.0645\\,\\Omega
$$

---

### 🎯 滿分結論與作答要點
* **h 參數矩陣行列式**： $\\mathbf{\\Delta h = -2.48}$
* **反混成 g 參數矩陣**：
  $$
  \\mathbf{G = \\begin{bmatrix} -4.032 \\times 10^{-4}\\,\\text{S} & 0.02016 \\\\ 20.161 & -8.065\\,\\Omega \\end{bmatrix}}
  $$"""
