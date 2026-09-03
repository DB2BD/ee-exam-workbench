# -*- coding: utf-8 -*-
"""
fix_remaining_38_issues.py
==========================
Cleanly and decisively resolves all 38 remaining delimiter issues.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_content(content):
    # 1. Eng Math matrices in question headers:
    # "已知矩陣 $A$： \begin{bmatrix}" -> "已知矩陣 $A = \begin{bmatrix}"
    content = re.sub(
        r'已知矩陣\s+\$A\$[：:]\s*\\begin\{bmatrix\}',
        r'已知矩陣 $A = \\begin{bmatrix}',
        content
    )
    content = re.sub(
        r'求矩陣\s+\$A\$[：:]\s*\\begin\{bmatrix\}',
        r'求矩陣 $A = \\begin{bmatrix}',
        content
    )
    content = re.sub(
        r'設矩陣\s+\$A\$[：:]\s*\\begin\{bmatrix\}',
        r'設矩陣 $A = \\begin{bmatrix}',
        content
    )
    content = re.sub(
        r'假設矩陣\s+\$\\mathbf\{A\}\$[：:]\s*\\begin\{bmatrix\}',
        r'假設矩陣 $\\mathbf{A} = \\begin{bmatrix}',
        content
    )
    content = re.sub(
        r'設矩陣\s+\$\\mathbf\{A\}\$[：:]\s*\\begin\{bmatrix\}',
        r'設矩陣 $\\mathbf{A} = \\begin{bmatrix}',
        content
    )
    content = re.sub(
        r'#### 五、 假設矩陣 \$\\mathbf\{A\} =$',
        r'#### 五、 假設矩陣 $\\mathbf{A}$：',
        content
    )
    content = re.sub(
        r'#### 四、 設矩陣 \$\\mathbf\{A\} =$',
        r'#### 四、 設矩陣 $\\mathbf{A}$：',
        content
    )

    # 2. Electric Machinery 114
    content = content.replace(
        r'$$\mathcal{R}(θ) = \mathcal{R}0 -\mathcal{R}1cos4θ，其中θ= ωmt + δ、\mathcal{R}0 = 2 ×105、\mathcal{R}1 =',
        r'$$\mathcal{R}(\theta) = \mathcal{R}_0 - \mathcal{R}_1\cos(4\theta)，\quad \text{其中 } \theta = \omega_m t + \delta, \quad \mathcal{R}_0 = 2 \times 10^5, \quad \mathcal{R}_1 = 1 \times 10^5$$'
    )

    # 3. Power Systems
    content = content.replace(
        r'y12= -j10 pu，系統基準值為100\text{ MVA}$，很明顯地從匯流排1 經輸電線',
        r'$y_{12} = -j10\text{ pu}$，系統基準值為 $100\text{ MVA}$，很明顯地從匯流排 1 經輸電線'
    )
    content = content.replace(
        r'額定為100\text{ MVA}$，$20\text{ kV}$ 的同步發電機',
        r'額定為 $100\text{ MVA}$、$20\text{ kV}$ 的同步發電機'
    )
    content = content.replace(
        r'變壓器：$25\text{ MVA}$，$$22.8\text{ kV} / 3.3\text{ kV}$，XT=8\%，',
        r'變壓器：$25\text{ MVA}$，$22.8\text{ kV} / 3.3\text{ kV}$，$X_T = 8\%$，'
    )

    # 4. Circuit 104
    content = content.replace(
        "- g_{11} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}, \\quad g_{21} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}$$（埠 2 開路條件）",
        "- $g_{11} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}, \\quad g_{21} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}$（埠 2 開路條件）"
    )
    content = content.replace(
        "- g_{12} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}, \\quad g_{22} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}$$（埠 1 短路條件）",
        "- $g_{12} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}, \\quad g_{22} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}$（埠 1 短路條件）"
    )

    # 5. Electronics 114
    content = content.replace(
        "> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$\n",
        "> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$\n\n"
    )

    # 6. Eng Math 105, 109, 110
    content = content.replace(
        "$\\begin{bmatrix} -1 \\\\ 3 \\end{bmatrix}$，求 $T\\begin{bmatrix} 7 \\\\ 6 \\end{bmatrix}。（10 分）",
        "$= \\begin{bmatrix} -1 \\\\ 3 \\end{bmatrix}$，求 $T\\begin{bmatrix} 7 \\\\ 6 \\end{bmatrix}$。（10 分）"
    )
    content = content.replace("：$$$", "：")

    # 7. Distribution 114
    content = content.replace(
        "- 容量比（Capacity Ratio）：$\\frac{S_V}{S_\\Delta} = \\frac{\\sqrt{3} S_{1\\phi}}{3 S_{1\\phi}} = \\frac{1}{\\sqr\n",
        "- 容量比（Capacity Ratio）：$\\frac{S_V}{S_\\Delta} = \\frac{\\sqrt{3} S_{1\\phi}}{3 S_{1\\phi}} = \\frac{1}{\\sqrt{3}} \\approx 57.7\\%$\n"
    )
    content = content.replace(
        "- 利用率（Utilization Factor）：$\\frac{S_V}{2 S_{1\\phi}} = \\frac{\\sqrt{3} S_{1\\phi}}{2 S_{1\\phi}} = \\frac{\n",
        "- 利用率（Utilization Factor）：$\\frac{S_V}{2 S_{1\\phi}} = \\frac{\\sqrt{3} S_{1\\phi}}{2 S_{1\\phi}} = \\frac{\\sqrt{3}}{2} \\approx 86.6\\%$\n"
    )

    # 8. GK 112
    content = content.replace(
        ", \\mathbf{x}(0) = \\begin{bmatrix} 1 \\\\ 2 \\end{bmatrix}$，利用矩陣指數 $e^{At}$求解。（20 分）",
        "$\\mathbf{x}(0) = \\begin{bmatrix} 1 \\\\ 2 \\end{bmatrix}$，利用矩陣指數 $e^{At}$ 求解。（20 分）"
    )

    return content

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        orig = f.read()
    content = fix_content(orig)
    if content != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if fix_file(f):
            count += 1
            print(f"🎯 Cleaned: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
