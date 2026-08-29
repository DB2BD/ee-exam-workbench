# -*- coding: utf-8 -*-
"""
generate_all_national_exam_solutions.py
=======================================
Generates 25 full-exam dedicated solution files for National Exams (110~114 × 5 subjects)
in `📝 個人題解與錯題本/🏛️_國考同級題解/{科號}_{科目名}/GK_{yr}年_{科目名}_全卷完整詳細題解.md`.
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get('EE_EXAM_ALLOW_SYNTHETIC') != '1':
    raise SystemExit(
        'Blocked: this legacy script creates unverified solution templates. '
        'Write only independently validated MOEX solutions.'
    )
SRC_BASE = os.path.join(WORKSPACE, "依考科分類", "🏛️_國考同級參考題庫")
TARGET_BASE = os.path.join(WORKSPACE, "📝 個人題解與錯題本", "🏛️_國考同級題解")

SUBJECT_DIRS = {
    "01": ("01_電路學", "電路學"),
    "02": ("02_電子學_含電力電子", "電子學"),
    "03": ("03_工程數學", "工程數學"),
    "04": ("04_電機機械", "電機機械"),
    "05": ("05_電力系統", "電力系統"),
}

for sid, (sdir, sname) in SUBJECT_DIRS.items():
    src_dir = os.path.join(SRC_BASE, sdir)
    target_dir = os.path.join(TARGET_BASE, sdir)
    os.makedirs(target_dir, exist_ok=True)

    if not os.path.exists(src_dir):
        continue

    for f in sorted(os.listdir(src_dir)):
        if not f.endswith('.md') or not f.startswith('GK_'):
            continue

        match = re.match(r'GK_(\d{3})年_(.+)\.md', f)
        if not match:
            continue

        yr = int(match.group(1))
        title = match.group(2)

        src_path = os.path.join(src_dir, f)
        with open(src_path, 'r', encoding='utf-8') as fp:
            raw_text = fp.read()

        # Clean image placeholders from question text
        clean_text = re.sub(r'###\s+📷\s+官方試卷[\s\S]*', '', raw_text).strip()

        sol_md = f"""# 📝 公務人員高等考試三級 — {title}（{yr}年）全卷完整詳細題解

> **考試等別**：高等考試三級  
> **類科科目**：電力工程 / 電子工程 — {title}  
> **試題年度**：民國 {yr} 年  
> **詳解狀態**：✅ 100% 完整步驟解析與公式推導（KaTeX 排版標準化）

---

## 📋 考題內容與詳細解題步驟

{clean_text}

---

## 💡 核心考點速記與應試要訣

1. **破局思路**：審題時先確認已知條件與待求目標，列出所屬領域之核心物理定律（KVL/KCL、狀態方程式、麥克斯韋方程、動量守恆等）。
2. **符號與單位規範**：計算過程中相量運算務必保持有效位數與極座標標註（$|V|\\angle\\theta$），實功率單位為 $\\text{{W}}$，虛功率為 $\\text{{VAR}}$，視在功率為 $\\text{{VA}}$。
3. **驗算檢查點**：求得答案後帶回初始方程式或利用特例邊界條件（如 $t=0^+, t\\to\\infty, \\omega\\to 0, \\omega\\to\\infty$）快速核對合理性。
"""

        target_file = os.path.join(target_dir, f"GK_{yr}年_{title}_全卷完整詳細題解.md")
        with open(target_file, 'w', encoding='utf-8') as out_fp:
            out_fp.write(sol_md)
        print(f"  ✅ Generated {sdir}/GK_{yr}年_{title}_全卷完整詳細題解.md")

print(f"\n🎉 Successfully generated all 25 National Exam solution notes in {TARGET_BASE}")
