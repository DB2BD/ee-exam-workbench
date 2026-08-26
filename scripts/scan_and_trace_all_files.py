# -*- coding: utf-8 -*-
"""
scan_and_trace_all_files.py
===========================
Finds all lines with odd single dollars or stray double dollars across ALL markdown files.
Ignores code blocks, inline backticks, and blockquote math markers.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    issues = []
    in_code = False
    in_display = False

    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        # Strip inline code spans
        s_no_inline_code = re.sub(r'`[^`\n]+`', '', s)

        if s_no_inline_code == '$$' or s_no_inline_code == '> $$' or s_no_inline_code == '>$':
            in_display = not in_display
            continue

        if in_display:
            continue

        if s_no_inline_code.startswith('$$') and s_no_inline_code.endswith('$$') and len(s_no_inline_code) > 4:
            continue

        # Look for stray $$ on a non-display line
        if '$$' in s_no_inline_code:
            issues.append((i, f"Stray $$ in line", s))
            continue

        # Check single dollar balance on line
        no_esc = s_no_inline_code.replace(r'\$', '')
        d_count = no_esc.count('$')
        if d_count % 2 != 0:
            issues.append((i, f"Odd single $ count ({d_count})", s))

    return issues

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    total_issues = 0
    
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        issues = audit_file(f)
        if issues:
            rel = os.path.relpath(f, WORKSPACE)
            print(f"\n📂 {rel} ({len(issues)} issues):")
            for line_no, issue_type, snippet in issues:
                total_issues += 1
                print(f"  Line {line_no:4d} [{issue_type}]: {snippet[:100]}")

    print(f"\n==========================================")
    print(f"Total line-level delimiter issues: {total_issues}")
    print(f"==========================================")

if __name__ == '__main__':
    main()
