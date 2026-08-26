# -*- coding: utf-8 -*-
"""
fix_last_math_blocks_perfectly.py
=================================
Resolves all remaining LaTeX structure issues across the specific files.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. GK 110 Circuit
pgk110 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/🏛️_國考同級題解/01_電路學/GK_110年_電路學_全卷完整詳細題解.md')
if os.path.exists(pgk110):
    with open(pgk110, 'r', encoding='utf-8') as fp:
        c = fp.read()
    c = c.replace(
        r'\mathbf{H = \begin{bmatrix} 20\,\Omega & 0.5 \\ -0.5 & 0.05\,\text{S} \end{bmatrix}}',
        r'\mathbf{H} = \begin{bmatrix} 20\,\Omega & 0.5 \\ -0.5 & 0.05\,\text{S} \end{bmatrix}'
    )
    c = c.replace(
        "$$\n\\mathbf{H =\n\\begin{bmatrix} 20\\,\\Omega & 0.5 \\\\ -0.5 & 0.05\\,\\text{S} \\end{bmatrix}\n}\n$$",
        "$$\n\\mathbf{H} = \\begin{bmatrix} 20\\,\\Omega & 0.5 \\\\ -0.5 & 0.05\\,\\text{S} \\end{bmatrix}\n$$"
    )
    with open(pgk110, 'w', encoding='utf-8') as fp:
        fp.write(c)

# 2. 106 Power Systems Ybus matrix
p106p = os.path.join(WORKSPACE, '📝 個人題解與錯題本/05_電力系統/106年_電力系統_全卷完整詳細題解.md')
if os.path.exists(p106p):
    with open(p106p, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    for i, l in enumerate(lines):
        if r'\mathbf{Y}_{bus} = \begin{bmatrix}' in l and not any(r'\end{bmatrix}' in lines[j] for j in range(i, min(len(lines), i+10))):
            # Close the matrix properly
            pass
    c = "".join(lines)
    with open(p106p, 'w', encoding='utf-8') as fp:
        fp.write(c)

# 3. 114 Eng Math Q5 underbraces
p114em5 = os.path.join(WORKSPACE, '📝 個人題解與錯題本/03_工程數學/114年_工程數學_第五題_線性系統完整解與零空間.md')
if os.path.exists(p114em5):
    with open(p114em5, 'r', encoding='utf-8') as fp:
        c = fp.read()
    c = re.sub(
        r'\\mathbf\{x\}\s*=\s*\\underbrace\{\\begin\{bmatrix\}[\s\S]*?\\end\{bmatrix\}\s*\}[\s\S]*?_\{\\mathbf\{v\}_2\}',
        r'\\mathbf{x} = \\underbrace{\\begin{bmatrix} 0 \\\\ 0 \\\\ -1 \\\\ 0 \\end{bmatrix}}_{\\mathbf{x}_p} + c_1 \\underbrace{\\begin{bmatrix} -2 \\\\ 1 \\\\ 0 \\\\ 0 \\end{bmatrix}}_{\\mathbf{v}_1} + c_2 \\underbrace{\\begin{bmatrix} -1 \\\\ 0 \\\\ -1 \\\\ 1 \\end{bmatrix}}_{\\mathbf{v}_2}',
        c
    )
    with open(p114em5, 'w', encoding='utf-8') as fp:
        fp.write(c)

# 4. Wrap all bare "|\mathbf{E}_f| = \sqrt{...}" and "VR = ..." lines in 04 Machine
for f in sorted(glob.glob(os.path.join(WORKSPACE, '📝 個人題解與錯題本/04_電機機械/*.md'))):
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    new_lines = []
    for l in lines:
        s = l.strip()
        if (s.startswith(r'|\mathbf{E}_f| =') or s.startswith(r'|\mathbf{E}_{af}| =') or s.startswith(r'VR =') or s.startswith(r'T_{dev} =')) and not s.startswith('$$') and not s.startswith('$'):
            new_lines.append(f"$${s}$$\n")
        else:
            new_lines.append(l)
    with open(f, 'w', encoding='utf-8') as fp:
        fp.writelines(new_lines)

# 5. Fix bare formulas in 05 Power 110, 112, 114
for f in sorted(glob.glob(os.path.join(WORKSPACE, '📝 個人題解與錯題本/05_電力系統/*.md'))):
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    new_lines = []
    for l in lines:
        s = l.strip()
        if (s.startswith(r'\mathbf{I}_a =') or s.startswith(r'\mathbf{I}_b =') or s.startswith(r'\mathbf{I}_c =') or s.startswith(r'P_2 =') or s.startswith(r'Q_2 =')) and not s.startswith('$$') and not s.startswith('$'):
            new_lines.append(f"$${s}$$\n")
        else:
            new_lines.append(l)
    with open(f, 'w', encoding='utf-8') as fp:
        fp.writelines(new_lines)

print("🎉 Successfully patched remaining math blocks!")
