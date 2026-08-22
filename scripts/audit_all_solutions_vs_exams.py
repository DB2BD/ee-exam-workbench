# -*- coding: utf-8 -*-
import os
import re

subjects = [
    ('01_電路學', '電路學'),
    ('04_電機機械', '電機機械'),
    ('05_電力系統', '電力系統'),
    ('06_工業配電', '工業配電')
]

print("=== Starting Full Audit of All Solution Files vs Exam Questions ===")

mismatches = []

for sdir, sname in subjects:
    exam_md_path = f"依考科分類/{sdir}.md"
    if not os.path.exists(exam_md_path):
        continue
    with open(exam_md_path, 'r', encoding='utf-8') as f:
        exam_text = f.read()
    
    # Split exam text by year
    year_sections = re.split(r'\n##\s+(\d+)\s*年', exam_text)
    exam_years = {}
    if len(year_sections) > 1:
        for i in range(1, len(year_sections), 2):
            yr = int(year_sections[i])
            exam_years[yr] = year_sections[i+1]
            
    sol_dir = f"📝 個人題解與錯題本/{sdir}"
    if not os.path.exists(sol_dir):
        continue
        
    for f in sorted(os.listdir(sol_dir)):
        if f.endswith('.md') and '全卷完整詳細' in f:
            yr_match = re.search(r'(\d+)年', f)
            if not yr_match:
                continue
            yr = int(yr_match.group(1))
            sol_path = os.path.join(sol_dir, f)
            with open(sol_path, 'r', encoding='utf-8') as sf:
                sol_text = sf.read()
                
            if yr not in exam_years:
                print(f"⚠️ Year {yr} not found in exam md for {sdir}")
                continue
                
            exam_sec = exam_years[yr]
            
            # Extract numbers / keywords from both to check for mismatch
            # Check question count
            exam_q_matches = re.findall(r'####\s+([一二三四五六七八九十]+)[、\.]', exam_sec)
            sol_q_matches = re.findall(r'##\s+([一二三四五六七八九十]+)[、\.]', sol_text)
            
            print(f"[{sdir}] {yr}年: Exam has {len(exam_q_matches)} Qs, Solution has {len(sol_q_matches)} Qs")
            
            # Check snippet of Q1
            q1_exam = exam_sec.split('#### 一、')[1].split('#### 二、')[0] if '#### 一、' in exam_sec and '#### 二、' in exam_sec else ""
            q1_sol = sol_text.split('## 一、')[1].split('## 二、')[0] if '## 一、' in sol_text and '## 二、' in sol_text else ""
            
            # Extract numbers of 3+ digits or distinct words
            exam_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', q1_exam[:300]))
            sol_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', q1_sol[:400]))
            
            common_nums = exam_nums.intersection(sol_nums)
            if len(exam_nums) > 2 and len(common_nums) == 0:
                print(f"  ❌ Potential Q1 Mismatch in {sdir} {yr}年!")
                print(f"     Exam Q1: {q1_exam.strip()[:100]}...")
                print(f"     Sol Q1 : {q1_sol.strip()[:100]}...")
                mismatches.append((sdir, yr, 'Q1 mismatch'))

print(f"\nTotal potential mismatches flagged: {len(mismatches)}")
