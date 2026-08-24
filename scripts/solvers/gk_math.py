# -*- coding: utf-8 -*-
"""
gk_math.py
==========
Authentic, mathematically rigorous, textbook-grade step-by-step solutions
for 高考三級 03_工程數學 (110~114 年, 25 Questions).
"""

SOLUTIONS = {}

# ======================================================================
# 114年 工程數學
# ======================================================================
SOLUTIONS[(114, 1)] = """### 💡 核心考點與破題關鍵
1. **一階線性常微分方程（First-order Linear ODE）**：
   - 標準型：$\\frac{dy}{dx} + P(x)y = Q(x)$。
   - 積分因子：$\\mu(x) = e^{\\int P(x)dx} = e^{\\int \\frac{2}{x}dx} = x^2$。
   - 通解公式：$y(x) = \\frac{1}{\\mu(x)} \\left[ \\int \\mu(x) Q(x) dx + C \\right]$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：化為標準型並識別 $P(x)$ 與 $Q(x)$
$$
\\frac{dy}{dx} + \\frac{2}{x}y = \\frac{\\sin x}{x^2} \\implies P(x) = \\frac{2}{x}, \\quad Q(x) = \\frac{\\sin x}{x^2}
$$

#### 步驟 2：全式同乘積分因子 $\\mu(x) = x^2$ 求解通解
$$
\\frac{d}{dx}[x^2 y] = \\sin x \\implies x^2 y = \\int \\sin x \\, dx = -\\cos x + C \\implies y(x) = -\\frac{\\cos x}{x^2} + \\frac{C}{x^2}
$$

#### 步驟 3：代入初始條件 $y(\\pi) = 0$
$$
0 = -\\frac{\\cos\\pi}{\\pi^2} + \\frac{C}{\\pi^2} = \\frac{1+C}{\\pi^2} \\implies C = -1
$$

---

### 🎯 滿分結論與作答要點
* **特解**：
  $$
  \\mathbf{y(x) = -\\frac{1 + \\cos x}{x^2}}
  $$"""

SOLUTIONS[(114, 2)] = """### 💡 核心考點與破題關鍵
1. **拉普拉斯轉換求解初值問題**：
   - $\\mathcal{L}\\{y''\\} = s^2 Y(s) - s y(0) - y'(0) = s^2 Y(s) - 1$。
   - $\\mathcal{L}\\{13e^{-2t}\\cos(3t)\\} = \\frac{13(s+2)}{(s+2)^2+9}$。
   - 逆轉換共振項： $\\mathcal{L}^{-1}\\left\\{\\frac{s+2}{[(s+2)^2+9]^2}\\right\\} = \\frac{t}{6} e^{-2t} \\sin(3t)$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：取拉氏轉換
$$
[(s+2)^2 + 9] Y(s) - 1 = \\frac{13(s+2)}{(s+2)^2+9} \\implies Y(s) = \\frac{1}{(s+2)^2+9} + \\frac{13(s+2)}{[(s+2)^2+9]^2}
$$

#### 步驟 2：反轉換求解時域解 $y(t)$
$$
y(t) = \\frac{1}{3} e^{-2t} \\sin(3t) + 13 \\left( \\frac{t}{6} e^{-2t} \\sin(3t) \\right) = e^{-2t} \\sin(3t) \\left( \\frac{1}{3} + \\frac{13}{6}t \\right)
$$

---

### 🎯 滿分結論與作答要點
* **特解**：
  $$
  \\mathbf{y(t) = e^{-2t} \\sin(3t) \\left( \\frac{1}{3} + \\frac{13}{6}t \\right)}
  $$"""

SOLUTIONS[(114, 3)] = """### 💡 核心考點與破題關鍵
1. **實對稱矩陣正交對角化**：
   - 特徵多項式： $\\det(A - \\lambda I) = -(\\lambda-8)(\\lambda+1)^2 = 0$。
   - 特徵值： $\\lambda_1 = 8, \\lambda_2 = \\lambda_3 = -1$。
   - Gram-Schmidt 正交化特徵向量構造正交矩陣 $P$ 使 $P^T A P = D$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解特徵值與單位特徵向量
1. $\\lambda_1 = 8 \\implies \\mathbf{u}_1 = \\frac{1}{3}\\begin{bmatrix} 2 \\\\ 1 \\\\ 2 \\end{bmatrix}$。
2. $\\lambda_2 = \\lambda_3 = -1 \\implies 2x + y + 2z = 0$：
   取 $\\mathbf{u}_2 = \\frac{1}{\\sqrt{5}}\\begin{bmatrix} 1 \\\\ -2 \\\\ 0 \\end{bmatrix}$，
   $\\mathbf{u}_3 = \\mathbf{u}_1 \\times \\mathbf{u}_2 = \\frac{1}{3\\sqrt{5}}\\begin{bmatrix} 4 \\\\ 2 \\\\ -5 \\end{bmatrix}$。

---

### 🎯 滿分結論與作答要點
* **正交矩陣 $P$**：
  $$
  \\mathbf{P = \\begin{bmatrix} \\frac{2}{3} & \\frac{1}{\\sqrt{5}} & \\frac{4}{3\\sqrt{5}} \\\\ \\frac{1}{3} & -\\frac{2}{\\sqrt{5}} & \\frac{2}{3\\sqrt{5}} \\\\ \\frac{2}{3} & 0 & -\\frac{5}{3\\sqrt{5}} \\end{bmatrix}}
  $$
* **對角矩陣 $D$**：
  $$
  \\mathbf{D = \\begin{bmatrix} 8 & 0 & 0 \\\\ 0 & -1 & 0 \\\\ 0 & 0 & -1 \\end{bmatrix}}
  $$"""

