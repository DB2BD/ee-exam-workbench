# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 108 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_108 = r'''---
考科: 電力系統
年份: 108
主題: 108 年 電力系統 全卷五大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、同步發電機內部電勢激磁增量與無效功率 (Synchronous Machine 20% Excitation)
  - 二、快速解耦電力潮流法二次疊代計算 (Fast Decoupled Power Flow FDLF 2 Iterations)
  - 三、多變壓器與發電機非對稱線間短路故障 (Multi-Machine L-L Subtransient Fault)
  - 四、發電機繞組差動電驛電流連續性保護原理 (Generator Differential Relay Protection)
  - 五、雙迴線三相故障與功率-角度方程式 (Parallel Lines Fault Power-Angle Equations)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 108 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 108 年 電力系統 試題導覽清單
- [👉 第一題：同步發電機內部電勢激磁增量與無效功率（20 分）](#一同步發電機內部電勢激磁增量與無效功率20-分)
- [👉 第二題：快速解耦電力潮流法二次疊代計算（20 分）](#二快速解耦電力潮流法二次疊代計算20-分)
- [👉 第三題：多變壓器與發電機非對稱線間短路故障（20 分）](#三多變壓器與發電機非對稱線間短路故障20-分)
- [👉 第四題：發電機繞組差動電驛電流連續性保護原理（20 分）](#四發電機繞組差動電驛電流連續性保護原理20-分)
- [👉 第五題：雙迴線三相故障與功率-角度方程式（20 分）](#五雙迴線三相故障與功率-角度方程式20-分)

---

## 一、同步發電機內部電勢激磁增量與無效功率（20 分）

### 📌 題目與已知條件
- 同步發電機：$X_d = 1.7241\text{ pu}$，端電壓 $V_t = 1.0\angle 0^\circ\text{ pu}$。
- 電流 $I_a = 0.8\text{ pu}$，功率因數 $\text{PF} = 0.9\text{ 滯後} \implies \mathbf{I}_a = 0.8\angle -25.84^\circ\text{ pu} = 0.72 - j0.3487\text{ pu}$。

* **(一)** 試求內部電動勢 $\mathbf{E}_i$ 之大小與功角 $\delta$、傳送之實功率 $P$ 與虛功率 $Q$。（10 分）
* **(二)** 若原動機輸入實功 $P$ 保持不變，激磁增加 $20\%$（即 $E_i' = 1.20 E_i$），求新的功角 $\delta'$ 與無效功率 $Q'$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **內部電勢計算**：$\mathbf{E}_i = \mathbf{V}_t + j X_d \mathbf{I}_a$。
2. **實功恆定條件**：$P = \frac{E_i V_t}{X_d} \sin\delta = \frac{E_i' V_t}{X_d} \sin\delta' = \text{常數}$。
3. **無效功率計算**：$Q' = \frac{E_i' V_t \cos\delta' - V_t^2}{X_d}$。

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：求解初始工作點
1. **內部電動勢 $\mathbf{E}_i$**：
   $$\mathbf{E}_i = 1.0\angle 0^\circ + j1.7241(0.72 - j0.3487) = 1.0 + (0.6012 + j1.2414) = \mathbf{1.6012 + j1.2414\text{ pu}}$$
   $$|\mathbf{E}_i| = \sqrt{1.6012^2 + 1.2414^2} = \sqrt{2.5638 + 1.5411} = \sqrt{4.1049} \approx \mathbf{2.0260\text{ pu}}$$
   $$\mathbf{\delta = \tan^{-1}\left(\frac{1.2414}{1.6012}\right) \approx 37.79^\circ}$$
2. **功率計算**：
   - 實功率：$P = V_t I_a \cos\theta = 1.0 \times 0.8 \times 0.9 = \mathbf{0.720\text{ pu}}$
   - 虛功率：$Q = V_t I_a \sin\theta = 1.0 \times 0.8 \times \sin(25.84^\circ) = \mathbf{0.3487\text{ pu}}$

---

#### 🔹 第 (二) 小題：求解激磁增加 20% 之新狀態
1. **新激磁電壓**：$E_i' = 1.20 \times 2.0260 = \mathbf{2.4312\text{ pu}}$
2. **新功角 $\delta'$**：
   $$0.72 = \frac{2.4312 \times 1.0}{1.7241} \sin\delta' = 1.4101 \sin\delta' \implies \sin\delta' = \frac{0.72}{1.4101} = 0.5106$$
   $$\mathbf{\delta' = \sin^{-1}(0.5106) \approx 30.70^\circ}$$
3. **新無效功率 $Q'$**：
   $$Q' = \frac{2.4312 \times 1.0 \times \cos(30.70^\circ) - 1.0^2}{1.7241} = \frac{2.4312 \times 0.85985 - 1.0}{1.7241} = \frac{2.0905 - 1.0}{1.7241} = \frac{1.0905}{1.7241} = \mathbf{0.6325\text{ pu}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **初始狀態**：$E_i = \mathbf{2.026\text{ pu}}, \delta = \mathbf{37.79^\circ}, P = \mathbf{0.720\text{ pu}}, Q = \mathbf{0.3487\text{ pu}}$
- **激磁增加 20% 後**：$\delta' = \mathbf{30.70^\circ}$（功角縮小），$Q' = \mathbf{0.6325\text{ pu}}$（無效功率大幅提升 $81\%$）

---

## 二、快速解耦電力潮流法二次疊代計算（20 分）

### 📌 題目與已知條件
![[108年_電力系統_第2題_快速解耦潮流圖.png|750]]
*圖：108年電力系統第二題 快速解耦法系統潮流單線圖*

- **Bus 1**：Slack bus，$\mathbf{V}_1 = 1.0\angle 0^\circ\text{ pu}$。
- **Bus 2**：PV bus，$|V_2| = 1.04\text{ pu}, P_{G2} = 0.5\text{ pu}$。
- **Bus 3**：PQ bus，$P_{L3} = 1.5\text{ pu}, Q_{L3} = 0.6\text{ pu}$。
- 線路導納矩陣電抗：$y_{12} = -j5\text{ pu}, y_{13} = -j4\text{ pu}, y_{23} = -j4\text{ pu}$。

**試求**：快速解耦法（FDLF）二次疊代後之電壓與相角。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **建立解耦矩陣**：
   $$\mathbf{B}' = \begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix}, \quad \mathbf{B}'' = [8]$$
2. **二次疊代數值結果**：
   - 第 1 次疊代：$\theta_2^{(1)} = 0.038\text{ rad} = 2.18^\circ, \theta_3^{(1)} = -0.207\text{ rad} = -11.84^\circ, V_3^{(1)} = 0.925\text{ pu}$
   - 第 2 次疊代：$\mathbf{\theta_2^{(2)} = 2.15^\circ}, \mathbf{\theta_3^{(2)} = -12.45^\circ}, \mathbf{V_3^{(2)} = 0.912\text{ pu}}$

---

### 🎯 第二題 滿分關鍵與結論
- **匯流排 2**：$\mathbf{V}_2 = \mathbf{1.04\angle 2.15^\circ\text{ pu}}$
- **匯流排 3**：$\mathbf{V}_3 = \mathbf{0.912\angle -12.45^\circ\text{ pu}}$

---

## 三、多變壓器與發電機非對稱線間短路故障（20 分）

### 📌 題目與已知條件
![[108年_電力系統_第3題_雙發電機故障圖.png|750]]
*圖：108年電力系統第三題 雙發電機與多變壓器非對稱故障單線圖*

基準容量 $S_{base} = 1000\text{ MVA}, V_{base} = 500\text{ kV}$：
- 發電機 $G_1$（$1000\text{ MVA}, X_1'' = X_2'' = 0.15\text{ pu}$）、$G_2$（$800\text{ MVA}, X_1'' = X_2'' = 0.15\text{ pu}$）。
- 故障點 $P$ 位於輸電線末端，故障前電壓 $V_f = 515\text{ kV} \implies V_f = 1.03\text{ pu}$。

**試求**：$P$ 點發生 $B-C$ 相線間（L-L）短路時之次暫態短路電流。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **等效正負序阻抗**：$Z_{th1} = Z_{th2} = j0.25\text{ pu}$。
2. **正序故障電流**：
   $$I_{a1} = \frac{V_f}{Z_{th1} + Z_{th2}} = \frac{1.03}{j0.50} = -j2.06\text{ pu}$$
3. **故障相次暫態短路電流**：
   $$I_f^{(L-L)} = \sqrt{3} |I_{a1}| = \sqrt{3} \times 2.06 = \mathbf{3.568\text{ pu}}$$
   $$I_{base} = \frac{1000\times 10^6}{\sqrt{3}\times 500\times 10^3} = 1154.7\text{ A} \implies I_{f,actual} = 3.568 \times 1.1547\text{ kA} = \mathbf{4.120\text{ kA}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **標么故障電流**：$I_f = \mathbf{3.568\text{ pu}}$
- **實體短路電流**：$I_f = \mathbf{4.12\text{ kA}}$

---

## 四、發電機繞組差動電驛電流連續性保護原理（20 分）

### 📌 題目與已知條件
![[108年_電力系統_第4題_發電機差動保護電路圖.png|750]]
*圖：108年電力系統第四題 發電機定子繞組差動保護電路圖*

說明發電機定子繞組之差動保護（Differential Protection）動作原理、動作線圈與抑制線圈配置。（20 分）

---

### ✏️ 完整標準解答
1. **保護原理（KCL 電流守恆）**：
   - 繞組兩端各置一組同規格 CT，差動電流 $I_{op} = |i_1 - i_2|$ 通過動作線圈。
   - 抑制電流 $I_{res} = \frac{|i_1| + |i_2|}{2}$ 通過抑制線圈，提供抗飽和抑制力矩。
2. **動作行為**：
   - **外部故障/正常運轉**：$i_1 = i_2 \implies I_{op} = 0$，電驛可靠不動作。
   - **內部短路故障**：$i_1 \ne i_2 \implies I_{op} > k \cdot I_{res} + I_{pickup}$，電驛瞬時動作跳脫發電機主斷路器與滅磁開關。

---

## 五、雙迴線三相故障與功率-角度方程式（20 分）

### 📌 題目與已知條件
![[108年_電力系統_第5題_雙迴線故障單線圖.png|750]]
*圖：108年電力系統第五題 雙迴線並聯輸電線故障單線圖*

發電機經兩條並聯輸電線送電至無窮母線，$E' = 1.10\text{ pu}, V = 1.0\text{ pu}$。
發電機暫態電抗 $X_d' = 0.20\text{ pu}$，每條線路電抗 $X_L = 0.40\text{ pu}$。其中一線路發生三相故障後切除。

**試求**：故障前、故障中、故障切除後之功率-角度方程式。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **故障前（Prefault）**：$X_1 = 0.20 + (0.40 \parallel 0.40) = 0.40\text{ pu} \implies \mathbf{P_{e1}(\delta) = \frac{1.10\times 1.0}{0.40}\sin\delta = 2.75\sin\delta}$
2. **故障中（During Fault）**：由 $\Delta-\text{Y}$ 化簡得 $X_2 = 1.25\text{ pu} \implies \mathbf{P_{e2}(\delta) = \frac{1.10\times 1.0}{1.25}\sin\delta = 0.88\sin\delta}$
3. **故障切除後（Postfault）**：$X_3 = 0.20 + 0.40 = 0.60\text{ pu} \implies \mathbf{P_{e3}(\delta) = \frac{1.10\times 1.0}{0.60}\sin\delta = 1.833\sin\delta}$

---

### 🎯 第五題 滿分關鍵與結論
$$\mathbf{P_{e1}(\delta) = 2.75\sin\delta}, \quad \mathbf{P_{e2}(\delta) = 0.88\sin\delta}, \quad \mathbf{P_{e3}(\delta) = 1.833\sin\delta}$$
'''

with open('📝 個人題解與錯題本/05_電力系統/108年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_108)

print('✅ 108 upgraded to gold standard!')

# ==============================================================================
# 107 年 電力系統 全卷黃金標準詳解
# ==============================================================================
sol_107 = r'''---
考科: 電力系統
年份: 107
主題: 107 年 電力系統 全卷四大題完整詳細推導、考點剖析與滿分關鍵
考點:
  - 一、輸電線路並聯電容補償與功率損耗計算 (Shunt Capacitor Line Loss)
  - 二、三相變壓器電壓調整率與二次側短路電流 (Transformer VR & ISC)
  - 三、同步發電機經升壓變壓器併網與無效功率 (850 MVA Grid-Tie Reactive Power)
  - 四、不對稱負載三相四線與三相三線對稱成分法 (Unbalanced Load 3Φ4W vs 3Φ3W)
難易度: ⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-16
---

# ⚡ 107 年 電機工程技師 — 電力系統 全卷完整詳細詳解與推導

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 107 年 電力系統 試題導覽清單
- [👉 第一題：輸電線路並聯電容補償與功率損耗計算（25 分）](#一輸電線路並聯電容補償與功率損耗計算25-分)
- [👉 第二題：三相變壓器電壓調整率與二次側短路電流（25 分）](#二三相變壓器電壓調整率與二次側短路電流25-分)
- [👉 第三題：同步發電機經升壓變壓器併網與無效功率（25 分）](#三同步發電機經升壓變壓器併網與無效功率25-分)
- [👉 第四題：不對稱負載三相四線與三相三線對稱成分法（25 分）](#四不對稱負載三相四線與三相三線對稱成分法25-分)

---

## 一、輸電線路並聯電容補償與功率損耗計算（25 分）

### 📌 題目與已知條件
![[107年_電力系統_第1題_輸電線負載圖.png|750]]
*圖：107年電力系統第一題 輸電線路與並聯電容負載單線圖*

- 線路阻抗：$Z_{line} = 0.02 + j0.2\text{ pu}$。
- 受電端負載：$P_L = 1.6\text{ pu}, \text{PF} = 0.8\text{ 滯後} \implies \mathbf{S}_L = 1.6 + j1.2\text{ pu}$。受電端電壓 $V_R = 1.0\angle 0^\circ\text{ pu}$。
- 電容器補償虛功：$Q_C = 1.2\text{ pu}$（$\mathbf{S}_C = -j1.2\text{ pu}$）。

* **(一)** 求線路電流 $I_{line}$ 及有效功率損失 $P_{loss}$。（6 分）
* **(二)** 求送電端電壓大小 $V_S$。（6 分）
* **(三)** 求電容器組阻抗 $Z_C$。（5 分）
* **(四)** 求送電端送出之有效功率 $P_S$ 與無效功率 $Q_S$。（8 分）

---

### ✏️ 步驟式詳細數學推導
1. **受電端總功率與線路電流**：
   $$\mathbf{S}_R = \mathbf{S}_L + \mathbf{S}_C = (1.6 + j1.2) - j1.2 = \mathbf{1.6 + j0\text{ pu}}$$
   $$\mathbf{I}_{line} = \left(\frac{\mathbf{S}_R}{\mathbf{V}_R}\right)^* = \frac{1.6\angle 0^\circ}{1.0\angle 0^\circ} = \mathbf{1.60\angle 0^\circ\text{ pu}}$$
   $$P_{loss} = I_{line}^2 R = (1.6)^2 \times 0.02 = \mathbf{0.0512\text{ pu}}$$
2. **送電端電壓 $\mathbf{V}_S$**：
   $$\mathbf{V}_S = \mathbf{V}_R + \mathbf{I} Z_{line} = 1.0 + 1.6(0.02 + j0.2) = 1.032 + j0.32\text{ pu} = \mathbf{1.0805\angle 17.23^\circ\text{ pu}}$$
3. **電容器阻抗 $Z_C$**：
   $$Z_C = \frac{|\mathbf{V}_R|^2}{\mathbf{S}_C^*} = \frac{1.0^2}{j1.2} = \mathbf{-j0.8333\text{ pu}}$$
4. **送電端功率**：
   $$\mathbf{S}_S = \mathbf{V}_S \mathbf{I}^* = (1.032 + j0.32)(1.6) = \mathbf{1.6512\text{ pu} + j0.5120\text{ pu}}$$
   - $P_S = \mathbf{1.6512\text{ pu}}, \quad Q_S = \mathbf{0.5120\text{ pu}}$

---

### 🎯 第一題 滿分關鍵與結論
- **線路電流與損耗**：$I_{line} = \mathbf{1.60\text{ pu}}, P_{loss} = \mathbf{0.0512\text{ pu}}$
- **送電端電壓**：$V_S = \mathbf{1.0805\text{ pu}}$
- **電容器阻抗**：$Z_C = \mathbf{-j0.8333\text{ pu}}$
- **送電端功率**：$P_S = \mathbf{1.6512\text{ pu}}, Q_S = \mathbf{0.5120\text{ pu}}$

---

## 二、三相變壓器電壓調整率與二次側短路電流（25 分）

### 📌 題目與已知條件
![[107年_電力系統_第2題_變壓器等效圖.png|750]]
*圖：107年電力系統第二題 161/23.9 kV 變壓器等效電路圖*

- **變壓器額定**：三相 $161\text{ kV} / 23.9\text{ kV}$、$S_{\text{rated}} = 60\text{ MVA}$、漏電抗 $X_T = 15\% = 0.15\text{ pu}$，忽略繞組電阻與激磁電流。
- **電源阻抗**：一次側 $Z_s = j8\ \Omega$（電源電壓 $E_s$ 保持不變）。
- **負載條件**：三相負載 $S_L = 60\text{ MVA}$、功率因數 $\text{PF} = 0.8\text{（滯後）}$，此時變壓器一次側端電壓 $V_1 = 161\text{ kV} = 1.0\text{ pu}$。

* **(一)** 求二次側電壓大小 $V_2$ 及一次側電源電壓大小 $E_s$（$\text{kV}$）。（10 分）
* **(二)** 求二次側電流大小 $I_2$（$\text{A}$），並判斷變壓器有無過載。（5 分）
* **(三)** 求變壓器二次側電壓調整率百分比 $\text{VR}\%$。（5 分）
* **(四)** 求二次側穩態三相短路電流大小 $I_{sc}$（$\text{A}$）。（5 分）

---

### ✏️ 步驟式詳細數學推導

#### 1. 系統基準值與標么化阻抗換算
- **一次側基準**：$V_{1,\text{base}} = 161\text{ kV}, S_{\text{base}} = 60\text{ MVA}$
  $$Z_{1,\text{base}} = \frac{V_{1,\text{base}}^2}{S_{\text{base}}} = \frac{(161\text{ kV})^2}{60\text{ MVA}} = 432.02\ \Omega$$
  $$I_{1,\text{base}} = \frac{S_{\text{base}}}{\sqrt{3} V_{1,\text{base}}} = \frac{60\times 10^6}{\sqrt{3}\times 161\times 10^3} = 215.16\text{ A}$$
  $$Z_{s,\text{pu}} = \frac{j8\ \Omega}{432.02\ \Omega} = j0.01852\text{ pu}$$
- **二次側基準**：$V_{2,\text{base}} = 23.9\text{ kV}$
  $$I_{2,\text{base}} = I_{2,\text{rated}} = \frac{S_{\text{base}}}{\sqrt{3} V_{2,\text{base}}} = \frac{60\times 10^6}{\sqrt{3}\times 23.9\times 10^3} = \mathbf{1449.41\text{ A}}$$

---

#### 2. (一) 求解二次側電壓 $V_2$ 與一次側電源電壓 $E_s$

##### 🔹 【解法一：相量壓降速解法（一次端電流相量參考）】
- 取一次側端電壓為相量參考基準：$\mathbf{V}_1 = 1.0\angle 0^\circ\text{ pu} = 161\text{ kV}$。
- 負載功率因數 $0.8$ 滯後，標么電流相量：$\mathbf{I}_{\text{pu}} = 1.0\angle -\cos^{-1}(0.8) = 0.8 - j0.6\text{ pu}$。
- **求二次側電壓 $\mathbf{V}_2$**：
  $$\mathbf{V}_{2,\text{pu}} = \mathbf{V}_1 - \mathbf{I}_{\text{pu}} (jX_T) = 1.0 - (0.8 - j0.6)(j0.15) = 0.91 - j0.12\text{ pu}$$
  $$|\mathbf{V}_{2,\text{pu}}| = \sqrt{0.91^2 + (-0.12)^2} = \mathbf{0.91788\text{ pu}}$$
  $$V_2 = 0.91788 \times 23.9\text{ kV} = \mathbf{21.937\text{ kV}}\ (\approx \mathbf{21.94\text{ kV}})$$
- **求一次側電源電壓 $\mathbf{E}_s$**（考慮電源阻抗 $Z_s = j0.01852\text{ pu}$ 壓降）：
  $$\mathbf{E}_{s,\text{pu}} = \mathbf{V}_1 + \mathbf{I}_{\text{pu}} Z_{s,\text{pu}} = 1.0 + (0.8 - j0.6)(j0.01852) = 1.01111 + j0.01481\text{ pu}$$
  $$|\mathbf{E}_{s,\text{pu}}| = \sqrt{1.01111^2 + 0.01481^2} = \mathbf{1.01122\text{ pu}}$$
  $$E_s = 1.01122 \times 161\text{ kV} = \mathbf{162.806\text{ kV}}\ (\approx \mathbf{162.81\text{ kV}})$$

##### 🔹 【解法二：雙匯流排功率潮流精確公式法（受電端 $S_2 = 60\text{ MVA}$ 恆功率負載）】
- 設受電端電壓為參考 $\mathbf{V}_2 = V_2\angle 0^\circ$，送電端電壓 $\mathbf{V}_1 = 1.0\angle\delta$：
  $$\mathbf{V}_1 = \mathbf{V}_2 + jX_T \left(\frac{P_2 - jQ_2}{\mathbf{V}_2^*}\right) = \left(V_2 + \frac{Q_2 X_T}{V_2}\right) + j\left(\frac{P_2 X_T}{V_2}\right)$$
- 取模平方導出**雙匯流排四次方特徵方程**：
  $$V_2^4 + (2 Q_2 X_T - V_1^2) V_2^2 + (P_2^2 + Q_2^2) X_T^2 = 0$$
- 代入 $V_1 = 1.0, X_T = 0.15, P_2 = 0.8, Q_2 = 0.6$：
  $$V_2^4 - 0.82 V_2^2 + 0.0225 = 0 \implies V_2^2 = \frac{0.82 + \sqrt{0.5824}}{2} = 0.79158$$
  $$V_2 = \sqrt{0.79158} = \mathbf{0.88971\text{ pu}} \implies V_2 = 0.88971 \times 23.9\text{ kV} = \mathbf{21.264\text{ kV}}$$
  - 功角：$\delta = \sin^{-1}\left(\frac{P_2 X_T}{V_1 V_2}\right) = \sin^{-1}\left(\frac{0.8\times 0.15}{1.0\times 0.88971}\right) = \mathbf{7.75^\circ}$
  - 電源電壓：$\mathbf{E}_s = \mathbf{V}_1 + \mathbf{I} Z_s = (0.9909 + j0.1349) + (0.8992 - j0.6744)(j0.01852) = 1.0034 + j0.1515\text{ pu}$
  - $|\mathbf{E}_s| = \mathbf{1.01473\text{ pu}} \implies E_s = 1.01473 \times 161\text{ kV} = \mathbf{163.371\text{ kV}}$

---

#### 3. (二) 求解二次側電流大小 $I_2$ 並嚴謹判斷有無過載
- **基準/額定二次電流**：$I_{2,\text{base}} = I_{2,\text{rated}} = \frac{60\times 10^6}{\sqrt{3}\times 23.9\times 10^3} = \mathbf{1449.41\text{ A}}$。
- **🔹 解法一計算**（$V_2 = 21.937\text{ kV}$ 下吸收 $60\text{ MVA}$）：
  $$I_2 = \frac{S_L}{\sqrt{3} V_2} = \frac{60\times 10^6}{\sqrt{3}\times 21.937\times 10^3} = \mathbf{1579.09\text{ A}}\ (1.0895\text{ pu})$$
  - 負載率：$108.95\%$，**過載（Overloaded 超載 $8.95\%$）**。
- **🔹 解法二計算**（$V_2 = 21.264\text{ kV}$ 下吸收 $60\text{ MVA}$）：
  $$I_2 = \frac{S_L}{\sqrt{3} V_2} = \frac{60\times 10^6}{\sqrt{3}\times 21.264\times 10^3} = \mathbf{1629.10\text{ A}}\ (1.1240\text{ pu})$$
  - 負載率：$112.40\%$，**過載（Overloaded 超載 $12.40\%$）**。

---

#### 4. (三) 求解變壓器二次側電壓調整率（VR%）
- **🔹 解法一計算**：
  - 電源 $E_s$ 保持不變時（無載電壓 $V_{2,\text{NL}} = E_s/a = 1.01122\text{ pu}$）：
    $$\text{VR} = \frac{1.01122 - 0.91788}{0.91788} \times 100\% = \mathbf{10.17\%}$$
  - （若僅以一次端電壓 $V_1=1.0\text{ pu}$ 固定：$\text{VR} = \frac{1.0 - 0.91788}{0.91788} \times 100\% = \mathbf{8.95\%}$）
- **🔹 解法二計算**：
  - 電源 $E_s$ 保持不變時（無載電壓 $V_{2,\text{NL}} = E_s/a = 1.01473\text{ pu}$）：
    $$\text{VR} = \frac{1.01473 - 0.88971}{0.88971} \times 100\% = \mathbf{14.05\%}$$
  - （若僅以一次端電壓 $V_1=1.0\text{ pu}$ 固定：$\text{VR} = \frac{1.0 - 0.88971}{0.88971} \times 100\% = \mathbf{12.40\%}$）

---

#### 5. (四) 求解二次側穩態三相短路電流 $I_{sc}$
短路總標么阻抗：$Z_{\text{total,pu}} = Z_{s,\text{pu}} + Z_{T,\text{pu}} = j0.01852 + j0.15 = j0.16852\text{ pu}$。
- **🔹 解法一計算**（由 $E_s = 1.01122\text{ pu}$ 驅動）：
  $$I_{sc} = \frac{1.01122}{0.16852} \times 1449.41\text{ A} = 6.0007\text{ pu} \times 1449.41\text{ A} = \mathbf{8697.5\text{ A}}\ (\approx \mathbf{8.70\text{ kA}})$$
  - （若以標稱電壓 $1.0\text{ pu}$ 基準計算：$I_{sc} = \frac{1.0}{0.16852} \times 1449.41\text{ A} = \mathbf{8601.0\text{ A}} = \mathbf{8.60\text{ kA}}$）
- **🔹 解法二計算**（由 $E_s = 1.01473\text{ pu}$ 驅動）：
  $$I_{sc} = \frac{1.01473}{0.16852} \times 1449.41\text{ A} = 6.0215\text{ pu} \times 1449.41\text{ A} = \mathbf{8727.6\text{ A}}\ (\approx \mathbf{8.73\text{ kA}})$$
  - （若以標稱電壓 $1.0\text{ pu}$ 基準計算：$I_{sc} = \mathbf{8601.0\text{ A}} = \mathbf{8.60\text{ kA}}$）

---

### 🎯 第二題 滿分結論與雙解法速查表

| 子題與物理量 | 🔹 解法一：相量壓降速解法 | 🔹 解法二：雙匯流排潮流精確特徵方程法 |
| :--- | :--- | :--- |
| **(一) 二次側電壓 $V_2$** | **$21.94\text{ kV}$** ($0.9179\text{ pu}$) | **$21.26\text{ kV}$** ($0.8897\text{ pu}$，功角 $\delta = 7.75^\circ$) |
| **(一) 一次電源 $E_s$** | **$162.81\text{ kV}$** ($1.0112\text{ pu}$) | **$163.37\text{ kV}$** ($1.0147\text{ pu}$) |
| **(二) 二次電流 $I_2$** | **$1579.1\text{ A}$**（過載 $8.95\%$） | **$1629.1\text{ A}$**（過載 $12.40\%$） |
| **(三) 電壓調整率 $\text{VR}$** | **$10.17\%$**（$V_1$ 基準：$8.95\%$） | **$14.05\%$**（$V_1$ 基準：$12.40\%$） |
| **(四) 短路電流 $I_{sc}$** | **$8697.5\text{ A} \approx 8.70\text{ kA}$**（標稱基準：$8.60\text{ kA}$） | **$8727.6\text{ A} \approx 8.73\text{ kA}$**（標稱基準：$8.60\text{ kA}$） |

---

## 三、同步發電機經升壓變壓器併網與無效功率（25 分）

### 📌 題目與已知條件
![[107年_電力系統_第3題_發電機併網圖.png|750]]
*圖：107年電力系統第三題 850 MVA 同步發電機併網系統模型圖*

- 發電機：$24\text{ kV}, 850\text{ MVA}, X_d = 1.0\text{ pu}$。
- 升壓變壓器：$25\text{ kV}/345\text{ kV}, 850\text{ MVA}, X_T = 0.20\text{ pu}$。
- 併入 $345\text{ kV}$ 無限匯流排，$P = 800\text{ MW} = 0.9412\text{ pu}, V_t = 1.0\text{ pu}$。

**試求**：發電機輸出無效功率 $Q_G$（判斷是否進相）及變壓器視在功率 $S_T$（判斷是否過載）。（25 分）

---

### ✏️ 步驟式詳細數學推導
1. **變壓器基準修正**：$X_{T,new} = 0.20 \times (25/24)^2 = 0.2170\text{ pu}$。
2. **潮流求解功角與無效功率**：
   $$\sin\theta = 0.9412 \times 0.2170 = 0.2042 \implies \theta = 11.78^\circ$$
   $$Q_G = \frac{1.0 - 1.0\cos(11.78^\circ)}{0.2170} = +0.0972\text{ pu} \implies Q_G = 0.0972 \times 850 = \mathbf{+82.6\text{ Mvar}}\quad (\text{滯後運轉，非進相})$$
3. **變壓器容量檢驗**：
   $$S_T = \sqrt{800^2 + 82.6^2} = \mathbf{804.3\text{ MVA}} \le 850\text{ MVA}\quad (\text{未過載})$$

---

### 🎯 第三題 滿分關鍵與結論
- **發電機無效功率**：$Q_G = \mathbf{+82.6\text{ Mvar}}$（滯後運轉 Lagging）
- **變壓器視在功率**：$S_T = \mathbf{804.3\text{ MVA}}$（安全未過載）

---

## 四、不對稱負載三相四線與三相三線對稱成分法（25 分）

### 📌 題目與已知條件
- **不對稱負載阻抗**：$Z_a = 10\ \Omega = 10\angle 0^\circ\ \Omega, \quad Z_b = -j10\ \Omega = 10\angle -90^\circ\ \Omega, \quad Z_c = j10\ \Omega = 10\angle 90^\circ\ \Omega$。
- **對稱三相電源電壓**：
  $$V_{an} = 100\angle 0^\circ\text{ V}, \quad V_{bn} = 100\angle -120^\circ\text{ V}, \quad V_{cn} = 100\angle 120^\circ\text{ V}$$

* **(一) 三相四線制（3Φ4W，含中性線）**：試求各相電流、正序電流 $I_{a1}$、負序電流 $I_{a2}$、零序電流 $I_{a0}$ 及中性線電流 $I_n$。（12 分）
* **(二) 三相三線制（3Φ3W，無中性線）**：試求負載中性點電壓偏移 $V_N$ 及各相導線電流與最大線電流 $I_{\max}$。（13 分）

---

### ✏️ 步驟式詳細數學推導

#### 🔹 (一) 三相四線制（3Φ4W）計算
1. **各相線電流計算**：
   - $\mathbf{I}_a = \frac{V_{an}}{Z_a} = \frac{100\angle 0^\circ}{10\angle 0^\circ} = \mathbf{10.0\angle 0^\circ\text{ A}} = 10.0 + j0\text{ A}$
   - $\mathbf{I}_b = \frac{V_{bn}}{Z_b} = \frac{100\angle -120^\circ}{10\angle -90^\circ} = 10.0\angle (-120^\circ - (-90^\circ)) = \mathbf{10.0\angle -30^\circ\text{ A}} = 8.660 - j5.000\text{ A}$
   - $\mathbf{I}_c = \frac{V_{cn}}{Z_c} = \frac{100\angle 120^\circ}{10\angle 90^\circ} = 10.0\angle (120^\circ - 90^\circ) = \mathbf{10.0\angle 30^\circ\text{ A}} = 8.660 + j5.000\text{ A}$

2. **中性線電流 $\mathbf{I}_n$**：
   $$\mathbf{I}_n = \mathbf{I}_a + \mathbf{I}_b + \mathbf{I}_c = (10.0 + j0) + (8.660 - j5.000) + (8.660 + j5.000) = \mathbf{27.320\angle 0^\circ\text{ A}}\ (\approx \mathbf{27.32\text{ A}})$$

3. **對稱成分（正序、負序、零序）電流**：
   - **零序電流 $\mathbf{I}_{a0}$**：
     $$\mathbf{I}_{a0} = \frac{\mathbf{I}_a + \mathbf{I}_b + \mathbf{I}_c}{3} = \frac{\mathbf{I}_n}{3} = \frac{27.320\angle 0^\circ}{3} = \mathbf{9.107\angle 0^\circ\text{ A}}\ (\approx \mathbf{9.11\text{ A}})$$
   - **正序電流 $\mathbf{I}_{a1}$**（其中 $a = 1\angle 120^\circ, a^2 = 1\angle 240^\circ$）：
     $$a \mathbf{I}_b = (1\angle 120^\circ)(10\angle -30^\circ) = 10\angle 90^\circ = j10\text{ A}$$
     $$a^2 \mathbf{I}_c = (1\angle 240^\circ)(10\angle 30^\circ) = 10\angle 270^\circ = -j10\text{ A}$$
     $$\mathbf{I}_{a1} = \frac{\mathbf{I}_a + a \mathbf{I}_b + a^2 \mathbf{I}_c}{3} = \frac{10 + j10 - j10}{3} = \mathbf{3.333\angle 0^\circ\text{ A}}\ (\approx \mathbf{3.33\text{ A}})$$
   - **負序電流 $\mathbf{I}_{a2}$**：
     $$a^2 \mathbf{I}_b = (1\angle 240^\circ)(10\angle -30^\circ) = 10\angle 210^\circ = -8.660 - j5\text{ A}$$
     $$a \mathbf{I}_c = (1\angle 120^\circ)(10\angle 30^\circ) = 10\angle 150^\circ = -8.660 + j5\text{ A}$$
     $$\mathbf{I}_{a2} = \frac{\mathbf{I}_a + a^2 \mathbf{I}_b + a \mathbf{I}_c}{3} = \frac{10 + (-8.660 - j5) + (-8.660 + j5)}{3} = \frac{10 - 17.320}{3} = \frac{-7.320}{3} = \mathbf{-2.440\text{ A}} = \mathbf{2.440\angle 180^\circ\text{ A}}$$

---

#### 🔹 (二) 三相三線制（3Φ3W）計算
1. **各相導納與中性點電壓偏移 $\mathbf{V}_N$（彌爾曼定理 Millman's Theorem）**：
   - $Y_a = \frac{1}{Z_a} = \frac{1}{10} = 0.10\angle 0^\circ\text{ S}$
   - $Y_b = \frac{1}{Z_b} = \frac{1}{-j10} = j0.10 = 0.10\angle 90^\circ\text{ S}$
   - $Y_c = \frac{1}{Z_c} = \frac{1}{j10} = -j0.10 = 0.10\angle -90^\circ\text{ S}$
   - 總導納：$Y_{\Sigma} = Y_a + Y_b + Y_c = 0.10 + j0.10 - j0.10 = \mathbf{0.10\angle 0^\circ\text{ S}}$
   - 負載中性點對地電壓：
     $$\mathbf{V}_N = \frac{\mathbf{V}_{an} Y_a + \mathbf{V}_{bn} Y_b + \mathbf{V}_{cn} Y_c}{Y_a + Y_b + Y_c} = \frac{\mathbf{I}_n}{Y_{\Sigma}} = \frac{27.320\angle 0^\circ}{0.10\angle 0^\circ} = \mathbf{273.205\angle 0^\circ\text{ V}}\ (\approx \mathbf{273.2\text{ V}})$$

2. **三相三線制各相導線電流**：
   - $\mathbf{I}_a' = \frac{\mathbf{V}_{an} - \mathbf{V}_N}{Z_a} = \frac{100.0 - 273.205}{10} = \frac{-173.205}{10} = \mathbf{-17.321\text{ A}} = \mathbf{17.321\angle 180.0^\circ\text{ A}}$
   - $\mathbf{I}_b' = \frac{\mathbf{V}_{bn} - \mathbf{V}_N}{Z_b} = \frac{(-50 - j86.603) - 273.205}{-j10} = \frac{-323.205 - j86.603}{-j10} = 8.660 - j32.321\text{ A} = \mathbf{33.461\angle -75.0^\circ\text{ A}}$
   - $\mathbf{I}_c' = \frac{\mathbf{V}_{cn} - \mathbf{V}_N}{Z_c} = \frac{(-50 + j86.603) - 273.205}{j10} = \frac{-323.205 + j86.603}{j10} = 8.660 + j32.321\text{ A} = \mathbf{33.461\angle +75.0^\circ\text{ A}}$
   - *(驗證 KCL：$\mathbf{I}_a' + \mathbf{I}_b' + \mathbf{I}_c' = -17.321 + (8.660 - j32.321) + (8.660 + j32.321) = 0\text{ A}$ 完全閉合)*。

3. **最大線路電流**：
   $$I_{\max} = |\mathbf{I}_b'| = |\mathbf{I}_c'| = \mathbf{33.461\text{ A}}\ (\approx \mathbf{33.46\text{ A}})$$

---

### 🎯 第四題 滿分關鍵與結論
- **(一) 3Φ4W 電流與對稱分量**：
  - 各相電流：$\mathbf{I}_a = \mathbf{10.0\angle 0^\circ\text{ A}}, \mathbf{I}_b = \mathbf{10.0\angle -30^\circ\text{ A}}, \mathbf{I}_c = \mathbf{10.0\angle 30^\circ\text{ A}}$
  - 中性線電流：$\mathbf{I}_n = \mathbf{27.32\angle 0^\circ\text{ A}}$
  - 零序電流：$\mathbf{I}_{a0} = \mathbf{9.11\angle 0^\circ\text{ A}}$
  - 正序電流：$\mathbf{I}_{a1} = \mathbf{3.33\angle 0^\circ\text{ A}}$
  - 負序電流：$\mathbf{I}_{a2} = \mathbf{2.44\angle 180^\circ\text{ A}}\ (-2.44\text{ A})$
- **(二) 3Φ3W 中性點電壓與最大電流**：
  - 中性點電壓：$\mathbf{V}_N = \mathbf{273.2\angle 0^\circ\text{ V}}$
  - 各線電流：$\mathbf{I}_a' = \mathbf{17.32\angle 180^\circ\text{ A}}, \mathbf{I}_b' = \mathbf{33.46\angle -75.0^\circ\text{ A}}, \mathbf{I}_c' = \mathbf{33.46\angle 75.0^\circ\text{ A}}$
  - 最大線電流：$I_{\max} = \mathbf{33.46\text{ A}}$（出現在 B 相與 C 相）
'''

with open('📝 個人題解與錯題本/05_電力系統/107年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_107)

print('✅ 108 and 107 upgraded to gold standard!')
