# -*- coding: utf-8 -*-
"""
fix_all_missing_open_dollars.py
===============================
Fixes all missing opening $ delimiters and removes duplicate trailing $$ on inline math.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if s.startswith('```') or s == '$$':
        return line

    # Fix pattern: "$...$$" at end of line or before punctuation -> "$...$"
    # e.g., "$5000\text{ kVA}$$" -> "$5000\text{ kVA}$"
    # e.g., "$0\text{ V}$$。" -> "$0\text{ V}$。"
    # e.g., "$18\ \Omega$$。" -> "$18\ \Omega$。"
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\u4e00-\u9fff，。；、\s\(\)]|$)', r'\1$', line)

    # Fix pattern: "- 9\text{ V}$" -> "- $9\text{ V}$"
    # e.g. "- 15\ \Omega$ 電阻" -> "- $15\ \Omega$ 電阻"
    # e.g. "- 10\text{ A}$ 獨立電流源" -> "- $10\text{ A}$ 獨立電流源"
    # e.g. "* V_1 = v + 6 = -8 + 6 = -2\text{ V} \implies$" -> "* $V_1 = v + 6 = -8 + 6 = -2\text{ V} \implies$"
    # e.g. "69\text{ kV}$/$3.3\text{ kV}$" -> "$69\text{ kV}$/$3.3\text{ kV}$"
    # e.g. "25\text{ MVA}$, PF = 0.8(滯後)$" -> "$25\text{ MVA}$, $\text{PF} = 0.8\text{ (滯後)}$"
    line = re.sub(r'(^|\s*[-*]\s+|\s*\d+\.\s+)(?<!\$)([0-9A-Za-z_\\\{\}\(\)\+\-\*/\^]+\s*(?:\\text\{[^\}]+\}|\\Omega|\\angle[^\$]*|\\frac\{[^\}]+\}\{[^\}]+\}|\\sqrt\{[^\}]+\}|\\le|\\ge|\\approx))\$', r'\1$\2$', line)
    
    # Fix matrix without opening dollar:
    # e.g. "\begin{bmatrix} ... \end{bmatrix}$" -> "$\begin{bmatrix} ... \end{bmatrix}$"
    line = re.sub(r'(^|\s*[-*]\s+|\s*\d+\.\s+)(?<!\$|\\)(\\begin\{(?:bmatrix|pmatrix|matrix)\}[\s\S]*?\\end\{(?:bmatrix|pmatrix|matrix)\})\$', r'\1$\2$', line)

    # Fix specific patterns
    line = line.replace(r'25\text{ MVA}$, PF = 0.8(滯後)$', r'$25\text{ MVA}$, $\text{PF} = 0.8\text{ (滯後)}$')
    line = line.replace(r'50\text{ MVA}$, PF = 0.8(滯後)$', r'$50\text{ MVA}$, $\text{PF} = 0.8\text{ (滯後)}$')
    line = line.replace(r'\lambda = 10\text{ 元/MWh}$$。', r'$\lambda = 10\text{ 元/MWh}$。')
    line = line.replace(r'69\text{ kV}$/$3.3\text{ kV}$', r'$69\text{ kV}$/$3.3\text{ kV}$')
    line = line.replace(r'200\text{ MVA}$；', r'$200\text{ MVA}$；')
    line = line.replace(r'100\text{ MVA}$，', r'$100\text{ MVA}$，')
    line = line.replace(r'ZT = 6\%$，', r'$Z_T = 6\%$，')
    line = line.replace(r'X/R = 2.5，', r'$X/R = 2.5$，')
    line = line.replace(r'11.4\text{ kV}$/480 V$，', r'$11.4\text{ kV}/480\text{ V}$，')
    line = line.replace(r'22.8\text{ kV}$/480 V、', r'$22.8\text{ kV}/480\text{ V}$、')

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)
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
            print(f"🔧 Fixed missing open $ in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully fixed {count} files.")

if __name__ == '__main__':
    main()
