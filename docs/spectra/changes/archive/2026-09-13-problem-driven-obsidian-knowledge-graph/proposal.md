## Why

目前題庫網站已有 69 個 `KNOWLEDGE_DAG` 節點、PE/GK 題目與作答後的 Recall／SM-2 狀態，但核心知識筆記、題目映射與個人錯因尚未共享同一個可追溯模型。關鍵字無命中時仍可能退回該科第一個節點，會把不確定的診斷變成錯誤弱點；現在正好需要在擴充 Obsidian 知識庫前先固定資料邊界與驗收契約。

## What Changes

- 建立 canonical knowledge graph，統一問題、核心機制、可重用 procedure、科目主線、前置關係與真實 QID 對應。
- 將節點生命週期、穩定 ID、`nodeRevisionHash` 與 `graphRevision` 納入可驗證契約；不確定題目映射改為 `unknown`，移除錯誤 fallback。
- 由 canonical data deterministic 生成網站 DAG 與問題驅動 Obsidian 筆記，分離 generated notes 與個人補充筆記，保護人工內容。
- 以三類黃金題型建立 20–30 個可人工審查的節點，涵蓋 Per Unit／SLG、Thevenin／受控源、二階 ODE／線性代數，並保留 negative controls。
- 在題目自評後加入可確認、修正、否定或跳過的問題診斷流程，以及由 append-only event log 重建的「我的弱點」檢視。
- 深化作答 attempt 的 durable lifecycle，讓 reload、crash-after-commit 與合法重做不會重複計入學習資料。
- 新增獨立的 knowledge-node retrieval／SRS；閱讀筆記本身不會建立 mastery 或排程，題目 SRS 與 knowledge SRS 維持分離。
- 建立 backup／restore、容量與 crash-recovery 契約，維持 static offline-first、PE/GK 隔離與既有題目資料格式。
- 建立 `KnowledgePatchCandidate` 與本機可複製的 Codex context packet；AI 建議只能進 revision-aware review queue，不得直接寫 canonical graph。
- 以 `analyze`、`validate`、targeted tests、完整建置與人工黃金樣本審查作為每階段品質閘門。

## Non-Goals (optional)

本 change 不包含 GitHub push、公開發布、版本 Tag、runtime backend、runtime LLM 診斷、向量資料庫、一次生成全部 321 題問題頁、直接把 69 個 legacy 節點全部轉成 Obsidian 文章，或自動把完整個人作答歷史傳送到外部模型。第一版不以 graph degree 代表弱點，也不自動把 split 前的 mastery 複製到所有新節點。

## Capabilities

### New Capabilities

- `canonical-knowledge-graph`: 定義四類知識節點、語義邊、穩定生命週期、版本雜湊、題目映射與 legacy compatibility。
- `knowledge-graph-generation`: 從 canonical data deterministic 生成網站 DAG 與 generated Obsidian notes，並保護個人筆記與人工修改。
- `learning-diagnosis`: 以題目、作答評分、錯因與 graph 產生可確認的問題診斷，記錄 issue events，重建弱點 projection 與網站入口。
- `knowledge-retrieval-srs`: 提供獨立 knowledge-node retrieval、排程與 stable node lifecycle 遷移行為。
- `knowledge-patch-workflow`: 產生可複製的 Codex context packet，驗證與審查 `KnowledgePatchCandidate`。
- `learning-data-recovery`: 擴充 attempt metadata、學習資料 backup/restore、容量與 import crash recovery。

### Modified Capabilities

無。現有題庫、Recall、SM-2 與 PE/GK 資料邊界的需求會被保留，新增行為由上述 capabilities 定義。

## Impact

- 新增 `data/knowledge/` canonical data、schema、migration inventory、golden fixtures 與對應 validator／generator scripts。
- 調整 `src/data/knowledge-dag.js` 的 legacy adapter 與題目 mapping，並新增 generated DAG 載入路徑。
- 調整 `src/state/attemptStore.js`、`src/state/recallStore.js`、`src/state/sm2Store.js` 與 backup 邏輯，加入 durable attempt、issue event、knowledge review 與 recovery 契約。
- 調整 `src/components/solutionModal.js`、`src/components/dailyPractice.js`、`src/components/reviewPage.js` 與相關樣式，加入 post-submit diagnosis、弱點入口與知識回想流程。
- 新增 generated Obsidian 輸出路徑與個人補充路徑；既有 `🧠 核心考點知識庫/` 保留為 overview／migration input，不直接被 generator 覆蓋。
- 擴充 `scripts/build_workbench.py` 與既有測試，確保 PE/GK bundle、offline-first 執行模式、題目來源與 provenance 不被污染。
- 可能升版 user-data backup schema；任何 migration、容量、rollback 與 crash-recovery 行為都必須有測試與人工審查證據。
