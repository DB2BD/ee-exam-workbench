# -*- coding: utf-8 -*-
import os

os.makedirs('📝 個人題解與錯題本/05_電力系統', exist_ok=True)

# 112 年 電力系統
sol_112 = r'''---
aliases: [112年電力系統技師題解, 112電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 112年]
created: 2026-08-16
subject: 電力系統
year: 112
---

# ⚡ 112 年 專門職業及技術人員高等考試 — 電力系統 全卷詳細題解

> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01120`  
> **滿分**：100 分（共 4 大題，各 25 分）

---

## 📑 112 年 全卷題解目錄導覽

* [[#一、四分裂導線換位輸電線路電感與電容計算|📌 第一題：四分裂導線（4-bundle）輸電線每公里電感與電容（25 分）]]
* [[#二、等微增燃料成本最佳經濟調度係數求解|📌 第二題：二發電機最佳經濟調度與成本係數求解（25 分）]]
* [[#三、含變壓器分接頭之四匯流排節點導納矩陣 Ybus|📌 第三題：含非額定抽頭變壓器（Tap Changer）之 Ybus 建立（25 分）]]
* [[#四、單機無窮母線系統等面積準則與臨界清除角|📌 第四題：三相短路故障等面積準則（Equal-Area）臨界清除角（25 分）]]

---

## 一、四分裂導線換位輸電線路電感與電容計算

### 📌 題目與已知條件
* 單回路三相水平換位輸電線路，相間距離 $D = 10\text{ m} = 1000\text{ cm}$。
* 每相由 4 條 ACSR 1,272,000 cmil 導線組成四分裂導線，正方形捆紮間距 $d = 50\text{ cm}$。
* 導線外徑 $2r = 3.5103\text{ cm} \implies r = 1.75515\text{ cm} = 0.0175515\text{ m}$。
* 單導線幾何平均半徑 $\text{GMR}_s = 1.4173\text{ cm} = 0.014173\text{ m}$。

**試決定**：此輸電線每相每公里之電感值 $L$（$\text{mH/km}$）及電容值 $C$（$\mu\text{F/km}$）。（25 分）

---

### 💡 核心考點與破題關鍵
1. **三相水平排列幾何平均距離 $\text{GMD}$**：
   $$\text{GMD} = \sqrt[3]{D_{ab} D_{bc} D_{ca}} = \sqrt[3]{D \cdot D \cdot 2D} = \sqrt[3]{2} D = 2^{1/3} \times 10\text{ m} \approx 12.5992\text{ m}$$
2. **四分裂導線等效幾何平均半徑 $\text{GMR}_L$（計算電感）**：
   $$\text{GMR}_L = \sqrt[4]{\text{GMR}_s \cdot d \cdot d \cdot \sqrt{2}d} = \sqrt[4]{\sqrt{2}} \cdot \sqrt[4]{\text{GMR}_s \cdot d^3} = 2^{1/8} \cdot (\text{GMR}_s \cdot d^3)^{1/4}$$
3. **四分裂導線等效半徑 $\text{GMR}_C$（計算電容）**：
   $$\text{GMR}_C = 2^{1/8} \cdot (r \cdot d^3)^{1/4}$$
4. **每相每公里電感與電容公式**：
   $$L = 2 \times 10^{-7} \ln\left(\frac{\text{GMD}}{\text{GMR}_L}\right)\text{ H/m} = 0.2 \ln\left(\frac{\text{GMD}}{\text{GMR}_L}\right)\text{ mH/km}$$
   $$C = \frac{2\pi \epsilon_0}{\ln(\text{GMD}/\text{GMR}_C)}\text{ F/m} = \frac{0.0556}{\ln(\text{GMD}/\text{GMR}_C)}\ \mu\text{F/km}$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算 $\text{GMD}$ 與四分裂導線之 $\text{GMR}_L, \text{GMR}_C$
* 三相水平排列等效距離：
  $$\text{GMD} = \sqrt[3]{10 \times 10 \times 20} = \sqrt[3]{2000} \approx 12.5992\text{ m}$$
* 電感等效半徑 $\text{GMR}_L$：
  $$\text{GMR}_L = \sqrt[4]{0.014173 \times (0.50)^3 \times \sqrt{2}} = \sqrt[4]{0.014173 \times 0.125 \times 1.414214} = \sqrt[4]{2.5054 \times 10^{-3}} \approx 0.22384\text{ m} = 22.384\text{ cm}$$
* 電容等效半徑 $\text{GMR}_C$：
  $$\text{GMR}_C = \sqrt[4]{0.0175515 \times (0.50)^3 \times \sqrt{2}} = \sqrt[4]{0.0175515 \times 0.125 \times 1.414214} = \sqrt[4]{3.1027 \times 10^{-3}} \approx 0.23602\text{ m} = 23.602\text{ cm}$$

#### 步驟 2：計算每相每公里電感值 $L$
$$L = 0.2 \ln\left(\frac{12.5992}{0.22384}\right) = 0.2 \ln(56.2866) = 0.2 \times 4.03046 = 0.8061\text{ mH/km}$$

#### 步驟 3：計算每相每公里電容值 $C$
$$C = \frac{2\pi \times 8.854 \times 10^{-12} \times 10^3}{\ln\left(\frac{12.5992}{0.23602}\right)} = \frac{5.5633 \times 10^{-8}}{\ln(53.3819)} = \frac{5.5633 \times 10^{-8}}{3.97745} \approx 1.3987 \times 10^{-8}\text{ F/km} = 0.01399\ \mu\text{F/km}$$

**結論**：
$$L = 0.8061\text{ mH/km},\quad C = 0.01399\ \mu\text{F/km} = 13.99\text{ nF/km}$$

---

## 二、等微增燃料成本最佳經濟調度係數求解

### 📌 題目與已知條件
* 機組 1 成本：$C_1 = 400 + 7.0 P_1 + \beta P_1^2\quad (\$/\text{h})$
* 機組 2 成本：$C_2 = 450 + \gamma P_2 + 0.002 P_2^2\quad (\$/\text{h})$
* 條件 1：總需求 $P_{D1} = 550\text{ MW}$ 時，增量成本 $\lambda_1 = 8\ \$/\text{MWh}$。
* 條件 2：總需求 $P_{D2} = 1300\text{ MW}$ 時，增量成本 $\lambda_2 = 10\ \$/\text{MWh}$。

**試求**：燃料成本未知係數 $\beta$ 與 $\gamma$。（25 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：列出微增成本方程式
$$\frac{dC_1}{dP_1} = 7.0 + 2\beta P_1 = \lambda \implies P_1 = \frac{\lambda - 7.0}{2\beta}$$
$$\frac{dC_2}{dP_2} = \gamma + 0.004 P_2 = \lambda \implies P_2 = \frac{\lambda - \gamma}{0.004} = 250(\lambda - \gamma)$$

#### 步驟 2：代入條件 1（$\lambda = 8, P_D = 550\text{ MW}$）
$$P_2^{(1)} = 250(8 - \gamma) = 2000 - 250\gamma$$
$$P_1^{(1)} = 550 - P_2^{(1)} = 550 - (2000 - 250\gamma) = 250\gamma - 1450$$
代入機組 1 增量成本式：
$$7.0 + 2\beta(250\gamma - 1450) = 8 \implies 2\beta(250\gamma - 1450) = 1.0\quad \text{--- (1)}$$

#### 步驟 3：代入條件 2（$\lambda = 10, P_D = 1300\text{ MW}$）
$$P_2^{(2)} = 250(10 - \gamma) = 2500 - 250\gamma$$
$$P_1^{(2)} = 1300 - P_2^{(2)} = 1300 - (2500 - 250\gamma) = 250\gamma - 1200$$
代入機組 1 增量成本式：
$$7.0 + 2\beta(250\gamma - 1200) = 10 \implies 2\beta(250\gamma - 1200) = 3.0\quad \text{--- (2)}$$

#### 步驟 4：聯立求解 $\beta, \gamma$
將 (2) 式除以 (1) 式：
$$\frac{250\gamma - 1200}{250\gamma - 1450} = \frac{3.0}{1.0} = 3$$
$$250\gamma - 1200 = 3(250\gamma - 1450) = 750\gamma - 4350$$
$$500\gamma = 3150 \implies \gamma = 6.30\ \$/\text{MWh}$$
將 $\gamma = 6.30$ 代回 (1) 式：
$$2\beta[250(6.30) - 1450] = 2\beta[1575 - 1450] = 2\beta(125) = 250\beta = 1.0 \implies \beta = 0.004\ \$/\text{MW}^2\text{h}$$

**結論**：
$$\beta = 0.004\ \$/\text{MW}^2\text{h},\quad \gamma = 6.30\ \$/\text{MWh}$$

---

## 三、含變壓器分接頭之四匯流排節點導納矩陣 Ybus

### 📌 題目與已知條件
* 變壓器 $T_1$：抽頭比 $a_1 = 0.8$，連接 Bus 1 與 Bus 3，漏電抗 $x_{13} = j0.1\text{ pu} \implies y = -j10\text{ pu}$。
* 變壓器 $T_2$：抽頭比 $a_2 = 1.25$，連接 Bus 4 與 Bus 2，漏電抗 $x_{42} = j0.1\text{ pu} \implies y = -j10\text{ pu}$。
* 輸電線路：
  * Line 1-2: $x_{12} = j0.2\text{ pu} \implies y_{12} = -j5\text{ pu}$
  * Line 3-4: $x_{34} = j0.25\text{ pu} \implies y_{34} = -j4\text{ pu}$

**試求**：匯流排導納矩陣 $\mathbf{Y}_{bus}$。（25 分）

---

### 💡 核心考點與破題關鍵
含非理想抽頭比變壓器（Tap ratio $a:1$ 在匯流排 $i$ 側）之 $\pi$ 型等效導納模型：
* 串聯支路導納：$\frac{y}{a}$
* 匯流排 $i$ 側並聯導納：$y \left(\frac{1 - a}{a^2}\right) = \frac{y}{a^2} - \frac{y}{a}$
* 匯流排 $j$ 側並聯導納：$y \left(\frac{a - 1}{a}\right) = y - \frac{y}{a}$

---

### ✏️ 步驟式詳細數學推導
1. **變壓器 $T_1$（$a = 0.8$ 連接 Bus 1 至 Bus 3，$y = -j10$）**：
   * $Y_{13} = -\frac{y}{a} = -\frac{-j10}{0.8} = j12.5\text{ pu}$
   * 自導納貢獻：$Y_{11}^{(T1)} = \frac{y}{a^2} = \frac{-j10}{0.64} = -j15.625\text{ pu}$
   * 自導納貢獻：$Y_{33}^{(T1)} = y = -j10\text{ pu}$
2. **變壓器 $T_2$（$a = 1.25$ 連接 Bus 4 至 Bus 2，$y = -j10$）**：
   * $Y_{42} = -\frac{y}{a} = -\frac{-j10}{1.25} = j8.0\text{ pu}$
   * 自導納貢獻：$Y_{44}^{(T2)} = \frac{y}{a^2} = \frac{-j10}{1.5625} = -j6.4\text{ pu}$
   * 自導納貢獻：$Y_{22}^{(T2)} = y = -j10\text{ pu}$
3. **合成 $4 \times 4$ 導納矩陣 $\mathbf{Y}_{bus}$**：
   $$\mathbf{Y}_{bus} = \begin{bmatrix}
   -j(5 + 15.625) & j5 & j12.5 & 0 \\
   j5 & -j(5 + 10) & 0 & j8 \\
   j12.5 & 0 & -j(10 + 4) & j4 \\
   0 & j8 & j4 & -j(4 + 6.4)
   \end{bmatrix} = \begin{bmatrix}
   -j20.625 & j5.0 & j12.5 & 0 \\
   j5.0 & -j15.0 & 0 & j8.0 \\
   j12.5 & 0 & -j14.0 & j4.0 \\
   0 & j8.0 & j4.0 & -j10.4
   \end{bmatrix}\text{ pu}$$

---

## 四、單機無窮母線系統等面積準則與臨界清除角

### 📌 題目與已知條件
* 發電機輸出：$P_e = 0.8\text{ pu}, Q = 0.074\text{ pu}$，無窮母線電壓 $V = 1.0\angle 0^\circ\text{ pu}$。
* 故障前總轉移電抗 $X_1 = 0.50\text{ pu}$，最大功率 $P_{max1} = 1.6\text{ pu}$。
* 故障期間電壓降至極低，故障傳輸功率 $P_{e2}(\delta) = P_{max2} \sin\delta = 0.20 \sin\delta$。
* 故障清除後系統恢復原狀：$P_{e3}(\delta) = P_{max1} \sin\delta = 1.6 \sin\delta$。

**試求**：該同步發電機之臨界清除角 $\delta_{cr}$。（25 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求初始功率角 $\delta_0$ 與最大功率角 $\delta_{max}$
$$\delta_0 = \sin^{-1}\left(\frac{P_m}{P_{max1}}\right) = \sin^{-1}\left(\frac{0.8}{1.6}\right) = \sin^{-1}(0.5) = 30^\circ = 0.5236\text{ rad}$$
$$\delta_{max} = \pi - \delta_0 = 180^\circ - 30^\circ = 150^\circ = 2.6180\text{ rad}$$

#### 步驟 2：利用等面積準則（Equal-Area Criterion）
加速面積 $A_1$ 等於減速面積 $A_2$：
$$\int_{\delta_0}^{\delta_{cr}} (P_m - P_{max2}\sin\delta) d\delta = \int_{\delta_{cr}}^{\delta_{max}} (P_{max1}\sin\delta - P_m) d\delta$$
$$P_m (\delta_{cr} - \delta_0) + P_{max2}(\cos\delta_{cr} - \cos\delta_0) = -P_{max1}(\cos\delta_{max} - \cos\delta_{cr}) - P_m(\delta_{max} - \delta_{cr})$$
$$P_m (\delta_{max} - \delta_0) + P_{max2}\cos\delta_{cr} - P_{max2}\cos\delta_0 = P_{max1}\cos\delta_{cr} - P_{max1}\cos\delta_{max}$$
$$(P_{max1} - P_{max2})\cos\delta_{cr} = P_m (\delta_{max} - \delta_0) + P_{max1}\cos\delta_{max} - P_{max2}\cos\delta_0$$

代入數值：
$$(1.6 - 0.2)\cos\delta_{cr} = 0.8(2.6180 - 0.5236) + 1.6\cos(150^\circ) - 0.2\cos(30^\circ)$$
$$1.4\cos\delta_{cr} = 0.8(2.0944) + 1.6(-0.8660) - 0.2(0.8660) = 1.6755 - 1.3856 - 0.1732 = 0.1167$$
$$\cos\delta_{cr} = \frac{0.1167}{1.4} \approx 0.08336$$
$$\delta_{cr} = \cos^{-1}(0.08336) \approx 85.22^\circ = 1.487\text{ rad}$$

**結論**：
$$\delta_{cr} = 85.22^\circ\quad (1.487\text{ rad})$$
'''

with open('📝 個人題解與錯題本/05_電力系統/112年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_112)

print('✅ 112年_電力系統_全卷完整詳細題解.md created!')
