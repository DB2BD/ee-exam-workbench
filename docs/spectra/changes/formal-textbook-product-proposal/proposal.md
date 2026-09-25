## Why

現階段最重要的成果不是把工作庫出版成正式教材，而是讓使用者通過電機工程技師考試。既有題庫、詳解與複習工具應先服務個人得分提升，正式出版則作為上榜後可再推進的長期成果。

## What Changes

- **Supersedes：**取代本 change 先前「正式教材優先」的執行決策；已完成的文件工作保留為歷史與長期方向，本次執行改為「使用者上榜優先」。
- 更新 `docs/產品化企劃書_2026-09-05.md`，把首要成功條件改為六科備考進度、可得分作答、弱點改善與計時模考表現，不以出版完成度衡量本次成果。
- 本次只執行四項：以客觀歷屆覆蓋建立六科預設核心題路徑；為核心題建立考場可直接書寫的得分型解答；依「母題 → 同型題 → 變式題 → 混合／整卷」安排練習；以錯因複習與計時模考確認改善。
- 執行採被動、免回填模式：第一輪固定為每科 2 個高覆蓋章節、共 36 題與 24 個核心時段，再做六科 12 題無章節提示混合橋接，最後接 6 科 114 年整卷。個人基線只供日後自選微調，不是開始或前進的條件；不得因固定路徑而捏造使用者弱點或保證及格。
- 目前 10 題人工覆核只在影響得分判斷或會誤導練習時優先處理；其餘維持可追溯狀態，不阻擋個人備考。核心路線只採已驗證題。
- 單一發布清單、公開勘誤、外部考生試用、正式卷冊、PDF／網頁出版與商業化保留為後續階段，不列入本次完成條件。

## Non-Goals

- 本次不以正式出版、全庫改寫、清完所有人工覆核、公開發布或商業化作為完成條件。
- 除依既有流程重建題解 bundle 與靜態工作台外，本次不修改工作台功能邏輯、資料 schema、複習演算法或發布流程。
- 不新增 AI 聊天室、即時 AI 解題、帳號、雲端同步、社群、排行榜、徽章、支付或其他遊戲化功能。
- 不在缺少個人模考與作答紀錄時宣稱已找出使用者弱點、預測及格機率或保證上榜。
- 不為了縮短備考範圍而刪除官方來源、驗證狀態、人工覆核證據或既有學習資料。

## Impact

- Affected specs: none
- Affected code:
  - New: `docs/spectra/changes/formal-textbook-product-proposal/proposal.md`, `docs/spectra/changes/formal-textbook-product-proposal/tasks.md`
  - New: `docs/上榜預設24時段_核心題路徑.md`, `docs/上榜混合橋接_六科12題.md`, `docs/上榜基線_114年六科診斷.md`, `docs/上榜核心母題候選_104-114年.md`
  - Modified: `README.md`, `docs/產品化企劃書_2026-09-05.md`
  - Modified as generated outputs: `data/pe-solution-audit.json`, `dashboard-data.js`, `solutions-bundle.js`, `index.html`
  - Modified content: 固定路徑入選題的 canonical 題解與對應年度彙整頁
  - Removed: none
- Compatibility: no capability-level observable behavior changes
