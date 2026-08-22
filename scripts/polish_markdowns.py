import fitz
import glob
import os
import re

# Comprehensive math replacements for each subject
def polish_engineering_math(text, year):
    # 114
    if year == '114':
        text = text.replace('二、 計算∫e17మ\n⁄\ndz，其中路徑C 為下圖所示複數平面z = x+iy 上，圓心在\n原點O 之單位圓。（15 分）',
                            '#### 二、 計算 $\\oint_C \\frac{e^{1/z^2}}{z} dz$（或 $\\oint_C e^{1/z^2} dz$），其中路徑 $C$ 為下圖所示複數平面 $z = x + iy$ 上，圓心在原點 $O$ 之單位圓。（15 分）')
        text = text.replace('三、 求解以下初始值問題之常微分方程式：y(2)+4y(1)+4y=0, y(0)=1, y(1)=3。\n（20 分）',
                            '#### 三、 求解以下初始值問題之常微分方程式：$y\'\'(t) + 4y\'(t) + 4y(t) = 0, y(0) = 1, y\'(0) = 3$。（20 分）')
        text = text.replace('四、 假設週期函數(x)之週期為2f，(x) = {0, -π < x ≤0\nx, 0 < x≤f。計算(x)之傅\n氏級數（Fourier Series）。（20 分）',
                            '#### 四、 假設週期函數 $f(x)$ 之週期為 $2\\pi$：\n$$f(x) = \\begin{cases} 0, & -\\pi < x \\le 0 \\\\ x, & 0 < x \\le \\pi \\end{cases}$$\n計算 $f(x)$ 之傅立葉級數（Fourier Series）。（20 分）')
        text = text.replace('五、 假設矩陣A = [0\n-1\n0\n1\n0\n1\n-1\n0]與b=[0, 1]\nT。',
                            '#### 五、 假設矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -1 & 0 \\\\ 0 & 1 \\\\ -1 & 0 \\end{bmatrix}$ 與 $\\mathbf{b} = \\begin{bmatrix} 0 \\\\ 1 \\end{bmatrix}^T$：')
    
    # 113
    elif year == '113':
        text = text.replace("#### 一、 試求常微分方程式\n2\n'' 4 ' 5\ncsc\nx\ny\ny\ny\ne\nx\n+\n+\n=\n之通解（General Solution）。（15 分）",
                            "#### 一、 試求常微分方程式 $y'' + 4y' + 5y = e^{-2x} \\csc x$ 之通解（General Solution）。（15 分）")
        text = text.replace("#### 二、 試求週期為2 之週期函數\n2\n, 0 1\n( )\n2\n, 1 2\nt\nt\nf t\nt\nt\n≤ <\n⎧\n=\n⎨\n−\n≤ <\n⎩\n之拉普拉斯轉換（Laplace\nTransform）L{f(t)}。（15 分）",
                            "#### 二、 試求週期 $T = 2$ 之週期函數：\n$$f(t) = \\begin{cases} t^2, & 0 \\le t < 1 \\\\ 2 - t, & 1 \\le t < 2 \\end{cases}$$\n之拉普拉斯轉換（Laplace Transform）$\\mathcal{L}\\{f(t)\\}$。（15 分）")
        text = text.replace("#### 三、 試求二階線性常微分方程組\n2\n4\nx\nx\ny\ny\nx\ny\n′\n⎧\n= −\n⎨\n′\n= −\n⎩\n之通解，其中\n,\ndx\ndy\nx\ny\ndt\ndt\n′\n′\n≡\n≡\n。（15 分）",
                            "#### 三、 試求二階線性常微分方程組：\n$$\\begin{cases} x'(t) = -2x(t) + y(t) \\\\ y'(t) = -4x(t) - y(t) \\end{cases}$$\n之通解，其中 $x' \\equiv \\frac{dx}{dt}, y' \\equiv \\frac{dy}{dt}$。（15 分）")
    
    # 112
    elif year == '112':
        text = text.replace("假設(x) = {-2x, -2 ≤x< 0\n2x,   0 ≤x< 20  。（20 分）",
                            "假設 $f(x) = \\begin{cases} -2x, & -2 \\le x < 0 \\\\ 2x, & 0 \\le x < 2 \\end{cases}$，週期為 $4$。（20 分）")
        text = text.replace("y(0)= y' (0)=0，其中(t) = {\n1,             5 ≤t< 20\n0,             其他",
                            "$y(0) = y'(0) = 0$，其中 $g(t) = \\begin{cases} 1, & 5 \\le t < 20 \\\\ 0, & \\text{其他} \\end{cases}$")
        text = text.replace("假設A =[\n1\n3\n0\n0\n0\n1\n1\n3\n1], b =[\n2\n4\n6], c =[\n1\n6\n7]",
                            "假設 $\\mathbf{A} = \\begin{bmatrix} 1 & 0 & 1 \\\\ 3 & 0 & 3 \\\\ 0 & 1 & 1 \\end{bmatrix}$，$\\mathbf{b} = \\begin{bmatrix} 2 \\\\ 4 \\\\ 6 \\end{bmatrix}$，$\\mathbf{c} = \\begin{bmatrix} 1 \\\\ 6 \\\\ 7 \\end{bmatrix}$")
    
    # 111
    elif year == '111':
        text = text.replace("一、 1y\nx\n=\n為\n2\n2\n2\n+ 2\nd y\ndy\nx\ny\ndx\nd x\n-\n-\n=\n2\n(\n)\n0\nx\nx\n之一解，試求其通解。（15 分）",
                            "#### 一、 已知 $y_1(x) = \\frac{1}{x}$ 為微分方程式 $x^2 \\frac{d^2y}{dx^2} - 2x \\frac{dy}{dx} + (2 - x^2) y = 0$ 之一解，試求其通解。（15 分）")
        text = text.replace("四、 矩陣\n1\n1\n1\n3\n[\n]\n=\n|\n|\n[\n]\nA\n。",
                            "#### 四、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 3 \\end{bmatrix}$。")
    
    # 110
    elif year == '110':
        text = text.replace("六、 3\n0\n2\n0\n2\n0\n2\n0\n0\nA\n-\n[\n]\n|\n|\n=\n|\n|\n|\n|\n-\n[\n]",
                            "#### 六、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 3 & 0 & -2 \\\\ 0 & 2 & 0 \\\\ -2 & 0 & 0 \\end{bmatrix}$")
        text = text.replace("二、 求\n2\n2x\ny\ny e-\n'=\n的通解（general solution）。（10 分）",
                            "#### 二、 求常微分方程 $y' = y^2 e^{-2x}$ 的通解（General Solution）。（10 分）")
    
    # 109
    elif year == '109':
        text = text.replace("求以下微分方程式的通解\n2\n2\n10\n25\n75\n20\nd y\ndy\ny\nx\ndx\ndx\n-\n+\n=\n+\n。（20 分）",
                            "#### 一、 求以下微分方程式的通解：$\\frac{d^2y}{dx^2} - 10\\frac{dy}{dx} + 25y = 75x + 20$。（20 分）")
        text = text.replace("矩陣\n7\n2\n3\n13\n2\n7\n8\n2\n2\nA\n-\n[\n]\n|\n|\n=-\n-\n|\n|\n|\n|\n-\n[\n]，找出A的反矩陣\n1\nA-。（20 分）",
                            "#### 五、 矩陣 $\\mathbf{A} = \\begin{bmatrix} -7 & 2 & -3 \\\\ 13 & 2 & -7 \\\\ 8 & 2 & -2 \\end{bmatrix}$，找出 $\\mathbf{A}$ 的反矩陣 $\\mathbf{A}^{-1}$。（20 分）")
    
    # 108
    elif year == '108':
        text = text.replace("二、 試求矩陣\n|\n|\n|\n[\n]\n[\n]\n|\n|\n|\n=\n3\n0\n0\n2\n0\n1\n0\n0\n2\nA\n的特徵值（Eigenvalues）與特徵向量（Eigenvectors）。（10 分）",
                            "#### 二、 試求矩陣 $\\mathbf{A} = \\begin{bmatrix} 2 & 0 & 0 \\\\ 1 & 0 & 2 \\\\ 0 & 0 & 3 \\end{bmatrix}$ 的特徵值（Eigenvalues）與特徵向量（Eigenvectors）。（10 分）")

    return text

