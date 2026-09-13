## Context

本提案承接已完成的 `problem-driven-obsidian-knowledge-graph`。目前 canonical graph 已通過 145 nodes、125 edges、482 question links 的 validation，weakness projection 也已固定 `weakness-priority.v1` 與 24-node/20-QID golden fixture。複查發現的 Warning 集中在可解釋性、報告新鮮度與規格可執行性，不需要改變 offline-first 部署邊界。

主要使用者是以題目作答後複習弱點的考生，以及需要審查 graph/candidate 的 Sol/Luna workflow。設計必須保留 PE/GK 隔離、append-only learning events、既有 QID 與既有產物路徑。

## Goals / Non-Goals

**Goals:**

- 讓每個時間範圍與 projection 結果都能指出使用的時間基準。
- 讓 correction 從有效結論回溯到完整事件鏈，且不污染 raw audit trail。
- 讓 candidate 與 reviewer receipt 可以回答「誰、何時、根據哪個 revision、審了哪個 hash」。
- 讓 acceptance artifacts 能互相核對 revision、source hash、量測門檻與產生時間。
- 為每個規格 scenario 提供最小、可重現的具體例子。

**Non-Goals:**

- 不引進同步服務、雲端 AI 依賴、Obsidian plugin 或帳號系統。
- 不重新設計題目 SRS、knowledge SRS、canonical node lifecycle 或 Critical priority formula。
- 不把 warning 修正直接混入已完成 change 的 archive；本 change 經 review 後才可 apply。

## Decisions

### Explicit evaluation clock is part of projection input

Projection 呼叫分成兩種模式：使用者查詢必須傳入 `options.now` ISO timestamp，重播/測試可以傳入固定 timestamp。輸出增加 `timeAnchor` 與 `timeAnchorMode`，避免把「資料最新時間」誤當成「現在」。為保持舊資料重建能力，未傳 `now` 的純 replay 呼叫可使用 latest-event fallback，但必須明確標示為 `latest-event-replay`，不作為 UI 的即時查詢路徑。

替代方案是直接在 projection 內呼叫 `Date.now()`；這會讓相同事件流在不同時間產生不同結果，破壞 deterministic replay，因此不採用。

### Supersession chains remain inspectable without changing raw events

Projection 保留目前 effective event 的統計方式，另外輸出每個 weakness 的 `supersessionChain`。每個 chain item 至少包含 `eventId`、`supersedesEventId`、`eventType`、`recordedAt`、`nodeIds` 與 `effective`；鏈按 recorded time、event ID 排序，遇到缺失 predecessor 時標示 `traceStatus: incomplete` 並保留 warning。raw event stream 永遠不被 projection 改寫。

替代方案是把 superseded event 重新加入 rawCount；這會讓修正造成重複計數，與目前 priority 與 idempotence 契約衝突，因此不採用。

### Candidate and review records use versioned provenance

Candidate validator 要求 `candidateVersion: 1` 與現有 `schemaVersion` 同時存在，並驗證 `likelyQuestions`、`reuse`、`create`、`update`、`questionLinks` 的資料型別與大小。approve/reject 都產生 review receipt；receipt 至少包含 `candidateId`、`candidateHash`、`baseGraphRevision`、`decision`、`reviewerId`、`reviewedAt`、`reason`/`notes` 與輸出 graph revision（若有）。reviewer identity 由 CLI/UI 明確傳入，不從任意 candidate 內容推斷。

替代方案是只保存 approved/rejected 狀態；它無法在 stale candidate 或多人審查時重建決策依據，因此不採用。

### Acceptance artifacts share one freshness identity

每個 acceptance/build report 都要記錄 `generatedAt`、`graphRevision`、canonical source hash summary 與所依賴的 output revision。總驗收命令在執行 promotion gate 前檢查這些欄位一致；任何缺欄位、revision 不一致或產生時間早於 source artifact 的報告視為 stale。舊 report 只作歷史紀錄，不能冒充目前驗收結果。

替代方案是只檢查命令 return code；這會讓「成功但沿用舊報告」通過 gate，因此不採用。

### Recovery acceptance uses measured time and fixed thresholds

