# -*- coding: utf-8 -*-
"""
build_master_national_subject_files.py
======================================
Compiles 5 subject-level master Markdown index files in `依考科分類/🏛️_國考同級參考題庫/`:
- 01_電路學.md
- 02_電子學_含電力電子.md
- 03_工程數學.md
- 04_電機機械.md
- 05_電力系統.md
Exactly matching the structure of PE Technician master files (e.g. `依考科分類/01_電路學.md`).
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

from generate_all_national_exams import EXAM_DATA, SUBJECT_DIRS

SUBJECT_NAMES = {
    '01': '電路學',
    '02': '電子學（含電力電子）',
    '03': '工程數學',
    '04': '電機機械',
    '05': '電力系統'
}

BASE_DIR = os.path.join(WORKSPACE, "依考科分類", "🏛️_國考同級參考題庫")

for sid, sdir in SUBJECT_DIRS.items():
    sname = SUBJECT_NAMES[sid]
    master_file = os.path.join(BASE_DIR, f"{sdir}.md")
    
    lines = [
        f"# 🏛️ 公務人員高等考試三級 歷屆試題彙編 — {sname}（110 ~ 114 年）",
        "",
        "> **考科核心範疇與常考重點**：",
        f"> 公務人員高等考試三級考試電力工程／電子工程類科之【{sname}】歷屆試題全真彙編。",
        "> 收錄 110 至 114 年共 5 個年度之官方標準試題、配分、詳細步驟解析與公式推導。",
        "",
        "---",
        "",
        "## 📑 快速目錄導覽",
        "",
        "| 年度 | 考科名稱 | 試題代號 | 考試時間 | 計算器規範 | 快速跳轉試題 | 官方試卷 PDF |",
        "| :---: | :--- | :---: | :---: | :---: | :--- | :--- |",
    ]
    
    for yr in [114, 113, 112, 111, 110]:
        data = EXAM_DATA.get((sid, yr))
        if data:
            lines.append(f"| **{yr} 年** | {data['title']} | `{data['code']}` | {data['time']} | 可以使用電子計算器 | [🔗 前往 {yr} 年試題](#{yr}年) | [📄 考選部原題平臺](https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx) |")
            
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for yr in [114, 113, 112, 111, 110]:
        data = EXAM_DATA.get((sid, yr))
        if not data:
            continue
            
        lines.append(f"## {yr}年")
        lines.append("")
        lines.append(f"> **考試年度**：{yr} 年  ")
        lines.append("> **等別**：高等考試三級  ")
        lines.append(f"> **類科**：電力工程 / 電子工程  ")
        lines.append(f"> **科目**：{data['title']}  ")
        lines.append(f"> **考試時間**：{data['time']}  ")
        lines.append(f"> **試題代號**：`{data['code']}`  ")
        lines.append("> **計算器規範**：可以使用電子計算器  ")
        lines.append(f"> **官方原始試題**：[📄 考選部考畢試題查詢平臺](https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx)  ")
        lines.append("")
        lines.append("### 📝 試題內容與數學公式編排（LaTeX）")
        lines.append("")
        
        num_map = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        for idx, (main_q, sub_qs) in enumerate(data["questions"]):
            num_str = num_map[idx]
            lines.append(f"#### {num_str}、 {main_q}")
            if sub_qs:
                lines.append("")
                for sub_idx, sub_q in enumerate(sub_qs):
                    sub_num = ["一", "二", "三", "四", "五", "六"][sub_idx]
                    lines.append(f"* **({sub_num})** {sub_q}")
                    lines.append("")
            else:
                lines.append("")
                
        lines.append("[⬆ 回到目錄導覽](#📑-快速目錄導覽)")
        lines.append("")
        lines.append("---")
        lines.append("")
        
    content = "\n".join(lines)
    with open(master_file, "w", encoding="utf-8") as fp:
        fp.write(content)
    print(f"  ✅ Created Master File: 依考科分類/🏛️_國考同級參考題庫/{sdir}.md")

print("\n🎉 Successfully compiled 5 master subject files for National Exams!")
