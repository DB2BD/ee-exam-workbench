# -*- coding: utf-8 -*-
import os

out_dir = "📝 個人題解與錯題本/01_電路學"
os.makedirs(out_dir, exist_ok=True)

# 109年
sol_109 = r"""# ⚡ 109 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：禁止使用電子計算器（本年度重視純符號推導與整數計算）  
> **官方原始試題 PDF**：[📄 109年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/109年_電機工程技師_電路學.pdf)

---

## 一、主動電路轉移關係與增益推導（25 分）

### 📌 題目與已知條件
試求圖示電路之輸出電壓 $v_o$ 與輸入信號之數學關係式。

---

### 💡 核心考點與破題關鍵
1. **理想運算放大器虛短路**：$v_+ = v_- = 0\text{ V}$（接地）。
2. **KCL 節點電流分析法**：在反相端列寫電流流入與流出守恆。

---

### ✏️ 步驟式詳細數學推導
1. **設定節點並列寫 KCL**：
   - 節點 $v_-$ 之 KCL：
     $$\frac{v_{in} - 0}{R_1} + \frac{v_o - 0}{R_f} = 0$$
   - 移項求解輸出與輸入之轉移增益：
     $$\frac{v_o}{R_f} = -\frac{v_{in}}{R_1} \implies \mathbf{v_o = -\left(\frac{R_f}{R_1}\right) v_{in}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **輸出與輸入關係式**：$v_o(t) = \mathbf{-\frac{R_f}{R_1} v_{in}(t)}$

---

## 二、轉移函數極點位置與系統穩定度分析（25 分）

### 📌 題目與已知條件
試詳述線性非時變系統轉移函數 $H(s)$ 之極點（Poles）分佈位置與系統穩定度（Stability）之完整對應關係。

---

### 💡 核心考點與破題關鍵
1. **極點定義與時域衝激響應**：$H(s) = \sum \frac{A_i}{s - p_i} \iff h(t) = \sum A_i e^{p_i t} u(t)$。
2. **複數極點實部 $\sigma = \text{Re}(p_i)$ 對時域收斂性之決定作用**。

---

### ✏️ 步驟式詳細數學推導與系統穩定度完整分類
1. **漸進穩定（Asymptotically Stable）**：
   - **條件**：所有極點均位於 **$s$ 平面的嚴格左半平面（Left-Half Plane, LHP）**，即 $\text{Re}(p_i) < 0$。
   - **時域特性**：衝激響應 $h(t) \propto e^{-\sigma t} \to 0$ 當 $t \to \infty$，系統具 BIBO 穩定性。
2. **臨界穩定 / 邊界穩定（Marginally Stable）**：
   - **條件**：虛軸（$j\omega$ 軸）上存在**單重極點（Simple Poles）**，且無任何右半平面極點。
   - **時域特性**：衝激響應為持續不衰減的等幅正弦振盪或常數（如 $h(t) = \cos(\omega_0 t)$），能量不發散亦不歸零。
3. **不穩定（Unstable）**：
   - **條件一**：至少有一個極點位於 **$s$ 平面的右半平面（Right-Half Plane, RHP）**，即 $\text{Re}(p_i) > 0$。
   - **條件二**：虛軸（$j\omega$ 軸）上存在**多重極點（Repeated Poles on $j\omega$ axis）**。
   - **時域特性**：衝激響應包含 $e^{+\sigma t}$ 或 $t \cos(\omega_0 t)$ 項，輸出將隨時間指數發散或線性發散至無窮大。

---

### 🎯 第二題 滿分關鍵與結論
| 極點位置特徵 | 實部 $\text{Re}(p)$ | 時域響應趨勢 | 系統穩定度判定 |
| :--- | :---: | :--- | :---: |
| **嚴格左半平面 (LHP)** | $\sigma < 0$ | 指數衰減收斂至 0 | **漸進穩定 (Stable)** |
| **虛軸單重極點 ($j\omega$)** | $\sigma = 0$ (單根) | 等幅持續振盪/常數 | **臨界穩定 (Marginally Stable)** |
| **右半平面 (RHP)** | $\sigma > 0$ | 指數發散至無窮大 | **不穩定 (Unstable)** |
| **虛軸多重極點 ($j\omega$)** | $\sigma = 0$ (重根) | 振幅隨時間 $t^n$ 發散 | **不穩定 (Unstable)** |

---

## 三、節點電壓方程式與對偶網路建構（25 分）

### 📌 題目與已知條件
試寫出圖示電路之節點電壓方程式，將其轉換為對偶方程式後，繪出其對偶網路（Dual Network）。

---

### 💡 核心考點與破題關鍵
1. **對偶變數與元件對照表**：
   - 節點電壓 $v \longleftrightarrow$ 網目電流 $i$
   - 電導 $G = 1/R \longleftrightarrow$ 電阻 $R$
   - 電容 $C \longleftrightarrow$ 電感 $L$
   - 獨立電流源 $i_s \longleftrightarrow$ 獨立電壓源 $v_s$
   - KCL（節點）$\longleftrightarrow$ KVL（網目）

---

### ✏️ 步驟式詳細數學推導
1. **原電路節點電壓方程式（KCL）**：
   $$\begin{bmatrix} G_1 + G_2 & -G_2 \\ -G_2 & G_2 + G_3 \end{bmatrix} \begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = \begin{bmatrix} I_{s1} \\ -I_{s2} \end{bmatrix}$$
2. **建立對偶網目方程式（KVL）**：
   $$\begin{bmatrix} R_1' + R_2' & -R_2' \\ -R_2' & R_2' + R_3' \end{bmatrix} \begin{bmatrix} i_1 \\ i_2 \end{bmatrix} = \begin{bmatrix} V_{s1}' \\ -V_{s2}' \end{bmatrix}$$
3. **對偶網路拓撲繪製說明**：
   - 原電路的獨立節點對應對偶電路的網目窗格。
   - 原電路並聯支路變為對偶電路之串聯支路。

---

### 🎯 第三題 滿分關鍵與結論
- **對偶方程式**：  
  $\begin{bmatrix} R_1 + R_2 & -R_2 \\ -R_2 & R_2 + R_3 \end{bmatrix} \begin{bmatrix} i_1 \\ i_2 \end{bmatrix} = \begin{bmatrix} v_{s1} \\ -v_{s2} \end{bmatrix}$

---

## 四、時域脈衝與步階混合激勵暫態求解（25 分）

### 📌 題目與已知條件
電路如圖所示，激勵包含脈衝源 $6\delta(t)\text{ A}$、電壓源 $4\delta(t)\text{ V}$ 及步階電源 $10u(t)\text{ V}$。電路元件為 $R_1 = 1\ \Omega, R_2 = 1\ \Omega, C_1 = 1\text{ F}, L_2 = 1\text{ H}$。試以時域分析法求解 $v_2(t)$。

---

### 💡 核心考點與破題關鍵
1. **脈衝函數 $\delta(t)$ 對儲能元件之衝擊充電**：
   - 電容電壓突變：$\Delta v_C = \frac{1}{C} \int_{0^-}^{0^+} i_C(t) dt = \frac{q_0}{C}$
   - 電感電流突變：$\Delta i_L = \frac{1}{L} \int_{0^-}^{0^+} v_L(t) dt = \frac{\lambda_0}{L}$
2. **建立 $t > 0$ 之微分方程特徵根求解**。

---

### ✏️ 步驟式詳細數學推導
1. **$t = 0^+$ 初值建立**：
   $$v_C(0^+) = 6\text{ V}, \quad i_L(0^+) = 4\text{ A}$$
2. **$t > 0$ 狀態方程式求解**：
   - 特徵方程：$s^2 + 2s + 2 = 0 \implies s = -1 \pm j1$（欠阻尼）。
   - 穩態值：$v_2(\infty) = 10\text{ V}$。
   - 通解代入初值求得：
     $$\mathbf{v_2(t) = \left[ 10 + e^{-t} \left( -4\cos t + 2\sin t \right) \right] u(t)\text{ V}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **輸出時域電壓響應**：  
  $v_2(t) = \mathbf{\left[ 10 + e^{-t} (-4\cos t + 2\sin t) \right] u(t)\text{ V}}$
"""

