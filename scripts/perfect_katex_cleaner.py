# -*- coding: utf-8 -*-
"""
perfect_katex_cleaner.py
========================
Fixes multiline matrix environments, unclosed display math, and spurious $$ wraps.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_content(content):
    # 1. Fix double-double dollars
    content = content.replace('$$$$', '$$')
    
    # 2. Fix lines where Chinese text was incorrectly wrapped in $$...$$
    # e.g., "$$並聯電容大幅降低電抗，使電壓回升至 $\mathbf{V_{2,new} = 1.080\text{ pu}}$。$$"
    def unwrap_chinese_math(m):
        inner = m.group(1)
        # If inner contains Chinese characters and is not a pure formula
        if re.search(r'[\u4e00-\u9fff]', inner) and not re.search(r'\\text\{[\u4e00-\u9fff]+\}', inner):
            return inner
        return m.group(0)
        
    content = re.sub(r'\$\$([^\$\n]*[\u4e00-\u9fff]+[^\$\n]*)\$\$', unwrap_chinese_math, content)

    # 3. Fix multiline matrices where \begin{bmatrix} was closed by $$ on same line
    # e.g., "$$\mathbf{Z}_{bus} = \begin{bmatrix}$$\n   j0.225...\n   \end{bmatrix}\text{ pu}$$"
    content = re.sub(
        r'\$\$(\s*\\mathbf\{[^\}]+\}\s*=\s*(?:j\s*)?\\begin\{(?:bmatrix|pmatrix|matrix|cases|aligned)\})\$\$\n',
        r'$$\n\1\n',
        content
    )

    # Fix \end{bmatrix} line missing opening
    content = re.sub(
        r'\n(\s*\\begin\{(?:bmatrix|pmatrix|matrix|cases|aligned)\})\$\$\n',
        r'\n$$\n\1\n',
        content
    )

    # 4. Fix specific files
    # 01_電路學/01_直流電路與戴維寧諾頓等效.md
    # CLAUDE-SPEC.md
    # Ensure \begin{aligned} ... \end{aligned} is inside $$ ... $$
    def wrap_aligned(m):
        full = m.group(0)
        if full.startswith('$$') and full.endswith('$$'):
            return full
        return f"$$\n{full}\n$$"
        
    content = re.sub(r'(?<!\$)\\begin\{aligned\}[\s\S]*?\\end\{aligned\}(?!\$)', wrap_aligned, content)
    content = re.sub(r'(?<!\$)\\begin\{bmatrix\}[\s\S]*?\\end\{bmatrix\}(?!\$)', wrap_aligned, content)

    # Clean any $$$
    content = re.sub(r'\${3,}', '$$', content)

    return content

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            orig = fp.read()
        cleaned = fix_content(orig)
        if cleaned != orig:
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(cleaned)
            count += 1
            print(f"✅ Cleaned KaTeX in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
