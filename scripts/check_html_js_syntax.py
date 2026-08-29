# -*- coding: utf-8 -*-
"""
check_html_js_syntax.py
=======================
Extracts all <script> blocks from index.html and checks for syntax errors with Node.js.
"""

import os
import re
import subprocess
import tempfile

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(WORKSPACE, 'index.html')

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script(?![^>]*src=)([^>]*)>([\s\S]*?)<\/script>', html, re.IGNORECASE)
print(f"Found {len(scripts)} inline script blocks in index.html.")

has_errors = False
with tempfile.TemporaryDirectory(prefix='ee-workbench-syntax-') as temp_dir:
    for idx, (attrs, code) in enumerate(scripts):
        temp_file = os.path.join(temp_dir, f'temp_script_{idx}.js')
        with open(temp_file, 'w', encoding='utf-8') as f_out:
            f_out.write(code)

        result = subprocess.run(['node', '--check', temp_file], capture_output=True, text=True)
        if result.returncode != 0:
            has_errors = True
            print(f"\n❌ Syntax Error in script block {idx}:")
            print(result.stderr)
        else:
            print(f"✅ Script block {idx} passed syntax check.")

if has_errors:
    raise SystemExit(1)