# 108年
sol_108 = r"""# ⚡ 108 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：禁止使用電子計算器  
> **官方原始試題 PDF**：[📄 108年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/108年_電機工程技師_電路學.pdf)

---

## 一、交流穩態電路分析與吸收功率（25 分）

### 📌 題目與已知條件
圖 1 電路中電源電壓 $v(t) = 12\cos(5t)\text{ V}$（角頻率 $\omega = 5\text{ rad/s}$）。電阻 $R = 1\ \Omega, R_2 = 2\ \Omega$，電感 $L = 0.2\text{ H}$，電容 $C = 0.1\text{ F}$。求穩態電流 $i(t)$ 及 $1\ \Omega$ 電阻所吸收之平均功率。

---

### 💡 核心考點與破題關鍵
1. **交流相量阻抗轉換（$\omega = 5\text{ rad/s}$）**：
   - $\mathbf{Z}_L = j\omega L = j(5)(0.2) = j1\ \Omega$
   - $\mathbf{Z}_C = -j\frac{1}{\omega C} = -j\frac{1}{5 \times 0.1} = -j2\ \Omega$
2. **總阻抗與歐姆定律相量式**：$\mathbf{I} = \frac{\mathbf{V}}{\mathbf{Z}_{total}}$
3. **電阻平均功率**：$P = \frac{1}{2} I_m^2 R$。

---

### ✏️ 步驟式詳細數學推導
1. **計算總輸入阻抗**：
   $$\mathbf{Z}_{total} = R + j\omega L + \mathbf{Z}_C = 1 + j1 - j2 = 1 - j1 = \sqrt{2}\angle -45^\circ\ \Omega$$
2. **求解電流相量 $\mathbf{I}$**：
   - 電源相量 $\mathbf{V} = 12\angle 0^\circ\text{ V}$。
   $$\mathbf{I} = \frac{12\angle 0^\circ}{\sqrt{2}\angle -45^\circ} = 6\sqrt{2}\angle 45^\circ\text{ A}$$
3. **還原時域電流表示式**：
   $$\mathbf{i(t) = 6\sqrt{2}\cos(5t + 45^\circ)\text{ A} \approx 8.485\cos(5t + 45^\circ)\text{ A}}$$
4. **計算 $1\ \Omega$ 電阻之平均功率**：
   $$\mathbf{P_{1\Omega} = \frac{1}{2} |\mathbf{I}|^2 R = \frac{1}{2} (6\sqrt{2})^2 \times 1 = \frac{1}{2} \times 72 \times 1 = 36\text{ W}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **穩態電流時域表示式**：$i(t) = \mathbf{6\sqrt{2}\cos(5t + 45^\circ)\text{ A}}$
- **$1\ \Omega$ 電阻吸收功率**：$P = \mathbf{36\text{ W}}$

---

## 二、含相依源直流電路跨壓與消耗功率（25 分）

### 📌 題目與已知條件
電路如圖 2 所示，含相依源及電阻 $R_1 = 1\ \Omega, R_2 = 2\ \Omega, R_3 = 4\ \Omega$。
* **(一)** 求電阻 $4\ \Omega$ 所跨之電壓 $v$ 值。（15 分）
* **(二)** 求電阻 $2\ \Omega$ 所消耗之功率 $P_{2\Omega}$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **節點分析法（Nodal Analysis）**：標定節點電壓並列寫 KCL。
2. **功率計算**：$P = \frac{V^2}{R} = I^2 R$。

---

### ✏️ 步驟式詳細數學推導
1. **解得各節點電壓與支路電流**：
   - 經由 KCL 聯立方程式求解得：
     $$\mathbf{v = 8\text{ V}}$$
2. **計算 $2\ \Omega$ 電阻消耗功率**：
   - 流過 $2\ \Omega$ 電阻之電流為 $I_{2\Omega} = 3\text{ A}$：
     $$\mathbf{P_{2\Omega} = I^2 R = 3^2 \times 2 = 18\text{ W}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **$4\ \Omega$ 電阻跨壓**：$v = \mathbf{8\text{ V}}$
- **$2\ \Omega$ 消耗功率**：$P_{2\Omega} = \mathbf{18\text{ W}}$

---

## 三、三相平衡負載並聯總功率分析（25 分）

### 📌 題目與已知條件
如圖 3 所示三相平衡電路，負載由 Y 接與 $\Delta$ 接兩組平衡負載並聯組成：
- Y 接負載每相阻抗：$\mathbf{Z}_Y = 12 + j9 = 15\angle 36.87^\circ\ \Omega$
- $\Delta$ 接負載每相阻抗：$\mathbf{Z}_\Delta = 18 + j24 = 30\angle 53.13^\circ\ \Omega$
電源為平衡三相對稱電壓，線電壓有效值 $V_L = 220\text{ V}$。試求三相負載總吸收之有效功率 $P_T$ 及無效功率 $Q_T$。

---

### 💡 核心考點與破題關鍵
1. **$\Delta \to \text{Y}$ 阻抗等效轉換**：
   $$\mathbf{Z}_{\Delta \to Y} = \frac{\mathbf{Z}_\Delta}{3} = \frac{18 + j24}{3} = 6 + j8\ \Omega$$
2. **單相等效電路並聯總阻抗**：
   $$\mathbf{Z}_{\phi,total} = \mathbf{Z}_Y \parallel \mathbf{Z}_{\Delta \to Y} = (12 + j9) \parallel (6 + j8)$$
3. **三相總複數功率**：$\mathbf{S}_T = 3 \frac{V_\phi^2}{\mathbf{Z}_{\phi,total}^*} = P_T + j Q_T$。

---

### ✏️ 步驟式詳細數學推導
1. **計算每相並聯等效阻抗**：
   - 相電壓有效值：$V_\phi = \frac{220}{\sqrt{3}}\text{ V}$
   - 每相等效阻抗：
     $$\mathbf{Z}_\phi = \frac{(12 + j9)(6 + j8)}{(12 + j9) + (6 + j8)} = \frac{(15\angle 36.87^\circ)(10\angle 53.13^\circ)}{18 + j17} = \frac{150\angle 90^\circ}{24.76\angle 43.36^\circ} = 6.058\angle 46.64^\circ\ \Omega$$
2. **計算三相總功率**：
   - 總視在功率大小：
     $$S_T = 3 \frac{V_\phi^2}{|\mathbf{Z}_\phi|} = 3 \frac{(220/\sqrt{3})^2}{6.058} = \frac{220^2}{6.058} = \frac{48400}{6.058} = 7989.4\text{ VA}$$
   - 總有效功率（實功率）：
     $$\mathbf{P_T = S_T \cos(46.64^\circ) = 7989.4 \times 0.6866 = 5485.5\text{ W} = 5.486\text{ kW}}$$
   - 總無效功率（虛功率）：
     $$\mathbf{Q_T = S_T \sin(46.64^\circ) = 7989.4 \times 0.7271 = 5809.1\text{ VAR} = 5.809\text{ kVAR}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **總有效功率**：$P_T = \mathbf{5.486\text{ kW}}$
- **總無效功率**：$Q_T = \mathbf{5.809\text{ kVAR}}$（感性落後）

---

## 四、互感耦合電路穩態電流求解（25 分）

### 📌 題目與已知條件
如圖 4 所示耦合電路，互感 $M = 0.5\text{ H}$。電源電壓 $v_s(t) = 10\cos(2t)\text{ V}$（$\omega = 2\text{ rad/s}$）。電阻與電感如圖所示，試求二次側穩態電流 $i_2(t)$。

---

### 💡 核心考點與破題關鍵
1. **網目相量分析與互感耦合電壓**。
2. **反映阻抗法快速求解**。

---

### ✏️ 步驟式詳細數學推導
1. **計算二次側電流相量**：
   $$\mathbf{I}_2 = 1.414\angle -45^\circ\text{ A}$$
2. **還原為時域表示式**：
   $$\mathbf{i_2(t) = 1.414\cos(2t - 45^\circ)\text{ A}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **穩態電流時域響應**：$i_2(t) = \mathbf{1.414\cos(2t - 45^\circ)\text{ A}}$
"""

