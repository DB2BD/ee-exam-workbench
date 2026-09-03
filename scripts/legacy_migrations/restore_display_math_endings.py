# -*- coding: utf-8 -*-
"""
restore_display_math_endings.py
===============================
Guarantees that every line starting with $$ and ending with $ ends with $$!
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line

    # If line starts with $$ and ends with single $:
    # e.g., "$$A = D = \cosh(\gamma l)...$" -> "$$A = D = \cosh(\gamma l)...$$"
    if s.startswith('$$') and not s.endswith('$$') and s.endswith('$'):
        indent = line[:len(line) - len(line.lstrip())]
        core = s[2:-1].strip()
        return f"{indent}$${core}$$\n"

    # If line starts with $$ and has no ending $:
    if s.startswith('$$') and not s.endswith('$$') and not re.search(r'[\u4e00-\u9fff]', s):
        indent = line[:len(line) - len(line.lstrip())]
        core = s[2:].strip()
        return f"{indent}$${core}$$\n"

    # Clean trailing $ after Chinese punctuation
    line = re.sub(r'([。，；：）])\$(?=[。，；：\s]|$)', r'\1', line)

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
            print(f"🎯 Restored display math in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