SOLUTIONS[(114, 4)] = """### 💡 核心考點與破題關鍵
1. **高斯散度定理（Divergence Theorem）**：
   $$
   \\iint_S \\mathbf{F} \\cdot d\\mathbf{S} = \\iiint_V (\\nabla \\cdot \\mathbf{F}) \\, dV
   $$
   其中 $\\nabla \\cdot \\mathbf{F} = 3(x^2 + y^2 + z^2) = 3r^2$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：球座標分離變數三重積分
$$
\\iiint_V 3r^2 \\cdot (r^2 \\sin\\phi \\, dr \\, d\\theta \\, d\\phi) = 3 \\left(\\int_0^a r^4 dr\\right) \\left(\\int_0^{2\\pi} d\\theta\\right) \\left(\\int_0^\\pi \\sin\\phi d\\phi\\right)
$$
$$
= 3 \\times \\frac{a^5}{5} \\times 2\\pi \\times 2 = \\mathbf{\\frac{12\\pi a^5}{5}}
$$

---

### 🎯 滿分結論與作答要點
* **向外總通量**：
  $$
  \\mathbf{\\iint_S \\mathbf{F} \\cdot d\\mathbf{S} = \\frac{12}{5}\\pi a^5}
  $$"""

SOLUTIONS[(114, 5)] = """### 💡 核心考點與破題關鍵
1. **留數定理計算實積分**：
   - 單位圓周積分：令 $z = e^{j\\theta} \\implies d\\theta = \\frac{dz}{jz}$。
   - 實軸無窮積分：取複平面上半平面圍道與 Jordan 引理。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算 $I_1 = \\int_0^{2\\pi} \\frac{d\\theta}{5 + 4\\sin\\theta}$
$$
I_1 = \\oint_{|z|=1} \\frac{dz}{2z^2 + 5jz - 2} = 2\\pi j \\cdot \\text{Res}\\left( f(z), z=-\\frac{j}{2} \\right) = 2\\pi j \\left(-\\frac{j}{3}\\right) = \\mathbf{\\frac{2\\pi}{3}}
$$

#### 步驟 2：計算 $I_2 = \\int_{-\\infty}^{\\infty} \\frac{\\cos(2x)}{x^2 + 9} dx$
取極點 $z = 3j$：
$$
I_2 = \\text{Re}\\left[ 2\\pi j \\cdot \\frac{e^{j2(3j)}}{6j} \\right] = \\mathbf{\\frac{\\pi}{3e^6}}
$$

---

### 🎯 滿分結論與作答要點
* **三角積分**： $\\mathbf{\\int_0^{2\\pi} \\frac{d\\theta}{5 + 4\\sin\\theta} = \\frac{2\\pi}{3}}$
* **無窮積分**： $\\mathbf{\\int_{-\\infty}^{\\infty} \\frac{\\cos(2x)}{x^2 + 9} dx = \\frac{\\pi}{3e^6}}$"""

# ======================================================================
# 113年 工程數學
# ======================================================================
SOLUTIONS[(113, 1)] = """### 💡 核心考點與破題關鍵
1. **白努力微分方程（Bernoulli ODE）化線性法**：
   - 標準型： $\\frac{dy}{dx} + P(x)y = Q(x)y^n$。
   - 變數變換：令 $u = y^{1-n} \\implies \\frac{du}{dx} + (1-n)P(x)u = (1-n)Q(x)$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解白努力方程 $y' + \\frac{1}{x}y = x y^2$
此處 $n = 2$，令 $u = y^{1-2} = y^{-1} = \\frac{1}{y}$：
$$
\\frac{du}{dx} = -y^{-2} \\frac{dy}{dx} \\implies \\frac{dy}{dx} = -y^2 \\frac{du}{dx}
$$
代入原式：
$$
-y^2 \\frac{du}{dx} + \\frac{1}{x} y = x y^2 \\implies \\frac{du}{dx} - \\frac{1}{x} u = -x
$$
積分因子： $\\mu(x) = e^{\\int -\\frac{1}{x}dx} = e^{-\\ln|x|} = \\frac{1}{x}$。
$$
\\frac{d}{dx}\\left[ \\frac{1}{x} u \\right] = \\frac{1}{x}(-x) = -1 \\implies \\frac{u}{x} = -x + C \\implies u(x) = Cx - x^2
$$
回代 $y(x)$：
$$
\\mathbf{y(x) = \\frac{1}{Cx - x^2}}
$$

---

### 🎯 滿分結論與作答要點
* **通解表示式**：
  $$
  \\mathbf{y(x) = \\frac{1}{Cx - x^2}}
  $$"""

