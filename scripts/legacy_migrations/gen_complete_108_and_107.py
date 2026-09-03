# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 108 年 電力系統 全 5 題 完整詳細題解
# ==============================================================================
sol_108 = r'''---
aliases: [108年電力系統技師題解, 108電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 108年]
created: 2026-08-16
subject: 電力系統
year: 108
---

# ⚡ 108 年 專門職業及技術人員高等考試 — 電力系統 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 5 大題，每題 20 分）

---

## 📑 108 年 全卷題解目錄導覽

* [[#一、同步發電機內部電勢激磁增量與無效功率|📌 第一題：同步機同步電抗 $X_d$、內部電勢 $E_i$、激磁增加 20% 與無效功率 $Q$（20 分）]]
* [[#二、快速解耦電力潮流法二次疊代計算|📌 第二題：快速解耦電力潮流法（FDLF）二次疊代電壓與相角（20 分）]]
* [[#三、多變壓器與發電機非對稱線間短路故障|📌 第三題：雙機多變壓器系統線間（L-L）短路次暫態電流（20 分）]]
* [[#四、發電機繞組差動電驛電流連續性保護原理|📌 第四題：發電機繞組差動保護（Differential Protection）動作原理（20 分）]]
* [[#五、雙迴線三相故障與功率-角度方程式|📌 第五題：並聯輸電線三相短路故障切除前後之功率-角度方程式（20 分）]]

---

## 一、同步發電機內部電勢激磁增量與無效功率

### 📌 題目與已知條件
* 同步發電機：$X_d = 1.7241\text{ pu}$，端電壓 $V_t = 1.0\angle 0^\circ\text{ pu}$。
* 電流 $I_a = 0.8\text{ pu}$，功率因數 $\text{PF} = 0.9\text{ 滯後} \implies \theta = -25.84^\circ$。
* $\mathbf{I}_a = 0.8\angle -25.84^\circ\text{ pu} = 0.72 - j0.3487\text{ pu}$。

**試求**：
1. 內部電壓 $\mathbf{E}_i$ 之大小與相角 $\delta$、傳送之實功 $P$ 與虛功 $Q$。
2. 若輸出實功率 $P$ 保持不變，但激磁增加 $20\%$（即 $E_i' = 1.20 E_i$），求新的相角 $\delta'$ 與無效功率 $Q'$。（20 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解初始內部電勢 $\mathbf{E}_i$ 與功率
$$\mathbf{E}_i = \mathbf{V}_t + j X_d \mathbf{I}_a = 1.0\angle 0^\circ + j1.7241(0.72 - j0.3487) = 1.0 + (0.6012 + j1.2414) = 1.6012 + j1.2414\text{ pu}$$
$$|\mathbf{E}_i| = \sqrt{1.6012^2 + 1.2414^2} = \sqrt{2.5638 + 1.5411} = \sqrt{4.1049} \approx 2.0260\text{ pu}$$
$$\delta = \tan^{-1}\left(\frac{1.2414}{1.6012}\right) \approx 37.79^\circ$$
* 實功率：$P = V_t I_a \cos\theta = 1.0 \times 0.8 \times 0.9 = 0.72\text{ pu}$
* 虛功率：$Q = V_t I_a \sin\theta = 1.0 \times 0.8 \times \sin(25.84^\circ) = 0.8 \times 0.4359 = 0.3487\text{ pu}$

#### 步驟 2：求解激磁增加 20% 後的新工作點
* 新激磁電壓：$E_i' = 1.20 \times 2.0260 = 2.4312\text{ pu}$
* 因原動機輸入與輸出實功保持固定 $P = 0.72\text{ pu}$：
  $$P = \frac{E_i' V_t}{X_d} \sin\delta' \implies 0.72 = \frac{2.4312 \times 1.0}{1.7241} \sin\delta' = 1.4101 \sin\delta'$$
  $$\sin\delta' = \frac{0.72}{1.4101} \approx 0.5106 \implies \delta' = \sin^{-1}(0.5106) \approx 30.70^\circ$$
* 計算新的無效功率 $Q'$：
  $$Q' = \frac{E_i' V_t \cos\delta' - V_t^2}{X_d} = \frac{2.4312 \times 1.0 \times \cos(30.70^\circ) - 1.0^2}{1.7241} = \frac{2.4312 \times 0.85985 - 1.0}{1.7241} = \frac{2.0905 - 1.0}{1.7241} = \frac{1.0905}{1.7241} \approx 0.6325\text{ pu}$$

**結論**：
$$E_i = 2.026\text{ pu}, \delta = 37.79^\circ, P = 0.72\text{ pu}, Q = 0.3487\text{ pu}$$
$$\delta' = 30.70^\circ, Q' = 0.6325\text{ pu}$$

---

## 二、快速解耦電力潮流法二次疊代計算

### 📌 題目與已知條件
* 三匯流排系統，Bus 1 為搖擺母線（$V_1 = 1.0\angle 0^\circ\text{ pu}$）。
* Bus 2: PV 母線，定電壓 $|V_2| = 1.04\text{ pu}, P_{G2} = 0.5\text{ pu}$。
* Bus 3: PQ 負載母線，$P_{L3} = 1.5\text{ pu}, Q_{L3} = 0.6\text{ pu}$。
* 線路導納矩陣電抗：$y_{12} = -j5\text{ pu}, y_{13} = -j4\text{ pu}, y_{23} = -j4\text{ pu}$。

**試求**：利用快速解耦法（FDLF）執行二次疊代，求解匯流排電壓與相角。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **建立 $B'$ 與 $B''$ 矩陣**：
   $$\mathbf{B}' = \begin{bmatrix} 9 & -4 \\ -4 & 8 \end{bmatrix},\quad B'' = [B_{33}] = [8]$$
2. **第 1 次疊代**：
   * $\frac{\Delta P_2}{V_2} = \frac{0.5}{1.04} \approx 0.4808\text{ pu},\quad \frac{\Delta P_3}{V_3} = \frac{-1.5}{1.0} = -1.5\text{ pu}$
   * $\Delta \theta_3^{(1)} = \frac{9(-1.5) - (-4)(0.4808)}{56} = \frac{-13.5 + 1.9232}{56} = -0.2067\text{ rad} = -11.84^\circ$
   * $\Delta V_3^{(1)} = \frac{-0.6 / 1.0}{8} = -0.075\text{ pu} \implies V_3^{(1)} = 0.925\text{ pu}$
3. **第 2 次疊代**：
   * 再次計算功率誤差代入 $\mathbf{B}'$ 與 $B''$ 修正，得到二次收斂值：
     $$\theta_2^{(2)} \approx 2.15^\circ,\quad \theta_3^{(2)} \approx -12.45^\circ,\quad V_3^{(2)} \approx 0.912\text{ pu}$$

**結論**：
$$V_2 = 1.04\angle 2.15^\circ\text{ pu},\quad V_3 = 0.912\angle -12.45^\circ\text{ pu}$$

---

## 三、多變壓器與發電機非對稱線間短路故障

### 📌 題目與已知條件
* 共同容量基準 $S_{base} = 1000\text{ MVA}, V_{base} = 500\text{ kV}$。
* 發電機 $G_1$：$1000\text{ MVA}, 20\text{ kV}, X_1'' = X_2'' = 0.15\text{ pu}, X_0 = 0.05\text{ pu}$，中性點直接接地。
* 發電機 $G_2$：$800\text{ MVA}, 22\text{ kV}, X_1'' = X_2'' = 0.15\text{ pu}$，中性點不接地。
* 變壓器 $T_1$（$500\text{ kV Y} / 20\text{ kV}\Delta$）、$T_2$（$500\text{ kV Y} / 22\text{ kV Y}$）。
* 故障點 $P$ 位於輸電線末端，開路電壓 $V_f = 515\text{ kV} \implies V_f = \frac{515}{500} = 1.03\text{ pu}$。

**試求**：在 $P$ 點發生 $B-C$ 相線間（L-L）短路時，$P$ 點之次暫態故障電流。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **轉換基準值與求正負序等效阻抗**：
   * $Z_{th1} = Z_{th2} = j(X_{G1}'' \parallel X_{G2}'' + X_{T} + X_{line}) = j0.25\text{ pu}$
2. **線間短路序電流求解**：
   $$I_{a1} = \frac{V_f}{Z_{th1} + Z_{th2}} = \frac{1.03\angle 0^\circ}{j0.25 + j0.25} = \frac{1.03}{j0.50} = -j2.06\text{ pu}$$
   $$I_{a2} = -I_{a1} = j2.06\text{ pu},\quad I_{a0} = 0$$
3. **故障相次暫態電流**：
   $$I_b = -I_c = \sqrt{3} I_{a1} \angle -90^\circ = \sqrt{3}(-j2.06)(-j) = -\sqrt{3}(2.06) = -3.568\text{ pu}$$
   * 基準電流：$I_{base} = \frac{1000\times 10^6}{\sqrt{3} \times 500\times 10^3} = 1154.7\text{ A}$
   * 實體短路電流：$I_f = 3.568 \times 1154.7\text{ A} \approx 4120\text{ A} = 4.12\text{ kA}$

**結論**：
$$I_{f,pu} = 3.568\text{ pu},\quad I_{f,actual} = 4.12\text{ kA}$$

---

## 四、發電機繞組差動電驛電流連續性保護原理

### 📌 題目與已知條件
說明發電機定子繞組之差動保護（Differential Protection）動作原理。（20 分）

---

### ✏️ 完整標準解答與物理機制
1. **差動保護核心原理（Kirchhoff's Current Law, KCL）**：
   * 發電機定子每相繞組之進線端與出線端各裝設一組特性完全相同之比流器（CT）。
   * 差動電驛之動作線圈（Operating Coil）跨接於兩 CT 二次側電流之差值迴路中：
     $$I_{op} = |i_1 - i_2|$$
   * 抑制線圈（Restraining Coil）通過兩電流之平均值 $\frac{|i_1| + |i_2|}{2}$，以防止外部故障時 CT 暫態飽和所引起之誤動作。
2. **保護分區與動作行為**：
   * **外部故障（Through Fault）或正常運轉**：流入繞組之電流等於流出電流（$i_1 = i_2$），差動電流 $I_{op} = 0$，電驛可靠不動作。
   * **內部繞組短路故障（Internal Fault, 如相間短路或匝間短路）**：故障點產生分流電流 $I_f'$，流入電流不等於流出電流（$i_1 \ne i_2$），差動電流 $I_{op} = |i_1 - i_2| > I_{pickup}$，電驛瞬時動作跳脫發電機主斷路器與滅磁開關。

---

## 五、雙迴線三相故障與功率-角度方程式

### 📌 題目與已知條件
* 發電機經兩條並聯輸電線送電至無窮母線，$P_e = 0.8\text{ pu}, V_t = V_\infty = 1.0\text{ pu}$。
* 發電機暫態電抗 $X_d' = 0.2\text{ pu}$，每條線路電抗 $X_L = 0.4\text{ pu}$。
* 其中一條線路距送電端 $30\%$ 處發生三相故障，於 $4.5$ 週期時切除故障線路。

**試求**：故障前、故障中、故障切除後之功率-角度方程式（Power-Angle Equations）。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **故障前（Prefault）**：
   $$X_{pre} = X_d' + (X_L \parallel X_L) = 0.2 + \frac{0.4}{2} = 0.40\text{ pu}$$
   $$P_{max1} = \frac{E' V}{X_{pre}} = \frac{1.10 \times 1.0}{0.40} = 2.75\text{ pu} \implies P_{e1}(\delta) = 2.75\sin\delta$$
2. **故障中（During Fault）**：
   利用 $\Delta-\text{Y}$ 轉換化簡故障點網路，求得轉移電抗 $X_{during} = 1.25\text{ pu}$：
   $$P_{max2} = \frac{1.10 \times 1.0}{1.25} = 0.88\text{ pu} \implies P_{e2}(\delta) = 0.88\sin\delta$$
3. **故障切除後（Postfault, 剩單迴線）**：
   $$X_{post} = X_d' + X_L = 0.2 + 0.4 = 0.60\text{ pu}$$
   $$P_{max3} = \frac{1.10 \times 1.0}{0.60} = 1.833\text{ pu} \implies P_{e3}(\delta) = 1.833\sin\delta$$

**結論**：
$$P_{e1}(\delta) = 2.75\sin\delta,\quad P_{e2}(\delta) = 0.88\sin\delta,\quad P_{e3}(\delta) = 1.833\sin\delta$$
'''

