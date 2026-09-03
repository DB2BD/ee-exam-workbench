# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

def pristine_clean(text):
    # Remove bad prefixes \f\frac, \t \times, \a \approx, \t \text, etc.
    text = text.replace(r'\f\frac', r'\frac')
    text = text.replace(r'\t \times', r'\times')
    text = text.replace(r'\t\times', r'\times')
    text = text.replace(r'\a \approx', r'\approx')
    text = text.replace(r'\a\approx', r'\approx')
    text = text.replace(r'\t \text', r'\text')
    text = text.replace(r'\t\text', r'\text')
    text = text.replace(r'\t \theta', r'\theta')
    text = text.replace(r'\t\theta', r'\theta')
    text = text.replace(r'\t \tau', r'\tau')
    text = text.replace(r'\t\tau', r'\tau')
    text = text.replace(r'\t \tan', r'\tan')
    text = text.replace(r'\t\tan', r'\tan')
    text = text.replace(r'\v \vec', r'\vec')
    text = text.replace(r'\v\vec', r'\vec')
    text = text.replace(r'\b \beta', r'\beta')
    text = text.replace(r'\b\beta', r'\beta')
    text = text.replace(r'\b \mathbf', r'\mathbf')
    text = text.replace(r'\b\mathbf', r'\mathbf')
    
    # Replace single backslash letters before commands like \f\frac -> \frac
    text = re.sub(r'\\f(?=\\frac)', '', text)
    text = re.sub(r'\\a(?=\\approx)', '', text)
    text = re.sub(r'\\t(?=\\text|\s*\\text|\s*\\times|\s*\\theta|\s*\\tau|\s*\\tan)', '', text)
    text = re.sub(r'\\v(?=\\vec|\s*\\vec)', '', text)
    text = re.sub(r'\\b(?=\\beta|\s*\\beta|\s*\\mathbf)', '', text)
    
    # Replace broken LaTeX command fragments without backslash
    text = re.sub(r'(?<!\\)\bfrac\{', r'\\frac{', text)
    text = re.sub(r'(?<!\\)\btimes\b', r'\\times', text)
    text = re.sub(r'(?<!\\)\bapprox\b', r'\\approx', text)
    text = re.sub(r'(?<!\\)\btheta\b', r'\\theta', text)
    text = re.sub(r'(?<!\\)\btau\b', r'\\tau', text)
    text = re.sub(r'(?<!\\)\balpha\b', r'\\alpha', text)
    text = re.sub(r'(?<!\\)\bbeta\b', r'\\beta', text)
    text = re.sub(r'(?<!\\)\bvec\{', r'\\vec{', text)
    text = re.sub(r'(?<!\\)\bmathbf\{', r'\\mathbf{', text)
    text = re.sub(r'(?<!\\)\bmathcal\{', r'\\mathcal{', text)
    text = re.sub(r'(?<!\\)\bsqrt\{', r'\\sqrt{', text)
    text = re.sub(r'(?<!\\)\bDelta\b', r'\\Delta', text)
    text = re.sub(r'(?<!\\)\bOmega\b', r'\\Omega', text)
    text = re.sub(r'(?<!\\)\bPhi\b', r'\\Phi', text)
    text = re.sub(r'(?<!\\)\bmu_0\b', r'\\mu_0', text)
    text = re.sub(r'(?<!\\)\bmu_r\b', r'\\mu_r', text)
    text = re.sub(r'(?<!\\)\bpi\b', r'\\pi', text)
    
    # Fix double backslashes
    text = text.replace(r'\\\frac', r'\frac')
    text = text.replace(r'\\\times', r'\times')
    text = text.replace(r'\\\text', r'\text')
    text = text.replace(r'\\\approx', r'\approx')
    text = text.replace(r'\\\theta', r'\theta')
    text = text.replace(r'\\\tau', r'\tau')
    text = text.replace(r'\\\alpha', r'\alpha')
    text = text.replace(r'\\\beta', r'\beta')
    text = text.replace(r'\\\mathbf', r'\mathbf')
    text = text.replace(r'\\\mathcal', r'\mathcal')
    text = text.replace(r'\\\sqrt', r'\sqrt')
    text = text.replace(r'\\\pi', r'\pi')
    text = text.replace(r'\\\mu', r'\mu')
    text = text.replace(r'\\\Phi', r'\Phi')
    text = text.replace(r'\\\Omega', r'\Omega')
    
    # Remove any stray control chars below ASCII 32 except 9, 10, 13
    cleaned = []
    for c in text:
        if ord(c) < 32 and ord(c) not in (9, 10, 13):
            continue
        cleaned.append(c)
    text = ''.join(cleaned)
    
    return text

count = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    cleaned = pristine_clean(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'✨ Pristine cleaned: {fpath}')
        count += 1

print(f'\nTotal files polished to pristine state: {count} / {len(files)}')
