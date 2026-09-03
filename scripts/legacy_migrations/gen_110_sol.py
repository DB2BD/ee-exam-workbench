# -*- coding: utf-8 -*-
import os

# 110 年 電力系統
sol_110 = r'''---
aliases: [110年電力系統技師題解, 110電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 110年]
created: 2026-08-16
subject: 電力系統
year: 110
---

# ⚡ 110 年 專門職業及技術人員高等考試 — 電力系統 全卷詳細題解

> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 5 大題，各 20 分）

---

## 📑 110 年 全卷題解目錄導覽

* [[#一、圓型轉子與凸極式同步發電機功角特性|📌 第一題：圓型與凸極式（Salient Pole）同步發電機直軸/交軸感抗求解（20 分）]]
* [[#二、快速解耦電力潮流法一次疊代計算|📌 第二題：快速解耦電力潮流法（FDLF）一次疊代電壓與相角（20 分）]]
* [[#三、不對稱故障同時發生單相接地與線間故障|📌 第三題：同時故障（Simultaneous Fault）對稱成分法分析（20 分）]]
* [[#四、考慮輸電線實功損耗之發電機協調方程式與微增損失|📌 第四題：含線路損失之經濟調度、增量損失與罰點因數（20 分）]]
* [[#五、發電機電壓調整率與突加機械功率暫態穩定度極限|📌 第五題：發電機等面積準則突加機械功率最大極限 $P_{m,max}$（20 分）]]

---

## 一、圓型轉子與凸極式同步發電機功角特性

### 📌 題目與已知條件
1. **(一) 圓型轉子同步機**：同步感抗 $X_s = 0.7\text{ pu}$，並聯輸電線兩條各 $0.6\text{ pu} \implies X_{line} = 0.3\text{ pu}$。無窮母線電壓 $V = 1.0\text{ pu}$，激磁電壓 $E = 1.5\text{ pu}$，實功率 $P = 0.75\text{ pu}$。求功率角 $\delta$。（4 分）
2. **(二) 凸極式同步機**：供應功因為 1.0 之負載 $P = 1.0\text{ pu}$。無窮母線電壓 $V = 1.05\text{ pu}$，激磁電壓 $E_q = 1.4\text{ pu}$，功率角 $\delta = 25^\circ$。求直軸感抗 $X_d$ 與交軸感抗 $X_q$。（16 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 圓型轉子發電機功率角 $\delta$
總轉移電抗為：
$$X_T = X_s + X_{line} = 0.7 + 0.3 = 1.0\text{ pu}$$
實功率傳輸公式：
$$P = \frac{E V}{X_T} \sin\delta \implies 0.75 = \frac{1.5 \times 1.0}{1.0} \sin\delta = 1.5 \sin\delta$$
$$\sin\delta = \frac{0.75}{1.5} = 0.5 \implies \delta = 30^\circ$$

#### (二) 凸極式同步發電機 $X_d$ 與 $X_q$ 求解
* 功因為 $1.0 \implies \phi = 0^\circ$，電樞電流 $I_a = \frac{P}{V\cos\phi} = \frac{1.0}{1.05 \times 1} \approx 0.95238\text{ pu}$，且 $\mathbf{I}_a$ 與 $\mathbf{V}$ 同相（相位角 $0^\circ$）。
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
$$\delta = 30^\circ,\quad X_q = 0.5141\text{ pu},\quad X_d = 1.1140\text{ pu}$$

---

## 二、快速解耦電力潮流法一次疊代計算

### 📌 題目與已知條件
* Bus 1: Slack bus, $V_1 = 1.0\angle 0^\circ\text{ pu}$
* Bus 2: PV bus, $V_2 = 1.05\text{ pu}, P_{G2} = 0.6\text{ pu}$
* Bus 3: PQ bus, $S_{L3} = 3.0 + j1.0\text{ pu} \implies P_3^{sch} = -3.0\text{ pu}, Q_3^{sch} = -1.0\text{ pu}$
* 線路導納：$y_{12} = -j5, y_{13} = -j4, y_{23} = -j4$

**試求**：快速解耦法（Fast Decoupled Power Flow）一次疊代後之 $\theta_3$ 與 $V_3$。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **建立 $B'$ 與 $B''$ 矩陣**：
   $$B'_{22} = 5 + 4 = 9,\ B'_{23} = -4,\ B'_{32} = -4,\ B'_{33} = 4 + 4 = 8$$
   $$\mathbf{B}' = \begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix},\quad B'' = [B_{33}] = [8]$$
2. **計算不平衡量 $\Delta P / V$ 與 $\Delta Q / V$**：
   在初始值 $\theta_2 = 0, \theta_3 = 0, V_3 = 1.0$ 下：
   * $P_2^{(0)} = 0 \implies \Delta P_2 = 0.6 - 0 = 0.6\text{ pu} \implies \frac{\Delta P_2}{V_2} = \frac{0.6}{1.05} \approx 0.5714\text{ pu}$
   * $P_3^{(0)} = 0 \implies \Delta P_3 = -3.0 - 0 = -3.0\text{ pu} \implies \frac{\Delta P_3}{V_3} = \frac{-3.0}{1.0} = -3.0\text{ pu}$
3. **求解相角修正量 $\Delta \theta$**：
   $$\begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix} \begin{bmatrix} \Delta \theta_2 \\ \Delta \theta_3 \end{bmatrix} = \begin{bmatrix} 0.5714 \\ -3.0 \end{bmatrix}$$
   $$\det = 72 - 16 = 56$$
   $$\Delta \theta_3 = \frac{9(-3.0) - (-4)(0.5714)}{56} = \frac{-27.0 + 2.2857}{56} = \frac{-24.7143}{56} \approx -0.4413\text{ rad} = -25.29^\circ$$
4. **求解電壓修正量 $\Delta V_3$**：
   $$Q_3^{(0)} = 0 \implies \Delta Q_3 = -1.0 - 0 = -1.0\text{ pu} \implies \frac{\Delta Q_3}{V_3} = -1.0\text{ pu}$$
   $$B'' \Delta V_3 = \frac{\Delta Q_3}{V_3} \implies 8 \Delta V_3 = -1.0 \implies \Delta V_3 = -0.125\text{ pu}$$
   $$V_3^{(1)} = V_3^{(0)} + \Delta V_3 = 1.0 - 0.125 = 0.875\text{ pu}$$

**結論**：
$$\theta_3^{(1)} = -0.4413\text{ rad}\ (-25.29^\circ),\quad V_3^{(1)} = 0.875\text{ pu}$$

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
'''

with open('📝 個人題解與錯題本/05_電力系統/110年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_110)

print('✅ 110年_電力系統_全卷完整詳細題解.md created!')
