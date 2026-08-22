# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

def fix_matrix_markup(text):
    # 1. Fix broken begin tags
    text = text.replace('egin{bmatrix}', r'\begin{bmatrix}')
    text = text.replace('egin{pmatrix}', r'\begin{pmatrix}')
    text = text.replace('egin{matrix}', r'\begin{matrix}')
    text = text.replace('egin{vmatrix}', r'\begin{vmatrix}')
    text = text.replace(r'\egin{', r'\begin{')
    
    # 2. Fix matrix row breaks inside matrix environments
    def fix_single_matrix(match):
        env = match.group(0)
        # Inside the environment, replace single \ that separates rows with \\
        # Match pattern: entry followed by single \ and then another entry
        # e.g., "2\mathcal{R} \ \mathcal{R}" or "7 \ 6" or "0 \ 1"
        # We replace single \ that is NOT part of a LaTeX command (\mathcal, \mathbf, \Delta, \Omega, \dots, \vdots, \cdots, \hline, \text)
        
        # Replace line breaks or spaces with single \ between items
        lines = env.split('\n')
        new_lines = []
        for line in lines:
            # If a line contains " \ " between numbers/variables
            # e.g., \begin{bmatrix} 2\mathcal{R} & \mathcal{R} \ \mathcal{R} & 2\mathcal{R} \end{bmatrix}
            # replace " \ " with " \\ "
            line = re.sub(r'(?<=[0-9A-Za-z\)\}])\s*\\\s*(?=[0-9A-Za-z\-\+\{\(]|\\[A-Za-z])', r' \\\\ ', line)
            # Ensure \\ isn't tripled or quadrupled
            line = re.sub(r'\\{3,}', r'\\\\', line)
            new_lines.append(line)
        return '\n'.join(new_lines)
    
    text = re.sub(r'\\begin\{(?:bmatrix|pmatrix|matrix|vmatrix)\}[\s\S]*?\\end\{(?:bmatrix|pmatrix|matrix|vmatrix)\}', fix_single_matrix, text)
    
    return text

fixed = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    cleaned = fix_matrix_markup(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'🎯 Perfectly fixed matrices in: {fpath}')
        fixed += 1

print(f'\nTotal files with matrices fixed: {fixed} / {len(files)}')
