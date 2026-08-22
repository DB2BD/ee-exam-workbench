# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)
print(f'Auditing {len(files)} markdown files for formula display errors and sync issues...')

unmatched_dollar_files = []
problematic_latex_files = []

for fpath in files:
    if '.git' in fpath or '.system_generated' in fpath or 'node_modules' in fpath:
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # 1. Check for mismatched display math $$
    num_double_dollars = text.count('$$')
    if num_double_dollars % 2 != 0:
        print(f'❌ {fpath}: Unmatched $$ (count = {num_double_dollars})')
        problematic_latex_files.append((fpath, 'Unmatched $$'))

    # 2. Check for unmatched single $
    # Remove code blocks and display math first
    t = re.sub(r'```[\s\S]*?```', '', text)
    t = re.sub(r'`[^`]*`', '', t)
    t = re.sub(r'\$\$[\s\S]*?\$\$', '', t)
    
    # Extract valid inline math $...$ on same line
    t_clean = re.sub(r'\$[^\$\n\r]+?\$', '', t)
    
    # Check if any stray $ remains
    if '$' in t_clean:
        for idx, line in enumerate(text.splitlines(), 1):
            line_no_display = re.sub(r'\$\$[\s\S]*?\$\$', '', line)
            line_no_inline = re.sub(r'\$[^\$\n\r]+?\$', '', line_no_display)
            line_no_code = re.sub(r'`[^`]*`', '', line_no_inline)
            if '$' in line_no_code:
                print(f'⚠️ {fpath}:{idx}: Unmatched $ -> {line.strip()[:80]}')
                unmatched_dollar_files.append((fpath, idx, line.strip()))

    # 3. Check for unsupported LaTeX patterns or bad formatting inside $$
    # e.g., \begin{bmatrix} with missing \\ or unescaped &
    display_matches = re.findall(r'\$\$([\s\S]*?)\$\$', text)
    for dm in display_matches:
        if r'\begin{bmatrix}' in dm and r'\\' not in dm and '\n' in dm:
            print(f'⚠️ {fpath}: Matrix with missing \\\\ row break: {dm.strip()[:60]}')
        if r'\mbox' in dm:
            print(f'⚠️ {fpath}: \\mbox used instead of \\text')
        if r'\rm ' in dm or r'\bf ' in dm:
            print(f'⚠️ {fpath}: Deprecated font switch \\rm / \\bf')

print(f'\nTotal unmatched $ found: {len(unmatched_dollar_files)}')
print(f'Total problematic display math found: {len(problematic_latex_files)}')
