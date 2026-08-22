# -*- coding: utf-8 -*-
import os

sol_109 = '''---
考科: 電機機械
年份: 109
主題: 109 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、雙繞組變壓器漏磁路磁阻、漏電感與激磁等效電路 (Transformer Leakage Reluctance & Inductance)
  - 二、25 kW 他激直流電動機電樞電壓調速與轉矩平衡 (Separately Excited DC Motor Speed Control)
  - 三、三相六極感應電動機功率流向圖與電磁轉矩計算 (Induction Motor Power Flow & Torque)
  - 四、凸極式同步發電機直軸/交軸雙反應理論與相量分析 (Salient Pole Xd & Xq Two-Reaction Theory)
  - 五、三相變壓器三次諧波抑制、感應機雙鼠籠與同步機阻尼繞組 (Core Concept QA)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 109 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 109 年 電機機械 試題導覽清單
- [👉 第一題：雙繞組變壓器漏磁阻與漏電感參數（20 分）](#一雙繞組變壓器漏磁阻與漏電感參數20-分)
- [👉 第二題：他激直流電動機電樞電壓速度控制（20 分）](#二他激直流電動機電樞電壓速度控制20-分)
- [👉 第三題：三相感應電動機功率流向與轉矩（20 分）](#三三相感應電動機功率流向與轉矩20-分)
- [👉 第四題：凸極式同步發電機雙反應理論相量圖（20 分）](#四凸極式同步發電機雙反應理論相量圖20-分)
- [👉 第五題：電機機械三大經典核心問答（20 分）](#五電機機械三大經典核心問答20-分)

---

## 一、雙繞組變壓器漏磁阻與漏電感參數（20 分）

### 📌 題目與已知條件
- 額定規格：$50\text{ kVA}, 2400\text{ V} / 240\text{ V}, 60\text{ Hz}$。
- 匝數：一次側 $N_P = 1000\text{ 匝}$，二次側 $N_S = 100\text{ 匝}$。
- 鐵心導磁係數 $\mu_c \to \infty$（主磁阻忽略），繞組電阻 $R_P = R_S = 0$。額定鐵損 $P_{core} = 500\text{ W}$。
- 漏磁路磁阻：一次側 $\mathcal{R}_{lP} = 4 \times 10^5\text{ A}\cdot\text{t/Wb}$，二次側 $\mathcal{R}_{lS} = 4 \times 10^3\text{ A}\cdot\text{t/Wb}$。

* **(一)** 求一次側漏電感 $L_{lP}$、二次側漏電感 $L_{lS}$ 與對應之感抗 $X_{lP}, X_{lS}$。（10 分）
* **(二)** 畫出等效至一次側之變壓器等效電路，並計算等效總阻抗與激磁電阻 $R_c$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **漏電感與漏電抗計算**：
   $$L_{lP} = \frac{N_P^2}{\mathcal{R}_{lP}} = \frac{1000^2}{4 \times 10^5} = \frac{10^6}{4 \times 10^5} = \mathbf{2.5\text{ H}}$$
   $$X_{lP} = \omega L_{lP} = (2\pi \times 60) \times 2.5 = 377 \times 2.5 = \mathbf{942.48\ \Omega}$$
   $$L_{lS} = \frac{N_S^2}{\mathcal{R}_{lS}} = \frac{100^2}{4 \times 10^3} = \frac{10^4}{4 \times 10^3} = \mathbf{2.5\text{ H}}$$
   $$X_{lS} = \omega L_{lS} = 377 \times 2.5 = \mathbf{942.48\ \Omega}$$
2. **反射至一次側等效電路**：
   匝數比 $a = \frac{N_P}{N_S} = \frac{1000}{100} = 10$。
   二次側漏抗反射至一次側：
   $$X_{lS}' = a^2 X_{lS} = 10^2 \times 942.48 = \mathbf{94248\ \Omega}$$
   一次側等效總漏抗：
   $$X_{eq1} = X_{lP} + X_{lS}' = 942.48 + 94248 = \mathbf{95190.5\ \Omega}$$
   激磁鐵損電阻（接於一次側額定電壓 $2400\text{ V}$）：
   $$\mathbf{R_c = \frac{V_P^2}{P_{core}} = \frac{2400^2}{500} = \frac{5760000}{500} = \mathbf{11520\ \Omega = 11.52\text{ k}\Omega}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **漏電感**：$L_{lP} = \mathbf{2.5\text{ H}}, L_{lS} = \mathbf{2.5\text{ H}}$
- **一次側總漏抗**：$X_{eq1} = \mathbf{95.19\text{ k}\Omega}$
- **激磁鐵損電阻**：$R_c = \mathbf{11.52\text{ k}\Omega}$

---

## 二、他激直流電動機電樞電壓速度控制（20 分）

### 📌 題目與已知條件
- 額定：$25\text{ kW}, 125\text{ V}, 1200\text{ rpm}$ 他激直流電動機，電樞電阻 $R_a = 0.04\ \Omega$。
- 負載轉矩與轉速成正比：$T_L \propto n$。磁場電流固定。

* **(一)** 額定滿載運轉時，求反電動勢 $E_a$ 與電磁轉矩 $T_{FL}$。（10 分）
* **(二)** 欲將轉速降至 $600\text{ rpm}$，求外加電樞端電壓 $V_t'$ 應調整為多少伏特？（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **額定狀態分析**：
   $$I_{a1} = \frac{P_{rated}}{V_t} = \frac{25000}{125} = \mathbf{200.0\text{ A}}$$
   $$E_{a1} = V_t - I_{a1} R_a = 125 - 200 \times 0.04 = 125 - 8.0 = \mathbf{117.0\text{ V}}$$
   $$\omega_{m1} = \frac{2\pi \times 1200}{60} = 40\pi \approx 125.66\text{ rad/s}$$
   $$\mathbf{T_{FL} = \frac{E_{a1} I_{a1}}{\omega_{m1}} = \frac{117.0 \times 200}{125.66} = \mathbf{186.21\text{ N}\cdot\text{m}}}$$
2. **降速至 $600\text{ rpm}$**：
   因磁通固定，$E_a \propto n \implies E_{a2} = E_{a1} \times \left(\frac{600}{1200}\right) = 117.0 \times 0.5 = \mathbf{58.5\text{ V}}$。
   因負載轉矩 $T_L \propto n \implies T_2 = 0.5 T_1$。
   因 $T \propto I_a \implies I_{a2} = 0.5 I_{a1} = 0.5 \times 200 = \mathbf{100.0\text{ A}}$。
   所需外加電樞端電壓：
   $$\mathbf{V_t' = E_{a2} + I_{a2} R_a = 58.5 + (100 \times 0.04) = 58.5 + 4.0 = \mathbf{62.5\text{ V}}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **額定反電動勢與轉矩**：$E_a = \mathbf{117.0\text{ V}}, T_{FL} = \mathbf{186.21\text{ N}\cdot\text{m}}$
- **新電樞端電壓**：$V_t' = \mathbf{62.5\text{ V}}$

---

## 三、三相感應電動機功率流向與轉矩（20 分）

### 📌 題目與已知條件
- 額定：三相 $220\text{ V}, 60\text{ Hz}, 6$ 極、$\text{Y}$ 接感應電動機，滿載輸入功率 $P_{in} = 15\text{ kW}$，定子銅損 $P_{cu1} = 600\text{ W}$，鐵損 $P_{core} = 400\text{ W}$。
- 滿載轉速 $n = 1140\text{ rpm}$，機械摩擦風阻損 $P_{rot} = 300\text{ W}$。

* **(一)** 計算氣隙功率 $P_{ag}$、轉子銅損 $P_{cu2}$ 與機電轉換功率 $P_{conv}$。（10 分）
* **(二)** 計算電動機軸端輸出功率 $P_{out}$、輸出電磁轉矩 $T_{ind}$ 與總操作效率 $\eta$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **同步轉速與轉差率**：
   $$n_s = \frac{120 \times 60}{6} = 1200\text{ rpm}$$
   $$\mathbf{s = \frac{1200 - 1140}{1200} = \frac{60}{1200} = \mathbf{0.05\ (5.0\%)}}$$
2. **功率流向推導**：
   - 氣隙功率：
     $$\mathbf{P_{ag} = P_{in} - P_{cu1} - P_{core} = 15000 - 600 - 400 = \mathbf{14000\text{ W} = 14.0\text{ kW}}}$$
   - 轉子銅損：
     $$\mathbf{P_{cu2} = s P_{ag} = 0.05 \times 14000 = \mathbf{700\text{ W}}}$$
   - 機電轉換功率：
     $$\mathbf{P_{conv} = (1 - s) P_{ag} = 0.95 \times 14000 = \mathbf{13300\text{ W} = 13.3\text{ kW}}}$$
   - 軸端淨輸出功率：
     $$\mathbf{P_{out} = P_{conv} - P_{rot} = 13300 - 300 = \mathbf{13000\text{ W} = 13.0\text{ kW}}}$$
3. **轉矩與總效率**：
   $$\omega_m = \frac{2\pi \times 1140}{60} = 119.38\text{ rad/s}$$
   $$\mathbf{T_{ind} = \frac{P_{conv}}{\omega_m} = \frac{13300}{119.38} = \mathbf{111.41\text{ N}\cdot\text{m}}}$$
   $$\mathbf{\eta = \frac{P_{out}}{P_{in}} \times 100\% = \frac{13000}{15000} \times 100\% = \mathbf{86.67\%}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **氣隙與轉換功率**：$P_{ag} = \mathbf{14.0\text{ kW}}, P_{cu2} = \mathbf{700\text{ W}}, P_{conv} = \mathbf{13.3\text{ kW}}$
- **軸輸出功率與轉矩**：$P_{out} = \mathbf{13.0\text{ kW}}, T_{ind} = \mathbf{111.41\text{ N}\cdot\text{m}}$
- **操作效率**：$\eta = \mathbf{86.67\%}$

---

## 四、凸極式同步發電機雙反應理論相量圖（20 分）

### 📌 題目與已知條件
一部三相 $2300\text{ V}, 60\text{ Hz}, 30$ 極凸極式同步發電機，每相直軸同步電抗 $X_d = 1.2\ \Omega$，交軸同步電抗 $X_q = 0.8\ \Omega$，電樞電阻忽略。額定滿載電流 $I_a = 400\text{ A}$，功率因數 $\text{PF} = 0.8\text{ 落後}$。

* **(一)** 畫出凸極同步發電機之相量圖，並求出功率角 $\delta$。（10 分）
* **(二)** 計算每相直軸電流 $I_d$、交軸電流 $I_q$ 與每相內生激磁電壓 $E_f$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **求解功率角 $\delta$**：
   $$V_\phi = \frac{2300}{\sqrt{3}} \approx 1327.91\text{ V}$$
   $$\tan\psi = \frac{V_\phi \sin\phi + I_a X_q}{V_\phi \cos\phi} = \frac{1327.91 \times 0.6 + 400 \times 0.8}{1327.91 \times 0.8} = \frac{796.75 + 320.0}{1062.33} = \frac{1116.75}{1062.33} = 1.0512$$
   $$\psi = \tan^{-1}(1.0512) = 46.43^\circ$$
   $$\mathbf{\delta = \psi - \phi = 46.43^\circ - 36.87^\circ = \mathbf{9.56^\circ}}$$
2. **求解 $I_d, I_q$ 與激磁電壓 $E_f$**：
   $$\mathbf{I_d = I_a \sin\psi = 400 \times \sin(46.43^\circ) = 400 \times 0.7245 = \mathbf{289.81\text{ A}}}$$
   $$\mathbf{I_q = I_a \cos\psi = 400 \times \cos(46.43^\circ) = 400 \times 0.6893 = \mathbf{275.70\text{ A}}}$$
   內生電壓幅值：
   $$\mathbf{E_f = V_\phi \cos\delta + I_d X_d = 1327.91 \times \cos(9.56^\circ) + 289.81 \times 1.2 = 1309.46 + 347.77 = \mathbf{1657.23\text{ V/相}}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **功角**：$\delta = \mathbf{9.56^\circ}$
- **直/交軸電流**：$I_d = \mathbf{289.81\text{ A}}, I_q = \mathbf{275.70\text{ A}}$
- **內生激磁電壓**：$E_f = \mathbf{1657.23\text{ V/相}}$（線電壓 $2870.4\text{ V}$）

---

## 五、電機機械三大經典核心問答（20 分）

* **(一) 變壓器 $\text{Y}-\text{Y}$ 接線為何通常加設第三繞組（$\Delta$ 繞組）？（7 分）**
  - **抑制三次諧波**：提供三次諧波激磁電流封閉環流通道，防止相電壓波形畸變與中性點電位漂移。
  - **提供廠用電與穩定中性點電壓**。

* **(二) 感應電動機雙鼠籠式（Double Cage）轉子之工作原理？（7 分）**
  - **起動時**：轉子頻率高（$60\text{ Hz}$），下層槽漏抗大，電流被擠至上層高電阻槽（集膚效應），產生**高起動轉矩、低起動電流**。
  - **運轉時**：轉差率小（$2\sim 3\text{ Hz}$），漏抗影響消失，電流均勻流入下層低電阻槽，維持**低銅損與高運轉效率**。

* **(三) 同步機轉子阻尼繞組（Damper Winding / Amortisseur）之兩大功能？（6 分）**
  - **抑制擺動（Hunting）**：當負載或電網擾動時，阻尼繞組感應電流產生非同步轉矩抑制轉子搖擺。
  - **作為非同步起動繞組**：使同步電動機在起動時能像感應馬達一樣自行加速至接近同步轉速。
'''

with open('📝 個人題解與錯題本/04_電機機械/109年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_109)
print('✅ 109年 電機機械 detailed solution written!')
