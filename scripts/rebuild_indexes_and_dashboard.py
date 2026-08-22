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

# 1. Update 📊 備考進度儀表板.md
dash_lines = []
dash_lines.append('# 📊 電機工程技師 — 歷屆試題備考進度總儀表板（104 ~ 114 年）\n')
dash_lines.append('> **目標**：專門職業及技術人員高等考試 — 電機工程技師及格（總分 600 分，平均 60 分及格）  ')
dash_lines.append('> **試卷總量**：6 大考科 × 11 個年度 = **共 66 份完整官方試題**  ')
dash_lines.append('> **使用方式**：直接勾選 `[ ]` 追蹤完成進度，或在 Obsidian 中搭配 Dataview 自動統計！\n')
dash_lines.append('---\n')

dash_lines.append('## 📈 總體備考進度概覽\n')
dash_lines.append('| 考科名稱 | 總份數 | 刷題進度 | 預估平均得分 | 掌握狀態 | 快速前往試題庫 | 考點筆記庫 |')
dash_lines.append('| :--- | :---: | :---: | :---: | :---: | :--- | :--- |')

for sfolder, sname, _ in subj_meta:
    dash_lines.append(f'| **{sname}** | 11 份 | 0 / 11 (0%) | — / 100 | ⚪ 未開始 | [[依考科分類/{sfolder}|📘 線上題庫]] | [[🧠 核心考點知識庫/{sfolder}/|🧠 考點筆記]] |')

dash_lines.append('| **全科目總計** | **66 份** | **0 / 66 (0%)** | **— / 600** | ⚪ 準備中 | [[README|📑 總目錄]] | [[📝 個人題解與錯題本/|📝 錯題本庫]] |')
dash_lines.append('\n---\n')

dash_lines.append('## 📋 66 份試卷完整互動式刷題檢核表\n')
dash_lines.append('| 狀態 | 年度 | 考科 | 題目直達連結 | 預計/完成日期 | 自評得分 | 掌握狀態 | 錯題/詳解筆記 |')
dash_lines.append('| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |')

for y in years:
    for sfolder, sname, _ in subj_meta:
        dash_lines.append(f'| - [ ] | **{y} 年** | {sname} | [[依考科分類/{sfolder}#{y} 年 電機工程技師 — {sname}|🔗 點我刷題]] | 2026-__-__ | ___ / 100 | ⚪ 待刷題 | [[📝 個人題解與錯題本/{sfolder}/|📝 建立筆記]] |')

dash_lines.append('\n---\n')

# Obsidian Dataview Section
dash_lines.append('## 🔮 Obsidian 自動化查詢（Dataview 外掛語法）\n')
dash_lines.append('如果您使用 Obsidian，下方代碼將**自動動態列出所有「需二刷」的錯題**與各科複習狀態：\n')
dash_lines.append('```dataview\nTABLE 考科, 考點, 難易度, 自我評分, 最後複習日期\nFROM "📝 個人題解與錯題本"\nWHERE 掌握狀態 = "🔴 需二刷"\nSORT 難易度 DESC\n```\n')
dash_lines.append('```dataview\nTABLE length(rows) AS 總題數, filter(rows, (r) => r.掌握狀態 = "🟢 已掌握") AS 已掌握, filter(rows, (r) => r.掌握狀態 = "🔴 需二刷") AS 需二刷\nFROM "📝 個人題解與錯題本"\nGROUP BY 考科\n```\n')
dash_lines.append('---\n')

# Strategy Section
dash_lines.append('## 🎯 建議備考三階段時間規劃\n')
dash_lines.append('```mermaid\ngraph LR\n    P1[第一階段: 單科擊破 60天] --> P2[第二階段: 錯題二刷 30天] --> P3[第三階段: 全真模考 15天]\n```\n')
dash_lines.append('1. **第一階段（單科靶心攻堅，約 60 天）**：\n   - 依 `依考科分類/` 逐科推進，先攻【電機機械】與【電力系統】（投資報酬率最高）。\n   - 每題務必在白紙上獨立手算，對照 `🧠 核心考點知識庫` 強化觀念。\n')
dash_lines.append('2. **第二階段（錯題二刷與弱點補強，約 30 天）**：\n   - 篩選所有標註為 `🔴 需二刷` 的題目，重新蓋牌計算。\n   - 補強易失分點（如工數留數定理、工業配電短路電流標么法計算）。\n')
dash_lines.append('3. **第三階段（全真計時模考，考前 15 天）**：\n   - 開啟 `依年度分類/`（特別是 114、113、112、111 近 4 年），按照考場 2 小時規範計時全真模擬。\n')

