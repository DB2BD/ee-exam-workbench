# 題幹稽核任務（Phase 0C）

你負責一個科目 104–114 年全部題目的「題幹文字」與官方裁切圖逐題比對並修正來源。回報與修正內容使用繁體中文。

## 範圍與檔案

- 來源（唯一要改的兩份）：
  1. `依考科分類/<科目檔>.md` 的各 `## YYY年` 段落中，每個 `#### 一、`… 題目區塊（題號行到下一個 `####`／`##` 為止）。
  2. 同科子資料夾的 `依考科分類/<科目資料夾>/*_歷屆試題彙編_104-114年.md` 中對應的題目文字（若存在且內容是同一份題幹，保持兩份一致）。
- 官方依據：`data/pe-question-crops.json` 的 `question_crop`（已稽核過的題目裁切圖）。數值或符號看不清時，以 PyMuPDF 高 DPI 渲染 `pdf_path` 對應頁面或讀取 PDF 文字層輔助。

## 每題步驟

1. 開裁切圖，逐字讀出題幹：題號、敘述、所有數值與單位、方程式／矩陣（含正負號）、子題（一）（二）…、各子題配分與總配分、圖號引用（圖一…）。
2. 與來源題目區塊比對，分類：`match`／`minor`（格式、錯字、單位寫法，不影響解題）／`major`（數值、符號、條件、子題、配分錯誤，或整題不是這一題）。
3. 有差異就改寫來源題目區塊，使其忠實轉錄官方題幹：
   - 保留 `#### <中文題號>、` 開頭格式（編譯器依此切題），子題沿用該檔既有格式（例如 `* **(一)** …（10 分）`）。
   - 數學用 `$…$`／`$$…$$`，矩陣用 `\begin{bmatrix}`；不寫解答、提示或註解；圖只以「如圖一所示」文字指稱，不嵌入新圖片。
   - 不改動年度段的 metadata 區塊與其他題目。
4. 題幹中有缺漏條件或命題矛盾時，照官方原文轉錄，不要替命題者補條件；在結果中標註 `stem_issue`。

## 禁止

- 修改題解（📝 個人題解與錯題本）、`data/*.json`、生成檔、測試、`scripts/`。
- git commit。

## 驗收

修改後執行：
```bash
python3 scripts/compile_dashboard_database.py
python3 -m unittest tests.test_engineering_math_official_alignment tests.test_compile_national_exams tests.test_question_schema tests.test_database_integrity tests.test_year_readmes
```
（`scripts/compile_dashboard_database.py` 內有 `ENGINEERING_MATH_TOPIC_OVERRIDES`／`PE_TOPIC_OVERRIDES` 手寫覆寫，你不要改它；在結果中列出：你修正來源後，哪些覆寫已可移除、哪些覆寫本身與裁切圖不符。）

若測試因題幹字串斷言失敗（測試鎖住了錯誤題幹），不要改測試，列入結果的 `test_conflicts`。

## 輸出

寫入呼叫訊息指定的 JSON：
```json
{"subject":"03","audited":67,
 "items":[{"qid":"EE-111-03-1","verdict":"match|minor|major","diffs":["來源：…／裁切圖：…"],"stem_issue":"","fixed":true}],
 "overrides":[{"qid":"EE-111-03-3","removable":true,"note":"…"}],
 "test_conflicts":[], "other_copies_changed":["…"]}
```
最後三行回報：major 數、minor 數、需主 session 處理的事項。
