# -*- coding: utf-8 -*-
"""
fix_all_360_unclosed_dollar_starts.py
=====================================
Fixes all lines starting with $$ that do not end with $$:
1. If line is Chinese text with stray leading $$, strips the leading $$
2. If line is a mathematical formula, appends $$
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line
    if s.startswith('$$') and s.endswith('$$'):
        return line

    if s.startswith('$$'):
        indent = line[:len(line) - len(line.lstrip())]
        after = s[2:].strip()
        
        # Case 1: Chinese text following $$
        # e.g., "$$電壓（thermal voltage）..." or "$$小為5 V/V..."
        if re.search(r'^[\u4e00-\u9fff]', after) or re.search(r'^[a-zA-Z0-9_\s]+\s*=\s*\$[0-9]', after):
            # Strip the leading $$
            return f"{indent}{after}\n"

        # Case 2: Formula ending with single $
        # e.g., "$$I_{1,n} = ... = 41.67\text{ A}$" -> "$$I_{1,n} = ... = 41.67\text{ A}$$"
        if after.endswith('$') and not after.endswith('$$'):
            core = after[:-1].strip()
            return f"{indent}$${core}$$\n"

        # Case 3: Pure formula without ending $
        # e.g., "$$108 + 3(9 - V_a) = ... \text{--- (式 1)}"
        # e.g., "$$p(x,y) = \begin{cases} ... \end{cases}"
        if is_pure_formula(after):
            return f"{indent}$${after}$$\n"

    return line

def is_pure_formula(text):
    # Check if text is predominantly mathematical
    no_text = re.sub(r'\\text\{[^\}]*\}', '', text)
    chinese = len(re.findall(r'[\u4e00-\u9fff]', no_text))
    if chinese > 3:
        return False
    return '=' in text or r'\begin' in text or r'\implies' in text or r'\frac' in text or r'\int' in text or r'\sum' in text

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
            print(f"🎯 Fixed unclosed $$ starts in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully fixed {count} files.")

if __name__ == '__main__':
    main()
