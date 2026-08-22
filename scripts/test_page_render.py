#!/usr/bin/env python3
import os

def test_syntax():
    with open('/Users/a/技師考試/歷屆試題_104-114年/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check key element IDs
    required_ids = [
        'question-grid', 'modal-overlay', 'modal-content', 'modal-split-container',
        'modal-pane-left', 'modal-pane-right', 'mobile-bottom-bar',
        'btn-mobile-tab-exam', 'btn-mobile-tab-solution'
    ]
    
    for rid in required_ids:
        if f'id="{rid}"' in html:
            print(f"✅ Found ID: {rid}")
        else:
            print(f"❌ Missing ID: {rid}")
            
    # Check JS balance of braces
    import re
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for idx, s in enumerate(scripts):
        open_braces = s.count('{')
        close_braces = s.count('}')
        print(f"Script {idx}: {{ = {open_braces}, }} = {close_braces}, diff = {open_braces - close_braces}")
        if open_braces == close_braces:
            print(f"✅ Script {idx} braces perfectly balanced!")
        else:
            print(f"❌ Script {idx} brace mismatch!")

if __name__ == '__main__':
    test_syntax()