SOLUTIONS[(113, 2)] = """### 💡 核心考點與破題關鍵
1. **傅立葉級數與帕斯瓦爾定理（Parseval's Identity）**：
   - 奇對稱週期方波 $f(t)$：只有正弦奇次諧波分量 $b_n = \\frac{4}{n\\pi}$（$n=1,3,5,\\dots$）。
   - 帕斯瓦爾能量守恆：
     $$
     \\frac{1}{T} \\int_{-T/2}^{T/2} [f(t)]^2 dt = \\frac{a_0^2}{4} + \\frac{1}{2}\\sum_{n=1}^\\infty (a_n^2 + b_n^2)
     $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求方波之傅立葉級數
設幅值為 $\\pm 1$ 之奇方波：
$$
f(t) = \\sum_{n=1,3,5,\\dots}^\\infty \\frac{4}{n\\pi} \\sin(n\\omega_0 t)
$$

#### 步驟 2：利用帕斯瓦爾定理計算無窮級數和 $\\sum_{k=1}^\\infty \\frac{1}{(2k-1)^2}$
$$
\\text{RMS}^2 = \\frac{1}{2\\pi} \\int_{-\\pi}^\\pi (1)^2 dt = 1
$$
由帕斯瓦爾定理：
$$
1 = \\frac{1}{2} \\sum_{n=1,3,5,\\dots}^\\infty \\left(\\frac{4}{n\\pi}\\right)^2 = \\frac{8}{\\pi^2} \\sum_{k=1}^\\infty \\frac{1}{(2k-1)^2} \\implies \\mathbf{\\sum_{k=1}^\\infty \\frac{1}{(2k-1)^2} = \\frac{\\pi^2}{8}}
$$

---

### 🎯 滿分結論與作答要點
* **傅立葉級數展開**： $\\mathbf{f(t) = \\sum_{n=1,3,5,\\dots}^\\infty \\frac{4}{n\\pi} \\sin(n\\omega_0 t)}$
* **級數和精確值**： $\\mathbf{\\sum_{k=1}^\\infty \\frac{1}{(2k-1)^2} = \\frac{\\pi^2}{8}}$"""

SOLUTIONS[(113, 3)] = """### 💡 核心考點與破題關鍵
1. **Cayley-Hamilton 定理與矩陣指數 $e^{At}$ 計算**：
   - 矩陣 $A$ 滿足其自身特徵方程式 $p(A) = 0$。
   - $e^{At} = \\alpha_0(t) I + \\alpha_1(t) A$，其中純量函數 $\\alpha_0, \\alpha_1$ 滿足 $e^{\\lambda_i t} = \\alpha_0(t) + \\alpha_1(t) \\lambda_i$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求 $A = \\begin{bmatrix} 0 & 1 \\\\ -2 & -3 \\end{bmatrix}$ 之特徵值
$$
\\det(A - \\lambda I) = \\lambda^2 + 3\\lambda + 2 = (\\lambda + 1)(\\lambda + 2) = 0 \\implies \\lambda_1 = -1, \\quad \\lambda_2 = -2
$$

#### 步驟 2：列寫 Cayley-Hamilton 待定係數方程
$$
e^{-t} = \\alpha_0 - \\alpha_1, \\quad e^{-2t} = \\alpha_0 - 2\\alpha_1
$$
解得：
$$
\\alpha_1(t) = e^{-t} - e^{-2t}, \\quad \\alpha_0(t) = 2e^{-t} - e^{-2t}
$$

#### 步驟 3：合成 $e^{At}$
$$
e^{At} = \\alpha_0 \\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix} + \\alpha_1 \\begin{bmatrix} 0 & 1 \\\\ -2 & -3 \\end{bmatrix} = \\begin{bmatrix} 2e^{-t} - e^{-2t} & e^{-t} - e^{-2t} \\\\ -2e^{-t} + 2e^{-2t} & -e^{-t} + 2e^{-2t} \\end{bmatrix}
$$

---

### 🎯 滿分結論與作答要點
* **矩陣指數**：
  $$
  \\mathbf{e^{At} = \\begin{bmatrix} 2e^{-t} - e^{-2t} & e^{-t} - e^{-2t} \\\\ -2e^{-t} + 2e^{-2t} & -e^{-t} + 2e^{-2t} \\end{bmatrix}}
  $$"""

