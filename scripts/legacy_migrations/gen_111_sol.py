# -*- coding: utf-8 -*-
import os

# 111 年 電力系統
sol_111 = r'''---
aliases: [111年電力系統技師題解, 111電力系統詳解]
tags: [國考, 電機工程技師, 電力系統, 歷屆題解, 111年]
created: 2026-08-16
subject: 電力系統
year: 111
---

# ⚡ 111 年 專門職業及技術人員高等考試 — 電力系統 全卷詳細題解

> **類科**：電機工程技師  
> **科目**：電力系統（Power Systems）  
> **考試時間**：2 小時（120 分鐘）  
> **試題代號**：`01140`  
> **滿分**：100 分（共 4 大題，各 25 分）

---

## 📑 111 年 全卷題解目錄導覽

* [[#一、輸電線路串聯電容補償原理與功用|📌 第一題：輸電線路串聯電容補償（Series Compensation）與最大傳輸容量（25 分）]]
* [[#二、五匯流排阻抗矩陣 Zbus 三相短路故障計算|📌 第二題：五匯流排阻抗矩陣 $\mathbf{Z}_{bus}$ 三相短路節點電壓與故障電流（25 分）]]
* [[#三、等面積準則臨界清除角與臨界清除時間|📌 第三題：暫態穩定度臨界清除角 $\delta_{cr}$ 與臨界清除時間 $t_{cr}$（25 分）]]
* [[#四、長程輸電線路 ABCD 參數與電壓調整率|📌 第四題：483 公里長程輸電線 $\text{ABCD}$ 參數、費蘭梯效應與滿載調整率（25 分）]]

---

## 一、輸電線路串聯電容補償原理與功用

### 📌 題目與已知條件
1. 何謂輸電線路之串聯補償？（15 分）
2. 試說明有串聯補償相對於未經補償的輸電線路，能增加線路最大傳送實功率的原因。（10 分）

---

### ✏️ 完整標準解答與推導

#### (一) 何謂輸電線路之串聯補償？
* **定義**：在長距離高壓/超高壓交流輸電線路中，將**串聯電容器組（Series Capacitor Bank）**直接串聯於傳輸線相導線中，以抵消部分線路感抗 $X_L$ 的補償技術。
* **串聯補償度（Degree of Compensation, $k_c$）**定義為：
  $$k_c = \frac{X_C}{X_L} \times 100\%$$
  工程實務上補償度通常設定於 $20\% \sim 70\%$ 之間，避免 $100\%$ 補償導致次同步諧振（Subsynchronous Resonance, SSR）。
* **主要目的**：
  1. 降低線路總等效串聯感抗 $X_{eff} = X_L - X_C$。
  2. 縮短輸電線的電氣長度（Electrical Length），改善系統動態與暫態穩定度。
  3. 降低線路之無效功率損失（$I^2 X$）。

#### (二) 增加線路最大傳送實功率的原因分析
* **功率傳輸方程式**：
  未補償前輸電線之實功率傳輸公式為：
  $$P = \frac{|V_S||V_R|}{X_L} \sin\delta \implies P_{max} = \frac{|V_S||V_R|}{X_L}$$
* **加裝串聯電容後**：
  線路總等效電抗降為 $X_{eff} = X_L(1 - k_c)$，最大實功傳送能力提高為：
  $$P_{max,comp} = \frac{|V_S||V_R|}{X_L(1 - k_c)} = \frac{1}{1 - k_c} P_{max}$$
  例如當補償度 $k_c = 50\%$ 時，$P_{max,comp} = \frac{1}{1 - 0.5} P_{max} = 2.0 P_{max}$，**線路最大實功率傳送容量提升為原來的 2 倍（增加 100%）**！

---

## 二、五匯流排阻抗矩陣 Zbus 三相短路故障計算

### 📌 題目與已知條件
* 系統阻抗矩陣 $\mathbf{Z}_{bus}$ 已知，故障前所有匯流排電壓均為 $V_f = 1.0\angle 0^\circ\text{ pu}$。
* 匯流排 5 發生直接三相接地短路故障（$Z_f = 0$）。
* 匯流排 5 之驅動點阻抗 $Z_{55} = j0.160\text{ pu}$，轉移阻抗 $Z_{35} = j0.080\text{ pu}$。
* 輸電線 1-2 阻抗 $z_{12} = j0.10\text{ pu}$，$Z_{15} = j0.050\text{ pu}, Z_{25} = j0.070\text{ pu}$。

**試求**：
1. 匯流排 3 於故障期間之電壓標么值 $V_3^{(f)}$。
2. 從匯流排 2 流至匯流排 1 之故障電流標么值 $I_{21}^{(f)}$。（25 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解故障點（Bus 5）之總短路電流 $I_f$
$$I_f = \frac{V_f}{Z_{55} + Z_f} = \frac{1.0\angle 0^\circ}{j0.160} = -j6.25\text{ pu}$$

#### 步驟 2：求解故障期間各匯流排電壓 $V_k^{(f)} = V_k^{(0)} - Z_{k5} I_f$
* **匯流排 3 電壓**：
  $$V_3^{(f)} = 1.0 - Z_{35} I_f = 1.0 - (j0.080)(-j6.25) = 1.0 - (0.50) = 0.50\angle 0^\circ\text{ pu}$$
* **匯流排 1 電壓**：
  $$V_1^{(f)} = 1.0 - Z_{15} I_f = 1.0 - (j0.050)(-j6.25) = 1.0 - (0.3125) = 0.6875\text{ pu}$$
* **匯流排 2 電壓**：
  $$V_2^{(f)} = 1.0 - Z_{25} I_f = 1.0 - (j0.070)(-j6.25) = 1.0 - (0.4375) = 0.5625\text{ pu}$$

#### 步驟 3：求解由匯流排 2 流向匯流排 1 之線路電流 $I_{21}^{(f)}$
$$I_{21}^{(f)} = \frac{V_2^{(f)} - V_1^{(f)}}{z_{12}} = \frac{0.5625 - 0.6875}{j0.10} = \frac{-0.125}{j0.10} = j1.25\text{ pu} = 1.25\angle 90^\circ\text{ pu}$$

**結論**：
$$V_3^{(f)} = 0.50\text{ pu},\quad I_{21}^{(f)} = 1.25\angle 90^\circ\text{ pu}\quad (\text{大小 } 1.25\text{ pu})$$

---

## 三、等面積準則臨界清除角與臨界清除時間

### 📌 題目與已知條件
* 慣量常數 $H = 6.0\text{ MJ/MVA}$，頻率 $f = 60\text{ Hz}$。
* 機械輸入功率 $P_m = 1.0\text{ pu}$。
* 正常與故障清除後最大功率 $P_{max1} = P_{max3} = 2.5\text{ pu}$。
* 故障期間電氣輸出功率 $P_{e2} = 0$（發電機端三相短路）。

**試求**：臨界清除角 $\delta_{cr}$ 及臨界清除時間 $t_{cr}$。（25 分）

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解初始功率角 $\delta_0$ 與最大功率角 $\delta_{max}$
$$\delta_0 = \sin^{-1}\left(\frac{P_m}{P_{max1}}\right) = \sin^{-1}\left(\frac{1.0}{2.5}\right) = \sin^{-1}(0.4) = 23.578^\circ = 0.4115\text{ rad}$$
$$\delta_{max} = \pi - \delta_0 = 180^\circ - 23.578^\circ = 156.422^\circ = 2.7301\text{ rad}$$

#### 步驟 2：利用等面積準則求臨界清除角 $\delta_{cr}$
當 $P_{e2} = 0$ 時，臨界清除角公式簡化為：
$$\cos\delta_{cr} = \frac{P_m (\delta_{max} - \delta_0) + P_{max3}\cos\delta_{max}}{P_{max3}}$$
$$\cos\delta_{cr} = \frac{1.0(2.7301 - 0.4115) + 2.5\cos(156.422^\circ)}{2.5} = \frac{2.3186 + 2.5(-0.9165)}{2.5} = \frac{2.3186 - 2.2913}{2.5} = \frac{0.0273}{2.5} = 0.01092$$
$$\delta_{cr} = \cos^{-1}(0.01092) \approx 89.37^\circ = 1.5598\text{ rad}$$

#### 步驟 3：求解臨界清除時間 $t_{cr}$
在故障期間 $P_e = 0$，轉子加速度為定值：
$$\frac{d^2\delta}{dt^2} = \frac{\pi f}{H} P_m = \frac{\pi \times 60}{6.0} \times 1.0 = 10\pi\text{ rad/s}^2 \approx 31.4159\text{ rad/s}^2$$
積分兩次得功率角軌跡：
$$\delta(t) = \delta_0 + \frac{1}{2}\left(\frac{\pi f}{H} P_m\right) t^2$$
$$\delta_{cr} - \delta_0 = \frac{1}{2}(10\pi) t_{cr}^2 = 5\pi t_{cr}^2$$
$$t_{cr} = \sqrt{\frac{2(\delta_{cr} - \delta_0)}{10\pi}} = \sqrt{\frac{1.5598 - 0.4115}{5\pi}} = \sqrt{\frac{1.1483}{15.7080}} = \sqrt{0.07310} \approx 0.2704\text{ s}$$

**結論**：
$$\delta_{cr} = 89.37^\circ\quad (1.560\text{ rad}),\quad t_{cr} = 0.2704\text{ s}\quad (16.2\text{ cycles})$$

---

## 四、長程輸電線路 ABCD 參數與電壓調整率

### 📌 題目與已知條件
* 長度 $483\text{ km}$，$345\text{ kV}$ 輸電線路，負載 $S_R = 400\text{ MVA}, \text{PF} = 0.8\text{ 滯後}$。
* $\text{ABCD}$ 參數：
  $$A = D = 0.8685\angle 1.90^\circ,\quad B = 133.8\angle 79.1^\circ\ \Omega,\quad C = 0.00186\angle 90.4^\circ\ \text{S}$$
* 受電端線電壓 $V_{R,LL} = 345\text{ kV} \implies V_R = \frac{345}{\sqrt{3}} = 199.186\text{ kV}\angle 0^\circ$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解受電端電流相量 $\mathbf{I}_R$
$$I_R = \frac{400\times 10^6}{\sqrt{3} \times 345\times 10^3} = 669.37\text{ A}$$
$$\mathbf{I}_R = 669.37\angle -36.87^\circ\text{ A} = 0.66937\angle -36.87^\circ\text{ kA}$$

#### 步驟 2：求解滿載送電端相電壓 $V_S$ 與電流 $I_S$
$$\mathbf{V}_S = A \mathbf{V}_R + B \mathbf{I}_R = (0.8685\angle 1.90^\circ)(199.186\angle 0^\circ) + (133.8\angle 79.1^\circ)(0.66937\angle -36.87^\circ)$$
$$\mathbf{V}_S = 172.993\angle 1.90^\circ + 89.562\angle 42.23^\circ = (172.90 + j5.73) + (66.32 + j60.20) = 239.22 + j65.93\text{ kV} = 248.14\angle 15.41^\circ\text{ kV}$$
* 送電端線電壓：$V_{S,LL} = \sqrt{3} \times 248.14 = 429.79\text{ kV}$。
* **送電端電流 $\mathbf{I}_S$**：
  $$\mathbf{I}_S = C \mathbf{V}_R + D \mathbf{I}_R = (0.00186\angle 90.4^\circ)(199.186\angle 0^\circ) + (0.8685\angle 1.90^\circ)(0.66937\angle -36.87^\circ)$$
  $$\mathbf{I}_S = 0.3705\angle 90.4^\circ + 0.5813\angle -34.97^\circ = (-0.0026 + j0.3705) + (0.4764 - j0.3332) = 0.4738 + j0.0373\text{ kA} = 475.3\angle 4.50^\circ\text{ A}$$

#### 步驟 3：求解無載受電端電壓與電壓調整率 $\text{VR}$
無載時 $I_R = 0 \implies V_S = A V_{R,NL} \implies V_{R,NL} = \frac{V_S}{|A|}$：
$$V_{R,NL} = \frac{248.14\text{ kV}}{0.8685} = 285.71\text{ kV}\quad (\text{線電壓 } 494.86\text{ kV})$$
電壓調整率：
$$\text{VR} = \frac{V_{R,NL} - V_{R,FL}}{V_{R,FL}} \times 100\% = \frac{285.71 - 199.19}{199.19} \times 100\% = \frac{86.52}{199.19} \times 100\% \approx 43.44\%$$

**結論**：
$$V_S = 248.14\text{ kV}\angle 15.41^\circ\ (V_{S,LL} = 429.8\text{ kV}),\quad I_S = 475.3\text{ A},\quad \text{VR} = 43.44\%$$
'''

with open('📝 個人題解與錯題本/05_電力系統/111年_電力系統_全卷完整詳細題解.md', 'w', encoding='utf-8') as f:
    f.write(sol_111)

print('✅ 111年_電力系統_全卷完整詳細題解.md created!')
