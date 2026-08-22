# -*- coding: utf-8 -*-
import os
import re
import shutil

print("🚀 Starting full synchronization and KaTeX formula repair...")

# 1. Sync full 104-114 year files between 依考科分類/{s}.md and 依考科分類/{s}/{s}_歷屆試題彙編_104-114年.md
subjects = [
    ('01_電路學', '01_電路學_歷屆試題彙編_104-114年.md'),
    ('02_電子學_含電力電子', '02_電子學_含電力電子_歷屆試題彙編_104-114年.md'),
    ('03_工程數學', '03_工程數學_歷屆試題彙編_104-114年.md'),
    ('04_電機機械', '04_電機機械_歷屆試題彙編_104-114年.md'),
    ('05_電力系統', '05_電力系統_歷屆試題彙編_104-114年.md'),
    ('06_工業配電', '06_工業配電_歷屆試題彙編_104-114年.md'),
]

for sname, ssubfile in subjects:
    p_sub = os.path.join('依考科分類', sname, ssubfile)
    p_root = os.path.join('依考科分類', f'{sname}.md')
    
    # Read both and pick the more complete one (longer)
    c_sub = ""
    c_root = ""
    if os.path.exists(p_sub):
        with open(p_sub, 'r', encoding='utf-8') as f:
            c_sub = f.read()
    if os.path.exists(p_root):
        with open(p_root, 'r', encoding='utf-8') as f:
            c_root = f.read()
            
    best_content = c_sub if len(c_sub) >= len(c_root) else c_root
    
    # Write back to both
    with open(p_sub, 'w', encoding='utf-8') as f:
        f.write(best_content)
    with open(p_root, 'w', encoding='utf-8') as f:
        f.write(best_content)
    print(f"✅ Synchronized {sname}: {len(best_content.splitlines())} lines written to both locations.")

# 2. Repair currency $ signs across all markdown files so they don't break KaTeX inline math
all_mds = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.system_generated' in root or 'node_modules' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            all_mds.append(os.path.join(root, f))

repaired_currency_count = 0
for fpath in all_mds:
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    orig = text
    
    # Fix currency patterns
    text = re.sub(r'NT\$\s*', r'NT\$ ', text)
    text = re.sub(r'(?<!\\)\$/h\b', r'\\$/h', text)
    text = re.sub(r'(?<!\\)\$/hr\b', r'\\$/hr', text)
    text = re.sub(r'(?<!\\)\$/MWh\b', r'\\$/MWh', text)
    text = re.sub(r'(?<!\\)\$/MW2h\b', r'\\$/MW2h', text)
    text = re.sub(r'(?<!\\)\$/kvar\b', r'\\$/kvar', text)
    text = re.sub(r'(?<!\\)\$/kWh\b', r'\\$/kWh', text)
    
    # Fix odd dollar patterns like "增量成本為 $8/MWh" -> "增量成本為 8 \$/MWh" or "$8\text{/MWh}$"
    text = re.sub(r'(?<!\\)\$(\d+(?:\.\d+)?)/MWh', r'$\1\\text{ \\$/MWh}$', text)
    
    if text != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
        repaired_currency_count += 1
        print(f"🔧 Repaired currency formatting in: {fpath}")

print(f"Total files with currency formatting fixed: {repaired_currency_count}")

