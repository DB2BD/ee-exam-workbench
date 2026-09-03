# -*- coding: utf-8 -*-
"""
fix_leaked_macros_final.py
==========================
Wraps any floating/unwrapped LaTeX macros in $...$ across the 10 remaining files.
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MACROS = [
    'Omega', 'Delta', 'alpha', 'beta', 'theta', 'tau', 'approx', 'angle',
    'sqrt', 'frac', 'times', 'pm', 'le', 'ge', 'infty', 'mu'
]

files = [
    '依考科分類/04_電機機械.md',
    '依考科分類/04_電機機械/04_電機機械_歷屆試題彙編_104-114年.md',
    '依考科分類/05_電力系統.md',
    '依考科分類/05_電力系統/05_電力系統_歷屆試題彙編_104-114年.md',
    '📝 個人題解與錯題本/05_電力系統/109年_電力系統_全卷完整詳細題解.md',
    '📝 個人題解與錯題本/🏛️_國考同級題解/05_電力系統/GK_113年_電力系統_全卷完整詳細題解.md',
    '🧠 核心考點知識庫/02_電子學_含電力電子/02_電力電子DC-DC轉換器Buck-Boost.md',
    '🧠 核心考點知識庫/03_工程數學/01_常微分方程ODE與尤拉柯西方程.md',
    '🧠 核心考點知識庫/04_電機機械/01_變壓器等效電路與效率計算.md',
    '🧠 核心考點知識庫/04_電機機械/02_三相感應電動機轉矩轉差率與啟動.md'
]

def fix_line(line):
    if line.strip().startswith('```') or line.strip().startswith('$$'):
        return line
        
    # Split by $...$ inline math
    # We want to match all $...$ without matching escaped \$
    tokens = re.split(r'(\$[^\$]+?\$)', line)
    new_tokens = []
    for t in tokens:
        if t.startswith('$') and t.endswith('$') and len(t) > 1:
            new_tokens.append(t)
        else:
            # Plain text part: find any \macro that should be wrapped in $...$
            # e.g., \frac{A}{B} -> $\frac{A}{B}$
            # e.g., \sqrt{A} -> $\sqrt{A}$
            # e.g., \Delta I -> $\Delta I$
            # e.g., \angle 30^\circ -> $\angle 30^\circ$
            p = t
            p = re.sub(r'\\frac\{([^\}]+)\}\{([^\}]+)\}', r'$\\frac{\1}{\2}$', p)
            p = re.sub(r'\\sqrt\{([^\}]+)\}', r'$\\sqrt{\1}$', p)
            p = re.sub(r'\\Delta\s+([A-Za-z0-9_]+)', r'$\\Delta \1$', p)
            p = re.sub(r'\\angle\s*([0-9\-\+]+(?:\^\\circ)?)', r'$\\angle \1$', p)
            p = re.sub(r'\\approx\s*([0-9\.]+)', r'$\\approx \1$', p)
            p = re.sub(r'\\pm\s*([0-9\.]+)', r'$\\pm \1$', p)
            p = re.sub(r'\\beta', r'$\\beta$', p)
            p = re.sub(r'\\tau', r'$\\tau$', p)
            p = re.sub(r'\\times', r'$\\times$', p)
            p = re.sub(r'\\Omega', r'$\\Omega$', p)
            p = re.sub(r'\\approx', r'$\\approx$', p)
            p = re.sub(r'\\Delta', r'$\\Delta$', p)
            new_tokens.append(p)
    return ''.join(new_tokens)

def main():
    fixed = 0
    for rel_f in files:
        full_p = os.path.join(WORKSPACE, rel_f)
        if not os.path.exists(full_p):
            continue
        with open(full_p, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = [fix_line(l) for l in lines]
        content = ''.join(new_lines)
        with open(full_p, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed += 1
        print(f"✅ Fixed leaked macros in: {rel_f}")
        
    print(f"\n🎉 Done! Fixed {fixed} files.")

if __name__ == '__main__':
    main()
