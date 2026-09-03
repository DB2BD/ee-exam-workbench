# -*- coding: utf-8 -*-
"""
fix_all_nested_and_corrupted_math_lines.py
==========================================
Eliminates all 471+ nested dollar signs, $$- bullets, and internal $ inside $$...$$.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line

    # 1. Fix bullet lines wrapped in $$:
    # e.g., "$$- $\mathbf{I}_a = \frac{V_{an}}{Z_a} = ...$$" -> "- $\mathbf{I}_a = \frac{V_{an}}{Z_a} = ...$"
    # e.g., "$$1. $\mathcal{L}^{-1}...$$" -> "1. $\mathcal{L}^{-1}...$"
    # e.g., "$$- $\mathbf{Z}_{ab} = -j4\ \Omega$$" -> "- $\mathbf{Z}_{ab} = -j4\ \Omega$"
    # e.g., "$$*(可求出 $V_1 = ...$)*$$" -> "*(可求出 $V_1 = ...$)*"
    m_wrapped_bullet = re.match(r'^(\s*)\$\$\s*([-*]|\d+\.|\*\([^\)]+\)\*)\s*(.+?)\s*\$\$$', line)
    if m_wrapped_bullet:
        indent = m_wrapped_bullet.group(1)
        bullet = m_wrapped_bullet.group(2)
        content = m_wrapped_bullet.group(3).strip()
        
        # If content starts with $ and doesn't end with $, append $
        if content.startswith('$') and not content.endswith('$'):
            content = content + '$'
        elif not content.startswith('$') and not content.endswith('$') and ('=' in content or r'\frac' in content):
            content = f"${content}$"
        elif content.startswith('$') and content.endswith('$') and content.count('$') == 2:
            pass # already perfect
            
        return f"{indent}{bullet} {content}\n"

    # 2. Fix lines with nested single $ inside display math:
    # e.g., "$$P = $360\text{ MW}$$" -> "$$P = 360\text{ MW}$$"
    # e.g., "$$MVAsc = $1500\text{ MVA}$$" -> "$$MVA_{sc} = 1500\text{ MVA}$$"
    # e.g., "$$a^2 \mathbf{I}_b = ... - $j5\text{ A}$$" -> "$$a^2 \mathbf{I}_b = ... - j5\text{ A}$$"
    # e.g., "$$RB = 100\text{ k}$\Omega$$" -> "$$R_B = 100\text{ k}\Omega$$"
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        indent = line[:len(line) - len(line.lstrip())]
        core = s[2:-2].strip()
        
        # If core has Chinese text and $...$, it's not a pure display formula
        if re.search(r'[\u4e00-\u9fff]', core) and ('$' in core or '，' in core or '、' in core):
            # e.g. "$$R_1 = 10\ \Omega$，$$" -> "$R_1 = 10\ \Omega$，$..."
            # Clean trailing and leading $$
            cleaned = re.sub(r'^\$\$\s*', '', line)
            cleaned = re.sub(r'\s*\$\$$', '', cleaned)
            return cleaned.rstrip() + '\n'
            
        # Strip internal single dollars from pure math
        core_no_dollar = core.replace(r'\$', '__ESCAPED_DOLLAR__').replace('$', '').replace('__ESCAPED_DOLLAR__', r'\$')
        return f"{indent}$${core_no_dollar}$$\n"

    # 3. Clean stray "$$-j" at start of line
    line = re.sub(r'^\$\$-j([0-9\.]+\s*\\\s*\\Omega)\$\$$', r'$-j\1$', line)

    # 4. Clean "-8.660 - $j5"
    line = re.sub(r'-\s*\$([j0-9])', r'- \1', line)

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)

    # Clean specific known patterns
    content = content.replace("$$3.45\\text{ kV}$/480 V$$", "$3.45\\text{ kV} / 480\\text{ V}$")
    content = content.replace("$$11.4\\text{ kV}$/380V$$", "$11.4\\text{ kV} / 380\\text{ V}$")
    content = content.replace("$$R_1 = 10\\ \\Omega$，$$", "$R_1 = 10\\ \\Omega$，")
    content = content.replace("$$R_1 = 1\\ \\Omega$、$$", "$R_1 = 1\\ \\Omega$、")

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
            print(f"🎯 Cleaned nested math in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully cleaned {count} files.")

if __name__ == '__main__':
    main()
