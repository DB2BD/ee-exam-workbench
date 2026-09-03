import glob
import re
import os

def fix_image_order():
    for fpath in glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md'):
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        def repl_block(match):
            block = match.group(0)
            imgs = re.findall(r'([\w\d_—–\-]+_p\d+\.png)', block)
            if not imgs:
                return block
            
            # Deduplicate while preserving sorted order
            unique_imgs = sorted(list(dict.fromkeys(imgs)), key=lambda x: (x.split('_p')[0], int(x.split('_p')[1].split('.')[0]) if '_p' in x else 0))
            
            res = ['### 📷 官方試卷與電路圖檔對照\n']
            for img in unique_imgs:
                res.append(f'![[{img}|750]]\n')
            return '\n'.join(res)

        new_content = re.sub(r'### 📷 官方試卷與電路圖檔對照[\s\S]*?(?=\[⬆ 回到目錄導覽\]|## 📌|\Z)', repl_block, content)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)

fix_image_order()
print('All images in all 6 subjects formatted in Obsidian native embed format with page ordering!')
