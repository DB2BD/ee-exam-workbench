# -*- coding: utf-8 -*-
"""
fix_bullet_multi_dollar_headers.py
==================================
Cleans bullet items that have corrupted '* $$**title**： $formula$$$' or similar syntax.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```'):
        return line

    # Fix "* $$**title**： $formula$$$" -> "* **title**： $formula$"
    # Fix "- $$**title**： $formula$$$" -> "- **title**： $formula$"
    # Fix "1. $$**title**： $formula$$$" -> "1. **title**： $formula$"
    line = re.sub(r'^(\s*[-*]|\s*\d+\.)\s*\$\$\s*(\*\*[^\*]+\*\*[\s：:]*)\s*([^\n]+)$', r'\1 \2\3', line)
    
    # Clean trailing $$$ or $$ on bullet lines containing Chinese title
    if re.search(r'[\u4e00-\u9fff]', line):
        line = re.sub(r'\${2,}$', '', line.rstrip()) + '\n'

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)
    
    # Also clean any remaining * $$** or - $$**
    content = re.sub(r'(\s*[-*]|\s*\d+\.)\s*\$\$\s*(\*\*)', r'\1 \2', content)

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
            print(f"🎯 Fixed bullet headers in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
