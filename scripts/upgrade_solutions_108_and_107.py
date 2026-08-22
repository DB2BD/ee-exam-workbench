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

- 變壓器：$161\text{ kV}/23.9\text{ kV}, 60\text{ MVA}, X_T = 15\% = 0.15\text{ pu}$。
- 電源阻抗：$Z_s = j8\ \Omega$（一次側基準）。
- 滿載：$\mathbf{S}_L = 60\text{ MVA}, \text{PF} = 0.8\text{ 滯後}$。

* **(一)** 求二次側電壓 $V_2$ 及一次側電源電壓 $E_s$（$\text{kV}$）。（10 分）
* **(二)** 求二次側滿載電流 $I_2$ 並判斷有無過載。（5 分）
* **(三)** 求變壓器二次側電壓調整率 $\text{VR}$。（5 分）
* **(四)** 求二次側穩態三相短路電流 $I_{sc}$（$\text{kA}$）。（5 分）

---

### ✏️ 步驟式詳細數學推導
1. **基準阻抗與標么化**：
   $$Z_{base1} = \frac{(161)^2}{60} = 432.02\ \Omega \implies Z_{s,pu} = \frac{j8}{432.02} = j0.01852\text{ pu}$$
   $$\mathbf{V}_{2,pu} = 1.0 - (0.8 - j0.6)(j0.15) = 0.91 - j0.12 = \mathbf{0.9179\angle -7.51^\circ\text{ pu}}$$
   $$V_2 = 0.9179 \times 23.9\text{ kV} = \mathbf{21.94\text{ kV}}$$
   $$\mathbf{E}_s = 1.0 + (0.8 - j0.6)(j0.01852) = 1.0111 + j0.0148\text{ pu} \implies E_s = 1.0112 \times 161\text{ kV} = \mathbf{162.8\text{ kV}}$$
2. **滿載電流**：
   $$I_2 = \frac{60\times 10^6}{\sqrt{3}\times 23.9\times 10^3} = \mathbf{1449.3\text{ A}}\quad (\text{未過載})$$
3. **電壓調整率**：
   $$\text{VR} = \frac{1.0 - 0.9179}{0.9179} \times 100\% = \mathbf{8.94\%}$$
4. **短路電流**：
   $$I_{sc,pu} = \frac{1.0}{0.01852 + 0.15} = \frac{1.0}{0.16852} = 5.934\text{ pu} \implies I_{sc} = 5.934 \times 1.4493\text{ kA} = \mathbf{8.60\text{ kA}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **二次側電壓**：$V_2 = \mathbf{21.94\text{ kV}}, E_s = \mathbf{162.8\text{ kV}}$
- **滿載電流**：$I_2 = \mathbf{1449.3\text{ A}}$（無過載）
- **電壓調整率**：$\text{VR} = \mathbf{8.94\%}$
- **短路電流**：$I_{sc} = \mathbf{8.60\text{ kA}}$

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
- 阻抗：$Z_a = 10\ \Omega, Z_b = -j10\ \Omega, Z_c = j10\ \Omega$。
- 電壓：$V_{an} = 100\angle 0^\circ\text{ V}, V_{bn} = 100\angle -120^\circ\text{ V}, V_{cn} = 100\angle 120^\circ\text{ V}$。

* **(一) 三相四線制（3Φ4W）**：求正序、負序、零序及中性線電流。（12 分）
* **(二) 三相三線制（3Φ3W）**：求中性點電壓 $V_N$ 及最大導線電流。（13 分）

---

### ✏️ 步驟式詳細數學推導
1. **三相四線制**：
   - $I_a = 10\angle 0^\circ\text{ A}, I_b = 10\angle -30^\circ\text{ A}, I_c = 10\angle 30^\circ\text{ A}$
   - **中性線電流**：$I_n = 10 + 8.66 - j5 + 8.66 + j5 = \mathbf{27.32\text{ A}}$
   - **零序電流**：$I_{a0} = I_n / 3 = \mathbf{9.11\text{ A}}$
   - **正序電流**：$I_{a1} = \mathbf{3.33\text{ A}}$
2. **三相三線制**：
   - 彌爾曼定理：$V_N = \frac{I_n}{Y_a+Y_b+Y_c} = \frac{27.32}{0.10} = \mathbf{273.2\text{ V}}$
   - 最大相電流：$|I_a'| = \frac{|100 - 273.2|}{10} = \mathbf{17.32\text{ A}}$

---

### 🎯 第四題 滿分關鍵與結論
- **3Φ4W**：$I_n = \mathbf{27.32\text{ A}}, I_{a0} = \mathbf{9.11\text{ A}}, I_{a1} = \mathbf{3.33\text{ A}}$
- **3Φ3W**：$V_N = \mathbf{273.2\text{ V}}, I_{max} = \mathbf{17.32\text{ A}}$
'''

with open('📝 個人題解與錯題本/05_電力系統/107年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_107)

print('✅ 108 and 107 upgraded to gold standard!')
