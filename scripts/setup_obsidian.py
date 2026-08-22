import json
import os

# 1. community-plugins.json
with open('.obsidian/community-plugins.json', 'w', encoding='utf-8') as f:
    json.dump(["dataview", "obsidian-kanban"], f, indent=2)

# 2. app.json
app_config = {
    "alwaysUpdateLinks": True,
    "newFileLocation": "current",
    "attachmentFolderPath": "/",
    "livePreview": True,
    "showLineNumber": True,
    "readableLineLength": False,
    "strictLineBreaks": False,
    "foldHeading": True,
    "foldIndent": True,
    "defaultViewMode": "preview",
    "autoPairMarkdown": True,
    "autoPairMath": True,
    "autoPairBrackets": True,
    "tabSize": 2
}
with open('.obsidian/app.json', 'w', encoding='utf-8') as f:
    json.dump(app_config, f, indent=2)

# 3. appearance.json
appearance_config = {
    "accentColor": "#6366f1",
    "baseFontSize": 16,
    "cssTheme": "",
    "theme": "obsidian",
    "enabledCssSnippets": ["custom-style"]
}
with open('.obsidian/appearance.json', 'w', encoding='utf-8') as f:
    json.dump(appearance_config, f, indent=2)

# 4. core-plugins.json
core_config = {
    "file-explorer": True,
    "global-search": True,
    "switcher": True,
    "graph": True,
    "backlink": True,
    "canvas": True,
    "outgoing-link": True,
    "tag-pane": True,
    "page-preview": True,
    "command-palette": True,
    "markdown-importer": True,
    "editor-status": True,
    "bookmarks": True,
    "outline": True,
    "word-count": True
}
with open('.obsidian/core-plugins.json', 'w', encoding='utf-8') as f:
    json.dump(core_config, f, indent=2)

# 5. CSS Snippet for beautiful UI
custom_css = r'''
/* Enhanced Table Styling */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  border-radius: 8px;
  overflow: hidden;
}

th {
  background-color: rgba(99, 102, 241, 0.15) !important;
  color: var(--text-normal);
  font-weight: 600;
  padding: 10px 14px;
}

td {
  padding: 8px 14px;
}

tr:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

/* Math LaTeX equation glow & centering */
.math-block {
  padding: 12px 16px;
  background-color: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366f1;
  border-radius: 4px;
  margin: 1em 0;
  overflow-x: auto;
}

/* Checkbox styling */
input[type="checkbox"] {
  cursor: pointer;
  transform: scale(1.15);
  accent-color: #6366f1;
}
'''
with open('.obsidian/snippets/custom-style.css', 'w', encoding='utf-8') as f:
    f.write(custom_css.strip())

# 6. Interactive Kanban Board
kanban_content = r'''---
kanban-plugin: basic
---

## ⚪ 未開始

- [ ] [[依考科分類/06_工業配電|06. 工業配電 歷屆試題]]
- [ ] [[依考科分類/02_電子學_含電力電子|02. 電子學 歷屆試題]]


## 🟡 進行中 (第一階段刷題)

- [ ] [[依考科分類/04_電機機械|04. 電機機械 歷屆試題]]
- [ ] [[依考科分類/05_電力系統|05. 電力系統 歷屆試題]]
- [ ] [[依考科分類/01_電路學|01. 電路學 歷屆試題]]
- [ ] [[依考科分類/03_工程數學|03. 工程數學 歷屆試題]]


## 🔴 需二刷 (錯題加強)

- [ ] [[📝 個人題解與錯題本/05_電力系統/114年_電力系統_第二題_單線接地故障SLG|114年 電力系統 Q2: 單線接地故障]]
- [ ] [[📝 個人題解與錯題本/03_工程數學/114年_工程數學_第三題_二階線性ODE|114年 工程數學 Q3: 二階常係數ODE]]


## 🟢 已掌握 (精通)

- [ ] [[📝 個人題解與錯題本/01_電路學/114年_電路學_第一題_節點電壓法|114年 電路學 Q1: 節點電壓法]]




%% kanban:settings
```json
{"kanban-plugin":"basic"}
```
%%
'''
with open('📌 6大考科刷題看板.md', 'w', encoding='utf-8') as f:
    f.write(kanban_content.strip())

print('Obsidian configurations, plugins, and Kanban created successfully!')
