# -*- coding: utf-8 -*-
"""
fix_all_181_line_issues.py
==========================
Systematically resolves all remaining 181 line-level delimiter issues.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_line(line):
    s = line.strip()
    if not s or s.startswith('```') or s == '$$':
        return line
    if s.startswith('$$') and s.endswith('$$') and s.count('$$') == 2:
        return line

    # 1. Stray $$}
    if s == '$$}':
        return ''

    # 2. Fix "$$\implies$" -> "$\implies$"
    line = line.replace(r'$$\implies$', r'$\implies$')
    line = line.replace(r'$$\Delta 負載', r'$\Delta$ 負載')
    line = line.replace(r'$$*KCL 核算：', r'*KCL 核算：')

    # 3. Fix bullet items starting with "- $$" and ending with "$。$" or "$":
    # e.g., "- $$\mathbf{u}_1 = \mathbf{v}_1$。$" -> "- $\mathbf{u}_1 = \mathbf{v}_1$。"
    # e.g., "- $$\mathcal{L}\{u(t-a)\} = \frac{e^{-as}}{s}$。$" -> "- $\mathcal{L}\{u(t-a)\} = \frac{e^{-as}}{s}$。"
    m_bullet_stray_dd = re.match(r'^(\s*[-*]|\s*\d+\.)\s*\$\$([^\$\n]+)\$([。，；：].*)\$$', line)
    if m_bullet_stray_dd:
        prefix = m_bullet_stray_dd.group(1)
        core = m_bullet_stray_dd.group(2).strip()
        punct = m_bullet_stray_dd.group(3)
        return f"{prefix}${core}${punct}\n"

    # 4. Fix "- $$\text{CMRR} = ...$。$"
    line = re.sub(r'(\s*[-*]|\s*\d+\.)\s*\$\$([^\$\n]+)\$。\$', r'\1 $\2$。\n', line)
    line = re.sub(r'(\s*[-*]|\s*\d+\.)\s*\$\$([^\$\n]+)\$：\$', r'\1 $\2$：\n', line)

    # 5. Fix bullet items with "- $$formula$" -> "- $formula$"
    line = re.sub(r'(\s*[-*]|\s*\d+\.)\s*\$\$([^\$\n]+)\$$', r'\1 $\2$\n', line)

    # 6. Fix "- [text]：$$formula$" -> "- [text]：$formula$"
    line = re.sub(r'(\s*[-*]|\s*\d+\.)\s*([^\$\n]+：)\$\$([^\$\n]+)\$$', r'\1 \2$\3$\n', line)

    # 7. Fix header lines ending with "$A ="
    line = re.sub(r'^(##\s+[^\n]+)\$([A-Za-z0-9_]+)\s*=\s*$', r'\1$\2$：\n', line)

    # 8. Fix missing opening $ on bullet items with "t=..." or "J_..."
    line = re.sub(r'^(\s*[-*]\s+)([a-zA-Z0-9_\{\}\\]+\s*=\s*[0-9A-Za-z_\\\{\}\(\)\+\-\*/\^]+)\$', r'\1$\2$', line)
    
    # 9. Clean trailing $$ on inline math with Chinese
    line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\u4e00-\u9fff，。；：\s\(\)]|$)', r'\1$', line)
    line = re.sub(r'([，。；：\s\u4e00-\u9fff])\${2,}$', r'\1', line)
    line = re.sub(r'([0-9A-Za-z\^_\+\-\*/\)\'\]\s])\${2,}$', r'\1$', line)

    # 10. Check if single $ count is odd, and line ends with math token
    no_esc = line.replace(r'\$', '')
    if no_esc.count('$') % 2 != 0:
        # If line starts with bullet and math formula:
        if re.search(r'(\\[A-Za-z]+|\}|[0-9A-Za-z\^_\+\-\*/\)\'\s\]])\s*$', line.rstrip()):
            line = line.rstrip() + '$\n'

    return line

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [fix_line(l) for l in lines]
    content = "".join(new_lines)

    # Specific cleanups
    content = content.replace(r'$$V_o = D V_s$$$', r'$$V_o = D V_s$$')
    content = content.replace(r'$$\Delta V\% =', r'$$\Delta V\% = ')
    content = content.replace(r'$$I = 0 \implies', r'$$I = 0 \implies ')

    if content != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if fix_file(f):
            count += 1
            print(f"🎯 Repaired line issues in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
