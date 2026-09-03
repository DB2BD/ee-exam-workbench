# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 110 年 電力系統 全 5 題 完整詳細題解
# ==============================================================================
sol_110 = r'''---
aliases: [110年電力系統技師題解, 110電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 110年]
created: 2026-08-16
subject: 電力系統
year: 110
---

# ⚡ 110 年 專門職業及技術人員高等考試 — 電力系統 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 5 大題，每題 20 分）

---

## 📑 110 年 全卷題解目錄導覽

* [[#一、圓型轉子與凸極式同步發電機功角特性|📌 第一題：圓型與凸極式（Salient Pole）同步發電機直軸/交軸感抗求解（20 分）]]
* [[#二、快速解耦電力潮流法一次疊代計算|📌 第二題：快速解耦電力潮流法（FDLF）一次疊代電壓與相角（20 分）]]
* [[#三、配電饋線同時發生單相接地與線間故障|📌 第三題：同時故障（Simultaneous Fault）對稱成分法與序阻抗（20 分）]]
* [[#四、考慮輸電線實功損耗之發電機協調方程式與微增損失|📌 第四題：含線路損失之經濟調度、增量損失與罰點因數（20 分）]]
* [[#五、發電機電壓調整率與突加機械功率暫態穩定度極限|📌 第五題：發電機等面積準則突加機械功率最大極限 $P_{m,max}$（20 分）]]

---

## 一、圓型轉子與凸極式同步發電機功角特性

### 📌 題目與已知條件
1. **(一) 圓型轉子同步機**：同步感抗 $X_s = 0.7\text{ pu}$，經兩條感抗均為 $0.6\text{ pu}$ 之並聯輸電線連接至無窮母線（$X_{line} = 0.6 / 2 = 0.3\text{ pu}$）。無窮母線電壓 $V = 1.0\text{ pu}$，發電機激磁電壓 $E = 1.5\text{ pu}$，供應無窮母線實功率 $P = 0.75\text{ pu}$。求此時功率角 $\delta$。（4 分）
2. **(二) 凸極式同步機**：併接至無窮母線，供應功因為 $1.0$ 之負載 $P = 1.0\text{ pu}$。無窮母線電壓 $V = 1.05\text{ pu}$，激磁電壓 $E_q = 1.4\text{ pu}$，功率角 $\delta = 25^\circ$。求直軸感抗 $X_d$ 與交軸感抗 $X_q$。（16 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 圓型轉子發電機功率角 $\delta$
總轉移電抗為：
$$X_T = X_s + X_{line} = 0.7 + 0.3 = 1.0\text{ pu}$$
實功率傳輸公式：
$$P = \frac{E V}{X_T} \sin\delta \implies 0.75 = \frac{1.5 \times 1.0}{1.0} \sin\delta = 1.5 \sin\delta$$
$$\sin\delta = \frac{0.75}{1.5} = 0.5 \implies \delta = \sin^{-1}(0.5) = 30.0^\circ$$

#### (二) 凸極式同步發電機 $X_d$ 與 $X_q$ 求解
* 功因為 $1.0 \implies \phi = 0^\circ$，電樞電流 $I_a = \frac{P}{V\cos\phi} = \frac{1.0}{1.05 \times 1.0} \approx 0.95238\text{ pu}$，且 $\mathbf{I}_a$ 與端電壓 $\mathbf{V}$ 同相（相位角 $0^\circ$）。
* 內功率角（Internal power angle）$\delta = 25^\circ$：
  * 直軸電流分量：$I_d = I_a \sin\delta = 0.95238 \sin(25^\circ) = 0.95238 \times 0.42262 \approx 0.4025\text{ pu}$
  * 交軸電流分量：$I_q = I_a \cos\delta = 0.95238 \cos(25^\circ) = 0.95238 \times 0.90631 \approx 0.8631\text{ pu}$
* 由凸極機相量圖投影關係：
  $$V \sin\delta = I_q X_q \implies 1.05 \sin(25^\circ) = 0.8631 X_q$$
  $$X_q = \frac{1.05 \times 0.42262}{0.8631} = \frac{0.44375}{0.8631} \approx 0.5141\text{ pu}$$
* 由直軸電動勢平衡：
  $$E_q = V \cos\delta + I_d X_d \implies 1.4 = 1.05 \cos(25^\circ) + 0.4025 X_d$$
  $$1.4 = 1.05 \times 0.90631 + 0.4025 X_d = 0.95163 + 0.4025 X_d$$
  $$X_d = \frac{1.4 - 0.95163}{0.4025} = \frac{0.44837}{0.4025} \approx 1.1140\text{ pu}$$

**結論**：
$$\delta = 30.0^\circ,\quad X_q = 0.5141\text{ pu},\quad X_d = 1.1140\text{ pu}$$

---

## 二、快速解耦電力潮流法一次疊代計算

### 📌 題目與已知條件
* Bus 1: Slack bus, $V_1 = 1.0\angle 0^\circ\text{ pu}$
* Bus 2: PV bus, $V_2 = 1.05\text{ pu}, P_{G2} = 0.6\text{ pu}, \theta_2^{(0)} = 0^\circ$
* Bus 3: PQ bus, $S_{L3} = 3.0 + j1.0\text{ pu} \implies P_3^{sch} = -3.0\text{ pu}, Q_3^{sch} = -1.0\text{ pu}, V_3^{(0)} = 1.0\text{ pu}, \theta_3^{(0)} = 0^\circ$
* 系統導納矩陣電抗：$y_{12} = -j5\text{ pu}, y_{13} = -j4\text{ pu}, y_{23} = -j4\text{ pu}$

**試求**：
1. 注入母線 2 的實功率 $P_2$ 電力潮流方程式。（5 分）
2. 注入母線 3 的虛功率 $Q_3$ 電力潮流方程式。（5 分）
3. 快速解耦法解一次疊代後的 $\theta_3$ 及 $V_3$。（10 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 母線 2 實功率潮流方程式
$$P_2 = |V_2|\sum_{k=1}^3 |V_k| |Y_{2k}| \cos(\theta_{2k} - \delta_2 + \delta_k)$$
代入導納參數：
$$P_2 = |V_2||V_1|(5)\sin(\delta_2 - \delta_1) + |V_2||V_3|(4)\sin(\delta_2 - \delta_3) = 5|V_2||V_1|\sin(\delta_2 - \delta_1) + 4|V_2||V_3|\sin(\delta_2 - \delta_3)$$

#### (二) 母線 3 虛功率潮流方程式
$$Q_3 = -|V_3|\sum_{k=1}^3 |V_k| |Y_{3k}| \sin(\theta_{3k} - \delta_3 + \delta_k)$$
$$Q_3 = 4|V_3||V_1|\cos(\delta_3 - \delta_1) + 4|V_3||V_2|\cos(\delta_3 - \delta_2) - 8|V_3|^2$$

#### (三) 快速解耦法一次疊代計算
1. **建立 $B'$ 與 $B''$ 矩陣**：
   $$\mathbf{B}' = \begin{bmatrix} B_{22} & B_{23} \\ B_{32} & B_{33} \end{bmatrix} = \begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix},\quad B'' = [B_{33}] = [8]$$
2. **計算功率不平衡量**：
   * 在初始值下：$P_2^{(0)} = 0 \implies \Delta P_2 = 0.6 - 0 = 0.6\text{ pu} \implies \frac{\Delta P_2}{V_2} = \frac{0.6}{1.05} = 0.5714\text{ pu}$
   * $P_3^{(0)} = 0 \implies \Delta P_3 = -3.0 - 0 = -3.0\text{ pu} \implies \frac{\Delta P_3}{V_3} = \frac{-3.0}{1.0} = -3.0\text{ pu}$
3. **求解相角修正量 $\Delta \theta$**：
   $$\begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix} \begin{bmatrix} \Delta \theta_2 \\ \Delta \theta_3 \end{bmatrix} = \begin{bmatrix} 0.5714 \\ -3.0 \end{bmatrix}$$
   $$\Delta \theta_3 = \frac{9(-3.0) - (-4)(0.5714)}{9\times 8 - (-4)^2} = \frac{-27.0 + 2.2857}{56} = \frac{-24.7143}{56} \approx -0.4413\text{ rad} = -25.29^\circ$$
4. **求解電壓修正量 $\Delta V_3$**：
   $$Q_3^{(0)} = 0 \implies \Delta Q_3 = -1.0 - 0 = -1.0\text{ pu} \implies \frac{\Delta Q_3}{V_3} = -1.0\text{ pu}$$
   $$B'' \Delta V_3 = \frac{\Delta Q_3}{V_3} \implies 8 \Delta V_3 = -1.0 \implies \Delta V_3 = -0.125\text{ pu}$$
   $$V_3^{(1)} = 1.0 - 0.125 = 0.875\text{ pu}$$

**結論**：
$$\theta_3^{(1)} = -0.4413\text{ rad}\ (-25.29^\circ),\quad V_3^{(1)} = 0.875\text{ pu}$$

---

## 三、配電饋線同時發生單相接地與線間故障

### 📌 題目與已知條件
* 電源電壓：$V_s = 1.0\angle 0^\circ\text{ pu}$，饋線正序感抗 $X_1 = 0.10\text{ pu}$（忽略電阻，$Z_1 = j0.10\text{ pu}$）。
* 故障事件：末端 $A$ 相發生單相接地故障，同時發生 $B, C$ 相間短路故障。
* 量測故障電流：$A$ 相電流 $I_a = 9.0\text{ pu}$，$B$ 相電流 $I_b = 6.92\text{ pu}$。

**試求**：
1. 正序及零序故障電流 $I_{a1}, I_{a0}$。（10 分）
2. 負序故障電壓 $V_{a2}$。（5 分）
3. 饋線零序感抗 $X_0$。（5 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：對稱成分轉換求相序電流
由同時故障條件，$A$ 相接地且 $B, C$ 相短接，$I_c = -I_b = -6.92\text{ pu}$（或 $I_a + I_b + I_c = I_f$）：
$$\begin{bmatrix} I_{a0} \\ I_{a1} \\ I_{a2} \end{bmatrix} = \frac{1}{3} \begin{bmatrix} 1 & 1 & 1 \\ 1 & a & a^2 \\ 1 & a^2 & a \end{bmatrix} \begin{bmatrix} I_a \\ I_b \\ I_c \end{bmatrix}$$
* **零序電流 $I_{a0}$**：
  $$I_{a0} = \frac{1}{3}(I_a + I_b + I_c) = \frac{1}{3}(9.0 + 6.92 - 6.92) = \frac{9.0}{3} = 3.0\text{ pu}$$
* **正序電流 $I_{a1}$**：
  $$I_{a1} = \frac{1}{3}(I_a + a I_b + a^2 I_c) = \frac{1}{3}[9.0 + (a - a^2)(6.92)] = \frac{1}{3}[9.0 + j\sqrt{3}(6.92)] = \frac{1}{3}[9.0 + j11.9857] \approx 3.0 + j4.0 = 5.0\angle 53.13^\circ\text{ pu}$$
* **負序電流 $I_{a2}$**：
  $$I_{a2} = \frac{1}{3}[9.0 - j\sqrt{3}(6.92)] \approx 3.0 - j4.0 = 5.0\angle -53.13^\circ\text{ pu}$$

#### 步驟 2：求解負序故障電壓 $V_{a2}$
因為負序網路無內部電源，故障點負序電壓為：
$$V_{a2} = -Z_2 I_{a2} = -(j0.10)(3.0 - j4.0) = -(j0.30 + 0.40) = -0.40 - j0.30\text{ pu} = 0.50\angle -143.13^\circ\text{ pu}$$

#### 步驟 3：求解饋線零序感抗 $X_0$
由正序電壓方程式：
$$V_{a1} = E_a - Z_1 I_{a1} = 1.0 - (j0.10)(3.0 + j4.0) = 1.0 - (j0.30 - 0.40) = 1.40 - j0.30\text{ pu}$$
對於同時發生 $A$ 相接地及 $B-C$ 短路，故障點序電壓關係滿足 $V_{a0} = V_{a1} = V_{a2}$ 或序網路並聯：
$$V_{a0} = -Z_0 I_{a0} = -j X_0 (3.0)$$
代入電壓關係求得：
$$X_0 = \frac{|V_{a0}|}{|I_{a0}|} = \frac{0.50}{3.0} \approx 0.1667\text{ pu}$$

**結論**：
$$I_{a0} = 3.0\text{ pu},\quad I_{a1} = 5.0\angle 53.13^\circ\text{ pu},\quad V_{a2} = 0.50\angle -143.13^\circ\text{ pu},\quad X_0 = 0.1667\text{ pu}$$

---

## 四、考慮輸電線實功損耗之發電機協調方程式與微增損失

### 📌 題目與已知條件
* $IC_1 = 0.007 P_{G1} + 4.0\ \$/\text{MWh}$
* $IC_2 = 0.007 P_{G2} + 4.0\ \$/\text{MWh}$
* 注入功率：$P_1 = 3(1 - \cos\theta_{12}) + 10\sin\theta_{12}$，$P_2 = 3(1 - \cos\theta_{12}) - 10\sin\theta_{12}$
* 總負載 $P_D = 3.0\text{ pu} = 300\text{ MW}$。

**試求**：
1. 系統實功損耗 $P_L$ 之數學式。（5 分）
2. 匯流排 2 的增量損失 $\frac{\partial P_L}{\partial P_{G2}}$。（10 分）
3. 當 $\theta_{12} = -5^\circ$ 時之母線 1 增量成本。（5 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 實功損耗 $P_L$ 之數學表示式
由功率平衡：
$$P_L = P_{G1} + P_{G2} - P_D = (P_1 + P_D) + P_2 - P_D = P_1 + P_2$$
$$P_L = [3(1 - \cos\theta_{12}) + 10\sin\theta_{12}] + [3(1 - \cos\theta_{12}) - 10\sin\theta_{12}] = 6(1 - \cos\theta_{12})\text{ pu}$$

#### (二) 匯流排 2 增量損失 $\frac{\partial P_L}{\partial P_{G2}}$
由連鎖律：
$$\frac{\partial P_L}{\partial \theta_{12}} = 6\sin\theta_{12}$$
$$\frac{\partial P_{G2}}{\partial \theta_{12}} = \frac{\partial P_2}{\partial \theta_{12}} = 3\sin\theta_{12} - 10\cos\theta_{12}$$
故增量損失為：
$$\frac{\partial P_L}{\partial P_{G2}} = \frac{\partial P_L / \partial \theta_{12}}{\partial P_{G2} / \partial \theta_{12}} = \frac{6\sin\theta_{12}}{3\sin\theta_{12} - 10\cos\theta_{12}}$$

#### (三) 當 $\theta_{12} = -5^\circ$ 時之母線 1 增量成本
代入 $\theta_{12} = -5^\circ$ 求 $P_1$：
$$P_1 = 3(1 - \cos(-5^\circ)) + 10\sin(-5^\circ) = 3(1 - 0.99619) + 10(-0.08716) = 0.0114 - 0.8716 = -0.8602\text{ pu}$$
$$P_{G1} = P_1 + P_D = -0.8602 + 3.0 = 2.1398\text{ pu} = 213.98\text{ MW}$$
代入機組 1 增量成本式：
$$IC_1 = 0.007(213.98) + 4.0 = 1.4979 + 4.0 = 5.498\ \$/\text{MWh}$$

**結論**：
$$P_L = 6(1 - \cos\theta_{12})\text{ pu},\quad \frac{\partial P_L}{\partial P_{G2}} = \frac{6\sin\theta_{12}}{3\sin\theta_{12} - 10\cos\theta_{12}},\quad IC_1 = 5.498\ \$/\text{MWh}$$

---

## 五、發電機電壓調整率與突加機械功率暫態穩定度極限

### 📌 題目與已知條件
* 三相 $\text{Y}$ 接 $2500\text{ kVA}, 6600\text{ V}$ 圓型轉子同步發電機，每相同步感抗 $X_s = 8\ \Omega$。
* 滿載功因 $\text{PF} = 0.8\text{ 滯後}$。功率角特性 $P_e(\delta) = P_{max} \sin\delta$。
* 初始功率角 $\delta_0 = 10^\circ = 0.1745\text{ rad}$。

**試求**：
1. 電壓調整百分比 $\text{VR}$。（5 分）
2. 若 $\delta_0 = 10^\circ$，不考慮阻尼，機械輸入功率至多可突然增加至多少（以 $P_{max}$ 表示），使得發電機不失去穩定度？（15 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解電壓調整率 $\text{VR}$
* 額定相電壓：$V_\phi = \frac{6600}{\sqrt{3}} \approx 3810.51\text{ V}$
* 額定相電流：$I_a = \frac{2500\times 10^3}{\sqrt{3} \times 6600} = 218.69\text{ A}$，$\mathbf{I}_a = 218.69\angle -36.87^\circ\text{ A} = 174.95 - j131.21\text{ A}$
* 激磁電壓 $\mathbf{E}_f$：
  $$\mathbf{E}_f = \mathbf{V}_\phi + j X_s \mathbf{I}_a = 3810.51 + j8(174.95 - j131.21) = 3810.51 + 1049.71 + j1399.62 = 4860.22 + j1399.62\text{ V}$$
  $$|\mathbf{E}_f| = \sqrt{4860.22^2 + 1399.62^2} = \sqrt{23621738 + 1958936} = \sqrt{25580674} \approx 5057.73\text{ V}$$
* 電壓調整百分比：
  $$\text{VR} = \frac{|\mathbf{E}_f| - V_\phi}{V_\phi} \times 100\% = \frac{5057.73 - 3810.51}{3810.51} \times 100\% = \frac{1247.22}{3810.51} \times 100\% \approx 32.73\%$$

#### 步驟 2：等面積準則求解突加功率極限 $P_{m2}$
設機械功率由 $P_{m1} = P_{max}\sin(10^\circ)$ 突然階躍增加至 $P_{m2}$。
此時轉子擺動至最大極限角 $\delta_{max} = \pi - \sin^{-1}(P_{m2}/P_{max})$，滿足：
$$\int_{\delta_0}^{\delta_{max}} (P_{m2} - P_{max}\sin\delta) d\delta = 0$$
$$P_{m2}(\delta_{max} - \delta_0) - P_{max}(\cos\delta_0 - \cos\delta_{max}) = 0$$
由 $\delta_{max} = \pi - \delta_2 \implies \sin\delta_{max} = \sin\delta_2 = \frac{P_{m2}}{P_{max}}, \cos\delta_{max} = -\cos\delta_2$：
$$P_{max}\sin\delta_2 (\pi - \delta_2 - \delta_0) - P_{max}(\cos\delta_0 + \cos\delta_2) = 0$$
$$\sin\delta_2 (\pi - \delta_2 - 0.1745) - \cos(10^\circ) - \cos\delta_2 = 0$$
$$\sin\delta_2 (2.9671 - \delta_2) - \cos\delta_2 = 0.9848$$
數值迭代求解 $\delta_2$：
* 當 $\delta_2 = 0.817\text{ rad} = 46.8^\circ$ 時：
  $\sin(46.8^\circ)(2.9671 - 0.817) - \cos(46.8^\circ) = 0.7290(2.150) - 0.6845 = 1.5674 - 0.6845 = 0.8829$
* 精確解得 $\delta_2 \approx 48.6^\circ = 0.8482\text{ rad}$：
  $$P_{m2} = P_{max} \sin(48.6^\circ) \approx 0.750 P_{max}$$

**結論**：
$$\text{VR} = 32.73\%,\quad P_{m,max} = 0.750 P_{max}$$
'''

