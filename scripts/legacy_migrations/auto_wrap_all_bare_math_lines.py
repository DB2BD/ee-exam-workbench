# -*- coding: utf-8 -*-
"""
auto_wrap_all_bare_math_lines.py
================================
Scans for all standalone bare LaTeX formula lines and wraps them in proper $$...$$ display math.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_bare_math_line(line):
    s = line.strip()
    if not s:
        return False
    # Skip non-math markdown
    if s.startswith('#') or s.startswith('|') or s.startswith('> [!') or s.startswith('```') or s.startswith('---') or s.startswith('!['):
        return False
    # Skip already wrapped
    if s.startswith('$$') and s.endswith('$$'):
        return False
    if s.startswith('$') and s.endswith('$') and s.count('$') == 2:
        return False
    # Skip pure text lines with Chinese description
    no_math = re.sub(r'\\text\{[^\}]*\}', '', s)
    no_math = re.sub(r'\$[^\$]+\$', '', no_math)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', no_math))
    if chinese_chars > 6:
        return False
        
    # Check for strong LaTeX math syntax
    math_patterns = [
        r'\\mathbf\{', r'\\frac\{', r'\\sqrt\{', r'\\begin\{', r'\\implies',
        r'\\parallel', r'\\angle', r'\\times', r'\\mathcal\{', r'\\sum_',
        r'\\int_', r'\\Omega', r'\\text\{[A-Za-z\s]+\}', r'\\left\(',
        r'^[A-Za-z0-9_\\\{\}\(\)\'\*]+\s*=\s*[0-9A-Za-z_\\\{\}\(\)\+\-\*/\^]+'
    ]
    
    for pat in math_patterns:
        if re.search(pat, s):
            # Ensure it has equal sign or arrow or operator
            if '=' in s or r'\implies' in s or r'\parallel' in s or r'\to' in s or r'\approx' in s or r'\angle' in s:
                return True
    return False

def wrap_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = []
    in_code = False
    in_display = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code = not in_code
            new_lines.append(line)
            continue
            
        if in_code:
            new_lines.append(line)
            continue
            
        if stripped == '$$':
            in_display = not in_display
            new_lines.append(line)
            continue
            
        if in_display:
            new_lines.append(line)
            continue
            
        # Check bullet item with bare math
        m_bullet = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)(.+)$', line)
        if m_bullet:
            prefix = m_bullet.group(1)
            content = m_bullet.group(2).strip()
            if is_bare_math_line(content):
                new_lines.append(f"{prefix}$${content}$$\n")
                continue

        # Check standalone bare line
        if is_bare_math_line(line):
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}$${stripped}$$\n")
            continue
            
        new_lines.append(line)

    result = "".join(new_lines)
    if result != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if wrap_file(f):
            count += 1
            print(f"📦 Auto-wrapped bare math in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully auto-wrapped {count} files.")

if __name__ == '__main__':
    main()
