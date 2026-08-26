# -*- coding: utf-8 -*-
"""
rebuild_kb_math.py
==================
Standardizes all math formulas in 🧠 核心考點知識庫 with proper KaTeX delimiters.
"""

import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(WORKSPACE, '🧠 核心考點知識庫')

kb_updates = {
    '04_電機機械/01_變壓器等效電路與效率計算.md': r"""# ⚙️ 電機機械 核心考點 01 — 變壓器等效電路與效率分析

## 📌 核心解題 SOP
1. **等效電路參數試驗（Equivalent Circuit Tests）**：
   - **開路試驗（Open-Circuit Test, OC，低壓側加額定電壓）**：
     $$P_{oc} = \frac{V_{oc}^2}{R_c}, \quad I_{oc} = \sqrt{I_c^2 + I_m^2} \implies Q_{oc} = \frac{V_{oc}^2}{X_m}$$
     可測得鐵損電阻 $R_c$ 與激磁電抗 $X_m$。
   - **短路試驗（Short-Circuit Test, SC，高壓側通額定電流）**：
     $$R_{eq} = \frac{P_{sc}}{I_{sc}^2}, \quad Z_{eq} = \frac{V_{sc}}{I_{sc}}, \quad X_{eq} = \sqrt{Z_{eq}^2 - R_{eq}^2}$$
     可測得等效銅損電阻 $R_{eq}$ 與漏電抗 $X_{eq}$。
2. **電壓調整率（Voltage Regulation, VR）**：
   $$\text{VR} = \frac{|V_{NL}| - |V_{FL}|}{|V_{FL}|} \times 100\% \approx \frac{I_L (R_{eq} \cos\theta \pm X_{eq} \sin\theta)}{V_{FL}} \times 100\%$$
   （$+$: 滯後 Lagging 功因；$-$: 超前 Leading 功因）
3. **全日效率（All-Day Efficiency $\eta_{\text{all-day}}$）**：
   $$\eta_{\text{all-day}} = \frac{W_{\text{out}}}{W_{\text{out}} + W_{\text{loss}}} = \frac{\sum (P_{i} \times t_i)}{\sum (P_{i} \times t_i) + 24 \times P_{\text{core}} + \sum (P_{cu,i} \times t_i)} \times 100\%$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：三相變壓器接線（Y-$\Delta$）與短路試驗參數折算。
- **112 年 第一題**：自耦變壓器容量提升比與效率計算。
- **110 年 第一題**：全日效率與最大效率條件（鐵損 = 銅損 $P_c = P_{cu}$）。
""",

    '04_電機機械/02_三相感應電動機轉矩轉差率與啟動.md': r"""# ⚙️ 電機機械 核心考點 02 — 三相感應電動機轉矩轉差率與啟動

## 📌 核心解題 SOP
1. **功率流向關係（Power Flow Pipeline）**：
   $$P_{\text{in}} \to P_{\text{ag}} \to P_{\text{conv}} \to P_{\text{out}}$$
   - 氣隙功率：$P_{\text{ag}} = 3 I_2'^2 \frac{R_2'}{s} = \frac{P_{\text{rcl}}}{s}$
   - 轉子銅損：$P_{\text{rcl}} = 3 I_2'^2 R_2' = s P_{\text{ag}}$
   - 電磁轉換功率：$P_{\text{conv}} = (1 - s) P_{\text{ag}} = \frac{1 - s}{s} P_{\text{rcl}}$
   - 核心比例：$$P_{\text{ag}} : P_{\text{rcl}} : P_{\text{conv}} = 1 : s : (1 - s)$$
2. **戴維寧等效與轉矩方程式**：
   - 戴維寧阻抗：$R_{\text{th}} \approx R_1 \left(\frac{X_m}{X_1 + X_m}\right)^2, \quad X_{\text{th}} \approx X_1$
   - 感應轉矩：
     $$\tau_{\text{ind}} = \frac{1}{\omega_s} \frac{3 V_{\text{th}}^2 (R_2'/s)}{(R_{\text{th}} + R_2'/s)^2 + (X_{\text{th}} + X_2')^2}$$
   - 最大轉矩（崩潰轉矩）發生之轉差率：
     $$s_{\text{max}} = \frac{R_2'}{\sqrt{R_{\text{th}}^2 + (X_{\text{th}} + X_2')^2}}$$
   - 最大轉矩大小（與 $R_2'$ 無關！）：
     $$\tau_{\text{max}} = \frac{1}{2\omega_s} \frac{3 V_{\text{th}}^2}{R_{\text{th}} + \sqrt{R_{\text{th}}^2 + (X_{\text{th}} + X_2')^2}}$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第二題**：戴維寧等效電路推導最大轉矩與啟動電阻。
- **113 年 第二題**：氣隙功率、轉子銅損與軸端輸出效率計算。
- **111 年 第二題**：轉矩-轉差率特性曲線與雙鼠籠式轉子設計。
""",

    '02_電子學_含電力電子/02_電力電子DC-DC轉換器Buck-Boost.md': r"""# ⚡ 電子學（含電力電子）核心考點 02 — DC-DC 降壓/升壓/升降壓轉換器

## 📌 核心解題 SOP
1. **降壓轉換器（Buck Converter）**：
   - 輸出電壓：$$V_o = D V_s$$
   - 電感漣波電流：$$\Delta I_L = \frac{V_s - V_o}{L} D T = \frac{V_o (1 - D)}{L f}$$
   - 輸出漣波電壓：$$\Delta V_o = \frac{\Delta Q}{C} = \frac{\Delta I_L}{8 C f} = \frac{V_o (1 - D)}{8 L C f^2}$$
   - 連續導通邊界電感：$$L_{\text{min}} = \frac{(1 - D) R}{2 f}$$
2. **升壓轉換器（Boost Converter）**：
   - 輸出電壓：$$V_o = \frac{V_s}{1 - D}$$
   - 電感漣波電流：$$\Delta I_L = \frac{V_s D}{L f}$$
   - 輸出漣波電壓：$$\Delta V_o = \frac{I_o D}{C f} = \frac{V_o D}{R C f}$$
   - 連續導通邊界電感：$$L_{\text{min}} = \frac{D (1 - D)^2 R}{2 f}$$
3. **升降壓轉換器（Buck-Boost Converter）**：
   - 輸出電壓（極性反向）：$$V_o = -\frac{D}{1 - D} V_s$$
   - 連續導通邊界電感：$$L_{\text{min}} = \frac{(1 - D)^2 R}{2 f}$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：Buck 轉換器臨界電感與輸出濾波電容設計。
- **113 年 第一題**：Boost 轉換器 CCM/DCM 邊界條件與效率計算。
- **110 年 第一題**：Buck-Boost 電路狀態空間平均法與小訊號建模。
""",

    '03_工程數學/01_常微分方程ODE與尤拉柯西方程.md': r"""# 📐 工程數學 核心考點 01 — 常微分方程（ODE）與尤拉-柯西方程式

## 📌 核心解題 SOP
1. **二階常係數線性齊次 ODE**：
   $$y'' + a y' + b y = 0 \implies \text{特徵方程 } r^2 + a r + b = 0$$
   - 相異實根 $r_1 \ne r_2$：$$y_h(x) = c_1 e^{r_1 x} + c_2 e^{r_2 x}$$
   - 重根 $r_1 = r_2 = r$：$$y_h(x) = (c_1 + c_2 x) e^{r x}$$
   - 共軛複根 $r = \alpha \pm j \beta$：$$y_h(x) = e^{\alpha x} (c_1 \cos\beta x + c_2 \sin\beta x)$$
2. **非齊次 ODE 之特解法（未定係數法 / 參數變異法）**：
   - 參數變異法通式（朗斯基行列式 $W = y_1 y_2' - y_1' y_2$）：
     $$y_p(x) = -y_1(x) \int \frac{y_2(x) R(x)}{W(x)} dx + y_2(x) \int \frac{y_1(x) R(x)}{W(x)} dx$$
3. **尤拉-柯西方程式（Euler-Cauchy Equation）**：
   $$x^2 y'' + a x y' + b y = 0 \implies \text{令 } x = e^t \text{ 或代入 } y = x^m$$
   - 輔助方程：$$m(m - 1) + a m + b = 0 \implies m^2 + (a - 1) m + b = 0$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：二階非齊次 ODE 參數變異法與邊界值求解。
- **113 年 第三題**：尤拉-柯西方程變數變換與初值條件。
- **111 年 第三題**：常係數非齊次 ODE 諧振項未定係數法。
"""
}

def main():
    for rel_path, content in kb_updates.items():
        full_path = os.path.join(KB_DIR, rel_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Rebuilt: {rel_path}")

if __name__ == '__main__':
    main()
