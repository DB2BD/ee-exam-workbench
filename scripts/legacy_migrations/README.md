# 歷史修復與生成腳本封存目錄 (Legacy Migrations & Historical Scripts)

本目錄封存了知識庫開發初期、歷次資料庫遷移、公式正則修復（`fix_*.py`、`clean_*.py`、`rebuild_*.py`）、批次題解生成（104~113 各科舊版腳本）等歷史一次性工具。

## 說明
- 這些腳本已順利完成其歷史階段性任務（產生的試題 Markdown、LaTeX 公式、圖檔映射與資料庫皆已固化於題庫中）。
- 為維持 `scripts/` 核心建置、編譯、自動化測試（CI/CD）管線清晰乾淨，歷史修復腳本統一收攏於本目錄封存備查。
- 專案日常建置與測試請使用根層 `scripts/` 中的活躍工具（如 `build_workbench.py`、`compile_dashboard_database.py`、`run_all_tests.py` 等）。
