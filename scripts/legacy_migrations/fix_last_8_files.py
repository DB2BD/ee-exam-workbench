# -*- coding: utf-8 -*-
"""
fix_last_8_files.py
===================
Cleanly fixes the remaining 8 files with unpaired $$ blocks.
"""

import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 105 Circuit
p1 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/01_電路學/105年_電路學_全卷完整詳細題解.md')
with open(p1, 'r', encoding='utf-8') as f:
    c1 = f.read()
c1 = c1.replace(
    "$$\nQ = \\frac{\\omega_0 L}{R} = \\frac{1000 \\times 1}{100} = 10 \\quad \\text{(完全相符！)}\n\n---",
    "$$\nQ = \\frac{\\omega_0 L}{R} = \\frac{1000 \\times 1}{100} = 10 \\quad \\text{(完全相符！)}\n$$\n\n---"
)
with open(p1, 'w', encoding='utf-8') as f:
    f.write(c1)

# 2. 114 Circuit
p2 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/01_電路學/114年_電路學_全卷完整詳細題解.md')
with open(p2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = c2.replace(
    "取反拉氏轉換：\n$$\n\\mathbf{v_o(t) = \\mathcal{L}^{-1}\\left\\{ \\frac{31.25}{s} - \\frac{31.25}{s + 4} \\right\\} = \\mathbf{31.25 (1 - e^{-4t}) u(t)\\text{ V}}}\n\n---",
    "取反拉氏轉換：\n$$\n\\mathbf{v_o(t) = \\mathcal{L}^{-1}\\left\\{ \\frac{31.25}{s} - \\frac{31.25}{s + 4} \\right\\} = \\mathbf{31.25 (1 - e^{-4t}) u(t)\\text{ V}}}\n$$\n\n---"
)
with open(p2, 'w', encoding='utf-8') as f:
    f.write(c2)

# 3. 104 Power Systems
p3 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/05_電力系統/104年_電力系統_全卷完整詳細題解.md')
with open(p3, 'r', encoding='utf-8') as f:
    c3 = f.read()
c3 = c3.replace(
    "1. **阻抗矩陣 $\\mathbf{Z}_{bus}$**：\n   \\mathbf{Z}_{bus} = \\begin{bmatrix}",
    "1. **阻抗矩陣 $\\mathbf{Z}_{bus}$**：\n   $$\\mathbf{Z}_{bus} = \\begin{bmatrix}"
)
with open(p3, 'w', encoding='utf-8') as f:
    f.write(c3)

# 4. GK 110 Electronics
p4 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/02_電子學_含電力電子/GK_110年_電子學_全卷完整詳細題解.md')
with open(p4, 'r', encoding='utf-8') as f:
    c4 = f.read()
c4 = c4.replace(
    "工作週期：\n$$\n\\mathbf{D = \\frac{t_H}{T} = \\frac{30}{50} = 60\\%}\n\n---",
    "工作週期：\n$$\n\\mathbf{D = \\frac{t_H}{T} = \\frac{30}{50} = 60\\%}\n$$\n\n---"
)
with open(p4, 'w', encoding='utf-8') as f:
    f.write(c4)

# 5. GK 110 Eng Math
p5 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/03_工程數學/GK_110年_工程數學_全卷完整詳細題解.md')
with open(p5, 'r', encoding='utf-8') as f:
    c5 = f.read()
c5 = c5.replace(
    "複變解析函數：\n$$\n$$f(z) = u + jv = (x^2 - y^2 + 2x) + j(2xy + 2y + C) = z^2 + 2z + jC$$",
    "複變解析函數：\n$$\nf(z) = u + jv = (x^2 - y^2 + 2x) + j(2xy + 2y + C) = z^2 + 2z + jC\n$$"
)
with open(p5, 'w', encoding='utf-8') as f:
    f.write(c5)

# 6. GK 111 Eng Math
p6 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/03_工程數學/GK_111年_工程數學_全卷完整詳細題解.md')
with open(p6, 'r', encoding='utf-8') as f:
    c6 = f.read()
c6 = c6.replace(
    "由高階積分公式：\n$$\n\\oint_{|z|=2} \\frac{\\cos z}{z^3} dz = \\frac{2\\pi j}{2!} f''(0) = \\frac{2\\pi j}{2} (-1) = \\mathbf{-\\pi j}\n\n---",
    "由高階積分公式：\n$$\n\\oint_{|z|=2} \\frac{\\cos z}{z^3} dz = \\frac{2\\pi j}{2!} f''(0) = \\frac{2\\pi j}{2} (-1) = \\mathbf{-\\pi j}\n$$\n\n---"
)
with open(p6, 'w', encoding='utf-8') as f:
    f.write(c6)

# 7. GK 113 Power Systems
p7 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/05_電力系統/GK_113年_電力系統_全卷完整詳細題解.md')
with open(p7, 'r', encoding='utf-8') as f:
    c7 = f.read()
c7 = c7.replace(
    "$$\n\\mathbf{P_2 = $\\frac{7.623}{0.018}$ \\approx 423.50\\,\\text{MW}}\n\n---",
    "$$\n\\mathbf{P_2 = \\frac{7.623}{0.018} \\approx 423.50\\,\\text{MW}}\n$$\n\n---"
)
c7 = c7.replace(
    "\\mathbf{P_1 = $\\frac{14.023 - 8.0}{0.016}$ = $\\frac{6.023}{0.016}$ \\approx 376.44\\,\\text{MW}}",
    "\\mathbf{P_1 = \\frac{14.023 - 8.0}{0.016} = \\frac{6.023}{0.016} \\approx 376.44\\,\\text{MW}}"
)
with open(p7, 'w', encoding='utf-8') as f:
    f.write(c7)

# 8. KB 03 RLC
p8 = os.path.join(WORKSPACE, '🧠 核心考點知識庫/01_電路學/03_一階與二階RLC暫態響應.md')
with open(p8, 'r', encoding='utf-8') as f:
    c8 = f.read()
c8 = c8.replace(
    "- $$\\alpha < \\omega_0$：**欠阻尼",
    "- $\\alpha < \\omega_0$：**欠阻尼"
)
with open(p8, 'w', encoding='utf-8') as f:
    f.write(c8)

print("🎉 Successfully patched the final 8 files!")
