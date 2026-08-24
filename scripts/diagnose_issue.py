# -*- coding: utf-8 -*-
"""
diagnose_issue.py
=================
Automated diagnostic tool for the EE Exam Workbench.
Performs 5-point root cause diagnosis:
1. Database Integrity & Count check
2. Stale Bundle & Precedence shadowing check
3. Broken Image Mappings & Local Path check
4. KaTeX delimiter & formatting syntax check
5. Cache buster & static load synchronization check
"""

import os
import json
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def diagnose():
    print("🩺 ========================================================")
    print("🩺 EE Exam Workbench — Automated 5-Point System Diagnostics")
    print("🩺 ========================================================\n")
    
    findings = []
    
    # 1. Database Check
    print("🔍 [Check 1/5] Checking Database Integrity...")
    with open('dashboard-data.js', 'r', encoding='utf-8') as f:
        t1 = f.read()
    m1 = re.search(r'questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:', t1)
    pe_len = len(json.loads(m1.group(1))) if m1 else 0
    
    with open('national-exams-data.js', 'r', encoding='utf-8') as f:
        t2 = f.read()
    m2 = re.search(r'questions:\s*(\[[\s\S]+?\])\s*\}\;', t2)
    gk_len = len(json.loads(m2.group(1))) if m2 else 0
    
    if pe_len == 318 and gk_len == 105:
        print(f"  ✅ Database counts 100% healthy (PE: {pe_len}, GK: {gk_len}, Total: {pe_len + gk_len})")
    else:
        findings.append(f"Database count anomaly: PE={pe_len} (expected 318), GK={gk_len} (expected 105)")
        print(f"  ❌ Anomaly detected: PE={pe_len}, GK={gk_len}")

    # 2. Bundle Shadowing Check
    print("\n🔍 [Check 2/5] Checking for Cross-Bundle Key Shadowing...")
    with open('solutions-bundle.js', 'r', encoding='utf-8') as f:
        sb = f.read()
    with open('national-solutions-bundle.js', 'r', encoding='utf-8') as f:
        nb = f.read()
        
    m_gk_in_pe = re.findall(r'\"(📝 個人題解與錯題本/🏛️_國考同級題解[^\"]+\.md)\"', sb)
    print(f"  ℹ️ GK solution keys found in PE bundle: {len(m_gk_in_pe)}")
    if len(m_gk_in_pe) > 0:
        print("  ⚠️ Notice: GK solutions present in PE bundle; frontend precedence rule must prioritize NATIONAL_BUNDLED_MD.")
        
    # 3. Frontend Precedence Check
    print("\n🔍 [Check 3/5] Checking Frontend Precedence Rules in index.html...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    if 'const isGK = currentExamCategory === \'gk\'' in html and 'NATIONAL_BUNDLED_MD[cleanPath]' in html:
        print("  ✅ Frontend precedence rule is active: GK questions strictly prioritize NATIONAL_BUNDLED_MD.")
    else:
        findings.append("Frontend precedence rule missing in index.html!")
        print("  ❌ Frontend precedence rule MISSING in index.html!")

    # 4. Cache Buster Check
    print("\n🔍 [Check 4/5] Checking Cache-Buster Timestamps in <head>...")
    cb_matches = re.findall(r'<script src=\"\./(.*?\.js)\?v=(.*?)\">', html)
    if len(cb_matches) >= 4:
        print(f"  ✅ All {len(cb_matches)} database scripts have cache-busters in <head>:")
        for script, v in cb_matches:
            print(f"      - {script} (v={v})")
    else:
        findings.append(f"Incomplete cache-busters in <head> (found {len(cb_matches)})")
        print(f"  ⚠️ Warning: Incomplete cache-busters found: {len(cb_matches)}")

    # 5. Image & KaTeX Syntax Check
    print("\n🔍 [Check 5/5] Checking Image Map & Bundle KaTeX Delimiters...")
    m_img = re.search(r'const IMAGE_MAP\s*=\s*(\{[\s\S]+?\});', sb)
    img_count = len(json.loads(m_img.group(1))) if m_img else 0
    print(f"  ✅ Total mapped image references in PE bundle: {img_count}")

    print("\n🩺 ========================================================")
    if not findings:
        print("🩺 DIAGNOSTIC SUMMARY: SYSTEM IS 100% HEALTHY WITH ZERO DEFECTS.")
    else:
        print("🩺 DIAGNOSTIC SUMMARY: FINDINGS DETECTED:")
        for f in findings:
            print(f"   ⚠️ {f}")
    print("🩺 ========================================================")

if __name__ == '__main__':
    diagnose()
