# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

def restore_matrix_commands(text):
    # Fix broken command splits like "\\ mathcal" -> "\mathcal"
    for cmd in ['mathcal', 'mathbf', 'begin', 'end', 'Phi', 'Delta', 'Omega', 'text', 'theta', 'delta', 'alpha', 'beta', 'lambda', 'dots', 'vdots', 'cdots', 'hline']:
        text = re.sub(rf'\\\\\s*{cmd}', rf'\\{cmd}', text)
        text = re.sub(rf'\\+\s*{cmd}', rf'\\{cmd}', text)

    # In 104年 第一題:
    # \begin{bmatrix} 2\mathcal{R} & \mathcal{R} \\ \mathcal{R} & 2\mathcal{R} \end{bmatrix} \begin{bmatrix} \Phi_1 \\ \Phi_2 \end{bmatrix} = \begin{bmatrix} \mathcal{F}_1 \\ \mathcal{F}_2 \end{bmatrix}
    text = text.replace(r'2 \mathcal{R} & \mathcal{R} \ \mathcal{R} & 2 \mathcal{R}', r'2\mathcal{R} & \mathcal{R} \\ \mathcal{R} & 2\mathcal{R}')
    text = text.replace(r'2\mathcal{R} & \mathcal{R} \ \mathcal{R} & 2\mathcal{R}', r'2\mathcal{R} & \mathcal{R} \\ \mathcal{R} & 2\mathcal{R}')
    text = text.replace(r'\Phi_1 \ \Phi_2', r'\Phi_1 \\ \Phi_2')
    text = text.replace(r'\mathcal{F}_1 \ \mathcal{F}_2', r'\mathcal{F}_1 \\ \mathcal{F}_2')
    text = text.replace(r'\\ \end{bmatrix}', r'\end{bmatrix}')
    text = text.replace(r'\\\end{bmatrix}', r'\end{bmatrix}')
    text = text.replace(r'\\ \end{pmatrix}', r'\end{pmatrix}')
    text = text.replace(r'\\\end{pmatrix}', r'\end{pmatrix}')
    
    return text

fixed = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    cleaned = restore_matrix_commands(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'✨ Fixed matrix commands in: {fpath}')
        fixed += 1

print(f'\nTotal files fixed: {fixed}')
