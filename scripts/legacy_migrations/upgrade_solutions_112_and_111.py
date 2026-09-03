# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 112 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_112 = r'''---
考科: 電力系統
年份: 112
主題: 112 年 電力系統 全卷四大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、四分裂導線換位輸電線路電感與電容計算 (4-Bundle GMD & GMR)
  - 二、等微增燃料成本最佳經濟調度係數求解 (Economic Dispatch Inversion)
  - 三、含變壓器分接頭之四匯流排節點導納矩陣 Ybus (Tap Changer Ybus)
  - 四、單機無窮母線系統等面積準則與臨界清除角 (Equal-Area SMIB Transient Stability)
難易度: ⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 112 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 112 年 電力系統 試題導覽清單
- [👉 第一題：四分裂導線換位輸電線路電感與電容計算（25 分）](#一四分裂導線換位輸電線路電感與電容計算25-分)
- [👉 第二題：等微增燃料成本最佳經濟調度係數求解（25 分）](#二等微增燃料成本最佳經濟調度係數求解25-分)
- [👉 第三題：含變壓器分接頭之四匯流排節點導納矩陣 Ybus（25 分）](#三含變壓器分接頭之四匯流排節點導納矩陣-ybus25-分)
- [👉 第四題：單機無窮母線系統等面積準則與臨界清除角（25 分）](#四單機無窮母線系統等面積準則與臨界清除角25-分)

---

## 一、四分裂導線換位輸電線路電感與電容計算（25 分）

### 📌 題目與已知條件
![[112年_電力系統_第1題_圖一四分裂導線.png|750]]
*圖：112年電力系統第一題 圖一 四分裂導線水平換位排列幾何圖*

一條單回路三相完全換位輸電線路，相間水平距離 $D = 10\text{ m} = 1000\text{ cm}$。
- 每相由 4 條 ACSR 1,272,000 cmil 導線組成四分裂導線，正方形捆紮間距 $d = 50\text{ cm} = 0.50\text{ m}$。
- 導線外徑 $2r = 3.5103\text{ cm} \implies r = 1.75515\text{ cm} = 0.0175515\text{ m}$。
- 單導線幾何平均半徑 $\text{GMR}_s = 1.4173\text{ cm} = 0.014173\text{ m}$。

**試決定**：此輸電線每相每公里之電感值 $L$（$\text{mH/km}$）及電容值 $C$（$\mu\text{F/km}$）。（25 分）

---

### 💡 核心考點與破題關鍵
1. **水平排列幾何平均距離 $\text{GMD}$**：
   $$\text{GMD} = \sqrt[3]{D_{ab} D_{bc} D_{ca}} = \sqrt[3]{D \cdot D \cdot 2D} = \sqrt[3]{2} D = \sqrt[3]{2} \times 10\text{ m} \approx 12.5992\text{ m}$$
2. **四分裂導線等效幾何平均半徑 $\text{GMR}_L$（計算電感）**：
   正方形四頂點導線間距分別為 $d, d, \sqrt{2}d$，故等效半徑為：
   $$\text{GMR}_L = \sqrt[4]{\text{GMR}_s \cdot d \cdot d \cdot \sqrt{2}d} = 2^{1/8} \cdot (\text{GMR}_s \cdot d^3)^{1/4}$$
3. **四分裂導線等效半徑 $\text{GMR}_C$（計算電容）**：
   $$\text{GMR}_C = \sqrt[4]{r \cdot d \cdot d \cdot \sqrt{2}d} = 2^{1/8} \cdot (r \cdot d^3)^{1/4}$$
4. **每公里電感與電容標準公式**：
   $$L = 0.2 \ln\left(\frac{\text{GMD}}{\text{GMR}_L}\right)\text{ mH/km}, \quad C = \frac{0.0556}{\ln(\text{GMD}/\text{GMR}_C)}\ \mu\text{F/km}$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算 $\text{GMD}$ 與四分裂導線之 $\text{GMR}_L, \text{GMR}_C$
1. **幾何平均距離**：
   $$\text{GMD} = \sqrt[3]{10 \times 10 \times 20} = \sqrt[3]{2000} \approx \mathbf{12.5992\text{ m}}$$
2. **電感幾何平均半徑 $\text{GMR}_L$**：
   $$\text{GMR}_L = \sqrt[4]{0.014173 \times (0.50)^3 \times \sqrt{2}} = \sqrt[4]{0.014173 \times 0.125 \times 1.414214} = \sqrt[4]{2.5054 \times 10^{-3}} \approx \mathbf{0.22384\text{ m}}$$
3. **電容幾何平均半徑 $\text{GMR}_C$**：
   $$\text{GMR}_C = \sqrt[4]{0.0175515 \times (0.50)^3 \times \sqrt{2}} = \sqrt[4]{0.0175515 \times 0.125 \times 1.414214} = \sqrt[4]{3.1027 \times 10^{-3}} \approx \mathbf{0.23602\text{ m}}$$

#### 步驟 2：計算每相每公里電感值 $L$
$$L = 0.2 \ln\left(\frac{12.5992}{0.22384}\right) = 0.2 \ln(56.2866) = 0.2 \times 4.03046 = \mathbf{0.8061\text{ mH/km}}$$

#### 步驟 3：計算每相每公里電容值 $C$
$$C = \frac{2\pi \times 8.854 \times 10^{-12} \times 10^3}{\ln\left(\frac{12.5992}{0.23602}\right)} = \frac{5.5633 \times 10^{-8}}{\ln(53.3819)} = \frac{5.5633 \times 10^{-8}}{3.97745} \approx \mathbf{0.01399\ \mu\text{F/km}} = \mathbf{13.99\text{ nF/km}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **三相等效距離**：$\text{GMD} = 12.599\text{ m}$
- **每相每公里電感值**：$L = \mathbf{0.8061\text{ mH/km}}$
- **每相每公里電容值**：$C = \mathbf{0.01399\ \mu\text{F/km}}$（$13.99\text{ nF/km}$）

---

## 二、等微增燃料成本最佳經濟調度係數求解（25 分）

### 📌 題目與已知條件
兩部發電機組供應電力系統，各機組之微增燃料成本為發電功率之線性函數：
$$\text{IC}_1 = a_1 P_1 + b_1\quad (\$/\text{MWh}), \quad \text{IC}_2 = a_2 P_2 + b_2\quad (\$/\text{MWh})$$
- 情況 1：當系統總負載為 $P_D^{(1)} = 400\text{ MW}$ 時，最佳經濟調度發電量為 $P_1 = 150\text{ MW}, P_2 = 250\text{ MW}$，系統增量成本為 $\lambda^{(1)} = 20\ \$/\text{MWh}$。
- 情況 2：當系統總負載增加至 $P_D^{(2)} = 600\text{ MW}$ 時，最佳經濟調度發電量為 $P_1 = 250\text{ MW}, P_2 = 350\text{ MW}$，系統增量成本為 $\lambda^{(2)} = 26\ \$/\text{MWh}$。

* **(一)** 試求兩機組微增成本函數之待定係數 $a_1, b_1, a_2, b_2$。（15 分）
* **(二)** 若總負載為 $P_D = 800\text{ MW}$，求兩機組之最佳發電分配及系統邊際成本 $\lambda$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **等微增成本聯立方程**：
   在最佳經濟調度下，$\text{IC}_1(P_1) = \text{IC}_2(P_2) = \lambda$。
2. **利用兩組運轉點建立 4 個線性方程**：
   - 點 1：$150 a_1 + b_1 = 20$，$250 a_2 + b_2 = 20$。
   - 點 2：$250 a_1 + b_1 = 26$，$350 a_2 + b_2 = 26$。

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：求解微增成本係數
1. **求解機組 1 參數 $a_1, b_1$**：
   $$\begin{cases} 150 a_1 + b_1 = 20 \\ 250 a_1 + b_1 = 26 \end{cases}$$
   兩式相減：$100 a_1 = 6 \implies \mathbf{a_1 = 0.06\ \$/\text{MW}^2\text{h}}$
   代入求 $b_1$：$b_1 = 20 - 150(0.06) = 20 - 9 = \mathbf{11.0\ \$/\text{MWh}}$
   $$\mathbf{\text{IC}_1 = 0.06 P_1 + 11.0}$$
2. **求解機組 2 參數 $a_2, b_2$**：
   $$\begin{cases} 250 a_2 + b_2 = 20 \\ 350 a_2 + b_2 = 26 \end{cases}$$
   兩式相減：$100 a_2 = 6 \implies \mathbf{a_2 = 0.06\ \$/\text{MW}^2\text{h}}$
   代入求 $b_2$：$b_2 = 20 - 250(0.06) = 20 - 15 = \mathbf{5.0\ \$/\text{MWh}}$
   $$\mathbf{\text{IC}_2 = 0.06 P_2 + 5.0}$$

---

#### 🔹 第 (二) 小題：求解 $P_D = 800\text{ MW}$ 時之最佳調度
1. **由等微增準則表示發電量**：
   $$P_1 = \frac{\lambda - 11}{0.06}, \quad P_2 = \frac{\lambda - 5}{0.06}$$
2. **代入總功率平衡**：
   $$P_1 + P_2 = \frac{2\lambda - 16}{0.06} = 800 \implies 2\lambda - 16 = 48 \implies 2\lambda = 64 \implies \mathbf{\lambda = 32.0\ \$/\text{MWh}}$$
3. **計算各機組發電量**：
   $$P_1 = \frac{32 - 11}{0.06} = \frac{21}{0.06} = \mathbf{350.0\text{ MW}}$$
   $$P_2 = \frac{32 - 5}{0.06} = \frac{27}{0.06} = \mathbf{450.0\text{ MW}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **機組 1 微增成本**：$\text{IC}_1 = 0.06 P_1 + 11.0\ \$/\text{MWh}$
- **機組 2 微增成本**：$\text{IC}_2 = 0.06 P_2 + 5.0\ \$/\text{MWh}$
- **800 MW 最佳分配**：$P_1 = \mathbf{350\text{ MW}}, P_2 = \mathbf{450\text{ MW}}, \lambda = \mathbf{32\ \$/\text{MWh}}$

---

## 三、含變壓器分接頭之四匯流排節點導納矩陣 Ybus（25 分）

### 📌 題目與已知條件
![[112年_電力系統_第3題_圖二4Bus單線圖.png|750]]
*圖：112年電力系統第三題 圖二 4-Bus 電力系統含變壓器分接頭單線圖*

如下圖所示為一個 4-Bus 電力系統：
- 輸電線阻抗：$z_{12} = j0.10\text{ pu}, z_{23} = j0.20\text{ pu}, z_{34} = j0.10\text{ pu}$。
- 變壓器 $T_1$ 連接於 Bus 1 與 Bus 3 之間，漏電抗 $x_T = 0.10\text{ pu}$（$y_T = -j10\text{ pu}$），分接頭（Tap）位於 Bus 1 側，變比為 $a : 1 = 1.05 : 1$。
- 各匯流排無對地並聯導納。

**試建立**：此系統完整的 $4\times 4$ 節點導納矩陣 $\mathbf{Y}_{bus}$。（25 分）

---

### 💡 核心考點與破題關鍵
1. **含非額定變比變壓器 $\pi$ 型等效電路模型**：
   若變壓器串聯導納為 $y$，分接頭 $a : 1$ 位於節點 $i$ 側：
   $$\mathbf{Y}_{branch} = \begin{bmatrix} \frac{y}{a^2} & -\frac{y}{a} \\ -\frac{y}{a} & y \end{bmatrix} = \begin{bmatrix} y_{ii} & y_{ij} \\ y_{ji} & y_{jj} \end{bmatrix}$$
2. **標準節點導納矩陣元素合成法**：
   - 對角線元素 $Y_{kk}$：連接至節點 $k$ 之所有導納總和。
   - 非對角線元素 $Y_{km} = -y_{km}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算各支路導納
- 線路導納：
  $$y_{12} = \frac{1}{j0.10} = -j10\text{ pu}$$
  $$y_{23} = \frac{1}{j0.20} = -j5\text{ pu}$$
  $$y_{34} = \frac{1}{j0.10} = -j10\text{ pu}$$
- 變壓器支路（Bus 1 至 Bus 3，$a = 1.05$）：
  $$y_{11}^{(T)} = \frac{-j10}{(1.05)^2} = \frac{-j10}{1.1025} \approx \mathbf{-j9.0703\text{ pu}}$$
  $$y_{13}^{(T)} = y_{31}^{(T)} = -\left(\frac{-j10}{1.05}\right) = \mathbf{j9.5238\text{ pu}} \implies Y_{13} = -\frac{y}{a} = \mathbf{j9.5238\text{ pu}}$$
  $$y_{33}^{(T)} = -j10\text{ pu}$$

#### 步驟 2：合成 $\mathbf{Y}_{bus}$ 矩陣元素
1. **自導納（對角項）**：
   - $Y_{11} = y_{12} + y_{11}^{(T)} = -j10 + (-j9.0703) = \mathbf{-j19.0703\text{ pu}}$
   - $Y_{22} = y_{12} + y_{23} = -j10 + (-j5) = \mathbf{-j15.0\text{ pu}}$
   - $Y_{33} = y_{23} + y_{34} + y_{33}^{(T)} = -j5 + (-j10) + (-j10) = \mathbf{-j25.0\text{ pu}}$
   - $Y_{44} = y_{34} = \mathbf{-j10.0\text{ pu}}$
2. **互導納（非對角項）**：
   - $Y_{12} = Y_{21} = -y_{12} = \mathbf{j10.0\text{ pu}}$
   - $Y_{13} = Y_{31} = \frac{y_T}{a} = \frac{-j10}{1.05} = \mathbf{j9.5238\text{ pu}}$
   - $Y_{23} = Y_{32} = -y_{23} = \mathbf{j5.0\text{ pu}}$
   - $Y_{34} = Y_{43} = -y_{34} = \mathbf{j10.0\text{ pu}}$
   - 其餘無直接連接元素均為 $0$。

#### 步驟 3：寫出完整 $\mathbf{Y}_{bus}$ 矩陣
$$\mathbf{Y}_{bus} = \begin{bmatrix}
-j19.0703 & j10.0000 & j9.5238 & 0 \\
j10.0000 & -j15.0000 & j5.0000 & 0 \\
j9.5238 & j5.0000 & -j25.0000 & j10.0000 \\
0 & 0 & j10.0000 & -j10.0000
\end{bmatrix}\text{ pu}$$

---

### 🎯 第三題 滿分關鍵與結論
- **變壓器分接頭 $\pi$ 模型公式**：$Y_{11}^{(T)} = y/a^2 = -j9.0703, Y_{13} = j9.5238$
- 矩陣對稱且符合物理守恆！

---

## 四、單機無窮母線系統等面積準則與臨界清除角（25 分）

### 📌 題目與已知條件
![[112年_電力系統_第4題_圖三單機無窮母線圖.png|750]]
*圖：112年電力系統第四題 圖三 單機無窮母線暫態穩定度系統圖*

一部同步發電機經由兩條並聯輸電線連接至無窮母線（Infinite Bus）：
- 無窮母線電壓 $V = 1.0\angle 0^\circ\text{ pu}$。
- 發電機暫態內電勢 $E' = 1.25\angle \delta\text{ pu}$。
- 故障前系統總轉移電抗為 $X_1 = 0.50\text{ pu}$。
- 在其中一條輸電線之中點發生三相金屬性短路故障，故障期間之轉移電抗為 $X_2 = 1.25\text{ pu}$。
- 故障清除後，跳脫故障線路（單迴線運轉），轉移電抗變為 $X_3 = 0.80\text{ pu}$。
- 故障前發電機輸出實功率為 $P_m = 1.0\text{ pu}$。

**試求**：利用等面積準則（Equal-Area Criterion）計算系統維持暫態穩定之**臨界清除角 $\delta_{cr}$**。（25 分）

---

### 💡 核心考點與破題關鍵
1. **各階段功率-角度曲線**：
   - 故障前（Prefault）：$P_{e1}(\delta) = \frac{E'V}{X_1}\sin\delta = \frac{1.25\times 1.0}{0.50}\sin\delta = 2.50\sin\delta$
   - 故障中（Faulted）：$P_{e2}(\delta) = \frac{E'V}{X_2}\sin\delta = \frac{1.25\times 1.0}{1.25}\sin\delta = 1.00\sin\delta$
   - 故障切除後（Postfault）：$P_{e3}(\delta) = \frac{E'V}{X_3}\sin\delta = \frac{1.25\times 1.0}{0.80}\sin\delta = 1.5625\sin\delta$
2. **關鍵角度計算**：
   - 初始角 $\delta_0$：$2.50\sin\delta_0 = 1.0 \implies \delta_0 = \sin^{-1}(0.40) \approx 0.4115\text{ rad} = 23.58^\circ$。
   - 最大擺動角 $\delta_{max}$：$1.5625\sin\delta_{max} = 1.0 \implies \delta_{max} = \pi - \sin^{-1}(0.64) = \pi - 0.6945 = 2.4471\text{ rad} = 140.21^\circ$。
3. **等面積準則積分平衡式**：
   $$\text{加速面積 } A_1 = \int_{\delta_0}^{\delta_{cr}} (P_m - P_{e2}) d\delta = \text{減速面積 } A_2 = \int_{\delta_{cr}}^{\delta_{max}} (P_{e3} - P_m) d\delta$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：建立等面積平衡方程式
$$\int_{\delta_0}^{\delta_{cr}} (1.0 - 1.0\sin\delta) d\delta = \int_{\delta_{cr}}^{\delta_{max}} (1.5625\sin\delta - 1.0) d\delta$$
展開左式（加速面積 $A_1$）：
$$A_1 = [\delta + \cos\delta]_{\delta_0}^{\delta_{cr}} = (\delta_{cr} - \delta_0) + (\cos\delta_{cr} - \cos\delta_0)$$
展開右式（減速面積 $A_2$）：
$$A_2 = [-1.5625\cos\delta - \delta]_{\delta_{cr}}^{\delta_{max}} = 1.5625(\cos\delta_{cr} - \cos\delta_{max}) - (\delta_{max} - \delta_{cr})$$

#### 步驟 2：移項整理求解 $\cos\delta_{cr}$
$$(\delta_{cr} - \delta_0) + \cos\delta_{cr} - \cos\delta_0 = 1.5625\cos\delta_{cr} - 1.5625\cos\delta_{max} - \delta_{max} + \delta_{cr}$$
兩邊消去 $\delta_{cr}$：
$$\cos\delta_{cr}(1.5625 - 1.0) = P_m(\delta_{max} - \delta_0) + 1.5625\cos\delta_{max} - \cos\delta_0$$
$$0.5625 \cos\delta_{cr} = 1.0(2.4471 - 0.4115) + 1.5625\cos(140.21^\circ) - \cos(23.58^\circ)$$
代入數值：
- $\cos(140.21^\circ) = -0.7684$
- $\cos(23.58^\circ) = 0.9165$
$$0.5625 \cos\delta_{cr} = 2.0356 + 1.5625(-0.7684) - 0.9165 = 2.0356 - 1.2006 - 0.9165 = -0.0815$$
$$\cos\delta_{cr} = \frac{-0.0815}{0.5625} \approx -0.14489$$
$$\mathbf{\delta_{cr} = \cos^{-1}(-0.14489) \approx 1.7162\text{ rad} = 98.33^\circ}$$

---

### 🎯 第四題 滿分關鍵與結論
- **初始功角**：$\delta_0 = 23.58^\circ$（$0.4115\text{ rad}$）
- **最大容許擺動角**：$\delta_{max} = 140.21^\circ$（$2.4471\text{ rad}$）
- **臨界清除角**：$\mathbf{\delta_{cr} = 98.33^\circ}$（$1.716\text{ rad}$）
'''

with open('📝 個人題解與錯題本/05_電力系統/112年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_112)

print('✅ 112年_電力系統_全卷完整詳細題解.md upgraded to gold standard!')

# ==============================================================================
# 111 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_111 = r'''---
考科: 電力系統
年份: 111
主題: 111 年 電力系統 全卷四大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、輸電線路串聯電容補償原理與次同步諧振 (Series Compensation & SSR)
  - 二、五匯流排阻抗矩陣 Zbus 三相短路故障計算 (5-Bus Zbus Fault Analysis)
  - 三、等面積準則臨界清除角與臨界清除時間 (Equal-Area CCT & tc)
  - 四、長程輸電線路雙曲函數精確 ABCD 參數與電壓調整率 (Hyperbolic Exact ABCD Line)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 111 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 111 年 電力系統 試題導覽清單
- [👉 第一題：輸電線路串聯電容補償原理與功用（20 分）](#一輸電線路串聯電容補償原理與功用20-分)
- [👉 第二題：五匯流排阻抗矩陣 Zbus 三相短路故障計算（30 分）](#二五匯流排阻抗矩陣-zbus-三相短路故障計算30-分)
- [👉 第三題：等面積準則臨界清除角與臨界清除時間（25 分）](#三等面積準則臨界清除角與臨界清除時間25-分)
- [👉 第四題：長程輸電線路 ABCD 參數與電壓調整率（25 分）](#四長程輸電線路-abcd-參數與電壓調整率25-分)

---

## 一、輸電線路串聯電容補償原理與功用（20 分）

### 📌 題目與說明
* **(一)** 何謂輸電線路的串聯電容補償？其主要功用為何？（10 分）
* **(二)** 串聯補償可能引起何種系統不良效應？應如何防範？（10 分）

---

### 💡 核心考點與破題關鍵
1. **串聯補償之定義與傳輸能力提升**：
   - 串聯電容器（$X_C$）串接於線路中，有效電抗減為 $X_{eff} = X_L - X_C = X_L(1 - k_{comp})$。
   - 最大傳輸實功率提升至：$P_{max} = \frac{V_S V_R}{X_L(1 - k_{comp})} > \frac{V_S V_R}{X_L}$。
2. **次同步諧振（Subsynchronous Resonance, SSR）**：
   - 串聯電容與線路電感構成天然 $LC$ 諧振迴路，其固有共振頻率為次同步頻率：
     $$f_r = f_0 \sqrt{\frac{X_C}{X_L}} < f_0 = 60\text{ Hz}$$
   - 當 $f_0 - f_r$ 恰好耦合汽輪發電機軸系之機械扭轉共振頻率時，會產生負阻尼扭力，導致發電機轉軸扭斷！

---

### ✏️ 完整標準解答

#### 🔹 第 (一) 小題：串聯補償之定義與四大主要功用
1. **定義**：在超高壓長距離輸電線路相導線中串聯適當容量之電力電容器組。
2. **四大主要功用**：
   - ① **大幅提高穩態功率傳輸極限**：降低等效傳輸阻抗，提升線路熱極限與穩定度極限。
   - ② **增強系統暫態穩定度**：故障清除後提供更強的同步化功率（Synchronizing Power）。
   - ③ **降低線路電壓降**：補償大部分感抗壓降，改善受電端電壓輪廓。
   - ④ **靈活調節並聯線路負載潮流分配**：避免並聯線路出現輕重載不均。

---

#### 🔹 第 (二) 小題：不良效應（次同步諧振 SSR）與四大防範對策
1. **不良效應**：
   - **次同步諧振（SSR）**：電氣諧振頻率 $f_r < 60\text{ Hz}$ 與發電機軸系多質量塊固有扭轉頻率（Torsional Frequency）發生共振耦合，引發轉軸疲勞破壞。
   - **自激現象（Self-Excitation / Induction Generator Effect）**。
   - **保護電驛誤動作**：電容器造成線路阻抗變號（電壓反轉），干擾距離電驛（Distance Relay）測距方向。
2. **防範對策**：
   - ① **裝設 FACTS 彈性交流輸電元件**：如閘流體控制串聯電容器（TCSC），動態調諧阻抗以破壞諧振條件。
   - ② **加裝次同步阻尼濾波器（SSDF / NGH Damping Scheme）**。
   - ③ **發電機裝設次同步保護電驛（SSR Protective Relay）**。
   - ④ **限制串聯補償度**（通常控制在 $k_{comp} \le 50\%\sim 70\%$）。

---

## 二、五匯流排阻抗矩陣 Zbus 三相短路故障計算（30 分）

### 📌 題目與已知條件
![[111年_電力系統_第2題_五匯流排阻抗圖.png|750]]
*圖：111年電力系統第二題 五匯流排系統單線圖與阻抗資料*

五匯流排系統之正序阻抗矩陣 $\mathbf{Z}_{bus}$ 已知（標么值）：
$$\mathbf{Z}_{bus} = j \begin{bmatrix}
0.160 & 0.120 & 0.080 & 0.060 & 0.040 \\
0.120 & 0.240 & 0.100 & 0.080 & 0.060 \\
0.080 & 0.100 & 0.200 & 0.090 & 0.070 \\
0.060 & 0.080 & 0.090 & 0.180 & 0.080 \\
0.040 & 0.060 & 0.070 & 0.080 & 0.150
\end{bmatrix}\text{ pu}$$
- 系統故障前無載，各匯流排電壓均為額定值 $V_f = 1.0\angle 0^\circ\text{ pu}$。
- 故障點：**匯流排 3 發生三相金屬性短路接地故障**（$Z_f = 0$）。

* **(一)** 試求匯流排 3 之對稱故障電流標么值 $I_f$。（10 分）
* **(二)** 試求故障期間各匯流排（Bus 1 ~ Bus 5）之端電壓標么值。（15 分）
* **(三)** 若 Bus 1 與 Bus 3 間之支路阻抗為 $z_{13} = j0.20\text{ pu}$，求故障期間由 Bus 1 流向 Bus 3 之短路電流 $I_{13}$。（5 分）

---

### 💡 核心考點與破題關鍵
1. **$\mathbf{Z}_{bus}$ 短路故障計算核心公式**：
   - 故障電流：$I_f = \frac{V_f}{Z_{kk} + Z_f} = \frac{1.0}{Z_{33}}$
   - 故障期間母線電壓：$V_i^{(f)} = V_f - Z_{ik} I_f = 1.0 - \frac{Z_{i3}}{Z_{33}} V_f$
2. **支路電流**：
   $$I_{13} = \frac{V_1^{(f)} - V_3^{(f)}}{z_{13}}$$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：求解 Bus 3 故障電流 $I_f$
由 $\mathbf{Z}_{bus}$ 第 3 列第 3 行元素：$Z_{33} = j0.200\text{ pu}$
$$I_f = \frac{V_f}{Z_{33}} = \frac{1.0\angle 0^\circ}{j0.200} = \mathbf{-j5.000\text{ pu}} = \mathbf{5.000\angle -90^\circ\text{ pu}}$$

---

#### 🔹 第 (二) 小題：求解故障期間各匯流排電壓
$$V_i^{(f)} = 1.0 - Z_{i3} I_f = 1.0 - Z_{i3}(-j5.0)$$
- **Bus 1**：$V_1^{(f)} = 1.0 - (j0.080)(-j5.0) = 1.0 - 0.400 = \mathbf{0.600\text{ pu}}$
- **Bus 2**：$V_2^{(f)} = 1.0 - (j0.100)(-j5.0) = 1.0 - 0.500 = \mathbf{0.500\text{ pu}}$
- **Bus 3**：$V_3^{(f)} = 1.0 - (j0.200)(-j5.0) = 1.0 - 1.000 = \mathbf{0.000\text{ pu}}$（故障點接地）
- **Bus 4**：$V_4^{(f)} = 1.0 - (j0.090)(-j5.0) = 1.0 - 0.450 = \mathbf{0.550\text{ pu}}$
- **Bus 5**：$V_5^{(f)} = 1.0 - (j0.070)(-j5.0) = 1.0 - 0.350 = \mathbf{0.650\text{ pu}}$

---

#### 🔹 第 (三) 小題：求解支路短路電流 $I_{13}$
$$I_{13} = \frac{V_1^{(f)} - V_3^{(f)}}{z_{13}} = \frac{0.600 - 0.000}{j0.20} = \mathbf{-j3.000\text{ pu}} = \mathbf{3.000\angle -90^\circ\text{ pu}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **故障電流**：$I_f = \mathbf{5.000\angle -90^\circ\text{ pu}}$
- **各匯流排電壓**：
  $$\mathbf{V}^{(f)} = [0.600,\ 0.500,\ 0.000,\ 0.550,\ 0.650]^T\text{ pu}$$
- **支路電流**：$I_{13} = \mathbf{3.000\angle -90^\circ\text{ pu}}$

---

## 三、等面積準則臨界清除角與臨界清除時間（25 分）

### 📌 題目與已知條件
一部 $60\text{ Hz}$ 同步發電機慣性常數 $H = 6.0\text{ MJ/MVA}$，經輸電線連接至無窮母線。
- 故障前輸出實功率為 $P_m = 1.0\text{ pu}$。
- 故障前：$P_{e1}(\delta) = 2.0\sin\delta\text{ pu}$。
- 故障期間（發電機端發生三相短路）：$P_{e2}(\delta) = 0.0\text{ pu}$。
- 故障清除後：$P_{e3}(\delta) = 1.5\sin\delta\text{ pu}$。

* **(一)** 試求初始功角 $\delta_0$ 及臨界清除角 $\delta_{cr}$。（15 分）
* **(二)** 試推導並計算臨界清除時間 $t_{cr}$（秒）。（10 分）

---

### 💡 核心考點與破題關鍵
1. **臨界清除角等面積解析解**（當故障中 $P_{e2} = 0$ 時）：
   $$\delta_0 = \sin^{-1}(1.0 / 2.0) = 30^\circ = \frac{\pi}{6}\text{ rad} \approx 0.5236\text{ rad}$$
   $$\delta_{max} = \pi - \sin^{-1}(1.0 / 1.5) = \pi - \sin^{-1}(0.6667) = \pi - 0.7297 = 2.4119\text{ rad} = 138.19^\circ$$
   $$\cos\delta_{cr} = \frac{P_m(\delta_{max} - \delta_0) + P_{max3}\cos\delta_{max}}{P_{max3}} = \frac{1.0(2.4119 - 0.5236) + 1.5(-0.7454)}{1.5} = \frac{1.8883 - 1.1180}{1.5} = 0.5135$$
   $$\delta_{cr} = \cos^{-1}(0.5135) \approx 1.0315\text{ rad} = 59.10^\circ$$
2. **臨界清除時間推導**（在故障中 $P_a = P_m - 0 = P_m$ 為常數）：
   $$\frac{d^2\delta}{dt^2} = \frac{\pi f_0}{H} P_m \implies \delta(t) = \delta_0 + \frac{\pi f_0 P_m}{2H} t^2$$
   $$t_{cr} = \sqrt{\frac{4 H (\delta_{cr} - \delta_0)}{\omega_0 P_m}} = \sqrt{\frac{2 H (\delta_{cr} - \delta_0)}{\pi f_0 P_m}}$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解臨界清除角 $\delta_{cr}$
$$\cos\delta_{cr} = 0.5135 \implies \mathbf{\delta_{cr} = 59.10^\circ = 1.0315\text{ rad}}$$

#### 步驟 2：求解臨界清除時間 $t_{cr}$
代入搖擺方程式二次積分公式：
$$t_{cr} = \sqrt{\frac{2 \times 6.0 \times (1.0315 - 0.5236)}{\pi \times 60 \times 1.0}} = \sqrt{\frac{12 \times 0.5079}{188.4956}} = \sqrt{\frac{6.0948}{188.4956}} = \sqrt{0.03233} \approx \mathbf{0.1798\text{ 秒}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **初始功角**：$\delta_0 = 30.0^\circ$（$0.5236\text{ rad}$）
- **臨界清除角**：$\mathbf{\delta_{cr} = 59.10^\circ}$（$1.0315\text{ rad}$）
- **臨界清除時間**：$\mathbf{t_{cr} = 0.180\text{ 秒}}$（約 $10.8$ 個電源週期）

---

## 四、長程輸電線路 ABCD 參數與電壓調整率（25 分）

### 📌 題目與已知條件
![[111年_電力系統_第4題_長程線路模型圖.png|750]]
*圖：111年電力系統第四題 483 km 長距離輸電線路模型圖*

一條三相 $60\text{ Hz}$ 長距離換位輸電線，長度 $l = 483\text{ km} = 300\text{ miles}$。
- 每相串聯阻抗 $z = 0.08 + j0.80\ \Omega/\text{mile} \implies z = 0.804\angle 84.29^\circ\ \Omega/\text{mile}$。
- 每相對地導納 $y = j5.0 \times 10^{-6}\ \text{S/mile} = 5.0\times 10^{-6}\angle 90^\circ\ \text{S/mile}$。
- 受電端額定負載為 $P_R = 200\text{ MW}, \text{PF} = 0.8\text{ 滯後}$，受電端線電壓為 $V_{R,LL} = 345\text{ kV}$。

* **(一)** 試求長程輸電線之傳播常數 $\gamma$ 及特性阻抗 $Z_c$。（10 分）
* **(二)** 試求長程輸電線之精確雙曲函數 $\text{ABCD}$ 傳輸參數。（10 分）
* **(三)** 試求滿載時之送電端線電壓 $V_{S,LL}$ 及全載電壓調整率 $\text{VR}$。（5 分）

---

### 💡 核心考點與破題關鍵
1. **特性阻抗與傳播常數**：
   $$Z_c = \sqrt{\frac{z}{y}}, \quad \gamma = \sqrt{z y} = \alpha + j\beta$$
2. **長程輸電線精確 ABCD 參數**：
   $$A = D = \cosh(\gamma l), \quad B = Z_c \sinh(\gamma l), \quad C = \frac{\sinh(\gamma l)}{Z_c}$$
3. **電壓調整率**：
   $$\text{VR} = \frac{|V_S / A| - |V_R|}{|V_R|} \times 100\%$$

---

### ✏️ 步驟式詳細數學推導

#### 步骤 1：求解 $Z_c$ 與 $\gamma l$
$$Z_c = \sqrt{\frac{0.804\angle 84.29^\circ}{5.0\times 10^{-6}\angle 90^\circ}} = \sqrt{160800\angle -5.71^\circ} = \mathbf{401.0\angle -2.86^\circ\ \Omega}$$
$$\gamma = \sqrt{(0.804\angle 84.29^\circ)(5.0\times 10^{-6}\angle 90^\circ)} = \sqrt{4.02\times 10^{-6}\angle 174.29^\circ} = 0.002005\angle 87.14^\circ\ \text{mile}^{-1}$$
$$\theta = \gamma l = 0.002005\angle 87.14^\circ \times 300 = 0.6015\angle 87.14^\circ = \mathbf{0.0300 + j0.6007\text{ rad}}$$

#### 步驟 2：計算雙曲函數與 ABCD 參數
- $\cosh(0.0300 + j0.6007) = \cosh(0.0300)\cos(0.6007) + j\sinh(0.0300)\sin(0.6007) \approx 1.00045(0.8248) + j(0.0300)(0.5654) = \mathbf{0.8251 + j0.0170} = \mathbf{0.8253\angle 1.18^\circ}$
- $\sinh(0.0300 + j0.6007) \approx \mathbf{0.0247 + j0.5657} = \mathbf{0.5662\angle 87.50^\circ}$
- $B = Z_c \sinh(\gamma l) = (401.0\angle -2.86^\circ)(0.5662\angle 87.50^\circ) = \mathbf{227.05\angle 84.64^\circ\ \Omega}$
- $C = \frac{\sinh(\gamma l)}{Z_c} = \frac{0.5662\angle 87.50^\circ}{401.0\angle -2.86^\circ} = \mathbf{0.001412\angle 90.36^\circ\ \text{S}}$

#### 步驟 3：送電端電壓與電壓調整率
- 受電端相電壓：$V_R = \frac{345}{\sqrt{3}} = 199.186\angle 0^\circ\text{ kV}$
- 負載電流：$I_R = \frac{200\times 10^3}{\sqrt{3}\times 345 \times 0.8} = 418.37\angle -36.87^\circ\text{ A} = 0.41837\angle -36.87^\circ\text{ kA}$
- 送電端相電壓：
  $$V_S = A V_R + B I_R = (0.8253\angle 1.18^\circ)(199.186) + (227.05\angle 84.64^\circ)(0.41837\angle -36.87^\circ) = 164.388\angle 1.18^\circ + 94.991\angle 47.77^\circ = (164.35 + j3.38) + (63.85 + j70.34) = 228.20 + j73.72\text{ kV}$$
  $$|V_S| = \sqrt{228.20^2 + 73.72^2} = \mathbf{239.81\text{ kV}} \implies V_{S,LL} = \sqrt{3} \times 239.81\text{ kV} = \mathbf{415.36\text{ kV}}$$
- 電壓調整率：
  $$\text{VR} = \frac{|V_S / A| - |V_R|}{|V_R|} \times 100\% = \frac{239.81 / 0.8253 - 199.186}{199.186} \times 100\% = \frac{290.57 - 199.186}{199.186} \times 100\% = \mathbf{45.88\%}$$

---

### 🎯 第四題 滿分關鍵與結論
- **特性阻抗**：$Z_c = \mathbf{401.0\angle -2.86^\circ\ \Omega}$
- **傳輸參數**：$A = D = \mathbf{0.8253\angle 1.18^\circ}, B = \mathbf{227.05\angle 84.64^\circ\ \Omega}$
- **送電端線電壓**：$V_{S,LL} = \mathbf{415.36\text{ kV}}$
- **電壓調整率**：$\text{VR} = \mathbf{45.88\%}$
'''

with open('📝 個人題解與錯題本/05_電力系統/111年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_111)

print('✅ 111年_電力系統_全卷完整詳細題解.md upgraded to gold standard!')