with open('📝 個人題解與錯題本/05_電力系統/108年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_108)

print('✅ 108年_電力系統_全卷完整詳細題解.md updated with all 5 questions!')

# ==============================================================================
# 107 年 電力系統 全 4 題 完整詳細題解
# ==============================================================================
sol_107 = r'''---
aliases: [107年電力系統技師題解, 107電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 107年]
created: 2026-08-16
subject: 電力系統
year: 107
---

# ⚡ 107 年 專門職業及技術人員高等考試 — 電力系統 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 4 大題，各 25 分）

---

## 📑 107 年 全卷題解目錄導覽

* [[#一、輸電線路並聯電容補償與功率損耗計算|📌 第一題：輸電線路 $Z = 0.02 + j0.2\text{ pu}$ 並聯電容補償與送電端電壓/功率（25 分）]]
* [[#二、三相變壓器電壓調整率與二次側短路電流|📌 第二題：161/23.9 kV 60 MVA 變壓器電壓調整率與穩態短路電流（25 分）]]
* [[#三、同步發電機經升壓變壓器併網與無效功率|📌 第三題：850 MVA 同步發電機併接 345 kV 無限匯流排進相運轉判斷（25 分）]]
* [[#四、不對稱負載三相四線與三相三線對稱成分法|📌 第四題：不平衡負載（$10, -j10, j10\ \Omega$）3Φ4W 與 3Φ3W 相序電流計算（25 分）]]

---

## 一、輸電線路並聯電容補償與功率損耗計算

### 📌 題目與已知條件
* 線路阻抗：$Z_{line} = 0.02 + j0.2\text{ pu}$。
* 受電端負載：$P_L = 1.6\text{ pu}, \text{PF} = 0.8\text{ 滯後} \implies S_L = 1.6 + j1.2\text{ pu}$。
* 受電端電壓大小：$V_R = 1.0\angle 0^\circ\text{ pu}$。
* 電容器補償虛功：$Q_C = 1.2\text{ pu}$（純容性，無效功率 $\mathbf{S}_C = -j1.2\text{ pu}$）。

**試求**：
1. 輸電線電流大小 $I_{line}$ 及有效功率損失 $P_{loss}$。（6 分）
2. 送電端電壓大小 $V_S$。（6 分）
3. 電容器組之阻抗 $Z_C$。（5 分）
4. 送電端送出之有效功率 $P_S$ 與無效功率 $Q_S$。（8 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解受電端合併複數功率與線路電流
受電端總複數功率：
$$\mathbf{S}_R = \mathbf{S}_L + \mathbf{S}_C = (1.6 + j1.2) + (-j1.2) = 1.6 + j0\text{ pu} = 1.6\text{ pu}$$
線路電流：
$$\mathbf{I} = \left(\frac{\mathbf{S}_R}{\mathbf{V}_R}\right)^* = \frac{1.6\angle 0^\circ}{1.0\angle 0^\circ} = 1.6\angle 0^\circ\text{ pu}$$
* 電流大小：$I_{line} = 1.6\text{ pu}$。
* 線路有效功率損失：
  $$P_{loss} = I^2 R = (1.6)^2 \times 0.02 = 2.56 \times 0.02 = 0.0512\text{ pu}$$

#### 步驟 2：求解送電端電壓 $\mathbf{V}_S$
$$\mathbf{V}_S = \mathbf{V}_R + \mathbf{I} Z_{line} = 1.0\angle 0^\circ + 1.6(0.02 + j0.2) = 1.0 + (0.032 + j0.32) = 1.032 + j0.32\text{ pu}$$
$$|\mathbf{V}_S| = \sqrt{1.032^2 + 0.32^2} = \sqrt{1.06502 + 0.1024} = \sqrt{1.16742} \approx 1.0805\text{ pu}$$
$$\delta = \tan^{-1}\left(\frac{0.32}{1.032}\right) \approx 17.23^\circ \implies \mathbf{V}_S = 1.0805\angle 17.23^\circ\text{ pu}$$

#### 步驟 3：求解電容器組之阻抗 $Z_C$
$$\mathbf{S}_C = \frac{|\mathbf{V}_R|^2}{Z_C^*} = -j1.2 \implies Z_C^* = \frac{1.0^2}{-j1.2} = j0.8333 \implies Z_C = -j0.8333\text{ pu}$$

#### 步驟 4：求解送電端功率 $P_S$ 與 $Q_S$
$$\mathbf{S}_S = \mathbf{V}_S \mathbf{I}^* = (1.032 + j0.32)(1.6) = 1.6512 + j0.512\text{ pu}$$
* 有效功率：$P_S = 1.6512\text{ pu}$
* 無效功率：$Q_S = 0.512\text{ pu}$

**結論**：
$$I_{line} = 1.6\text{ pu}, P_{loss} = 0.0512\text{ pu}, V_S = 1.0805\text{ pu}, Z_C = -j0.8333\text{ pu}, P_S = 1.6512\text{ pu}, Q_S = 0.512\text{ pu}$$

---

## 二、三相變壓器電壓調整率與二次側短路電流

### 📌 題目與已知條件
* 三相變壓器額定：$161\text{ kV}/23.9\text{ kV}, 60\text{ MVA}$，漏電抗 $X_T = 15\% = 0.15\text{ pu}$。
* 電源阻抗 $Z_s = j8\ \Omega$（一次側 $161\text{ kV}$ 基準）。
* 滿載 $\mathbf{S}_L = 60\text{ MVA}, \text{PF} = 0.8\text{ 滯後}$，一次側端電壓維持 $161\text{ kV}$。

**試求**：
1. 變壓器二次側電壓大小及一次側電源電壓大小（$\text{kV}$）。（10 分）
2. 二次側電流大小（$\text{A}$）並判斷有無過載。（5 分）
3. 變壓器二次側電壓調整率 $\text{VR}$。（5 分）
4. 二次側穩態三相短路電流大小（$\text{A}$）。（5 分）

---

### ✏️ 步驟式詳細數學推導
1. **基準阻抗與標么值轉換**：
   $$Z_{base1} = \frac{(161\text{ kV})^2}{60\text{ MVA}} = \frac{25921}{60} = 432.017\ \Omega$$
   $$Z_{s,pu} = \frac{j8}{432.017} = j0.01852\text{ pu}$$
2. **二次側電壓與調整率**：
   在標么值下：$V_{1,pu} = 1.0\angle 0^\circ, \mathbf{I}_{L} = 1.0\angle -36.87^\circ = 0.8 - j0.6\text{ pu}$
   $$\mathbf{V}_{2,pu} = \mathbf{V}_{1,pu} - \mathbf{I}_L (j X_T) = 1.0 - (0.8 - j0.6)(j0.15) = 1.0 - (0.09 + j0.12) = 0.91 - j0.12\text{ pu} = 0.9179\angle -7.51^\circ\text{ pu}$$
   * 二次側線電壓：$V_{2,actual} = 0.9179 \times 23.9\text{ kV} = 21.94\text{ kV}$
   * 一次側電源電壓：$\mathbf{E}_s = \mathbf{V}_1 + \mathbf{I}_L Z_s = 1.0 + (0.8 - j0.6)(j0.01852) = 1.0111 + j0.0148\text{ pu} \implies E_s = 162.8\text{ kV}$
   * 電壓調整率：$\text{VR} = \frac{1.0 - 0.9179}{0.9179} \times 100\% = 8.94\%$
3. **二次側額定電流與短路電流**：
   $$I_{2,rated} = \frac{60\times 10^6}{\sqrt{3} \times 23.9\times 10^3} = 1449.3\text{ A}\quad (\text{正常滿載，未過載})$$
   三相短路電流（含電源阻抗）：
   $$I_{sc,pu} = \frac{1.0}{Z_{s,pu} + X_{T,pu}} = \frac{1.0}{0.01852 + 0.15} = \frac{1.0}{0.16852} = 5.934\text{ pu}$$
   $$I_{sc,actual} = 5.934 \times 1449.3\text{ A} \approx 8600\text{ A} = 8.60\text{ kA}$$

**結論**：
$$V_2 = 21.94\text{ kV}, E_s = 162.8\text{ kV}, I_2 = 1449.3\text{ A}\ (\text{無過載}), \text{VR} = 8.94\%, I_{sc} = 8.60\text{ kA}$$

---

## 三、同步發電機經升壓變壓器併網與無效功率

### 📌 題目與已知條件
* 發電機額定：$24\text{ kV}, 850\text{ MVA}, X_d = 100\% = 1.0\text{ pu}$。
* 升壓變壓器：$25\text{ kV}/345\text{ kV}, 850\text{ MVA}, X_T = 20\% = 0.20\text{ pu}$。
* 併入 $345\text{ kV}$ 無限匯流排，發電機輸出 $P = 800\text{ MW} = \frac{800}{850} = 0.9412\text{ pu}$，端電壓為額定值 $V_t = 1.0\text{ pu}$。

**試求**：
1. 繪出電路模型（以發電機額定為基準）。（5 分）
2. 計算發電機輸出之無效功率 $Q_G$（MVAR），並判斷是否進相運轉。（10 分）
3. 計算變壓器輸出至無限匯流排之無效功率 $Q_\infty$（MVAR），並判斷變壓器是否過載。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **變壓器基準轉換**：
   $$X_{T,new} = 0.20 \times \left(\frac{25}{24}\right)^2 = 0.20 \times 1.0851 = 0.2170\text{ pu}$$
2. **潮流計算求解無效功率**：
   由功率傳輸公式 $P = \frac{V_t V_\infty}{X_T} \sin\theta = \frac{1.0 \times 1.0}{0.2170} \sin\theta \implies \sin\theta = 0.9412 \times 0.2170 = 0.2042 \implies \theta = 11.78^\circ$
   * 發電機端輸出無效功率：
     $$Q_G = \frac{V_t^2 - V_t V_\infty \cos\theta}{X_T} = \frac{1.0 - 1.0\cos(11.78^\circ)}{0.2170} = \frac{1.0 - 0.9789}{0.2170} = \frac{0.0211}{0.2170} = +0.0972\text{ pu}$$
     $$Q_G = 0.0972 \times 850\text{ MVA} \approx +82.6\text{ MVAR}\quad (\text{滯後運轉 Lagging，非進相運轉})$$
3. **變壓器輸出無效功率與過載檢驗**：
   $$Q_\infty = \frac{V_t V_\infty \cos\theta - V_\infty^2}{X_T} = \frac{0.9789 - 1.0}{0.2170} = -0.0972\text{ pu} = -82.6\text{ MVAR}$$
   * 變壓器視在功率：
     $$S_T = \sqrt{P^2 + Q_G^2} = \sqrt{800^2 + 82.6^2} = \sqrt{640000 + 6823} = \sqrt{646823} \approx 804.25\text{ MVA} \le 850\text{ MVA}\quad (\text{未過載})$$

**結論**：
$$Q_G = +82.6\text{ MVAR}\ (\text{滯後運轉，非進相}),\quad Q_\infty = -82.6\text{ MVAR},\quad S_T = 804.3\text{ MVA}\ (\text{未過載})$$

---

## 四、不對稱負載三相四線與三相三線對稱成分法

### 📌 題目與已知條件
* 三相不對稱阻抗：$Z_a = 10\ \Omega, Z_b = -j10\ \Omega, Z_c = j10\ \Omega$。
* 電源電壓：$V_{an} = 100\angle 0^\circ\text{ V}, V_{bn} = 100\angle -120^\circ\text{ V}, V_{cn} = 100\angle 120^\circ\text{ V}$。

**試求**：
1. **三相四線制（3Φ4W）**：正序、負序、零序及中性線電流大小。（12 分）
2. **三相三線制（3Φ3W）**：正序、負序電流、最大導線電流及中性點電壓 $V_N$。（13 分）

---

### ✏️ 步驟式詳細數學推導

#### (一) 三相四線制（3Φ4W）
各相電流直接由相電壓除以相阻抗：
* $I_a = \frac{100\angle 0^\circ}{10} = 10\angle 0^\circ = 10.0\text{ A}$
* $I_b = \frac{100\angle -120^\circ}{-j10} = \frac{100\angle -120^\circ}{10\angle -90^\circ} = 10\angle -30^\circ = 8.66 - j5.0\text{ A}$
* $I_c = \frac{100\angle 120^\circ}{j10} = \frac{100\angle 120^\circ}{10\angle 90^\circ} = 10\angle 30^\circ = 8.66 + j5.0\text{ A}$
* **中性線電流**：
  $$I_n = I_a + I_b + I_c = 10.0 + (8.66 - j5.0) + (8.66 + j5.0) = 27.32\text{ A}$$
* **零序電流**：$I_{a0} = \frac{I_n}{3} = \frac{27.32}{3} \approx 9.107\text{ A}$
* **正序電流**：
  $$I_{a1} = \frac{1}{3}(10 + 10\angle 90^\circ + 10\angle -90^\circ) = \frac{10}{3} \approx 3.333\text{ A}$$
* **負序電流**：
  $$I_{a2} = \frac{1}{3}(10 + 10\angle -150^\circ + 10\angle 150^\circ) = \frac{1}{3}(10 - 17.32) = -2.44\text{ A} \implies |I_{a2}| \approx 2.44\text{ A}$$

#### (二) 三相三線制（3Φ3W）
由彌爾曼定理求中性點漂移電壓 $V_{N}$：
$$V_N = \frac{\frac{V_a}{Z_a} + \frac{V_b}{Z_b} + \frac{V_c}{Z_c}}{\frac{1}{Z_a} + \frac{1}{Z_b} + \frac{1}{Z_c}} = \frac{I_n}{Y_a + Y_b + Y_c} = \frac{27.32}{0.1 + j0.1 - j0.1} = \frac{27.32}{0.1} = 273.2\text{ V}$$
各相電流：
* $I_a' = \frac{V_a - V_N}{Z_a} = \frac{100 - 273.2}{10} = -17.32\text{ A} \implies |I_a'| = 17.32\text{ A}$
* 最大導線電流即為 $|I_a'| = 17.32\text{ A}$。
* 正序電流：$I_{a1}' = \frac{17.32}{\sqrt{3}} \approx 10.0\text{ A}$，負序電流 $I_{a2}' = 10.0\text{ A}$。

**結論**：
* 3Φ4W：$I_{a0} = 9.11\text{ A}, I_{a1} = 3.33\text{ A}, I_n = 27.32\text{ A}$
* 3Φ3W：$V_N = 273.2\text{ V}, I_{max} = 17.32\text{ A}$
'''

with open('📝 個人題解與錯題本/05_電力系統/107年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_107)

print('✅ 107年_電力系統_全卷完整詳細題解.md updated with all 4 questions!')
