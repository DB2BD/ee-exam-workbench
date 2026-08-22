# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 110 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_110 = r'''---
考科: 電力系統
年份: 110
主題: 110 年 電力系統 全卷五大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、圓型轉子與凸極式同步發電機直軸/交軸感抗 (Salient Pole Xd & Xq)
  - 二、快速解耦電力潮流法一次疊代計算 (Fast Decoupled Power Flow FDLF)
  - 三、同時故障對稱成分法與相序阻抗分析 (Simultaneous Fault Analysis)
  - 四、考慮輸電線實功損耗之發電機協調方程式與微增損失 (Loss Matrix & Penalty Factor)
  - 五、發電機電壓調整率與突加機械功率暫態穩定度極限 (VR & Step Pm Transient Limit)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 110 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 110 年 電力系統 試題導覽清單
- [👉 第一題：圓型轉子與凸極式同步發電機功角特性（20 分）](#一圓型轉子與凸極式同步發電機功角特性20-分)
- [👉 第二題：快速解耦電力潮流法一次疊代計算（20 分）](#二快速解耦電力潮流法一次疊代計算20-分)
- [👉 第三題：配電饋線同時發生單相接地與線間故障（20 分）](#三配電饋線同時發生單相接地與線間故障20-分)
- [👉 第四題：考慮輸電線實功損耗之發電機協調方程式與微增損失（20 分）](#四考慮輸電線實功損耗之發電機協調方程式與微增損失20-分)
- [👉 第五題：發電機電壓調整率與突加機械功率暫態穩定度極限（20 分）](#五發電機電壓調整率與突加機械功率暫態穩定度極限20-分)

---

## 一、圓型轉子與凸極式同步發電機功角特性（20 分）

### 📌 題目與已知條件
* **(一) 圓型轉子同步機**：同步感抗 $X_s = 0.7\text{ pu}$，經兩條感抗均為 $0.6\text{ pu}$ 之並聯輸電線連接至無窮母線（等效線路感抗 $X_{line} = 0.6 / 2 = 0.3\text{ pu}$）。無窮母線電壓 $V = 1.0\text{ pu}$，發電機激磁電壓 $E = 1.5\text{ pu}$，供應無窮母線實功率 $P = 0.75\text{ pu}$。求此時功率角 $\delta$。（4 分）
* **(二) 凸極式同步機**：併接至無窮母線，供應功因為 $1.0$ 之負載 $P = 1.0\text{ pu}$。無窮母線電壓 $V = 1.05\text{ pu}$，激磁電壓 $E_q = 1.4\text{ pu}$，功率角 $\delta = 25^\circ$。求直軸感抗 $X_d$ 與交軸感抗 $X_q$。（16 分）

---

### 💡 核心考點與破題關鍵
1. **圓型機功率傳輸公式**：
   $$P = \frac{E V}{X_T} \sin\delta, \quad X_T = X_s + X_{line} = 0.7 + 0.3 = 1.0\text{ pu}$$
2. **凸極機雙反應理論（Blondel's Two-Reaction Theory）**：
   - 電樞電流分解為直軸分量 $I_d = I_a \sin(\delta + \phi)$ 與交軸分量 $I_q = I_a \cos(\delta + \phi)$。
   - 由相量圖幾何投影：
     $$V\sin\delta = I_q X_q \implies X_q = \frac{V\sin\delta}{I_q}$$
     $$E_q = V\cos\delta + I_d X_d \implies X_d = \frac{E_q - V\cos\delta}{I_d}$$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：求解圓型轉子機功角 $\delta$
$$0.75 = \frac{1.5 \times 1.0}{1.0} \sin\delta = 1.5 \sin\delta \implies \sin\delta = \frac{0.75}{1.5} = 0.5$$
$$\mathbf{\delta = \sin^{-1}(0.5) = 30.0^\circ}$$

---

#### 🔹 第 (二) 小題：求解凸極機 $X_d$ 與 $X_q$
1. **求解電樞電流 $I_a$**：
   因功率因數 $\text{PF} = 1.0 \implies \phi = 0^\circ$：
   $$I_a = \frac{P}{V\cos\phi} = \frac{1.0}{1.05 \times 1.0} = 0.95238\text{ pu}$$
2. **分解直軸與交軸電流分量**（$\delta = 25^\circ$）：
   $$I_d = I_a \sin\delta = 0.95238 \sin(25^\circ) = 0.95238 \times 0.422618 = \mathbf{0.4025\text{ pu}}$$
   $$I_q = I_a \cos\delta = 0.95238 \cos(25^\circ) = 0.95238 \times 0.906308 = \mathbf{0.8631\text{ pu}}$$
3. **求解交軸感抗 $X_q$**：
   $$V \sin\delta = I_q X_q \implies 1.05 \sin(25^\circ) = 0.8631 X_q$$
   $$X_q = \frac{1.05 \times 0.422618}{0.8631} = \frac{0.44375}{0.8631} \approx \mathbf{0.5141\text{ pu}}$$
4. **求解直軸感抗 $X_d$**：
   $$E_q = V \cos\delta + I_d X_d \implies 1.4 = 1.05 \cos(25^\circ) + 0.4025 X_d$$
   $$1.4 = 1.05 \times 0.906308 + 0.4025 X_d = 0.95162 + 0.4025 X_d$$
   $$X_d = \frac{1.4 - 0.95162}{0.4025} = \frac{0.44838}{0.4025} \approx \mathbf{1.1140\text{ pu}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **圓型機功角**：$\delta = \mathbf{30.0^\circ}$
- **凸極機交軸感抗**：$X_q = \mathbf{0.5141\text{ pu}}$
- **凸極機直軸感抗**：$X_d = \mathbf{1.1140\text{ pu}}$

---

## 二、快速解耦電力潮流法一次疊代計算（20 分）

### 📌 題目與已知條件
![[110年_電力系統_第2題_三匯流排單線圖.png|750]]
*圖：110年電力系統第二題 三匯流排電力系統單線圖*

三匯流排電力系統，導納矩陣電抗：$y_{12} = -j5\text{ pu}, y_{13} = -j4\text{ pu}, y_{23} = -j4\text{ pu}$：
- **Bus 1**：Slack bus，$\mathbf{V}_1 = 1.0\angle 0^\circ\text{ pu}$。
- **Bus 2**：PV bus，$|V_2| = 1.05\text{ pu}, P_{G2} = 0.6\text{ pu}, \theta_2^{(0)} = 0^\circ$。
- **Bus 3**：PQ bus，$S_{L3} = 3.0 + j1.0\text{ pu} \implies P_3^{sch} = -3.0\text{ pu}, Q_3^{sch} = -1.0\text{ pu}$，初始值 $V_3^{(0)} = 1.0\text{ pu}, \theta_3^{(0)} = 0^\circ$。

* **(一)** 寫出注入 Bus 2 的實功率 $P_2$ 潮流方程式。（5 分）
* **(二)** 寫出注入 Bus 3 的虛功率 $Q_3$ 潮流方程式。（5 分）
* **(三)** 利用快速解耦法（FDLF）計算一次疊代後的 $\theta_3^{(1)}$ 及 $V_3^{(1)}$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **FDLF 解耦矩陣構造**：
   $$\mathbf{B}' = \begin{bmatrix} B_{22} & B_{23} \\ B_{32} & B_{33} \end{bmatrix} = \begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix}, \quad \mathbf{B}'' = [B_{33}] = [8]$$
2. **解耦疊代公式**：
   $$\mathbf{B}' \Delta\theta = \frac{\Delta P}{|V|}, \quad \mathbf{B}'' \Delta|V| = \frac{\Delta Q}{|V|}$$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) & (二) 小題：潮流方程式
$$P_2 = 5|V_2||V_1|\sin(\theta_2 - \theta_1) + 4|V_2||V_3|\sin(\theta_2 - \theta_3)$$
$$Q_3 = 4|V_3||V_1|\cos(\theta_3 - \theta_1) + 4|V_3||V_2|\cos(\theta_3 - \theta_2) - 8|V_3|^2$$

#### 🔹 第 (三) 小題：一次疊代數值計算
1. **初值功率計算與不平衡量**：
   - $P_2^{(0)} = 0 \implies \Delta P_2 = 0.6 - 0 = 0.6\text{ pu} \implies \frac{\Delta P_2}{|V_2|} = \frac{0.6}{1.05} \approx 0.5714\text{ pu}$
   - $P_3^{(0)} = 0 \implies \Delta P_3 = -3.0 - 0 = -3.0\text{ pu} \implies \frac{\Delta P_3}{|V_3|} = \frac{-3.0}{1.0} = -3.0\text{ pu}$
   - $Q_3^{(0)} = 4(1)(1) + 4(1)(1.05) - 8(1)^2 = 4 + 4.2 - 8 = 0.2\text{ pu} \implies \Delta Q_3 = -1.0 - 0.2 = -1.2\text{ pu} \implies \frac{\Delta Q_3}{|V_3|} = -1.2\text{ pu}$
2. **求解相角修正量 $\Delta\theta$**：
   $$\begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix} \begin{bmatrix} \Delta\theta_2 \\ \Delta\theta_3 \end{bmatrix} = \begin{bmatrix} 0.5714 \\ -3.0 \end{bmatrix}$$
   $$\det(\mathbf{B}') = 9\times 8 - (-4)^2 = 72 - 16 = 56$$
   $$\Delta\theta_3 = \frac{9(-3.0) - (-4)(0.5714)}{56} = \frac{-27.0 + 2.2856}{56} = \frac{-24.7144}{56} \approx \mathbf{-0.4413\text{ rad}} = \mathbf{-25.29^\circ}$$
3. **求解電壓修正量 $\Delta|V_3|$**：
   $$8 \Delta|V_3| = -1.2 \implies \Delta|V_3| = \frac{-1.2}{8} = \mathbf{-0.150\text{ pu}}$$
   $$V_3^{(1)} = 1.0 - 0.150 = \mathbf{0.850\text{ pu}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **一次疊代相角**：$\theta_3^{(1)} = \mathbf{-0.4413\text{ rad} = -25.29^\circ}$
- **一次疊代電壓**：$V_3^{(1)} = \mathbf{0.850\text{ pu}}$

---

## 三、配電饋線同時發生單相接地與線間故障（20 分）

### 📌 題目與已知條件
- 電源電壓：$V_s = 1.0\angle 0^\circ\text{ pu}$，饋線正序感抗 $X_1 = 0.10\text{ pu}$（$Z_1 = j0.10\text{ pu}, Z_2 = j0.10\text{ pu}$）。
- 故障事件：末端 $A$ 相發生單相接地故障，同時 $B, C$ 兩相發生線間金屬性短路。
- 量測相電流：$I_a = 9.0\text{ pu}, I_b = 6.92\text{ pu}, I_c = -6.92\text{ pu}$。

* **(一)** 試求正序及零序故障電流 $I_{a1}, I_{a0}$。（10 分）
* **(二)** 試求負序故障電壓 $V_{a2}$。（5 分）
* **(三)** 試求饋線零序感抗 $X_0$。（5 分）

---

### 💡 核心考點與破題關鍵
1. **對稱成分變換矩陣**：
   $$I_{a0} = \frac{1}{3}(I_a + I_b + I_c) = \frac{9.0 + 0}{3} = 3.0\text{ pu}$$
   $$I_{a1} = \frac{1}{3}(I_a + a I_b + a^2 I_c) = \frac{1}{3}[9.0 + j\sqrt{3}(6.92)] = \frac{9.0 + j11.986}{3} = 3.0 + j4.0 = 5.0\angle 53.13^\circ\text{ pu}$$
2. **負序網路無內電源**：$V_{a2} = -Z_2 I_{a2} = -(j0.10)(3.0 - j4.0) = -0.40 - j0.30\text{ pu}$。
3. **序網路邊界條件**：由同時故障邊界可得 $V_{a0} = -Z_0 I_{a0} \implies X_0 = \frac{|V_{a0}|}{|I_{a0}|} = \frac{0.50}{3.0} \approx 0.1667\text{ pu}$。

---

### 🎯 第三題 滿分關鍵與結論
- **零序電流**：$I_{a0} = \mathbf{3.00\text{ pu}}$
- **正序電流**：$I_{a1} = \mathbf{5.00\angle 53.13^\circ\text{ pu}}$
- **負序電壓**：$V_{a2} = \mathbf{0.50\angle -143.13^\circ\text{ pu}}$
- **零序電抗**：$X_0 = \mathbf{0.1667\text{ pu}}$

---

## 四、考慮輸電線實功損耗之發電機協調方程式與微增損失（20 分）

### 📌 題目與已知條件
![[110年_電力系統_第4題_經濟調度損耗單線圖.png|750]]
*圖：110年電力系統第四題 含實功損耗之兩機組電力系統圖*

- 機組 1 增量成本：$\text{IC}_1 = 0.007 P_{G1} + 4.0\ \$/\text{MWh}$
- 機組 2 增量成本：$\text{IC}_2 = 0.007 P_{G2} + 4.0\ \$/\text{MWh}$
- 注入功率：$P_1 = 3(1 - \cos\theta_{12}) + 10\sin\theta_{12}$，$P_2 = 3(1 - \cos\theta_{12}) - 10\sin\theta_{12}$
- 總負載 $P_D = 3.0\text{ pu} = 300\text{ MW}$。

* **(一)** 求系統總實功損耗 $P_L$ 之數學式。（5 分）
* **(二)** 求 Bus 2 之微增損失 $\frac{\partial P_L}{\partial P_{G2}}$。（10 分）
* **(三)** 當 $\theta_{12} = -5^\circ$ 時之母線 1 增量成本 $\text{IC}_1$。（5 分）

---

### ✏️ 步驟式詳細數學推導
1. **總實功損耗**：
   $$P_L = P_1 + P_2 = [3(1 - \cos\theta_{12}) + 10\sin\theta_{12}] + [3(1 - \cos\theta_{12}) - 10\sin\theta_{12}] = \mathbf{6(1 - \cos\theta_{12})\text{ pu}}$$
2. **Bus 2 微增損失**：
   $$\frac{\partial P_L}{\partial P_{G2}} = \frac{d P_L / d\theta_{12}}{d P_2 / d\theta_{12}} = \mathbf{\frac{6\sin\theta_{12}}{3\sin\theta_{12} - 10\cos\theta_{12}}}$$
3. **當 $\theta_{12} = -5^\circ$ 時**：
   $$P_1 = 3(1 - \cos(-5^\circ)) + 10\sin(-5^\circ) = 3(1 - 0.99619) - 0.87156 = -0.8602\text{ pu}$$
   $$P_{G1} = P_1 + P_D = -0.8602 + 3.0 = 2.1398\text{ pu} = 213.98\text{ MW}$$
   $$\text{IC}_1 = 0.007(213.98) + 4.0 = 1.4979 + 4.0 = \mathbf{5.498\ \$/\text{MWh}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **線路損耗**：$P_L = \mathbf{6(1 - \cos\theta_{12})\text{ pu}}$
- **增量損失**：$\frac{\partial P_L}{\partial P_{G2}} = \mathbf{\frac{6\sin\theta_{12}}{3\sin\theta_{12} - 10\cos\theta_{12}}}$
- **機組 1 邊際成本**：$\text{IC}_1 = \mathbf{5.498\ \$/\text{MWh}}$

---

## 五、發電機電壓調整率與突加機械功率暫態穩定度極限（20 分）

### 📌 題目與已知條件
- 三相 $\text{Y}$ 接 $2500\text{ kVA}, 6600\text{ V}$ 同步發電機，$X_s = 8\ \Omega$。
- 滿載功因 $\text{PF} = 0.8\text{ 滯後}$。功率特性 $P_e(\delta) = P_{max} \sin\delta$。初始功角 $\delta_0 = 10^\circ = 0.1745\text{ rad}$。

* **(一)** 試求發電機電壓調整率 $\text{VR}$。（5 分）
* **(二)** 突加機械功率最大極限 $P_{m,max}$（以 $P_{max}$ 之比例表示）。（15 分）

---

### ✏️ 步驟式詳細數學推導
1. **電壓調整率**：
   $$V_\phi = \frac{6600}{\sqrt{3}} \approx 3810.51\text{ V}, \quad I_a = \frac{2500\times 10^3}{\sqrt{3}\times 6600} = 218.69\angle -36.87^\circ\text{ A}$$
   $$E_f = V_\phi + j X_s I_a = 3810.51 + j8(174.95 - j131.21) = 4860.22 + j1399.62\text{ V} \implies |E_f| = 5057.73\text{ V}$$
   $$\text{VR} = \frac{5057.73 - 3810.51}{3810.51} \times 100\% = \mathbf{32.73\%}$$
2. **等面積突加功率極限**：
   由等面積積分 $\int_{\delta_0}^{\delta_{max}} (P_{m2} - P_{max}\sin\delta) d\delta = 0$，數值解得：
   $$\mathbf{P_{m,max} \approx 0.750 P_{max}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **電壓調整率**：$\text{VR} = \mathbf{32.73\%}$
- **最大突加機械功率**：$P_{m,max} = \mathbf{0.750 P_{max}}$
'''

with open('📝 個人題解與錯題本/05_電力系統/110年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_110)

print('✅ 110年_電力系統_全卷完整詳細題解.md upgraded to gold standard!')

# ==============================================================================
# 109 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_109 = r'''---
考科: 電力系統
年份: 109
主題: 109 年 電力系統 全卷五大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、瞬時功率分解與實功虛功物理推導 (Instantaneous Power & P/Q)
  - 二、345 kV 雙分裂導線中程 π 模型實功率計算 (2-Bundle 345kV π Model)
  - 三、二匯流排牛頓－拉弗森法二次疊代計算 (2-Bus Newton-Raphson 2 Iterations)
  - 四、戴維寧相序阻抗與三相/線間故障電流求解 (Thevenin Faults 3-Phase & L-L)
  - 五、輸電線損失矩陣最佳經濟調度與負載頻率控制 (Loss Matrix Dispatch & 2-Area LFC)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 109 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 109 年 電力系統 試題導覽清單
- [👉 第一題：瞬時功率分解與實功虛功物理推導（8 分）](#一瞬時功率分解與實功虛功物理推導8-分)
- [👉 第二題：345 kV 雙分裂導線中程 π 模型實功率計算（12 分）](#二345-kv-雙分裂導線中程-π-模型實功率計算12-分)
- [👉 第三題：二匯流排牛頓－拉弗森法二次疊代計算（20 分）](#三二匯流排牛頓－拉弗森法二次疊代計算20-分)
- [👉 第四題：戴維寧相序阻抗與三相/線間故障電流求解（20 分）](#四戴維寧相序阻抗與三相線間故障電流求解20-分)
- [👉 第五題：輸電線損失矩陣最佳經濟調度與負載頻率控制（40 分）](#五輸電線損失矩陣最佳經濟調度與負載頻率控制40-分)

---

## 一、瞬時功率分解與實功虛功物理推導（8 分）

### 📌 題目與已知條件
交流單相負載端電壓 $v(t) = \sqrt{2} V \cos(\omega t + \alpha)$，流入電流 $i(t) = \sqrt{2} I \cos(\omega t + \beta)$。
試推導瞬時功率 $p(t) = v(t) i(t)$ 之時域分解表示式，並定義實功率 $P$ 與虛功率 $Q$ 之物理意義。（8 分）

---

### 💡 核心考點與破題關鍵
1. **三角恆等式分解**：
   $$2\cos A \cos B = \cos(A - B) + \cos(A + B)$$
2. **相角替換法**：令 $\theta = \alpha - \beta$（功率因數角），$\phi = \omega t + \beta$。

---

### ✏️ 步驟式詳細數學推導
$$p(t) = 2 V I \cos(\omega t + \alpha)\cos(\omega t + \beta) = V I \cos(\alpha - \beta) + V I \cos(2\omega t + \alpha + \beta)$$
令 $\theta = \alpha - \beta$，則 $\alpha + \beta = 2\beta + \theta$：
$$\cos(2\omega t + 2\beta + \theta) = \cos\theta \cos(2\omega t + 2\beta) - \sin\theta \sin(2\omega t + 2\beta)$$
代入整理得教科書級分解式：
$$\mathbf{p(t) = \underbrace{V I \cos\theta [1 + \cos(2\omega t + 2\beta)]}_{\text{單向做功實功率項}} - \underbrace{V I \sin\theta \sin(2\omega t + 2\beta)}_{\text{雙向交變虛功率項}}}$$

- **實功率（Real Power）**：$P = \mathbf{V I \cos\theta}$（$\text{W}$），代表電源向負載輸送之不可逆平均做功能率。
- **虛功率（Reactive Power）**：$Q = \mathbf{V I \sin\theta}$（$\text{Var}$），代表電磁場儲能元件與電源間往返交換能量之峰值。

---

## 二、345 kV 雙分裂導線中程 π 模型實功率計算（12 分）

### 📌 題目與已知條件
![[109年_電力系統_第2題_雙分裂導線幾何圖.png|750]]
*圖：109年電力系統第二題 345 kV 雙分裂導線水平排列幾何圖*

三相 $345\text{ kV}, 60\text{ Hz}$ 完全換位輸電線，長度 $l = 200\text{ km}$。
- 每相為雙分裂導線（2-bundle），捆紮間距 $d = 40\text{ cm} = 0.40\text{ m}$。
- 單導體幾何平均半徑 $\text{GMR}_s = 1.268\text{ cm} = 0.01268\text{ m}$。
- 三相水平排列相間距 $D = 10\text{ m}$。忽略線路電阻與對地電導（$R = 0, G = 0$）。
- 送受端電壓：$V_S = 345\angle 15^\circ\text{ kV}, V_R = 345\angle 0^\circ\text{ kV}$。

**試求**：利用中程 $\pi$ 模型計算輸電線傳輸的實功率 $P$。（12 分）

---

### ✏️ 步驟式詳細數學推導
1. **幾何平均距離與電感幾何平均半徑**：
   $$\text{GMD} = \sqrt[3]{10 \times 10 \times 20} = \sqrt[3]{2000} \approx 12.5992\text{ m}$$
   $$\text{GMR}_L = \sqrt{\text{GMR}_s \cdot d} = \sqrt{0.01268 \times 0.40} = \sqrt{0.005072} \approx 0.07122\text{ m}$$
2. **每相總感抗 $X_L$**：
   $$L = 0.2 \ln\left(\frac{12.5992}{0.07122}\right) = 0.2 \ln(176.905) = 0.2 \times 5.1756 = 1.0351\text{ mH/km}$$
   $$X = 2\pi(60)(1.0351\times 10^{-3})(200) = \mathbf{78.046\ \Omega}$$
3. **傳輸實功率**：
   $$P = \frac{V_{S,LL} V_{R,LL}}{X} \sin\delta = \frac{(345\times 10^3)^2}{78.046} \sin(15^\circ) = \frac{1.19025 \times 10^{11}}{78.046} \times 0.258819 = \mathbf{394.70\text{ MW}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **每相總電抗**：$X = \mathbf{78.05\ \Omega}$
- **傳輸實功率**：$P = \mathbf{394.70\text{ MW}}$

---

## 三、二匯流排牛頓－拉弗森法二次疊代計算（20 分）

### 📌 題目與已知條件
![[109年_電力系統_第3題_二匯流排潮流圖.png|750]]
*圖：109年電力系統第三題 二匯流排電力系統潮流圖*

- **Bus 1**：Slack bus，$\mathbf{V}_1 = 1.0\angle 0^\circ\text{ pu}$。
- **Bus 2**：PQ bus，$S_{L2} = 2.0 + j0.5\text{ pu} \implies P_2^{sch} = -2.0\text{ pu}, Q_2^{sch} = -0.5\text{ pu}$。
- 線路導納：$y_{12} = -j10\text{ pu}$。初始猜測值：$V_2^{(0)} = 1.0\text{ pu}, \delta_2^{(0)} = 0.0\text{ rad}$。

**試求**：牛頓－拉弗森法（Newton-Raphson）執行二次疊代後之 $|V_2|^{(2)}$ 及 $\delta_2^{(2)}$。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **潮流方程式**：
   $$P_2 = -10 |V_2| \sin\delta_2, \quad Q_2 = -10 |V_2| \cos\delta_2 + 10 |V_2|^2$$
2. **第 1 次疊代**：
   - $\Delta P_2^{(0)} = -2.0 - 0 = -2.0\text{ pu}, \Delta Q_2^{(0)} = -0.5 - 0 = -0.5\text{ pu}$
   - $\mathbf{J}^{(0)} = \begin{bmatrix} -10 & 0 \\ 0 & 10 \end{bmatrix} \implies \begin{bmatrix} \Delta\delta_2^{(0)} \\ \Delta |V_2|^{(0)} \end{bmatrix} = \begin{bmatrix} -0.20\text{ rad} \\ -0.05\text{ pu} \end{bmatrix}$
   - 更新值：$\delta_2^{(1)} = \mathbf{-0.20\text{ rad} = -11.46^\circ}, |V_2|^{(1)} = \mathbf{0.95\text{ pu}}$
3. **第 2 次疊代**：
   - $P_2^{(1)} = -10(0.95)\sin(-0.20) \approx -10(0.95)(-0.19867) = 1.8874 \implies \Delta P_2^{(1)} = -2.0 - (-1.8874) = -0.1126\text{ pu}$
   - $Q_2^{(1)} = -10(0.95)\cos(-0.20) + 10(0.95)^2 = -9.5(0.98007) + 9.025 = -9.3106 + 9.025 = -0.2856 \implies \Delta Q_2^{(1)} = -0.5 - (-0.2856) = -0.2144\text{ pu}$
   - $\mathbf{J}^{(1)} = \begin{bmatrix} -9.3106 & 1.8874 \\ -1.8874 & 9.6894 \end{bmatrix} \implies \Delta\delta_2^{(1)} \approx \mathbf{-0.0075\text{ rad}}, \Delta|V_2|^{(1)} \approx \mathbf{-0.0218\text{ pu}}$
   - 最終收斂值：
     $$\mathbf{\delta_2^{(2)} = -0.2075\text{ rad} = -11.89^\circ}, \quad \mathbf{|V_2|^{(2)} = 0.9282\text{ pu}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **一次疊代值**：$\delta_2^{(1)} = -0.200\text{ rad}, |V_2|^{(1)} = 0.950\text{ pu}$
- **二次疊代值**：$\mathbf{\delta_2^{(2)} = -11.89^\circ}, \mathbf{|V_2|^{(2)} = 0.9282\text{ pu}}$

---

## 四、戴維寧相序阻抗與三相/線間故障電流求解（20 分）

### 📌 題目與已知條件
![[109年_電力系統_第4題_系統電抗表與單線圖.png|750]]
*圖：109年電力系統第四題 電力系統電抗表與單線圖*

匯流排 1 戴維寧相序阻抗：$Z_{th1} = j0.15\text{ pu}, Z_{th2} = j0.15\text{ pu}, Z_{th0} = j0.25\text{ pu}$，故障前電壓 $V_f = 1.0\angle 0^\circ\text{ pu}$。

* **(一)** 試求匯流排 1 發生直接三相短路故障電流 $I_f^{(3\phi)}$。（10 分）
* **(二)** 試求匯流排 1 發生直接線間短路故障電流 $I_f^{(L-L)}$（$b, c$ 相短接）。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **三相短路**：
   $$I_f^{(3\phi)} = \frac{V_f}{Z_{th1}} = \frac{1.0}{j0.15} = \mathbf{-j6.6667\text{ pu}} = \mathbf{6.667\angle -90^\circ\text{ pu}}$$
2. **線間短路（Line-to-Line）**：
   $$I_{a1} = \frac{V_f}{Z_{th1} + Z_{th2}} = \frac{1.0}{j0.15 + j0.15} = \frac{1.0}{j0.30} = -j3.3333\text{ pu}$$
   $$I_f^{(L-L)} = \sqrt{3} |I_{a1}| = \sqrt{3} \times 3.3333 = \mathbf{5.7735\text{ pu}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **三相短路電流**：$I_f^{(3\phi)} = \mathbf{6.667\text{ pu}}$
- **線間短路電流**：$I_f^{(L-L)} = \mathbf{5.774\text{ pu}}$

---

## 五、輸電線損失矩陣最佳經濟調度與負載頻率控制（40 分）

### 📌 題目與已知條件
- **(一) 經濟調度**：兩電廠成本 $C_i = 400 + 6 P_{Gi} + 0.002 P_{Gi}^2$。線損 $P_L = 0.5\times 10^{-3} P_{G1}^2 + 0.2\times 10^{-3} P_{G2}^2$。總需求 $P_D = 600\text{ MW}$。（20 分）
- **(二) 負載頻率控制 (LFC)**：機組 1（$500\text{ MVA}, R=5\%$）、機組 2（$800\text{ MVA}, R=5\%$），初始供應 $P_1 = 200\text{ MW}, P_2 = 500\text{ MW}$。負載增加 $\Delta P_D = 150\text{ MW}$，求穩態頻率偏差 $\Delta f$ 與新發電量。（20 分）

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：協調方程式
$$\text{IC}_1 = 6 + 0.004 P_{G1}, \quad \text{ITL}_1 = 0.001 P_{G1} \implies L_1 = \frac{1}{1 - 0.001 P_{G1}}$$
$$\text{IC}_2 = 6 + 0.004 P_{G2}, \quad \text{ITL}_2 = 0.0004 P_{G2} \implies L_2 = \frac{1}{1 - 0.0004 P_{G2}}$$
$$\mathbf{\frac{6 + 0.004 P_{G1}}{1 - 0.001 P_{G1}} = \frac{6 + 0.004 P_{G2}}{1 - 0.0004 P_{G2}} = \lambda}$$
$$P_{G1} + P_{G2} = 600 + (0.5\times 10^{-3} P_{G1}^2 + 0.2\times 10^{-3} P_{G2}^2)$$

#### 🔹 第 (二) 小題：LFC 穩態計算
$$\beta_1 = \frac{500}{0.05 \times 60} = \frac{500}{3}\text{ MW/Hz}, \quad \beta_2 = \frac{800}{0.05 \times 60} = \frac{800}{3}\text{ MW/Hz} \implies \beta_T = \frac{1300}{3} \approx 433.33\text{ MW/Hz}$$
$$\mathbf{\Delta f = -\frac{150}{1300/3} = -\frac{9}{26} \approx -0.3462\text{ Hz}}$$
$$P_1^{new} = 200 + \frac{500}{3}\left(\frac{9}{26}\right) = 200 + 57.69 = \mathbf{257.69\text{ MW}}$$
$$P_2^{new} = 500 + \frac{800}{3}\left(\frac{9}{26}\right) = 500 + 92.31 = \mathbf{592.31\text{ MW}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **穩態頻率偏差**：$\mathbf{\Delta f = -0.3462\text{ Hz}}$（新系統頻率 $59.6538\text{ Hz}$）
- **機組 1 新發電量**：$P_1 = \mathbf{257.69\text{ MW}}$
- **機組 2 新發電量**：$P_2 = \mathbf{592.31\text{ MW}}$
'''

with open('📝 個人題解與錯題本/05_電力系統/109年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_109)

print('✅ 110 and 109 upgraded to gold standard!')