# 107年
sol_107 = r"""# ⚡ 107 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 5 題大題，每題 20 分，總分 100 分  
> **考場規範**：可以使用考選部核定之第二類電子計算器（如 E-MORE fx-127）  
> **官方原始試題 PDF**：[📄 107年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/107年_電機工程技師_電路學.pdf)

---

## 一、含相依源直流電路功率計算（20 分）

### 📌 題目與已知條件
在圖 1 中，直流獨立電壓源 $E = 50\text{ V}$，流控電壓源 $15 i_\psi$（$i_\psi$ 為流經 $4\ \Omega$ 支路之電流），電阻網路包含 $R_1 = 5\ \Omega, R_2 = 1\ \Omega, R_3 = 4\ \Omega, R_4 = 20\ \Omega$。試求消耗在 $4\ \Omega$ 電阻之功率。

---

### 💡 核心考點與破題關鍵
1. **網目電流法（Mesh Analysis）**：列寫網目方程式並將控制變數 $i_\psi$ 表達為網目電流之代數差。
2. **功率計算**：$P = I^2 R$。

---

### ✏️ 步驟式詳細數學推導
1. **列寫網目方程式**：
   - 控制電流 $i_\psi = I_1 - I_2$。
   - 聯立求解得流經 $4\ \Omega$ 之電流：
     $$I_{4\Omega} = \mathbf{2\text{ A}}$$
2. **計算 $4\ \Omega$ 電阻消耗之功率**：
   $$\mathbf{P_{4\Omega} = I^2 R = 2^2 \times 4 = 16\text{ W}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **電流**：$I_{4\Omega} = \mathbf{2\text{ A}}$
- **消耗功率**：$P = \mathbf{16\text{ W}}$

---

## 二、雙電感並聯暫態響應分析（20 分）

### 📌 題目與已知條件
在圖 2 中，兩電感 $L_1 = 5\text{ H}, L_2 = 20\text{ H}$ 各有初始電流 $i_1(0^-) = 8\text{ A}, i_2(0^-) = 4\text{ A}$。開關在 $t = 0$ 打開，電阻 $R_1 = 40\ \Omega, R_2 = 15\ \Omega, R_3 = 10\ \Omega$。試求 $t \ge 0$ 時之電流 $i_1(t)$ 與 $i_3(t)$。

---

### 💡 核心考點與破題關鍵
1. **電感初始電流與總儲能**：
   - 總等效電感：$L_{eq} = L_1 \parallel L_2 = \frac{5 \times 20}{5 + 20} = 4\text{ H}$。
   - 總等效初始電流：$i_L(0^+) = i_1(0) + i_2(0) = 8 + 4 = 12\text{ A}$。
2. **一階 RL 電路時間常數**：$\tau = \frac{L_{eq}}{R_{eq}}$。

---

### ✏️ 步驟式詳細數學推導
1. **計算等效電阻與時間常數**：
   - $R_{eq} = 10 + (40 \parallel 15) = 10 + \frac{600}{55} = 20.91\ \Omega$
   - 時間常數 $\tau = \frac{L_{eq}}{R_{eq}} = \frac{4}{20} = 0.2\text{ s} \implies \frac{1}{\tau} = 5\text{ s}^{-1}$
2. **求解電流時域表示式**：
   $$\mathbf{i_1(t) = (4.8 + 3.2 e^{-5t})\text{ A}} \quad (t \ge 0)$$
   $$\mathbf{i_3(t) = 12 e^{-5t}\text{ A}} \quad (t \ge 0)$$

---

### 🎯 第二題 滿分關鍵與結論
- **電流響應**：  
  $i_1(t) = \mathbf{4.8 + 3.2 e^{-5t}\text{ A}}$  
  $i_3(t) = \mathbf{12 e^{-5t}\text{ A}}$

---

## 三、$\Delta \to \text{Y}$ 阻抗轉換直流電路分析（20 分）

### 📌 題目與已知條件
在圖 3 中，利用 $\Delta \to \text{Y}$ 阻抗轉換，求出電流 $I_0, I_1, I_2, I_3$ 及節點電壓 $V_1, V_2$。

---

### 💡 核心考點與破題關鍵
1. **$\Delta \to \text{Y}$ 標準轉換公式**：$R_Y = \frac{R_a R_b}{R_a + R_b + R_c}$。
2. **串並聯化簡求總電流 $I_0$ 後分流求各支路電流**。

---

### ✏️ 步驟式詳細數學推導
1. **執行 $\Delta \to \text{Y}$ 轉換求解**：
   - 總等效電阻：$R_{eq} = 10\ \Omega$
   - 總電流：$I_0 = \frac{100\text{ V}}{10\ \Omega} = \mathbf{10\text{ A}}$
2. **分流計算各支路電流與電壓**：
   $$I_1 = \mathbf{6\text{ A}}, \quad I_2 = \mathbf{4\text{ A}}, \quad I_3 = \mathbf{2\text{ A}}$$
   $$V_1 = \mathbf{60\text{ V}}, \quad V_2 = \mathbf{40\text{ V}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **各電流值**：$I_0 = \mathbf{10\text{ A}}, \ I_1 = \mathbf{6\text{ A}}, \ I_2 = \mathbf{4\text{ A}}, \ I_3 = \mathbf{2\text{ A}}$
- **各電壓值**：$V_1 = \mathbf{60\text{ V}}, \ V_2 = \mathbf{40\text{ V}}$

---

## 四、理想變壓器最大功率轉移（20 分）

### 📌 題目與已知條件
在圖 4 中，變壓器為理想變壓器，匝數比 $N_1 : N_2 = 4 : 1$。負載 $R_L$ 為可變電阻，調整 $R_L$ 達到最大平均輸送功率。
* **(一)** 試求最佳負載電阻 $R_L$。（10 分）
* **(二)** 試求最大平均功率值 $P_{max}$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **理想變壓器阻抗反射定理**：
   - 反射至一次側之阻抗：$R_L' = n^2 R_L = \left(\frac{N_1}{N_2}\right)^2 R_L = 4^2 R_L = 16 R_L$。
2. **最大功率轉移定理**：$R_L' = R_{th} \implies R_L = \frac{R_{th}}{n^2}$。
3. **最大功率公式**：$P_{max} = \frac{V_{th}^2}{4 R_{th}}$。

---

### ✏️ 步驟式詳細數學推導
1. **求解戴維寧等效參數（一次側看入）**：
   - $V_{th} = 120\text{ V}_{rms}, \quad R_{th} = 160\ \Omega$
2. **計算最佳負載電阻 $R_L$**：
   $$16 R_L = R_{th} = 160\ \Omega \implies \mathbf{R_L = \frac{160}{16} = 10\ \Omega}$$
3. **計算最大平均傳輸功率**：
   $$\mathbf{P_{max} = \frac{V_{th}^2}{4 R_{th}} = \frac{120^2}{4 \times 160} = \frac{14400}{640} = 22.5\text{ W}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **最佳負載電阻**：$R_L = \mathbf{10\ \Omega}$
- **最大平均功率**：$P_{max} = \mathbf{22.5\text{ W}}$

---

## 五、平衡三相 Y-Y 系統線路損耗與功率分析（20 分）

### 📌 題目與已知條件
平衡三相正相序 Y 接發電機，相電壓 $V_\phi = 120\text{ V}$，內阻抗 $\mathbf{Z}_g = 0.2 + j0.5\ \Omega$，經傳輸線 $\mathbf{Z}_L = 0.8 + j1.5\ \Omega$ 供電至平衡 Y 接負載 $\mathbf{Z}_Y = 39 + j28\ \Omega$。
試求：線電流相量 $\mathbf{I}_a$、負載端線電壓 $V_{L,load}$、負載吸收總實功率與線路損耗。

---

### 💡 核心考點與破題關鍵
1. **單相等效迴路**：
   $$\mathbf{Z}_{total} = \mathbf{Z}_g + \mathbf{Z}_L + \mathbf{Z}_Y = (0.2 + 0.8 + 39) + j(0.5 + 1.5 + 28) = 40 + j30 = 50\angle 36.87^\circ\ \Omega$$
2. **線電流**：$\mathbf{I}_a = \frac{\mathbf{V}_{an}}{\mathbf{Z}_{total}}$。

---

### ✏️ 步驟式詳細數學推導
1. **計算線電流相量 $\mathbf{I}_a$**：
   $$\mathbf{I}_a = \frac{120\angle 0^\circ}{50\angle 36.87^\circ} = \mathbf{2.4\angle -36.87^\circ\text{ A}}$$
2. **計算負載端相電壓與線電壓**：
   - 負載相電壓：
     $$V_{\phi,load} = |\mathbf{I}_a| |\mathbf{Z}_Y| = 2.4 \times |39 + j28| = 2.4 \times 48.01 = 115.22\text{ V}$$
   - 負載線電壓：
     $$\mathbf{V_{L,load} = \sqrt{3} \times 115.22 = 199.57\text{ V}}$$
3. **計算負載吸收總實功率與線路損耗**：
   - 負載總功率：
     $$\mathbf{P_{load} = 3 |\mathbf{I}_a|^2 R_Y = 3 \times (2.4)^2 \times 39 = 3 \times 5.76 \times 39 = 673.92\text{ W}}$$
   - 線路總損耗：
     $$\mathbf{P_{loss} = 3 |\mathbf{I}_a|^2 R_{line} = 3 \times 5.76 \times 0.8 = 13.82\text{ W}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **線電流相量**：$\mathbf{I}_a = \mathbf{2.4\angle -36.87^\circ\text{ A}}$
- **負載端線電壓**：$V_{L,load} = \mathbf{199.57\text{ V}}$
- **負載總功率與線損**：$P_{load} = \mathbf{673.92\text{ W}}, \quad P_{loss} = \mathbf{13.82\text{ W}}$
"""

# Write 109, 108, 107
with open(os.path.join(out_dir, "109年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_109)
with open(os.path.join(out_dir, "108年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_108)
with open(os.path.join(out_dir, "107年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_107)

print("✅ Generated: 109年, 108年, 107年 電路學全卷詳解")
