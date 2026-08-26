# -*- coding: utf-8 -*-
"""
fix_final_6_items.py
====================
Fixes the exact final 6 lines across the repository.
"""

import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. CLAUDE-SPEC.md
p1 = os.path.join(WORKSPACE, 'CLAUDE-SPEC.md')
if os.path.exists(p1):
    with open(p1, 'r', encoding='utf-8') as f:
        c1 = f.read()
    c1 = c1.replace("使用雙美元符號 `$$ ... `。", "使用雙美元符號 `$$ ... $$`。")
    with open(p1, 'w', encoding='utf-8') as f:
        f.write(c1)

# 2. CLAUDE.md
p2 = os.path.join(WORKSPACE, 'CLAUDE.md')
if os.path.exists(p2):
    with open(p2, 'r', encoding='utf-8') as f:
        c2 = f.read()
    c2 = c2.replace("獨立大公式或矩陣必須使用 `$ ... `，", "獨立大公式或矩陣必須使用 `$$ ... $$`，")
    with open(p2, 'w', encoding='utf-8') as f:
        f.write(c2)

# 3. 05 Power System compilers
for f in [
    '依考科分類/05_電力系統.md',
    '依考科分類/05_電力系統/05_電力系統_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace(r'24 - $j30\ \Omega$', r'24 - j30\ \Omega$')
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 4. 06 Industrial Distribution compilers
for f in [
    '依考科分類/06_工業配電.md',
    '依考科分類/06_工業配電/06_工業配電_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = c.replace(
            "次暫態電抗同為 $25\%$$，其經由一 100\\text{ MVA}$，",
            "次暫態電抗同為 $25\%$，其經由一 $100\\text{ MVA}$，"
        )
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

# 5. 114 Electronics
p5 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/02_電子學_含電力電子/114年_電子學_全卷完整詳細題解.md')
if os.path.exists(p5):
    with open(p5, 'r', encoding='utf-8') as f:
        c5 = f.read()
    c5 = c5.replace(
        "> \n> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$\n>",
        "> \n> $$\n> A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}\n> $$\n>"
    )
    with open(p5, 'w', encoding='utf-8') as f:
        f.write(c5)

# 6. GK 113 Eng Math
p6 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/03_工程數學/GK_113年_工程數學_全卷完整詳細題解.md')
if os.path.exists(p6):
    with open(p6, 'r', encoding='utf-8') as f:
        c6 = f.read()
    c6 = c6.replace(
        "## 二、 線性系統與零空間：已知矩陣 $A = \\begin{bmatrix} 1 & 2 & 0 & 1 \\\\ 2 & 4 & 1 & 4 \\\\ 3 & 6 & 1 & 5 \\end{bmatrix}，求其列空間",
        "## 二、 線性系統與零空間：已知矩陣 $A = \\begin{bmatrix} 1 & 2 & 0 & 1 \\\\ 2 & 4 & 1 & 4 \\\\ 3 & 6 & 1 & 5 \\end{bmatrix}$，求其列空間"
    )
    with open(p6, 'w', encoding='utf-8') as f:
        f.write(c6)

print("🎉 Successfully patched the final items!")
