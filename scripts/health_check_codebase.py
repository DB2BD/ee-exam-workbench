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

from verify_moex_national_exams import audit_solutions

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def run_health_check():
    print("========================================================")
    print("EE Exam Workbench — Codebase Health & Anti-Entropy Audit")
    print("========================================================\n")
    
    score = 100
    deductions = []

    # 1. Database Integrity (30 pts)
    print("[Check 1/5] Evaluating Database Integrity (30 pts)...")
    try:
        with open('dashboard-data.js', 'r', encoding='utf-8') as f:
            t1 = f.read()
        m1 = re.search(r'questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:', t1)
        pe_len = len(json.loads(m1.group(1))) if m1 else 0

        with open('national-exams-data.js', 'r', encoding='utf-8') as f:
            t2 = f.read()
        m2 = re.search(r'questions:\s*(\[[\s\S]+?\])\s*\}\;', t2)
        gk_len = len(json.loads(m2.group(1))) if m2 else 0

        crop_manifest = json.load(open('data/moex-question-crops.json', encoding='utf-8'))
        expected_gk = crop_manifest['summary']['questions']
        if pe_len == 321 and gk_len == expected_gk:
            print(f"  PASS: {pe_len + gk_len} active questions verified (PE: {pe_len}, GK: {gk_len}).")
        else:
            diff = abs(pe_len - 321) + abs(gk_len - expected_gk)
            penalty = min(30, diff * 5)
            score -= penalty
            deductions.append(f"-{penalty} pts: Question count mismatch (PE: {pe_len}/321, GK: {gk_len}/{expected_gk})")
    except Exception as e:
        score -= 30
        deductions.append(f"-30 pts: Failed to parse databases ({e})")

    # 2. ADR & Context Alignment (20 pts)
    print("\n[Check 2/5] Evaluating ADR & CONTEXT.md Alignment (20 pts)...")
    adr_dir = os.path.join('docs', 'adr')
    has_context = os.path.exists('CONTEXT.md')
    adr_count = len([f for f in os.listdir(adr_dir) if f.endswith('.md')]) if os.path.exists(adr_dir) else 0

    if has_context and adr_count >= 4:
        print(f"  PASS: CONTEXT.md present, {adr_count} ADRs documented.")
    else:
        penalty = 10 if not has_context else 0
        if adr_count < 4:
            penalty += (4 - adr_count) * 2.5
        score -= penalty
        deductions.append(f"-{penalty} pts: Incomplete documentation / ADR records")

    # 3. Solution Golden Standard Compliance (20 pts)
    print("\n[Check 3/5] Evaluating Validated Solution Coverage (20 pts)...")
    with open('data/moex-national-exams.json', 'r', encoding='utf-8') as fp:
        source_manifest = json.load(fp)
    solution_audit = audit_solutions(source_manifest)
    gk_total = solution_audit['total_questions']
    gk_verified = solution_audit['validated_questions']
    gk_pending = len(solution_audit['pending_question_ids'])
    gk_invalid = len(solution_audit['invalid_solution_entries'])

    # PE solutions have a separate question-level audit manifest.  Do not let
    # the complete GK coverage hide unresolved PE derivations in the headline.
    with open('data/pe-solution-audit.json', encoding='utf-8') as fp:
        pe_manifest = json.load(fp)
    pe_summary = pe_manifest.get('summary', {})
    pe_total = int(pe_summary.get('questions', len(pe_manifest.get('entries', []))))
    pe_verified = int(pe_summary.get('verified', 0))
    pe_manual = int(pe_summary.get('needs_manual_review', 0))
    pe_suspected = int(pe_summary.get('suspected_error', 0))
    unresolved = gk_pending + gk_invalid + pe_manual + pe_suspected

    if unresolved == 0:
        print(f"  PASS: GK {gk_verified}/{gk_total}; PE {pe_verified}/{pe_total} questions validated.")
    else:
        penalty = 20
        score -= penalty
        print(
            f"  PARTIAL: GK {gk_verified}/{gk_total}; PE {pe_verified}/{pe_total} verified, "
            f"{pe_manual} manual-review, {pe_suspected} suspected-error."
        )
        deductions.append(
            f"-{penalty} pts: solution coverage incomplete; GK pending={gk_pending}, invalid={gk_invalid}; "
            f"PE manual-review={pe_manual}, suspected-error={pe_suspected}"
        )

    # 4. Stray Files & Image Mappings (15 pts)
    print("\n[Check 4/5] Checking Official Image Mappings (15 pts)...")
    with open('national-solutions-bundle.js', 'r', encoding='utf-8') as f:
        nb = f.read()
    m_img = re.search(r'const NATIONAL_IMAGE_MAP\s*=\s*(\{[\s\S]+?\});', nb)
    gk_imgs = json.loads(m_img.group(1)) if m_img else {}
    expected_images = crop_manifest['summary']['figure_crops']
    if len(gk_imgs) >= expected_images:
        print(f"  PASS: {len(gk_imgs)} national image mappings active; {expected_images} official figure crops covered.")
    else:
        score -= 5
        deductions.append(f"-5 pts: Image mapping count lower than official figure crop count ({len(gk_imgs)}/{expected_images})")

    # 5. Automated Test Suite (15 pts)
    print("\n[Check 5/5] Running Automated Test Suite (15 pts)...")
    res = subprocess.run([sys.executable, 'scripts/run_all_tests.py'], capture_output=True, text=True)
    if res.returncode == 0:
        print("  PASS: All unit and integration test suites pass with zero failures.")
    else:
        score -= 15
        deductions.append("-15 pts: Automated test suite failed!")

    print("\n========================================================")
    print(f"ARCHITECTURE HEALTH SCORE: {max(0, score)} / 100")
    if deductions:
        print("Deductions:")
        for d in deductions:
            print(f"   {d}")
    else:
        print("STATUS: all configured checks passed.")
    print("========================================================")

if __name__ == '__main__':
    run_health_check()
