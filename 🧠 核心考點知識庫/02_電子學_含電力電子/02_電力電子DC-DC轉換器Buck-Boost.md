# ⚡ 電子學（含電力電子）核心考點 02 — DC-DC 降壓/升壓/升降壓轉換器

## 📌 核心解題 SOP
1. **降壓轉換器（Buck Converter）**：
   - 輸出電壓：$V_o = D V_s$
   - 電感漣波電流：\Delta I_L = \frac{V_s - V_o}{L} D T = \frac{V_o (1 - D)}{L f}
   - 輸出漣波電壓：\Delta V_o = \frac{\Delta Q}{C} = \frac{\Delta I_L}{8 C f} = \frac{V_o (1 - D)}{8 L C f^2}
   - 連續導通邊界電感：L_{\text{min}} = \frac{(1 - D) R}{2 f}
2. **升壓轉換器（Boost Converter）**：
   - 輸出電壓：V_o = \frac{V_s}{1 - D}
   - 電感漣波電流：\Delta I_L = \frac{V_s D}{L f}
   - 輸出漣波電壓：\Delta V_o = \frac{I_o D}{C f} = \frac{V_o D}{R C f}
   - 連續導通邊界電感：L_{\text{min}} = \frac{D (1 - D)^2 R}{2 f}
3. **升降壓轉換器（Buck-Boost Converter）**：
   - 輸出電壓（極性反向）：V_o = -\frac{D}{1 - D} V_s
   - 連續導通邊界電感：L_{\text{min}} = \frac{(1 - D)^2 R}{2 f}

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：Buck 轉換器臨界電感與輸出濾波電容設計。
- **113 年 第一題**：Boost 轉換器 CCM/DCM 邊界條件與效率計算。
- **110 年 第一題**：Buck-Boost 電路狀態空間平均法與小訊號建模。
