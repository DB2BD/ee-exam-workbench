# -*- coding: utf-8 -*-
"""
fix_all_mismatched_double_single_dollars.py
===========================================
Fixes all 1,366+ mismatched $$...$ and $...$$ lines across all files.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```'):
        return line

    # 1. Clean weird nested patterns like "$$RB=$100\text{ k}\Omega$" -> "$R_B = 100\text{ k}\Omega$"
    line = re.sub(r'\$\$([A-Za-z0-9_]+)=\$([0-9\.]+\s*\\text\{[^\}]+\})', r'$\1 = \2$', line)
    line = re.sub(r'\$\$([A-Za-z0-9_]+)=\$([0-9\.]+\s*\\\s*\\Omega)', r'$\1 = \2$', line)
    line = re.sub(r'\$\$-j\$([0-9\.]+\s*\\\s*\\Omega)', r'$-j\1$', line)
    line = re.sub(r'\$\$-j\$([0-9\.]+)', r'$-j\1$', line)

    # 2. Fix "$$formula$" at end of line (when the line starts with $$ and has no other $$)
    # Check if line matches: [indent]$$[math]$
    m_display = re.match(r'^(\s*)\$\$([^\$\n]+)\$$', line)
    if m_display:
        indent = m_display.group(1)
        math_content = m_display.group(2).strip()
        # If it's a standalone formula, close with $$
        # e.g., "$$I_o = \frac{V_2}{2\text{ k}\Omega}$" -> "$$I_o = \frac{V_2}{2\text{ k}\Omega}$$"
        return f"{indent}$${math_content}$$\n"

    # Check if bullet item has: [indent]- $$[math]$
    m_bullet_display = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)\$\$([^\$\n]+)\$$', line)
    if m_bullet_display:
        prefix = m_bullet_display.group(1)
        math_content = m_bullet_display.group(2).strip()
        return f"{prefix}$${math_content}$$\n"

    # 3. Fix "$$formula$ text" -> "$formula$ text" (extra leading $)
    # e.g., "$$R_1 = 10\ \Omega$，$..." -> "$R_1 = 10\ \Omega$，$..."
    line = re.sub(r'^\$\$([A-Za-z0-9_\\\{\}\(\)\s\+\-\*/=\.]+)\$([，、。；\s\u4e00-\u9fff])', r'$\1$\2', line)
    line = re.sub(r'^(\s*[-*]\s+|\s*\d+\.\s+)\$\$([A-Za-z0-9_\\\{\}\(\)\s\+\-\*/=\.]+)\$([，、。；\s\u4e00-\u9fff])', r'\1$\2$\3', line)

    # 4. Fix "$formula$$" -> "$formula$"
    m_extra_close = re.match(r'^(\s*)\$([^\$\n]+)\$\$$', line)
    if m_extra_close:
        indent = m_extra_close.group(1)
        math_content = m_extra_close.group(2).strip()
        return f"{indent}$${math_content}$$\n"

    # Clean double dollars before commas/punctuation
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[，。；、\s\u4e00-\u9fff]|$)', r'\1$', line)

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
            print(f"🎯 Fixed $$ vs $ mismatches in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully fixed {count} files with mismatched delimiters!")

if __name__ == '__main__':
    main()
