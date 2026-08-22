# -*- coding: utf-8 -*-
import os

sol_105 = '''---
考科: 電機機械
年份: 105
主題: 105 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、方波電壓源施加於純電感之電流波形與積分推導 (Square Wave Applied to Inductor)
  - 二、120/240V 變壓器降壓操作之二次側輸出電壓與最大可用容量 (Transformer De-rating)
  - 三、繞線式感應電動機轉子外接電阻改善起動特性分析 (Wound-Rotor IM External Resistor)
  - 四、同步電動機功率因數由 0.8 超前調至 1.0 之激磁相量圖 (Synchronous Motor PF Control)
  - 五、300V 外激直流電動機減磁與降壓調速轉速計算 (DC Separately Excited Motor Speed)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 105 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 105 年 電機機械 試題導覽清單
- [👉 第一題：交流方波施加於電感之瞬時電流變化（20 分）](#一交流方波施加於電感之瞬時電流變化20-分)
- [👉 第二題：變壓器非額定電壓操作之輸出與容量（20 分）](#二變壓器非額定電壓操作之輸出與容量20-分)
- [👉 第三題：繞線式感應機外接電阻起動原理（20 分）](#三繞線式感應機外接電阻起動原理20-分)
- [👉 第四題：同步電動機功率因數調整與相量圖（20 分）](#四同步電動機功率因數調整與相量圖20-分)
- [👉 第五題：外激直流電動機降壓與減磁調速（20 分）](#五外激直流電動機降壓與減磁調速20-分)

---

## 一、交流方波施加於電感之瞬時電流變化（20 分）

### 📌 題目與已知條件
- 交流方波電壓源：振幅 $V_m = 10\text{ V}$，週期 $T = 1\text{ ms} = 10^{-3}\text{ s}$（半週期 $\frac{T}{2} = 0.5\text{ ms}$）。
- 連接至 $L = 1\text{ mH} = 10^{-3}\text{ H}$ 電感器，電阻忽略。
- 開關於「電壓由正轉負零交越點」切入導通（即 $t=0$ 時 $v(t)$ 從 $+10\text{ V}$ 切換為 $-10\text{ V}$）。

* 試繪出開關導通後第一個週期內電感電流 $i(t)$ 的變化。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **電感基本積分方程式**：
   $$i(t) = i(0) + \frac{1}{L} \int_0^t v(\tau) d\tau$$
   假設初始電流 $i(0) = 0$。
2. **前半週期（$0 \le t \le 0.5\text{ ms}$），電壓 $v(t) = -10\text{ V}$**：
   $$i(t) = 0 + \frac{1}{10^{-3}} \int_0^t (-10) d\tau = -10000 t\text{ A}$$
   在 $t = 0.5\text{ ms} = 0.5 \times 10^{-3}\text{ s}$ 時：
   $$i(0.5\text{ ms}) = -10000 \times (0.5 \times 10^{-3}) = \mathbf{-5.0\text{ A}}$$
3. **後半週期（$0.5\text{ ms} \le t \le 1.0\text{ ms}$），電壓 $v(t) = +10\text{ V}$**：
   $$i(t) = -5.0 + \frac{1}{10^{-3}} \int_{0.5\times 10^{-3}}^t (+10) d\tau = -5.0 + 10000 (t - 0.5 \times 10^{-3})$$
   在 $t = 1.0\text{ ms}$ 時：
   $$i(1.0\text{ ms}) = -5.0 + 10000 (0.5 \times 10^{-3}) = -5.0 + 5.0 = \mathbf{0\text{ A}}$$
4. **波形結論**：
   $i(t)$ 在第一個週期內為**下凹之三角形斜坡波（Triangular Wave）**，從 $0\text{ A}$ 線性降至 $-5.0\text{ A}$，再線性回升至 $0\text{ A}$。

---

### 🎯 第一題 滿分關鍵與結論
- **電流變化**：為線性三角波，最小值在 $t = 0.5\text{ ms}$ 達到 $\mathbf{-5.0\text{ A}}$，在 $t = 1.0\text{ ms}$ 回到 $\mathbf{0\text{ A}}$。

---

## 二、變壓器非額定電壓操作之輸出與容量（20 分）

### 📌 題目與已知條件
- 變壓器額定：$120\text{ V} / 240\text{ V}, 12\text{ kVA}, 60\text{ Hz}$。
- 將 $110\text{ V}, 60\text{ Hz}$ 交流電源接於變壓器高壓側（$240\text{ V}$ 繞組）。

* 計算低壓側之輸出電壓與變壓器之最大可用容量。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **低壓側輸出電壓**：
   變壓器匝數比固定：$a = \frac{V_H}{V_L} = \frac{240}{120} = 2.0$。
   當高壓側施加 $V_H' = 110\text{ V}$ 時，低壓側空載輸出電壓為：
   $$\mathbf{V_{out} = \frac{V_H'}{a} = \frac{110\text{ V}}{2.0} = \mathbf{55.0\text{ V}}}$$
2. **最大可用容量（De-rating Capacity）**：
   變壓器繞組容量受限於**額定電流（溫升極限）**：
   - 高壓側額定電流：$I_{H,rated} = \frac{12000\text{ VA}}{240\text{ V}} = \mathbf{50.0\text{ A}}$。
   - 低壓側額定電流：$I_{L,rated} = \frac{12000\text{ VA}}{120\text{ V}} = \mathbf{100.0\text{ A}}$。
   當輸入電壓降為 $110\text{ V}$，為不使繞組過熱，允許最大輸入/輸出電流仍為 $50.0\text{ A}$：
   $$\mathbf{S_{max} = V_H' \times I_{H,rated} = 110\text{ V} \times 50.0\text{ A} = \mathbf{5500\text{ VA} = 5.5\text{ kVA}}}$$
   （亦等於 $V_{out} \times I_{L,rated} = 55\text{ V} \times 100\text{ A} = 5.5\text{ kVA}$）

---

### 🎯 第二題 滿分關鍵與結論
- **低壓側輸出電壓**：$V_{out} = \mathbf{55.0\text{ V}}$
- **最大可用容量**：$S_{max} = \mathbf{5.5\text{ kVA}}$（降額運轉）

---

## 三、繞線式感應機外接電阻起動原理（20 分）

* **(一) 提升起動轉矩原理**：
  由感應機轉矩公式：$T_{start} = \frac{3 V_{TH}^2 (R_2 + R_{ext})}{\omega_s [(R_{TH} + R_2 + R_{ext})^2 + (X_{TH} + X_2')^2]}$。
  最大轉矩發生轉差率 $s_{max} = \frac{R_2 + R_{ext}}{\sqrt{R_{TH}^2 + X_{eq}^2}}$。
  - 當外接適當電阻使 $R_2 + R_{ext} = \sqrt{R_{TH}^2 + X_{eq}^2}$ 時，最大轉矩剛好發生在起動點（$s=1.0$），使**起動轉矩達到極大值 $T_{max}$**。
* **(二) 降低起動電流原理**：
  起動時總阻抗為 $|Z_{start}| = \sqrt{(R_{TH} + R_2 + R_{ext})^2 + X_{eq}^2}$。
  外接電阻 $R_{ext}$ 大幅提升了電路總阻抗，直接限制了轉子與定子迴路的突波電流，達到**顯著降低起動電流 $I_{start}$ 之效果**。

---

## 四、同步電動機功率因數調整與相量圖（20 分）

* **相量方程式**：$\mathbf{V}_\phi = \mathbf{E}_f + j X_s \mathbf{I}_a \implies \mathbf{E}_f = \mathbf{V}_\phi - j X_s \mathbf{I}_a$。
* **物理推導與調整步驟**：
  1. 原操作於 $\text{PF} = 0.8\text{ 超前}$，代表電流 $\mathbf{I}_a$ 超前電壓 $\mathbf{V}_\phi$，此時電動機處於**過激磁狀態（Over-excited）**，向電網輸出虛功（相當於電容器）。
  2. 欲使功率因數提高至 $\text{PF} = 1.0$（單位功因），需**調降轉子激磁直流電流 $I_f$**。
  3. 激磁電流減小使內生電動勢 $E_f$ 之幅值縮小，相量圖上 $j X_s \mathbf{I}_a$ 與 $\mathbf{I}_a$ 順時針旋轉，直到 $\mathbf{I}_a$ 與 $\mathbf{V}_\phi$ 同相位（落於 V 形曲線最底部）。此時電樞電流達到**局部最小值**，且不再與電網交換無效功率。

---

## 五、外激直流電動機降壓與減磁調速（20 分）

### 📌 題目與已知條件
- 額定：$V_{t1} = 300\text{ V}, R_a = 100\text{ m}\Omega = 0.1\ \Omega, I_{a,rated} = 600\text{ A}, I_{f,rated} = 12\text{ A}, n_1 = 800\text{ rpm}$。
- 新運轉條件：負載轉矩 $T_2 = \frac{1}{2} T_{rated}$，電樞電壓 $V_{t2} = 240\text{ V}$，磁場電流調至 $I_{f2} = 6\text{ A}$（因未飽和 $\Phi_2 = \frac{6}{12}\Phi_1 = 0.5 \Phi_1$）。

* 計算新運轉條件下之轉速 $n_2$ 為多少 rpm？（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **額定狀態反電動勢**：
   $$E_{a1} = V_{t1} - I_{a1} R_a = 300 - (600 \times 0.1) = 300 - 60 = \mathbf{240.0\text{ V}}$$
2. **狀況二之電樞電流 $I_{a2}$**：
   轉矩關係：$T = K \Phi I_a \implies \frac{T_2}{T_1} = \left(\frac{\Phi_2}{\Phi_1}\right)\left(\frac{I_{a2}}{I_{a1}}\right)$
   $$0.5 = 0.5 \times \left(\frac{I_{a2}}{600}\right) \implies \mathbf{I_{a2} = \mathbf{600.0\text{ A}}}$$
3. **狀況二反電動勢 $E_{a2}$ 與轉速 $n_2$**：
   $$E_{a2} = V_{t2} - I_{a2} R_a = 240 - (600 \times 0.1) = 240 - 60 = \mathbf{180.0\text{ V}}$$
   轉速關係：$\frac{E_{a2}}{E_{a1}} = \left(\frac{\Phi_2}{\Phi_1}\right)\left(\frac{n_2}{n_1}\right)$
   $$\frac{180}{240} = 0.5 \times \left(\frac{n_2}{800}\right) \implies 0.75 = \frac{n_2}{1600}$$
   $$\mathbf{n_2 = 0.75 \times 1600 = \mathbf{1200\text{ rpm}}}$$

---

### 🎯 第五題 滿分關鍵與結論
- **新轉速**：$n_2 = \mathbf{1200\text{ rpm}}$
'''

