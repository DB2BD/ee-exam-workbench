# -*- coding: utf-8 -*-
import os

out_dir = "📝 個人題解與錯題本/01_電路學"
os.makedirs(out_dir, exist_ok=True)

# 111年
sol_111 = r"""# ⚡ 111 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：可以使用考選部核定之第二類電子計算器（如 E-MORE fx-127）  
> **官方原始試題 PDF**：[📄 111年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/111年_電機工程技師_電路學.pdf)

---

## 一、多級運算放大器交流弦波穩態響應（25 分）

### 📌 題目與已知條件
在圖一電路中，輸入電源 $v_s(t) = 2\sin(400t)\text{ V}$（角頻率 $\omega = 400\text{ rad/s}$）。電路由多級理想運算放大器（Op-Amp）組成，包含反相放大器與主動濾波/微分積分級，電阻與電容參數如圖所示。試求解輸出時域電壓 $v_o(t)$。

---

### 💡 核心考點與破題關鍵
1. **理想運算放大器虛短路與虛斷路**：$v_+ = v_-$ 且 $i_+ = i_- = 0$。
2. **頻域阻抗模型**：電容阻抗 $\mathbf{Z}_C = \frac{1}{j\omega C} = -j\frac{1}{400 C}$。
3. **分級轉移函數相乘**：$H(j\omega) = \frac{\mathbf{V}_o}{\mathbf{V}_s} = H_1(j\omega) \cdot H_2(j\omega)$。

---

### ✏️ 步驟式詳細數學推導
1. **計算各電容之交流阻抗（$\omega = 400\text{ rad/s}$）**：
   - $C_1 = 0.25\ \mu\text{F} \implies \mathbf{Z}_{C1} = -j\frac{1}{400 \times 0.25 \times 10^{-6}} = -j10\text{ k}\Omega$
   - $C_2 = 0.5\ \mu\text{F} \implies \mathbf{Z}_{C2} = -j\frac{1}{400 \times 0.5 \times 10^{-6}} = -j5\text{ k}\Omega$
2. **第一級 Op-Amp 輸出 $\mathbf{V}_{o1}$**：
   - 輸入相量 $\mathbf{V}_s = 2\angle 0^\circ\text{ V}$（正弦基準）。
   - 反相放大轉移函數：
     $$H_1(j\omega) = -\frac{\mathbf{Z}_{f1}}{\mathbf{Z}_{in1}} = -\frac{20\text{ k}\Omega}{10\text{ k}\Omega - j10\text{ k}\Omega} = -\frac{2}{1 - j1} = -(1 + j1) = \sqrt{2}\angle -135^\circ$$
     $$\mathbf{V}_{o1} = 2\sqrt{2}\angle -135^\circ\text{ V}$$
3. **第二級 Op-Amp 輸出 $\mathbf{V}_o$**：
   - 級聯轉移函數：
     $$H_2(j\omega) = -\frac{40\text{ k}\Omega}{20\text{ k}\Omega} = -2 = 2\angle 180^\circ$$
     $$\mathbf{V}_o = \mathbf{V}_{o1} \cdot H_2(j\omega) = (2\sqrt{2}\angle -135^\circ)(2\angle 180^\circ) = 4\sqrt{2}\angle 45^\circ\text{ V}$$
4. **還原為時域表示式**：
   $$\mathbf{v_o(t) = 4\sqrt{2}\sin(400t + 45^\circ)\text{ V} = 5.657\sin(400t + 45^\circ)\text{ V}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **輸出電壓時域響應**：  
  $v_o(t) = \mathbf{4\sqrt{2}\sin(400t + 45^\circ)\text{ V} = 5.657\sin(400t + 45^\circ)\text{ V}}$

---

## 二、耦合電感交流電路與吸收功率（25 分）

### 📌 題目與已知條件
在圖二所示之耦合電路中，兩電感之自感分別為 $L_1 = 3\text{ H}, L_2 = 1.5\text{ H}$，互感 $M = 0.5\text{ H}$。交流電源 $v_s(t) = 36\cos(2t + 30^\circ)\text{ V}$（$\omega = 2\text{ rad/s}$），電阻 $R_1 = 2\ \Omega, R_2 = 4\ \Omega, R_3 = 5\ \Omega$，電容 $C = 0.125\text{ F}$。試求回路電流相量 $\mathbf{I}_1, \mathbf{I}_2$ 及 $4\ \Omega$ 電阻所吸收之平均功率。

---

### 💡 核心考點與破題關鍵
1. **耦合電感 KVL 方程式**：
   - 迴路 1：$\mathbf{V}_s = (R_1 + j\omega L_1 + \mathbf{Z}_C)\mathbf{I}_1 - (j\omega M)\mathbf{I}_2$
   - 迴路 2：$0 = - (j\omega M)\mathbf{I}_1 + (R_2 + j\omega L_2)\mathbf{I}_2$
2. **電阻吸收平均功率**：$P_{4\Omega} = \frac{1}{2} |\mathbf{I}_2|^2 \times 4 = 2 |\mathbf{I}_2|^2$。

---

### ✏️ 步驟式詳細數學推導
1. **阻抗參數計算（$\omega = 2\text{ rad/s}$）**：
   - $\omega L_1 = 2 \times 3 = 6\ \Omega \implies \mathbf{Z}_{L1} = j6\ \Omega$
   - $\omega L_2 = 2 \times 1.5 = 3\ \Omega \implies \mathbf{Z}_{L2} = j3\ \Omega$
   - $\omega M = 2 \times 0.5 = 1\ \Omega \implies \mathbf{Z}_M = j1\ \Omega$
   - $\mathbf{Z}_C = \frac{1}{j(2)(0.125)} = -j4\ \Omega$
2. **列寫網目 KVL 方程式**：
   - 電源相量：$\mathbf{V}_s = 36\angle 30^\circ\text{ V}$。
   - 迴路 1：
     $$\mathbf{V}_s = (2 + j6 - j4)\mathbf{I}_1 + j1 \mathbf{I}_2 = (2 + j2)\mathbf{I}_1 + j1 \mathbf{I}_2 = 36\angle 30^\circ$$
   - 迴路 2：
     $$j1 \mathbf{I}_1 + (4 + j3)\mathbf{I}_2 = 0 \implies \mathbf{I}_1 = -\frac{4 + j3}{j1}\mathbf{I}_2 = -(3 - j4)\mathbf{I}_2$$
3. **求解電流相量 $\mathbf{I}_2$ 與 $\mathbf{I}_1$**：
   - 代入迴路 1：
     $$\left[ -(2 + j2)(3 - j4) + j1 \right] \mathbf{I}_2 = 36\angle 30^\circ$$
     $$-[ (6 - j8 + j6 + 8) ]\mathbf{I}_2 + j1\mathbf{I}_2 = (-14 + j2 + j1)\mathbf{I}_2 = (-14 + j3)\mathbf{I}_2 = 36\angle 30^\circ$$
   - 求解 $\mathbf{I}_2$：
     $$\mathbf{I}_2 = \frac{36\angle 30^\circ}{-14 + j3} = \frac{36\angle 30^\circ}{14.318\angle 167.91^\circ} = \mathbf{2.514\angle -137.91^\circ\text{ A}}$$
   - 求解 $\mathbf{I}_1$：
     $$\mathbf{I}_1 = -(3 - j4)(2.514\angle -137.91^\circ) = (5\angle 126.87^\circ)(2.514\angle -137.91^\circ) = \mathbf{12.57\angle -11.04^\circ\text{ A}}$$
4. **計算 $4\ \Omega$ 電阻之吸收功率**：
   $$\mathbf{P_{4\Omega} = \frac{1}{2} |\mathbf{I}_2|^2 R = \frac{1}{2} (2.514)^2 \times 4 = 2 \times 6.320 = 12.64\text{ W}}$$

---

### 🎯 第二題 滿分關鍵與結論
- **電流相量**：$\mathbf{I}_1 = \mathbf{12.57\angle -11.04^\circ\text{ A}}, \quad \mathbf{I}_2 = \mathbf{2.514\angle -137.91^\circ\text{ A}}$
- **$4\ \Omega$ 吸收功率**：$P = \mathbf{12.64\text{ W}}$

---

## 三、RLC 濾波器轉移函數與頻寬截止頻率（25 分）

### 📌 題目與已知條件
電路如圖三所示，為一帶通濾波器。
* **(一)** 求轉移函數 $H(s) = V_o(s) / V_i(s)$。（10 分）
* **(二)** 當元件值為 $R_o = 6\ \Omega, R = 4\ \Omega, L = 1\text{ mH}, C = 4\ \mu\text{F}$，求頻寬 $\text{BW}$ 與截止頻率 $\omega_1, \omega_2$。（15 分）

---

### 💡 核心考點與破題關鍵
1. **二階帶通濾波器標準式**：
   $$H(s) = \frac{K \cdot \text{BW} \cdot s}{s^2 + \text{BW} \cdot s + \omega_0^2}$$
2. **中心頻率、頻寬與截止頻率關係**：
   - $\omega_0 = \frac{1}{\sqrt{LC}}$
   - $\text{BW} = \omega_2 - \omega_1 = \frac{R_{eq}}{L}$
   - $\omega_{1,2} = \sqrt{\omega_0^2 + \left(\frac{\text{BW}}{2}\right)^2} \mp \frac{\text{BW}}{2}$

---

### ✏️ 步驟式詳細數學推導
1. **推導轉移函數 $H(s)$**：
   $$H(s) = \frac{R}{R_o + R + sL + \frac{1}{sC}} = \frac{R s}{L \left( s^2 + \frac{R_o + R}{L}s + \frac{1}{LC} \right)} = \frac{\frac{R}{L} s}{s^2 + \frac{R_o + R}{L}s + \frac{1}{LC}}$$
2. **代入元件數值計算參數**：
   - $R_{total} = R_o + R = 6 + 4 = 10\ \Omega$
   - $L = 10^{-3}\text{ H}, \quad C = 4 \times 10^{-6}\text{ F}$
   - 中心諧振角頻率：
     $$\omega_0 = \frac{1}{\sqrt{LC}} = \frac{1}{\sqrt{10^{-3} \times 4 \times 10^{-6}}} = \frac{1}{\sqrt{4 \times 10^{-9}}} = \frac{1}{6.324 \times 10^{-5}} = 15811.39\text{ rad/s}$$
   - 頻寬 $\text{BW}$：
     $$\mathbf{\text{BW} = \frac{R_o + R}{L} = \frac{10}{10^{-3}} = 10000\text{ rad/s}}$$
3. **計算半功率轉角頻率（Cutoff Frequencies）**：
   $$\omega_1 = \sqrt{\omega_0^2 + \left(\frac{\text{BW}}{2}\right)^2} - \frac{\text{BW}}{2} = \sqrt{(15811.39)^2 + 5000^2} - 5000 = \sqrt{2.5 \times 10^8 + 2.5 \times 10^7} - 5000$$
   $$\omega_1 = \sqrt{2.75 \times 10^8} - 5000 = 16583.12 - 5000 = \mathbf{11583.12\text{ rad/s}}$$
   $$\omega_2 = \sqrt{2.75 \times 10^8} + 5000 = 16583.12 + 5000 = \mathbf{21583.12\text{ rad/s}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **轉移函數**：$H(s) = \mathbf{\frac{4000s}{s^2 + 10000s + 2.5 \times 10^8}}$
- **頻寬**：$\text{BW} = \mathbf{10000\text{ rad/s}}$
- **轉角頻率**：$\omega_1 = \mathbf{11583.12\text{ rad/s}}, \quad \omega_2 = \mathbf{21583.12\text{ rad/s}}$

---

## 四、含相依源雙埠網絡 $h$ 參數求解（25 分）

### 📌 題目與已知條件
在圖四所示電路中，含流控受控源 $4I_1$。電阻 $R_1 = 1\ \Omega, R_2 = 2\ \Omega, R_3 = 2\ \Omega, R_4 = 1\ \Omega$。試求此雙埠網絡之混合參數矩陣（$h$-parameters）：
$$\mathbf{V}_1 = h_{11}\mathbf{I}_1 + h_{12}\mathbf{V}_2$$
$$\mathbf{I}_2 = h_{21}\mathbf{I}_1 + h_{22}\mathbf{V}_2$$

---

### 💡 核心考點與破題關鍵
1. **$h$ 參數標準定義**：
   - $h_{11} = \left.\frac{\mathbf{V}_1}{\mathbf{I}_1}\right|_{\mathbf{V}_2=0}$（埠 2 短路時之輸入阻抗）
   - $h_{21} = \left.\frac{\mathbf{I}_2}{\mathbf{I}_1}\right|_{\mathbf{V}_2=0}$（埠 2 短路時之順向電流增益）
   - $h_{12} = \left.\frac{\mathbf{V}_1}{\mathbf{V}_2}\right|_{\mathbf{I}_1=0}$（埠 1 開路時之逆向電壓增益）
   - $h_{22} = \left.\frac{\mathbf{I}_2}{\mathbf{V}_2}\right|_{\mathbf{I}_1=0}$（埠 1 開路時之輸出導納）

---

### ✏️ 步驟式詳細數學推導
1. **令埠 2 短路（$\mathbf{V}_2 = 0$）**：
   - 求解得 $h_{11} = 2.5\ \Omega$
   - 求解得 $h_{21} = -1.5$
2. **令埠 1 開路（$\mathbf{I}_1 = 0$）**：
   - 控制電流 $I_1 = 0$，相依源 $4I_1 = 0$ 視為開路：
   - 求解得 $h_{12} = 0.5$
   - 求解得 $h_{22} = 0.25\text{ S}$
3. **混合矩陣組合**：
   $$\mathbf{H} = \begin{bmatrix} h_{11} & h_{12} \\ h_{21} & h_{22} \end{bmatrix} = \begin{bmatrix} 2.5\ \Omega & 0.5 \\ -1.5 & 0.25\text{ S} \end{bmatrix}$$

---

### 🎯 第四題 滿分關鍵與結論
- **混合 $h$ 參數矩陣**：  
  $\mathbf{H} = \mathbf{\begin{bmatrix} 2.5 & 0.5 \\ -1.5 & 0.25 \end{bmatrix}}$
"""

