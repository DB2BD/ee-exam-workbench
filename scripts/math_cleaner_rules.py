import fitz
import glob
import os
import re

# Comprehensive math polishers for all subjects

def clean_engineering_math(text):
    # 114
    text = re.sub(r'二、\s*計算∫e17మ[^\n]*\n[^\n]*dz[^\n]*',
                  r'二、 計算 $\\oint_C e^{1/z^2} dz$，其中路徑 $C$ 為下圖所示複數平面 $z = x+iy$ 上，圓心在原點 $O$ 之單位圓。（15 分）', text)
    text = re.sub(r'三、\s*求解以下初始值問題之常微分方程式[^\n]*',
                  r'三、 求解以下初始值問題之常微分方程式：$y\'\'(t) + 4y\'(t) + 4y(t) = 0, y(0) = 1, y\'(0) = 3$。（20 分）', text)
    text = re.sub(r'四、\s*假設週期函數\(x\)之週期為2f[^\n]*\nx[^\n]*\n[^\n]*',
                  r'四、 假設週期函數 $f(x)$ 之週期為 $2\\pi$：\n$$f(x) = \\begin{cases} 0, & -\\pi < x \\le 0 \\\\ x, & 0 < x \\le \\pi \\end{cases}$$\n計算 $f(x)$ 之傅立葉級數（Fourier Series）。（20 分）', text)
    text = re.sub(r'五、\s*假設矩陣A = \[0[\s\S]*?T。',
                  r'五、 假設矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -1 & 0 \\\\ 0 & 1 \\\\ -1 & 0 \\end{bmatrix}$ 與 $\\mathbf{b} = \\begin{bmatrix} 0 \\\\ 1 \\end{bmatrix}^T$：', text)
    
    # 113
    text = re.sub(r'一、\s*試求常微分方程式[\s\S]*?之通解。（20 分）',
                  r'一、 試求常微分方程式 $y\'\' + 4y\' + 5y = e^{-2x} \\csc x$ 之通解。（20 分）', text)
    text = re.sub(r'二、\s*試求一時間函數[\s\S]*?之拉普拉斯轉換[^\n]*',
                  r'二、 試求一時間函數 $f(t) = \\frac{1}{2\\beta^3} (\\sin \\beta t - \\beta t \\cos \\beta t),\\ t \\ge 0,\\ \\beta \\ne 0$ 之拉普拉斯轉換（Laplace Transform）$F(s)$。（10 分）', text)
    text = re.sub(r'三、\s*試以剩值定理[\s\S]*?之值。（20 分）',
                  r'三、 試以留數定理（Residue Theorem）求 $\\int_{-\\infty}^\\infty \\frac{1}{x^4 + 16} dx$ 之值。（20 分）', text)
    text = re.sub(r'四、\s*一矩陣[\s\S]*?A\s*，其轉置矩陣[\s\S]*?T\s*A\s*。',
                  r'四、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -5 & -6 \\end{bmatrix}$，其轉置矩陣 $\\mathbf{A}^T = \\begin{bmatrix} 0 & -5 \\\\ 1 & -6 \\end{bmatrix}$。', text)
    text = re.sub(r'滿足下列矩陣方程式，[\s\S]*?PA\s*A P\s*。',
                  r'滿足下列矩陣方程式：$\\mathbf{P}\\mathbf{A} + \\mathbf{A}^T\\mathbf{P} = -\\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}$。', text)
    text = re.sub(r'五、[\s\S]*?一曲線C，其表示式為[\s\S]*?r t[\s\S]*?，t 為參數',
                  r'五、\n\n* **(一)** 一曲線 $C$，其表示式為 $\\mathbf{r}(t) = [3t^2, 4t, 8t^4]$，$t$ 為參數', text)
    text = re.sub(r'試求一向量函數[\s\S]*?F[\s\S]*?之面積分[\s\S]*?S x[\s\S]*?9\s*S',
                  r'試求一向量函數 $\\mathbf{F} = 7x\\mathbf{i} + 3y\\mathbf{j} - z\\mathbf{k}$ 之面積分 $\\iint_S \\mathbf{F} \\cdot \\mathbf{n} dA$，其中 $\\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$', text)
    text = re.sub(r'六、[\s\S]*?聯合機率密度函數[\s\S]*?p x y[\s\S]*?其他區域。',
                  r'六、 $X$ 與 $Y$ 為兩隨機變數（Random variables），其聯合機率密度函數（Joint probability density function）為：\n$$p(x,y) = \\begin{cases} k e^{-x - 2y}, & 0 \\le x < \\infty,\\ 0 \\le y < \\infty \\\\ 0, & \\text{其他區域} \\end{cases}$$\n', text)
    
    # 112
    text = re.sub(r'假設\(x\) = \{-2x, -2 ≤x< 0[\s\S]*?20\s*。（20 分）',
                  r'假設 $f(x) = \\begin{cases} -2x, & -2 \\le x < 0 \\\\ 2x, & 0 \\le x < 2 \\end{cases}$，週期為 $4$。（20 分）', text)
    text = re.sub(r"y\(0\)=\s*y'\s*\(0\)=0，其中\(t\) = \{[\s\S]*?其他",
                  r"$y(0) = y'(0) = 0$，其中 $g(t) = \\begin{cases} 1, & 5 \\le t < 20 \\\\ 0, & \\text{其他} \\end{cases}$", text)
    text = re.sub(r'假設A =\[\s*1\s*3\s*0\s*0\s*0\s*1\s*1\s*3\s*1\], b =\[\s*2\s*4\s*6\], c =\[\s*1\s*6\s*7\]',
                  r'假設 $\\mathbf{A} = \\begin{bmatrix} 1 & 0 & 1 \\\\ 3 & 0 & 3 \\\\ 0 & 1 & 1 \\end{bmatrix}$，$\\mathbf{b} = \\begin{bmatrix} 2 \\\\ 4 \\\\ 6 \\end{bmatrix}$，$\\mathbf{c} = \\begin{bmatrix} 1 \\\\ 6 \\\\ 7 \\end{bmatrix}$', text)
    
    # 111
    text = re.sub(r'一、\s*1y\s*x\s*=\s*為[\s\S]*?0\s*x\s*x\s*之一解，試求其通解。（15 分）',
                  r'一、 已知 $y_1(x) = \\frac{1}{x}$ 為微分方程式 $x^2 \\frac{d^2y}{dx^2} - 2x \\frac{dy}{dx} + (2 - x^2) y = 0$ 之一解，試求其通解。（15 分）', text)
    text = re.sub(r'四、\s*矩陣\s*1\s*1\s*1\s*3\s*\[\s*\]\s*=\s*\|\s*\|\s*\[\s*\]\s*A\s*。',
                  r'四、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 3 \\end{bmatrix}$。', text)
    
    # 110
    text = re.sub(r'六、\s*3\s*0\s*2\s*0\s*2\s*0\s*2\s*0\s*0\s*A[\s\S]*?-\s*\[\s*\]',
                  r'六、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 3 & 0 & -2 \\\\ 0 & 2 & 0 \\\\ -2 & 0 & 0 \\end{bmatrix}$', text)
    text = re.sub(r"二、\s*求\s*2\s*2x\s*y\s*y e-\s*'\s*=\s*的通解[^\n]*",
                  r"二、 求常微分方程 $y' = y^2 e^{-2x}$ 的通解（General Solution）。（10 分）", text)
    
    # 109
    text = re.sub(r'求以下微分方程式的通解[\s\S]*?75\s*20[\s\S]*?。（20 分）',
                  r'一、 求以下微分方程式的通解：$\\frac{d^2y}{dx^2} - 10\\frac{dy}{dx} + 25y = 75x + 20$。（20 分）', text)
    text = re.sub(r'矩陣\s*7\s*2\s*3\s*13\s*2\s*7\s*8\s*2\s*2\s*A[\s\S]*?找出A的反矩陣\s*1\s*A-\s*。（20 分）',
                  r'五、 矩陣 $\\mathbf{A} = \\begin{bmatrix} -7 & 2 & -3 \\\\ 13 & 2 & -7 \\\\ 8 & 2 & -2 \\end{bmatrix}$，找出 $\\mathbf{A}$ 的反矩陣 $\\mathbf{A}^{-1}$。（20 分）', text)
    
    # 108
    text = re.sub(r'二、\s*試求矩陣[\s\S]*?3\s*0\s*0\s*2\s*0\s*1\s*0\s*0\s*2\s*A[\s\S]*?特徵向量（Eigenvectors）。（10 分）',
                  r'二、 試求矩陣 $\\mathbf{A} = \\begin{bmatrix} 2 & 0 & 0 \\\\ 1 & 0 & 2 \\\\ 0 & 0 & 3 \\end{bmatrix}$ 的特徵值（Eigenvalues）與特徵向量（Eigenvectors）。（10 分）', text)

    return text

print('Math cleaner rules defined.')
