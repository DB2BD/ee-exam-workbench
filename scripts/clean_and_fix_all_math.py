# -*- coding: utf-8 -*-
import glob
import os
import re

directories = ['📝 個人題解與錯題本', '依考科分類', '💼 個人職涯發展與國際戰略']
all_files = []
for d in directories:
    all_files.extend(glob.glob(f'{d}/**/*.md', recursive=True))

print(f'Total markdown files to check: {len(all_files)}')

def clean_math_in_content(content):
    # 1. Fix nested \mathbf inside \mathbf: \mathbf{... \mathbf{X} ...} -> \mathbf{... X ...}
    while re.search(r'\\mathbf\{([^{}]*)\\mathbf\{([^{}]*)\}([^{}]*)\}', content):
        content = re.sub(r'\\mathbf\{([^{}]*)\\mathbf\{([^{}]*)\}([^{}]*)\}', r'\\mathbf{\1\2\3}', content)
    
    # 2. Fix nested \mathbf like \mathbf{a = \mathbf{0.6325}} -> \mathbf{a} = \mathbf{0.6325}
    content = re.sub(r'\\mathbf\{([A-Za-z0-9_\\,\s\(\)\^]+)\s*=\s*\\mathbf\{([^}]+)\}\}', r'\\mathbf{\1} = \\mathbf{\2}', content)
    content = re.sub(r'\\mathbf\{([A-Za-z0-9_\\,\s\(\)\^]+)\s*=\s*([^}]+)\s*=\s*\\mathbf\{([^}]+)\}\}', r'\\mathbf{\1} = \2 = \\mathbf{\3}', content)

    # 3. Fix unneeded bold wrapping around math: **$...$** -> $...$ or clean up
    content = re.sub(r'\*\*\s*\$\$([\s\S]*?)\$\$\s*\*\*', r'$$\1$$', content)
    
    # 4. Clean double/triple spaces inside LaTeX
    content = re.sub(r'\\mathbf\{\s+', r'\\mathbf{', content)
    content = re.sub(r'\s+\}', r'}', content)

    # 5. Fix common OCR artifacts
    content = content.replace('subseteq', r'\mathcal{R}')
    content = content.replace('⊆', r'\mathcal{R}')
    
    return content

fixed_count = 0
for fpath in sorted(all_files):
    if not os.path.isfile(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    cleaned = clean_math_in_content(orig)
    if cleaned != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'✅ Polished: {fpath}')
        fixed_count += 1
    else:
        print(f'✨ Pristine: {fpath}')

print(f'\nTotal files polished: {fixed_count} / {len(all_files)}')
