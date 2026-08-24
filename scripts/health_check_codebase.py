# -*- coding: utf-8 -*-
"""
health_check_codebase.py
========================
Periodic Codebase Health Check & Anti-Entropy Analyzer.
Calculates Architecture Health Score (0~100) based on:
1. Core Database Integrity (30 pts)
2. ADR & Specification Alignment (20 pts)
3. Solution Golden Standard Compliance (20 pts)
4. Dead / Stray Files & Asset Linking (15 pts)
5. Automated Test Suite Status (15 pts)
"""

import os
import json
import re
import subprocess
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def run_health_check():
    print("🏥 ========================================================")
    print("🏥 EE Exam Workbench — Codebase Health & Anti-Entropy Audit")
    print("🏥 ========================================================\n")
    
    score = 100
    deductions = []

    # 1. Database Integrity (30 pts)
    print("📊 [Check 1/5] Evaluating Database Integrity (30 pts)...")
    try:
        with open('dashboard-data.js', 'r', encoding='utf-8') as f:
            t1 = f.read()
        m1 = re.search(r'questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:', t1)
        pe_len = len(json.loads(m1.group(1))) if m1 else 0

        with open('national-exams-data.js', 'r', encoding='utf-8') as f:
            t2 = f.read()
        m2 = re.search(r'questions:\s*(\[[\s\S]+?\])\s*\}\;', t2)
        gk_len = len(json.loads(m2.group(1))) if m2 else 0

        if pe_len == 318 and gk_len == 105:
            print(f"  ✅ Perfect: 423 total questions verified (PE: {pe_len}, GK: {gk_len}).")
        else:
            diff = abs(pe_len - 318) + abs(gk_len - 105)
            penalty = min(30, diff * 5)
            score -= penalty
            deductions.append(f"-{penalty} pts: Question count mismatch (PE: {pe_len}/318, GK: {gk_len}/105)")
    except Exception as e:
        score -= 30
        deductions.append(f"-30 pts: Failed to parse databases ({e})")

    # 2. ADR & Context Alignment (20 pts)
    print("\n📜 [Check 2/5] Evaluating ADR & CONTEXT.md Alignment (20 pts)...")
    adr_dir = os.path.join('docs', 'adr')
    has_context = os.path.exists('CONTEXT.md')
    adr_count = len([f for f in os.listdir(adr_dir) if f.endswith('.md')]) if os.path.exists(adr_dir) else 0

    if has_context and adr_count >= 4:
        print(f"  ✅ Perfect: CONTEXT.md present, {adr_count} ADRs documented.")
    else:
        penalty = 10 if not has_context else 0
        if adr_count < 4:
            penalty += (4 - adr_count) * 2.5
        score -= penalty
        deductions.append(f"-{penalty} pts: Incomplete documentation / ADR records")

    # 3. Solution Golden Standard Compliance (20 pts)
    print("\n💎 [Check 3/5] Evaluating Solution Golden Standard Compliance (20 pts)...")
    sol_base = os.path.join('📝 個人題解與錯題本', '🏛️_國考同級題解')
    missing_blocks = 0
    total_sol_files = 0
    if os.path.exists(sol_base):
        for root, dirs, files in os.walk(sol_base):
            for f in files:
                if f.endswith('_全卷完整詳細題解.md'):
                    total_sol_files += 1
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                        content = fp.read()
                    if '📌 題目與已知條件' not in content or '💡 核心考點與破題關鍵' not in content or '🎯 滿分結論與作答要點' not in content:
                        missing_blocks += 1
    if total_sol_files >= 25 and missing_blocks == 0:
        print(f"  ✅ Perfect: All {total_sol_files} solution files comply 100% with Golden Standard.")
    else:
        penalty = min(20, missing_blocks * 2)
        score -= penalty
        deductions.append(f"-{penalty} pts: {missing_blocks} solution files missing golden standard blocks")

    # 4. Stray Files & Image Mappings (15 pts)
    print("\n🔍 [Check 4/5] Checking for Broken Image Mappings (15 pts)...")
    with open('national-solutions-bundle.js', 'r', encoding='utf-8') as f:
        nb = f.read()
    m_img = re.search(r'const NATIONAL_IMAGE_MAP\s*=\s*(\{[\s\S]+?\});', nb)
    gk_imgs = json.loads(m_img.group(1)) if m_img else {}
    if len(gk_imgs) >= 140:
        print(f"  ✅ Perfect: {len(gk_imgs)} verified national exam image mappings active.")
    else:
        score -= 5
        deductions.append(f"-5 pts: Image mapping count lower than expected ({len(gk_imgs)} mappings)")

    # 5. Automated Test Suite (15 pts)
    print("\n🧪 [Check 5/5] Running Automated Test Suite (15 pts)...")
    res = subprocess.run([sys.executable, 'scripts/run_all_tests.py'], capture_output=True, text=True)
    if res.returncode == 0:
        print("  ✅ Perfect: All unit and integration test suites pass with zero failures.")
    else:
        score -= 15
        deductions.append("-15 pts: Automated test suite failed!")

    print("\n🏥 ========================================================")
    print(f"🏥 ARCHITECTURE HEALTH SCORE: {max(0, score)} / 100")
    if deductions:
        print("🏥 Deductions:")
        for d in deductions:
            print(f"   ⚠️ {d}")
    else:
        print("🏥 STATUS: PRISTINE — ZERO ARCHITECTURAL DEBT DETECTED.")
    print("🏥 ========================================================")

if __name__ == '__main__':
    run_health_check()
