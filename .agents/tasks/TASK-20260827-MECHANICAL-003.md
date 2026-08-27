# Task Packet: TASK-20260827-MECHANICAL-003

## Objective
修正規格書中的圖片嵌入語法範例，避免自動圖片驗證器把佔位文字誤判為實際缺圖。

## Context
`SPEC_國考同級參考題庫擴充架構規格書.md` 目前以 `![[image_file|750]]` 示範圖片嵌入格式；這個字串會被 `scripts/test_all_pe_and_gk_images.py` 當作真實圖片參照，造成一筆非實際缺圖的失敗。

## Constraints
- Executor: Antigravity / Gemini 3.7 Flash High (`gemini-3.7-flash-high`).
- 只允許修改 `SPEC_國考同級參考題庫擴充架構規格書.md` 與本任務的 Result Packet。
- 保留原本「使用圖片嵌入語法並可指定寬度」的規格意義，但不要在文件中留下會被圖片 regex 當成真實檔名的 `![[...]]` 佔位語法。
- 不得修改任何 `.js`、`.py`、`.html`、`.css`、測試、題目、題解或設定檔。
- 不得改動工作樹中本任務開始前既有的未提交變更。

## Expected Output
1. 文件中的最小必要修正。
2. `.agents/results/TASK-20260827-MECHANICAL-003.md`，包含修改檔案、範圍遵守與實際驗證命令；不可宣稱未執行的命令。

## Validation
Codex 會獨立執行 `python3 scripts/test_all_pe_and_gk_images.py`、`python3 scripts/run_all_tests.py`、`python3 scripts/verify_slicing_and_links.py`，並檢查 diff。

## Stop Condition
完成限定文件修正並回傳 Result Packet 後停止，不得自行處理其他問題。

## Return Target
請將 Result Packet 寫入 `.agents/results/TASK-20260827-MECHANICAL-003.md`。
