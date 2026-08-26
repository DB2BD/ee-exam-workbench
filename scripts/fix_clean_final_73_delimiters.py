# -*- coding: utf-8 -*-
"""
fix_clean_final_73_delimiters.py
================================
Surgically fixes the remaining 73 lines across all files.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line

    # 1. Trailing single $ after Chinese punctuation or end of bullet
    line = re.sub(r'([。，；：）])\$(?=[。，；：\s\n]|$)', r'\1', line)
    line = re.sub(r'(\$[^\$\n]+)\$([。，；：])\$', r'\1\2', line)
    line = re.sub(r'([0-9A-Za-z\^_\+\-\*/\)\'\]\s])：\$$', r'\1：', line)

    # 2. Missing opening $ on bullet items with units or variable ranges
    # e.g. "- 1\text{ Hz} \le f \le 100\text{ Hz}$" -> "- $1\text{ Hz} \le f \le 100\text{ Hz}$"
    # e.g. "- f \le 10\text{ Hz}$" -> "- $f \le 10\text{ Hz}$"
    # e.g. "- f \ge 1\text{ kHz}$" -> "- $f \ge 1\text{ kHz}$"
    # e.g. "- 11.4\text{ kV}$" -> "- $11.4\text{ kV}$"
    # e.g. "- 69\text{ kV}$" -> "- $69\text{ kV}$"
    # e.g. "- 3.45\text{ kV}$" -> "- $3.45\text{ kV}$"
    # e.g. "- 3.3\text{ kV}$" -> "- $3.3\text{ kV}$"
    # e.g. "- 22\text{ kV}$" -> "- $22\text{ kV}$"
    # e.g. "- 20\text{ HP}$" -> "- $20\text{ HP}$"
    # e.g. "- 10\text{ HP}$" -> "- $10\text{ HP}$"
    # e.g. "- 100\text{ Hz} \le f \le 10\text{ MHz}$" -> "- $100\text{ Hz} \le f \le 10\text{ MHz}$"
    line = re.sub(r'^(\s*[-*]\s+)([0-9\.]+\\text\{[^\}]+\}\s*\\le\s*[^\$]+)\$', r'\1$\2$', line)
    line = re.sub(r'^(\s*[-*]\s+)([a-zA-Z_]\s*\\(?:le|ge)\s*[^\$]+)\$', r'\1$\2$', line)
    line = re.sub(r'^(\s*[-*]\s+)([0-9\.]+\\text\{[^\}]+\})\$', r'\1$\2$', line)

    # 3. Fix "* $**(2) $v_2 = v_1$**：" -> "* **(2) $v_2 = v_1$**："
    line = re.sub(r'^\s*\*\s*\$\s*(\*\*\([0-9]+\)\s*\$[^\$]+\$\*\*[：:])', r'* \1', line)

    # 4. Fix "- $A：$P_{max,A}..." -> "- **A 負載**：$P_{max,A}..."
    line = re.sub(r'^(\s*[-*]\s+)\$([A-D])：\$', r'\1**\2 負載**：$', line)

    # 5. Fix "11. $4\text{ kV}$" -> "$11.4\text{ kV}$"
    line = line.replace("11. $4\\text{ kV}$", "$11.4\\text{ kV}$")

    # 6. Fix "y = j4.2 \times 10^{-6}..."
    if line.strip().startswith('y = j4.2') and line.strip().endswith('km}$，長度 $l = 300\\text{ km}$。'):
        line = '$' + line.strip() + '\n'

    # 7. Fix unclosed piecewise formulas
    if s.startswith('f_{X,Y}(x,y) = \\begin{cases}') or s.startswith('p(x,y) = \\begin{cases}'):
        core = s.rstrip('$')
        return f"$${core}$$\n"

    # 8. Clean trailing single $ on lines starting with $$
    if s.startswith('$$') and not s.endswith('$$') and s.endswith('$'):
        core = s[2:-1].strip()
        indent = line[:len(line) - len(line.lstrip())]
        return f"{indent}$${core}$$\n"

    # 9. Clean stray $$ on bullet items
    # e.g., "- $**Bus 1**：$V_1..." -> "- **Bus 1**：$V_1..."
    line = re.sub(r'^(\s*[-*]\s+)\$\s*(\*\*[^\*]+\*\*[：:]\s*\$)', r'\1\2', line)

    # 10. Clean "$$V_{D1} = ..." without closing $$
    if s.startswith('$$V_{D1} =') and not s.endswith('$$'):
        return f"{line.rstrip()}$$\n"

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)

    # Specific file cleanups
    content = content.replace("$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})$\n", "$$Q_G = \\frac{1.0 - 1.0\\cos(11.78^\\circ)}{0.2170} = +0.0972\\text{ pu} \\implies Q_G = 0.0972 \\times 850 = \\mathbf{+82.6\\text{ Mvar}}\\quad (\\text{滯後運轉，非進相})$$\n")
    content = content.replace("$$P_2 = 312.50\\text{ MW} \\le 500\\text{ MW}\\quad (\\text{未超出額定容量，完全安全！})$\n", "$$P_2 = 312.50\\text{ MW} \\le 500\\text{ MW}\\quad (\\text{未超出額定容量，完全安全！})$$\n")
    content = content.replace("$$\\mathbf{Z}_{5,C} = j(5 \\times 0.06 X_C - \\frac{X_C}{5}) = j(0.30 - 0.20)X_C = +j0.10 X_C\\text{ (呈感性！)}$\n", "$$\\mathbf{Z}_{5,C} = j(5 \\times 0.06 X_C - \\frac{X_C}{5}) = j(0.30 - 0.20)X_C = +j0.10 X_C\\text{ (呈感性！)}$$\n")

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
            print(f"🎯 Repaired: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
