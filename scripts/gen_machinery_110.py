# -*- coding: utf-8 -*-
import os

sol_110 = '''---
考科: 電機機械
年份: 110
主題: 110 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、鐵心磁路含氣隙之磁動勢、磁阻與磁通密度 (Magnetic Circuit with Air Gap)
  - 二、220/160V 雙繞組變壓器改接自耦變壓器容量與優點 (Autotransformer Capacity & Advantage)
  - 三、380V 8極 Y接三相同步電動機相量圖與功角計算 (Synchronous Motor Phasor & Power Angle)
  - 四、180V 3hp 永磁直流電動機反電動勢常數與負載轉速 (PMDC Motor Back EMF & Speed)
  - 五、208V 30hp 六極鼠籠感應電動機等效電路與起動/最大轉矩 (Induction Motor Equivalent Circuit)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 110 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 110 年 電機機械 試題導覽清單
- [👉 第一題：鐵心氣隙磁路與磁通密度計算（20 分）](#一鐵心氣隙磁路與磁通密度計算20-分)
- [👉 第二題：雙繞組變壓器改接自耦變壓器（20 分）](#二雙繞組變壓器改接自耦變壓器20-分)
- [👉 第三題：八極三相同步電動機相量與功角（20 分）](#三八極三相同步電動機相量與功角20-分)
- [👉 第四題：永磁直流電動機反電動勢與負載轉速（20 分）](#四永磁直流電動機反電動勢與負載轉速20-分)
- [👉 第五題：六極鼠籠式感應電動機等效電路與轉矩（20 分）](#五六極鼠籠式感應電動機等效電路與轉矩20-分)

---

## 一、鐵心氣隙磁路與磁通密度計算（20 分）

### 📌 題目與已知條件
- 鐵心平均長度 $l_c = 40\text{ cm} = 0.40\text{ m}$，相對導磁係數 $\mu_r = 1500$，截面積 $A = 16\text{ cm}^2 = 1.6 \times 10^{-3}\text{ m}^2$。
- 氣隙長度 $l_g = 1.5\text{ mm} = 1.5 \times 10^{-3}\text{ m}$。線圈匝數 $N = 600\text{ 匝}$。
- 欲在氣隙中建立 $B_g = 1.2\text{ T}$ 之磁通密度。

* **(一)** 求鐵心磁阻 $\mathcal{R}_c$、氣隙磁阻 $\mathcal{R}_g$ 與總磁阻 $\mathcal{R}_{total}$。（10 分）
* **(二)** 求線圈所需通入之激磁電流 $I$ 與此時之線圈電感 $L$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **磁阻計算**：
   $$\mathcal{R}_c = \frac{l_c}{\mu_r \mu_0 A} = \frac{0.40}{1500 \times (4\pi \times 10^{-7}) \times (1.6 \times 10^{-3})} = \frac{0.40}{3.0159 \times 10^{-6}} \approx \mathbf{1.3263 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
   $$\mathcal{R}_g = \frac{l_g}{\mu_0 A} = \frac{1.5 \times 10^{-3}}{(4\pi \times 10^{-7}) \times (1.6 \times 10^{-3})} = \frac{1.5 \times 10^{-3}}{2.0106 \times 10^{-9}} \approx \mathbf{7.4604 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
   $$\mathcal{R}_{total} = \mathcal{R}_c + \mathcal{R}_g = 1.3263 \times 10^5 + 7.4604 \times 10^5 = \mathbf{8.7867 \times 10^5\text{ A}\cdot\text{t/Wb}}$$
2. **所需電流與電感值**：
   磁通量 $\Phi = B_g A = 1.2 \times (1.6 \times 10^{-3}) = \mathbf{1.92 \times 10^{-3}\text{ Wb} = 1.92\text{ mWb}}$。
   總磁動勢 $\mathcal{F} = \Phi \mathcal{R}_{total} = (1.92 \times 10^{-3}) \times (8.7867 \times 10^5) = \mathbf{1687.05\text{ A}\cdot\text{t}}$。
   $$\mathbf{I = \frac{\mathcal{F}}{N} = \frac{1687.05}{600} \approx \mathbf{2.812\text{ A}}}$$
   $$\mathbf{L = \frac{N^2}{\mathcal{R}_{total}} = \frac{600^2}{8.7867 \times 10^5} = \frac{360000}{878670} \approx \mathbf{0.4097\text{ H} = 409.7\text{ mH}}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **總磁阻**：$\mathcal{R}_{total} = \mathbf{8.787 \times 10^5\text{ A}\cdot\text{t/Wb}}$
- **激磁電流**：$I = \mathbf{2.812\text{ A}}$
- **線圈電感**：$L = \mathbf{409.7\text{ mH}}$

---

## 二、雙繞組變壓器改接自耦變壓器（20 分）

### 📌 題目與已知條件
- 雙繞組變壓器額定：$60\text{ Hz}, 220\text{ V} / 160\text{ V}, 30\text{ kVA}$。
- 將兩繞組串聯改接為自耦變壓器，從 $220\text{ V}$ 輸入端升壓至 $380\text{ V}$（即 $220 + 160 = 380\text{ V}$）輸出供應負載。

* **(一)** 計算此自耦變壓器之額定視在功率容量 $S_{auto}$（$\text{kVA}$）。（10 分）
* **(二)** 分析自耦變壓器容量中，透過「電氣傳導（Conducted）」與「磁場感應（Transformed）」傳輸之功率各為多少？（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **額定電流與自耦容量**：
   - 原一次側（$220\text{ V}$）額定電流：$I_1 = \frac{30000}{220} = 136.36\text{ A}$。
   - 原二次側（$160\text{ V}$，作為自耦串聯繞組）額定電流：$I_2 = \frac{30000}{160} = \mathbf{187.5\text{ A}}$。
   - 輸出端電壓 $V_H = 220 + 160 = 380\text{ V}$，允許最大輸出電流即為串聯繞組電流 $I_{out} = I_2 = 187.5\text{ A}$。
   - **自耦變壓器額定容量**：
     $$\mathbf{S_{auto} = V_H \times I_{out} = 380\text{ V} \times 187.5\text{ A} = \mathbf{71250\text{ VA} = 71.25\text{ kVA}}}$$
     *(容量提升比率 $\frac{S_{auto}}{S_{two-wdg}} = \frac{380}{160} = 2.375$ 倍！)*
2. **傳導與感應功率拆解**：
   - **磁場感應功率（Transformed Power）**：等於雙繞組本體容量：
     $$\mathbf{S_{ind} = S_{two-wdg} = \mathbf{30.0\text{ kVA}}}$$
   - **電氣直接傳導功率（Conducted Power）**：
     $$\mathbf{S_{cond} = S_{auto} - S_{ind} = 71.25 - 30.0 = \mathbf{41.25\text{ kVA}}}$$
     （傳導比例為 $\frac{220}{380} = 57.89\%$，感應比例為 $\frac{160}{380} = 42.11\%$）

---

### 🎯 第二題 滿分關鍵與結論
- **自耦變壓器容量**：$S_{auto} = \mathbf{71.25\text{ kVA}}$
- **感應功率**：$S_{ind} = \mathbf{30.0\text{ kVA}}$，**傳導功率**：$S_{cond} = \mathbf{41.25\text{ kVA}}$

---

## 三、八極三相同步電動機相量與功角（20 分）

### 📌 題目與已知條件
- 額定：三相 $\text{Y}$ 接、$380\text{ V}, 60\text{ Hz}, 15\text{ kW}$、8 極同步電動機。
- 每相同步電抗 $X_s = 2.5\ \Omega$，電樞電阻忽略。
- 運轉於額定滿載輸出 $15\text{ kW}$，功率因數 $\text{PF} = 0.85\text{ 超前}$。忽略損耗。

* **(一)** 求電動機電樞電流相量 $\mathbf{I}_a$ 與每相反電動勢（內生電壓）$E_f$。（10 分）
* **(二)** 求電動機之功率角 $\delta$ 與電磁轉矩 $T$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **每相端電壓與電樞電流**：
   $$V_\phi = \frac{380}{\sqrt{3}} \approx 219.39\text{ V}$$
   $$I_a = \frac{P_{in}}{\sqrt{3} V_L \cos\theta} = \frac{15000}{\sqrt{3} \times 380 \times 0.85} = \frac{15000}{559.45} = \mathbf{26.812\text{ A}}$$
   因功因超前 $\theta = +\cos^{-1}(0.85) = +31.79^\circ$：
   $$\mathbf{I}_a = 26.812\angle 31.79^\circ = 26.812(0.85 + j0.5268) = \mathbf{22.79 + j14.12\text{ A}}$$
2. **電動機反電動勢相量 $\mathbf{E}_f$**：
   電動機方程式：$\mathbf{E}_f = \mathbf{V}_\phi - j X_s \mathbf{I}_a$
   $$\mathbf{E}_f = 219.39\angle 0^\circ - j 2.5 \times (22.79 + j 14.12) = 219.39 - j 56.98 + 35.30 = \mathbf{254.69 - j 56.98\text{ V}}$$
   $$|\mathbf{E}_f| = \sqrt{254.69^2 + (-56.98)^2} = \sqrt{64867 + 3247} = \sqrt{68114} \approx \mathbf{260.99\text{ V/相}}$$
   $$\mathbf{\delta = \tan^{-1}\left(\frac{-56.98}{254.69}\right) = \mathbf{-12.61^\circ}}$$
   *(功角為負值代表電動機模式，轉子磁場落後於定子旋轉磁場 $12.61^\circ$)*
3. **同步轉速與轉矩**：
   $$n_s = \frac{120 \times 60}{8} = 900\text{ rpm} \implies \omega_s = \frac{2\pi \times 900}{60} = 30\pi \approx 94.248\text{ rad/s}$$
   $$\mathbf{T = \frac{P_{conv}}{\omega_s} = \frac{15000}{94.248} = \mathbf{159.15\text{ N}\cdot\text{m}}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **電樞電流**：$\mathbf{I}_a = \mathbf{26.81\angle 31.79^\circ\text{ A}}$
- **內生反電動勢**：$E_f = \mathbf{260.99\text{ V/相}}$
- **功率角**：$\delta = \mathbf{-12.61^\circ}$
- **電磁轉矩**：$T = \mathbf{159.15\text{ N}\cdot\text{m}}$

---

## 四、永磁直流電動機反電動勢與負載轉速（20 分）

### 📌 題目與已知條件
- 額定規格：$3\text{ hp}$（$2238\text{ W}$）、$180\text{ V}$ 永磁式直流電動機（PMDC），電樞電阻 $R_a = 2.01\ \Omega$。
- 無載試驗：外加額定電壓 $180\text{ V}$ 時，無載電流 $I_{a,nl} = 1.0\text{ A}$，無載轉速 $n_{nl} = 2400\text{ rpm}$。
- 滿載額定輸出時，總效率為 $82\%$。

* **(一)** 計算電動機之反電動勢常數 $K_E$（$\text{V/rpm}$）與無載旋轉損耗 $P_{rot}$。（10 分）
* **(二)** 當接上額定負載且端電壓為 $180\text{ V}$ 時，求電樞電流 $I_a$ 與滿載轉速 $n_{FL}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **無載參數推導**：
   $$E_{a,nl} = V_t - I_{a,nl} R_a = 180 - (1.0 \times 2.01) = \mathbf{177.99\text{ V}}$$
   $$\mathbf{K_E = \frac{E_{a,nl}}{n_{nl}} = \frac{177.99}{2400} \approx \mathbf{0.07416\text{ V/rpm}}}$$
   無載旋轉機械損：
   $$\mathbf{P_{rot} = E_{a,nl} I_{a,nl} = 177.99 \times 1.0 = \mathbf{177.99\text{ W}}}$$
2. **滿載運轉推導**：
   額定輸出 $P_{out} = 3\text{ hp} = 2238\text{ W}$，效率 $\eta = 82\% = 0.82$：
   $$P_{in} = \frac{P_{out}}{\eta} = \frac{2238}{0.82} \approx 2729.27\text{ W}$$
   $$\mathbf{I_{a,FL} = \frac{P_{in}}{V_t} = \frac{2729.27}{180} = \mathbf{15.163\text{ A}}}$$
   滿載反電動勢：
   $$E_{a,FL} = V_t - I_{a,FL} R_a = 180 - (15.163 \times 2.01) = 180 - 30.48 = \mathbf{149.52\text{ V}}$$
   滿載轉速：
   $$\mathbf{n_{FL} = \frac{E_{a,FL}}{K_E} = \frac{149.52}{0.07416} \approx \mathbf{2016.2\text{ rpm}}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **反電動勢常數**：$K_E = \mathbf{0.07416\text{ V/rpm}}$
- **滿載電樞電流**：$I_a = \mathbf{15.16\text{ A}}$
- **滿載轉速**：$n_{FL} = \mathbf{2016.2\text{ rpm}}$

---

## 五、六極鼠籠式感應電動機等效電路與轉矩（20 分）

### 📌 題目與已知條件
- 額定：三相 $60\text{ Hz}, 208\text{ V}$（$\text{Y}$ 接）、6 極、$30\text{ hp}$ 鼠籠式感應電動機。
- 每相等效電路參數：$R_1 = 0.08\ \Omega, X_1 = 0.25\ \Omega, R_2' = 0.06\ \Omega, X_2' = 0.25\ \Omega, X_m = 10\ \Omega$。忽略鐵損。

* **(一)** 求額定滿載轉差率 $s = 3.5\%$ 時之定子輸入電流與功率因數。（10 分）
* **(二)** 求電動機之起動轉矩 $T_{start}$ 與最大電磁轉矩 $T_{max}$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **滿載阻抗與電流（$s = 0.035$）**：
   $$V_1 = \frac{208}{\sqrt{3}} \approx 120.09\text{ V}$$
   轉子支路阻抗：$Z_2 = \frac{R_2'}{s} + j X_2' = \frac{0.06}{0.035} + j 0.25 = 1.7143 + j 0.25\ \Omega$
   轉子與激磁並聯阻抗：
   $$Z_p = \frac{(j 10)(1.7143 + j 0.25)}{1.7143 + j 10.25} = \frac{-2.5 + j 17.143}{1.7143 + j 10.25} = 1.621 + j 0.518\ \Omega$$
   總輸入阻抗：$Z_{in} = (R_1 + j X_1) + Z_p = (0.08 + 1.621) + j(0.25 + 0.518) = 1.701 + j 0.768\ \Omega$
   $$|Z_{in}| = \sqrt{1.701^2 + 0.768^2} = \mathbf{1.866\ \Omega}$$
   $$\mathbf{I_1 = \frac{120.09}{1.866} = \mathbf{64.36\text{ A}}}$$
   $$\mathbf{PF = \cos(\tan^{-1}\frac{0.768}{1.701}) = \cos(24.29^\circ) = \mathbf{0.9115\text{ 落後}}}$$
2. **起動轉矩與最大轉矩**：
   - 戴維寧參數：$V_{TH} \approx 120.09 \times \frac{10}{10.25} = 117.16\text{ V}, R_{TH} \approx 0.08 \times (0.9756)^2 = 0.076\ \Omega, X_{TH} \approx 0.25\ \Omega$。
   - 同步轉速：$n_s = \frac{120 \times 60}{6} = 1200\text{ rpm} \implies \omega_s = \frac{2\pi \times 1200}{60} = 40\pi \approx 125.66\text{ rad/s}$。
   - **起動轉矩（$s = 1.0$）**：
     $$I_{start} = \frac{117.16}{\sqrt{(0.076 + 0.06)^2 + (0.25 + 0.25)^2}} = \frac{117.16}{\sqrt{0.136^2 + 0.50^2}} = \frac{117.16}{0.5182} = \mathbf{226.08\text{ A}}$$
     $$\mathbf{T_{start} = \frac{3 \times (226.08)^2 \times 0.06}{125.66} = \frac{9200}{125.66} = \mathbf{73.21\text{ N}\cdot\text{m}}}$$
   - **最大轉矩**：
     $$s_{max} = \frac{0.06}{\sqrt{0.076^2 + 0.50^2}} = \frac{0.06}{0.5057} = \mathbf{0.1186\ (11.86\%)}$$
     $$\mathbf{T_{max} = \frac{3 \times 117.16^2}{2 \times 125.66 \times (0.076 + 0.5057)} = \frac{41180.6}{251.33 \times 0.5817} = \mathbf{281.67\text{ N}\cdot\text{m}}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **滿載定子電流與功因**：$I_1 = \mathbf{64.36\text{ A}}, \text{PF} = \mathbf{0.9115\text{ 落後}}$
- **起動轉矩**：$T_{start} = \mathbf{73.21\text{ N}\cdot\text{m}}$
- **最大電磁轉矩**：$T_{max} = \mathbf{281.67\text{ N}\cdot\text{m}}$（$s_{max} = 11.86\%$）
'''

with open('📝 個人題解與錯題本/04_電機機械/110年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_110)
print('✅ 110年 電機機械 detailed solution written!')
