# 🤖 Repository Agent Instructions & Collaboration Contract (AGENTS.md)

> 本文件依據 **Codex × Antigravity 協作架構** 制定，為本 Repository 中所有 AI Agent（包括 Antigravity、Codex、GitHub Copilot、本地模型等）的通用遵循規範。

---

## 1. 核心原則 (Core Principles)

1. **原生能力優先 (Native Capabilities First)**:
   - 充分利用各平台的原生能力（Antigravity 的 Browser/Subagent/UI、Codex 的 Batch Code/Testing），不額外引入多餘的中介框架。
2. **依能力分工 (Capability-Aware Routing)**:
   - **Antigravity**: 負責 UI/UX 設計、即時瀏覽器測試、Google 搜尋驗證、LaTeX 數學公式排版、互動式工作台。
   - **Codex**: 負責大規模程式碼重構、單元測試執行、CI/CD 腳本維護、GitHub Issue/PR 自動化。
   - **Local Model**: 負責離線敏感資料審查與私密內容過濾。
3. **有限度委派防護 (One-Hop Delegation Guard)**:
   - 跨 Runtime 委派深度限制為 1-hop，禁止 A ➔ B ➔ A ➔ B 的遞迴鏈條。接收到外部任務的 Runtime 必須在內部完成並產出結果。
4. **規格導向與寫入隔離 (Spec-Driven & Write Isolation)**:
   - 所有破壞性或架構性變更 **必須** 先核對或更新對應的 `SPEC_*.md`。
   - 修改程式碼時需保證 CI/CD 自動建置與 GitHub Pages 的正確性。

---

## 2. 專案雙核心架構 (Repository Dual Core)

本倉庫包含兩大核心子系統，任何 Agent 修改時均不得破壞既有架構：

### 核心 A: 電機技師歷屆試題雙欄對照工作台
- **主頁面**: `index.html`
- **資料庫**: `dashboard-data.js`, `solutions-bundle.js`
- **架構規格書**: `SPEC_雙欄原題與詳解同步對照旗艦工作台.md`
- **編譯腳本**: `scripts/compile_dashboard_database.py`

### 核心 B: 澳洲重電求職情報戰情室 (Australia Job Radar)
- **主頁面**: `australia-job-radar.html`
- **資料庫**: `au-job-radar-data.js` (⚠️ 由 Python 自動產生，禁止手動修改)
- **爬蟲/資料產生器**: `scripts/au_job_radar_crawler.py` (6 大模組)
- **架構規格書**: `SPEC_澳洲重電求職戰情室架構規格書.md`
- **CI/CD 自動排程**: `.github/workflows/job-radar-update.yml` (每日 08:00 AM 台北時間自動爬取)

---

## 3. 內容規範與安全不變量 (Content Invariants)

1. **中立性原則**:
   - 澳洲戰情室及題庫內容面向公開 GitHub Pages，嚴禁出現特定前雇主或現職企業字眼（如「中鼎」、「CTCI」等），統一使用客觀工程/產業用語（如「EPC 重工業」、「LNG 天然氣工程」）。
2. **URL 建構規範**:
   - 澳洲戰情室的所有職缺連結必須透過 `scripts/au_job_radar_crawler.py` 中的 `build_links()` 產生，嚴禁手動寫死失效路徑。
   - LinkedIn GeoID: Perth 必須使用 `101902409`，Brisbane 使用 `101471505`。
   - Indeed AU 必須使用 `au.indeed.com`。
   - Google Jobs 必須攜帶 `&ibp=htl;jobs`。

---

## 4. 跨平台交接格式 (Task / Result Packet Protocol)

當不同 AI Runtime 之間透過 GitHub Issue、PR 或 Markdown 交換任務時，請遵循標準封包格式：

- 任務交辦範本：`.agents/templates/TASK_PACKET.md`
- 成果回報範本：`.agents/templates/RESULT_PACKET.md`
