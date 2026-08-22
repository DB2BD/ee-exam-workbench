import re
import os

def polish_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 114 Engineering Math
    text = re.sub(r'#### 二、\s*計算∫e17మ[\s\S]*?原點O 之單位圓。（15 分）',
                  lambda m: r'#### 二、 計算 $\oint_C e^{1/z^2} dz$，其中路徑 $C$ 為下圖所示複數平面 $z = x+iy$ 上，圓心在原點 $O$ 之單位圓。（15 分）', text)
    text = re.sub(r'#### 三、\s*求解以下初始值問題之常微分方程式：\$y\'\'\(t\) \+ 4y\'\(t\) \+ 4y\(t\) = 0, y\(0\) = 1, y\'\(0\) = 3\$。（20 分）\s*（20 分）',
                  lambda m: r'#### 三、 求解以下初始值問題之常微分方程式：$y\'\'(t) + 4y\'(t) + 4y(t) = 0, y(0) = 1, y\'(0) = 3$。（20 分）', text)

    # 113 Engineering Math
    text = re.sub(r'#### 二、\s*試求一時間函數[\s\S]*?換（Laplace Transform）F\(s\)。',
                  lambda m: r'#### 二、 試求一時間函數 $f(t) = \frac{1}{2\beta^3}(\sin \beta t - \beta t \cos \beta t),\ t \ge 0,\ \beta \ne 0$ 之拉普拉斯轉換（Laplace Transform）$F(s)$。', text)
    text = re.sub(r'#### 四、\s*一矩陣[\s\S]*?A\s*。',
                  lambda m: r'#### 四、 矩陣 $\mathbf{A} = \begin{bmatrix} 0 & 1 \\ -5 & -6 \end{bmatrix}$，其轉置矩陣 $\mathbf{A}^T = \begin{bmatrix} 0 & -5 \\ 1 & -6 \end{bmatrix}$。', text)
    text = re.sub(r'滿足下列矩陣方程式，[\s\S]*?PA\s*A P\s*。',
                  lambda m: r'滿足下列矩陣方程式：$\mathbf{P}\mathbf{A} + \mathbf{A}^T\mathbf{P} = -\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}$。', text)

    # Circuit fixes
    text = re.sub(r'(\d+)\s*\n\s*R\s*=\s*Ω', lambda m: rf'$R_1 = {m.group(1)}\ \Omega$', text)
    text = re.sub(r'(\d+)\s*H\s*\n\s*L\s*=', lambda m: rf'$L = {m.group(1)}\text{{ H}}$', text)
    text = re.sub(r'(\d+)\s*H\s*\n\s*M\s*=', lambda m: rf'$M = {m.group(1)}\text{{ H}}$', text)

    # Clean double ####
    text = re.sub(r'#{4,}\s*', '#### ', text)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

# Apply to all subject markdown files
for root, dirs, files in os.walk('依考科分類'):
    for file in files:
        if file.endswith('.md'):
            fpath = os.path.join(root, file)
            polish_file(fpath)
            print('Polished:', fpath)

print('All subject markdown files polished successfully!')
