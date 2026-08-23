# 🤝 Collaboration Contract & Write Protocols

## 1. 寫入所有權與 Git 隔離 (Write Ownership)
- 多個 Agent 可以同時閱讀、檢索與分析本工作區。
- 實際修改程式碼時，遵循 Optimistic Concurrency 模式：
  - 小幅修改（如更新職缺資料、修正錯字）：可直接在 `main` 分支進行並確認 `git diff`。
  - 大幅或破壞性重構：必須開立專用 branch（如 `feat/xxx` 或 `refactor/xxx`），經過 review 後再 merge 回 `main`。

## 2. 跨 Runtime 呼叫邊界 (Delegation Bounds)
- **One-Hop Guard**: 當接收來自外部 Runtime（例如 Codex 轉交）的任務時，當前 Runtime 僅能在內部平行調用 subagent 解決，**不得自動再將同一任務轉拋給另一個外部 Runtime**，避免循環依賴與 Token 無限膨脹。
- 任何跨 Runtime 轉交必須由人類 Coordinator 或明確的任務分派決定。

## 3. CI/CD 與自動化整合防護
- 每次修改 `au_job_radar_crawler.py` 或 `compile_dashboard_database.py` 後，必須在本地執行一次產生腳本以驗證無語法或執行錯誤。
- 確保所有輸出檔案（如 `au-job-radar-data.js`、`dashboard-data.js`）皆可被瀏覽器以 Vanilla JS 直接載入，不依賴需要 build step 的打包工具。