sol_104 = '''---
考科: 電機機械
年份: 104
主題: 104 年 電機機械 全卷五大題完整詳細推導、考點剖析與 E-MORE fx-127 計算機秒殺解法
考點:
  - 一、對稱雙支路磁路安培環路定律與磁通方程推導 (Magnetic Circuit Node Equations)
  - 二、1.0 kVA 變壓器 60Hz 接 50Hz 電源操作分析與磁通飽和 (Transformer Frequency Derating)
  - 三、3.0V 永磁直流電動機升壓調速、電流與效率計算 (PMDC Motor Speed & Efficiency)
  - 四、三相 2.2 kVA 380V 感應電動機標么等效電路起動電流 (Induction Motor pu Starting Current)
  - 五、三相 6.6 kVA 380V 同步發電機功角與激磁調節分析 (Synchronous Generator Power Angle)
難易度: ⭐⭐⭐⭐⭐
掌握狀態: 🟢 已掌握
最後複習日期: 2026-08-17
---

# ⚡ 104 年 電機工程技師 — 電機機械 全卷完整詳細詳解與推導
## 🧮 附錄：E-MORE fx-127 國考合格計算機「相量與虛實轉換」全步驟秒殺按法

> [!TIP]
> 💡 **閱讀提示**：如果在 Obsidian 中看到一堆符號代碼，按鍵盤 **`Cmd + E`**（或點右上角的「書本 📖」圖示），畫面就會立刻切換成漂亮的教科書印刷排版！

---

## 📑 104 年 電機機械 試題導覽清單
- [👉 第一題：對稱雙支路磁路磁通推導（20 分）](#一對稱雙支路磁路磁通推導20-分)
- [👉 第二題：60Hz 變壓器接 50Hz 電源操作分析（20 分）](#二60hz-變壓器接-50hz-電源操作分析20-分)
- [👉 第三題：永磁直流電動機調壓與操作效率（20 分）](#三永磁直流電動機調壓與操作效率20-分)
- [👉 第四題：三相感應電動機標么值起動電流計算（20 分）](#四三相感應電動機標么值起動電流計算20-分)
- [👉 第五題：三相同步發電機激磁調節與功角（20 分）](#五三相同步發電機激磁調節與功角20-分)

---

## 一、對稱雙支路磁路磁通推導（20 分）

### 📌 題目與已知條件
如圖一所示之三柱磁路，各支路之磁阻均為 $\mathcal{R}$。左支路有磁動勢 $\mathcal{F}_1 = N_1 I_1$，右支路有磁動勢 $\mathcal{F}_2 = N_2 I_2$。

* 推導流經兩個支路之磁通 $\Phi_1$ 與 $\Phi_2$ 之表示式。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **磁路節點與迴路方程式**：
   - 節點磁通連續性：中間柱磁通 $\Phi_3 = \Phi_1 + \Phi_2$。
   - 左迴路 KVL：$\mathcal{F}_1 = \Phi_1 \mathcal{R} + \Phi_3 \mathcal{R} = 2 \mathcal{R} \Phi_1 + \mathcal{R} \Phi_2$。
   - 右迴路 KVL：$\mathcal{F}_2 = \Phi_2 \mathcal{R} + \Phi_3 \mathcal{R} = \mathcal{R} \Phi_1 + 2 \mathcal{R} \Phi_2$。
2. **聯立求解 $\Phi_1, \Phi_2$**：
   由矩陣形式：
   $$\begin{bmatrix} 2\mathcal{R} & \mathcal{R} \\ \mathcal{R} & 2\mathcal{R} \end{bmatrix} \begin{bmatrix} \Phi_1 \\ \Phi_2 \end{bmatrix} = \begin{bmatrix} \mathcal{F}_1 \\ \mathcal{F}_2 \end{bmatrix}$$
   行列式 $\Delta = (2\mathcal{R})(2\mathcal{R}) - \mathcal{R}^2 = 3\mathcal{R}^2$。
   $$\mathbf{\Phi_1 = \frac{2\mathcal{R}\mathcal{F}_1 - \mathcal{R}\mathcal{F}_2}{3\mathcal{R}^2} = \mathbf{\frac{2\mathcal{F}_1 - \mathcal{F}_2}{3\mathcal{R}}}}$$
   $$\mathbf{\Phi_2 = \frac{2\mathcal{R}\mathcal{F}_2 - \mathcal{R}\mathcal{F}_1}{3\mathcal{R}^2} = \mathbf{\frac{2\mathcal{F}_2 - \mathcal{F}_1}{3\mathcal{R}}}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **支路磁通**：$\Phi_1 = \mathbf{\frac{2\mathcal{F}_1 - \mathcal{F}_2}{3\mathcal{R}}}, \quad \Phi_2 = \mathbf{\frac{2\mathcal{F}_2 - \mathcal{F}_1}{3\mathcal{R}}}$

---

## 二、60Hz 變壓器接 50Hz 電源操作分析（20 分）

### 📌 題目與已知條件
單相變壓器額定 $1.0\text{ kVA}, 200\text{ V} / 100\text{ V}, 60\text{ Hz}$。若低壓側接 $10\ \Omega$ 純電阻負載，高壓側接 $200\text{ V}, 50\text{ Hz}$ 電源。

* 說明此電路之可能操作情形與物理影響。（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **磁通密度增加與鐵心飽和**：
   由電壓公式 $V \approx 4.44 f N \Phi_m \implies \Phi_m \propto \frac{V}{f}$。
   頻率由 $60\text{ Hz}$ 降至 $50\text{ Hz}$（電壓維持 $200\text{ V}$）：
   $$\frac{\Phi_{m,50}}{\Phi_{m,60}} = \frac{60}{50} = \mathbf{1.20\ (增加\ 20\%)}$$
   鐵心工作點將深入**嚴重磁飽和區**，導致激磁電流 $I_m$ 呈非線性暴增 $3\sim 5$ 倍，波形產生嚴重尖峰畸變。
2. **損耗與溫度效應**：
   - 磁滯損 $P_h \propto f B_m^{1.6} \propto 50 \times (1.2)^{1.6} \approx 50 \times 1.339 = 66.9$（相較於 $60 \times 1 = 60$ 增加約 $11.6\%$）。
   - 激磁電流增加使空載銅損大幅上升，變壓器**溫升劇增，有過熱燒毀風險**。
3. **負載運轉能力**：
   二次側輸出電壓仍約為 $100\text{ V}$，負載電流 $I_2 = \frac{100}{10} = 10\text{ A}$，輸出容量 $S = 100 \times 10 = 1000\text{ VA} = 1.0\text{ kVA}$（達到額定滿載），由於鐵損與激磁電流均上升，**此時操作將處於過溫危險狀態，建議降額（De-rate）至 $80\%$ 容量運轉**。

---

### 🎯 第二題 滿分關鍵與結論
- **核心影響**：磁通增加 $\mathbf{20\%}$ 引起磁飽和、激磁電流暴增、溫升劇增，建議降額至 $\mathbf{0.8\text{ kVA}}$ 以下運轉。

---

## 三、永磁直流電動機調壓與操作效率（20 分）

### 📌 題目與已知條件
- 額定 $3.0\text{ V}$ 永磁直流電動機（PMDC），$R_a = 0.05\ \Omega$，機械摩擦損忽略，負載轉矩固定。
- 狀況一：輸入 $V_{t1} = 3.0\text{ V}, I_{a1} = 2.0\text{ A}$ 時，轉速 $n_1 = 600\text{ rpm}$。
- 狀況二：輸入電壓提昇至 $V_{t2} = 3.1\text{ V}$，負載轉矩不變，轉速升至 $n_2 = 612\text{ rpm}$。

* **(一)** 狀況一之電動機輸出功率 $P_{out1}$ 為何？（7 分）
* **(二)** 狀況二之電樞電流 $I_{a2}$ 為多少安培？（7 分）
* **(三)** 狀況二之操作效率 $\eta_2$ 為多少 $\%$？（6 分）

---

### ✏️ 步驟式詳細數學推導
1. **狀況一輸出功率**：
   $$E_{a1} = V_{t1} - I_{a1} R_a = 3.0 - (2.0 \times 0.05) = 3.0 - 0.10 = \mathbf{2.90\text{ V}}$$
   $$\mathbf{P_{out1} = E_{a1} I_{a1} = 2.90 \times 2.0 = \mathbf{5.80\text{ W}}}$$
2. **狀況二電樞電流**：
   因負載轉矩固定且永磁磁通 $\Phi$ 固定，由 $T = K\Phi I_a$ 可知：
   $$\mathbf{I_{a2} = I_{a1} = \mathbf{2.0\text{ A}}}$$
3. **狀況二反電動勢與操作效率**：
   $$E_{a2} = V_{t2} - I_{a2} R_a = 3.1 - (2.0 \times 0.05) = 3.1 - 0.10 = \mathbf{3.00\text{ V}}$$
   輸出功率：$P_{out2} = E_{a2} I_{a2} = 3.00 \times 2.0 = \mathbf{6.00\text{ W}}$。
   輸入功率：$P_{in2} = V_{t2} I_{a2} = 3.1 \times 2.0 = \mathbf{6.20\text{ W}}$。
   $$\mathbf{\eta_2 = \frac{P_{out2}}{P_{in2}} \times 100\% = \frac{6.00}{6.20} \times 100\% \approx \mathbf{96.77\%}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **狀況一輸出功率**：$P_{out1} = \mathbf{5.80\text{ W}}$
- **狀況二電樞電流**：$I_{a2} = \mathbf{2.0\text{ A}}$
- **狀況二效率**：$\eta_2 = \mathbf{96.77\%}$

---

## 四、三相感應電動機標么值起動電流計算（20 分）

### 📌 題目與已知條件
- 基準值：三相 $S_{base} = 2.2\text{ kVA}, V_{base} = 380\text{ V}$（$\text{Y}$ 接）。
- 標么值參數：$r_s = 0.05\text{ pu}, r_r = 0.05\text{ pu}, x_s = 0.15\text{ pu}, x_r = 0.15\text{ pu}, R_c = 30\text{ pu}, X_m = 40\text{ pu}$。

* 求感應電動機起動電流 $I_{start}$ 為多少安培？（20 分）

---

### ✏️ 步驟式詳細數學推導
1. **基準電流計算**：
   $$\mathbf{I_{base} = \frac{S_{base}}{\sqrt{3} V_{base}} = \frac{2200}{\sqrt{3} \times 380} = \frac{2200}{658.18} \approx \mathbf{3.3426\text{ A}}}$$
2. **起動時等效標么阻抗（$s = 1.0$）**：
   轉子支路標么阻抗：$Z_r = r_r + j x_r = 0.05 + j 0.15\text{ pu}$。
   激磁支路阻抗 $Z_m = R_c \parallel j X_m = 30 \parallel j 40 = \frac{j 1200}{30 + j 40} = 19.2 + j 14.4\text{ pu} \gg Z_r$（激磁支路可忽略或精算）。
   精確並聯阻抗：
   $$Z_p = Z_r \parallel Z_m \approx Z_r = 0.05 + j 0.15\text{ pu}$$
   總起動標么阻抗：
   $$Z_{start,pu} = (r_s + j x_s) + Z_r = (0.05 + 0.05) + j(0.15 + 0.15) = \mathbf{0.10 + j 0.30\text{ pu}}$$
   $$|Z_{start,pu}| = \sqrt{0.10^2 + 0.30^2} = \sqrt{0.01 + 0.09} = \sqrt{0.10} \approx \mathbf{0.31623\text{ pu}}$$
3. **起動標么電流與實際電流**：
   $$I_{start,pu} = \frac{V_{pu}}{|Z_{start,pu}|} = \frac{1.0}{0.31623} \approx \mathbf{3.1623\text{ pu}}$$
   $$\mathbf{I_{start} = I_{start,pu} \times I_{base} = 3.1623 \times 3.3426 \approx \mathbf{10.57\text{ A}}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **基準電流**：$I_{base} = \mathbf{3.343\text{ A}}$
- **起動標么電流**：$I_{start,pu} = \mathbf{3.162\text{ pu}}$
- **實際起動電流**：$I_{start} = \mathbf{10.57\text{ A}}$

---

## 五、三相同步發電機激磁調節與功角（20 分）

### 📌 題目與已知條件
- 額定：三相 $6.6\text{ kVA}, 380\text{ V}, 60\text{ Hz}, 4$ 極同步發電機，同步電抗 $X_s = 1.0\ \Omega/\text{相}$，電樞電阻與損耗忽略。
- 運轉於額定滿載輸出，調節激磁電流使功率因數為 $\text{PF} = 1.0$。

* **(一)** 計算額定滿載電流 $I_a$ 與相電壓 $V_\phi$。（10 分）
* **(二)** 計算激磁電壓 $E_f$ 與功率角 $\delta$。（10 分）

---

### ✏️ 步驟式詳細數學推導
1. **相電壓與額定電流**：
   $$V_\phi = \frac{380}{\sqrt{3}} \approx \mathbf{219.39\text{ V}}$$
   $$\mathbf{I_a = \frac{6600}{\sqrt{3} \times 380 \times 1.0} = \mathbf{10.028\text{ A} \angle 0^\circ}}$$
2. **求解激磁相量 $\mathbf{E}_f$ 與功角 $\delta$**：
   $$\mathbf{E}_f = V_\phi + j X_s \mathbf{I}_a = 219.39 + j(1.0 \times 10.028) = \mathbf{219.39 + j 10.028\text{ V}}$$
   $$|\mathbf{E}_f| = \sqrt{219.39^2 + 10.028^2} = \sqrt{48132 + 100.56} = \sqrt{48232.6} \approx \mathbf{219.62\text{ V/相}}$$
   $$\mathbf{\delta = \tan^{-1}\left(\frac{10.028}{219.39}\right) = \tan^{-1}(0.0457) = \mathbf{2.62^\circ}}$$
   *(線電壓激磁電勢為 $E_{f,L} = \sqrt{3} \times 219.62 = 380.4\text{ V}$)*

---

### 🎯 第五題 滿分關鍵與結論
- **滿載電流與相電壓**：$V_\phi = \mathbf{219.39\text{ V}}, I_a = \mathbf{10.03\text{ A}}$
- **每相激磁電壓**：$E_f = \mathbf{219.62\text{ V/相}}$
- **功率角**：$\delta = \mathbf{2.62^\circ}$
'''

with open('📝 個人題解與錯題本/04_電機機械/105年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_105)
with open('📝 個人題解與錯題本/04_電機機械/104年_電機機械_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_104)
print('✅ 105年 & 104年 電機機械 detailed solutions written!')
