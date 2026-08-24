# -*- coding: utf-8 -*-
"""
crawl_moex_exams.py
===================
Crawls authentic official PDF files from MOEX (考選部) for 110~114 Gaokao Level 3.
"""

import os
import re
import ssl
import urllib.request
import urllib.parse

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

BASE_URL = 'https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx'

def extract_form_state(html):
    data = {}
    for inp in re.findall(r'<input[^>]*>', html):
        name_m = re.search(r'name=\"([^\"]+)\"', inp)
        val_m = re.search(r'value=\"([^\"]*)\"', inp)
        if name_m:
            data[name_m.group(1)] = val_m.group(1) if val_m else ''
    return data

def post_form(data):
    post_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(BASE_URL, data=post_data, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode('utf-8')

req_init = urllib.request.Request(BASE_URL, headers=HEADERS)
with urllib.request.urlopen(req_init, context=ctx) as resp:
    init_html = resp.read().decode('utf-8')

EXAM_CODES = {
    '114': ('2025', '114080'),
    '113': ('2024', '113080'),
    '112': ('2023', '112090'),
    '111': ('2022', '111090'),
    '110': ('2021', '110090')
}

TARGET_SUBJECTS = {
    '01': '電路學',
    '02': '電子學',
    '03': '工程數學',
    '04': '電機機械',
    '05': '電力系統'
}

for yr, (year_val, exam_code) in EXAM_CODES.items():
    print(f"\n=======================================================")
    print(f"📡 Querying MOEX for {yr} 年 (Exam Code: {exam_code})...")
    print(f"=======================================================")
    
    # Step 1: Set Year
    form1 = extract_form_state(init_html)
    form1['ctl00$holderContent$wUctlExamYearStart$ddlExamYear'] = year_val
    form1['ctl00$holderContent$wUctlExamYearEnd$ddlExamYear'] = year_val
    form1['ctl00$holderContent$btnYear'] = '查詢'
    resp_year_html = post_form(form1)
    
    # Step 2: Set Exam Code & Search (Display Mode: 2 for 科目)
    form2 = extract_form_state(resp_year_html)
    form2['ctl00$holderContent$ddlExamCode'] = exam_code
    form2['ctl00$holderContent$ddlExamDisplayMode1'] = '2' # By Subject
    form2['ctl00$holderContent$btnSearch'] = '查詢'
    
    resp_search_html = post_form(form2)
    print(f"  Received Search Response: {len(resp_search_html)} bytes")
    
    # Search for table rows or links
    rows = re.findall(r'<tr[^>]*>([\s\S]*?)<\/tr>', resp_search_html)
    print(f"  Found {len(rows)} table rows in search result.")
    
    for row in rows:
        row_text = re.sub(r'<[^>]+>', ' ', row).strip()
        for sid, sname in TARGET_SUBJECTS.items():
            if sname in row_text:
                pdf_match = re.search(r'href=\"([^\"]*ExamFiles[^\"]*|wFrmExam[^\"]*|[^\"]*\.pdf[^\"]*)\"', row)
                if pdf_match:
                    link = pdf_match.group(1)
                    print(f"    🎯 MATCH {yr} 年 【{sname}】: {link}")
                else:
                    # Print row snippet
                    links_in_row = re.findall(r'href=\"([^\"]+)\"', row)
                    print(f"    🔎 Row for {sname}: {links_in_row}")