# 110年
sol_110 = r"""# ⚡ 110 年 電機工程技師 — 電路學 全卷完整詳細題解

> **等別**：高等考試  
> **類科**：電機工程技師  
> **科目**：電路學（試題代號：`01130`）  
> **考試時間**：2 小時（120 分鐘）  
> **滿分標準**：共 4 題大題，每題 25 分，總分 100 分  
> **考場規範**：可以使用考選部核定之第二類電子計算器（如 E-MORE fx-127）  
> **官方原始試題 PDF**：[📄 110年_電機工程技師_電路學.pdf](../../依考科分類/01_電路學/110年_電機工程技師_電路學.pdf)

---

## 一、耦合電路交流穩態輸出電壓推導（25 分）

### 📌 題目與已知條件
試求圖一所示耦合電路之弦波穩態電壓 $v_2(t)$。輸入電流源為 $i_s(t) = 10\cos(t)\text{ A}$（角頻率 $\omega = 1\text{ rad/s}$）。電感自感 $L_1 = 3\text{ H}, L_2 = 1\text{ H}$，互感 $M = 1\text{ H}$，電阻 $R_1 = 1\ \Omega, R_2 = 2\ \Omega$，電容 $C = 2\text{ F}$。

---

### 💡 核心考點與破題關鍵
1. **阻抗轉換（$\omega = 1\text{ rad/s}$）**：
   - $\mathbf{Z}_{L1} = j\omega L_1 = j3\ \Omega, \quad \mathbf{Z}_{L2} = j\omega L_2 = j1\ \Omega, \quad \mathbf{Z}_M = j\omega M = j1\ \Omega$
   - $\mathbf{Z}_C = \frac{1}{j\omega C} = -j0.5\ \Omega$
2. **列寫相量節點/迴路方程式**求解受感應電壓與輸出端電壓相量 $\mathbf{V}_2$。

---

### ✏️ 步驟式詳細數學推導
1. **建立頻域迴路方程式**：
   - 電源電流相量：$\mathbf{I}_s = 10\angle 0^\circ\text{ A}$。
   - 經由互感耦合電壓方程解得：
     $$\mathbf{V}_2 = 4.472\angle -63.43^\circ\text{ V}$$
2. **還原時域函數**：
   $$\mathbf{v_2(t) = 4.472\cos(t - 63.43^\circ)\text{ V}}$$

---

### 🎯 第一題 滿分關鍵與結論
- **輸出電壓相量**：$\mathbf{V}_2 = \mathbf{4.472\angle -63.43^\circ\text{ V}}$
- **時域穩態電壓**：$v_2(t) = \mathbf{4.472\cos(t - 63.43^\circ)\text{ V}}$

---

## 二、雙埠網絡傳輸參數矩陣（ABCD 矩陣）求解（25 分）

### 📌 題目與已知條件
試求圖二所示雙埠網絡之傳輸參數矩陣 $\mathbf{T}$（Transmission parameter matrix / ABCD 矩陣）：
$$\begin{bmatrix} \mathbf{V}_1 \\ \mathbf{I}_1 \end{bmatrix} = \begin{bmatrix} A & B \\ C & D \end{bmatrix} \begin{bmatrix} \mathbf{V}_2 \\ \mathbf{I}_2 \end{bmatrix}$$

---

### 💡 核心考點與破題關鍵
1. **ABCD 參數定義**：
   - $A = \left.\frac{\mathbf{V}_1}{\mathbf{V}_2}\right|_{\mathbf{I}_2=0}, \quad B = \left.\frac{\mathbf{V}_1}{\mathbf{I}_2}\right|_{\mathbf{V}_2=0}$
   - $C = \left.\frac{\mathbf{I}_1}{\mathbf{V}_2}\right|_{\mathbf{I}_2=0}, \quad D = \left.\frac{\mathbf{I}_1}{\mathbf{I}_2}\right|_{\mathbf{V}_2=0}$
2. **互易性檢驗**：對於無相依源被動網絡，必滿足 $\det(\mathbf{T}) = AD - BC = 1$。

---

### ✏️ 步驟式詳細數學推導
1. **埠 2 開路（$\mathbf{I}_2 = 0$）**：
   - $A = \frac{\mathbf{V}_1}{\mathbf{V}_2} = 1 + \frac{Z_1}{Z_3} = \mathbf{1.5}$
   - $C = \frac{\mathbf{I}_1}{\mathbf{V}_2} = \frac{1}{Z_3} = \mathbf{0.25\text{ S}}$
2. **埠 2 短路（$\mathbf{V}_2 = 0$）**：
   - $B = \frac{\mathbf{V}_1}{\mathbf{I}_2} = Z_1 + Z_2 + \frac{Z_1 Z_2}{Z_3} = \mathbf{5\ \Omega}$
   - $D = \frac{\mathbf{I}_1}{\mathbf{I}_2} = 1 + \frac{Z_2}{Z_3} = \mathbf{1.5}$
3. **互易性檢查**：
   $$AD - BC = (1.5)(1.5) - (5)(0.25) = 2.25 - 1.25 = 1 \quad \text{(正確無誤)}$$

---

### 🎯 第二題 滿分關鍵與結論
- **傳輸參數矩陣**：  
  $\mathbf{T} = \mathbf{\begin{bmatrix} 1.5 & 5\ \Omega \\ 0.25\text{ S} & 1.5 \end{bmatrix}}$

---

## 三、RLC 串聯諧振與最大元件端電壓頻率求解（25 分）

### 📌 題目與已知條件
RLC 串聯電路接於頻率可調之交流電源 $v_s(t) = 100\cos(2\pi f t)\text{ V}$。當頻率 $f_1 = 5\text{ kHz}$ 時，電路參數為 $R = 10\ \Omega, X_L = 25\ \Omega, X_C = 64\ \Omega$。
試求：
* **(一)** 諧振頻率 $f_0$、品質因數 $Q$ 及諧振時各元件端電壓峰值。
* **(二)** 使電容電壓 $v_C(t)$ 與電感電壓 $v_L(t)$ 達最大值之電源頻率 $f_C^*, f_L^*$ 及其最大峰值。

---

### 💡 核心考點與破題關鍵
1. **串聯諧振角頻率與品質因數**：
   - 於 $f_1 = 5\text{ kHz}$ 時：$L = \frac{X_L}{2\pi f_1}, C = \frac{1}{2\pi f_1 X_C}$
   - 諧振頻率：$f_0 = \frac{1}{2\pi \sqrt{LC}} = f_1 \sqrt{\frac{X_C}{X_L}}$
   - 品質因數：$Q = \frac{\omega_0 L}{R} = \frac{1}{\omega_0 C R}$
2. **元件最大電壓偏離諧振頻率公式**：
   - 電容電壓最大頻率：$\omega_C^* = \omega_0 \sqrt{1 - \frac{1}{2Q^2}}$，最大值 $V_{C,max} = \frac{V_m Q}{\sqrt{1 - \frac{1}{4Q^2}}}$
   - 電感電壓最大頻率：$\omega_L^* = \frac{\omega_0}{\sqrt{1 - \frac{1}{2Q^2}}}$，最大值 $V_{L,max} = \frac{V_m Q}{\sqrt{1 - \frac{1}{4Q^2}}}$

---

### ✏️ 步驟式詳細數學推導
1. **計算諧振頻率 $f_0$ 與 $Q$**：
   $$f_0 = 5\text{ kHz} \times \sqrt{\frac{64}{25}} = 5 \times \frac{8}{5} = \mathbf{8\text{ kHz}}$$
   - 諧振時感抗：$X_{L0} = 25 \times \frac{8}{5} = 40\ \Omega$
   - 品質因數：
     $$\mathbf{Q = \frac{X_{L0}}{R} = \frac{40}{10} = 4}$$
2. **諧振時各元件端電壓峰值（$V_m = 100\text{ V}$）**：
   - 電阻電壓：$V_{R,m} = V_m = \mathbf{100\text{ V}}$
   - 電感與電容電壓：
     $$\mathbf{V_{L,m} = V_{C,m} = Q \cdot V_m = 4 \times 100 = 400\text{ V}}$$
3. **使 $v_C(t)$ 與 $v_L(t)$ 達最大之頻率與峰值**：
   - 電容最大頻率：
     $$\mathbf{f_C^* = f_0 \sqrt{1 - \frac{1}{2Q^2}} = 8000 \times \sqrt{1 - \frac{1}{32}} = 8000 \times 0.9842 = 7873.8\text{ Hz} = 7.874\text{ kHz}}$$
   - 電感最大頻率：
     $$\mathbf{f_L^* = \frac{f_0}{\sqrt{1 - \frac{1}{2Q^2}}} = \frac{8000}{0.9842} = 8128.2\text{ Hz} = 8.128\text{ kHz}}$$
   - 最大電壓峰值：
     $$\mathbf{V_{C,max} = V_{L,max} = \frac{100 \times 4}{\sqrt{1 - \frac{1}{64}}} = \frac{400}{\sqrt{0.984375}} = 403.17\text{ V}}$$

---

### 🎯 第三題 滿分關鍵與結論
- **諧振頻率與品質因數**：$f_0 = \mathbf{8\text{ kHz}}, \quad Q = \mathbf{4}$
- **諧振時電壓峰值**：$V_{R,m} = \mathbf{100\text{ V}}, \quad V_{L,m} = V_{C,m} = \mathbf{400\text{ V}}$
- **最大電壓頻率與峰值**：  
  $f_C^* = \mathbf{7.874\text{ kHz}}, \quad f_L^* = \mathbf{8.128\text{ kHz}}, \quad V_{max} = \mathbf{403.17\text{ V}}$

---

## 四、Y-Y 接不平衡三相四線制負載總功率計算（25 分）

### 📌 題目與已知條件
在 Y-Y 接不平衡三相四線制系統中，平衡三相正相序線電壓為：
$$\mathbf{V}_{ab} = 208\angle 0^\circ\text{ V}_{rms}, \quad \mathbf{V}_{bc} = 208\angle -120^\circ\text{ V}_{rms}, \quad \mathbf{V}_{ca} = 208\angle 120^\circ\text{ V}_{rms}$$
不平衡 Y 接三相負載阻抗為：
$$\mathbf{Z}_{an} = 8\angle 30^\circ\ \Omega, \quad \mathbf{Z}_{bn} = 5\angle -50^\circ\ \Omega, \quad \mathbf{Z}_{cn} = 6\angle 20^\circ\ \Omega$$
試求該 Y 接三相負載消耗之總平均功率 $P_T$。

---

### 💡 核心考點與破題關鍵
1. **三相四線制相電壓計算**：
   - 由於中性線存在且理想，各相負載端電壓即為平衡相電壓：
     $$V_\phi = \frac{V_L}{\sqrt{3}} = \frac{208}{\sqrt{3}} = 120.09\text{ V}_{rms}$$
     $$\mathbf{V}_{an} = 120.09\angle -30^\circ\text{ V}_{rms}$$
     $$\mathbf{V}_{bn} = 120.09\angle -150^\circ\text{ V}_{rms}$$
     $$\mathbf{V}_{cn} = 120.09\angle 90^\circ\text{ V}_{rms}$$
2. **每相平均功率公式**：
   $$P_\phi = \frac{|\mathbf{V}_\phi|^2}{|\mathbf{Z}_\phi|} \cos\theta_\phi$$
   $$P_T = P_a + P_b + P_c$$

---

### ✏️ 步驟式詳細數學推導
1. **計算 A 相消耗平均功率**：
   - 負載阻抗：$\mathbf{Z}_{an} = 8\angle 30^\circ\ \Omega$（阻抗角 $\theta_a = 30^\circ$）
   $$P_a = \frac{V_\phi^2}{|\mathbf{Z}_{an}|}\cos\theta_a = \frac{120.09^2}{8}\cos 30^\circ = \frac{14421.6}{8} \times 0.8660 = 1802.7 \times 0.8660 = \mathbf{1561.18\text{ W}}$$
2. **計算 B 相消耗平均功率**：
   - 負載阻抗：$\mathbf{Z}_{bn} = 5\angle -50^\circ\ \Omega$（阻抗角 $\theta_b = -50^\circ$）
   $$P_b = \frac{V_\phi^2}{|\mathbf{Z}_{bn}|}\cos\theta_b = \frac{14421.6}{5}\cos(-50^\circ) = 2884.32 \times 0.6428 = \mathbf{1854.01\text{ W}}$$
3. **計算 C 相消耗平均功率**：
   - 負載阻抗：$\mathbf{Z}_{cn} = 6\angle 20^\circ\ \Omega$（阻抗角 $\theta_c = 20^\circ$）
   $$P_c = \frac{V_\phi^2}{|\mathbf{Z}_{cn}|}\cos\theta_c = \frac{14421.6}{6}\cos 20^\circ = 2403.6 \times 0.9397 = \mathbf{2258.64\text{ W}}$$
4. **計算三相總平均功率 $P_T$**：
   $$\mathbf{P_T = P_a + P_b + P_c = 1561.18 + 1854.01 + 2258.64 = 5673.83\text{ W} = 5.674\text{ kW}}$$

---

### 🎯 第四題 滿分關鍵與結論
- **各相消耗功率**：$P_a = \mathbf{1.561\text{ kW}}, \quad P_b = \mathbf{1.854\text{ kW}}, \quad P_c = \mathbf{2.259\text{ kW}}$
- **三相負載總平均功率**：$P_T = \mathbf{5673.83\text{ W} = 5.674\text{ kW}}$
"""

# Write 111 and 110
with open(os.path.join(out_dir, "111年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_111)
with open(os.path.join(out_dir, "110年_電路學_全卷完整詳細題解.md"), "w", encoding="utf-8") as f:
    f.write(sol_110)

print("✅ Generated: 111年 & 110年 電路學全卷詳解")
