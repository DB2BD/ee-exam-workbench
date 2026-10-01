# Worker 任務：題解精確化與去冗（lean-v1）

你負責一批 PE canonical 題解（QID 清單見呼叫訊息）。回報與題解內文一律使用繁體中文。

## 先讀

1. `AGENT-SOLVE.md`（唯一版型 `lean-v1`、P1–P6、去冗規則、範例）。
2. `CONTEXT.md` 第 3 節不可逾越規則。
3. `.agents/protected_notes.json`：你的 QID 若在其中，記下對應測試檔。

## 每題流程（S → D → E）

**S｜盲解（先不要看現行題解）**
1. 從 `data/pe-question-crops.json` 找到該題 `question_crop`，用 Read 開圖，逐字抄錄已知量、單位、接線／極性／方向、每個子題與配分。
2. 若裁切圖本身有缺漏、滲入他題或表頭，**停止該題**，在結果中回報 `crop_defect`，不要繞過。
3. 撰寫 `verification/pe/<QID>.py`：只用題目已知量，以 SymPy／NumPy 從第一原理求解；每個子題答案用 `assert`（相對誤差 ≤ 0.5% 或符號相等）；最後印出 `PASS <QID>`。不得讀取題解檔、不得把題解的中間結果寫死。
4. 執行 `python3 scripts/run_verify_scripts.py <QID>`（此時尚未遷移，不會要求 missing）。
   - 論述題（無數值答案，如「說明差動保護原理」）：腳本改為檢查題解中的關鍵量（例如由題目數據導出的比值、方向）或以 `assert` 驗證你提出的定量論據；若整題純文字無可計算量，腳本只需印出 `PASS <QID> (descriptive)` 並在結果中註明。

**D｜比對**
5. 讀現行題解，與 S 的結果逐子題比對，分類為 `none`（一致）、`corrected`（現行答案錯）、`condition_clarified`（題幹確有歧義，需條件分支）。
6. `corrected` 必須附證據：題圖原文、你的推導關鍵式、腳本輸出，以及舊答案錯在哪一步。

**E｜重寫**
7. 依 `lean-v1` 版型整份重寫該題 canonical：
   - frontmatter：保留既有鍵（含 `review_*`、`reference_book_*`），統一為 `qid/year/subject/chapter`，加入 `template: lean-v1`；工程數學以外的科目設 `annual_sync: true`；`method` 改為描述你的獨立方法；`verified_at` 設為今天；**不要改 `audit_status`**（狀態由主 session 決定）。
   - 正文：標題 → 裁切圖連結 → 已知與所求 → 考場標準作答（每子題 `\boxed{}` 帶單位）→ 驗算（不同方法）→ 失分點（≤3 條、本題具體）→ 必要時條件與疑義／計算機按法。
   - 短題（總配分 ≤10 分或一式解完）加 `compact: true`，只留考場標準作答與驗算（失分點僅在確有典型陷阱時保留）。
   - H1 標題若被年度頁測試要求（例如工程數學「# 106 年第 8 題｜…」），沿用原標題。
   - 舊五段式的「得分點拆解」「完整教學推導」內容：有得分價值且未重複者併入考場標準作答，其餘刪除。
   - 驗算段只放「不同方法」的檢查；不得重抄主解已算過的比值或數值，也不用單側擾動（如 ±1 MW）冒充最佳性證明（試點審查教訓）。
   - 刪除：重複推導、校驗紀錄、稽核歷程、正文中的路徑／QID／日期、泛用提醒。
   - 有測試引用的題解：保留測試 `assertIn` 的字串（先讀該測試檔）；若精簡必須動到斷言字串，保留原句並在結果中回報 `needs_test_change`。
8. 自檢：
   - `python3 scripts/lint_canonical_notes.py <QID> --strict`
   - `python3 scripts/run_verify_scripts.py <QID>`
   - 若在 protected 清單：`python3 -m unittest <對應測試模組>`
   全部通過才算完成；最多自修 3 輪。

## 禁止

- 修改生成檔（`*-bundle.js`、`dashboard-data.js`、`index.html`）、`data/*.json`、測試檔、年度全卷檔、其他題目的檔案、裁切腳本。
- 變更 `audit_status`、git commit、push。

## 輸出

寫入呼叫訊息指定的 JSON 路徑，每題一筆：

```json
{"qid":"EE-114-05-3","crop_checked":true,"crop_defect":"","verify_script":"verification/pe/EE-114-05-3.py",
 "verify_passed":true,"answer_change":"none|corrected|condition_clarified",
 "old_answer":"…","new_answer":"…","evidence":"…","chars_before":0,"chars_after":0,
 "asserted_strings_kept":true,"needs_test_change":"","proposed_status":"verified|reference_book_verified|needs_manual_review",
 "lint_passed":true,"open_issues":[]}
```

最後以三行回報：完成題數、`corrected` 題號、仍有問題的題號。
