# -*- coding: utf-8 -*-
import os

sol_112 = '''---
考科: 電機機械
年份: 112
主題: 112 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、鐵心電感器電感值、阻抗與最大交變磁通量計算 (Inductor L & Peak Magnetic Flux)
  - 二、大型三相同步發電機相量圖、功角與靜態穩定極限 (Synchronous Generator Ef & Pmax)
  - 三、三相感應電動機轉矩-轉差率曲線與起動/最大轉矩 (Induction Motor Starting & Breakdown Torque)
  - 四、直流並激電動機電樞反應、反電動勢與負載轉速 (DC Shunt Motor Ea & Speed Regulation)
  - 五、三相變壓器組接法、全日效率與最大效率條件 (Transformer All-Day Efficiency)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 112 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 112 年 電機機械 試題導覽清單
- [👉 第一題：鐵心電感器電感值與最大磁通量計算（20 分）](#一鐵心電感器電感值與最大磁通量計算20-分)
- [👉 第二題：大型三相同步發電機相量與功率極限（20 分）](#二大型三相同步發電機相量與功率極限20-分)
- [👉 第三題：三相感應電動機起動與最大轉矩特性（20 分）](#三三相感應電動機起動與最大轉矩特性20-分)
- [👉 第四題：直流並激電動機負載反電動勢與轉速特性（20 分）](#四直流並激電動機負載反電動勢與轉速特性20-分)
- [👉 第五題：三相變壓器組接法與全日效率計算（20 分）](#五三相變壓器組接法與全日效率計算20-分)

---

## 一、鐵心電感器電感值與最大磁通量計算（20 分）

### 📌 題目與已知條件
- 鐵心參數：相對導磁係數 $\mu_r = 950$，磁路平均長度 $l_c = 32\text{ cm} = 0.32\text{ m}$，截面積 $A_c = 20\text{ cm}^2 = 20 \times 10^{-4}\text{ m}^2 = 2 \times 10^{-3}\text{ m}^2$。
- 線圈匝數 $N = 70\text{ 匝}$。
- 電路連接：與 $R = 60\ \Omega$ 電阻器串聯，接至 $V_s = 220\text{ V}, 60\text{ Hz}$ 單相交流電源（$\omega = 2\pi \times 60 = 377\text{ rad/s}$）。

* **(一)** 計算此電感器之電感值 $L$。（10 分）
* **(二)** 計算鐵心中磁通量 $\Phi$ 之最大值 $\Phi_{max}$。（10 分）

---

### 💡 核心考點與破題關鍵
1. **磁阻與電感公式**：
   $$\mathcal{R}_c = \frac{l_c}{\mu_r \mu_0 A_c}, \quad L = \frac{N^2}{\mathcal{R}_c} = \frac{N^2 \mu_r \mu_0 A_c}{l_c}$$
2. **交流串聯電路電流與端電壓**：
   - 感抗 $X_L = \omega L$
   - 總阻抗 $Z = R + j X_L \implies |Z| = \sqrt{R^2 + X_L^2}$
   - 電流有效值 $I_{rms} = \frac{V_s}{|Z|}$
3. **最大磁通量 $\Phi_{max}$**：
   $$\Phi_{max} = \frac{\mathcal{F}_{max}}{\mathcal{R}_c} = \frac{N I_{max}}{\mathcal{R}_c} = \frac{N (\sqrt{2} I_{rms})}{\mathcal{R}_c} = \frac{L (\sqrt{2} I_{rms})}{N} = \frac{V_{L,max}}{N \omega}$$

---

### ✏️ 步驟式詳細數學推導

#### 🔹 第 (一) 小題：計算電感值 $L$
1. **計算磁阻 $\mathcal{R}_c$**：
   $$\mu = \mu_r \mu_0 = 950 \times (4\pi \times 10^{-7}) = 3.8\pi \times 10^{-4} \approx 1.1938 \times 10^{-3}\text{ H/m}$$
   $$\mathcal{R}_c = \frac{0.32}{(1.1938 \times 10^{-3}) \times (2 \times 10^{-3})} = \frac{0.32}{2.3876 \times 10^{-6}} \approx \mathbf{1.3403 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
2. **計算電感 $L$**：
   $$\mathbf{L = \frac{N^2}{\mathcal{R}_c} = \frac{70^2}{1.3403 \times 10^5} = \frac{4900}{134026} \approx \mathbf{0.03656\text{ H} = 36.56\text{ mH}}}$$

---

#### 🔹 第 (二) 小題：計算鐵心中磁通量最大值 $\Phi_{max}$
1. **計算感抗與總阻抗**：
   $$X_L = \omega L = (2\pi \times 60) \times 0.03656 = 376.99 \times 0.03656 = \mathbf{13.78\ \Omega}$$
   $$|Z| = \sqrt{R^2 + X_L^2} = \sqrt{60^2 + 13.78^2} = \sqrt{3600 + 189.9} = \sqrt{3789.9} = \mathbf{61.56\ \Omega}$$
2. **計算電路電流**：
   $$I_{rms} = \frac{V_s}{|Z|} = \frac{220}{61.56} = 3.5737\text{ A} \implies I_{max} = \sqrt{2} \times 3.5737 = \mathbf{5.054\text{ A}}$$
3. **計算最大磁通量 $\Phi_{max}$**：
   $$\mathbf{\Phi_{max} = \frac{N I_{max}}{\mathcal{R}_c} = \frac{70 \times 5.054}{1.3403 \times 10^5} = \frac{353.78}{134026} \approx \mathbf{2.6396 \times 10^{-3}\text{ Wb} = 2.64\text{ mWb}}}$$
   *(磁通密度峰值 $B_{max} = \frac{\Phi_{max}}{A_c} = \frac{2.64 \times 10^{-3}}{2 \times 10^{-3}} = 1.32\text{ T}$)*

---

### 🎯 第一題 滿分關鍵與結論
- **電感值**：$L = \mathbf{36.56\text{ mH}}$
- **最大磁通量**：$\Phi_{max} = \mathbf{2.64\text{ mWb}}$（$B_{max} = 1.32\text{ T}$）

---

## 二、大型三相同步發電機相量與功率極限（20 分）

### 📌 題目與已知條件
- 額定：三相 $\text{Y}$ 接、$5000\text{ kVA}$、$13.8\text{ kV}$、$60\text{ Hz}$。
- 同步電抗 $X_s = 20\ \Omega/\text{相}$，電樞電阻 $R_a$ 忽略。
- 運轉條件：額定滿載，功率因數 $\text{PF} = 0.8\text{ 落後}$。

* **(一)** 求額定滿載下每相激磁電壓 $E_f$、功角 $\delta$ 與電壓調整率 $\text{VR}$。（10 分）
* **(二)** 在激磁電流固定（$E_f$ 固定）下，求此發電機之最大輸出實功率 $P_{max}$ 與此時之電樞電流 $I_{a,max}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **每相端電壓與電樞電流**：
   $$V_\phi = \frac{13800}{\sqrt{3}} \approx 7967.43\text{ V}, \quad I_a = \frac{5000 \times 10^3}{\sqrt{3}\times 13800} = 209.18\angle -36.87^\circ\text{ A} = (167.35 - j125.51)\text{ A}$$
2. **求解激磁相量 $\mathbf{E}_f$**：
   $$\mathbf{E}_f = V_\phi + j X_s \mathbf{I}_a = 7967.43 + j20(167.35 - j125.51) = (7967.43 + 2510.20) + j3347.00 = 10477.63 + j3347.00\text{ V}$$
   $$|\mathbf{E}_f| = \sqrt{10477.63^2 + 3347.00^2} = \mathbf{10999.0\text{ V/相} \approx 11.0\text{ kV/相}}$$
   $$\mathbf{\delta = \tan^{-1}\left(\frac{3347.00}{10477.63}\right) = \mathbf{17.72^\circ}}$$
   $$\mathbf{VR = \frac{10999.0 - 7967.43}{7967.43} \times 100\% = \mathbf{38.05\%}}$$
3. **最大輸出實功率 $P_{max}$（$\delta = 90^\circ$）**：
   $$\mathbf{P_{max} = \frac{3 E_f V_\phi}{X_s} = \frac{3 \times 10999.0 \times 7967.43}{20} = \frac{262900742}{20} = \mathbf{13145\text{ kW} = 13.145\text{ MW}}}$$
4. **最大功率時之電樞電流**：
   $$\mathbf{I}_{a,max} = \frac{\mathbf{E}_f(90^\circ) - \mathbf{V}_\phi}{j X_s} = \frac{j 10999.0 - 7967.43}{j 20} = 549.95 + j 398.37\text{ A}$$
   $$|\mathbf{I}_{a,max}| = \sqrt{549.95^2 + 398.37^2} = \mathbf{679.08\text{ A}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **(一) 激磁電壓與功角**：$E_f = \mathbf{11.0\text{ kV/相}}$（線電壓 $19.05\text{ kV}$），$\delta = \mathbf{17.72^\circ}$，$\text{VR} = \mathbf{38.05\%}$
- **(二) 最大輸出功率與電流**：$P_{max} = \mathbf{13.145\text{ MW}}$，$I_{a,max} = \mathbf{679.08\text{ A}}$

---

## 三、三相感應電動機起動與最大轉矩特性（20 分）

### 📌 題目與已知條件
一部三相、4 極、$60\text{ Hz}$、$460\text{ V}$（$\text{Y}$ 接）、$50\text{ hp}$ 感應電動機，等效至定子側之單相參數為：
$R_1 = 0.1\ \Omega, X_1 = 0.4\ \Omega, R_2' = 0.12\ \Omega, X_2' = 0.4\ \Omega, X_m = 12\ \Omega$。忽略鐵損與旋轉損。

* **(一)** 計算電動機之起動電流 $I_{start}$ 與起動轉矩 $T_{start}$。（10 分）
* **(二)** 計算最大轉矩（崩潰轉矩）$T_{max}$ 與此時之轉差率 $s_{max}$ 及轉速 $n_{max}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **戴維寧等效參數**：
   $$V_1 = \frac{460}{\sqrt{3}} \approx 265.58\text{ V}$$
   $$V_{TH} \approx V_1 \frac{X_m}{X_1 + X_m} = 265.58 \times \frac{12}{12.4} = \mathbf{257.01\text{ V}}$$
   $$Z_{TH} \approx R_1 \left(\frac{X_m}{X_1+X_m}\right)^2 + j X_1 = 0.1 \times (0.9677)^2 + j 0.4 = \mathbf{0.0936 + j 0.40\ \Omega}$$
2. **起動特性（$s = 1.0$）**：
   $$Z_{start} = (R_{TH} + R_2') + j(X_{TH} + X_2') = (0.0936 + 0.12) + j(0.40 + 0.40) = 0.2136 + j 0.80\ \Omega$$
   $$|Z_{start}| = \sqrt{0.2136^2 + 0.80^2} = 0.828\ \Omega$$
   $$I_{start} = \frac{V_{TH}}{|Z_{start}|} = \frac{257.01}{0.828} = \mathbf{310.40\text{ A}}$$
   $$\omega_s = \frac{2\pi \times 1800}{60} = 188.50\text{ rad/s}$$
   $$\mathbf{T_{start} = \frac{3 I_{start}^2 (R_2'/1.0)}{\omega_s} = \frac{3 \times (310.40)^2 \times 0.12}{188.50} = \frac{34685}{188.50} = \mathbf{184.0\text{ N}\cdot\text{m}}}$$
3. **最大轉矩特性**：
   $$\mathbf{s_{max} = \frac{R_2'}{\sqrt{R_{TH}^2 + (X_{TH} + X_2')^2}} = \frac{0.12}{\sqrt{0.0936^2 + 0.80^2}} = \frac{0.12}{0.8055} = \mathbf{0.1490\ (14.90\%)}}$$
   $$\mathbf{T_{max} = \frac{3 V_{TH}^2}{2\omega_s [R_{TH} + \sqrt{R_{TH}^2 + (X_{TH} + X_2')^2}]} = \frac{3 \times 257.01^2}{2 \times 188.50 \times (0.0936 + 0.8055)} = \frac{198162}{377 \times 0.8991} = \mathbf{584.6\text{ N}\cdot\text{m}}}$$
   $$\mathbf{n_{max} = (1 - 0.1490) \times 1800 = \mathbf{1531.8\text{ rpm}}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **(一) 起動電流與轉矩**：$I_{start} = \mathbf{310.40\text{ A}}$，$T_{start} = \mathbf{184.0\text{ N}\cdot\text{m}}$
- **(二) 最大轉矩與轉速**：$T_{max} = \mathbf{584.6\text{ N}\cdot\text{m}}$，$s_{max} = \mathbf{14.90\%}$，$n_{max} = \mathbf{1531.8\text{ rpm}}$

---

## 四、直流並激電動機負載反電動勢與轉速特性（20 分）

### 📌 題目與已知條件
- 額定：$240\text{ V}, 1200\text{ rpm}, R_a = 0.2\ \Omega, R_f = 120\ \Omega$。
- 滿載輸入總電流 $I_L = 52\text{ A}$。忽略電樞反應與機械摩擦損。

* **(一)** 計算滿載時之電樞電流 $I_a$、反電動勢 $E_a$ 與電磁轉矩 $T$。（10 分）
* **(二)** 若負載轉矩降為滿載之 $60\%$，且在場電路串聯電阻使磁通減少 $10\%$，求此時之電樞電流與穩定轉速。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **滿載額定狀態**：
   $$I_f = \frac{V_t}{R_f} = \frac{240}{120} = 2.0\text{ A} \implies I_{a1} = I_L - I_f = 52 - 2 = \mathbf{50.0\text{ A}}$$
   $$E_{a1} = V_t - I_{a1} R_a = 240 - 50 \times 0.2 = \mathbf{230.0\text{ V}}$$
   $$\omega_{m1} = \frac{2\pi \times 1200}{60} = 40\pi \approx 125.66\text{ rad/s}$$
   $$\mathbf{T_1 = \frac{E_{a1} I_{a1}}{\omega_{m1}} = \frac{230 \times 50}{125.664} = \mathbf{91.51\text{ N}\cdot\text{m}}}$$
2. **負載改變與弱磁運轉**：
   - 磁通 $\Phi_2 = 0.90 \Phi_1$，轉矩 $T_2 = 0.60 T_1 = 0.60 \times 91.51 = 54.91\text{ N}\cdot\text{m}$。
   - 因 $T = K \Phi I_a \implies \frac{T_2}{T_1} = \frac{\Phi_2}{\Phi_1} \frac{I_{a2}}{I_{a1}} \implies 0.60 = 0.90 \times \frac{I_{a2}}{50}$：
     $$\mathbf{I_{a2} = 50 \times \frac{0.60}{0.90} = \mathbf{33.33\text{ A}}}$$
   - 新反電動勢：$E_{a2} = V_t - I_{a2} R_a = 240 - 33.33 \times 0.2 = 240 - 6.67 = \mathbf{233.33\text{ V}}$。
   - 因 $E_a = K \Phi n \implies \frac{E_{a2}}{E_{a1}} = \frac{\Phi_2}{\Phi_1} \frac{n_2}{n_1}$：
     $$\frac{233.33}{230.0} = 0.90 \times \frac{n_2}{1200} \implies \mathbf{n_2 = 1200 \times \frac{233.33}{230.0 \times 0.90} = \mathbf{1352.6\text{ rpm}}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **(一) 滿載參數**：$I_a = \mathbf{50.0\text{ A}}, E_a = \mathbf{230.0\text{ V}}, T = \mathbf{91.51\text{ N}\cdot\text{m}}$
- **(二) 弱磁輕載參數**：$I_{a2} = \mathbf{33.33\text{ A}}, n_2 = \mathbf{1352.6\text{ rpm}}$

---

## 五、三相變壓器組接法與全日效率計算（20 分）

### 📌 題目與已知條件
- 單相變壓器 3 台，每台額定 $50\text{ kVA}, 2400/240\text{ V}, 60\text{ Hz}$。
- 每台鐵損 $P_c = 300\text{ W}$，滿載銅損 $P_{cu,FL} = 600\text{ W}$。
- 組成三相變壓器組，供應負載運轉日負載曲線如下：
  - 滿載（$\text{PF} = 0.8$ 落後）：6 小時
  - 半載（$\text{PF} = 1.0$）：8 小時
  - 無載：10 小時

* **(一)** 計算三相組滿載時之傳統效率 $\eta_{FL}$（$\text{PF} = 0.8$）。（10 分）
* **(二)** 計算此變壓器組之全日效率（All-Day Efficiency）$\eta_{all-day}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **三相組總容量與損耗**：
   - 總額定容量 $S_{3\phi} = 3 \times 50 = 150\text{ kVA}$。
   - 總鐵損（24小時固定）：$P_{c,total} = 3 \times 300\text{ W} = 0.9\text{ kW}$。
   - 總滿載銅損：$P_{cu,total} = 3 \times 600\text{ W} = 1.8\text{ kW}$。
2. **滿載傳統效率（$\text{PF} = 0.8$）**：
   $$P_{out,FL} = 150 \times 0.8 = 120\text{ kW}$$
   $$P_{loss,FL} = P_{c,total} + P_{cu,total} = 0.9 + 1.8 = 2.7\text{ kW}$$
   $$\mathbf{\eta_{FL} = \frac{120}{120 + 2.7} \times 100\% = \frac{120}{122.7} \times 100\% = \mathbf{97.80\%}}$$
3. **全日能量損耗與輸出**：
   - **24小時總輸出電能**：
     $$W_{out} = (150 \times 0.8 \times 6) + (150 \times 0.5 \times 1.0 \times 8) + 0 = 720 + 600 = \mathbf{1320\text{ kWh}}$$
   - **24小時總鐵損電能**：
     $$W_{core} = 0.9\text{ kW} \times 24\text{ h} = \mathbf{21.6\text{ kWh}}$$
   - **24小時總銅損電能**：
     $$W_{cu} = [1.8 \times (1.0)^2 \times 6] + [1.8 \times (0.5)^2 \times 8] + 0 = 10.8 + 3.6 = \mathbf{14.4\text{ kWh}}$$
   - **全日效率**：
     $$\mathbf{\eta_{all-day} = \frac{W_{out}}{W_{out} + W_{core} + W_{cu}} \times 100\% = \frac{1320}{1320 + 21.6 + 14.4} \times 100\% = \frac{1320}{1356} \times 100\% = \mathbf{97.35\%}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **滿載傳統效率**：$\eta_{FL} = \mathbf{97.80\%}$
- **全日能量效率**：$\eta_{all-day} = \mathbf{97.35\%}$
'''

with open('📝 個人題解與錯題本/04_電機機械/112年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_112)
print('✅ 112年 電機機械 detailed solution written!')