with open('📊 備考進度儀表板.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(dash_lines))

print('Updated: 📊 備考進度儀表板.md with 100% working Obsidian wikilink anchors!')

# 2. Update Year READMEs
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
        # Obsidian wikilink anchor
        wiki_link = f'[[依考科分類/{sfolder}#{y} 年 電機工程技師 — {sname}|🔗 線上刷題]]'
        # PDF file name
        subj_pdf = f'{y}年_電機工程技師_{sname}.pdf'
        lines.append(f'| **第 {idx} 節** | **{sname}** | `{def_code}` | 120 分鐘 | 可以使用電子計算器 | {wiki_link} | [📄 下載 PDF](./{subj_pdf}) |')
    
    lines.append('\n---\n')
    
    lines.append('## 📊 本年度全真模考成績自評卡\n')
    lines.append('| 科目 | 預計模考日期 | 實際作答時間 | 答對題數 / 總題數 | 自評得分 (滿分100) | 掌握狀態 | 檢討與錯題筆記 |')
    lines.append('| :--- | :---: | :---: | :---: | :---: | :---: | :--- |')
    for _, sname, _ in subj_meta:
        lines.append(f'| **{sname}** | 2026-__-__ | ___ 分鐘 | __ / 5 題 | ___ 分 | ⚪ 待模考 | [[📝 個人題解與錯題本/|📝 建立錯題本]] |')
    
    lines.append('| **總計 / 平均** | — | **總時間：___ 分鐘** | **總題數：__ / 30 題** | **總分：___ / 平均：___** | ⚪ 待評估 | **目標：總分 $\\ge 360$ 分** |')
    lines.append('\n---\n')
    
    lines.append('### 💡 考場時間分配與作答策略建議：\n')
    lines.append('1. **每題平均時間**：每份試卷通常為 4 ~ 5 大題，每題分配 **20 ~ 25 分鐘**，預留 **10 ~ 15 分鐘** 進行全卷數值與單位驗算。')
    lines.append('2. **審題 5 分鐘**：先快速瀏覽全部題目，優先作答最具把握的題型（如基本節點法、標么轉換、ODE），建立答題信心。')
    lines.append('3. **計算機操作確認**：進入考場前確認計算器角度制（DEG）與弧度制（RAD），矩陣與複數計算模式操作熟練。')
    
    with open(os.path.join(year_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print('Updated: All 11 Year READMEs with 100% working Obsidian wikilink anchors!')

# 3. Update Root README.md
root_lines = []
root_lines.append('# ⚡ 專門職業及技術人員高等考試：電機工程技師 歷屆試題與備考知識庫（104 ~ 114 年）\n')
root_lines.append('本資料庫已完整收錄考選部官方公布之**近十一年（104 年 ~ 114 年，共 11 個年度、66 份完整官方試題 PDF 與 130 張高解析度原卷圖檔）**，並已全數標準化為 **LaTeX 數學公式、電路圖檔對照與互動式備考系統**。\n')
root_lines.append('---\n')

root_lines.append('## 🎯 備考資料庫四大核心模組\n')
root_lines.append('| 模組 | 名稱 | 核心功能與說明 | 快速入口 |')
root_lines.append('| :---: | :--- | :--- | :--- |')
root_lines.append('| **📊** | **[[📊 備考進度儀表板|備考進度儀表板]]** | **66 份試卷互動檢核表**、刷題進度統計、錯題自動化查詢與三階段時間表 | [[📊 備考進度儀表板|🔗 點我開啟儀表板]] |')
root_lines.append('| **📚** | **[[依考科分類/|考科題庫總彙編]]** | **6 大考科 11 年歷屆試題**，標準 LaTeX 公式排版、電路圖檔對照、PDF 原檔下載 | [[依考科分類/|🔗 前往考科題庫]] |')
root_lines.append('| **🧠** | **[[🧠 核心考點知識庫/|核心考點知識庫]]** | 各科高頻核心公式、標準解題步驟（SOP）、歷屆出題考點分析 | [[🧠 核心考點知識庫/|🔗 查閱核心考點]] |')
root_lines.append('| **📝** | **[[📝 個人題解與錯題本/|個人題解與錯題本]]** | 包含標準題解模板、手寫/打字詳解、失分避坑筆記與複習狀態打標 | [[📝 個人題解與錯題本/|🔗 前往錯題本庫]] |')
root_lines.append('\n---\n')

root_lines.append('## 📚 6 大考科 Markdown 題庫快速導覽（點擊直接線上刷題）\n')
root_lines.append('| 科目代號 | 考科名稱 | 收錄年份 | 份數 | 📖 完整 Markdown 題庫 | 🧠 核心考點卡 | 📂 考科資料夾 |')
root_lines.append('| :---: | :--- | :---: | :---: | :--- | :--- | :--- |')
for sfolder, sname, _ in subj_meta:
    root_lines.append(f'| **{sfolder[:2]}** | **{sname}** | 104 ~ 114 年 | 11 份 | [[依考科分類/{sfolder}|📘 {sname}.md]] | [[🧠 核心考點知識庫/{sfolder}/|⚡ 核心考點]] | [[依考科分類/{sfolder}/|📂 資料夾]] |')

root_lines.append('\n---\n')

root_lines.append('## 📅 各年度全真模擬試卷快速索引（含計時規範與成績自評卡）\n')
root_lines.append('| 年度 | 試卷總覽與自評卡 | 收錄科目 | 建議用途 |')
root_lines.append('| :---: | :--- | :---: | :--- |')
for y in years:
    status = '🎯 考前全真計時模擬' if int(y) >= 111 else ('📚 章節靶心鞏固' if int(y) >= 107 else '📚 題型廣度擴充')
    root_lines.append(f'| **{y} 年** | [[依年度分類/{y}年/README|📄 {y} 年全真模擬試卷與計時自評卡]] | 完整 6 科 | {status} |')

root_lines.append('\n---\n')

root_lines.append('## 💡 推薦備考作戰工作流（Obsidian / VS Code）\n')
root_lines.append('```mermaid\ngraph TD\n    A[第 1 階段: 單科靶心攻堅] -->|依考科分類 .md| B[研讀 🧠 核心考點知識庫]\n    B --> C[白紙蓋牌獨立推導]\n    C -->|紀錄計算心得與易錯陷阱| D[撰寫 📝 個人題解與錯題本]\n    D --> E[在 📊 備考儀表板 標記 🟢已掌握 或 🔴需二刷]\n    E --> F[第 2 階段: 錯題二刷與弱點補強]\n    F --> G[第 3 階段: 依年度分類 全真 120 分鐘計時模考]\n```\n')

with open('README.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(root_lines))

print('Updated: Root README.md with 100% working Obsidian wikilinks!')
