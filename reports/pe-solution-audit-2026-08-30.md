# 其他考科詳解稽核（2026-08-30）

本輪已將同一套稽核管線套用至電路學、電子學（含電力電子）、電機機械、電力系統與工業配電，共 254 題。

- 官方逐題裁切圖仍是題目來源；年度 Markdown 只作為待稽核詳解來源。
- 新增 `scripts/audit_pe_solutions.py` 與 `data/pe-solution-audit.json`。
- 編譯器會依 manifest 顯示 `verified`、`suspected_error`、`needs_manual_review`、`not_attempted`，避免年度模板被誤標為 verified。
- 目前 254 題先標為 `not_attempted`，等待各科按教科書章節分批建立 canonical 詳解；未覆蓋或未驗證的題目不會被宣稱已校驗。

下一階段依序處理：電路學／電子學、電機機械／電力系統、工業配電；每批 8–12 題，完成後才更新題號級 solutionLink。