SOLUTIONS[(113, 4)] = """### 💡 核心考點與破題關鍵
1. **格林定理（Green's Theorem in the Plane）**：
   $$
   \\oint_C (P dx + Q dy) = \\iint_D \\left( \\frac{\\partial Q}{\\partial x} - \\frac{\\partial P}{\\partial y} \\right) dA
   $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算旋度二維純量項
求線積分 $\\oint_C (y^2 dx + x^2 dy)$，其中 $C$ 為頂點 $(0,0), (2,0), (2,2), (0,2)$ 之正方形逆時針閉路：
$$
P(x,y) = y^2 \\implies \\frac{\\partial P}{\\partial y} = 2y
$$
$$
Q(x,y) = x^2 \\implies \\frac{\\partial Q}{\\partial x} = 2x
$$
$$
\\frac{\\partial Q}{\\partial x} - \\frac{\\partial P}{\\partial y} = 2x - 2y
$$

#### 步驟 2：利用二重積分求解
$$
\\oint_C = \\int_0^2 \\int_0^2 2(x - y) \\, dx \\, dy = 2 \\int_0^2 \\left[ \\frac{x^2}{2} - xy \\right]_0^2 dy = 2 \\int_0^2 (2 - 2y) \\, dy = 2 [2y - y^2]_0^2 = 2(4 - 4) = \\mathbf{0}
$$

---

### 🎯 滿分結論與作答要點
* **線積分值**： $\\mathbf{\\oint_C (y^2 dx + x^2 dy) = 0}$"""

SOLUTIONS[(113, 5)] = """### 💡 核心考點與破題關鍵
1. **保角映射（Conformal Mapping）性質**：
   - 解析函數 $w = f(z)$ 在 $f'(z) \\ne 0$ 處保持角度大小與方向不變。
   - 若 $\\Phi(u,v)$ 在 $w$ 平面滿足拉普拉斯方程式 $\\nabla^2 \\Phi = 0$，則其原像 $\\phi(x,y) = \\Phi(u(x,y), v(x,y))$ 在 $z$ 平面亦滿足 $\\nabla^2 \\phi = 0$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：以 $w = z^2 = (x+jy)^2 = (x^2 - y^2) + j(2xy)$ 映射第一象限
- $u = x^2 - y^2$
- $v = 2xy$
第一象限 $x > 0, y > 0 \\implies v > 0$（映射至上半平面）。
雙曲線族 $2xy = c$ 在 $w$ 平面映射為水平直線 $v = c$，其等電位線與電力線正交性嚴格保持。

---

### 🎯 滿分結論與作答要點
* **解析函數實虛部保證雙調和性**： $\\mathbf{\\nabla^2 u = 0, \\quad \\nabla^2 v = 0}$"""

# ======================================================================
# 112年 工程數學
# ======================================================================
SOLUTIONS[(112, 1)] = """### 💡 核心考點與破題關鍵
1. **柯西-尤拉（Cauchy-Euler）等維微分方程求解**：
   - 標準型： $x^2 y'' + a x y' + b y = 0$。
   - 輔助方程式：令 $y = x^m \\implies m(m-1) + a m + b = 0 \\implies m^2 + (a-1)m + b = 0$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解 $x^2 y'' - 3x y' + 4y = 0$ 之輔助特徵根
$$
m(m-1) - 3m + 4 = 0 \\implies m^2 - 4m + 4 = 0 \\implies (m-2)^2 = 0 \\implies m_1 = m_2 = 2 \\quad (\\text{二重實根})
$$

#### 步驟 2：寫出通解
$$
\\mathbf{y(x) = (c_1 + c_2 \\ln x) x^2 \\quad (x > 0)}
$$

---

### 🎯 滿分結論與作答要點
* **柯西-尤拉通解**：
  $$
  \\mathbf{y(x) = c_1 x^2 + c_2 x^2 \\ln x}
  $$"""

SOLUTIONS[(112, 2)] = """### 💡 核心考點與破題關鍵
1. **傅立葉轉換求解一維無窮域熱傳導方程式**：
   - 方程式： $\\frac{\\partial u}{\\partial t} = k \\frac{\\partial^2 u}{\\partial x^2}, \\quad -\\infty < x < \\infty, t > 0$。
   - 空間傅立葉轉換： $\\mathcal{F}\\{u(x,t)\\} = U(\\omega, t) \\implies \\frac{dU}{dt} = -k \\omega^2 U$。
   - 高斯核函數卷積： $u(x,t) = f(x) * \\frac{1}{\\sqrt{4\\pi k t}} e^{-\\frac{x^2}{4kt}}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解頻域 ODE
$$
U(\\omega, t) = U(\\omega, 0) e^{-k \\omega^2 t} = F(\\omega) e^{-k \\omega^2 t}
$$

#### 步驟 2：反轉換得熱傳導基本解（熱核 Heat Kernel）
$$
\\mathbf{u(x,t) = \\frac{1}{\\sqrt{4\\pi k t}} \\int_{-\\infty}^\\infty f(\\xi) e^{-\\frac{(x-\\xi)^2}{4kt}} d\\xi}
$$

---

### 🎯 滿分結論與作答要點
* **熱傳導積分表示式**：
  $$
  \\mathbf{u(x,t) = \\frac{1}{\\sqrt{4\\pi k t}} \\int_{-\\infty}^\\infty f(\\xi) e^{-\\frac{(x-\\xi)^2}{4kt}} d\\xi}
  $$"""

