import os
import glob
import re

# 1. Create missing 02 and 06 Knowledge Base notes
kb_electronics = [
    {
        'file': '01_BJT與MOSFET小訊號交流分析.md',
        'title': 'BJT 與 MOSFET 小訊號交流分析與放大器組態',
        'content': r'''# ⚡ 電子學 核心考點 01 — BJT 與 MOSFET 小訊號分析

## 📌 核心參數與小訊號模型
1. **BJT 小訊號參數**：
   - 轉導（Transconductance）：$g_m = \frac{I_C}{V_T} \approx \frac{I_C}{25\text{ mV}}$
   - 輸入電阻：$r_\pi = \frac{\beta}{g_m} = \frac{V_T}{I_B}, \quad r_e = \frac{\alpha}{g_m} = \frac{r_\pi}{1 + \beta} \approx \frac{1}{g_m}$
   - 輸出電阻（厄利效應 Early Effect）：$r_o = \frac{V_A + V_{CE}}{I_C} \approx \frac{V_A}{I_C}$
2. **MOSFET 小訊號參數**：
   - 飽和區汲極電流：$I_D = \frac{1}{2} k_n' \left(\frac{W}{L}\right) (V_{GS} - V_{tn})^2 (1 + \lambda V_{DS})$
   - 轉導：$g_m = \sqrt{2 k_n' \left(\frac{W}{L}\right) I_D} = \frac{2I_D}{V_{ov}} = k_n' \left(\frac{W}{L}\right) V_{ov}$
   - 輸出電阻（通道長度調變 Channel-Length Modulation）：$r_o = \frac{1}{\lambda I_D} = \frac{V_A}{I_D}$
3. **三大基本放大器組態比較**：
   - **共射 / 共源（CE / CS）**：中等輸入阻抗、高電壓反向增益（$A_v \approx -g_m R_L'$）、中等輸出阻抗。
   - **共基 / 共閘（CB / CG）**：低輸入阻抗（$R_{in} \approx 1/g_m$）、高同向電壓增益（$A_v \approx g_m R_L'$）、高頻寬（無米勒效應 Miller Effect）。
   - **共集 / 共汲（CC / CD，射極/源極隨耦器 Emitter/Source Follower）**：高輸入阻抗、電壓增益略小於 1（$A_v \approx 1$）、低輸出阻抗（作緩衝器 Buffer 用）。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：MOSFET 差動對與主動負載小訊號增益計算。
- **113 年 第一題**：BJT 共射極放大器偏壓穩定度與交流頻率響應。
- **111 年 第二題**：MOSFET 多級放大器串級分析與輸入/輸出阻抗。
'''
    },
    {
        'file': '02_電力電子DC-DC轉換器Buck-Boost.md',
        'title': '電力電子：Buck, Boost 與 Buck-Boost 轉換器穩態分析',
        'content': r'''# ⚡ 電子學（含電力電子） 核心考點 02 — DC-DC 轉換器

## 📌 核心穩態原理（連續導通模式 CCM）
1. **電感伏秒平衡原理（Inductor Volt-Second Balance）**：
   $$\int_0^{T_s} v_L(t) dt = 0 \implies V_{L,\text{on}} \cdot D T_s + V_{L,\text{off}} \cdot (1-D) T_s = 0$$
2. **電容安秒平衡原理（Capacitor Charge Balance）**：
   $$\int_0^{T_s} i_C(t) dt = 0 \implies I_{C,\text{on}} \cdot D T_s + I_{C,\text{off}} \cdot (1-D) T_s = 0$$
3. **三大非隔離轉換器電壓轉換比與臨界電感 $L_{\text{crit}}$**：
   - **降壓轉換器（Buck Converter）**：
     $$V_o = D V_s, \quad \Delta I_L = \frac{(V_s - V_o) D}{f_s L}, \quad L_{\text{crit}} = \frac{(1-D) R}{2 f_s}$$
   - **升壓轉換器（Boost Converter）**：
     $$V_o = \frac{V_s}{1 - D}, \quad \Delta I_L = \frac{V_s D}{f_s L}, \quad L_{\text{crit}} = \frac{D (1-D)^2 R}{2 f_s}$$
   - **升降壓轉換器（Buck-Boost Converter）**：
     $$V_o = -\frac{D}{1 - D} V_s, \quad \Delta I_L = \frac{V_s D}{f_s L}, \quad L_{\text{crit}} = \frac{(1-D)^2 R}{2 f_s}$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第四題**：Boost 升壓轉換器輸出漣波電壓與電感電容選定。
- **112 年 第四題**：Buck 降壓轉換器連續/不連續導通模式（CCM/DCM）臨界邊界分析。
- **110 年 第四題**：單相全橋反流器（Inverter）PWM 調變指數與輸出諧波分析。
'''
    }
]

