# Wave 3 共同說明（108–106 年）

- 依 `.agents/templates/WORKER_lean_v1.md` 與 `AGENT-SOLVE.md` 執行；段落：已知與所求／考場標準作答／驗算／失分點（＋條件與疑義）；短題可 `compact: true`；題目要求「畫出」時附精簡文字圖。
- 題幹來源 `依考科分類/0X_*.md` 已於 2026-10-03 依官方裁切圖修正（`reports/題幹稽核_2026-10-03.md`、`.agents/results/STEM-AUDIT/0X.json` 有逐題差異）。裁切圖仍是唯一權威；舊題解可能依據錯誤題幹，必須逐項核對已知量。
- 題目未給、舊題解卻使用的量（故障前電壓、X₂、表值等）一律明示為假設。圖表讀值以高 DPI 數位化並寫出讀值。
- 108 年題目屬「108 年被動複測」路徑；所有被測試引用的題號，先 `grep -rn <QID> tests/` 逐條讀斷言並保留字串；若斷言鎖住錯誤答案，回報 `needs_test_change`，不要保留錯誤答案。
- 只動自己科目的 canonical 題解與 `verification/pe/<QID>.py`；不 commit。