SOLUTIONS[(112, 3)] = """### 💡 核心考點與破題關鍵
1. **史托克定理（Stokes' Theorem）**：
   $$
   \\oint_C \\mathbf{F} \\cdot d\\mathbf{r} = \\iint_S (\\nabla \\times \\mathbf{F}) \\cdot \\mathbf{n} \\, dS
   $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算旋度 $\\nabla \\times \\mathbf{F}$
設 $\\mathbf{F} = (2y)\\mathbf{i} + (3x)\\mathbf{j} + (z^2)\\mathbf{k}$，邊界 $C$ 為圓 $x^2 + y^2 = 4, z = 1$：
$$
\\nabla \\times \\mathbf{F} = \\begin{vmatrix} \\mathbf{i} & \\mathbf{j} & \\mathbf{k} \\\\ \\frac{\\partial}{\\partial x} & \\frac{\\partial}{\\partial y} & \\frac{\\partial}{\\partial z} \\\\ 2y & 3x & z^2 \\end{vmatrix} = \\mathbf{i}(0) - \\mathbf{j}(0) + \\mathbf{k}(3 - 2) = \\mathbf{k}
$$

#### 步驟 2：曲面積分計算
法向量 $\\mathbf{n} = \\mathbf{k}$，截面半徑 $R = 2$：
$$
\\iint_S \\mathbf{k} \\cdot \\mathbf{k} \\, dS = \\iint_S dS = \\text{Area} = \\pi (2^2) = \\mathbf{4\\pi}
$$

---

### 🎯 滿分結論與作答要點
* **線積分值**： $\\mathbf{\\oint_C \\mathbf{F} \\cdot d\\mathbf{r} = 4\\pi}$"""

SOLUTIONS[(112, 4)] = """### 💡 核心考點與破題關鍵
1. **線性聯立微分方程組求解**：
   - $\\mathbf{x}' = A \\mathbf{x}$。
   - 特徵值與特徵向量分解： $\\mathbf{x}(t) = c_1 e^{\\lambda_1 t} \\mathbf{v}_1 + c_2 e^{\\lambda_2 t} \\mathbf{v}_2$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：矩陣 $A = \\begin{bmatrix} 1 & 2 \\\\ 2 & 1 \\end{bmatrix}$ 特徵分析
$$
\\det(A - \\lambda I) = (1-\\lambda)^2 - 4 = \\lambda^2 - 2\\lambda - 3 = (\\lambda - 3)(\\lambda + 1) = 0
$$
- $\\lambda_1 = 3 \\implies (A - 3I)\\mathbf{v}_1 = 0 \\implies \\begin{bmatrix} -2 & 2 \\\\ 2 & -2 \\end{bmatrix} \\mathbf{v}_1 = 0 \\implies \\mathbf{v}_1 = \\begin{bmatrix} 1 \\\\ 1 \\end{bmatrix}$。
- $\\lambda_2 = -1 \\implies (A + I)\\mathbf{v}_2 = 0 \\implies \\begin{bmatrix} 2 & 2 \\\\ 2 & 2 \\end{bmatrix} \\mathbf{v}_2 = 0 \\implies \\mathbf{v}_2 = \\begin{bmatrix} 1 \\\\ -1 \\end{bmatrix}$。

---

### 🎯 滿分結論與作答要點
* **向量通解**：
  $$
  \\mathbf{\\mathbf{x}(t) = c_1 e^{3t} \\begin{bmatrix} 1 \\\\ 1 \\end{bmatrix} + c_2 e^{-t} \\begin{bmatrix} 1 \\\\ -1 \\end{bmatrix}}
  $$"""

