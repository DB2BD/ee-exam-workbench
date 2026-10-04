# ⚡ 電子學 核心考點 01 — BJT 與 MOSFET 小訊號分析

## 📌 核心參數與小訊號模型
1. **BJT 小訊號參數**：
   - 轉導（Transconductance）：$g_m = \frac{I_C}{V_T} \approx \frac{I_C}{25\text{ mV}}$
   - 輸入電阻：$r_\pi = \frac{\beta}{g_m} = \frac{V_T}{I_B}, \quad r_e = \frac{\alpha}{g_m} = \frac{r_\pi}{1 + \beta} \approx \frac{1}{g_m}$
   - 輸出電阻（厄利效應 Early Effect）：$r_o = \frac{V_A + V_{CE}}{I_C} \approx \frac{V_A}{I_C}$
2. **MOSFET 小訊號參數**：
   - 飽和區汲極電流：$I_D = \frac{1}{2} k_n' \left( \frac{W}{L} \right) (V_{GS} - V_{tn})^2 (1 + \lambda V_{DS})$
   - 轉導：$g_m = \sqrt{2 k_n' \left( \frac{W}{L} \right) I_D} = \frac{2I_D}{V_{ov}} = k_n' \left( \frac{W}{L} \right) V_{ov}$
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
