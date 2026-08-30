# 其他考科詳解稽核（2026-08-30）

本輪已將同一套稽核管線套用至電路學、電子學（含電力電子）、電機機械、電力系統與工業配電，共 254 題。

- 官方逐題裁切圖仍是題目來源；年度 Markdown 只作為待稽核詳解來源。
- 新增 `scripts/audit_pe_solutions.py` 與 `data/pe-solution-audit.json`。
- 編譯器會依 manifest 顯示 `verified`、`suspected_error`、`needs_manual_review`、`not_attempted`，避免年度模板被誤標為 verified。
- 本輪已完成 114 年首批 24 題 canonical 詳解並通過 Sol 複核：電路學 5 題、電子學 4 題、電機機械 5 題、電力系統 5 題、工業配電 5 題。稽核 manifest 統計為 `verified=24`、`not_attempted=230`、`suspected_error=0`、`needs_manual_review=0`；其餘題目仍不宣稱已校驗。

所有已校驗題目均綁定官方逐題裁切圖、章節分類與標準 LaTeX 推導。工業配電 114 年第 3–5 題因原始裁切圖圖層空白，改以官方 PDF 與既有解答交叉重建，並在詳解方法欄註明來源限制，後續可再補高解析裁切圖。