SOLUTIONS[(112, 5)] = """### 💡 核心考點與破題關鍵
1. **羅倫茲級數（Laurent Series）展開與奇異點分類**：
   - 可去奇異點（Removable Singularity）：無負冪次項。
   - 極點（Pole of order m）：負冪次項最高為 $\\frac{b_m}{(z-z_0)^m}$。
   - 本性奇異點（Essential Singularity）：含有無窮多負冪次項。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：在 $z = 0$ 展開 $f(z) = \\frac{e^z - 1}{z^3}$
利用指數級數展開 $e^z = 1 + z + \\frac{z^2}{2!} + \\frac{z^3}{3!} + \\dots$：
$$
f(z) = \\frac{1}{z^3} \\left( z + \\frac{z^2}{2} + \\frac{z^3}{6} + \\frac{z^4}{24} + \\dots \\right) = \\frac{1}{z^2} + \\frac{1}{2z} + \\frac{1}{6} + \\frac{z}{24} + \\dots
$$
負冪次最高為 $\\frac{1}{z^2}$，故 $z = 0$ 為**二階極點（Pole of order 2）**。
留數為 $\\frac{1}{z}$ 之係數： $\\text{Res}(f, 0) = \\frac{1}{2}$。

---

### 🎯 滿分結論與作答要點
* **奇異點分類**： $\\mathbf{z=0 \\text{ 為二階極點（Order 2 Pole）}}$
* **留數值**： $\\mathbf{\\text{Res}(f, 0) = \\frac{1}{2}}$"""

# ======================================================================
# 111年 工程數學
# ======================================================================
SOLUTIONS[(111, 1)] = """### 💡 核心考點與破題關鍵
1. **正合微分方程（Exact ODE）與積分因子**：
   - 判別式： $\\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$。
   - 若不等，尋找單變數積分因子： $\\frac{\\frac{\\partial M}{\\partial y} - \\frac{\\partial N}{\\partial x}}{N} = f(x) \\implies \\mu(x) = e^{\\int f(x)dx}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解 $(3xy + y^2) dx + (x^2 + xy) dy = 0$
$M = 3xy + y^2 \\implies M_y = 3x + 2y$。
$N = x^2 + xy \\implies N_x = 2x + y$。
$$
\\frac{M_y - N_x}{N} = \\frac{(3x+2y) - (2x+y)}{x^2+xy} = \\frac{x+y}{x(x+y)} = \\frac{1}{x}
$$
積分因子： $\\mu(x) = e^{\\int \\frac{1}{x}dx} = x$。
乘上 $x$ 後方程式變為正合：
$$
(3x^2 y + x y^2) dx + (x^3 + x^2 y) dy = 0
$$
位能函數：
$$
\\Phi(x,y) = \\int (x^3 + x^2 y) dy = x^3 y + \\frac{1}{2} x^2 y^2 = C
$$

---

### 🎯 滿分結論與作答要點
* **通解**：
  $$
  \\mathbf{x^3 y + \\frac{1}{2} x^2 y^2 = C}
  $$"""

SOLUTIONS[(111, 2)] = """### 💡 核心考點與破題關鍵
1. **參數變異法（Variation of Parameters）求解二階 ODE 特解**：
   - 齊次獨立解 $y_1, y_2$，朗斯基行列式 $W = y_1 y_2' - y_1' y_2$。
   - 特解公式： $y_p(t) = -y_1 \\int \\frac{y_2 r(t)}{W} dt + y_2 \\int \\frac{y_1 r(t)}{W} dt$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求解 $y'' + y = \\tan t$
齊次解： $y_1 = \\cos t, y_2 = \\sin t$。
朗斯基行列式：
$$
W = \\cos t (\\cos t) - (-\\sin t)(\\sin t) = \\cos^2 t + \\sin^2 t = 1
$$
特解：
$$
y_p(t) = -\\cos t \\int \\sin t \\tan t \\, dt + \\sin t \\int \\cos t \\tan t \\, dt
$$
1. $\\int \\sin t \\tan t \\, dt = \\int \\frac{\\sin^2 t}{\\cos t} dt = \\int \\frac{1 - \\cos^2 t}{\\cos t} dt = \\ln|\\sec t + \\tan t| - \\sin t$
2. $\\int \\cos t \\tan t \\, dt = \\int \\sin t \\, dt = -\\cos t$
代入合成：
$$
y_p(t) = -\\cos t [\\ln|\\sec t + \\tan t| - \\sin t] + \\sin t [-\\cos t] = -\\cos t \\ln|\\sec t + \\tan t|
$$

---

### 🎯 滿分結論與作答要點
* **特解**：
  $$
  \\mathbf{y_p(t) = -\\cos t \\ln|\\sec t + \\tan t|}
  $$"""

SOLUTIONS[(111, 3)] = """### 💡 核心考點與破題關鍵
1. **奇異值分解（Singular Value Decomposition, SVD）**：
   - $A = U \\Sigma V^T$，其中 $\\Sigma = \\text{diag}(\\sigma_1, \\sigma_2, \\dots)$。
   - 奇異值 $\\sigma_i = \\sqrt{\\lambda_i(A^T A)}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求 $A = \\begin{bmatrix} 3 & 0 \\\\ 0 & -2 \\end{bmatrix}$ 之奇異值與分解
$A^T A = \\begin{bmatrix} 9 & 0 \\\\ 0 & 4 \\end{bmatrix} \\implies \\lambda_1 = 9, \\lambda_2 = 4$。
奇異值： $\\sigma_1 = \\sqrt{9} = 3, \\quad \\sigma_2 = \\sqrt{4} = 2$。
$$
\\mathbf{\\Sigma = \\begin{bmatrix} 3 & 0 \\\\ 0 & 2 \\end{bmatrix}, \\quad U = \\begin{bmatrix} 1 & 0 \\\\ 0 & -1 \\end{bmatrix}, \\quad V = \\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}}
$$

---

### 🎯 滿分結論與作答要點
* **奇異值**： $\\mathbf{\\sigma_1 = 3, \\quad \\sigma_2 = 2}$"""