capacity fixture 與 recovery 故障注入測試輸出 `recoveryTimeMs`、`recoveryTimeThresholdMs`、`recoveryTimePass`，並與 event count、issue bytes、backup bytes 一起寫入 acceptance report。threshold 由設定或 fixture 明確指定，不能從本次測量值反推。

替代方案是只驗證最後 state 正確；這無法發現 recovery 退化到影響使用者的程度，因此不採用。

### Scenario examples are contract evidence

每個 `### Requirement` 下的每個 `#### Scenario` 增加一個 `##### Example:`，內容至少列出最小輸入、操作與可觀察輸出。例子使用固定 QID、node ID、revision 或測試資料，避免使用模糊的「正常情況」。範例是規格 evidence，不取代 automated tests。

## Implementation Contract

- Projection interface：`buildWeaknessProjection(stream, { examFamily, range, now, graph })`；UI 使用 `now`，輸出必須包含 `timeAnchor`、`timeAnchorMode`。每個 weakness node 保留現有 priority fields，新增可遍歷的 `supersessionChain` 與 `traceStatus`。
- Candidate interface：candidate 必須帶 `candidateVersion: 1`、現有 `schemaVersion: knowledge-patch-candidate.v1`、source issue IDs、完整 operation arrays、evidence、expected hashes；缺欄位或超限回傳穩定 error code 且不寫檔。
- Review interface：reject/approve 的 receipt 必須含 candidate hash、reviewer identity、review time、decision、base revision 與結果 revision；approval 只有在 rebase、validation 與 output write 全部成功後才寫 approved receipt。
- Acceptance interface：每份 acceptance/build report 必須含 `schemaVersion`、`generatedAt`、`graphRevision`、source/output identity、checks、blocking failures；capacity/recovery report 另含 measured values、thresholds 與 pass/fail。freshness mismatch 必須阻擋 promotion。
- Scenario contract：新增 capability 的所有 scenario 與既有 change 中受本 Warning 影響的 scenario 都要有 `##### Example:`；example 必須可由 task 的測試或 CLI 驗證。
- Scope boundary：本 change 不直接修改 canonical meaning、既有 QID mapping、raw event 內容或 Obsidian personal notes；不通過 freshness/review gate 的資料不得進入 generated outputs。

## Risks / Trade-offs

- [Risk] 強制 UI 傳入時間基準可能使舊呼叫者暫時缺欄。 → [Mitigation] 保留標示清楚的 latest-event replay fallback，並用測試找出所有 UI 呼叫點。
- [Risk] 完整 correction chain 增加 projection payload 大小。 → [Mitigation] 僅對已有 supersession 的 weakness 輸出 bounded chain，並限制每條鏈的 evidence 數量。
- [Risk] freshness gate 會讓舊報告在本地開發時被拒絕。 → [Mitigation] 報告顯示缺少的 revision/hash 與重新產生命令，保留歷史 report 供比較。
- [Risk] reviewer receipt 增加審查操作成本。 → [Mitigation] CLI/UI 預填 candidate hash、revision 與時間，reviewer 只需提供 identity 與 decision/reason。

## Migration Plan

1. 先為 projection、candidate、reports 建立 fixtures 與 red tests，不改 production data。
2. 加入 time anchor、correction trace 與 candidate/review receipt；舊 raw events 與舊 candidate 只可讀取，缺版本者 fail closed 並提供 re-export/review 指示。
3. 更新 acceptance/build writers 與 recovery fixture，重跑 canonical、website、Obsidian、capacity 與 full unittest checks。
4. 補齊 scenario examples，執行 `spectra analyze`、`spectra validate`，確認沒有 capability/spec/task 缺口後才可 apply。
5. rollback 以保留舊 projection/report readers 為界；若 freshness 或 receipt gate 失敗，不替換既有 generated/canonical outputs。

## Resolved Decisions

- reviewer identity 由每次 CLI/UI 操作明確傳入 `reviewerId`；receipt 不從 candidate 內容推斷身份。
- recovery time fixture threshold 固定為 250 ms，並與實際 `recoveryTimeMs` 一起寫入 machine-readable report；日後若需調整，另開 change 重新建立基線。