# 3. Update yearly README.md files (104 ~ 114 年) to link to full-exam detailed solutions
for yr in range(104, 115):
    readme_path = f"依年度分類/{yr}年/README.md"
    if not os.path.exists(readme_path):
        continue
    
    content = f"""# 📅 {yr} 年 專門職業及技術人員高等考試：電機工程技師 全真模擬試卷

> **考試年度**：民國 {yr} 年  
> **考試等級**：專技高考 — 電機工程技師  
> **考科總數**：6 科（每科考試時間 2 小時，滿分 100 分，總分 600 分，平均 60 分及格）

---

## 📑 本年度 6 大考科全真試題與滿分詳細題解索引

| 節次 | 科目名稱 | 試題代號 | 考試時間 | 計算器規範 | 💡 滿分詳細題解 (Markdown) | 📄 官方試卷 PDF |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **第 1 節** | **電路學** | `01130` | 120 分鐘 | 可以使用電子計算器 | [[../../📝 個人題解與錯題本/01_電路學/{yr}年_電路學_全卷完整詳細題解|💡 {yr}年 電路學全卷詳解]] | [📄 下載 PDF](./{yr}年_電機工程技師_電路學.pdf) |
| **第 2 節** | **電子學（包括電力電子學）** | `01120` | 120 分鐘 | 可以使用電子計算器 | [📖 線上試題](../../依考科分類/02_電子學_含電力電子.md#{yr}年) | [📄 下載 PDF](./{yr}年_電機工程技師_電子學（包括電力電子學）.pdf) |
| **第 3 節** | **工程數學** | `01140` | 120 分鐘 | 可以使用電子計算器 | [📖 線上試題](../../依考科分類/03_工程數學.md#{yr}年) | [📄 下載 PDF](./{yr}年_電機工程技師_工程數學.pdf) |
| **第 4 節** | **電機機械** | `01160` | 120 分鐘 | 可以使用電子計算器 | [[../../📝 個人題解與錯題本/04_電機機械/{yr}年_電機機械_全卷完整詳細題解|💡 {yr}年 電機機械全卷詳解]] | [📄 下載 PDF](./{yr}年_電機工程技師_電機機械.pdf) |
| **第 5 節** | **電力系統** | `01150` | 120 分鐘 | 可以使用電子計算器 | [[../../📝 個人題解與錯題本/05_電力系統/{yr}年_電力系統_全卷完整詳細題解|💡 {yr}年 電力系統全卷詳解]] | [📄 下載 PDF](./{yr}年_電機工程技師_電力系統.pdf) |
| **第 6 節** | **工業配電** | `01110` | 120 分鐘 | 可以使用電子計算器 | [[../../📝 個人題解與錯題本/06_工業配電/{yr}年_工業配電_全卷完整詳細題解|💡 {yr}年 工業配電全卷詳解]] | [📄 下載 PDF](./{yr}年_電機工程技師_工業配電.pdf) |

---

## 📊 本年度全真模考成績自評卡

| 科目 | 滿分標準 | 掌握狀態 | 檢討與題解筆記 |
| :--- | :---: | :---: | :--- |
| **電路學** | 100 分 | 🟢 已掌握 | [[../../📝 個人題解與錯題本/01_電路學/{yr}年_電路學_全卷完整詳細題解|📝 查看 100% 完整推導]] |
| **電子學（包括電力電子學）** | 100 分 | ⚪ 待模考 | [📖 查看試題與考點分析](../../依考科分類/02_電子學_含電力電子.md#{yr}年) |
| **工程數學** | 100 分 | ⚪ 待模考 | [📖 查看試題與考點分析](../../依考科分類/03_工程數學.md#{yr}年) |
| **電機機械** | 100 分 | 🟢 已掌握 | [[../../📝 個人題解與錯題本/04_電機機械/{yr}年_電機機械_全卷完整詳細題解|📝 查看 100% 完整推導]] |
| **電力系統** | 100 分 | 🟢 已掌握 | [[../../📝 個人題解與錯題本/05_電力系統/{yr}年_電力系統_全卷完整詳細題解|📝 查看 100% 完整推導]] |
| **工業配電** | 100 分 | 🟢 已掌握 | [[../../📝 個人題解與錯題本/06_工業配電/{yr}年_工業配電_全卷完整詳細題解|📝 查看 100% 完整推導]] |
| **總計 / 及格標準** | **總分：600 分** | **目標：$\ge 360$ 分 (平均 60 分)** | **4 大主科已建置滿分題解** |
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Updated yearly README: {readme_path}")

print("✨ All file synchronizations and link updates completed successfully!")
