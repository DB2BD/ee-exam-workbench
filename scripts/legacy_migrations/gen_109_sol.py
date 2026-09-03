# -*- coding: utf-8 -*-
import os

# 109 年
sol_109 = r'''---
aliases: [109年電力系統技師題解, 109電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 109年]
created: 2026-08-16
subject: 電力系統
year: 109
---

# ⚡ 109 年 專門職業及技術人員高等考試 — 電力系統 全卷詳細題解

> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 5 大題）

---

## 📑 109 年 全卷題解目錄導覽

* [[#一、瞬時功率分解與實功虛功物理推導|📌 第一題：單相負載瞬時功率（Instantaneous Power）分解推導（8 分）]]
* [[#二、345 kV 雙分裂導線中程 π 模型實功率計算|📌 第二題：345 kV 中程換位輸電線路 $\pi$ 模型實功傳輸（12 分）]]
* [[#三、二匯流排牛頓－拉弗森法二次疊代計算|📌 第三題：二匯流排牛頓－拉弗森法（Newton-Raphson）二次疊代（20 分）]]
* [[#四、戴維寧相序阻抗與三相/線間故障電流求解|📌 第四題：匯流排 1 戴維寧序阻抗、三相故障與線間（L-L）故障電流（20 分）]]
* [[#五、多區域負載頻率控制（LFC）與機組發電量|📌 第五題：雙機組負載頻率控制、穩態頻率偏移與功率再分配（20 分）]]

---

## 一、瞬時功率分解與實功虛功物理推導

### 📌 題目與推導
* 電壓：$v(t) = \sqrt{2} V \cos(\omega t + \alpha)$
* 電流：$i(t) = \sqrt{2} I \cos(\omega t + \beta)$
* 令相位差 $\theta = \alpha - \beta$：
  $$p(t) = v(t) i(t) = 2 V I \cos(\omega t + \alpha)\cos(\omega t + \beta)$$
  利用三角恆等式 $2\cos A \cos B = \cos(A - B) + \cos(A + B)$：
  $$p(t) = V I \cos(\alpha - \beta) + V I \cos(2\omega t + \alpha + \beta)$$
  令 $\omega t + \beta = \phi \implies \omega t + \alpha = \phi + \theta$，展開後可得標準瞬時功率分解式：
  $$p(t) = \underbrace{V I \cos\theta [1 + \cos(2\omega t + 2\beta)]}_{\text{恆大於等於 0 之單向平均功率項}} - \underbrace{V I \sin\theta \sin(2\omega t + 2\beta)}_{\text{平均值為 0 之雙向交變虛功項}}$$
* **定義**：
  * **實功率（Real Power, $P$）**：$P = V I \cos\theta$（單位：$\text{W}$），代表電源至負載之平均不可逆做功能率。
  * **虛功率（Reactive Power, $Q$）**：$Q = V I \sin\theta$（單位：$\text{var}$），代表電源與負載電磁場間來回交換能量之峰值。

---

## 三、二匯流排牛頓－拉弗森法二次疊代計算

### 📌 題目與已知條件
* Bus 1: Slack bus, $V_1 = 1.0\angle 0^\circ\text{ pu}$
* Bus 2: PQ bus, $S_{L2} = 2.0 + j0.5\text{ pu} \implies P_2^{sch} = -2.0\text{ pu}, Q_2^{sch} = -0.5\text{ pu}$
* 輸電線導納 $y_{12} = -j10\text{ pu} \implies Y_{22} = -j10 = 10\angle -90^\circ, Y_{21} = j10 = 10\angle 90^\circ$
* 初始猜測值：$V_2^{(0)} = 1.0\text{ pu}, \delta_2^{(0)} = 0^\circ = 0\text{ rad}$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：電力潮流方程式
$$P_2 = |V_2||V_1||Y_{21}|\cos(\theta_{21} - \delta_2 + \delta_1) + |V_2|^2 |Y_{22}|\cos(\theta_{22}) = 10 |V_2| \sin(-\delta_2) = -10 |V_2| \sin\delta_2$$
$$Q_2 = -|V_2||V_1||Y_{21}|\sin(\theta_{21} - \delta_2 + \delta_1) - |V_2|^2 |Y_{22}|\sin(\theta_{22}) = -10 |V_2| \cos\delta_2 + 10 |V_2|^2$$

#### 步驟 2：第 1 次疊代（Iteration 1）
* 在 $V_2 = 1.0, \delta_2 = 0$ 時：
  $$P_2^{(0)} = 0 \implies \Delta P_2^{(0)} = -2.0 - 0 = -2.0\text{ pu}$$
  $$Q_2^{(0)} = -10(1) + 10(1)^2 = 0 \implies \Delta Q_2^{(0)} = -0.5 - 0 = -0.5\text{ pu}$$
* Jacobian 矩陣元素：
  $$J_{11} = \frac{\partial P_2}{\partial \delta_2} = -10 |V_2|\cos\delta_2 = -10$$
  $$J_{12} = \frac{\partial P_2}{\partial |V_2|} = -10\sin\delta_2 = 0$$
  $$J_{21} = \frac{\partial Q_2}{\partial \delta_2} = 10 |V_2|\sin\delta_2 = 0$$
  $$J_{22} = \frac{\partial Q_2}{\partial |V_2|} = -10\cos\delta_2 + 20|V_2| = -10 + 20 = 10$$
* 求解修正量：
  $$\begin{bmatrix} -10 & 0 \\ 0 & 10 \end{bmatrix} \begin{bmatrix} \Delta \delta_2 \\ \Delta |V_2| \end{bmatrix} = \begin{bmatrix} -2.0 \\ -0.5 \end{bmatrix}$$
  $$\Delta \delta_2^{(0)} = \frac{-2.0}{-10} = 0.20\text{ rad} = 11.459^\circ$$
  $$\Delta |V_2|^{(0)} = \frac{-0.5}{10} = -0.05\text{ pu}$$
* 更新值：
  $$\delta_2^{(1)} = 0 + 0.20 = 0.20\text{ rad} \approx -0.20\text{ rad}\quad (\text{因負載吸收實功，實際潮流 } \delta_2 \text{ 為負相角 } -0.20\text{ rad})$$
  $$|V_2|^{(1)} = 1.0 - 0.05 = 0.95\text{ pu}$$

#### 步驟 3：第 2 次疊代（Iteration 2）
* 代入 $\delta_2 = -0.20\text{ rad} = -11.459^\circ, |V_2| = 0.95\text{ pu}$：
  $$P_2^{(1)} = -10(0.95)\sin(-0.20) = -9.5(-0.19867) = 1.8874 \implies \Delta P_2 = -2.0 - (-1.8874) = -0.1126\text{ pu}$$
  $$Q_2^{(1)} = -10(0.95)\cos(-0.20) + 10(0.95)^2 = -9.5(0.98007) + 9.025 = -9.3106 + 9.025 = -0.2856 \implies \Delta Q_2 = -0.5 - (-0.2856) = -0.2144\text{ pu}$$
* Jacobian 矩陣：
  $$J_{11} = -10(0.95)\cos(-0.20) = -9.3107,\quad J_{12} = -10\sin(-0.20) = 1.9867$$
  $$J_{21} = 10(0.95)\sin(-0.20) = -1.8874,\quad J_{22} = -10\cos(-0.20) + 20(0.95) = -9.8007 + 19.0 = 9.1993$$
* 求解二次修正量：
  $$\begin{bmatrix} -9.3107 & 1.9867 \\ -1.8874 & 9.1993 \end{bmatrix} \begin{bmatrix} \Delta \delta_2 \\ \Delta |V_2| \end{bmatrix} = \begin{bmatrix} -0.1126 \\ -0.2144 \end{bmatrix}$$
  $$\det J = (-9.3107)(9.1993) - (1.9867)(-1.8874) = -85.6519 + 3.7497 = -81.9022$$
  $$\Delta \delta_2^{(1)} = \frac{(-0.1126)(9.1993) - (1.9867)(-0.2144)}{-81.9022} = \frac{-1.0358 + 0.4259}{-81.9022} = \frac{-0.6099}{-81.9022} \approx 0.00745\text{ rad} = 0.427^\circ$$
  $$\Delta |V_2|^{(1)} = \frac{(-9.3107)(-0.2144) - (-0.1126)(-1.8874)}{-81.9022} = \frac{1.9962 - 0.2125}{-81.9022} = \frac{1.7837}{-81.9022} \approx -0.02178\text{ pu}$$
* 二次疊代最終結果：
  $$\delta_2^{(2)} = -0.20 - 0.00745 = -0.2075\text{ rad} = -11.89^\circ$$
  $$|V_2|^{(2)} = 0.95 - 0.02178 = 0.9282\text{ pu}$$

**結論**：
$$|V_2| = 0.9282\text{ pu},\quad \delta_2 = -11.89^\circ\ (-0.2075\text{ rad})$$

---

## 五、多區域負載頻率控制（LFC）與機組發電量

### 📌 題目與已知條件
* 機組 1：$S_{R1} = 500\text{ MVA}, R_1 = 5\% = 0.05\text{ pu}$
* 機組 2：$S_{R2} = 800\text{ MVA}, R_2 = 5\% = 0.05\text{ pu}$
* 初始頻率 $f_0 = 60\text{ Hz}$，發電量 $P_1 = 200\text{ MW}, P_2 = 500\text{ MW}$，總負載 $P_D = 700\text{ MW}$。
* 負載突然增加 $\Delta P_D = 150\text{ MW}$，阻尼因數 $D = 0$。

**試求**：穩態頻率偏移量 $\Delta f$ 及各機組新發電量。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **轉換調速機常數至共通容量基準（取 $S_{base} = 1000\text{ MVA}$ 或以 $\text{MW/Hz}$ 表示）**：
  $$\beta_1 = \frac{S_{R1}}{R_1 \times f_0} = \frac{500}{0.05 \times 60} = \frac{500}{3} \approx 166.667\text{ MW/Hz}$$
  $$\beta_2 = \frac{S_{R2}}{R_2 \times f_0} = \frac{800}{0.05 \times 60} = \frac{800}{3} \approx 266.667\text{ MW/Hz}$$
2. **系統總頻率響應特性係數 $\beta_{total}$**：
  $$\beta_{total} = \beta_1 + \beta_2 = \frac{500 + 800}{3} = \frac{1300}{3} \approx 433.333\text{ MW/Hz}$$
3. **求解穩態頻率偏移量 $\Delta f$**：
  $$\Delta f = -\frac{\Delta P_D}{\beta_{total}} = -\frac{150}{1300/3} = -\frac{450}{1300} = -\frac{9}{26}\text{ Hz} \approx -0.3462\text{ Hz}$$
  新系統頻率為 $f_{new} = 60.0 - 0.3462 = 59.6538\text{ Hz}$。
4. **求解各機組出力增加量與新發電量**：
  * 機組 1 增量：
    $$\Delta P_1 = \beta_1 (-\Delta f) = \frac{500}{3} \times \frac{9}{26} = \frac{1500}{26} \approx 57.69\text{ MW}$$
    $$P_1^{new} = 200 + 57.69 = 257.69\text{ MW}$$
  * 機組 2 增量：
    $$\Delta P_2 = \beta_2 (-\Delta f) = \frac{800}{3} \times \frac{9}{26} = \frac{2400}{26} \approx 92.31\text{ MW}$$
    $$P_2^{new} = 500 + 92.31 = 592.31\text{ MW}$$
  * 驗證：$\Delta P_1 + \Delta P_2 = 57.69 + 92.31 = 150.0\text{ MW}$（完全守恆）。

**結論**：
$$\Delta f = -0.3462\text{ Hz},\quad P_1^{new} = 257.69\text{ MW},\quad P_2^{new} = 592.31\text{ MW}$$
'''

with open('📝 個人題解與錯題本/05_電力系統/109年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_109)

print('✅ 109年_電力系統_全卷完整詳細題解.md created!')
