# -*- coding: utf-8 -*-
"""
clean_all_latex_delimiters_ultimate.py
======================================
Comprehensive, definitive normalization of all LaTeX delimiters and macros.
1. Cleans $$$ and $$$$ artifacts
2. Fixes - $$math$ and - math$ bullets to clean - $math$
3. Fixes \mathbf{\begin{bmatrix} ... \end{bmatrix}}
4. Fixes unescaped % inside math
5. Fixes unbalanced braces
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```'):
        return line

    # 1. Clean multi-dollars
    # e.g., "。$$$" -> "。"
    # e.g., "$$$" -> "$$"
    line = re.sub(r'([，。；、\s\u4e00-\u9fff])\${2,}', r'\1', line)
    line = re.sub(r'\${3,}', '$$', line)

    # 2. Fix bullet items starting with - $$math$ or - $$math$$:
    # e.g., "- $$f \le 10\text{ Hz}$： $\angle A(f) \approx 0^\circ$。" -> "- $f \le 10\text{ Hz}$： $\angle A(f) \approx 0^\circ$。"
    # e.g., "- $$f_t = A_0 f_b = 10^4 \times 100\text{ Hz} = 1\text{ MHz}$。" -> "- $f_t = A_0 f_b = 10^4 \times 100\text{ Hz} = 1\text{ MHz}$。"
    m_bullet_double = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)\$\$([^\$\n]+)\$([，。；：\s\u4e00-\u9fff].*)$', line)
    if m_bullet_double:
        prefix = m_bullet_double.group(1)
        math_content = m_bullet_double.group(2).strip()
        rest = m_bullet_double.group(3)
        line = f"{prefix}${math_content}${rest}\n"

    # e.g., "- f = 10\text{ kHz}$ 時為" -> "- $f = 10\text{ kHz}$ 時為"
    m_bullet_missing_start = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)([A-Za-z0-9_\\\{\}\(\)\+\-\*/\^]+\s*(?:\\text\{[^\}]+\}|\\Omega|\\angle[^\$]*|\\frac\{[^\}]+\}\{[^\}]+\}|\\sqrt\{[^\}]+\}|\\le|\\ge|\\approx|=|\\Delta))\$([，。；：\s\u4e00-\u9fff].*)$', line)
    if m_bullet_missing_start:
        prefix = m_bullet_missing_start.group(1)
        math_content = m_bullet_missing_start.group(2).strip()
        rest = m_bullet_missing_start.group(3)
        line = f"{prefix}${math_content}${rest}\n"

    # 3. Fix \mathbf{\begin{bmatrix} -> \begin{bmatrix}
    line = re.sub(r'\\mathbf\{\s*(\\begin\{(?:bmatrix|pmatrix|matrix|cases|aligned)\})', r'\1', line)
    # Fix \end{bmatrix}} -> \end{bmatrix}
    line = re.sub(r'(\\end\{(?:bmatrix|pmatrix|matrix|cases|aligned)\})\s*\}', r'\1', line)

    # 4. Fix unbalanced \mathbf{ in matrix equations:
    # e.g. "$\mathbf{T} = \mathbf{\begin{bmatrix} ... \end{bmatrix}$" -> "$\mathbf{T} = \begin{bmatrix} ... \end{bmatrix}$"
    line = re.sub(r'\\mathbf\{\s*\\begin\{', r'\\begin{', line)

    # 5. Fix 113 Circuit Q4 matrices
    line = line.replace(r'$$\mathbf{Y}(s) = \mathbf{$$', r'$$\mathbf{Y}(s) = ')
    line = line.replace(r'$$\mathbf{Y}(j\omega) = \mathbf{$$', r'$$\mathbf{Y}(j\omega) = ')

    # 6. Fix unescaped % inside math blocks on single line
    # If line has $...$ or $$...$$
    def escape_pct_in_math(m):
        full = m.group(0)
        return re.sub(r'(?<!\\)%', r'\\%', full)
        
    line = re.sub(r'\$\$[\s\S]*?\$\$', escape_pct_in_math, line)
    line = re.sub(r'(?<!\\)\$[^\$\n]+(?<!\\)\$', escape_pct_in_math, line)

    # 7. Clean trailing $$ on inline math before Chinese characters
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\u4e00-\u9fff，。；：\s\(\)]|$)', r'\1$', line)

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)
    
    # Clean whole-file patterns
    # Fix underbrace in 114 Eng Math Q5
    content = content.replace(r'$$}_{\mathbf{v}_2}$$', r'}_{\mathbf{v}_2}$$')
    content = content.replace(r'$$_{\mathbf{v}_1}', r'_{\mathbf{v}_1}')
    content = content.replace(r'$$_{\mathbf{v}_2}', r'_{\mathbf{v}_2}')
    content = content.replace(r'$$_{\mathbf{x}_p', r'_{\mathbf{x}_p')

    # Fix 111 Circuit Q3
    content = re.sub(
        r'\\mathbf\{H\}\s*=\s*\\mathbf\{\\begin\{bmatrix\}\s*([\s\S]*?)\\end\{bmatrix\}\s*\}',
        r'\\mathbf{H} = \\begin{bmatrix}\n\1\\end{bmatrix}',
        content
    )

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
            print(f"✨ Ultimate Normalized: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Normalized {count} files.")

if __name__ == '__main__':
    main()
