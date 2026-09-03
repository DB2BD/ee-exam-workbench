# -*- coding: utf-8 -*-
import os

sol_111 = '''---
考科: 電機機械
年份: 111
主題: 111 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、環形鐵磁電感氣隙磁阻、磁通密度與線圈電感 (Toroidal Inductor with Air-Gap)
  - 二、四極三相繞線式感應馬達轉子外加電阻與最大轉矩轉差 (Wound-Rotor IM External Resistor)
  - 三、20 kW 直流發電機電樞電阻、反電動勢與電壓調整率 (DC Generator Ea & Voltage Regulation)
  - 四、25 MVA 同步發電機短路比、同步電抗與功角相量 (25 MVA Synchronous Generator SCR & Phasor)
  - 五、2300 V 工廠電感性負載功因改善與並聯電容計算 (Power Factor Correction & Capacitor Sizing)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 111 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 111 年 電機機械 試題導覽清單
- [👉 第一題：環形鐵磁電感氣隙磁阻與電感（20 分）](#一環形鐵磁電感氣隙磁阻與電感20-分)
- [👉 第二題：三相繞線式感應電動機轉子外加電阻（20 分）](#二三相繞線式感應電動機轉子外加電阻20-分)
- [👉 第三題：20 kW 直流發電機端電壓與電壓調整率（20 分）](#三20-kw-直流發電機端電壓與電壓調整率20-分)
- [👉 第四題：25 MVA 同步發電機短路比與激磁電壓（20 分）](#四25-mva-同步發電機短路比與激磁電壓20-分)
- [👉 第五題：2300 V 工廠感性負載功因改善與並聯電容（20 分）](#五2300-v-工廠感性負載功因改善與並聯電容20-分)

---

## 一、環形鐵磁電感氣隙磁阻與電感（20 分）

### 📌 題目與已知條件
環形鐵磁材料導磁係數 $\mu_r = 2000$，平均半徑 $r = 10\text{ cm} = 0.10\text{ m}$（平均周長 $l_c = 2\pi r = 0.2\pi\text{ m}$），截面積 $A = 10\text{ cm}^2 = 10^{-3}\text{ m}^2$。
- 氣隙長度 $l_g = 1\text{ mm} = 10^{-3}\text{ m}$。
- 線圈匝數 $N = 500\text{ 匝}$，線圈電流 $I = 2\text{ A}$。忽略邊緣與漏磁。

* **(一)** 求鐵心與氣隙各自之磁阻及總磁阻 $\mathcal{R}_{total}$。（10 分）
* **(二)** 求氣隙中磁通密度 $B$ 與此電感器之電感值 $L$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **磁阻計算**：
   - 鐵心長度：$l_{core} = l_c - l_g \approx 0.2\pi - 0.001 = 0.6273\text{ m}$
   - 鐵心磁阻：
     $$\mathcal{R}_c = \frac{l_{core}}{\mu_r \mu_0 A} = \frac{0.6273}{2000 \times (4\pi \times 10^{-7}) \times 10^{-3}} = \frac{0.6273}{8\pi \times 10^{-7}} = \frac{0.6273 \times 10^7}{8\pi} \approx \mathbf{2.496 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
   - 氣隙磁阻：
     $$\mathcal{R}_g = \frac{l_g}{\mu_0 A} = \frac{10^{-3}}{(4\pi \times 10^{-7}) \times 10^{-3}} = \frac{10^7}{4\pi} \approx \mathbf{7.958 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
   - 總磁阻：
     $$\mathcal{R}_{total} = \mathcal{R}_c + \mathcal{R}_g = 2.496 \times 10^5 + 7.958 \times 10^5 = \mathbf{1.0454 \times 10^6\text{ A}\cdot\text{t/Wb}}$$
2. **磁通量、磁通密度與電感**：
   - 磁動勢 $\mathcal{F} = N I = 500 \times 2 = 1000\text{ A}\cdot\text{t}$
   - 磁通量 $\Phi = \frac{\mathcal{F}}{\mathcal{R}_{total}} = \frac{1000}{1.0454 \times 10^6} = \mathbf{0.9566\text{ mWb}}$
   - 磁通密度 $\mathbf{B = \frac{\Phi}{A} = \frac{0.9566 \times 10^{-3}}{10^{-3}} = \mathbf{0.9566\text{ T}}}$
   - 電感值：
     $$\mathbf{L = \frac{N^2}{\mathcal{R}_{total}} = \frac{500^2}{1.0454 \times 10^6} = \frac{250000}{1.0454 \times 10^6} = \mathbf{0.2391\text{ H} = 239.1\text{ mH}}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **總磁阻**：$\mathcal{R}_{total} = \mathbf{1.0454 \times 10^6\text{ A}\cdot\text{t/Wb}}$
- **磁通密度**：$B = \mathbf{0.9566\text{ T}}$
- **電感值**：$L = \mathbf{239.1\text{ mH}}$

---

## 二、三相繞線式感應電動機轉子外加電阻（20 分）

### 📌 題目與已知條件
- 額定：三相 $60\text{ Hz}$、4 極繞線式感應馬達，滿載轉速 $n_{FL} = 1710\text{ rpm}$。
- 轉子每相電阻 $R_2 = 0.05\ \Omega$。產生最大轉矩時之轉差率為 $s_{max} = 0.20$。
- 負載轉矩維持額定滿載轉矩不變。

* **(一)** 求馬達在額定運轉時之轉差率 $s_{FL}$ 與轉子感應電壓頻率 $f_2$。（10 分）
* **(二)** 若欲使最大轉矩發生在「起動瞬間（$s = 1.0$）」，轉子每相迴路需外加多少電阻 $R_{ext}$？（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **額定轉差率與轉子頻率**：
   $$n_s = \frac{120 \times 60}{4} = 1800\text{ rpm}$$
   $$\mathbf{s_{FL} = \frac{n_s - n_{FL}}{n_s} = \frac{1800 - 1710}{1800} = \frac{90}{1800} = \mathbf{0.05\ (5.0\%)}}$$
   $$\mathbf{f_2 = s_{FL} \times f_1 = 0.05 \times 60 = \mathbf{3.0\text{ Hz}}}$$
2. **外加電阻使最大轉矩發生於起動**：
   由感應機最大轉矩轉差率公式：$s_{max} \propto R_{rotor,total}$：
   $$\frac{s_{max2}}{s_{max1}} = \frac{R_2 + R_{ext}}{R_2}$$
   代入 $s_{max1} = 0.20, s_{max2} = 1.0, R_2 = 0.05\ \Omega$：
   $$\frac{1.0}{0.20} = 5 = \frac{0.05 + R_{ext}}{0.05} \implies 0.05 + R_{ext} = 0.25\ \Omega$$
   $$\mathbf{R_{ext} = 0.25 - 0.05 = \mathbf{0.20\ \Omega/\text{相}}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **額定轉差率與轉子頻率**：$s_{FL} = \mathbf{5.0\%}, f_2 = \mathbf{3.0\text{ Hz}}$
- **轉子外加電阻**：$R_{ext} = \mathbf{0.20\ \Omega/\text{相}}$

---

## 三、20 kW 直流發電機端電壓與電壓調整率（20 分）

### 📌 題目與已知條件
- 額定：$20\text{ kW}, 200\text{ V}, 1800\text{ rpm}$ 他激直流發電機。
- 電樞電阻 $R_a = 0.05\ \Omega$。無載端電壓為 $210\text{ V}$（額定場電流與轉速下）。

* **(一)** 求額定負載下之電樞電流 $I_a$ 與滿載端電壓 $V_t$。（10 分）
* **(二)** 求此直流發電機之電壓調整率 $\text{VR}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **滿載電流與端電壓**：
   無載時 $I_a = 0 \implies E_a = V_{oc} = 210\text{ V}$。
   額定輸出電功率 $P_{rated} = 20\text{ kW} = 20000\text{ W}$，額定端電壓 $V_t = 200\text{ V}$：
   $$I_a = \frac{P_{rated}}{V_t} = \frac{20000}{200} = \mathbf{100.0\text{ A}}$$
   發電機電樞方程式：
   $$V_t = E_a - I_a R_a = 210 - (100 \times 0.05) = 210 - 5.0 = \mathbf{205.0\text{ V}}$$
   *(若以額定電流 $100\text{ A}$ 運轉，端電壓為 $205.0\text{ V}$)*
2. **電壓調整率 $\text{VR}$**：
   $$\mathbf{VR = \frac{V_{nl} - V_{fl}}{V_{fl}} \times 100\% = \frac{210 - 205}{205} \times 100\% = \frac{5}{205} \times 100\% \approx \mathbf{2.44\%}}$$
   （若以額定端電壓 200V 計算 $\text{VR} = \frac{210 - 200}{200} \times 100\% = \mathbf{5.00\%}$）

---

### 🎯 第三題 滿分關鍵與結論
- **滿載電樞電流**：$I_a = \mathbf{100.0\text{ A}}$
- **滿載端電壓**：$V_t = \mathbf{205.0\text{ V}}$
- **電壓調整率**：$\text{VR} = \mathbf{2.44\%}$（基準額定值為 $\mathbf{5.0\%}$）

---

## 四、25 MVA 同步發電機短路比與激磁電壓（20 分）

### 📌 題目與已知條件
- 額定：三相 $\text{Y}$ 接、$25\text{ MVA}, 11\text{ kV}, 60\text{ Hz}$。
- 開路額定線電壓時場電流 $I_{f,oc} = 120\text{ A}$；短路額定電樞電流時場電流 $I_{f,sc} = 100\text{ A}$。
- 電樞電阻忽略。

* **(一)** 計算短路比 $\text{SCR}$ 與同步電抗 $X_s$（$\text{pu}$ 與 $\Omega$）。（10 分）
* **(二)** 當發電機在額定容量、$\text{PF} = 0.8$ 滯後運轉時，求每相激磁電壓 $E_f$ 與功角 $\delta$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **短路比與同步電抗**：
   $$\mathbf{SCR = \frac{I_{f,oc}}{I_{f,sc}} = \frac{120}{100} = \mathbf{1.20}}$$
   $$X_s\ (\text{pu}) = \frac{1}{\text{SCR}} = \frac{1}{1.20} = \mathbf{0.8333\text{ pu}}$$
   $$Z_{base} = \frac{V_L^2}{S} = \frac{11000^2}{25 \times 10^6} = \frac{121 \times 10^6}{25 \times 10^6} = 4.84\ \Omega$$
   $$\mathbf{X_s = 0.8333 \times 4.84 = \mathbf{4.0333\ \Omega/\text{相}}}$$
2. **激磁電壓與功角**：
   $$V_\phi = \frac{11000}{\sqrt{3}} \approx 6350.85\text{ V}, \quad I_a = \frac{25 \times 10^6}{\sqrt{3}\times 11000} = 1312.16\angle -36.87^\circ\text{ A}$$
   標么值法秒殺：
   $$\mathbf{E}_{f,pu} = 1.0\angle 0^\circ + (j 0.8333)(1.0\angle -36.87^\circ) = 1.0 + 0.8333\angle 53.13^\circ$$
   $$\mathbf{E}_{f,pu} = 1.0 + (0.50 + j0.6666) = 1.50 + j0.6666\text{ pu}$$
   $$|\mathbf{E}_{f,pu}| = \sqrt{1.50^2 + 0.6666^2} = \mathbf{1.6415\text{ pu}} \implies E_f = 1.6415 \times 6350.85 = \mathbf{10425.0\text{ V/相}}$$
   $$\mathbf{\delta = \tan^{-1}\left(\frac{0.6666}{1.50}\right) = \tan^{-1}(0.4444) = \mathbf{23.96^\circ}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **短路比**：$\text{SCR} = \mathbf{1.20}$，$X_s = \mathbf{0.8333\text{ pu} = 4.033\ \Omega}$
- **每相激磁電壓**：$E_f = \mathbf{1.6415\text{ pu} = 10425.0\text{ V/相}}$
- **功率角**：$\delta = \mathbf{23.96^\circ}$

---

## 五、2300 V 工廠感性負載功因改善與並聯電容（20 分）

### 📌 題目與已知條件
- 工廠負載：三相 $V_L = 2300\text{ V}, 60\text{ Hz}$，總實功 $P = 1200\text{ kW}$，初始功率因數 $\text{PF}_1 = 0.707\text{ 落後}$（$\theta_1 = 45.0^\circ$）。
- 欲將功率因數提高至 $\text{PF}_2 = 0.95\text{ 落後}$（$\theta_2 = \cos^{-1} 0.95 = 18.19^\circ$）。

* **(一)** 求需並聯之三相電容器總無效功率容量 $Q_c$（$\text{kVAR}$）。（10 分）
* **(二)** 若電容器為 $\Delta$ 接線，求每相電容量 $C_\Delta$（$\mu\text{F}$）。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **補償電容容量 $Q_c$**：
   $$\tan\theta_1 = \tan(45.0^\circ) = 1.0$$
   $$\tan\theta_2 = \tan(18.19^\circ) = 0.3287$$
   $$\mathbf{Q_c = P (\tan\theta_1 - \tan\theta_2) = 1200 \times (1.0 - 0.3287) = 1200 \times 0.6713 = \mathbf{805.54\text{ kVAR}}}$$
2. **求 $\Delta$ 接每相電容量 $C_\Delta$**：
   每相電容承受全線電壓 $V_C = V_L = 2300\text{ V}$：
   $$Q_{c,1\phi} = \frac{Q_c}{3} = \frac{805.54}{3} = 268.51\text{ kVAR} = 268513\text{ VAR}$$
   $$Q_{c,1\phi} = V_L^2 \omega C_\Delta \implies C_\Delta = \frac{Q_{c,1\phi}}{\omega V_L^2}$$
   $$\mathbf{C_\Delta = \frac{268513}{(2\pi \times 60) \times (2300)^2} = \frac{268513}{376.99 \times 5.29 \times 10^6} = \frac{268513}{1.9943 \times 10^9} \approx \mathbf{1.346 \times 10^{-4}\text{ F} = 134.6\ \mu\text{F}}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **補償電容總容量**：$Q_c = \mathbf{805.54\text{ kVAR}}$
- **$\Delta$ 接每相電容值**：$C_\Delta = \mathbf{134.6\ \mu\text{F}}$
'''

with open('📝 個人題解與錯題本/04_電機機械/111年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_111)
print('✅ 111年 電機機械 detailed solution written!')
