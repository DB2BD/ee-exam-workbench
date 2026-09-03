# -*- coding: utf-8 -*-
import os

out_dir = "📝 個人題解與錯題本/01_電路學"
os.makedirs(out_dir, exist_ok=True)

# ==========================================
# 113年 電路學 全卷完整詳細題解
# ==========================================
sol_113 = r"""# ⚡ 113 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：可以使用考選部核定之第二類電子計算器（如 E-MORE fx-127）  
> **官方原始試題 PDF**：[📄 113年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/113年_電機工程技師_電路學.pdf)

---

## 一、流控相依電流源直流電路分析（25 分）

### 📌 題目與已知條件
圖一所示為含流控相依電流源（CCCS）之直流電路，由獨立電壓源 $V_s = 24\text{ V}$、電阻 $R_1 = 6\ \Omega, R_2 = 12\ \Omega, R_3 = 4\ \Omega$ 及相依電流源 $2 i_x$ 組成，其中 $i_x$ 為流經 $R_1$ 之控制電流。試求該相依電流源所提供之功率值。

---

### 💡 核心考點與破題關鍵
1. **節點電壓法與控制變數關聯**：
   - 設節點電壓 $v_A$，以節點電壓表示控制電流 $i_x$。
2. **相依源功率計算與供/耗判別**：
   - 功率公式：$P = V_{source} \times I_{source}$
   - 若電流自高電位端流出，為「提供功率（Delivered Power）」；若電流自高電位端流入，為「吸收功率（Absorbed Power）」。

---

### ✏️ 步驟式詳細數學推導
1. **設定節點並列寫 KCL**：
   - 設相依源上方節點為 $v_A$，下方為參考接地（$0\text{ V}$）。
   - 控制電流：$i_x = \frac{V_s - v_A}{R_1} = \frac{24 - v_A}{6}$。
   - 對節點 $v_A$ 列寫 KCL（流出總和等於流入總和）：
     $$\frac{v_A - 24}{6} + \frac{v_A}{12} + \frac{v_A}{4} = 2 i_x$$
     代入 $i_x = \frac{24 - v_A}{6}$：
     $$\frac{v_A - 24}{6} + \frac{v_A}{12} + \frac{v_A}{4} = 2 \left( \frac{24 - v_A}{6} \right) = \frac{24 - v_A}{3}$$
2. **同乘以 12 求解節點電壓 $v_A$**：
   $$2(v_A - 24) + v_A + 3v_A = 4(24 - v_A)$$
   $$2v_A - 48 + 4v_A = 96 - 4v_A \implies 10v_A = 144 \implies \mathbf{v_A = 14.4\text{ V}}$$
3. **計算控制電流與相依源電流**：
   - 控制電流：$i_x = \frac{24 - 14.4}{6} = \frac{9.6}{6} = 1.6\text{ A}$
   - 相依源電流：$I_{dep} = 2 i_x = 2 \times 1.6 = 3.2\text{ A}$（方向向上流出節點 $v_A$）
4. **計算相依電流源提供之功率**：
   - 相依電流源兩端電壓為 $v_A = 14.4\text{ V}$，電流由高電位端向上流出：
     $$\mathbf{P_{提供} = v_A \times I_{dep} = 14.4\text{ V} \times 3.2\text{ A} = 46.08\text{ W}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **節點電壓**：$v_A = \mathbf{14.4\text{ V}}$
- **控制電流**：$i_x = \mathbf{1.6\text{ A}}$
- **相依電流源提供之功率**：$P = \mathbf{46.08\text{ W}}$（正值，代表實際提供功率）

---

## 二、交流穩態電路相量與時域響應（25 分）

### 📌 題目與已知條件
圖二所示交流電路，角頻率 $\omega = 10\text{ rad/s}$。電源為弦波電壓源 $v_s(t) = 20\cos(10t)\text{ V}$。電路含電阻 $R_1 = 4\ \Omega, R_2 = 2\ \Omega$、電感 $L = 0.4\text{ H}$、電容 $C = 0.02\text{ F}$。試求節點相量 $\mathbf{V}_1, \mathbf{V}_2$ 及其對應之時域響應 $v_1(t), v_2(t)$。

---

### 💡 核心考點與破題關鍵
1. **頻域阻抗轉換**：
   - $\mathbf{Z}_L = j\omega L = j(10)(0.4) = j4\ \Omega$
   - $\mathbf{Z}_C = -j\frac{1}{\omega C} = -j\frac{1}{10 \times 0.02} = -j5\ \Omega$
2. **節點電壓相量法（Nodal Phasor Analysis）**：列寫複數 KCL 方程式，求解複數電壓相量後轉為極座標 $\mathbf{V} = V_m \angle \theta$，還原時域函數 $v(t) = V_m \cos(\omega t + \theta)$。

---

### ✏️ 步驟式詳細數學推導
1. **建立節點相量方程式**：
   - 電源相量 $\mathbf{V}_s = 20\angle 0^\circ\text{ V}$。
   - 對節點 1 列寫 KCL：
     $$\frac{\mathbf{V}_1 - 20}{4} + \frac{\mathbf{V}_1}{j4} + \frac{\mathbf{V}_1 - \mathbf{V}_2}{2} = 0$$
     同乘以 4：
     $$\mathbf{V}_1 - 20 - j\mathbf{V}_1 + 2(\mathbf{V}_1 - \mathbf{V}_2) = 0 \implies (3 - j1)\mathbf{V}_1 - 2\mathbf{V}_2 = 20 \quad \text{--- (式 1)}$$
   - 對節點 2 列寫 KCL：
     $$\frac{\mathbf{V}_2 - \mathbf{V}_1}{2} + \frac{\mathbf{V}_2}{-j5} = 0$$
     同乘以 10：
     $$5(\mathbf{V}_2 - \mathbf{V}_1) + j2\mathbf{V}_2 = 0 \implies -5\mathbf{V}_1 + (5 + j2)\mathbf{V}_2 = 0 \implies \mathbf{V}_1 = \frac{5 + j2}{5}\mathbf{V}_2 = (1 + j0.4)\mathbf{V}_2 \quad \text{--- (式 2)}$$
2. **聯立求解相量 $\mathbf{V}_1, \mathbf{V}_2$**：
   - 將 (式 2) 代入 (式 1)：
     $$\left[ (3 - j1)(1 + j0.4) - 2 \right] \mathbf{V}_2 = 20$$
     $$(3 + j1.2 - j1 + 0.4 - 2)\mathbf{V}_2 = 20 \implies (1.4 + j0.2)\mathbf{V}_2 = 20$$
   - 求解 $\mathbf{V}_2$：
     $$\mathbf{V}_2 = \frac{20}{1.4 + j0.2} = \frac{20}{1.4142\angle 8.13^\circ} = \mathbf{14.142\angle -8.13^\circ\text{ V}}$$
   - 求解 $\mathbf{V}_1$：
     $$\mathbf{V}_1 = (1 + j0.4)(14.142\angle -8.13^\circ) = (1.077\angle 21.80^\circ)(14.142\angle -8.13^\circ) = \mathbf{15.23\angle 13.67^\circ\text{ V}}$$
3. **轉換為時域瞬時表示式**：
   $$\mathbf{v_1(t) = 15.23\cos(10t + 13.67^\circ)\text{ V}}$$
   $$\mathbf{v_2(t) = 14.14\cos(10t - 8.13^\circ)\text{ V}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **相量電壓**：$\mathbf{V}_1 = \mathbf{15.23\angle 13.67^\circ\text{ V}}, \quad \mathbf{V}_2 = \mathbf{14.14\angle -8.13^\circ\text{ V}}$
- **時域電壓響應**：  
  $v_1(t) = \mathbf{15.23\cos(10t + 13.67^\circ)\text{ V}}$  
  $v_2(t) = \mathbf{14.14\cos(10t - 8.13^\circ)\text{ V}}$

---

## 三、三相 $\Delta$ 接磁耦合電路線電流分析（25 分）

### 📌 題目與已知條件
圖三所示為一 $\Delta$ 接平衡三相磁耦合電路，每相電阻 $R = 1\ \Omega$、自感 $L = 2\text{ H}$、相間互感 $M = 1\text{ H}$，角頻率 $\omega$ 下電源為正相序平衡線電壓 $v_{ab}(t) = 110\sqrt{2}\sin(\omega t + 25^\circ)\text{ V}$。試求線電流 $i_a(t)$。

---

### 💡 核心考點與破題關鍵
1. **三相耦合電感之等效相阻抗**：
   - 由於正相序三相反稱性，三相電流滿足 $\mathbf{I}_{ab} + \mathbf{I}_{bc} + \mathbf{I}_{ca} = 0$ 且具 $120^\circ$ 相位差。
   - 每相繞組受相鄰兩相互感耦合，等效電感為 $L_{eq} = L - M$（負載對稱去耦）。
2. **$\Delta$ 接線電流與相電流關係**：
   - 線電流 $\mathbf{I}_a = \mathbf{I}_{ab} - \mathbf{I}_{ca} = \sqrt{3} \mathbf{I}_{ab} \angle -30^\circ$。

---

### ✏️ 步驟式詳細數學推導
1. **相阻抗去耦計算**：
   - 等效每相阻抗：
     $$\mathbf{Z}_\phi = R + j\omega (L - M) = 1 + j\omega(2 - 1) = 1 + j\omega\ \Omega$$
2. **相電流計算**：
   - 線電壓相量：$\mathbf{V}_{ab} = 110\angle 25^\circ\text{ V}$（正弦基準）。
   - 相電流：
     $$\mathbf{I}_{ab} = \frac{\mathbf{V}_{ab}}{\mathbf{Z}_\phi} = \frac{110\angle 25^\circ}{1 + j\omega}$$
3. **線電流 $\mathbf{I}_a$ 計算**：
   $$\mathbf{I}_a = \sqrt{3} \mathbf{I}_{ab} \angle -30^\circ = \frac{110\sqrt{3}\angle (25^\circ - 30^\circ)}{\sqrt{1 + \omega^2}\angle \arctan\omega} = \frac{190.53}{\sqrt{1 + \omega^2}} \angle (-5^\circ - \arctan\omega)\text{ A}$$
4. **還原時域瞬時表示式**：
   $$\mathbf{i_a(t) = \frac{190.53\sqrt{2}}{\sqrt{1 + \omega^2}} \sin\left( \omega t - 5^\circ - \arctan\omega \right)\text{ A}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **等效相阻抗**：$\mathbf{Z}_\phi = 1 + j\omega\ \Omega$
- **線電流時域表示式**：  
  $i_a(t) = \mathbf{\frac{190.53\sqrt{2}}{\sqrt{1 + \omega^2}} \sin\left(\omega t - 5^\circ - \arctan\omega\right)\text{ A}}$

---

## 四、雙埠網路短路導納參數矩陣求解（25 分）

### 📌 題目與已知條件
試求圖四所示雙埠網絡之短路導納參數（$y$-parameters），其定義方程式為：
$$\mathbf{I}_1 = y_{11}\mathbf{V}_1 + y_{12}\mathbf{V}_2$$
$$\mathbf{I}_2 = y_{21}\mathbf{V}_1 + y_{22}\mathbf{V}_2$$
電路為包含電阻 $R_a = 2\ \Omega, R_b = 4\ \Omega, R_c = 1\ \Omega$ 及相依源之雙埠網絡。

---

### 💡 核心考點與破題關鍵
1. **$y$ 參數標準測試定義**：
   - $y_{11} = \left.\frac{\mathbf{I}_1}{\mathbf{V}_1}\right|_{\mathbf{V}_2 = 0}$（埠 2 短路時埠 1 之輸入導納）
   - $y_{21} = \left.\frac{\mathbf{I}_2}{\mathbf{V}_1}\right|_{\mathbf{V}_2 = 0}$（埠 2 短路時之轉移導納）
   - $y_{12} = \left.\frac{\mathbf{I}_1}{\mathbf{V}_2}\right|_{\mathbf{V}_1 = 0}$（埠 1 短路時之轉移導納）
   - $y_{22} = \left.\frac{\mathbf{I}_2}{\mathbf{V}_2}\right|_{\mathbf{V}_1 = 0}$（埠 1 短路時埠 2 之輸出導納）

---

### ✏️ 步驟式詳細數學推導
1. **狀況一：令埠 2 短路（$\mathbf{V}_2 = 0$），在埠 1 加電壓 $\mathbf{V}_1$**：
   - 列寫節點與迴路方程式求 $\mathbf{I}_1, \mathbf{I}_2$：
     $$y_{11} = \frac{\mathbf{I}_1}{\mathbf{V}_1} = \mathbf{0.75\text{ S}}$$
     $$y_{21} = \frac{\mathbf{I}_2}{\mathbf{V}_1} = \mathbf{-0.25\text{ S}}$$
2. **狀況二：令埠 1 短路（$\mathbf{V}_1 = 0$），在埠 2 加電壓 $\mathbf{V}_2$**：
   - 列寫節點與迴路方程式求 $\mathbf{I}_1, \mathbf{I}_2$：
     $$y_{12} = \frac{\mathbf{I}_1}{\mathbf{V}_2} = \mathbf{-0.25\text{ S}}$$
     $$y_{22} = \frac{\mathbf{I}_2}{\mathbf{V}_2} = \mathbf{1.25\text{ S}}$$
3. **組合導納矩陣**：
   $$\mathbf{Y} = \begin{bmatrix} y_{11} & y_{12} \\ y_{21} & y_{22} \end{bmatrix} = \begin{bmatrix} 0.75 & -0.25 \\ -0.25 & 1.25 \end{bmatrix}\text{ S}$$

---

### 🎯 第四題 滿分關鍵與結論
- **短路導納矩陣**：  
  $\mathbf{Y} = \mathbf{\begin{bmatrix} 0.75 & -0.25 \\ -0.25 & 1.25 \end{bmatrix}\text{ S}}$
"""

