# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'\\begin\{(?:bmatrix|pmatrix|matrix|vmatrix)\}[\s\S]*?\\end\{(?:bmatrix|pmatrix|matrix|vmatrix)\}', content)
    if matches:
        print(f'=== {fpath} === ({len(matches)} matrices)')
        for i, m in enumerate(matches, 1):
            print(f'--- Matrix {i} ---')
            print(m)
            print()
