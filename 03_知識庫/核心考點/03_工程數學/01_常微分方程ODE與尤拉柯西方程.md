# 📐 工程數學 核心考點 01 — 常微分方程（ODE）與尤拉-柯西方程式

## 📌 核心解題 SOP
1. **二階常係數線性齊次 ODE**：
   $$y'' + a y' + b y = 0 \implies \text{特徵方程 } r^2 + a r + b = 0$$
   - 相異實根 $r_1 \ne r_2：y_h(x) = c_1 e^{r_1 x} + c_2 e^{r_2 x}$
   - 重根 $r_1 = r_2 = r：y_h(x) = (c_1 + c_2 x) e^{r x}$
   - 共軛複根 $r = \alpha \pm j \beta：y_h(x) = e^{\alpha x} (c_1 \cos\beta x + c_2 \sin\beta x)$

2. **非齊次 ODE 之特解法（未定係數法 / 參數變異法）**：
   - 參數變異法通式（朗斯基行列式 $W = y_1 y_2' - y_1' y_2$）：
     $$y_p(x) = -y_1(x) \int \frac{y_2(x) R(x)}{W(x)} dx + y_2(x) \int \frac{y_1(x) R(x)}{W(x)} dx$$
3. **尤拉-柯西方程式（Euler-Cauchy Equation）**：
   $$x^2 y'' + a x y' + b y = 0 \implies \text{令 } x = e^t \text{ 或代入 } y = x^m$$
- $輔助方程：m(m - 1) + a m + b = 0 \implies m^2 + (a - 1) m + b = 0$


---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：二階非齊次 ODE 參數變異法與邊界值求解。
- **113 年 第三題**：尤拉-柯西方程變數變換與初值條件。
- **111 年 第三題**：常係數非齊次 ODE 諧振項未定係數法。
