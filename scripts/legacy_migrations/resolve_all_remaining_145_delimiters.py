# -*- coding: utf-8 -*-
"""
resolve_all_remaining_145_delimiters.py
=======================================
Fixes all remaining delimiter issues:
1. Standalone formulas with missing $$ at start or end
2. Trailing single $ after periods/brackets (e.g. "。$", "）$")
3. Bullet points missing opening $ (e.g. "- t=1\text{ ms}$", "- A = U \Sigma V^T$", "- J_{11} = ...")
4. Clean stray $$ on bullet lines
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line
    if s.startswith('$$') and s.endswith('$$') and s.count('$$') == 2:
        return line

    # 1. Clean trailing stray $ after Chinese punctuation
    # e.g., "。$" -> "。"
    # e.g., "）$。" -> "）。"
    # e.g., "）$" -> "）"
    line = re.sub(r'([。，；：）])\$(?=[。，；：\s]|$)', r'\1', line)

    # 2. Fix standalone formula ending in $$ but missing opening $$:
    # e.g. "|\mathbf{E}_i| = ... \approx \mathbf{2.026\text{ pu}}$$" -> "$$|\mathbf{E}_i| = ... \approx \mathbf{2.026\text{ pu}}$$"
    if s.endswith('$$') and not s.startswith('$$') and ('=' in s or r'\implies' in s or r'\sqrt' in s):
        indent = line[:len(line) - len(line.lstrip())]
        core = s[:-2].strip()
        return f"{indent}$${core}$$\n"

    # 3. Fix standalone formula ending in $ (bare math line ending with single $):
    # e.g. "V_2^4 + (2 Q_2 X_T - V_1^2) V_2^2 + (P_2^2 + Q_2^2) X_T^2 = 0$" -> "$$V_2^4 + ... = 0$$"
    # e.g. "P_{G1} + P_{G2} = P_D + P_L$" -> "$$P_{G1} + P_{G2} = P_D + P_L$$"
    # e.g. "\Delta P_2 / |V_2| = 0.6 / 1.05 \approx 0.57143 ...$" -> "$$\Delta P_2 / |V_2| = ...$$"
    if s.endswith('$') and not s.startswith('$') and ('=' in s or r'\approx' in s) and not re.search(r'[\u4e00-\u9fff]', s):
        indent = line[:len(line) - len(line.lstrip())]
        core = s[:-1].strip()
        return f"{indent}$${core}$$\n"

    # 4. Fix bullet items starting with missing $
    # e.g. "- t=0$ 起始於" -> "- $t=0$ 起始於"
    # e.g. "- t=1\,\text{ms}$ 瞬間" -> "- $t=1\,\text{ms}$ 瞬間"
    # e.g. "- J_{11} = \frac...$ -> "- $J_{11} = \frac...$"
    # e.g. "- A = U \Sigma V^T$ -> "- $A = U \Sigma V^T$"
    # e.g. "- C$ 相故障電流" -> "- $C$ 相故障電流"
    # e.g. "- I_{sc} = \frac...$$" -> "- $I_{sc} = \frac...$"
    line = re.sub(r'^(\s*[-*]\s+)([A-Za-z0-9_\{\}\\\^]+)\$([，。；：\s\u4e00-\u9fff])', r'\1$\2$\3', line)
    line = re.sub(r'^(\s*[-*]\s+)([a-zA-Z0-9_\{\}\\]+\s*=\s*[0-9A-Za-z_\\\{\}\(\)\+\-\*/\^\\\,\s]+)\$', r'\1$\2$', line)
    line = re.sub(r'^(\s*[-*]\s+)(I_{sc}\s*=\s*[^$]+)\$\$(.*)$', r'\1$\2$\3', line)

    # 5. Fix bullet items starting with "- $$"
    # e.g. "- $$*(驗證 KCL..." -> "- *(驗證 KCL..."
    # e.g. "- $$\Delta 側..." -> "- $\Delta$ 側..."
    # e.g. "- 輸出電壓：$$V_o = D V_s$" -> "- 輸出電壓：$V_o = D V_s$"
    # e.g. "- 相異實根 $r_1 \ne r_2$：$$y_h(x) = ..." -> "- 相異實根 $r_1 \ne r_2$：$y_h(x) = ..."
    line = re.sub(r'^(\s*[-*]\s+)\$\$(\*\()', r'\1\2', line)
    line = re.sub(r'^(\s*[-*]\s+)\$\$\\Delta\s*([^\n]+)$', r'\1$\\Delta$ \2\n', line)
    line = re.sub(r'：\$\$([^\$\n]+)\$', r'：$\1$', line)
    line = re.sub(r'：\$\$([^\$\n]+)$', r'：$\1$\n', line)

    # 6. Fix "容量比（Capacity Ratio）：\frac{S_V}{S_\Delta} = ...$"
    line = re.sub(r'：(\\frac\{[^\}]+\}\{[^\}]+\}\s*=\s*[^\$\n]+)$', r'：$\1$\n', line)

    # 7. Fix "$$$$ at end of line"
    if s.endswith('$$$$'):
        line = line.rstrip()[:-2] + '\n'

    # 8. Clean $$ in middle of text
    # e.g. "* l = 200\text{ km}, 60\text{ Hz}$$下之總串聯電抗：" -> "* $l = 200\text{ km}$, $60\text{ Hz}$ 下之總串聯電抗："
    line = line.replace(r'* l = 200\text{ km}, 60\text{ Hz}$$下之總串聯電抗：', r'* $l = 200\text{ km}, 60\text{ Hz}$ 下之總串聯電抗：')
    line = line.replace(r'$$30$ 噸電弧爐', r'$30$ 噸電弧爐')
    line = line.replace(r'$$11.4\text{ kV}$ 受電', r'$11.4\text{ kV}$ 受電')
    line = line.replace(r'$$\Delta V\% =', r'$$\Delta V\% =')
    line = line.replace(r'$$I = 0 \implies', r'$$I = 0 \implies')
    line = line.replace(r'$$\begin{bmatrix}', r'\begin{bmatrix}')
    line = line.replace(r'A^+$$（Pseud', r'A^+$（Pseud')
    line = line.replace(r'$$, \mathbf{x}(0)', r', \mathbf{x}(0)')

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
            print(f"🎯 Repaired: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully repaired {count} files.")

if __name__ == '__main__':
    main()
