# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

matrix_files = []

for fpath in files:
    if not os.path.isfile(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'begin{bmatrix}' in content or 'begin{pmatrix}' in content or 'begin{matrix}' in content or 'begin{vmatrix}' in content:
        matrix_files.append(fpath)

print(f'Found {len(matrix_files)} files containing matrices:')
for f in matrix_files:
    print(' -', f)

# Let's inspect the matrices in these files and fix any single slash linebreaks
for fpath in matrix_files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check lines inside matrix
    # In LaTeX matrix, row endings MUST be \\
    # If there are single \ followed by space or newline or symbol, fix to \\
    
    # 104年 第一題 example: \begin{bmatrix} 2\mathcal{R} & \mathcal{R} \\ \mathcal{R} & 2\mathcal{R} \end{bmatrix}
    
    # Regex to find matrix environments
    def fix_matrix(m):
        env = m.group(0)
        # Fix single slash line breaks inside matrix: e.g. " & \mathcal{R} \ \mathcal{R} & " -> " \\ "
        # Replace instances of " \ " inside matrix that should be " \\ "
        # (excluding known commands like \mathcal, \mathbf, \dots, \vdots, \cdots, \hline)
        lines = env.split('\n')
        fixed_lines = []
        for line in lines:
            # If line ends with single \ or has isolated \ between matrix entries
            line = re.sub(r'(?<=[0-9A-Za-z\}])\s+\\\s+(?=[0-9A-Za-z\{\\])', r' \\\\ ', line)
            fixed_lines.append(line)
        return '\n'.join(fixed_lines)

    new_content = re.sub(r'\\begin\{(?:bmatrix|pmatrix|matrix|vmatrix)\}[\s\S]*?\\end\{(?:bmatrix|pmatrix|matrix|vmatrix)\}', fix_matrix, content)
    
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed matrices in: {fpath}')

print('Matrix inspection completed.')
