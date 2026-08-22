import glob
import os
import re

# Build map of base filenames to relative paths
all_files = {}
for root, dirs, files in os.walk('.'):
    if '.obsidian' in root or '.git' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            base = os.path.splitext(f)[0]
            rel = os.path.relpath(os.path.join(root, f), '.')
            all_files[base] = rel.replace('\\', '/')

print(f'Indexed {len(all_files)} markdown files.')

# Clean sample notes
for fpath in glob.glob('📝 個人題解與錯題本/**/*.md', recursive=True) + glob.glob('📌 *.md') + glob.glob('💡 *.md'):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix short KB links to full paths
    content = content.replace('[[01_直流電路與戴維寧諾頓等效]]', '[[🧠 核心考點知識庫/01_電路學/01_直流電路與戴維寧諾頓等效|01_直流電路與戴維寧諾頓等效]]')
    content = content.replace('[[01_常微分方程ODE與尤拉柯西方程]]', '[[🧠 核心考點知識庫/03_工程數學/01_常微分方程ODE與尤拉柯西方程|01_常微分方程ODE與尤拉柯西方程]]')
    content = content.replace('[[01_標么系統與對稱成分故障分析]]', '[[🧠 核心考點知識庫/05_電力系統/01_標么系統與對稱成分故障分析|01_標么系統與對稱成分故障分析]]')
    content = content.replace('[[01_變壓器等效電路與效率計算]]', '[[🧠 核心考點知識庫/04_電機機械/01_變壓器等效電路與效率計算|01_變壓器等效電路與效率計算]]')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated all sample and guide wikilinks!')
