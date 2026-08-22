# ⚡ 電子學（含電力電子） 核心考點 02 — DC-DC 轉換器

## 📌 核心穩態原理（連續導通模式 CCM）
1. **電感伏秒平衡原理（Inductor Volt-Second Balance）**：
   \int_0^{T_s} v_L(t) dt = 0 \implies V_{L,\text{on}} \cdot D T_s + V_{L,\text{off}} \cdot (1-D) T_s = 0
2. **電容安秒平衡原理（Capacitor Charge Balance）**：
   \int_0^{T_s} i_C(t) dt = 0 \implies I_{C,\text{on}} \cdot D T_s + I_{C,\text{off}} \cdot (1-D) T_s = 0
3. **三大非隔離轉換器電壓轉換比與臨界電感 $L_{\text{crit}}$**：
   - **降壓轉換器（Buck Converter）**：
     V_o = D V_s, \quad \Delta I_L = \frac{(V_s - V_o) D}{f_s L}, \quad L_{\text{crit}} = \frac{(1-D) R}{2 f_s}
   - **升壓轉換器（Boost Converter）**：
     V_o = \frac{V_s}{1 - D}, \quad \Delta I_L = \frac{V_s D}{f_s L}, \quad L_{\text{crit}} = \frac{D (1-D)^2 R}{2 f_s}
   - **升降壓轉換器（Buck-Boost Converter）**：
     V_o = -\frac{D}{1 - D} V_s, \quad \Delta I_L = \frac{V_s D}{f_s L}, \quad L_{\text{crit}} = \frac{(1-D)^2 R}{2 f_s}

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第四題**：Boost 升壓轉換器輸出漣波電壓與電感電容選定。
- **112 年 第四題**：Buck 降壓轉換器連續/不連續導通模式（CCM/DCM）臨界邊界分析。
- **110 年 第四題**：單相全橋反流器（Inverter）PWM 調變指數與輸出諧波分析。
