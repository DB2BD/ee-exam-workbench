# -*- coding: utf-8 -*-
import re
import os

for fpath in sorted(os.listdir('依考科分類')):
    if not fpath.endswith('.md'):
        continue
    full = os.path.join('依考科分類', fpath)
    with open(full, 'r', encoding='utf-8') as fp:
        txt = fp.read()
        
    # Clean double headers like '#### 一、 #### 一、' or '#### 一、 #### 二、'
    txt = re.sub(r'####\s*[一二三四五六七八九十]+\s*、\s*####\s*([一二三四五六七八九十]+)\s*、', r'#### \1、', txt)
    txt = re.sub(r'####\s*([一二三四五六七八九十]+)\s*、\s*####\s*\1\s*、', r'#### \1、', txt)
    
    with open(full, 'w', encoding='utf-8') as fp:
        fp.write(txt)
        
    print(f'✅ Cleaned double headers in {full}')