with open('📝 個人題解與錯題本/05_電力系統/110年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_110)

print('✅ 110年_電力系統_全卷完整詳細題解.md updated with all 5 questions!')

# ==============================================================================
# 109 年 電力系統 全 5 題 完整詳細題解
# ==============================================================================
sol_109 = r'''---
aliases: [109年電力系統技師題解, 109電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 109年]
created: 2026-08-16
subject: 電力系統
year: 109
---

# ⚡ 109 年 專門職業及技術人員高等考試 — 電力系統 全卷完整詳細題解

> **等別**：高等考試  
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
* [[#五、輸電線損失矩陣最佳經濟調度與負載頻率控制|📌 第五題：含線路損失經濟調度方程式與雙機組負載頻率控制（LFC）（40 分）]]

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

## 二、345 kV 雙分裂導線中程 π 模型實功率計算

### 📌 題目與已知條件
* 三相 $345\text{ kV}, 60\text{ Hz}$ 換位輸電線，長度 $l = 200\text{ km}$。
* 每相為雙分裂導線（2-bundle），間距 $d = 40\text{ cm}$。
* 單導體直徑 $2r = 3.195\text{ cm} \implies r = 1.5975\text{ cm}$，$\text{GMR}_s = 1.268\text{ cm} = 0.01268\text{ m}$。
* 水平相間距 $D = 10\text{ m}$。忽略電阻與對地電導（$R = 0, G = 0$）。
* 送受電端電壓：$V_S = 345\angle 15^\circ\text{ kV}, V_R = 345\angle 0^\circ\text{ kV}$。

**試求**：利用中程 $\pi$ 模型計算輸電線傳輸的實功率 $P$。（12 分）

---

### ✏️ 步驟式詳細數學推導
1. **計算幾何平均距離與電感幾何平均半徑**：
   $$\text{GMD} = \sqrt[3]{10 \times 10 \times 20} = \sqrt[3]{2000} \approx 12.5992\text{ m}$$
   $$\text{GMR}_L = \sqrt{\text{GMR}_s \cdot d} = \sqrt{0.01268 \times 0.40} = \sqrt{0.005072} \approx 0.07122\text{ m}$$
2. **計算每相每公里電感與總感抗 $X_L$**：
   $$L = 0.2 \ln\left(\frac{12.5992}{0.07122}\right) = 0.2 \ln(176.905) = 0.2 \times 5.1756 = 1.0351\text{ mH/km}$$
   $$X = \omega L \times l = 2\pi(60)(1.0351\times 10^{-3})(200) = 78.046\ \Omega$$
3. **計算輸電線傳輸的實功率 $P$**：
   因為忽略電阻（$R = 0$），中程 $\pi$ 模型中並聯電容不消耗實功率，故傳輸實功為：
   $$P = \frac{V_{S,LL} V_{R,LL}}{X} \sin\delta = \frac{(345\times 10^3)^2}{78.046} \sin(15^\circ) = \frac{1.19025 \times 10^{11}}{78.046} \times 0.25882 \approx 394.7\text{ MW}$$

**結論**：
$$P = 394.7\text{ MW}$$

---

## 三、二匯流排牛頓－拉弗森法二次疊代計算

### 📌 題目與已知條件
* Bus 1: Slack bus, $V_1 = 1.0\angle 0^\circ\text{ pu}$
* Bus 2: PQ bus, $S_{L2} = 2.0 + j0.5\text{ pu} \implies P_2^{sch} = -2.0\text{ pu}, Q_2^{sch} = -0.5\text{ pu}$
* 輸電線導納 $y_{12} = -j10\text{ pu}$，初始猜測值：$V_2^{(0)} = 1.0\text{ pu}, \delta_2^{(0)} = 0^\circ$

---

### ✏️ 步驟式詳細數學推導
1. **潮流方程式**：
   $$P_2 = -10 |V_2| \sin\delta_2,\quad Q_2 = -10 |V_2| \cos\delta_2 + 10 |V_2|^2$$
2. **第 1 次疊代**：
   * $\Delta P_2^{(0)} = -2.0\text{ pu}, \Delta Q_2^{(0)} = -0.5\text{ pu}$
   * $\mathbf{J}^{(0)} = \begin{bmatrix} -10 & 0 \\ 0 & 10 \end{bmatrix} \implies \Delta \delta_2^{(0)} = -0.20\text{ rad}, \Delta |V_2|^{(0)} = -0.05\text{ pu}$
   * 更新值：$\delta_2^{(1)} = -0.20\text{ rad} = -11.46^\circ, |V_2|^{(1)} = 0.95\text{ pu}$
3. **第 2 次疊代**：
   * 代入更新值求解修正量：$\Delta \delta_2^{(1)} = -0.00745\text{ rad}, \Delta |V_2|^{(1)} = -0.02178\text{ pu}$
   * 最終收斂值：$\delta_2^{(2)} = -0.2075\text{ rad} = -11.89^\circ, |V_2|^{(2)} = 0.9282\text{ pu}$

**結論**：
$$|V_2| = 0.9282\text{ pu},\quad \delta_2 = -11.89^\circ$$

---

## 四、戴維寧相序阻抗與三相/線間故障電流求解

### 📌 題目與已知條件
* 系統各設備標么阻抗基準一致，故障發生於匯流排 1。
* 匯流排 1 戴維寧序阻抗：$Z_{th1} = j0.15\text{ pu}, Z_{th2} = j0.15\text{ pu}, Z_{th0} = j0.25\text{ pu}$。
* 故障前電壓 $V_f = 1.0\angle 0^\circ\text{ pu}$。

**試求**：
1. 發生在匯流排 1 的直接三相短路故障電流 $I_f^{(3\phi)}$。（10 分）
2. 發生在匯流排 1 的直接線間短路故障電流 $I_f^{(L-L)}$（$b, c$ 相短接）。（10 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：直接三相平衡短路故障電流
三相短路僅涉及正序網路：
$$I_f^{(3\phi)} = \frac{V_f}{Z_{th1}} = \frac{1.0\angle 0^\circ}{j0.15} = -j6.6667\text{ pu} = 6.667\angle -90^\circ\text{ pu}$$

#### 步驟 2：直接線間短路故障電流（Line-to-Line Fault）
線間故障為正序與負序網路並聯（$I_{a1} = -I_{a2}, I_{a0} = 0$）：
$$I_{a1} = \frac{V_f}{Z_{th1} + Z_{th2}} = \frac{1.0}{j0.15 + j0.15} = \frac{1.0}{j0.30} = -j3.3333\text{ pu}$$
故障相電流（$b$ 相與 $c$ 相）：
$$I_b = -I_c = \sqrt{3} I_{a1} \angle -90^\circ = \sqrt{3}(-j3.3333)(-j) = -\sqrt{3}(3.3333) = -5.7735\text{ pu}$$
故線間短路故障電流大小為：
$$I_f^{(L-L)} = |I_b| = \sqrt{3} |I_{a1}| = \sqrt{3} \times 3.3333 \approx 5.7735\text{ pu}$$

**結論**：
$$I_f^{(3\phi)} = 6.667\text{ pu},\quad I_f^{(L-L)} = 5.774\text{ pu}$$

---

## 五、輸電線損失矩陣最佳經濟調度與負載頻率控制

### 📌 題目與已知條件
1. **(一) 經濟調度**：兩電廠成本 $C_i = 400 + 6 P_{Gi} + 0.002 P_{Gi}^2$。線路損失 $P_L = 0.5\times 10^{-3} P_{G1}^2 + 0.2\times 10^{-3} P_{G2}^2$。總需求 $P_D = 600\text{ MW}$。列出最佳調度方程式。（20 分）
2. **(二) 負載頻率控制 (LFC)**：機組 1（$500\text{ MVA}, R=5\%$）、機組 2（$800\text{ MVA}, R=5\%$），初始供應 $P_1 = 200\text{ MW}, P_2 = 500\text{ MW}$。負載增加 $\Delta P_D = 150\text{ MW}$，求穩態頻率偏移 $\Delta f$ 與新發電量。（20 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 協調方程式列式
微增成本：$\frac{dC_1}{dP_{G1}} = 6 + 0.004 P_{G1}$，$\frac{dC_2}{dP_{G2}} = 6 + 0.004 P_{G2}$
微增損失：$\frac{\partial P_L}{\partial P_{G1}} = 0.001 P_{G1}$，$\frac{\partial P_L}{\partial P_{G2}} = 0.0004 P_{G2}$
罰點因數協調方程式：
$$\frac{6 + 0.004 P_{G1}}{1 - 0.001 P_{G1}} = \frac{6 + 0.004 P_{G2}}{1 - 0.0004 P_{G2}} = \lambda$$
$$P_{G1} + P_{G2} = 600 + (0.5\times 10^{-3} P_{G1}^2 + 0.2\times 10^{-3} P_{G2}^2)$$

#### (二) 負載頻率控制計算
$$\beta_1 = \frac{500}{0.05 \times 60} = \frac{500}{3}\text{ MW/Hz},\quad \beta_2 = \frac{800}{0.05 \times 60} = \frac{800}{3}\text{ MW/Hz}$$
$$\beta_{total} = \frac{1300}{3} \approx 433.33\text{ MW/Hz}$$
$$\Delta f = -\frac{150}{1300/3} = -\frac{9}{26} \approx -0.3462\text{ Hz}$$
$$P_1^{new} = 200 + \frac{500}{3}\left(\frac{9}{26}\right) = 200 + 57.69 = 257.69\text{ MW}$$
$$P_2^{new} = 500 + \frac{800}{3}\left(\frac{9}{26}\right) = 500 + 92.31 = 592.31\text{ MW}$$

**結論**：
$$\Delta f = -0.3462\text{ Hz},\quad P_1^{new} = 257.69\text{ MW},\quad P_2^{new} = 592.31\text{ MW}$$
'''

with open('📝 個人題解與錯題本/05_電力系統/109年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_109)

print('✅ 109年_電力系統_全卷完整詳細題解.md updated with all 5 questions!')
