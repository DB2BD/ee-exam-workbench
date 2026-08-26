# -*- coding: utf-8 -*-
"""
master_markdown_latex_repair.py
===============================
Comprehensive, robust repair of all bullet point inline LaTeX expressions.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def repair_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line
    if s.startswith('$$') and s.endswith('$$'):
        return line

    # 1. Fix missing opening $ after bullet:
    # e.g. "- 1.8\text{ A}$" -> "- $1.8\text{ A}$"
    # e.g. "- 9\text{ V}$" -> "- $9\text{ V}$"
    # e.g. "- 15\ \Omega$" -> "- $15\ \Omega$"
    line = re.sub(r'^(\s*[-*]|\s*\d+\.)\s+([0-9\.]+\s*(?:\\text\{[^\}]+\}|\\\s*\\Omega|\\Omega))\$', r'\1 $\2$', line)

    # 2. Fix bare formula bullets:
    # e.g. "- g_{11} = \left.\frac{\mathbf{I}_1}{\mathbf{V}_1}\right|_{\mathbf{I}_2=0}, \quad g_{21} = ..."
    # e.g. "- A = \left.\frac{\mathbf{V}_1}{\mathbf{V}_2}\right|_{\mathbf{I}_2=0}..."
    m_bare_bullet = re.match(r'^(\s*[-*]|\s*\d+\.)\s+([a-zA-Z0-9_\{\}\\\(\)]+\s*=\s*(?:\\left|\\frac|\\mathbf|\\sqrt)[^\$\n]+)$', line)
    if m_bare_bullet and '$' not in m_bare_bullet.group(2):
        prefix = m_bare_bullet.group(1)
        math_content = m_bare_bullet.group(2).strip()
        line = f"{prefix}${math_content}$\n"

    # 3. Fix unclosed inline math on bullet lines
    temp = line.replace('$$', '').replace(r'\$', '')
    if temp.count('$') % 2 != 0:
        if re.search(r'(\\[A-Za-z]+|\}|[0-9A-Za-z\^_\+\-\*/\)\'\s])\s*$', line.rstrip()):
            line = line.rstrip() + '$\n'

    # 4. Clean trailing $$ on inline math before Chinese characters or punctuation
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\u4e00-\u9fff，。；：\s\(\)]|$)', r'\1$', line)

    # 5. Fix stray brace
    if line.strip() == '}':
        line = ''

    return line

def repair_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [repair_line(l) for l in lines]
    content = "".join(new_lines)
    
    # Specific targeted fixes
    content = content.replace(
        r'\mathbf{H} = \mathbf{\begin{bmatrix}',
        r'\mathbf{H} = \begin{bmatrix}'
    )
    
    content = content.replace(
        r'$\mathbf{T} = \mathbf{\begin{bmatrix} 1.5 & 5\ \Omega \\ 0.25\text{ S} & 1.5 \end{bmatrix}$',
        r'$\mathbf{T} = \begin{bmatrix} 1.5 & 5\ \Omega \\ 0.25\text{ S} & 1.5 \end{bmatrix}$'
    )

    content = re.sub(
        r'\\mathbf\{i_o\(t\)\s*=\s*\\begin\{cases\}\s*\\mathbf\{10\s*-\s*18\.483\s*e\^\{-500\s*t\}\\text\{\s*A\}\},\s*&\s*0\s*\\le\s*t\s*\\le\s*5\\text\{\s*ms\}\s*\\\\',
        r'\\mathbf{i_o(t)} = \\begin{cases} 10 - 18.483 e^{-500 t}\\text{ A}, & 0 \\le t \\le 5\\text{ ms} \\\\',
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
        if repair_file(f):
            count += 1
            print(f"🔧 Repaired: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully repaired {count} files.")

if __name__ == '__main__':
    main()
