# -*- coding: utf-8 -*-
"""
fix_remaining_81_issues.py
==========================
Fixes the remaining 81 line-level delimiter issues with surgical precision.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line

    # 1. Strip stray leading $$ before non-formula text or punctuation
    # e.g., "$$（" -> "（"
    # e.g., "$$>" -> ">"
    # e.g., "$$*KCL" -> "*KCL"
    line = re.sub(r'^\s*\$\$(?=[\uff08\(\u4e00-\u9fff>])', '', line)

    # 2. Fix bullet items starting with missing opening $:
    # e.g., "2. I_1 = 0$" -> "2. $I_1 = 0$"
    # e.g., "* V_1 = v + 6" -> "* $V_1 = v + 6"
    # e.g., "1. D_1$" -> "1. $D_1$"
    # e.g., "2. D_2$" -> "2. $D_2$"
    # e.g., "i(t)$ 在第一個" -> "$i(t)$ 在第一個"
    # e.g., "- 基準容量 100\text{ MVA}$" -> "- 基準容量 $100\text{ MVA}$"
    # e.g., "- V_{in} D = " -> "- $V_{in} D = "
    line = re.sub(r'^(\s*(?:[-*]|\d+\.)\s+)([IivVDJ]\d*|[a-zA-Z_]+)\$([，。；：\s\u4e00-\u9fff])', r'\1$\2$\3', line)
    line = re.sub(r'^(\s*(?:[-*]|\d+\.)\s+)([Vv]\d*\s*=\s*[^\$]+?\s*\\implies)', r'\1$\2$', line)
    line = re.sub(r'^(\s*(?:[-*]|\d+\.)\s+)(V_{in}\s*D\s*=\s*[^\$]+)\$([，。；：\s\u4e00-\u9fff])', r'\1$\2$\3', line)
    line = re.sub(r'^\s*i\(t\)\$([，。；：\s\u4e00-\u9fff])', r'$i(t)$\1', line)
    line = re.sub(r'(\s*[-*]\s+基準容量\s+)([0-9\.]+\\text\{[^\}]+\})\$', r'\1$\2$', line)

    # 3. Fix "- h_{11} = ...$$（...）" -> "- $h_{11} = ...$（...）"
    line = re.sub(r'^(\s*[-*]\s+)(h_{\d+}\s*=\s*[^$]+)\$\$([，。；：\uff08\(\s\u4e00-\u9fff].*)$', r'\1$\2$\3', line)

    # 4. Clean trailing $$ before Chinese brackets/punctuation
    # e.g., "- \frac{3}{2}v_2 = -6\text{ A}$$（向下流入地）。" -> "- $\frac{3}{2}v_2 = -6\text{ A}$（向下流入地）。"
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\uff08\(\u4e00-\u9fff，。；：\s]|$)', r'\1$', line)
    line = re.sub(r'(\\[A-Za-z]+|[0-9A-Za-z\^_\+\-\*/\)\'\]])\$\$([，。；：\uff08\(\s\u4e00-\u9fff].*)$', r'$\1$\2', line)

    # 5. Fix standalone formulas ending with $$ without opening $$
    # e.g. "\Delta I_C / I_{C1} \times 100\%, ...$$" -> "$$\Delta I_C / I_{C1} \times 100\%, ...$$"
    # e.g. "T \propto \frac{...}{...}$$" -> "$$T \propto \frac{...}{...}$$"
    # e.g. "\mathbf{S_{Tr,main} \ge 110\text{ kVA}}$$" -> "$$\mathbf{S_{Tr,main} \ge 110\text{ kVA}}$$"
    if s.endswith('$$') and not s.startswith('$$') and not s.startswith('```'):
        indent = line[:len(line) - len(line.lstrip())]
        core = s[:-2].strip()
        return f"{indent}$${core}$$\n"

    # 6. Fix header line ending with "$A ="
    line = re.sub(r'^(##\s+[^\n]+?)\s*=\s*$', r'\1：\n', line)

    # 7. Odd dollar count on single line ending with math
    no_esc = line.replace(r'\$', '')
    if no_esc.count('$') % 2 != 0:
        if re.search(r'(\\[A-Za-z]+|\}|[0-9A-Za-z\^_\+\-\*/\)\'\s\]])\s*$', line.rstrip()):
            line = line.rstrip() + '$\n'

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)

    # Specific 113 Circuit Q4 fix
    content = content.replace(
        "$$\\mathbf{Y}(s) =$$\n\\begin{bmatrix} y_{11}(s) & y_{12}(s) \\\\ y_{21}(s) & y_{22}(s) \\end{bmatrix}\n$$= \\mathbf{$$\n\\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}\n$$\\text{ S}}",
        "$$\\mathbf{Y}(s) = \\begin{bmatrix} y_{11}(s) & y_{12}(s) \\\\ y_{21}(s) & y_{22}(s) \\end{bmatrix} = \\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}\\text{ S}$$"
    )
    content = content.replace(
        "$$\\mathbf{Y}(j\\omega) = \\mathbf{$$\n\\begin{bmatrix} 1 + j2\\omega & -j2\\omega \\\\ -4 - j2\\omega & 3 + j2\\omega \\end{bmatrix}\n$$\\text{ S}}",
        "$$\\mathbf{Y}(j\\omega) = \\begin{bmatrix} 1 + j2\\omega & -j2\\omega \\\\ -4 - j2\\omega & 3 + j2\\omega \\end{bmatrix}\\text{ S}$$"
    )

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
