# -*- coding: utf-8 -*-
"""
audit_all_phase_and_display.py
==============================
Deep Audit Script for Phase Angles, Phasors, Symmetrical Components,
Power Flow Angles, and Math Display Errors across 104-114 EE Exam Solutions.
"""

import os
import re
import glob
import json
import math
import cmath

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOLUTIONS_DIR = os.path.join(WORKSPACE, '📝 個人題解與錯題本')

def audit_file(filepath):
    rel_path = os.path.relpath(filepath, WORKSPACE)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    issues = []
    
    # 1. Check for KaTeX display issues
    # Check for unescaped angle issues or malformed angle syntax
    # e.g., \angle without proper spacing or numbers
    malformed_angles = re.findall(r'\\angle(?![0-9\s\-+\{A-Za-z\(\\])', content)
    if malformed_angles:
        issues.append(f"Malformed \\angle usage: {malformed_angles}")

    # Check for double backslash issues in markdown math (e.g., \\\\angle instead of \\angle)
    double_slash_angle = re.findall(r'\\\\angle', content)
    if double_slash_angle:
        issues.append(f"Double slash in angle: {len(double_slash_angle)} occurrences")

    # Check for unsupported KaTeX macros
    for bad_macro in [r'\phase', r'\phasor', r'\boldmath']:
        if bad_macro in content:
            issues.append(f"Unsupported KaTeX macro used: {bad_macro}")

    # 2. Check for Symmetrical Component Phase Angles:
    # a = 1∠120°, a^2 = 1∠240° = 1∠-120°
    # Look for instances where a or a^2 are defined or used with wrong angles
    if '1\\angle' in content or '1.0\\angle' in content or '1\\angle 120' in content:
        # Check if a^2 is mistakenly written as 1∠120° or a as 1∠240°
        wrong_a2 = re.findall(r'a\^2\s*=\s*1\s*\\angle\s*120', content)
        if wrong_a2:
            issues.append(f"Wrong a^2 definition: a^2 = 1∠120°: {wrong_a2}")
        wrong_a = re.findall(r'(?<!\^)a\s*=\s*1\s*\\angle\s*240', content)
        if wrong_a:
            issues.append(f"Wrong a definition: a = 1∠240°: {wrong_a}")

    # 3. Check for Polar to Rectangular arithmetic errors in solutions
    # Search for patterns like r\angle \theta^\circ = x + jy
    polar_rect_patterns = re.findall(r'([0-9\.]+)\s*\\angle\s*([+\-]?[0-9\.]+)\^\\circ.*?=\s*([+\-]?[0-9\.]+)\s*([+\-])\s*j([0-9\.]+)', content)
    for r_str, deg_str, real_str, sign_str, imag_str in polar_rect_patterns:
        try:
            r = float(r_str)
            deg = float(deg_str)
            claimed_real = float(real_str)
            claimed_imag = float(imag_str) if sign_str == '+' else -float(imag_str)
            
            actual = cmath.rect(r, math.radians(deg))
            
            # Check deviation
            if abs(actual.real - claimed_real) > 0.05 or abs(actual.imag - claimed_imag) > 0.05:
                # Potential precision or phase error
                issues.append(f"Polar->Rect mismatch: {r}∠{deg}° -> claimed {claimed_real}{sign_str}j{imag_str}, actual {actual.real:.3f} + j{actual.imag:.3f}")
        except Exception as e:
            pass

    # 4. Check for Power Factor Angle & Complex Power sign
    # S = P + jQ = V * I*
    # If lagging PF, I has negative angle relative to V, so I* has positive angle -> Q > 0 (+jQ)
    # If leading PF, I has positive angle relative to V, so I* has negative angle -> Q < 0 (-jQ)
    # Check for phrases like "0.8 滯後" with -j or "0.8 領先" with +j
    lagging_minus_j = re.findall(r'0\.[0-9]+\s*滯後.*?=\s*[0-9\.]+\s*-\s*j[0-9\.]+\s*(?:pu|MVA|kVA|VA)', content)
    # Note: impedance of inductive load has +j, but current has -j. We will check context.

    return issues

def main():
    all_files = sorted(glob.glob(os.path.join(SOLUTIONS_DIR, '**', '*.md'), recursive=True))
    print(f"Auditing {len(all_files)} solution files across all subjects & years...")
    
    total_issues = 0
    results = {}
    
    for f in all_files:
        issues = audit_file(f)
        if issues:
            results[os.path.relpath(f, WORKSPACE)] = issues
            total_issues += len(issues)
            
    print(f"\nAudit complete. Found {total_issues} potential issues in {len(results)} files.\n")
    for f, iss in results.items():
        print(f"📄 {f}:")
        for i in iss:
            print(f"   ⚠️ {i}")
        print()

if __name__ == '__main__':
    main()
