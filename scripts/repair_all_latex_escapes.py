# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)
print(f'Total markdown files found: {len(files)}')

def restore_corrupted_latex(text):
    # Fix formfeed \x0c
    text = text.replace('\x0crac', r'\frac')
    text = text.replace('\x0c', '')  # any stray formfeed
    
    # Fix bell \x07
    text = text.replace('\x07pprox', r'\approx')
    text = text.replace('\x07lpha', r'\alpha')
    text = text.replace('\x07', '')
    
    # Fix vtab \x0b
    text = text.replace('\x0bec', r'\vec')
    text = text.replace('\x0b', '')
    
    # Fix backspace \x08
    text = text.replace('\x08eta', r'\beta')
    text = text.replace('\x08f', r'\mathbf')
    text = text.replace('\x08', '')
    
    # Fix tab \x09 inside LaTeX terms
    text = text.replace('\tчью', '')
    text = text.replace('\times', r'\times')
    text = text.replace('\text', r'\text')
    text = text.replace('\theta', r'\theta')
    text = text.replace('\tau', r'\tau')
    text = text.replace('\tan', r'\tan')
    
    # Replace broken string artifacts where slash was completely eaten
    # 1. rac -> \frac
    text = re.sub(r'(?<!\\)rac\{', r'\\frac{', text)
    # 2. 	imes -> \times
    text = re.sub(r'[\t\s]imes\b', r' \\times', text)
    text = re.sub(r'(?<=[0-9A-Za-z\)\}])\s*imes\b', r' \\times', text)
    # 3. 	ext -> \text
    text = re.sub(r'[\t\s]ext\{', r' \\text{', text)
    text = re.sub(r'(?<=[0-9A-Za-z\)\}])\s*ext\{', r' \\text{', text)
    # 4. pprox -> \approx
    text = re.sub(r'[\t\s]pprox\b', r' \\approx', text)
    text = re.sub(r'(?<=[0-9A-Za-z\)\}])\s*pprox\b', r' \\approx', text)
    # 5. lpha -> \alpha
    text = re.sub(r'(?<!\\)\blpha\b', r'\\alpha', text)
    # 6. heta -> \theta
    text = re.sub(r'(?<!\\)\bheta\b', r'\\theta', text)
    
    # Clean up double slashes before \frac if any introduced
    text = text.replace(r'\\\frac', r'\frac')
    text = text.replace(r'\\\times', r'\times')
    text = text.replace(r'\\\text', r'\text')
    text = text.replace(r'\\\approx', r'\approx')
    
    # Remove any remaining raw control characters below ASCII 32 except \n (10) and \r (13) and \t (9)
    cleaned_chars = []
    for c in text:
        code = ord(c)
        if code < 32 and code not in (10, 13, 9):
            continue
        cleaned_chars.append(c)
    text = ''.join(cleaned_chars)
    
    return text

fixed_files = 0
for fpath in files:
    if not os.path.isfile(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    repaired = restore_corrupted_latex(orig)
    if repaired != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(repaired)
        print(f'🔧 Repaired LaTeX in: {fpath}')
        fixed_files += 1

print(f'\nTotal files successfully repaired: {fixed_files} / {len(files)}')
