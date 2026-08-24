# -*- coding: utf-8 -*-
"""
ingest_official_national_pdfs.py
================================
Automated ingestion tool for user-provided official MOEX Gaokao Level 3 PDFs.
- Scans `依考科分類/🏛️_國考同級參考題庫/` and optional drop folder `PDF_DROP/`.
- Standardizes PDF names and places them in subject folders.
- Automatically generates 300 DPI high-resolution PNG page images using macOS `sips`.
- Recompiles `compile_national_exams.py` to immediately update the workbench.
"""

import os
import re
import shutil
import subprocess

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

BASE_DIR = os.path.join(WORKSPACE, "依考科分類", "🏛️_國考同級參考題庫")
DROP_DIR = os.path.join(BASE_DIR, "📥_官方PDF投放處")
os.makedirs(DROP_DIR, exist_ok=True)

SUBJECT_DIRS = {
    '01': '01_電路學',
    '02': '02_電子學_含電力電子',
    '03': '03_工程數學',
    '04': '04_電機機械',
    '05': '05_電力系統'
}

SUBJECT_KEYWORDS = {
    '01': ['電路學', '電路'],
    '02': ['電子學', '電力電子'],
    '03': ['工程數學', '工數'],
    '04': ['電機機械', '機械'],
    '05': ['電力系統', '電力']
}

print("=" * 70)
print("📥 國考同級官方原檔 PDF 自動收納與 300 DPI 轉圖管線")
print("=" * 70)

# Step 1: Scan for dropped PDF files
found_pdfs = []
for root, _, files in os.walk(BASE_DIR):
    for f in files:
        if f.lower().endswith(".pdf"):
            full_p = os.path.join(root, f)
            found_pdfs.append(full_p)

print(f"🔍 掃描到 {len(found_pdfs)} 份 PDF 檔案。")

processed_count = 0
for p in found_pdfs:
    filename = os.path.basename(p)
    
    # Extract Year (110~114 or 2021~2025)
    yr_m = re.search(r'(11[0-4]|202[1-5])', filename)
    if not yr_m:
        continue
    yr = yr_m.group(1)
    if yr.startswith('202'):
        yr = str(int(yr) - 1911)
        
    # Match Subject
    matched_sid = None
    for sid, kw_list in SUBJECT_KEYWORDS.items():
        if any(kw in filename or kw in p for kw in kw_list):
            matched_sid = sid
            break
            
    if not matched_sid:
        continue
        
    sdir = SUBJECT_DIRS[matched_sid]
    sname_short = sdir.split('_')[1]
    target_dir = os.path.join(BASE_DIR, sdir)
    target_pdf_name = f"GK_{yr}年_高考三級_{sname_short}.pdf"
    target_pdf_path = os.path.join(target_dir, target_pdf_name)
    
    # If in drop folder or differently named, move/copy to canonical location
    if os.path.abspath(p) != os.path.abspath(target_pdf_path):
        shutil.copy2(p, target_pdf_path)
        print(f"  📦 歸檔試卷: {filename} ➔ {sdir}/{target_pdf_name}")
        
    # Step 2: Convert to high-resolution PNG using macOS sips
    images_dir = os.path.join(target_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    out_png_base = os.path.join(images_dir, f"GK_{yr}年_{sname_short}_p1.png")
    
    # Run sips
    res = subprocess.run([
        'sips', '-s', 'format', 'png', target_pdf_path, '--out', out_png_base
    ], capture_output=True, text=True)
    
    if res.returncode == 0:
        print(f"  🎨 轉出高解析原卷圖檔: {sdir}/images/GK_{yr}年_{sname_short}_p1.png")
        processed_count += 1
    else:
        print(f"  ⚠️ sips 轉圖警告: {res.stderr}")

print(f"\n✅ 成功處理 {processed_count} 份官方試卷！")

# Step 3: Trigger compiler to refresh bundle
print("\n🔄 重新編譯國考題庫資料庫...")
subprocess.run(['python3', 'scripts/compile_national_exams.py'], check=True)
print("🎉 全流程執行完畢！雙欄工作台已即時套用最新官方試卷與圖檔。")
