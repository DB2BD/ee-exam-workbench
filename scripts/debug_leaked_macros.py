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
    if s == '$$':
        in_display = not in_display
        continue
    if in_display:
        continue
    if s.startswith('$$') and s.endswith('$$') and len(s) > 4:
        continue
    # Remove inline math
    no_inline = re.sub(r'(?<!\\)\$[^\$\n]+(?<!\\)\$', ' ', l)
    leaked = re.findall(r'(?<![A-Za-z0-9\$\\])\\(?:Omega|tau|frac|sqrt|angle|approx)\b', no_inline)
    if leaked:
        print(f"Line {i}: {leaked} -> {l.strip()[:100]}")
