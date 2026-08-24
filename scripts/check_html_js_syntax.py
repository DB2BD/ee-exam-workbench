# -*- coding: utf-8 -*-
"""
check_html_js_syntax.py
=======================
Extracts all <script> blocks from index.html and checks for syntax errors with Node.js.
"""

import os
import re
import subprocess

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(WORKSPACE, 'index.html')

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script(?![^>]*src=)([^>]*)>([\s\S]*?)<\/script>', html, re.IGNORECASE)
print(f"Found {len(scripts)} inline script blocks in index.html.")

for idx, (attrs, code) in enumerate(scripts):
    temp_file = os.path.join(WORKSPACE, f'temp_script_{idx}.js')
    with open(temp_file, 'w', encoding='utf-8') as f_out:
        f_out.write(code)
    
    result = subprocess.run(['node', '--check', temp_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\n❌ Syntax Error in script block {idx}:")
        print(result.stderr)
    else:
        print(f"✅ Script block {idx} passed syntax check.")
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
