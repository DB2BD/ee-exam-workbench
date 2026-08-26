# -*- coding: utf-8 -*-
"""
clean_all_spurious_dollar_wraps.py
==================================
1. Strips spurious $$ wrapping lines that contain Chinese characters.
2. Formats multiline matrices and bare equations perfectly.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    orig = "".join(lines)
    new_lines = []
    
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
            
        if in_code_block:
            new_lines.append(line)
            continue

        # If a line starts with $$ and ends with $$ but contains Chinese text outside \text{...}
        # e.g., "$$**埠 2 開路（$\mathbf{I}_2 = 0$）**：$$" or "$$利用電感電流...$$"
        if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
            inner = stripped[2:-2].strip()
            # If inner contains Chinese characters (excluding \text{...})
            no_text_macros = re.sub(r'\\text\{[^\}]*\}', '', inner)
            if re.search(r'[\u4e00-\u9fff]', no_text_macros):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}{inner}\n")
                continue

        # If a bullet item starts with "$$" and contains Chinese: e.g. "1. $$**互易性檢驗**...$$"
        bullet_m = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)\$\$(.+)\$\$$', stripped)
        if bullet_m:
            prefix = bullet_m.group(1)
            inner = bullet_m.group(2).strip()
            no_text_macros = re.sub(r'\\text\{[^\}]*\}', '', inner)
            if re.search(r'[\u4e00-\u9fff]', no_text_macros):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}{prefix}{inner}\n")
                continue

        # Fix specific 110 Circuit line 71
        if stripped == r'AD - BC = (1.5)(1.5) - (5)(0.25) = 2.25 - 1.25 = 1 \quad \text{(正確無誤)}':
            new_lines.append(r'   $$AD - BC = (1.5)(1.5) - (5)(0.25) = 2.25 - 1.25 = 1 \quad \text{(正確無誤)}$$' + '\n')
            continue

        new_lines.append(line)

    content = "".join(new_lines)

    # Clean specific broken matrices in 104 Circuit
    content = content.replace(
        """  $$
  \\mathbf{G} = $$
\\begin{bmatrix} g_{11} & g_{12} \\\\ g_{21} & g_{22} \\end{bmatrix}
$$ = \\mathbf{$$
\\begin{bmatrix} 0.04 - j0.02\\text{ S} & -4 + j2 \\\\ 0 & \\frac{600}{101} - j\\frac{6000}{101}\\ \\Omega \\end{bmatrix}
$$}
  $$""",
        """  $$
  \\mathbf{G} = \\begin{bmatrix} g_{11} & g_{12} \\\\ g_{21} & g_{22} \\end{bmatrix} = \\begin{bmatrix} 0.04 - j0.02\\text{ S} & -4 + j2 \\\\ 0 & \\frac{600}{101} - j\\frac{6000}{101}\\ \\Omega \\end{bmatrix}
  $$"""
    )

    # Clean specific broken matrices in 113 Circuit
    content = content.replace(
        """    $$
    \\mathbf{Y}(s) = $$
\\begin{bmatrix} y_{11}(s) & y_{12}(s) \\\\ y_{21}(s) & y_{22}(s) \\end{bmatrix}
$$ = \\mathbf{$$
\\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}
$$\\text{ S}}
    $$""",
        """    $$
    \\mathbf{Y}(s) = \\begin{bmatrix} y_{11}(s) & y_{12}(s) \\\\ y_{21}(s) & y_{22}(s) \\end{bmatrix} = \\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}\\text{ S}
    $$"""
    )

    content = content.replace(
        """    $$
    \\mathbf{Y}(j\\omega) = \\mathbf{$$
\\begin{bmatrix} 1 + j2\\omega & -j2\\omega \\\\ -4 - j2\\omega & 3 + j2\\omega \\end{bmatrix}
$$\\text{ S}}
    $$""",
        """    $$
    \\mathbf{Y}(j\\omega) = \\begin{bmatrix} 1 + j2\\omega & -j2\\omega \\\\ -4 - j2\\omega & 3 + j2\\omega \\end{bmatrix}\\text{ S}
    $$"""
    )

    content = content.replace(
        """  $$\\mathbf{Y}(s) = \\mathbf{$$
\\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}
$$\\text{ S}}$$""",
        """  $$\\mathbf{Y}(s) = \\begin{bmatrix} 2s + 1 & -2s \\\\ -2s - 4 & 2s + 3 \\end{bmatrix}\\text{ S}$$"""
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
        if clean_file(f):
            count += 1
            print(f"✨ Cleaned spurious $$ in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Total cleaned files: {count}")

if __name__ == '__main__':
    main()