kb_distribution = [
    {
        'file': '01_工廠配電負載特性與契約容量.md',
        'title': '工廠配電：負載因數、需量因數、參差因數與契約容量',
        'content': r'''# ⚡ 工業配電 核心考點 01 — 負載特性與契約容量

## 📌 核心名詞定義與計算公式
1. **需量因數（Demand Factor, DF）**：
   $$\text{DF} = \frac{\text{最大需量 (Maximum Demand)}}{\text{總連接負載 (Connected Load)}} \le 1$$
2. **負載因數（Load Factor, LF）**：
   $$\text{LF} = \frac{\text{平均負載 (Average Load)}}{\text{最大需量 (Maximum Demand)}} = \frac{\text{總用電度數 (kWh)}}{\text{最大需量 (kW)} \times 24\text{ 小時} \times \text{天數}} \le 1$$
3. **參差因數（Diversity Factor, DivF）**：
   $$\text{DivF} = \frac{\sum \text{各個別負載之最大需量}}{\text{系統綜合最大需量}} \ge 1$$
4. **利用率（Utilization Factor, UF）**：
   $$\text{UF} = \frac{\text{最大需量}}{\text{供電設備額定容量 (如變壓器 kVA)}} \le 1$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：多用電戶群負載曲線、參差因數與主變壓器容量計算。
- **111 年 第一題**：需量因數與日負載因數改善對電費支出之評估。
'''
    },
    {
        'file': '02_短路電流計算與斷路器容量選定.md',
        'title': '工業配電：短路電流計算（標么法/歐姆法）與保護協調',
        'content': r'''# ⚡ 工業配電 核心考點 02 — 短路電流與保護協調

## 📌 核心計算公式
1. **短路容量（Short-Circuit MVA, SCMVA）與對稱短路電流**：
   $$I_{\text{sc}} = \frac{I_{\text{base}}}{Z_{\text{pu}}} = \frac{S_{\text{base}}}{\sqrt{3} V_{\text{base}} Z_{\text{pu}}} \quad [\text{kA}]$$
   $$\text{SCMVA} = \sqrt{3} V_{\text{base}} I_{\text{sc}} = \frac{S_{\text{base}}}{Z_{\text{pu}}} \quad [\text{MVA}]$$
2. **非對稱短路電流峰值（考慮直流分量 DC Offset）**：
   $$I_{\text{peak}} = \sqrt{2} K_{\text{asym}} I_{\text{sc}}, \quad \text{其中 } K_{\text{asym}} = \sqrt{1 + 2 e^{-2\pi / (X/R)}}$$
3. **過電流電驛（CO/LVP）保護協調階梯曲線**：
   - 始動電流標置（Tap Setting）：$I_{\text{pickup}} = \text{CT 比} \times \text{Tap}$
   - 時間乘率標置（Time Dial Setting, TDS）
   - 上下游電驛協調時間差（Coordination Time Interval, CTI $\approx 0.3 \sim 0.4\text{ 秒}$）。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：工廠 22.8 kV 轉 380 V 系統短路容量與 VCB 啟斷容量選定。
- **113 年 第二題**：過電流電驛 CO-8 反時限曲線保護協調階梯圖設定。
'''
    }
]

# Write KB files
os.makedirs('🧠 核心考點知識庫/02_電子學_含電力電子', exist_ok=True)
for item in kb_electronics:
    with open(f'🧠 核心考點知識庫/02_電子學_含電力電子/{item["file"]}', 'w', encoding='utf-8') as f:
        f.write(item['content'].strip() + '\n')

os.makedirs('🧠 核心考點知識庫/06_工業配電', exist_ok=True)
for item in kb_distribution:
    with open(f'🧠 核心考點知識庫/06_工業配電/{item["file"]}', 'w', encoding='utf-8') as f:
        f.write(item['content'].strip() + '\n')

print('Created missing KB folders and notes!')
