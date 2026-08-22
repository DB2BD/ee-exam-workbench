# -*- coding: utf-8 -*-
import os
import re

def clean_ocr_artifacts(text):
    lines = text.split('\n')
    cleaned_lines = []
    
    skip_tokens = {
        'θ', 'φ', 'α', 'β', 'N1', 'I1', 'N2', 'I2', 'M', 'φl1', 'φl2', 'RM', 'Rl1', 'Rl2',
        '950', 'r', 'μ=', '70', 'N =', '匝', 'i', 'a', 'b', 'AC', '圖一', '圖1', '圖2', '圖3', '圖4',
        'd', 't', 'dt', 'v t', '1 cos2', 'cos', 'sin(', ')', 'sin sin', '0.2/ s', '×', '、'
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped in skip_tokens or (len(stripped) <= 3 and stripped in 'θφαβiφda±×、'):
            continue
        cleaned_lines.append(line)
        
    res = '\n'.join(cleaned_lines)
    
    # Fix broken math terms in sentences
    res = res.replace('110\n2 V', '110\\sqrt{2}\\text{ V}')
    res = res.replace('110\n2', '110\\sqrt{2}')
    res = res.replace('110\n2 sin', '110\\sqrt{2} \\sin')
    res = res.replace('0.$1\\ \\Omega$', '$0.1\\ \\Omega$')
    res = res.replace('0.$10\\ \\Omega$', '$0.10\\ \\Omega$')
    res = res.replace('2.$5\\ \\Omega$', '$2.5\\ \\Omega$')
    res = res.replace('3.5+j6.$2\\ \\Omega$', '$3.5+j6.2\\ \\Omega$')
    res = res.replace('7.2+j4.$8\\ \\Omega$', '$7.2+j4.8\\ \\Omega$')
    res = res.replace('0.$05\\ \\Omega$', '$0.05\\ \\Omega$')
    res = res.replace('1.$0\\ \\Omega$', '$1.0\\ \\Omega$')
    res = res.replace('2.$0\\ \\Omega$', '$2.0\\ \\Omega$')
    res = res.replace('Ra=2.$01\\ \\Omega$', '$R_a = 2.01\\ \\Omega$')
    res = res.replace('subseteq', '\\mathcal{R}')
    res = res.replace('⊆', '\\mathcal{R}')
    
    # Fix broken hint formulas safely with lambda
    hint_text = '（提示：$v(t) = N\\frac{d\\Phi}{dt}, T = \\frac{\\partial W_{fld}}{\\partial\\theta} = -\\frac{1}{2}\\Phi^2\\frac{d\\mathcal{R}}{d\\theta}$）'
    res = re.sub(r'（Hint\s*：[\s\S]*?）', lambda m: hint_text, res)
    
    # Clean multiple consecutive empty lines
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res

files_to_clean = [
    '依考科分類/04_電機機械/04_電機機械_歷屆試題彙編_104-114年.md',
    '依考科分類/04_電機機械.md',
    '依考科分類/05_電力系統/05_電力系統_歷屆試題彙編_104-114年.md',
    '依考科分類/05_電力系統.md'
]

for fpath in files_to_clean:
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        cleaned = clean_ocr_artifacts(text)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'✅ Cleaned OCR fragments in: {fpath}')

print('All target files cleaned successfully!')
