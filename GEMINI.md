# Agent 協作補充規範

本檔案保留給採用 Gemini 或其他 Agent 的協作者閱讀；它不指定模型，也不取代根目錄的 `AGENTS.md`。

## 開始工作前

先讀 `AGENTS.md`、`CONTEXT.md` 與本次相關的 `docs/adr/`，再確認目標 QID、原題來源、題解來源與驗證狀態。現行產品是 PE 321 題與 GK 161 筆的靜態雙資料庫，澳洲求職雷達不屬於目前工作台核心。

## 必守工程紀律

1. 欄位或狀態變更先補回歸測試，再改 `src/`、schema、編譯器與生成檔。
2. Solver 與 Verifier 分離；參考書核對完成使用 `reference_book_verified`，不要誤報成官方標準答案。
3. 遇到異常遵循最小復現、假說、探針、原子修復、回歸驗證。
4. 以目前實際存在的編譯器與測試為準：`compile_dashboard_database.py`、`compile_national_exams.py`、`build_workbench.py`、`run_all_tests.py`、`check_html_js_syntax.py`、`verify_slicing_and_links.py`。
5. `health_check_codebase.py` 的分數要如實回報，不能要求或假設永遠 100/100；人工複核是有效的產品狀態。
6. 以繁體中文記錄題解、文件與結果。

## 交付前

確認 PE／GK bundle 沒有互相覆蓋、README 與索引的數量正確、所有新增連結可解析、測試與 `git diff --check` 通過，並列出仍需人工判定的題目。推送 GitHub 前需取得使用者對明確 remote、分支與 commit／tag 的同意。
