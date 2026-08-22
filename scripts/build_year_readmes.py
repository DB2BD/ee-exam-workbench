import os
import glob
import re

years = [str(y) for y in range(114, 103, -1)]

subj_meta = [
    ('01_電路學', '電路學', '01130'),
    ('02_電子學_含電力電子', '電子學（包括電力電子學）', '01120'),
    ('03_工程數學', '工程數學', '01140'),
    ('04_電機機械', '電機機械', '01160'),
    ('05_電力系統', '電力系統', '01150'),
    ('06_工業配電', '工業配電', '01110')
]

# 1. Build Year READMEs
for y in years:
    year_dir = os.path.join('依年度分類', f'{y}年')
    os.makedirs(year_dir, exist_ok=True)
    
    lines = []
    lines.append(f'# 📅 {y} 年 專門職業及技術人員高等考試：電機工程技師 全真模擬試卷\n')
    lines.append(f'> **考試年度**：民國 {y} 年  ')
    lines.append(f'> **考試等級**：專技高考 — 電機工程技師  ')
    lines.append(f'> **考科總數**：6 科（每科考試時間 2 小時，滿分 100 分，總分 600 分，平均 60 分及格）\n')
    lines.append('---\n')
    
    lines.append('## 📑 本年度 6 大考科全真模擬試題索引\n')
    lines.append('| 節次 | 科目名稱 | 試題代號 | 考試時間 | 計算器規範 | 📖 線上題目 (Markdown) | 📄 官方試卷 PDF |')
    lines.append('| :---: | :--- | :---: | :---: | :---: | :--- | :--- |')
    
    for idx, (sfolder, sname, def_code) in enumerate(subj_meta, 1):
        md_link = f'../../依考科分類/{sfolder}.md#{y}-年-電機工程技師--{sname}'
        # Check PDF file
        pdf_pattern = f'{year_dir}/{y}年_電機工程技師_*.pdf'
        pdf_matches = glob.glob(pdf_pattern)
        subj_pdf = ''
        for p in pdf_matches:
            if sname in p or sfolder.split('_')[1] in p:
                subj_pdf = os.path.basename(p)
                break
        if not subj_pdf:
            subj_pdf = f'{y}年_電機工程技師_{sname}.pdf'
            
        lines.append(f'| **第 {idx} 節** | **{sname}** | `{def_code}` | 120 分鐘 | 可以使用電子計算器 | [🔗 線上刷題]({md_link}) | [📄 下載 PDF](./{subj_pdf}) |')
    
    lines.append('\n---\n')
    
    # Mock Scorecard
    lines.append('## 📊 本年度全真模考成績自評卡\n')
    lines.append('| 科目 | 預計模考日期 | 實際作答時間 | 答對題數 / 總題數 | 自評得分 (滿分100) | 掌握狀態 | 檢討與錯題筆記 |')
    lines.append('| :--- | :---: | :---: | :---: | :---: | :---: | :--- |')
    for _, sname, _ in subj_meta:
        lines.append(f'| **{sname}** | 2026-__-__ | ___ 分鐘 | __ / 5 題 | ___ 分 | ⚪ 待模考 | [📝 建立錯題本](../../📝%20個人題解與錯題本/) |')
    
    lines.append('| **總計 / 平均** | — | **總時間：___ 分鐘** | **總題數：__ / 30 題** | **總分：___ / 平均：___** | ⚪ 待評估 | **目標：總分 $\\ge 360$ 分** |')
    lines.append('\n---\n')
    
    lines.append('### 💡 考場時間分配與作答策略建議：\n')
    lines.append('1. **每題平均時間**：每份試卷通常為 4 ~ 5 大題，每題分配 **20 ~ 25 分鐘**，預留 **10 ~ 15 分鐘** 進行全卷數值與單位驗算。')
    lines.append('2. **審題 5 分鐘**：先快速瀏覽全部題目，優先作答最具把握的題型（如基本節點法、標么轉換、ODE），建立答題信心。')
    lines.append('3. **計算機操作確認**：進入考場前確認計算器角度制（DEG）與弧度制（RAD），矩陣與複數計算模式操作熟練。')
    
    with open(os.path.join(year_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Created Year README: {year_dir}/README.md')

print('All 11 Year README files created successfully!')
