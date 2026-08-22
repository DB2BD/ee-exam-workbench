# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

def cleanup_latex_formatting(text):
    # 1. Fix broken \to like "\t o" or "\t o "
    text = re.sub(r'\\t\s*o\b', r'\\to', text)
    text = re.sub(r'[\t\s]o\s*\\infty', r' \\to \\infty', text)
    text = text.replace(r'\mu_c \to \infty', r'\mu_c \to \infty')
    text = text.replace(r'\mu_c 	o \infty', r'\mu_c \to \infty')
    
    # 2. Fix \left( ... \n\right) -> \left( ... \right)
    # Remove awkward newlines before \right) or \right] or \right}
    text = re.sub(r'(\S)\s*\n\s*(\\right[\)\]\}\|\.])', r'\1 \2', text)
    text = re.sub(r'(\\left[\(\[\{\|\.])\s*\n\s*(\S)', r'\1 \2', text)
    
    # 3. Ensure \left( \frac{...}{...} \right) is on a single continuous line inside math
    text = re.sub(r'\\left\(\s*\\frac\{([^}]+)\}\{([^}]+)\}\s*\\right\)', r'\\left( \\frac{\1}{\2} \\right)', text)
    
    # 4. Clean any remaining broken \t, \a, \f artifacts
    text = text.replace(r'\t ', ' ')
    text = text.replace(r'\a ', ' ')
    text = text.replace(r'\f ', ' ')
    text = text.replace(r'\v ', ' ')
    text = text.replace(r'\b ', ' ')
    
    return text

fixed = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    cleaned = cleanup_latex_formatting(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'🌟 Cleaned: {fpath}')
        fixed += 1

print(f'\nTotal files polished: {fixed}')
