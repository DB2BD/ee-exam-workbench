# 📋 Task Packet

## Metadata
- **Task ID**: `TASK-20260827-MECHANICAL-002`
- **Sender Runtime**: `Codex`
- **Target Runtime**: `Antigravity`
- **Model**: `gemini-3.7-flash-high`
- **Hop Count**: `1`
- **Target Branch**: `main`

## Objective

修復上一份品質盤點中有明確證據的機械性 Markdown 瑕疵，降低 KaTeX、轉義字元與 Obsidian 連結造成的顯示錯誤。

## Allowed Files

只能修改下列類型：

- 題解與知識庫的原始 `.md` 檔案。
- `.agents/results/TASK-20260827-MECHANICAL-002.md`。

不得修改任何 `.js`、`.py`、`.html`、`.css`、測試、設定或核心狀態檔案。

## Required Work

1. 修復報告中指出的兩個檔案內遺失的 LaTeX 反斜線／控制字元，保留原本數學意義。
2. 補上 `GK-114-05-1` 題解缺少的第一大題標題；若無法從原始題目可靠判定標題，停止並回報，不得猜測。
3. 修復報告列出的奇數 `$$` 檔案：只合併明顯被錯誤拆開的數學區塊，不得用盲目補字元方式掩蓋結構問題。
4. 修復 `依考科分類/` 中有明確錯誤的相對路徑與表格 Wikilink；範本佔位符不修改。
5. 每次修改後檢查：括號／分隔符平衡、公式內容未遺失、連結目標存在、原始檔案仍可被題解抽取器讀取。

## Non-Goals / Constraints

- 不得修改任何題目 ID、題目文字、答案數值、解題推導、配分或考點標籤。
- 不得修改或直接重建 `dashboard-data.js`、`solutions-bundle.js`、`national-solutions-bundle.js` 或其他產生檔。
- 不得修改 `src/state/`、`src/components/`、`src/main.js`、`scripts/` 或 `tests/`。
- 不得處理沒有來源證據的數學內容；疑似答案錯誤只回報，不自行更正。
- 不得撤回、覆蓋或整理工作樹原有未提交變更。
- 不得再轉交其他外部 Runtime。

## Acceptance Criteria

- [ ] 只修改允許的 Markdown 檔案與 Result Packet。
- [ ] 每個修改列出檔案、行號、修改前後目的與證據。
- [ ] 重新執行相關抽取／連結／KaTeX 檢查，逐項記錄退出碼。
- [ ] Result Packet 明確區分 `PASS`、`FAIL`、`WARN` 與未處理項目。
- [ ] 若任何修復需要猜測，必須停止該項目並回報 `UNRESOLVED`。

## Return Target

`.agents/results/TASK-20260827-MECHANICAL-002.md`
