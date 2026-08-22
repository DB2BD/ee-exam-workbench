# -*- coding: utf-8 -*-
import os

os.makedirs('📝 個人題解與錯題本/05_電力系統', exist_ok=True)

# 113 年 電力系統 全卷完整詳細題解
sol_113 = r'''---
aliases: [113年電力系統技師題解, 113電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 113年]
created: 2026-08-16
subject: 電力系統
year: 113
---

# ⚡ 113 年 專門職業及技術人員高等考試 — 電力系統 全卷詳細題解

> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01120`  
> **滿分**：100 分（共 4 大題，各 25 分）

---

## 📑 113 年 全卷題解目錄導覽

* [[#一、三相並聯負載阻抗與複數功率分析|📌 第一題：三相並聯負載等效阻抗、線電流與複數功率計算（25 分）]]
* [[#二、同步機與輸電線路三相短路故障暫態電流|📌 第二題：同步發電機與電動機三相短路次暫態電流求解（25 分）]]
* [[#三、二發電機組等微增燃料成本最佳經濟調度|📌 第三題：二發電機最佳經濟調度與燃料成本係數反求（25 分）]]
* [[#四、同步發電機調速機速度調節率與頻率響應|📌 第四題：調速機速度調節率（Speed Regulation）與頻率偏移（25 分）]]

---

## 一、三相並聯負載阻抗與複數功率分析

### 📌 題目與已知條件
如下圖所示，為由一個三相平衡電源供電給兩個並聯三相負載之架構：
* 三相平衡電源線電壓大小：$V_L = 210\text{ V}$（有效值 rms）。
* 線路每相阻抗：$Z_l = 1 + j1\ \Omega$。
* $\Delta$ 連接負載每相阻抗：$Z_\Delta = 24 - j30\ \Omega$。
* $\text{Y}$ 連接負載每相阻抗：$Z_Y = 12 + j5\ \Omega$。

**試求解**：
1. 由三相電源端看入之 $\text{Y}$ 連接合併負載之每相等效阻抗 $Z_{Y,\text{total}}$。
2. 流經該合併負載之線電流大小 $I_L$。
3. 由三相電源流入之總實功 $P$、總虛功 $Q$、總視在功率 $S$、總複數功率 $\mathbf{S}$ 及總功率因數 $\text{PF}$。（25 分）

---

### 💡 核心考點與破題關鍵
1. **$\Delta-\text{Y}$ 阻抗等效轉換**：
   $$\Delta \text{ 接阻抗轉為單相 } \text{Y} \text{ 接阻抗：} Z_{Y\Delta} = \frac{Z_\Delta}{3} = \frac{24 - j30}{3} = 8 - j10\ \Omega$$
2. **負載並聯等效**：
   $$Z_{load} = Z_{Y\Delta} \parallel Z_Y = \frac{(8 - j10)(12 + j5)}{(8 - j10) + (12 + j5)}$$
3. **包含傳輸線之每相總阻抗**：
   $$Z_{total} = Z_l + Z_{load} = (1 + j1) + Z_{load}$$
4. **單相分析法求線電流與三相總功率**：
   $$V_{ph} = \frac{210}{\sqrt{3}}\text{ V},\quad \mathbf{I}_L = \frac{V_{ph}\angle 0^\circ}{Z_{total}},\quad \mathbf{S}_{total} = 3 V_{ph} \mathbf{I}_L^* = \sqrt{3} V_L I_L \angle \theta$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解負載端 $\text{Y}$ 接等效阻抗 $Z_{load}$
* 將 $\Delta$ 接負載轉換為等效 $\text{Y}$ 接阻抗：
  $$Z_{Y\Delta} = \frac{Z_\Delta}{3} = \frac{24 - j30}{3} = 8 - j10\ \Omega$$
* 二負載並聯後之每相負載阻抗 $Z_{load}$：
  $$Z_{load} = \frac{Z_{Y\Delta} \cdot Z_Y}{Z_{Y\Delta} + Z_Y} = \frac{(8 - j10)(12 + j5)}{(8 - j10) + (12 + j5)} = \frac{(96 + 50) + j(-120 + 40)}{20 - j5} = \frac{146 - j80}{20 - j5}$$
  分子分母同乘共軛數 $(20 + j5)$：
  $$Z_{load} = \frac{(146 - j80)(20 + j5)}{20^2 + (-5)^2} = \frac{(2920 + 400) + j(730 - 1600)}{425} = \frac{3320 - j870}{425} \approx 7.8118 - j2.0471\ \Omega$$

#### 步驟 2：求解包含線路阻抗之電源端總等效阻抗 $Z_{total}$
$$Z_{total} = Z_l + Z_{load} = (1 + j1) + (7.8118 - j2.0471) = 8.8118 - j1.0471\ \Omega$$
轉為極座標形式：
$$|Z_{total}| = \sqrt{8.8118^2 + (-1.0471)^2} = \sqrt{77.6478 + 1.0964} = \sqrt{78.7442} \approx 8.8738\ \Omega$$
$$\theta_Z = \tan^{-1}\left(\frac{-1.0471}{8.8118}\right) \approx -6.780^\circ$$
$$Z_{total} = 8.8738\angle -6.780^\circ\ \Omega$$

#### 步驟 3：求解電源線電流大小 $I_L$
電源相電壓大小為：
$$V_{ph} = \frac{V_L}{\sqrt{3}} = \frac{210}{\sqrt{3}} \approx 121.2436\text{ V}$$
取相電壓為參考相量 $\mathbf{V}_{an} = 121.2436\angle 0^\circ\text{ V}$：
$$\mathbf{I}_a = \frac{\mathbf{V}_{an}}{Z_{total}} = \frac{121.2436\angle 0^\circ}{8.8738\angle -6.780^\circ} = 13.6631\angle +6.780^\circ\text{ A}$$
故線電流大小為：
$$\mathbf{I}_L = 13.663\text{ A}$$

#### 步驟 4：求解電源端送出之各項功率與功率因數
1. **總視在功率 $S$**：
   $$S = \sqrt{3} V_L I_L = \sqrt{3} \times 210 \times 13.6631 = 4970.07\text{ VA} \approx 4.970\text{ kVA}$$
2. **總功率因數 $\text{PF}$**：
   $$\text{PF} = \cos(-6.780^\circ) \approx 0.9930\quad (\text{超前 Leading，因負載呈現容性})$$
3. **總實功率 $P$**：
   $$P = S \cos\theta = 4970.07 \times 0.9930 \approx 4935.28\text{ W} = 4.935\text{ kW}$$
4. **總虛功率 $Q$**：
   $$Q = S \sin\theta = 4970.07 \times \sin(-6.780^\circ) = -586.82\text{ var} = -0.587\text{ kvar}\quad (\text{提供容性虛功})$$
5. **總複數功率 $\mathbf{S}$**：
   $$\mathbf{S} = P + jQ = 4935.28 - j586.82\text{ VA} = 4970.07\angle -6.780^\circ\text{ VA}$$

---

### ⚠️ 考場陷阱與評分避坑指南
1. **$\Delta$ 轉 $\text{Y}$ 阻抗必須除以 3**：$Z_Y = Z_\Delta / 3$，許多考生考試緊張忘記除以 3 直接並聯，導致全題失分！
2. **線電壓轉相電壓需除以 $\sqrt{3}$**：計算單相迴路電流時，電壓必須代入相電壓 $210/\sqrt{3}$。
3. **功率因數必須註明「超前」或「滯後」**：阻抗虛部為負，電流相位領先電壓，務必明確寫出 $\text{Leading}$（超前）。

---

## 二、同步機與輸電線路三相短路故障暫態電流

### 📌 題目與已知條件
* **同步發電機 G**：額定三相 $100\text{ MVA}, 24\text{ kV}, 60\text{ Hz}$，次暫態電抗 $X_d'' = 0.25\text{ pu}$。
* **輸電線路 TL**：電抗 $X_{line} = 0.10\text{ pu}$（基準值 $100\text{ MVA}, 24\text{ kV}$）。
* **同步電動機 M**：額定三相 $100\text{ MVA}, 24\text{ kV}, 60\text{ Hz}$，次暫態電抗 $X_d'' = 0.20\text{ pu}$。
* **故障前運轉條件**：電動機端電壓 $V_m = 20\text{ kV}$，吸收功率 $P_m = 50\text{ MW}$，功率因數 $\text{PF} = 0.8\text{ 超前}$。
* **故障事件**：在發電機端點發生三相短路故障。

**試求**：每一部電機之次暫態電流及短路點之總次暫態電流。（25 分）

---

### 💡 核心考點與破題關鍵
1. **基準值設定**：
   選定系統基準值 $S_{base} = 100\text{ MVA}, V_{base} = 24\text{ kV}$。
   $$I_{base} = \frac{S_{base}}{\sqrt{3} V_{base}} = \frac{100\times 10^6}{\sqrt{3} \times 24\times 10^3} = 2405.63\text{ A}$$
2. **故障前電動機端標么值**：
   $$V_{m,pu} = \frac{20\text{ kV}}{24\text{ kV}} = 0.8333\angle 0^\circ\text{ pu}$$
   $$P_{m,pu} = \frac{50\text{ MW}}{100\text{ MVA}} = 0.50\text{ pu},\quad S_{m,pu} = \frac{0.50}{0.8} = 0.625\text{ pu}$$
   $$\mathbf{I}_{L0} = \left(\frac{\mathbf{S}_m}{\mathbf{V}_m}\right)^* = \frac{0.625\angle -36.87^\circ}{0.8333\angle 0^\circ} = 0.75\angle +36.87^\circ\text{ pu} = 0.60 + j0.45\text{ pu}$$
3. **故障內部電勢模型**：
   * 發電機故障內部電勢：$E_g'' = V_{t0} + j X_{dg}'' \mathbf{I}_{L0}$
   * 電動機故障內部電勢：$E_m'' = V_{m0} - j X_{dm}'' \mathbf{I}_{L0}$
4. **各機提供至短路點之次暫態電流**：
   $$I_g'' = \frac{E_g''}{j X_{dg}''},\quad I_m'' = \frac{E_m''}{j(X_{dm}'' + X_{line})},\quad I_f'' = I_g'' + I_m''$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求故障前發電機端電壓 $\mathbf{V}_{t0}$
$$\mathbf{V}_{t0} = \mathbf{V}_{m0} + \mathbf{I}_{L0} (j X_{line}) = 0.8333\angle 0^\circ + (0.60 + j0.45)(j0.10) = 0.8333 + (-0.045 + j0.060) = 0.7883 + j0.060\text{ pu}$$

#### 步驟 2：求解發電機內部次暫態電勢 $E_g''$ 與電流 $I_g''$
$$E_g'' = \mathbf{V}_{t0} + j X_{dg}'' \mathbf{I}_{L0} = (0.7883 + j0.060) + j0.25(0.60 + j0.45) = (0.7883 - 0.1125) + j(0.060 + 0.150) = 0.6758 + j0.210\text{ pu}$$
當發電機端發生三相短路（$V_f = 0$）：
$$\mathbf{I}_g'' = \frac{E_g''}{j X_{dg}''} = \frac{0.6758 + j0.210}{j0.25} = 0.840 - j2.7032\text{ pu} \approx 2.8306\angle -72.73^\circ\text{ pu}$$
實體值：
$$I_g'' = 2.8306 \times 2405.63\text{ A} = 6809.3\text{ A} = 6.809\text{ kA}$$

#### 步驟 3：求解電動機內部次暫態電勢 $E_m''$ 與電流 $I_m''$
$$E_m'' = \mathbf{V}_{m0} - j X_{dm}'' \mathbf{I}_{L0} = 0.8333 - j0.20(0.60 + j0.45) = 0.8333 - (-0.090 + j0.120) = 0.9233 - j0.120\text{ pu}$$
電動機至故障點之總阻抗為 $j(X_{dm}'' + X_{line}) = j(0.20 + 0.10) = j0.30\text{ pu}$：
$$\mathbf{I}_m'' = \frac{E_m''}{j0.30} = \frac{0.9233 - j0.120}{j0.30} = -0.40 - j3.0777\text{ pu} \approx 3.1036\angle -97.41^\circ\text{ pu}$$
實體值：
$$I_m'' = 3.1036 \times 2405.63\text{ A} = 7466.1\text{ A} = 7.466\text{ kA}$$

#### 步驟 4：求解短路故障點總電流 $I_f''$
$$\mathbf{I}_f'' = \mathbf{I}_g'' + \mathbf{I}_m'' = (0.840 - j2.7032) + (-0.40 - j3.0777) = 0.440 - j5.7809\text{ pu} \approx 5.7976\angle -85.65^\circ\text{ pu}$$
實體總短路電流：
$$I_f'' = 5.7976 \times 2405.63\text{ A} = 13946.8\text{ A} = 13.947\text{ kA}$$

---

## 三、二發電機組等微增燃料成本最佳經濟調度

### 📌 題目與已知條件
* 機組 1 燃料成本函數：$C_1 = 500 + 8 P_1 + 0.005 P_1^2\quad (\$/\text{h})$
* 機組 2 燃料成本函數：$C_2 = 700 + \alpha P_2 + \beta P_2^2\quad (\$/\text{h})$
* 兩機組額定容量均為 $1300\text{ MW}$。忽略輸電線損失（$P_L = 0$）。
* **條件 1**：當總負載需求 $P_{D1} = 800\text{ MW}$ 時，系統增量成本 $\lambda_1 = 10\ \$/\text{MWh}$。
* **條件 2**：當總負載需求 $P_{D2} = 1500\text{ MW}$ 時，系統增量成本 $\lambda_2 = 12\ \$/\text{MWh}$。

**試求**：未知的成本係數 $\alpha$ 與 $\beta$ 之值。（25 分）

---

### 💡 核心考點與破題關鍵
1. **等微增燃料成本準則（Equal Incremental Cost）**：
   $$\lambda = \frac{dC_1}{dP_1} = \frac{dC_2}{dP_2}$$
2. **機組微增成本方程式**：
   $$\frac{dC_1}{dP_1} = 8 + 0.01 P_1 = \lambda \implies P_1 = \frac{\lambda - 8}{0.01} = 100(\lambda - 8)$$
   $$\frac{dC_2}{dP_2} = \alpha + 2\beta P_2 = \lambda \implies P_2 = \frac{\lambda - \alpha}{2\beta}$$
3. **功率平衡條件**：
   $$P_1 + P_2 = P_D \implies P_2 = P_D - P_1$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：利用條件 1（$P_D = 800\text{ MW}, \lambda = 10\ \$/\text{MWh}$）
* 計算機組 1 出力 $P_1^{(1)}$：
  $$P_1^{(1)} = 100(10 - 8) = 200\text{ MW}$$
* 計算機組 2 出力 $P_2^{(1)}$：
  $$P_2^{(1)} = P_{D1} - P_1^{(1)} = 800 - 200 = 600\text{ MW}$$
* 代入機組 2 微增成本式：
  $$\alpha + 2\beta(600) = 10 \implies \alpha + 1200\beta = 10\quad \text{--- (方程式 1)}$$

#### 步驟 2：利用條件 2（$P_D = 1500\text{ MW}, \lambda = 12\ \$/\text{MWh}$）
* 計算機組 1 出力 $P_1^{(2)}$：
  $$P_1^{(2)} = 100(12 - 8) = 400\text{ MW}$$
* 計算機組 2 出力 $P_2^{(2)}$：
  $$P_2^{(2)} = P_{D2} - P_1^{(2)} = 1500 - 400 = 1100\text{ MW}$$
* 代入機組 2 微增成本式：
  $$\alpha + 2\beta(1100) = 12 \implies \alpha + 2200\beta = 12\quad \text{--- (方程式 2)}$$

#### 步驟 3：解聯立方程式求解 $\alpha, \beta$
將 (方程式 2) 減去 (方程式 1)：
$$(2200 - 1200)\beta = 12 - 10 \implies 1000\beta = 2 \implies \beta = 0.002$$
將 $\beta = 0.002$ 代回 (方程式 1)：
$$\alpha + 1200(0.002) = 10 \implies \alpha + 2.4 = 10 \implies \alpha = 7.6$$

#### 步驟 4：驗證機組出力未超出容量上限
* 在 $1500\text{ MW}$ 負載時：$P_1 = 400\text{ MW} \le 1300\text{ MW}$，$P_2 = 1100\text{ MW} \le 1300\text{ MW}$，均在安全運轉容量內。

**最終結果**：
$$\alpha = 7.6\ \$/\text{MWh},\quad \beta = 0.002\ \$/\text{MW}^2\text{h}$$

---

## 四、同步發電機調速機速度調節率與頻率響應

### 📌 題目與已知條件
* 同步發電機額定容量：$S_{base} = 500\text{ MW}$，額定頻率 $f_0 = 60\text{ Hz}$。
* 調速機速度調節率（Speed Regulation）：$R = 0.05\text{ pu}$。
* 調節率關係式：
  $$\frac{\Delta \omega}{\omega_0} = \frac{\Delta f}{f_0} = -R \Delta P_m\quad (\Delta P_m \text{ 單位為標么 pu})$$

**試求**：
1. 當發電機頻率由 $60\text{ Hz}$ 降至 $59\text{ Hz}$ 時，發電機機械輸入功率 $\Delta P_m$ 的增加量（以 pu 及 MW 表示）。（12 分）
2. 該發電機之機械輸入功率 $P_m$ 由無載（$0\text{ pu}$）變化至滿載（$1.0\text{ pu}$）時的頻率變動範圍（$\text{Hz}$）。（13 分）

---

### 💡 核心考點與破題關鍵
1. **頻率偏差與功率增量關係**：
   $$\Delta f = -R f_0 \Delta P_{m,pu} \implies \Delta P_{m,pu} = -\frac{1}{R} \frac{\Delta f}{f_0}$$
2. **滿載頻降量（Full-Load Droop）**：
   $$\Delta f_{\text{full}} = -R f_0 \times 1.0 = -0.05 \times 60 = -3.0\text{ Hz}$$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解頻率降至 $59\text{ Hz}$ 時之功率增加量
* 頻率變動量：
  $$\Delta f = 59 - 60 = -1.0\text{ Hz}$$
* 標么頻率變動量：
  $$\frac{\Delta f}{f_0} = \frac{-1.0}{60} = -\frac{1}{60}\text{ pu}$$
* 代入調速機特性公式：
  $$\Delta P_{m,pu} = -\frac{1}{R}\left(\frac{\Delta f}{f_0}\right) = -\frac{1}{0.05}\left(-\frac{1}{60}\right) = \frac{20}{60} = \frac{1}{3}\text{ pu} \approx 0.3333\text{ pu}$$
* 轉換為實體功率增加量（$\text{MW}$）：
  $$\Delta P_m = \Delta P_{m,pu} \times S_{base} = \frac{1}{3} \times 500\text{ MW} \approx 166.67\text{ MW}$$

#### 步驟 2：求解由無載至滿載之頻率變動範圍
* **無載狀態（$P_m = 0\text{ pu}$）**：
  發電機運轉於額定空載頻率 $f_{\text{no-load}} = 60.0\text{ Hz}$。
* **滿載狀態（$P_m = 1.0\text{ pu}$）**：
  $$\Delta P_m = 1.0 - 0 = 1.0\text{ pu}$$
  $$\Delta f = -R f_0 \Delta P_m = -0.05 \times 60 \times 1.0 = -3.0\text{ Hz}$$
  故滿載時的頻率為：
  $$f_{\text{full-load}} = 60.0 - 3.0 = 57.0\text{ Hz}$$
* **頻率變動範圍**：
  $$\text{頻率變動範圍為：} 57.0\text{ Hz} \sim 60.0\text{ Hz}\quad (\text{變動量 } \Delta f = 3.0\text{ Hz})$$

---

### 🎯 總結評分要點
| 題號 | 核心考點 | 最終正確答案 |
| :---: | :--- | :--- |
| **一** | 三相並聯等效阻抗與功率 | $Z_{load} = 7.812 - j2.047\ \Omega, I_L = 13.66\text{ A}, \mathbf{S} = 4935 - j587\text{ VA}, \text{PF} = 0.993\text{ (超前)}$ |
| **二** | 同步機三相短路次暫態電流 | $I_g'' = 6.809\text{ kA}, I_m'' = 7.466\text{ kA}, I_f'' = 13.947\text{ kA}$ |
| **三** | 等微增成本經濟調度 | $\alpha = 7.6\ \$/\text{MWh}, \beta = 0.002\ \$/\text{MW}^2\text{h}$ |
| **四** | 調速機特性與頻率響應 | $\Delta P_m = 0.333\text{ pu} (166.67\text{ MW})$, 頻率範圍 $57.0\text{ Hz} \sim 60.0\text{ Hz}$ |
'''

with open('📝 個人題解與錯題本/05_電力系統/113年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_113)

print('✅ 113年_電力系統_全卷完整詳細題解.md created!')