def polish_circuits(text, year):
    if year == '114':
        text = text.replace('電流I = ?（5 分）', '電流 $I = ?$（5 分）')
        text = text.replace('節點電壓v1、v2、v3 分別為何？（15 分）', '節點電壓 $v_1, v_2, v_3$ 分別為何？（15 分）')
        text = text.replace('端點a-b 所視之諾\n頓等效電路圖（Norton’s equivalent circuit）。（20 分）', '端點 $a-b$ 所視之諾頓等效電路圖（Norton’s equivalent circuit）。（20 分）')
        text = text.replace('開關打開瞬間，v(t = 0) = ?；i(t = 0) = ?（10 分）', '開關打開瞬間，$v(0^+) = ?$；$i(0^+) = ?$（10 分）')
        text = text.replace('v(t > 0)之表示式為何？（10 分）', '$v(t > 0)$ 之表示式為何？（10 分）')
        text = text.replace('求vo(t)之交流輸出響應。（20 分）', '求 $v_o(t)$ 之交流輸出響應。（20 分）')
        text = text.replace('求vo(t > 0)之表示式。（20 分）', '求 $v_o(t > 0)$ 之表示式。（20 分）')
    elif year == '113':
        text = text.replace('圖一所示為含流控相依電流源之直流電路', '如圖一所示為含流控相依電流源之直流電路')
    return text

# Comprehensive master builder
def process_all_markdowns():
    subj_dirs = {
        '01_電路學': '電路學',
        '02_電子學_含電力電子': '電子學（包括電力電子學）',
        '03_工程數學': '工程數學',
        '04_電機機械': '電機機械',
        '05_電力系統': '電力系統',
        '06_工業配電': '工業配電'
    }
    
    for folder, sname in subj_dirs.items():
        folder_path = os.path.join('依考科分類', folder)
        md_file = os.path.join(folder_path, f'{folder}_歷屆試題彙編_104-114年.md')
        top_md_file = os.path.join('依考科分類', f'{folder}.md')
        
        if not os.path.exists(md_file):
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Refine content
        if folder == '03_工程數學':
            for y in ['114', '113', '112', '111', '110', '109', '108']:
                content = polish_engineering_math(content, y)
        elif folder == '01_電路學':
            for y in ['114', '113']:
                content = polish_circuits(content, y)
                
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Top-level version
        top_content = content
        top_content = top_content.replace('(./images/', f'(./{folder}/images/')
        top_content = top_content.replace('](./images/', f'](./{folder}/images/')
        top_content = top_content.replace('(./', f'(./{folder}/')
        top_content = top_content.replace('](./', f'](./{folder}/')
        
        with open(top_md_file, 'w', encoding='utf-8') as f:
            f.write(top_content)
            
    print('Markdown files polished and synchronized with LaTeX typography!')

process_all_markdowns()