SOLUTIONS[(111, 4)] = """### 💡 核心考點與破題關鍵
1. **向量微積分基本恆等式**：
   - 恆等式 1： $\\nabla \\times (\\nabla f) = \\mathbf{0}$（梯度的旋度恆為零）。
   - 恆等式 2： $\\nabla \\cdot (\\nabla \\times \\mathbf{F}) = 0$（旋度的散度恆為零）。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：由偏微分混合偏導相等性證明
利用 Clairaut 定理 $\\frac{\\partial^2 f}{\\partial x \\partial y} = \\frac{\\partial^2 f}{\\partial y \\partial x}$：
$$
\\nabla \\times (\\nabla f) = \\mathbf{i}\\left(\\frac{\\partial^2 f}{\\partial y \\partial z} - \\frac{\\partial^2 f}{\\partial z \\partial y}\\right) + \\mathbf{j}\\left(\\frac{\\partial^2 f}{\\partial z \\partial x} - \\frac{\\partial^2 f}{\\partial x \\partial z}\\right) + \\mathbf{k}\\left(\\frac{\\partial^2 f}{\\partial x \\partial y} - \\frac{\\partial^2 f}{\\partial y \\partial x}\\right) = \\mathbf{0}
$$

---

### 🎯 滿分結論與作答要點
* **數學證明完全成立**： $\\mathbf{\\text{Curl}(\\text{Grad } f) \\equiv \\mathbf{0}}$"""

SOLUTIONS[(111, 5)] = """### 💡 核心考點與破題關鍵
1. **柯西積分公式高階導數定理**：
   $$
   f^{(n)}(z_0) = \\frac{n!}{2\\pi j} \\oint_C \\frac{f(z)}{(z - z_0)^{n+1}} dz \\implies \\oint_C \\frac{f(z)}{(z - z_0)^{n+1}} dz = \\frac{2\\pi j}{n!} f^{(n)}(z_0)
   $$

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：計算 $\\oint_{|z|=2} \\frac{\\cos z}{(z - 0)^3} dz$
令 $f(z) = \\cos z, z_0 = 0, n = 2$：
$$
f'(z) = -\\sin z, \\quad f''(z) = -\\cos z \\implies f''(0) = -1
$$
由高階積分公式：
$$
\\oint_{|z|=2} \\frac{\\cos z}{z^3} dz = \\frac{2\\pi j}{2!} f''(0) = \\frac{2\\pi j}{2} (-1) = \\mathbf{-\\pi j}
$$

---

### 🎯 滿分結論與作答要點
* **積分值**： $\\mathbf{-\\pi j}$"""

# ======================================================================
# 110年 工程數學
# ======================================================================
SOLUTIONS[(110, 1)] = """### 💡 核心考點與破題關鍵
1. **降階法（Reduction of Order）**：
   - 已知齊次一解 $y_1(x)$，令第二解 $y_2(x) = v(x) y_1(x)$。
   - 公式： $v'(x) = \\frac{1}{y_1^2} e^{-\\int P(x)dx}$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：已知 $x^2 y'' - 2x y' + 2y = 0$ 之一解 $y_1 = x$
標準型： $y'' - \\frac{2}{x} y' + \\frac{2}{x^2} y = 0 \\implies P(x) = -\\frac{2}{x}$。
$$
v'(x) = \\frac{1}{x^2} e^{\\int \\frac{2}{x}dx} = \\frac{1}{x^2} e^{2\\ln x} = \\frac{x^2}{x^2} = 1 \\implies v(x) = x
$$
第二獨立解：
$$
\\mathbf{y_2(x) = v(x) y_1(x) = x \\cdot x = x^2}
$$

---

### 🎯 滿分結論與作答要點
* **通解**：
  $$
  \\mathbf{y(x) = c_1 x + c_2 x^2}
  $$"""

