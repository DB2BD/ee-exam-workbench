# 電機工程技師題庫維護 Runbook

本文件是目前 PE／GK 靜態雙資料庫的可重現維護流程。先改來源，再編譯生成檔；不要手改 bundle 來掩蓋來源問題。

## 一、資料變更流程

1. 先定位 QID、官方題目 PDF／裁切圖、題解來源與現有驗證狀態。
2. 修改 `依考科分類/`、`依年度分類/`、`📝 個人題解與錯題本/` 或 GK 對應來源目錄。
3. 若調整欄位、狀態或編譯格式，先更新測試與 schema 契約。
4. 執行對應編譯器，產生 PE 或 GK bundle。
5. 重新建置 `index.html`，再跑完整測試與連結／裁切檢核。

## 二、常用命令

### PE／GK 編譯與前端建置

```bash
python3 scripts/compile_dashboard_database.py
python3 scripts/compile_national_exams.py
python3 scripts/build_workbench.py
```

兩個編譯器的輸出互相隔離：PE 產生 `dashboard-data.js`、`solutions-bundle.js`；GK 產生 `national-exams-data.js`、`national-solutions-bundle.js`。

### 稽核與測試

```bash
python3 scripts/audit_pe_solutions.py --write
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/verify_slicing_and_links.py
python3 scripts/health_check_codebase.py
git diff --check
```

`audit_pe_solutions.py --write` 會更新 PE 稽核快照；若只想觀察，先不帶 `--write`。健康檢查分數是診斷資訊，不能取代逐題人工判定。

## 三、題解與參考書更新

- 以官方 PDF／題目裁切圖確認題幹，以參考書作為核對材料。
- 參考書與題意或獨立驗算不一致時，不要靜默覆蓋；在題解保留兩種解法、出題疑義與 `needs_manual_review`。
- 只有完成推導與獨立驗算才可標 `verified`；只有書本核對完成則使用 `reference_book_verified`。
- 題解中的公式、單位、條件分支、驗算與結論要能直接對應題目，不得留下「待補」等偽完成文字。

## 四、GitHub Pages 發布

`.github/workflows/deploy-pages.yml` 會在 GitHub Actions 重新執行建置、測試並發布 `index.html`。本機發布前請確認：

1. 來源、生成檔、README、索引與發版紀錄一致。
2. `run_all_tests.py`、HTML／JS 語法檢查與 slicing/link 檢查全數通過。
3. `git diff --check` 無錯誤，且沒有意外加入個人照片、暫存檔或秘密。
4. 對使用者清楚列出 commit、tag、remote、分支與未解的人工複核項目。
5. `git push` 或其他外部發布動作須得到使用者對明確目的地與 payload 的確認。

## 五、不要使用的過時入口

舊文件中可能出現不存在或不屬於現行工作台的爬蟲、模考產生器、Australia Job Radar 或 `audit_all_solutions_vs_exams.py` 等名稱。以本 Runbook 的實際腳本清單、`AGENTS.md` 與 `CONTEXT.md` 為準；若要恢復舊功能，先另立需求與架構決策。
