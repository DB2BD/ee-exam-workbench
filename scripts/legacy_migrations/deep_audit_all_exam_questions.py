# -*- coding: utf-8 -*-
import os
import re

print("=== Deep Audit of All Solution Files vs Original Exam Content ===")

subjects = [
    '01_電路學',
    '04_電機機械',
    '05_電力系統',
    '06_工業配電'
]

report = []

for s in subjects:
    sol_dir = f"📝 個人題解與錯題本/{s}"
    exam_file = f"依考科分類/{s}.md"
    
    if not os.path.exists(sol_dir) or not os.path.exists(exam_file):
        continue
        
    with open(exam_file, 'r', encoding='utf-8') as f:
        exam_raw = f.read()
        
    for yr in range(104, 115):
        sol_file = f"{sol_dir}/{yr}年_{s.split('_')[1]}_全卷完整詳細題解.md"
        if not os.path.exists(sol_file):
            print(f"❌ Missing solution file: {sol_file}")
            continue
            
        with open(sol_file, 'r', encoding='utf-8') as sf:
            sol_content = sf.read()
            
        # Find the year section in exam_file
        y_match = re.search(rf'##\s+{yr}\s*年[^\n]*\n([\s\S]*?)(?=\n##\s+\d+\s*年|\Z)', exam_raw)
        if not y_match:
            print(f"❌ Year {yr} missing in {exam_file}")
            continue
            
        y_text = y_match.group(1)
        
        # Check questions in solution file
        sol_headings = re.findall(r'##\s+([一二三四五六七八九十]+)[、\.]\s*([^\n]+)', sol_content)
        
        # Check if sol_content has placeholder or wrong numbers
        # Let's check for each question
        for qnum_char, qtitle in sol_headings:
            # check if title keywords appear in y_text
            # extract key words from title
            clean_title = re.sub(r'[（\(][^）\)]+[）\)]', '', qtitle)
            words = [w for w in re.findall(r'[\u4e00-\u9fa5]{2,4}', clean_title) if w not in ['計算', '分析', '求取', '特性', '設計', '求解', '完整', '詳細']]
            
            matches = [w for w in words if w in y_text]
            if len(words) > 0 and len(matches) == 0:
                print(f"⚠️ [{s} {yr}年 {qnum_char}] Title '{qtitle}' may not match exam text!")
                print(f"   Words checked: {words}")

print("=== Deep Audit Complete ===")
