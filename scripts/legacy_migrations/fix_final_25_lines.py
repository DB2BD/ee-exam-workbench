# -*- coding: utf-8 -*-
"""
fix_final_25_lines.py
=====================
Pristine resolution of the final 25 lines.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_content(c):
    # 1. 03 Eng Math
    c = c.replace(
        "#### 五、 假設矩陣 $\\mathbf{A}$：\n\\begin{bmatrix} 0 & 1 \\\\ -1 & 0 \\\\ 0 & 1 \\\\ -1 & 0 \\end{bmatrix}$ 與向量",
        "#### 五、 假設矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -1 & 0 \\\\ 0 & 1 \\\\ -1 & 0 \\end{bmatrix}$ 與向量"
    )
    c = c.replace(
        "## 四、 假設矩陣 $\\mathbf{A}$：\n\\begin{bmatrix} 1 & 0 & 1 \\\\ 3 & 0 & 3 \\\\ 0 & 1 & 1 \\end{bmatrix}$，向量",
        "## 四、 假設矩陣 $\\mathbf{A} = \\begin{bmatrix} 1 & 0 & 1 \\\\ 3 & 0 & 3 \\\\ 0 & 1 & 1 \\end{bmatrix}$，向量"
    )

    # 2. 06 Industrial Distribution
    c = c.replace("3. 45\\text{ kV}$/480 V", "$3.45\\text{ kV} / 480\\text{ V}$")
    c = c.replace("11. 4\\text{ kV}$/380V", "$11.4\\text{ kV} / 380\\text{ V}$")

    # 3. Career strategy
    c = c.replace(
        "\\text{總報酬 (Total Comp)} = \\text{Base Salary (USD/SGD)} + \\text{Expat Uplift (30\\% ~ 70\\%)} + \\text{Site Allowance} + \\text{Performance Bonus}\n",
        "$$\\text{總報酬 (Total Comp)} = \\text{Base Salary (USD/SGD)} + \\text{Expat Uplift (30\\% ~ 70\\%)} + \\text{Site Allowance} + \\text{Performance Bonus}$$\n"
    )

    # 4. Circuit 105, 107, 112, 113, 114
    c = c.replace(
        "(3V_2 + 8) - V_2 - \\left( V_2 + \\frac{28}{3} \\right) = - 4$\n",
        "$$(3V_2 + 8) - V_2 - \\left( V_2 + \\frac{28}{3} \\right) = -4$$\n"
    )
    c = c.replace("$$20\\ \\Omega$ 頂部對地電位：", "$20\\ \\Omega$ 頂部對地電位：")
    c = c.replace(
        "- 反映阻抗：$\\mathbf{Z}_r = \\frac{(\\omega M)^2}{\\mathbf{Z}_{22}} = \\frac{40^2}{100 + j100} = 8 - j8\\ \\Omega\n",
        "- 反映阻抗：$\\mathbf{Z}_r = \\frac{(\\omega M)^2}{\\mathbf{Z}_{22}} = \\frac{40^2}{100 + j100} = 8 - j8\\ \\Omega$\n"
    )
    c = c.replace(
        "- 15\\ \\Omega$ 電阻串聯後續兩枚 $6\\ \\Omega$ 並聯電阻：",
        "- $15\\ \\Omega$ 電阻串聯後續兩枚 $6\\ \\Omega$ 並聯電阻："
    )
    c = c.replace(
        "- 2V_x$ 電壓源左側節點電位為",
        "- $2V_x$ 電壓源左側節點電位為"
    )

    # 5. Power 106, 108, 109, 107
    c = re.sub(r'(\s*[-*]\s+)\$\s*(\*\*Bus\s+\d+\*\*)', r'\1\2', c)
    c = c.replace(
        "$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})$$",
        "$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})$$"
    )
    c = c.replace(
        "$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})\n",
        "$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})$$\n"
    )

    # 6. Distribution 104
    c = c.replace(
        "$$\\mathbf{Z}_{5,C} = j(5 \\times 0.06 X_C - \\frac{X_C}{5}) = j(0.30 - 0.20)X_C = +j0.10 X_C\\text{ (呈感性！)}\n",
        "$$\\mathbf{Z}_{5,C} = j(5 \\times 0.06 X_C - \\frac{X_C}{5}) = j(0.30 - 0.20)X_C = +j0.10 X_C\\text{ (呈感性！)}$$\n"
    )

    # 7. GK 114 Power
    c = c.replace(
        "y = j4.2 \\times 10^{-6}\\,\\text{S/km} = 4.2 \\times 10^{-6}\\angle 90^\\circ\\,\\text{S/km}$，長度 $l = 300\\,\\text{km}$。",
        "$y = j4.2 \\times 10^{-6}\\,\\text{S/km} = 4.2 \\times 10^{-6}\\angle 90^\\circ\\,\\text{S/km}$，長度 $l = 300\\,\\text{km}$。"
    )

    return c

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
