# -*- coding: utf-8 -*-
"""
find_and_fix_unpaired_display_dollars.py
========================================
Pinpoints and fixes the exact line in each file that has an unpaired $$ marker.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit_file_display_dollars(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    in_code = False
    in_display = False
    display_start_line = None

    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        # Check line for $$
        # If line is self-contained $$...$$
        if s.startswith('$$') and s.endswith('$$') and len(s) > 4 and s.count('$$') % 2 == 0:
            continue

        # Count standalone $$ or unclosed $$ on line
        dd_count = s.count('$$')
        for _ in range(dd_count):
            if not in_display:
                in_display = True
                display_start_line = i
            else:
                in_display = False
                display_start_line = None

    if in_display:
        return display_start_line
    return None

def fix_unpaired_file(file_path, start_line):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    orig = "".join(lines)
    
    # Inspect the line around start_line
    idx = start_line - 1
    line = lines[idx]
    
    # Common causes of unpaired $$:
    # 1. Line is "- $$formula" or "1. $$formula" without closing $$
    # 2. Line is "$$formula" at end of section without closing $$
    # 3. Line is "text $$ text" without closing $$
    # 4. Stray "$$" on its own line before a header
    s = line.strip()
    
    if s == '$$':
        # If next non-empty line is a header or divider, this $$ is a stray opening
        # Check ahead
        next_lines = [l.strip() for l in lines[idx+1:idx+6] if l.strip()]
        if next_lines and (next_lines[0].startswith('#') or next_lines[0].startswith('---') or next_lines[0].startswith('![')):
            lines[idx] = '' # Remove stray $$
    elif s.startswith('$$') and not s.endswith('$$'):
        # Check if line should end with $$
        lines[idx] = line.rstrip() + '$$\n'
    elif s.startswith('- $$') or s.startswith('* $$') or re.match(r'^\d+\.\s+\$\$', s):
        # Bullet item with $$ at start
        if not s.endswith('$$'):
            # Convert to inline $...$
            lines[idx] = re.sub(r'^\s*([-*]|\d+\.)\s+\$\$([^\$\n]+)$', r'\1 $\2$\n', line)
    else:
        # Check if line has an odd $$ in middle
        parts = line.split('$$')
        if len(parts) == 2:
            # Single $$ in line
            # If it's at start of formula: e.g. "text $$formula" -> "text $$formula$$"
            lines[idx] = line.rstrip() + '$$\n'

    content = "".join(lines)
    if content != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    
    # Iterate up to 10 passes to fix multiple unpaired markers in the same file if any
    for pass_num in range(1, 6):
        fixed_in_pass = 0
        for f in files:
            if '.git' in f or 'node_modules' in f:
                continue
            unpaired_line = audit_file_display_dollars(f)
            if unpaired_line:
                rel = os.path.relpath(f, WORKSPACE)
                if fix_unpaired_file(f, unpaired_line):
                    fixed_in_pass += 1
                    print(f"Pass {pass_num} - Fixed unpaired $$ in: {rel} (line {unpaired_line})")
        if fixed_in_pass == 0:
            break
            
    print("\n🔍 Final Verification of all $$ counts across all files:")
    still_odd = []
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        unpaired = audit_file_display_dollars(f)
        if unpaired:
            still_odd.append((os.path.relpath(f, WORKSPACE), unpaired))
            
    print(f"Files still with unpaired $$: {len(still_odd)}")
    for f, l in still_odd:
        print(f"  ❌ {f} at line {l}")

if __name__ == '__main__':
    main()