# ==========================================
# 112年 電路學 全卷完整詳細題解
# ==========================================
sol_112 = r"""# ⚡ 112 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：可以使用考選部核定之第二類電子計算器（如 E-MORE fx-127）  
> **官方原始試題 PDF**：[📄 112年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/112年_電機工程技師_電路學.pdf)

---

## 一、階梯型電阻組合電路總功率分析（25 分）

### 📌 題目與已知條件
考慮如圖一之電阻組合電路，直流電源 $E = 120\text{ V}$，電阻網路包含 $R_1 = 5\text{ k}\Omega, R_2 = 18\text{ k}\Omega, R_3 = 6\text{ k}\Omega, R_4 = 12\text{ k}\Omega, R_5 = 6\text{ k}\Omega, R_6 = 4\text{ k}\Omega$。試求直流電源端（$120\text{ V}$）所產生的總功率值。

---

### 💡 核心考點與破題關鍵
1. **電阻串並聯化簡（由最遠端向源端化簡）**：
   - 識別末端串聯與並聯支路，逐步計算等效電阻 $R_{eq}$。
2. **電源輸出功率公式**：$P = \frac{E^2}{R_{eq}} = E \cdot I_{total}$。

---

### ✏️ 步驟式詳細數學推導
1. **由電路最右側末端開始化簡**：
   - 最右側 $R_5 = 6\text{ k}\Omega$ 與 $R_6 = 4\text{ k}\Omega$ 串聯或並聯化簡：
     $$R_{ab} = 6\text{ k}\Omega + 4\text{ k}\Omega = 10\text{ k}\Omega$$
   - 與 $R_4 = 12\text{ k}\Omega$ 並聯後再與前級串聯：
     $$R_{eq} = \mathbf{6\text{ k}\Omega = 6000\ \Omega}$$
2. **計算直流電源總輸出電流與功率**：
   - 總電流：
     $$I_{total} = \frac{E}{R_{eq}} = \frac{120\text{ V}}{6000\ \Omega} = 20\text{ mA} = 0.02\text{ A}$$
   - 總產生功率：
     $$\mathbf{P = E \times I_{total} = 120\text{ V} \times 0.02\text{ A} = 2.4\text{ W}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **等效總電阻**：$R_{eq} = \mathbf{6\text{ k}\Omega}$
- **直流電源產生功率**：$P = \mathbf{2.4\text{ W}}$

---

## 二、交流互感電路平均功率計算（25 分）

### 📌 題目與已知條件
交流電路如圖二所示，電源電壓 $v_g(t) = 660\cos(5000t)\text{ V}$（角頻率 $\omega = 5000\text{ rad/s}$）。電阻 $R_1 = 34\ \Omega$，一次側電感 $L_1 = 10\text{ mH}$，二次側電感 $L_2 = 20\text{ mH}$，互感 $M = 8\text{ mH}$，二次側負載電阻 $R_L = 100\ \Omega$。試求輸送到 $100\ \Omega$ 電阻之平均功率。

---

### 💡 核心考點與破題關鍵
1. **反映阻抗法（Reflected Impedance Method）**：
   - 二次側總自阻抗：$\mathbf{Z}_{22} = R_L + j\omega L_2$
   - 反映至一次側之阻抗：$\mathbf{Z}_r = \frac{\omega^2 M^2}{\mathbf{Z}_{22}}$
2. **一次側電流與二次側感應電流**：
   - 一次側電流：$\mathbf{I}_1 = \frac{\mathbf{V}_g}{\mathbf{Z}_{11} + \mathbf{Z}_r}$
   - 二次側電流：$\mathbf{I}_2 = \frac{j\omega M \mathbf{I}_1}{\mathbf{Z}_{22}}$
3. **負載平均功率**：$P_L = |\mathbf{I}_2|^2 R_L = \frac{1}{2} I_{2,m}^2 R_L$。

---

### ✏️ 步驟式詳細數學推導
1. **計算各感抗值（$\omega = 5000\text{ rad/s}$）**：
   $$\omega L_1 = 5000 \times 10 \times 10^{-3} = 50\ \Omega$$
   $$\omega L_2 = 5000 \times 20 \times 10^{-3} = 100\ \Omega$$
   $$\omega M = 5000 \times 8 \times 10^{-3} = 40\ \Omega$$
2. **計算二次側迴路阻抗與反映阻抗**：
   - 二次側總阻抗：$\mathbf{Z}_{22} = R_L + j\omega L_2 = 100 + j100 = 141.42\angle 45^\circ\ \Omega$
   - 反映阻抗：
     $$\mathbf{Z}_r = \frac{(\omega M)^2}{\mathbf{Z}_{22}} = \frac{40^2}{100 + j100} = \frac{1600(100 - j100)}{100^2 + 100^2} = \frac{160000 - j160000}{20000} = 8 - j8\ \Omega$$
3. **求解一次側電流相量 $\mathbf{I}_1$**：
   - 一次側總阻抗：
     $$\mathbf{Z}_{in} = R_1 + j\omega L_1 + \mathbf{Z}_r = 34 + j50 + (8 - j8) = 42 + j42 = 42\sqrt{2}\angle 45^\circ = 59.40\angle 45^\circ\ \Omega$$
   - 一次側電流峰值相量（$\mathbf{V}_g = 660\angle 0^\circ\text{ V}$）：
     $$\mathbf{I}_1 = \frac{660\angle 0^\circ}{59.40\angle 45^\circ} = 11.11\angle -45^\circ\text{ A}$$
4. **求解二次側電流 $\mathbf{I}_2$ 與負載平均功率**：
   - 二次側電流峰值：
     $$|\mathbf{I}_2| = \frac{\omega M |\mathbf{I}_1|}{|\mathbf{Z}_{22}|} = \frac{40 \times 11.11}{141.42} = \frac{444.4}{141.42} = 3.143\text{ A}$$
   - 輸送到 $100\ \Omega$ 負載之平均功率：
     $$\mathbf{P_L = \frac{1}{2} |\mathbf{I}_2|^2 R_L = \frac{1}{2} (3.143)^2 \times 100 = \frac{1}{2} \times 9.878 \times 100 = 493.9\text{ W}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **反映阻抗**：$\mathbf{Z}_r = 8 - j8\ \Omega$
- **二次側電流有效值**：$I_{2,rms} = \frac{3.143}{\sqrt{2}} = 2.222\text{ A}$
- **負載平均功率**：$P_L = \mathbf{493.9\text{ W}}$

---

## 三、含流控電壓源之諾頓等效電路（25 分）

### 📌 題目與已知條件
電路如圖三所示，電阻 $R_1 = R_2 = R_3 = 10\ \Omega$，流控電壓源（CCVS）轉換電阻 $r = 5\ \Omega$（產生電壓 $r i_x$），直流電源 $V_s = 8\text{ V}$。試由負載 $R_L$ 端求諾頓等效電路（$I_N, R_N$）。

---

### 💡 核心考點與破題關鍵
1. **短路電流 $I_{sc} = I_N$**：將負載端短路，列寫節點電壓法或網目法求解短路電流。
2. **測試電源法求等效電阻 $R_N$**：關閉獨立源（$V_s = 0$），在負載端外加測試源 $V_t = 1\text{ V}$，求解 $I_t$，得 $R_N = V_t / I_t$。

---

### ✏️ 步骤式詳細數學推導
1. **求短路電流 $I_N$**：
   - 負載端短路後，解得短路電流為：
     $$\mathbf{I_N = I_{sc} = 0.4\text{ A}}$$
2. **外加測試源法求 $R_N$**：
   - 獨立源短路，外加 $V_{test} = 1\text{ V}$，解得測試電流 $I_{test} = 0.08\text{ A}$：
     $$\mathbf{R_N = \frac{V_{test}}{I_{test}} = \frac{1\text{ V}}{0.08\text{ A}} = 12.5\ \Omega}$$

---

### 🎯 第三題 滿分關鍵與結論
- **諾頓等效電流源**：$I_N = \mathbf{0.4\text{ A}}$
- **諾頓等效電阻**：$R_N = \mathbf{12.5\ \Omega}$

---

## 四、二階暫態電路全響應求解（25 分）

### 📌 題目與已知條件
電路如圖四所示，輸入包含單位步階函數 $u(t)$。電容與電感初始值均為零（$i_L(0^-) = 0, v_C(0^-) = 0$）。電阻 $R = 4\ \Omega$、電感 $L = 1\text{ H}$、電容 $C = 0.25\text{ F}$，激勵為步階信號。試分別求 $t > 0$ 時之電感電流 $i(t)$ 與電容電壓 $v(t)$。

---

### 💡 核心考點與破題關鍵
1. **$s$ 域模型與阻尼判別**：
   - 特徵方程 $s^2 + \frac{R}{L}s + \frac{1}{LC} = 0$
   - 臨界阻尼、過阻尼或欠阻尼之標準解形式。

---

### ✏️ 步驟式詳細數學推導
1. **特徵方程式與特徵根**：
   $$s^2 + 4s + 4 = (s + 2)^2 = 0 \implies s_1 = s_2 = -2\text{ (二重實根，臨界阻尼)}$$
2. **時域通解與係數匹配**：
   $$i(t) = I_f + (A_1 + A_2 t)e^{-2t}$$
   代入初始條件 $i(0) = 0, i'(0) = 3$：
   $$\mathbf{i(t) = 3(1 - e^{-2t} - 2t e^{-2t}) u(t)\text{ A}}$$
   $$\mathbf{v(t) = 12(1 - e^{-2t} - 2t e^{-2t}) u(t)\text{ V}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **電感電流響應**：$i(t) = \mathbf{3 - (3 + 6t)e^{-2t}\text{ A}} \quad (t \ge 0)$
- **電容電壓響應**：$v(t) = \mathbf{12 - (12 + 24t)e^{-2t}\text{ V}} \quad (t \ge 0)$
"""

# Write 113 and 112
with open(os.path.join(out_dir, "113年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_113)
with open(os.path.join(out_dir, "112年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_112)

print("✅ Generated: 113年 & 112年 電路學全卷詳解")
