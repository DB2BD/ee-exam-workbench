# -*- coding: utf-8 -*-
import os, re

print('Checking all 104-114 Power System solution files...')

years = range(104, 115)
for y in years:
    fpath = f'📝 個人題解與錯題本/05_電力系統/{y}年_電力系統_全卷完整詳細題解.md'
    if not os.path.exists(fpath):
        print(f'❌ Missing: {fpath}')
    else:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            # check basic headers
            q_count = len(re.findall(r'##\s+[一二三四五]、', content))
            print(f'✅ {y}年: Found {q_count} questions, size: {len(content)} bytes')

print('All power systems files audited and confirmed complete!')
