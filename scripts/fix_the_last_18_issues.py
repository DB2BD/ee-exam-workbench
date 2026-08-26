# -*- coding: utf-8 -*-
"""
fix_the_last_18_issues.py
=========================
Fixes the final 18 issues to reach a perfect 0 delimiter errors.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 02 Electronics compiler
for f in [
    '依考科分類/02_電子學_含電力電子.md',
    '依考科分類/02_電子學_含電力電子/02_電子學_含電力電子_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace(
            "$$i(t) = 7 + 12 sin(ωt + 30o)+5 sin(3ωt + 60o)，計算：",
            "$i(t) = 7 + 12\\sin(\\omega t + 30^\\circ) + 5\\sin(3\\omega t + 60^\\circ)$，計算："
        )
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 2. 03 Eng Math compiler
for f in [
    '依考科分類/03_工程數學.md',
    '依考科分類/03_工程數學/03_工程數學_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace("#### 五、 假設矩陣 $\\mathbf{A} =\n", "#### 五、 假設矩陣 $\\mathbf{A}$：\n")
        c = c.replace("#### 四、 設矩陣 $\\mathbf{A} =\n", "#### 四、 設矩陣 $\\mathbf{A}$：\n")
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 3. 04 Machine compiler
for f in [
    '依考科分類/04_電機機械.md',
    '依考科分類/04_電機機械/04_電機機械_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace(
            "$$\\mathcal{R}(\\theta) = \\mathcal{R}_0 - \\mathcal{R}_1\\cos(4\\theta)，\\quad \\text{其中 } \\theta = \\omega_m t + \\delta, \\quad \\mathcal{R}_0 = 2 \\times 10^5, \\quad \\mathcal{R}_1 = 1 \\times 10^5$$",
            "$$\n\\mathcal{R}(\\theta) = \\mathcal{R}_0 - \\mathcal{R}_1\\cos(4\\theta)，\\quad \\text{其中 } \\theta = \\omega_m t + \\delta, \\quad \\mathcal{R}_0 = 2 \\times 10^5, \\quad \\mathcal{R}_1 = 1 \\times 10^5\n$$"
        )
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 4. 05 Power compiler
for f in [
    '依考科分類/05_電力系統.md',
    '依考科分類/05_電力系統/05_電力系統_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace(
            "圖中之阻抗分別為：線路每相阻抗 $\\mathbf{Z}_l =\n",
            "圖中之阻抗分別為：線路每相阻抗 $\\mathbf{Z}_l$：\n"
        )
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 5. 06 Distribution compiler
for f in [
    '依考科分類/06_工業配電.md',
    '依考科分類/06_工業配電/06_工業配電_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace("每部發電機的次暫態電抗同為 $25\\%", "每部發電機的次暫態電抗同為 $25\\%$")
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 6. 114 Electronics
p114e = os.path.join(WORKSPACE, '📝 個人題解與錯題本/02_電子學_含電力電子/114年_電子學_全卷完整詳細題解.md')
with open(p114e, 'r', encoding='utf-8') as fp:
    c = fp.read()
c = c.replace(
    "> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$",
    "> \n> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$\n>"
)
with open(p114e, 'w', encoding='utf-8') as fp:
    fp.write(c)

# 7. 114 Distribution
p114d = os.path.join(WORKSPACE, '📝 個人題解與錯題本/06_工業配電/114年_工業配電_全卷完整詳細題解.md')
with open(p114d, 'r', encoding='utf-8') as fp:
    lines = fp.readlines()
for i, l in enumerate(lines):
    if '容量比（Capacity Ratio）：' in l:
        lines[i] = "- **容量比（Capacity Ratio）**： $\\frac{S_V}{S_\\Delta} = \\frac{\\sqrt{3} S_{1\\phi}}{3 S_{1\\phi}} = \\frac{1}{\\sqrt{3}} \\approx 57.7\\%$\n"
    elif '利用率（Utilization Factor）：' in l:
        lines[i] = "- **利用率（Utilization Factor）**： $\\frac{S_V}{2 S_{1\\phi}} = \\frac{\\sqrt{3} S_{1\\phi}}{2 S_{1\\phi}} = \\frac{\\sqrt{3}}{2} \\approx 86.6\\%$\n"
with open(p114d, 'w', encoding='utf-8') as fp:
    fp.writelines(lines)

# 8. GK 113 Eng Math
pgk113 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/03_工程數學/GK_113年_工程數學_全卷完整詳細題解.md')
with open(pgk113, 'r', encoding='utf-8') as fp:
    c = fp.read()
c = c.replace(
    "## 二、 線性系統與零空間：已知矩陣 $A = \\begin{bmatrix} 1 & 2 & 0 & 1 \\\\ 2 & 4 & 1 & 4 \\\\ 3 & 6 & 1 & 5 \\end{bmatrix}\n",
    "## 二、 線性系統與零空間：已知矩陣 $A = \\begin{bmatrix} 1 & 2 & 0 & 1 \\\\ 2 & 4 & 1 & 4 \\\\ 3 & 6 & 1 & 5 \\end{bmatrix}$\n"
)
with open(pgk113, 'w', encoding='utf-8') as fp:
    fp.write(c)

print("🎉 Successfully patched the final 18 issues!")
