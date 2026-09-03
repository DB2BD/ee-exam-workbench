# -*- coding: utf-8 -*-
import glob
import os
import re

files = glob.glob('**/*.md', recursive=True)

def comprehensive_latex_repair(text):
    # 1. Fix all broken \right variants
    text = re.sub(r'(?<!\\)\bright\b', r'\\right', text)
    text = re.sub(r'(?<![\\r])\bight\)', r'\\right)', text)
    text = re.sub(r'(?<![\\r])\bight\]', r'\\right]', text)
    text = re.sub(r'(?<![\\r])\bight\}', r'\\right}', text)
    text = re.sub(r'(?<![\\r])\bight\|', r'\\right|', text)
    text = re.sub(r'(?<![\\r])\bight\.', r'\\right.', text)
    text = re.sub(r'(?<![\\r])\bight\b', r'\\right', text)
    
    # 2. Fix \rightarrow and \Rightarrow
    text = re.sub(r'(?<!\\)\brightarrow\b', r'\\rightarrow', text)
    text = re.sub(r'(?<![\\r])\bightarrow\b', r'\\rightarrow', text)
    text = re.sub(r'(?<!\\)\bRightarrow\b', r'\\Rightarrow', text)
    text = re.sub(r'(?<![\\r])\bightarrow\b', r'\\Rightarrow', text)
    
    # 3. Fix \rho, \rangle
    text = re.sub(r'(?<!\\)\brho\b', r'\\rho', text)
    text = re.sub(r'(?<!\\)\brangle\b', r'\\rangle', text)
    
    # 4. Fix \left variants
    text = re.sub(r'(?<!\\)\bleft\(', r'\\left(', text)
    text = re.sub(r'(?<!\\)\bleft\[', r'\\left[', text)
    text = re.sub(r'(?<!\\)\bleft\{', r'\\left{', text)
    text = re.sub(r'(?<!\\)\bleft\|', r'\\left|', text)
    text = re.sub(r'(?<!\\)\bleft\.', r'\\left.', text)
    text = re.sub(r'(?<!\\)\bleft\b', r'\\left', text)

    # 5. Fix \frac
    text = re.sub(r'(?<!\\)\bfrac\{', r'\\frac{', text)
    text = re.sub(r'(?<![\\f])\brac\{', r'\\frac{', text)
    
    # 6. Fix \times, \text, \theta, \tau, \tan
    text = re.sub(r'(?<!\\)\btimes\b', r'\\times', text)
    text = re.sub(r'(?<![\\t])\bimes\b', r'\\times', text)
    text = re.sub(r'(?<!\\)\btext\{', r'\\text{', text)
    text = re.sub(r'(?<![\\t])\bext\{', r'\\text{', text)
    text = re.sub(r'(?<!\\)\btheta\b', r'\\theta', text)
    text = re.sub(r'(?<![\\t])\bheta\b', r'\\theta', text)
    text = re.sub(r'(?<!\\)\btau\b', r'\\tau', text)
    text = re.sub(r'(?<![\\t])\bau\b', r'\\tau', text)
    text = re.sub(r'(?<!\\)\btan\b', r'\\tan', text)
    text = re.sub(r'(?<![\\t])\ban\b', r'\\tan', text)
    
    # 7. Fix \approx, \alpha, \angle
    text = re.sub(r'(?<!\\)\bapprox\b', r'\\approx', text)
    text = re.sub(r'(?<![\\a])\bpprox\b', r'\\approx', text)
    text = re.sub(r'(?<!\\)\balpha\b', r'\\alpha', text)
    text = re.sub(r'(?<![\\a])\blpha\b', r'\\alpha', text)
    text = re.sub(r'(?<!\\)\bangle\b', r'\\angle', text)
    
    # 8. Fix \beta, \begin, \mathbf, \bar
    text = re.sub(r'(?<!\\)\bbeta\b', r'\\beta', text)
    text = re.sub(r'(?<![\\b])\beta\b', r'\\beta', text)
    text = re.sub(r'(?<!\\)\bbegin\{', r'\\begin{', text)
    text = re.sub(r'(?<![\\b])\begin\{', r'\\begin{', text)
    text = re.sub(r'(?<!\\)\bmathbf\{', r'\\mathbf{', text)
    text = re.sub(r'(?<!\\)\bmathcal\{', r'\\mathcal{', text)
    
    # 9. Fix \vec
    text = re.sub(r'(?<!\\)\bvec\{', r'\\vec{', text)
    text = re.sub(r'(?<![\\v])\bec\{', r'\\vec{', text)
    
    # 10. Fix double-slashes created mistakenly
    text = text.replace(r'\\\right', r'\right')
    text = text.replace(r'\\\left', r'\left')
    text = text.replace(r'\\\frac', r'\frac')
    text = text.replace(r'\\\times', r'\times')
    text = text.replace(r'\\\text', r'\text')
    text = text.replace(r'\\\approx', r'\approx')
    text = text.replace(r'\\\theta', r'\theta')
    text = text.replace(r'\\\tau', r'\tau')
    text = text.replace(r'\\\alpha', r'\alpha')
    text = text.replace(r'\\\beta', r'\beta')
    text = text.replace(r'\\\begin', r'\begin')
    text = text.replace(r'\\\mathbf', r'\mathbf')
    text = text.replace(r'\\\mathcal', r'\mathcal')
    text = text.replace(r'\\\vec', r'\vec')
    text = text.replace(r'\\\rho', r'\rho')
    text = text.replace(r'\\\rightarrow', r'\rightarrow')
    
    return text

repaired_count = 0
for fpath in sorted(files):
    if not os.path.isfile(fpath): continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    cleaned = comprehensive_latex_repair(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'✅ Repaired: {fpath}')
        repaired_count += 1

print(f'\nTotal files repaired: {repaired_count} / {len(files)}')
