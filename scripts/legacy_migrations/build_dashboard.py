import os

years = [str(y) for y in range(114, 103, -1)]

subj_meta = [
    ('01_電路學', '電路學'),
    ('02_電子學_含電力電子', '電子學（包括電力電子學）'),
    ('03_工程數學', '工程數學'),
    ('04_電機機械', '電機機械'),
    ('05_電力系統', '電力系統'),
    ('06_工業配電', '工業配電')
]

lines = []
lines.append('# 📊 電機工程技師 — 歷屆試題備考進度總儀表板（104 ~ 114 年）\n')
lines.append('> **目標**：專門職業及技術人員高等考試 — 電機工程技師及格（總分 600 分，平均 60 分及格）  ')
lines.append('> **試卷總量**：6 大考科 × 11 個年度 = **共 66 份完整官方試題**  ')
lines.append('> **使用方式**：直接勾選 `[ ]` 追蹤完成進度，或在 Obsidian 中搭配 Dataview 自動統計！\n')
lines.append('---\n')

lines.append('## 📈 總體備考進度概覽\n')
lines.append('| 考科名稱 | 總份數 | 刷題進度 | 預估平均得分 | 掌握狀態 | 快速前往試題庫 | 考點筆記庫 |')
lines.append('| :--- | :---: | :---: | :---: | :---: | :--- | :--- |')

for sfolder, sname in subj_meta:
    lines.append(f'| **{sname}** | 11 份 | 0 / 11 (0%) | — / 100 | ⚪ 未開始 | [📘 線上題庫](./依考科分類/{sfolder}.md) | [🧠 考點筆記](./🧠%20核心考點知識庫/{sfolder}/) |')

lines.append('| **全科目總計** | **66 份** | **0 / 66 (0%)** | **— / 600** | ⚪ 準備中 | [📑 總目錄](./README.md) | [📝 錯題本庫](./📝%20個人題解與錯題本/) |')
lines.append('\n---\n')

lines.append('## 📋 66 份試卷完整互動式刷題檢核表\n')
lines.append('| 狀態 | 年度 | 考科 | 題目連結 | 預計/完成日期 | 自評得分 | 掌握狀態 | 錯題/詳解筆記 |')
lines.append('| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |')

for y in years:
    for sfolder, sname in subj_meta:
        exam_anchor = f'./依考科分類/{sfolder}.md#{y}-年-電機工程技師--{sname}'
        lines.append(f'| - [ ] | **{y} 年** | {sname} | [🔗 點我刷題]({exam_anchor}) | 2026-__-__ | ___ / 100 | ⚪ 待刷題 | [📝 建立筆記](./📝%20個人題解與錯題本/{sfolder}/) |')

lines.append('\n---\n')

# Obsidian Dataview Section
lines.append('## 🔮 Obsidian 自動化查詢（Dataview 外掛語法）\n')
lines.append('如果您使用 Obsidian，下方代碼將**自動動態列出所有「需二刷」的錯題**與各科複習狀態：\n')
lines.append('```dataview\nTABLE 考科, 考點, 難易度, 自我評分, 最後複習日期\nFROM "📝 個人題解與錯題本"\nWHERE 掌握狀態 = "🔴 需二刷"\nSORT 難易度 DESC\n```\n')
lines.append('```dataview\nTABLE length(rows) AS 總題數, filter(rows, (r) => r.掌握狀態 = "🟢 已掌握") AS 已掌握, filter(rows, (r) => r.掌握狀態 = "🔴 需二刷") AS 需二刷\nFROM "📝 個人題解與錯題本"\nGROUP BY 考科\n```\n')
lines.append('---\n')

# Strategy Section
lines.append('## 🎯 建議備考三階段時間規劃\n')
lines.append('```mermaid\ngraph LR\n    P1[第一階段: 單科擊破 60天] --> P2[第二階段: 錯題二刷 30天] --> P3[第三階段: 全真模考 15天]\n```\n')
lines.append('1. **第一階段（單科靶心攻堅，約 60 天）**：\n   - 依 `依考科分類/` 逐科推進，先攻【電機機械】與【電力系統】（投資報酬率最高）。\n   - 每題務必在白紙上獨立手算，對照 `🧠 核心考點知識庫` 強化觀念。\n')
lines.append('2. **第二階段（錯題二刷與弱點補強，約 30 天）**：\n   - 篩選所有標註為 `🔴 需二刷` 的題目，重新蓋牌計算。\n   - 補強易失分點（如工數留數定理、工業配電短路電流標么法計算）。\n')
lines.append('3. **第三階段（全真計時模考，考前 15 天）**：\n   - 開啟 `依年度分類/`（特別是 114、113、112、111 近 4 年），按照考場 2 小時規範計時全真模擬。\n')

with open('📊 備考進度儀表板.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Created: 📊 備考進度儀表板.md')
