# -*- coding: utf-8 -*-
import os
import re

# Update all subject markdown files to ensure both standard Obsidian wikilinks ![[...|750]] and clean layouts
for subj in ['01_電路學', '02_電子學_含電力電子', '03_工程數學', '04_電機機械', '05_電力系統', '06_工業配電']:
    md_path = f'依考科分類/{subj}.md'
    if not os.path.exists(md_path):
        continue
        
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    # Standardize image embeds to Obsidian native format ![[filename.png|750]]
    # Replace markdown images ![alt](filename.png) -> ![[filename.png|750]]
    text = re.sub(r'!\[([^\]]*)\]\(([^\)]+\.png)\)', r'![[\2|750]]', text)
    # Clean up double extensions or path prefixes in wikilinks
    text = re.sub(r'!\[\[(?:.*?\/)?([^\/\]]+\.png)(?:\|(\d+))?\]\]', r'![[\1|750]]', text)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)
        
    print(f'✅ Standardized Obsidian image wikilinks in {md_path}')
