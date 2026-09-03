# -*- coding: utf-8 -*-
"""
fix_all_matrix_bold_and_percents.py
===================================
1. Strips \mathbf{ wrapping matrices: \mathbf{\begin{bmatrix} ... \end{bmatrix}} -> \begin{bmatrix} ... \end{bmatrix}
2. Escapes unescaped % inside math mode: X0 = 12% -> X0 = 12\%
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Fix GK 113 Circuit
pgk113c = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/01_電路學/GK_113年_電路學_全卷完整詳細題解.md')
if os.path.exists(pgk113c):
    with open(pgk113c, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(
        "$$\n\\mathbf{T =\n\\begin{bmatrix} 2 & 10\\,\\Omega \\\\ 0.1\\,\\text{S} & 1.5 \\end{bmatrix}\n}\n$$",
        "$$\n\\mathbf{T} = \\begin{bmatrix} 2 & 10\\,\\Omega \\\\ 0.1\\,\\text{S} & 1.5 \\end{bmatrix}\n$$"
    )
    c = c.replace(
        "\\mathbf{T = \\begin{bmatrix} 2 & 10\\,\\Omega \\\\ 0.1\\,\\text{S} & 1.5 \\end{bmatrix}}",
        "\\mathbf{T} = \\begin{bmatrix} 2 & 10\\,\\Omega \\\\ 0.1\\,\\text{S} & 1.5 \\end{bmatrix}"
    )
    with open(pgk113c, 'w', encoding='utf-8') as f:
        f.write(c)

# 2. Fix GK 110 Circuit
pgk110c = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/01_電路學/GK_110年_電路學_全卷完整詳細題解.md')
if os.path.exists(pgk110c):
    with open(pgk110c, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'\\mathbf\{H\s*=\s*\\begin\{bmatrix\}', r'\\mathbf{H} = \\begin{bmatrix}', c)
    c = c.replace(r'\end{bmatrix}}', r'\end{bmatrix}')
    with open(pgk110c, 'w', encoding='utf-8') as f:
        f.write(c)

# 3. Fix 113 Circuit
p113c = os.path.join(WORKSPACE, '📝 個人題解與錯題本/01_電路學/113年_電路學_全卷完整詳細題解.md')
if os.path.exists(p113c):
    with open(p113c, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'\\mathbf\{Y\}\(j\\omega\)\s*=\s*\\mathbf\{\s*\\begin\{bmatrix\}', r'\\mathbf{Y}(j\\omega) = \\begin{bmatrix}', c)
    c = c.replace(r'\text{ S}}', r'\text{ S}')
    with open(p113c, 'w', encoding='utf-8') as f:
        f.write(c)

# 4. Fix 111 Circuit
p111c = os.path.join(WORKSPACE, '📝 個人題解與錯題本/01_電路學/111年_電路學_全卷完整詳細題解.md')
if os.path.exists(p111c):
    with open(p111c, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'\\mathbf\{Z\}_\{bus\}\s*=\s*\\mathbf\{\s*\\begin\{bmatrix\}', r'\\mathbf{Z}_{bus} = \\begin{bmatrix}', c)
    c = re.sub(r'\\end\{bmatrix\}\s*\}', r'\\end{bmatrix}', c)
    with open(p111c, 'w', encoding='utf-8') as f:
        f.write(c)

# 5. Fix 106 Power Ybus matrix
p106p = os.path.join(WORKSPACE, '📝 個人題解與錯題本/05_電力系統/106年_電力系統_全卷完整詳細題解.md')
if os.path.exists(p106p):
    with open(p106p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(
        "$$\n\\mathbf{Y}_{bus} = \\begin{bmatrix}\n-j17.5 & j10 & j5 \\\\\nj10 & -j17.5 & j5 \\\\\nj5 & j5 & -j11\n\\end{bmatrix}\n$$",
        "$$\n\\mathbf{Y}_{bus} = \\begin{bmatrix} -j17.5 & j10 & j5 \\\\ j10 & -j17.5 & j5 \\\\ j5 & j5 & -j11 \\end{bmatrix}\n$$"
    )
    with open(p106p, 'w', encoding='utf-8') as f:
        f.write(c)

# 6. Escape unescaped % in 05 Power compilers
for f in [
    '依考科分類/05_電力系統.md',
    '依考科分類/05_電力系統/05_電力系統_歷屆試題彙編_104-114年.md'
]:
    p = os.path.join(WORKSPACE, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        c = re.sub(r'(X[012]\s*=\s*(?:X[012]\s*=\s*)*[0-9\.]+)\%(?=\s|\$|\n|，|、)', r'\1\\%', c)
        with open(p, 'w', encoding='utf-8') as fp:
            fp.write(c)

print("🎉 Successfully cleaned all matrix bold and escaped percents!")