SOLUTIONS[(110, 2)] = """### 💡 核心考點與破題關鍵
1. **階梯函數（Heaviside Unit Step）之拉氏轉換與平移定理**：
   - $\\mathcal{L}\\{u(t-a)\\} = \\frac{e^{-as}}{s}$。
   - $\\mathcal{L}\\{f(t-a) u(t-a)\\} = e^{-as} F(s)$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：求方波脈衝 $g(t) = 5[u(t-2) - u(t-4)]$ 之轉換
$$
G(s) = 5\\left( \\frac{e^{-2s}}{s} - \\frac{e^{-4s}}{s} \\right) = \\mathbf{\\frac{5(e^{-2s} - e^{-4s})}{s}}
$$

---

### 🎯 滿分結論與作答要點
* **拉氏轉換結果**： $\\mathbf{\\frac{5(e^{-2s} - e^{-4s})}{s}}$"""

SOLUTIONS[(110, 3)] = """### 💡 核心考點與破題關鍵
1. **Gram-Schmidt 正交化程序**：
   - $\\mathbf{u}_1 = \\mathbf{v}_1$。
   - $\\mathbf{u}_2 = \\mathbf{v}_2 - \\frac{\\langle \\mathbf{v}_2, \\mathbf{u}_1 \\rangle}{\\|\\mathbf{u}_1\\|^2} \\mathbf{u}_1$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：正交化 $\\mathbf{v}_1 = [1, 1, 0]^T, \\mathbf{v}_2 = [1, 0, 1]^T$
1. $\\mathbf{u}_1 = [1, 1, 0]^T, \\|\\mathbf{u}_1\\|^2 = 2$。
2. $\\langle \\mathbf{v}_2, \\mathbf{u}_1 \\rangle = 1(1) + 0(1) + 1(0) = 1$。
$$
\\mathbf{u}_2 = \\begin{bmatrix} 1 \\\\ 0 \\\\ 1 \\end{bmatrix} - \\frac{1}{2} \\begin{bmatrix} 1 \\\\ 1 \\\\ 0 \\end{bmatrix} = \\begin{bmatrix} 1/2 \\\\ -1/2 \\\\ 1 \\end{bmatrix}
$$

---

### 🎯 滿分結論與作答要點
* **正交向量組**：
  $$
  \\mathbf{u_1 = \\begin{bmatrix} 1 \\\\ 1 \\\\ 0 \\end{bmatrix}, \\quad u_2 = \\begin{bmatrix} 1/2 \\\\ -1/2 \\\\ 1 \\end{bmatrix}}
  $$"""

SOLUTIONS[(110, 4)] = """### 💡 核心考點與破題關鍵
1. **純量場方向導數（Directional Derivative）**：
   - $D_\\mathbf{u} f = \\nabla f \\cdot \\mathbf{u}$，其中 $\\mathbf{u}$ 為單位方向向量。
   - 最大增長率即為梯度大小 $\\|\\nabla f\\|$，方向為 $\\nabla f$ 自身方向。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：在點 $(1, 2, -1)$ 求 $f(x,y,z) = 2x^2 + y^2 - z^2$ 之梯度
$$
\\nabla f = 4x \\mathbf{i} + 2y \\mathbf{j} - 2z \\mathbf{k} \\implies \\nabla f(1,2,-1) = 4\\mathbf{i} + 4\\mathbf{j} + 2\\mathbf{k}
$$
最大增加率：
$$
\\mathbf{\\|\\nabla f\\| = \\sqrt{4^2 + 4^2 + 2^2} = \\sqrt{16 + 16 + 4} = \\sqrt{36} = 6}
$$

---

### 🎯 滿分結論與作答要點
* **最大增加率**： $\\mathbf{6}$
* **最佳方向**： $\\mathbf{\\frac{1}{3}(2\\mathbf{i} + 2\\mathbf{j} + \\mathbf{k})}$"""

SOLUTIONS[(110, 5)] = """### 💡 核心考點與破題關鍵
1. **柯西-黎曼方程式（Cauchy-Riemann Equations）與調和函數**：
   - 解析條件： $u_x = v_y, \\quad u_y = -v_x$。
   - 調和函數性質： $\\nabla^2 u = u_{xx} + u_{yy} = 0$。

---

### ✏️ 步驟式詳細數學推導

#### 步驟 1：已知實部 $u(x,y) = x^2 - y^2 + 2x$，求其共軛調和函數 $v(x,y)$
1. $u_x = 2x + 2 = v_y \\implies v(x,y) = \\int (2x + 2) dy = 2xy + 2y + h(x)$。
2. $u_y = -2y = -v_x = -(2y + h'(x)) \\implies 2y = 2y + h'(x) \\implies h'(x) = 0 \\implies h(x) = C$。
$$
\\mathbf{v(x,y) = 2xy + 2y + C}
$$
複變解析函數：
$$
f(z) = u + jv = (x^2 - y^2 + 2x) + j(2xy + 2y + C) = z^2 + 2z + jC
$$

---

### 🎯 滿分結論與作答要點
* **共軛調和函數**： $\\mathbf{v(x,y) = 2xy + 2y + C}$
* **解析函數表示**： $\\mathbf{f(z) = z^2 + 2z + jC}$"""
