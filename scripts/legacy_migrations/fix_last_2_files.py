# -*- coding: utf-8 -*-
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 104 Power Systems
p104 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/05_電力系統/104年_電力系統_全卷完整詳細題解.md')
with open(p104, 'r', encoding='utf-8') as f:
    c104 = f.read()
c104 = c104.replace(
    "$$\\mathbf{Z}_{bus} = \\begin{bmatrix}$$\nj0.225 & j0.150 & j0.150 \\\\\n   j0.150 & j0.240 & j0.160 \\\\\n   j0.150 & j0.160 & j0.260\n   \\end{bmatrix}\\text{ pu}\n$$",
    "$$\n\\mathbf{Z}_{bus} = \\begin{bmatrix}\nj0.225 & j0.150 & j0.150 \\\\\nj0.150 & j0.240 & j0.160 \\\\\nj0.150 & j0.160 & j0.260\n\\end{bmatrix}\\text{ pu}\n$$"
)
with open(p104, 'w', encoding='utf-8') as f:
    f.write(c104)

# 2. GK 113 Power Systems
pgk = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/05_電力系統/GK_113年_電力系統_全卷完整詳細題解.md')
with open(pgk, 'r', encoding='utf-8') as f:
    cgk = f.read()
cgk = cgk.replace(
    "$$\n\\mathbf{P_2 = $\\frac{14.023 - 6.4}{0.018}$ = $\\frac{7.623}{0.018}$ \\approx 423.50\\,\\text{MW}}\n\n---",
    "$$\n\\mathbf{P_2 = \\frac{14.023 - 6.4}{0.018} = \\frac{7.623}{0.018} \\approx 423.50\\,\\text{MW}}\n$$\n\n---"
)
cgk = cgk.replace(
    "* **系統微增成本**： $\\mathbf{\\lambda \\approx 14.02\\,\\text{NT\\$/MWh}}\n",
    "* **系統微增成本**： $\\mathbf{\\lambda \\approx 14.02\\,\\text{NT\\$/MWh}}$\n"
)
with open(pgk, 'w', encoding='utf-8') as f:
    f.write(cgk)

print("✅ Patched 104 and GK 113 Power Systems!")
