import re
import os

def polish_all_files():
    replacements = [
        # 114 Engineering Math
        (r'#### 三、\s*求解以下初始值問題之常微分方程式[^\n]*\n（20 分）',
         r'#### 三、 求解以下初始值問題之常微分方程式：$y\'\'(t) + 4y\'(t) + 4y(t) = 0, y(0) = 1, y\'(0) = 3$。（20 分）'),
        (r'求得線性方程式Ax=b 之完整解', r'求得線性方程式 $\mathbf{A}\mathbf{x} = \mathbf{b}$ 之完整解'),
        (r'求得矩陣A 之零空間（Null Space）N\(A\)', r'求得矩陣 $\mathbf{A}$ 之零空間（Null Space）$N(\mathbf{A})$'),

        # 113 Engineering Math
        (r'#### 五、\s*\(一\)一曲線C，其表示式為[\s\S]*?單位切線向量。（10 分）',
         r'#### 五、\n\n* **(一)** 一曲線 $C$，其表示式為 $\mathbf{r}(t) = [3t^2, 4t, 8t^4]$，$t$ 為參數，試求其切線向量與單位切線向量。（10 分）'),
        (r'\* \*\*(二)\*\* 試求一向量函數[\s\S]*?S: x\^2 \+ y\^2 \+ z\^2 = 9',
         r'* **(二)** 試求一向量函數 $\mathbf{F} = 7x\mathbf{i} + 3y\mathbf{j} - z\mathbf{k}$ 之面積分 $\iint_S \mathbf{F} \cdot \mathbf{n} dA$，其中 $\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$（10 分）'),

        # 112 Engineering Math
        (r'F\(t\)=\[cos\(t\)\+tsin\(t\)\] i\+\[sin\(t\)−tcos\(t\)\] j\+t2 k',
         r'$\mathbf{F}(t) = [\cos(t) + t\sin(t)]\mathbf{i} + [\sin(t) - t\cos(t)]\mathbf{j} + t^2\mathbf{k}$'),
        (r'單位切線向量（Unit Tangent Vector）T\(t\)與曲率（Curvature）κ\(t\)',
         r'單位切線向量（Unit Tangent Vector）$\mathbf{T}(t)$ 與曲率（Curvature）$\kappa(t)$'),
        (r'滿足線性方程組\[ܣ\s*ܾ\]ݔ=\s*ܿ之所有解',
         r'滿足線性方程組 $[\mathbf{A} \quad \mathbf{b}]\mathbf{x} = \mathbf{c}$ 之所有解'),
        (r'向量ݔ=\s*\[ݔଵ ݔଶ ݔଷ ݔସ\]்',
         r'向量 $\mathbf{x} = [x_1, x_2, x_3, x_4]^T$'),

        # 111 Engineering Math
        (r'試求\s*\* \*\*(一)\*\*[\s\S]*?dz[\s\S]*?\(10 分\)\s*\* \*\*(二)\*\*[\s\S]*?dz[\s\S]*?\(10 分\)',
         r'試求：\n\n* **(一)** $\oint_C \frac{z^2 + 1}{(z + 3)(z - 1)} dz$（10 分）\n\n* **(二)** $\oint_C \frac{z^2 + 1}{(z + 3)(z - 1)^2} dz$（10 分）'),
        (r'已知向量函數[\s\S]*?xyzk[\s\S]*?試求其散度',
         r'已知向量函數 $\mathbf{F} = (x^2 + y^2)\sin z\mathbf{i} + (x^3 + 2y^2 z)\mathbf{j} + (4\cos xy + z^2)\mathbf{k}$，試求其散度'),
        (r'試求從點：\(0,1,2\)至點：\(1,-1,7\)之線積分[\s\S]*?dz[\s\S]*?\(10 分\)',
         r'試求從點 $(0,1,2)$ 至點 $(1,-1,7)$ 之線積分 $\int_C (2x + y^2) dx + (2xy + z^2) dy + (2yz + 3) dz$（10 分）'),
        (r'其機率密度函數為[\s\S]*?p x x[\s\S]*?其他區域',
         r'其機率密度函數為：\n$$p(x) = \begin{cases} x, & 0 \le x \le 1 \\ 2 - x, & 1 < x \le 2 \\ 0, & \text{其他區域} \end{cases}$$\n'),

        # 110 Engineering Math
        (r'#### 一、\s*2\s*0\s*\( \)\s*2\s*\( \)\s*t\s*f t\s*t\s*f t\s*e d[\s\S]*?求解\s*\( \)\s*f t\s*。（10 分）',
         r'#### 一、 已知積分方程式 $f(t) = t^2 + 2\int_0^t f(\tau) e^{-(t-\tau)} d\tau$，求解 $f(t)$。（10 分）'),
        (r'#### 三、\s*求\s*2\s*\( \)\s*f x\s*x\s*x\s*=\s*-\s*的傅立葉展開',
         r'#### 三、 求 $f(x) = x - x^2,\ -\pi \le x \le \pi$ 的傅立葉展開（Fourier Expansion）。（20 分）'),
        (r'#### 四、\s*曲線C 的參數表示式為[\s\S]*?求\s*z\s*c xdx[\s\S]*?。（10 分）',
         r'#### 四、 曲線 $C$ 的參數表示式為 $x = t^3, y = -t, z = t^2$；其中 $1 \le t \le 2$，求線積分 $\int_C x dx + yz dy + e^{-z} dz$。（10 分）'),
        (r'#### 五、\s*求\s*2\s*2\s*2\s*\( , , \)\s*f x y z[\s\S]*?方向的改變率',
         r'#### 五、 求純量函數 $f(x,y,z) = x^2 y - xy^2 + xz^2$ 在點 $(1,-1,1)$ 沿 $(1,-2,1)$ 方向的方向導數（Rate of Change）。（10 分）'),
        (r'#### 七、\s*機率函數\( \)\s*\( 1\)\s*p x\s*a x\s*=\s*\+[\s\S]*?變異數（variance）。（20 分）',
         r'#### 七、 機率密度函數 $p(x) = a(x + 1)$，其中 $0 \le x \le 2$，求常數 $a$、該機率函數的期望值（Expected Value）及變異數（Variance）。（20 分）'),

        # 109 Engineering Math
        (r'求雙重積分[\s\S]*?dA\s*，其中R 為在第一象限被[\s\S]*?圍起來的區域。（20 分）',
         r'求雙重積分 $\iint_R x e^{y^2} dA$，其中 $R$ 為在第一象限被 $y = x^2$、$y = 4$、$x = 0$ 所圍起來的區域。（20 分）'),
        (r'隨機變數X 和Y 的聯合機率密度函數為[\s\S]*?otherwise\s*，求機率\s*\[ \]\s*P X\s*Y\s*>',
         r'隨機變數 $X$ 和 $Y$ 的聯合機率密度函數為：\n$$f_{X,Y}(x,y) = \begin{cases} \frac{1}{15}, & 0 \le x \le 5,\ 0 \le y \le 3 \\ 0, & \text{otherwise} \end{cases}$$\n求機率 $P[X > Y]$。（20 分）'),
        (r'\( \) f x 是週期2π的函數，當[\s\S]*?三角傅立葉級數',
         r'$f(x)$ 是週期為 $2\pi$ 的函數，當 $-\pi < x < \pi$ 時，$f(x) = |x| - \pi$，請將 $f(x)$ 展開為三角傅立葉級數（Trigonometric Fourier Series）的型式。（20 分）'),

        # 108 Engineering Math
        (r'#### 一、\s*試求下列微分方程之完全解[\s\S]*?2\s*2\s*2\s*2\s*\+[\s\S]*?。（20 分）',
         r'#### 一、 試求下列微分方程之完全解（Complete Solution）：$(x + a)^2 \frac{d^2y}{dx^2} - 2(x + a)\frac{dy}{dx} + 2y = 3(x + a)^2 + 1$。（20 分）'),
        (r'空間中任何點的溫度函數為[\s\S]*?T\s*\+[\s\S]*?=\s*。',
         r'空間中任何點的溫度函數為 $T(x,y,z) = xy + yz + zx$。'),
        (r'已知向量[\s\S]*?F[\s\S]*?及封閉曲面[\s\S]*?S[\s\S]*?試求[\s\S]*?其中n\^ 為dA',
         r'已知向量 $\mathbf{F} = x\hat{\mathbf{i}} + y\hat{\mathbf{j}} + z\hat{\mathbf{k}}$ 及封閉曲面 $S: x^2 + y^2 + z^2 = 1$，試求 $\iint_S \mathbf{F} \cdot \hat{\mathbf{n}} dA$，其中 $\hat{\mathbf{n}}$ 為 $dA$ 指向外的法線方向單位向量。（10 分）'),
        (r'在以下兩狀況，試求∫[\s\S]*?dz[\s\S]*?1\s*2\s*之值',
         r'在以下兩狀況，試求複數積分 $\oint_C \frac{1}{z^2 - 1} dz$ 之值'),
        (r'假設X 為隨機變數[\s\S]*?Var\s*。（10 分）',
         r'假設 $X$ 為隨機變數，且 $X$ 的期望值 $E(X) = 2$，$X(X - 4)$ 的期望值 $E[X(X - 4)] = 5$，試求：\n\n* **(一)** $X^2$ 的期望值 $E(X^2)$。（5 分）\n\n* **(二)** $4X + 10$ 的期望值 $E(4X + 10)$。（5 分）\n\n* **(三)** $4X + 10$ 的變異數與標準差 $\\text{Var}(4X + 10)$ 與 $\\sigma(4X + 10)$。（10 分）')
    ]

    for root, dirs, files in os.walk('依考科分類'):
        for file in files:
            if file.endswith('.md'):
                fpath = os.path.join(root, file)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pat, repl in replacements:
                    content = re.sub(pat, lambda m: repl, content)

                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print('Polished file:', fpath)

polish_all_files()
