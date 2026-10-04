# Wave 4 共同說明（105–104 年，61 題）

- 依 `.agents/templates/WORKER_lean_v1.md` 與 `AGENT-SOLVE.md` 執行；段落：已知與所求／考場標準作答／驗算／失分點（＋條件與疑義）；短題可 `compact: true`；題目要求「畫出」時附精簡文字圖。
- 題幹來源 `依考科分類/0X_*.md` 已於 2026-10-03 依官方裁切圖修正（`reports/題幹稽核_2026-10-03.md`、`.agents/results/STEM-AUDIT/0X.json` 有逐題差異）。裁切圖仍是唯一權威；舊題解可能依據錯誤題幹，必須逐項核對已知量。
- 已知高風險（交接文件）：EE-104-03-1、EE-105-03-1、EE-105-03-2 舊題解解錯題目，須依官方裁切圖重解；EE-104-06-2 舊解漏參差因數。
- 題目未給、舊題解卻使用的量（故障前電壓、X₂、表值等）一律明示為假設。圖表讀值以高 DPI 數位化並寫出讀值。
- 104 年部分題目在 24 核心時段與混合橋接路徑中（`grep -rn <QID> docs/上榜*.md tests/`）；所有被測試引用的題號，逐條讀斷言並保留字串；若斷言鎖住錯誤答案，回報 `needs_test_change`，不要保留錯誤答案。
- 只動自己科目的 canonical 題解與 `verification/pe/<QID>.py`；不改 `audit_status`、不 commit。
- 結果寫入 `.agents/results/WAVE-4/0X.json`（X＝科目代碼）；審查寫入 `.agents/results/WAVE-4/review-0X.json`。
