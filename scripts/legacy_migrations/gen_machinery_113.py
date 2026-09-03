# -*- coding: utf-8 -*-
import os

sol_113 = '''---
考科: 電機機械
年份: 113
主題: 113 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、單相變壓器實體磁路與等效電路電感參數公式 (Transformer Reluctance & Inductance Model)
  - 二、三相同步發電機短路比、同步電抗與勵磁電壓 (SCR, Synchronous Reactance & Ef)
  - 三、三相感應電動機戴維寧等效電路、轉矩與轉差率 (Induction Motor Thevenin & Torque-Speed)
  - 四、直流並激電動機轉速控制與電樞電阻調速 (Shunt DC Motor Speed Control & Ra)
  - 五、三相變壓器 Y-Δ 接線、短路阻抗與電壓調整率 (Three-Phase Y-Delta Transformer Regulation)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 113 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 113 年 電機機械 試題導覽清單
- [👉 第一題：單相變壓器實體磁路與等效電感模型（20 分）](#一單相變壓器實體磁路與等效電感模型20-分)
- [👉 第二題：三相同步發電機短路比與勵磁電壓（20 分）](#二三相同步發電機短路比與勵磁電壓20-分)
- [👉 第三題：三相感應電動機戴維寧轉矩與轉差率（20 分）](#三三相感應電動機戴維寧轉矩與轉差率20-分)
- [👉 第四題：直流並激電動機電樞電阻串聯調速（20 分）](#四直流並激電動機電樞電阻串聯調速20-分)
- [👉 第五題：三相變壓器 Y-Δ 短路阻抗與電壓調整率（20 分）](#五三相變壓器-y-δ-短路阻抗與電壓調整率20-分)

---

## 一、單相變壓器實體磁路與等效電感模型（20 分）

### 📌 題目與已知條件
一單相變壓器，一次側/二次側電壓、電流、匝數、漏磁通分別為 $V_1/V_2, I_1/I_2, N_1/N_2, \Phi_{l1}/\Phi_{l2}$，鐵心主磁通為 $\Phi_M$，鐵心主磁阻為 $\mathcal{R}_M$，一次側/二次側漏磁阻分別為 $\mathcal{R}_{l1}/\mathcal{R}_{l2}$。
* **(一)** 繪出此變壓器的磁路圖（含磁動勢 $\mathcal{F}$、磁阻 $\mathcal{R}$、磁通 $\Phi$）。（10 分）
* **(二)** 考量線圈銅損、鐵損後，畫出變壓器之等效電路，並列出等效電路中各電感公式（以匝數 $N$ 及磁阻 $\mathcal{R}$ 表示）。（10 分）

---

### 💡 核心考點與破題關鍵
1. **變壓器磁路分析**：
   - 一次側磁動勢 $\mathcal{F}_1 = N_1 I_1$，二次側磁動勢 $\mathcal{F}_2 = N_2 I_2$。
   - 總磁通分為：互感主磁通 $\Phi_M$（通過鐵心 $\mathcal{R}_M$）與各自的漏磁通 $\Phi_{l1}, \Phi_{l2}$（通過空氣漏磁路 $\mathcal{R}_{l1}, \mathcal{R}_{l2}$）。
2. **等效電感代數關係**：
   - 激磁/互感電感：$L_M = \frac{N_1^2}{\mathcal{R}_M}$
   - 一次側漏電感：$L_{l1} = \frac{N_1^2}{\mathcal{R}_{l1}}$
   - 二次側漏電感：$L_{l2} = \frac{N_2^2}{\mathcal{R}_{l2}}$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：繪製變壓器磁路模型
- **磁動勢源**：$\mathcal{F}_1 = N_1 I_1$（推動磁通）與 $\mathcal{F}_2 = N_2 I_2$（反向去磁）。
- **並聯磁路結構**：
  - 一次側漏磁迴路：$\Phi_{l1} = \frac{\mathcal{F}_1}{\mathcal{R}_{l1}}$
  - 主磁通迴路：$\Phi_M = \frac{\mathcal{F}_1 - \mathcal{F}_2}{\mathcal{R}_M} = \frac{N_1 I_1 - N_2 I_2}{\mathcal{R}_M}$
  - 二次側漏磁迴路：$\Phi_{l2} = \frac{\mathcal{F}_2}{\mathcal{R}_{l2}}$

#### 🔹 第 (二) 小題：等效電路與電感公式
1. **實體等效電路元件對應**：
   - $R_1, R_2$：一次/二次繞組電阻（代表線圈銅損 $I^2 R$）。
   - $R_c$：鐵損激磁電阻（代表渦流與磁滯損耗 $P_{core} = V_1^2 / R_c$）。
   - $X_{l1} = \omega L_{l1}$：一次側漏電抗，其中 $\mathbf{L_{l1} = \frac{N_1^2}{\mathcal{R}_{l1}}}$。
   - $X_{l2} = \omega L_{l2}$：二次側漏電抗，其中 $\mathbf{L_{l2} = \frac{N_2^2}{\mathcal{R}_{l2}}}$。
   - $X_m = \omega L_M$：激磁互感電抗，其中 $\mathbf{L_M = \frac{N_1^2}{\mathcal{R}_M}}$。
   - 理想變壓器：匝數比 $N_1 : N_2$。

---

### 🎯 第一題 滿分關鍵與結論
- **互感電感**：$L_M = \mathbf{\frac{N_1^2}{\mathcal{R}_M}}$
- **一次漏感**：$L_{l1} = \mathbf{\frac{N_1^2}{\mathcal{R}_{l1}}}$，**二次漏感**：$L_{l2} = \mathbf{\frac{N_2^2}{\mathcal{R}_{l2}}}$

---

## 二、三相同步發電機短路比與勵磁電壓（20 分）

### 📌 題目與已知條件
- 額定：三相 $\text{Y}$ 接、$600\text{ kVA}$、$4.2\text{ kV}$、$60\text{ Hz}$、1800 rpm、效率 $\eta = 0.90$。
- 運轉條件：在 $\text{PF} = 0.90\text{ 滯後}$ 滿載運轉。
- 開路與短路試驗數據：
  - 開路額定線電壓 $4.2\text{ kV}$ 時之場電流 $I_{f,oc} = 25\text{ A}$。
  - 短路額定電流 $I_{a,rated}$ 時之場電流 $I_{f,sc} = 20\text{ A}$。
- 電樞電阻 $R_a$ 忽略不計。

* **(一)** 求短路比（Short-Circuit Ratio, SCR）與不飽和同步電抗 $X_s$（$\Omega$ 與 $\text{pu}$）。（10 分）
* **(二)** 求滿載時之每相內生激磁電壓 $E_f$ 與電壓調整率 $\text{VR}$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **短路比（SCR）定義**：
   $$\text{SCR} = \frac{I_{f,oc}}{I_{f,sc}} = \frac{1}{X_{s,sat}\ (\text{pu})}$$
2. **同步電抗計算**：
   - 基準阻抗：$Z_{base} = \frac{V_{L,base}^2}{S_{3\phi,base}} = \frac{(4.2\times 10^3)^2}{600\times 10^3} = \frac{17.64\times 10^6}{600\times 10^3} = 29.4\ \Omega$
   - 標么值同步電抗：$X_s\ (\text{pu}) = \frac{1}{\text{SCR}} = \frac{I_{f,sc}}{I_{f,oc}}$
   - 歐姆值同步電抗：$X_s\ (\Omega) = X_s\ (\text{pu}) \times Z_{base}$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：求 SCR 與同步電抗 $X_s$
1. **短路比 SCR**：
   $$\mathbf{SCR = \frac{I_{f,oc}}{I_{f,sc}} = \frac{25\text{ A}}{20\text{ A}} = \mathbf{1.25}}$$
2. **同步電抗標么值與實際歐姆值**：
   $$X_s\ (\text{pu}) = \frac{1}{\text{SCR}} = \frac{1}{1.25} = \mathbf{0.80\text{ pu}}$$
   $$Z_{base} = \frac{V_L^2}{S} = \frac{4200^2}{600000} = 29.4\ \Omega$$
   $$\mathbf{X_s = 0.80 \times 29.4 = \mathbf{23.52\ \Omega/\text{相}}}$$

---

#### 🔹 第 (二) 小題：求激磁電壓 $E_f$ 與電壓調整率 $\text{VR}$
1. **相電壓與額定電流**：
   $$V_\phi = \frac{4200}{\sqrt{3}} \approx 2424.87\text{ V}, \quad I_a = \frac{600 \times 10^3}{\sqrt{3}\times 4200} = 82.4786\angle -25.84^\circ\text{ A}$$
2. **內生電壓相量 $\mathbf{E}_f$**：
   $$\mathbf{E}_f = V_\phi + j X_s \mathbf{I}_a = 2424.87 + j23.52 \times (82.4786\angle -25.84^\circ)$$
   $$j X_s \mathbf{I}_a = 23.52 \times 82.4786 \angle (90^\circ - 25.84^\circ) = 1939.90 \angle 64.16^\circ = 845.24 + j1745.91\text{ V}$$
   $$\mathbf{E}_f = (2424.87 + 845.24) + j1745.91 = 3270.11 + j1745.91\text{ V}$$
   $$|\mathbf{E}_f| = \sqrt{3270.11^2 + 1745.91^2} = \mathbf{3707.03\text{ V/相}}$$
   （線電壓形式為 $E_{f,L} = \sqrt{3} \times 3707.03 = \mathbf{6420.76\text{ V}}$，功角 $\delta = \tan^{-1}\frac{1745.91}{3270.11} = 28.10^\circ$）
3. **電壓調整率 $\text{VR}$**：
   $$\mathbf{VR = \frac{|\mathbf{E}_f| - V_\phi}{V_\phi} \times 100\% = \frac{3707.03 - 2424.87}{2424.87} \times 100\% = \mathbf{52.88\%}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **短路比**：$\text{SCR} = \mathbf{1.25}$
- **同步電抗**：$X_s = \mathbf{0.80\text{ pu} = 23.52\ \Omega}$
- **激磁電壓**：$E_f = \mathbf{3707.03\text{ V/相}}$（線電壓 $6420.8\text{ V}$）
- **電壓調整率**：$\text{VR} = \mathbf{52.88\%}$

---

## 三、三相感應電動機戴維寧轉矩與轉差率（20 分）

### 📌 題目與已知條件
一部三相、4 極、$60\text{ Hz}$、$\text{Y}$ 接感應電動機，端電壓 $V_L = 220\text{ V}$。
- 單相等效電路參數：$R_1 = 0.3\ \Omega, X_1 = 0.5\ \Omega, R_2' = 0.2\ \Omega, X_2' = 0.5\ \Omega, X_m = 15\ \Omega$。
- 旋轉與鐵損忽略。

* **(一)** 求定子側戴維寧等效電壓 $V_{TH}$ 與阻抗 $Z_{TH} = R_{TH} + j X_{TH}$。（10 分）
* **(二)** 求產生最大轉矩時之轉差率 $s_{max}$、最大電磁轉矩 $T_{max}$ 與此時轉速 $n_{max}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **戴維寧等效參數**：
   $$V_1 = \frac{220}{\sqrt{3}} \approx 127.02\text{ V}$$
   $$V_{TH} = V_1 \left|\frac{j X_m}{R_1 + j(X_1 + X_m)}\right| = 127.02 \times \frac{15}{\sqrt{0.3^2 + 15.5^2}} = 127.02 \times \frac{15}{15.503} = \mathbf{122.90\text{ V}}$$
   $$Z_{TH} = \frac{j X_m (R_1 + j X_1)}{R_1 + j(X_1 + X_m)} = \frac{j 15(0.3 + j 0.5)}{0.3 + j 15.5} \approx \mathbf{0.281 + j 0.484\ \Omega}$$
   （即 $R_{TH} = 0.281\ \Omega, X_{TH} = 0.484\ \Omega$）
2. **最大轉矩之轉差率 $s_{max}$**：
   $$\mathbf{s_{max} = \frac{R_2'}{\sqrt{R_{TH}^2 + (X_{TH} + X_2')^2}} = \frac{0.2}{\sqrt{0.281^2 + (0.484 + 0.5)^2}} = \frac{0.2}{\sqrt{0.0790 + 0.9683}} = \frac{0.2}{1.0234} = \mathbf{0.1954 \approx 19.54\%}}$$
3. **同步角速度與最大轉矩**：
   $$n_s = \frac{120 \times 60}{4} = 1800\text{ rpm} \implies \omega_s = \frac{2\pi \times 1800}{60} = 188.50\text{ rad/s}$$
   $$\mathbf{T_{max} = \frac{3 V_{TH}^2}{2 \omega_s [R_{TH} + \sqrt{R_{TH}^2 + (X_{TH} + X_2')^2}]} = \frac{3 \times 122.90^2}{2 \times 188.50 \times (0.281 + 1.0234)} = \frac{45313.2}{377 \times 1.3044} = \mathbf{92.14\text{ N}\cdot\text{m}}}$$
4. **最大轉矩時轉速**：
   $$\mathbf{n_{max} = (1 - s_{max}) n_s = (1 - 0.1954) \times 1800 = \mathbf{1448.3\text{ rpm}}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **戴維寧等效**：$V_{TH} = \mathbf{122.90\text{ V}}, Z_{TH} = \mathbf{0.281 + j0.484\ \Omega}$
- **最大轉矩轉差率**：$s_{max} = \mathbf{0.1954\ (19.54\%)}$
- **最大電磁轉矩**：$T_{max} = \mathbf{92.14\text{ N}\cdot\text{m}}$
- **此時轉子轉速**：$n_{max} = \mathbf{1448.3\text{ rpm}}$

---

## 四、直流並激電動機電樞電阻串聯調速（20 分）

### 📌 題目與已知條件
- 額定：$220\text{ V}, 10\text{ hp}$（輸出 $7460\text{ W}$）、$1200\text{ rpm}$、滿載電樞電流 $I_a = 40\text{ A}$。
- 電樞電阻 $R_a = 0.25\ \Omega$，磁場固定不變。
- 負載轉矩與轉速之平方成正比：$T_L \propto n^2$。

* **(一)** 欲使轉速降至 $900\text{ rpm}$，求電樞迴路需外加串聯電阻 $R_{ext}$ 為何？（10 分）
* **(二)** 在 $900\text{ rpm}$ 時之電動機輸出功率與操作效率為何？（忽略機械與鐵損）（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **額定狀態反電動勢與轉矩**：
   $$E_{a1} = V_t - I_{a1} R_a = 220 - 40 \times 0.25 = 210\text{ V}$$
   因磁場固定，$E_a = K_e n \implies K_e = \frac{210}{1200} = 0.175\text{ V/rpm}$。
   電磁轉矩 $T = K_t I_a$。
2. **在 $900\text{ rpm}$ 時之電樞電流 $I_{a2}$**：
   因 $T_L \propto n^2 \implies \frac{T_2}{T_1} = \left(\frac{900}{1200}\right)^2 = (0.75)^2 = 0.5625$。
   因 $T \propto I_a \implies I_{a2} = I_{a1} \times 0.5625 = 40 \times 0.5625 = \mathbf{22.5\text{ A}}$。
3. **求外加電阻 $R_{ext}$**：
   在 $900\text{ rpm}$ 下之反電動勢：
   $$E_{a2} = K_e \times 900 = 0.175 \times 900 = 157.5\text{ V}$$
   回路方程式：$V_t - E_{a2} = I_{a2} (R_a + R_{ext})$
   $$220 - 157.5 = 22.5 \times (0.25 + R_{ext}) \implies 62.5 = 22.5 (0.25 + R_{ext})$$
   $$0.25 + R_{ext} = \frac{62.5}{22.5} = 2.7778\ \Omega \implies \mathbf{R_{ext} = 2.7778 - 0.25 = \mathbf{2.5278\ \Omega \approx 2.53\ \Omega}}$$
4. **輸出功率與效率**：
   $$P_{out,2} = E_{a2} I_{a2} = 157.5 \times 22.5 = \mathbf{3543.75\text{ W}}$$
   $$P_{in,2} = V_t I_{a2} = 220 \times 22.5 = \mathbf{4950\text{ W}}$$
   $$\mathbf{\eta = \frac{P_{out,2}}{P_{in,2}} \times 100\% = \frac{3543.75}{4950} \times 100\% = \mathbf{71.59\%}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **外加電阻**：$R_{ext} = \mathbf{2.528\ \Omega}$
- **輸出功率**：$P_{out} = \mathbf{3543.75\text{ W}}$（約 $4.75\text{ hp}$）
- **操作效率**：$\eta = \mathbf{71.59\%}$

---

## 五、三相變壓器 Y-Δ 短路阻抗與電壓調整率（20 分）

### 📌 題目與已知條件
- 三台相同單相變壓器組成三相組，額定容量 $300\text{ kVA}$（每台 $100\text{ kVA}$）、電壓比 $11\text{ kV} / 220\text{ V}$（$\text{Y}-\Delta$ 接線）。
- 單台變壓器等效至高壓側之短路阻抗為 $Z_{eq,H} = (1.2 + j3.6)\ \Omega$。
- 負載為三相平衡滿載，功率因數 $\text{PF} = 0.8\text{ 落後}$。

* **(一)** 求此三相變壓器組等效至一次側（$\text{Y}$ 側）之每相標么阻抗 $Z_{pu}$。（10 分）
* **(二)** 求滿載 $\text{PF} = 0.8\text{ 落後}$ 下之二次側端電壓與電壓調整率 $\text{VR}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **基準值與標么阻抗**：
   一次側為 $\text{Y}$ 接，$V_{L1} = 11\text{ kV}, S_{3\phi} = 300\text{ kVA}$。
   $$Z_{base1} = \frac{V_{L1}^2}{S_{3\phi}} = \frac{(11\times 10^3)^2}{300\times 10^3} = \frac{121 \times 10^6}{300 \times 10^3} = 403.33\ \Omega$$
   每相實際高壓側阻抗即為單台高壓側阻抗 $Z_{eq} = 1.2 + j3.6\ \Omega$：
   $$R_{pu} = \frac{1.2}{403.33} = 0.002975\text{ pu}, \quad X_{pu} = \frac{3.6}{403.33} = 0.008926\text{ pu}$$
   $$\mathbf{Z_{pu} = 0.00298 + j0.00893\text{ pu} \quad (|Z_{pu}| = 0.00941\text{ pu} = 0.941\%)}$$
2. **電壓調整率公式**：
   $$\mathbf{VR \approx (R_{pu} \cos\theta + X_{pu} \sin\theta) \times 100\%}$$
   代入 $\cos\theta = 0.8, \sin\theta = 0.6$：
   $$\text{VR} \approx (0.002975 \times 0.8 + 0.008926 \times 0.6) \times 100\% = (0.00238 + 0.005356) \times 100\% = \mathbf{0.774\%}$$
   精密相量解：
   $$V_1 = 1.0\angle 0^\circ + (1.0\angle -36.87^\circ)(0.002975 + j0.008926) = 1.00774 + j0.00536 \implies |V_1| = 1.00775\text{ pu}$$
   $$\mathbf{VR = \frac{1.00775 - 1.0}{1.0} \times 100\% = \mathbf{0.775\%}}$$
   二次側線電壓：$V_{L2} = \frac{220}{1.00775} = \mathbf{218.31\text{ V}}$。

---

### 🎯 第五題 滿分關鍵與結論
- **標么阻抗**：$Z_{pu} = \mathbf{0.00298 + j0.00893\text{ pu} = 0.941\angle 71.57^\circ\%}$
- **電壓調整率**：$\text{VR} = \mathbf{0.775\%}$
- **滿載二次端電壓**：$V_{L2} = \mathbf{218.31\text{ V}}$
'''

with open('📝 個人題解與錯題本/04_電機機械/113年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_113)
print('✅ 113年 電機機械 detailed solution written!')
