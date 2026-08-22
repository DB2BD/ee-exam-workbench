# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

fixed_count = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove stray "\b\" or "\b " before commands
    orig = content
    content = content.replace(r'\b\begin', r'\begin')
    content = content.replace(r'\b \begin', r'\begin')
    content = content.replace(r'\b\mathbf', r'\mathbf')
    content = content.replace(r'\b \mathbf', r'\mathbf')
    content = content.replace(r'\b\Delta', r'\Delta')
    content = content.replace(r'\b\theta', r'\theta')
    content = content.replace(r'\b\Phi', r'\Phi')
    content = content.replace(r'\b\mathcal', r'\mathcal')
    content = re.sub(r'\\b(?=\\[A-Za-z])', '', content)
    
    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'🧹 Cleaned stray \\b in: {fpath}')
        fixed_count += 1

print(f'\nTotal files cleaned: {fixed_count}')
