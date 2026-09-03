# -*- coding: utf-8 -*-
"""
fix_all_parse_errors_comprehensive.py
=====================================
Fixes all KaTeX parse errors, unbalanced braces, and leaked macros across all markdown files.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    orig = content
    
    # 1. Fix known unbalanced braces & typos
    # 109 Machinery Q1
    content = content.replace(
        r'\mathbf{X_P = \omega L_P = 2\pi \times 60 \times (2.5 \times 10^{-3}\text{ H}) = \mathbf{0.3\pi\ \Omega \approx 0.9425\ \Omega}}}',
        r'\mathbf{X_P = \omega L_P = 2\pi \times 60 \times (2.5 \times 10^{-3}\text{ H}) = 0.3\pi\ \Omega \approx 0.9425\ \Omega}'
    )
    
    # 111 Machinery Q5
    content = content.replace(
        r'\mathbf{E}_{f,LL} = \sqrt{3} \times 2074.71\text{ V} = \mathbf{3593.5\text{ V} \approx 3.59\text{ kV}}}',
        r'\mathbf{E}_{f,LL} = \sqrt{3} \times 2074.71\text{ V} = \mathbf{3593.5\text{ V}} \approx \mathbf{3.59\text{ kV}}'
    )
    
    # GK 114 Power Systems Q3
    target_gk114 = r"""\mathbf{\frac{\Delta \mathbf{P}}{|\mathbf{V}|} = \mathbf{B}' \Delta \boldsymbol{\theta}, \quad \mathbf{\frac{\Delta \mathbf{Q}}{|\mathbf{V}|} = \mathbf{B}'' \Delta |\mathbf{V}|}"""
    replace_gk114 = r"""\frac{\Delta \mathbf{P}}{|\mathbf{V}|} = \mathbf{B}' \Delta \boldsymbol{\theta}, \quad \frac{\Delta \mathbf{Q}}{|\mathbf{V}|} = \mathbf{B}'' \Delta |\mathbf{V}|"""
    content = content.replace(target_gk114, replace_gk114)
    
    # 108 Electronics Q3 double superscript
    content = content.replace(
        r'\frac{1}{2R^2C^2}',
        r'\frac{1}{2 R^2 C^2}'
    )

    # 2. Fix leaked macros outside math mode in specific files
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith('```') or line.strip().startswith('$$'):
            new_lines.append(line)
            continue
            
        l = line
        parts = re.split(r'(\$[^\$\n]+\$|\$\$[\s\S]*?\$\$)', l)
        for i in range(0, len(parts), 2):
            p = parts[i]
            # Replace leaked macros in plain text part
            p = re.sub(r'(?<![A-Za-z0-9\\])\\le\b', r'$\\le$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\ge\b', r'$\\ge$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\approx\b', r'$\\approx$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\times\b', r'$\\times$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\infty\b', r'$\\infty$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\beta\b', r'$\\beta$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\tau\b', r'$\\tau$', p)
            p = re.sub(r'(?<![A-Za-z0-9\\])\\angle\s*([0-9\-\+]+(?:\^\\circ)?)', r'$\\angle \1$', p)
            parts[i] = p
            
        l = ''.join(parts)
        new_lines.append(l)

    content = '\n'.join(new_lines)
    
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
            print(f"🔧 Fixed: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Total fixed files: {count}")

if __name__ == '__main__':
    main()
