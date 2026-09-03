# -*- coding: utf-8 -*-
"""
sanitize_all_dollars_completely.py
==================================
Performs complete, pristine sanitization of all math delimiters across every markdown file.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sanitize_line(line):
    s = line.strip()
    if not s or s.startswith('```'):
        return line

    # 1. Clean multi-dollars: $$$$ -> $$, $$$ -> $$
    line = re.sub(r'\${3,}', '$$', line)

    # 2. Fix bullet items starting with "- $$" or "* $$" or "1. $$":
    # e.g. "- $$由法拉第定律：$V \approx E..." -> "- 由法拉第定律：$V \approx E..."
    # e.g. "- $$中性點電壓：$\mathbf{V}_N..." -> "- 中性點電壓：$\mathbf{V}_N..."
    line = re.sub(r'^(\s*[-*]|\s*\d+\.)\s*\$\$(?=[\u4e00-\u9fff\w])', r'\1 ', line)

    # 3. Fix "$$$$\mathbf{...}$$$$" or "$$\mathbf{...}$$$$" -> "$$\mathbf{...}$$"
    m_display = re.match(r'^(\s*)\$\$(.+)\$\$$', line)
    if m_display:
        indent = m_display.group(1)
        core = m_display.group(2).strip()
        core = core.strip('$')
        line = f"{indent}$${core}$$\n"

    # 4. Clean trailing $$ on bullet points with Chinese:
    # e.g. "* 中性點電壓：$\mathbf{V}_N = 273.2\text{ V}$$" -> "* 中性點電壓：$\mathbf{V}_N = 273.2\text{ V}$"
    if re.search(r'[\u4e00-\u9fff]', line):
        line = re.sub(r'(\$[^\$\n]+)\$\$(?=[\u4e00-\u9fff，。；：\s\(\)]|$)', r'\1$', line)
        line = re.sub(r'([，。；：\s\u4e00-\u9fff])\${2,}$', r'\1', line)

    return line

def sanitize_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = [sanitize_line(l) for l in lines]
    content = "".join(new_lines)
    
    # Specific fixes
    # 05 Power 104 Q4 line 123
    content = content.replace(
        "2. **負載端電壓**：\n   I_{L2} = ",
        "2. **負載端電壓**：\n   $$I_{L2} = "
    )
    content = content.replace(
        "\\implies \\mathbf{V_2 = 0.931\\text{ pu}}\n3. **電容補償後電壓**：",
        "\\implies \\mathbf{V_2 = 0.931\\text{ pu}}$$\n3. **電容補償後電壓**："
    )

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
        if sanitize_file(f):
            count += 1
            print(f"🧹 Sanitized: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Sanitized {count} files.")

if __name__ == '__main__':
    main()
