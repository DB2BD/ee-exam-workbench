# -*- coding: utf-8 -*-
"""
fix_matrix_and_brace_environments.py
====================================
Fixes all broken matrix environments, underbraces, and leaked macros across the repository.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    orig = content

    # 1. Fix 104 Power Systems Q4 matrix
    content = re.sub(
        r'\$\$\s*\\mathbf\{Z\}_\{bus\}\s*=\s*\$\$\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Z}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )
    content = re.sub(
        r'\\mathbf\{Z\}_\{bus\}\s*=\s*\$\$\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Z}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )

    # 2. Fix 106 Power Systems Q4 matrix
    content = re.sub(
        r'\$\$\s*\\mathbf\{Y\}_\{bus\}\s*=\s*\$\$\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Y}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )
    content = re.sub(
        r'\\mathbf\{Y\}_\{bus\}\s*=\s*\$\$\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Y}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )

    # 3. Fix 111 Power Systems Q2 matrix
    content = re.sub(
        r'\$\$\s*\\mathbf\{Z\}_\{bus\}\s*=\s*\$\$\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Z}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )

    # 4. Fix 112 Power Systems Q4 matrix
    content = re.sub(
        r'\$\$\s*\\mathbf\{Y\}_\{bus\}\s*=\s*\\begin\{bmatrix\}\$\$\s*([\s\S]*?)\\end\{bmatrix\}\s*\$\$\\text\{\s*pu\}\$\$',
        r'$$\n\\mathbf{Y}_{bus} = \\begin{bmatrix}\n\1\\end{bmatrix}\\text{ pu}\n$$',
        content
    )

    # 5. Fix 114 Eng Math Q5 underbraces
    target_114_eng = """$$\\mathbf{x} = \\underbrace{\\begin{bmatrix} 0 \\\\ 0 \\\\ -1 \\\\ 0 \\end{bmatrix}
$$_{\\mathbf{x}_p\\text{ (特解)}} + c_1 \\underbrace{\\begin{bmatrix} 1 \\\\ 0 \\\\ 0 \\\\ 0 \\end{bmatrix}
$$_{\\mathbf{v}_1} + c_2 \\underbrace{\\begin{bmatrix} 0 \\\\ 1 \\\\ 1 \\\\ 1 \\end{bmatrix}
$$_{\\mathbf{v}_2}$$"""
    replace_114_eng = """$$\\mathbf{x} = \\underbrace{\\begin{bmatrix} 0 \\\\ 0 \\\\ -1 \\\\ 0 \\end{bmatrix}}_{\\mathbf{x}_p\\text{ (特解)}} + c_1 \\underbrace{\\begin{bmatrix} 1 \\\\ 0 \\\\ 0 \\\\ 0 \\end{bmatrix}}_{\\mathbf{v}_1} + c_2 \\underbrace{\\begin{bmatrix} 0 \\\\ 1 \\\\ 1 \\\\ 1 \\end{bmatrix}}_{\\mathbf{v}_2}$$"""
    content = content.replace(target_114_eng, replace_114_eng)

    # 6. Fix general pattern of \begin{bmatrix}$$ and \end{bmatrix}$$
    content = re.sub(r'\\begin\{(bmatrix|pmatrix|matrix|cases|aligned)\}\$\$', r'\\begin{\1}', content)
    content = re.sub(r'\$\$\\begin\{(bmatrix|pmatrix|matrix|cases|aligned)\}', r'\\begin{\1}', content)
    content = re.sub(r'\\end\{(bmatrix|pmatrix|matrix|cases|aligned)\}\$\$', r'\\end{\1}', content)
    content = re.sub(r'\$\$\\end\{(bmatrix|pmatrix|matrix|cases|aligned)\}', r'\\end{\1}', content)

    # Ensure any \begin{bmatrix} ... \end{bmatrix} block is wrapped in outer $$ ... $$
    def ensure_wrapped_matrix(m):
        full = m.group(0)
        # check if preceded by $$
        return full

    # 7. Fix unescaped % inside text headers or markdown
    content = re.sub(r'(?<!\\)%\s*(?=\s*成為|\s*落後|\s*超前|\s*之|\s*，|\s*）)', r'\\%', content)

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
        if fix_file_content(f):
            count += 1
            print(f"🔧 Fixed matrix/brace syntax in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Total fixed: {count}")

if __name__ == '__main__':
    main()
