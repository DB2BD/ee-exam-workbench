# -*- coding: utf-8 -*-
"""
fix_all_unclosed_dollars.py
===========================
Systematically scans and closes all unclosed $ delimiters across all markdown files.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_unclosed_dollars_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = []
    in_code_block = False
    in_display_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code block tracking
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
            
        if in_code_block:
            new_lines.append(line)
            continue

        # Clean weird prefix like $$> $$
        if stripped.startswith('$$> $$'):
            line = line.replace('$$> $$', '> $$')
            stripped = line.strip()

        # Display block tracking
        if stripped == '$$':
            in_display_block = not in_display_block
            new_lines.append(line)
            continue
            
        if in_display_block:
            new_lines.append(line)
            continue
            
        # If line is $$...$$, already balanced
        if stripped.startswith('$$') and stripped.endswith('$$'):
            new_lines.append(line)
            continue

        # Count unescaped single dollars
        temp = stripped.replace('$$', '')
        temp = re.sub(r'\\\$', '', temp)
        single_count = temp.count('$')
        
        if single_count % 2 != 0:
            # Odd number of dollars! Let's analyze where the dollar is missing.
            l = line.rstrip('\r\n')
            
            # Case 1: Missing opening dollar at start of bullet
            # e.g., "- \alpha < \omega_0$：**欠阻尼**"
            # e.g., "- H$：慣性常數"
            # e.g., "- P_m$：機械輸入功率"
            m_start = re.match(r'^(\s*[-*]\s+)([A-Za-z0-9_\\-]+.*?\$\s*[:：].*)$', l)
            if m_start:
                l = f"{m_start.group(1)}${m_start.group(2)}"
                temp2 = l.replace('$$', '').replace(r'\$', '')
                if temp2.count('$') % 2 == 0:
                    new_lines.append(l + '\n')
                    continue

            # Case 2: Missing closing dollar at end of line
            # e.g., "* **直流增益**： $\mathbf{A_{vo} = -2.5\text{ V/V}}"
            # e.g., "- 電阻阻抗：$\mathbf{Z}_R = R"
            # e.g., "- 氣隙功率：$P_{\text{ag}} = 3 I_2'^2 \frac{R_2'}{s} = \frac{P_{\text{rcl}}}{s}"
            # Check if line ends with math characters (not Chinese)
            if re.search(r'[\}\)0-9A-Za-z\^_\+\-\*/\\]$', l.strip()):
                l = l.rstrip() + '$'
                temp2 = l.replace('$$', '').replace(r'\$', '')
                if temp2.count('$') % 2 == 0:
                    new_lines.append(l + '\n')
                    continue

            # Case 3: Missing closing dollar before Chinese remarks or punctuation
            # e.g. "長度 $l = 300\,\text{km}：..." -> "$l = 300\,\text{km}$："
            # e.g. "其中 $\mathbf{V}_1 = 10\text{ V} 為輸入" -> "其中 $\mathbf{V}_1 = 10\text{ V}$ 為輸入"
            # Find the unclosed math segment starting with $
            parts = l.split('$')
            # The odd piece is missing a closing $
            # Usually last part is "l = 300\text{ km}，長度..."
            # Let's inspect parts
            reconstructed = []
            for idx, p in enumerate(parts):
                reconstructed.append(p)
                if idx % 2 == 1 and idx == len(parts) - 1:
                    # p contains math followed by Chinese or punctuation
                    m_split = re.search(r'([,\u4e00-\u9fff，。；（\(].*)', p)
                    if m_split:
                        math_part = p[:m_split.start()].rstrip()
                        text_part = p[m_split.start():]
                        reconstructed[-1] = f"{math_part}${text_part}"
                    else:
                        reconstructed[-1] = f"{p}$"
            l = '$'.join(reconstructed)
            new_lines.append(l + '\n')
            continue

        new_lines.append(line)

    result = "".join(new_lines)
    
    if result != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if fix_unclosed_dollars_in_file(f):
            count += 1
            print(f"💰 Closed unclosed $ in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully fixed {count} files with unclosed $!")

if __name__ == '__main__':
    main()
