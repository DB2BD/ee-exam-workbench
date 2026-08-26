# -*- coding: utf-8 -*-
import re

file_path = '📝 個人題解與錯題本/01_電路學/104年_電路學_全卷完整詳細題解.md'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_code = False
in_display = False

for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    
    # Check display state
    if s == '$$':
        in_display = not in_display
        # print(f"Line {i}: '$$' toggled display to {in_display}")
        continue
        
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
        
    if '$$' in s:
        print(f"Line {i}: stray $$ -> {s}")
        
    # Check inline dollar balance on line
    no_esc = s.replace(r'\$', '')
    d_count = no_esc.count('$')
    if d_count % 2 != 0:
        print(f"Line {i}: ODD single $ ({d_count}) -> {s}")
