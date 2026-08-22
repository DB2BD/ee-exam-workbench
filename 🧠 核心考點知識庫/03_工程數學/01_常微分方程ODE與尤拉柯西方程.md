# 📐 工程數學 核心考點 01 — 常微分方程（ODE）

## 📌 核心解題 SOP
1. **一階線性常微分方程**：$y' + P(x) y = Q(x)$
   - 積分因子：$I(x) = e^{\int P(x) dx}$
   - 通解公式：$y(x) = \frac{1}{I(x)} \left[ \int I(x) Q(x) dx + C \right]$
2. **二階常係數齊次線性 ODE**：$y'' + a y' + b y = 0$
   - 特徵方程：$\lambda^2 + a\lambda + b = 0$
   - 實相異根 $\lambda_1 \ne \lambda_2 \implies y_h = c_1 e^{\lambda_1 x} + c_2 e^{\lambda_2 x}$
   - 重根 $\lambda_1 = \lambda_2 \implies y_h = (c_1 + c_2 x) e^{\lambda_1 x}$
   - 複數共軛根 $\lambda = \alpha \pm j\beta \implies y_h = e^{\alpha x} (c_1 \cos\beta x + c_2 \sin\beta x)$
3. **二階非齊次 ODE 特解求法（參數變異法 Method of Variation of Parameters）**：
   y_p(x) = -y_1(x) \int \frac{y_2(x) r(x)}{W(y_1, y_2)} dx + y_2(x) \int \frac{y_1(x) r(x)}{W(y_1, y_2)} dx
   其中朗斯基行列式（Wronskian）$W(y_1, y_2) = \begin{vmatrix} y_1 & y_2 \\ y_1' & y_2' \end{vmatrix} = y_1 y_2' - y_1' y_2$。
4. **尤拉-柯西方程（Euler-Cauchy Equation）**：
   x^2 y'' + a x y' + b y = 0
   令 $y = x^m \implies m(m-1) + a m + b = 0 \implies m^2 + (a-1)m + b = 0$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：$y'' + 4y' + 4y = 0$ 重根初始值問題。
- **113 年 第一題**：$y'' + 4y' + 5y = e^{-2x} \csc x$ 參數變異法求解。
- **111 年 第一題**：降階法（Reduction of Order）已知一解求通解。
- **109 年 第一題**：二階非齊次常係數 ODE 待定係數法。
