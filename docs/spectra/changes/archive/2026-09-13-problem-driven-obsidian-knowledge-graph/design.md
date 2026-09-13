# 設計：問題驅動 Obsidian 知識圖譜

## Context

目前專案是靜態、離線優先的題庫工作台，前端以 generated JavaScript bundle 載入資料，並以 PE 與 GK 分離維持考試家族的資料邊界。現有 `src/data/knowledge-dag.js` 約有 69 個 DAG 節點與 14 個核心 Obsidian 筆記，題目到 DAG 的對應仍由關鍵字規則決定，無法命中時會退回該科第一個 subject 節點。這使網站、題目診斷與 Obsidian 內容沒有共同的語意來源。

現有學習流程已有題目揭露、作答、Recall、評分與 SM-2；`src/state/attemptStore.js` 以記憶體 map 保存成功學習嘗試，並有 recovery journal 支援多鍵寫入復原，但尚未形成可跨重新載入恢復的完整 attempt envelope。`src/components/solutionModal.js` 會在解題視窗建立 learning attempt ID，評分後以短延遲前進；`src/components/dailyPractice.js` 另有完成嘗試的套用入口。這些流程需要在導入知識診斷後保持相容，且診斷事件不能在尚未提交成功的作答前產生。

目標資料會同時服務網站 DAG、題目診斷、弱點檢視、知識節點複習與 Obsidian。專案仍必須維持無後端、無執行期向量搜尋、無執行期 LLM 寫入的邊界；AI 只產生待審核候選，不能直接改 canonical graph。現有 2026-09-12 的規劃文件先以可驗收的 20–30 個 golden 節點與可追溯題目連結建立垂直切片，現在已依相同規則完成全量 PE/GK 題目覆蓋。

## Goals

- 建立一份以穩定 ID、題目 QID、exam family 與 graph revision 為核心的 canonical knowledge graph。
- 由 canonical graph 確定性產生網站 DAG 與 Obsidian generated notes，讓生成結果可重建、可檢查漂移，並保護個人補充筆記。
- 將成功作答後的使用者確認診斷記錄為 append-only issue events，產生可重算的「我的弱點」投影。
- 讓知識節點的 retrieval SRS 與題目 SRS 使用不同的識別與狀態，且只在明確回想後排程。
- 以可恢復的 attempt envelope、備份遷移與容量門檻支援瀏覽器崩潰、重新載入與匯入復原。
- 讓 Codex 取得可審計的 context packet 與 revision-aware patch candidate，所有 graph 更新經過驗證、審核與 rebase。
- 保留現有題庫、PE/GK 隔離、Recall/SM-2 與網站檢視器的相容入口，讓導入可分階段回退。

## Non-Goals

- 本 change 不包含 push、publish、tag、部署或任何外部訊息發送。
- 不建立後端、帳號同步、執行期向量資料庫或執行期 LLM 自動寫入。
- 不在沒有題解、題圖或可追溯分類證據時，批次猜測題目對應；證據不足的新增資料必須保留 unknown。
- 不把個人筆記內容直接寫入 generated notes，也不把完整個人學習歷史放入每次 Codex context packet。
- 不以圖的 degree、中心性或相似度取代有證據的題目診斷與人工確認。
- 不在此 change 內完成任意知識節點的自動 split 或自動判定精通。

## Decisions

### Canonical graph owns knowledge meaning

`data/knowledge/nodes.json`、`edges.json`、`question-links.json` 與 `schema.json` 是知識語意的單一來源。Node 至少包含穩定 `nodeId`、`nodeType`、title、examFamily、lifecycle 與 revision metadata；node type 固定支援 question、mechanism、procedure、mainline。Edge 必須包含 `from`、`relation`、`to`、`why`、`confidence`、`evidence` 與 `reviewStatus`。Question link 必須包含 QID、node IDs、confidence、evidence 與 review status，且 QID 受 exam family 邊界約束。

這個決策把「網站節點長什麼樣」與「這個概念為何連到該題」分開，讓網站與 Obsidian 可以各自投影同一份語意。替代方案是繼續把 `knowledge-dag.js` 當主資料，或以 Obsidian markdown 作為可直接解析的資料庫；前者保留目前的 fallback 問題，後者會把排版與語意耦合，也難以做確定性驗證，因此不採用。

### Stable IDs and deterministic graph revisions preserve history

Node ID、QID、issue event ID、attempt ID 與 knowledge review ID 都必須穩定且可追溯。Canonical graph 每次建置產生 deterministic graph revision；節點更新以 lifecycle、node revision hash 與 merged/retired metadata 表達，不覆寫歷史事件所引用的 ID。Rename、merge、split、retire 必須由明確的 migration record 轉移後續查詢與複習狀態。

這能讓備份、診斷事件、Obsidian wikilink 與 Codex candidate 對同一個語意版本保持可驗證關聯。替代方案是使用檔名或陣列 index 作為識別，或每次建置重編 ID；這會使重建後的歷史與 SRS 狀態無法對齊，因此不採用。

### Legacy DAG remains behind a fail-closed compatibility adapter

`src/data/knowledge-dag.js` 的既有 viewer、tracer 與題目檢視入口暫時保留，但題目映射改由 canonical question-links 及一個相容 adapter 提供。映射命中未知、跨 exam family、低信心或資料驗證失敗時，adapter 必須回傳 unknown 狀態與可觀測原因，不得退回任意 subject 節點。第一階段只有通過 validator 的 golden graph 才能取代既有 mapping。

這讓導入期間可以保留已存在的 UI 與測試，同時移除錯誤的假確定性。替代方案是立刻刪除 legacy DAG，或維持現有 fallback 直到資料完全轉換；前者擴大回歸面，後者會把錯誤關聯繼續傳入診斷，因此採用有界 adapter。

### Generated Obsidian notes and personal notes use separate paths

Canonical graph 產生的筆記固定放在 `🧠 問題驅動知識庫/`，個人補充固定放在 `📝 個人知識補充/`。Generated note 使用 stable-ID filename、frontmatter、graph revision、來源 hash 與 semantic wikilinks；生成器必須能辨識非 generated 檔案，不覆寫個人檔案。Generated body drift 會在建置時 fail closed，要求重新生成或人工處理；個人筆記只透過明確的 backlink 或 context 參照參與閱讀。

這保留 Obsidian 的可讀性與個人編輯自由，同時讓網站投影可重建。替代方案是將生成內容與個人內容混在相同檔案中，或讓生成器以檔案標題猜測關聯；兩者都會造成覆寫風險與不穩定連結，因此不採用。

### Durable attempt commit precedes diagnosis events

解題流程以 stable session ID 建立 durable attempt envelope，狀態至少區分 active、committed、acknowledged。`beginOrResume`、`submit`、`ack`、`recover` 必須可重入；只有成功 commit 並確認作答結果後，才可以建立 diagnosis event。若在 commit 與 ack 之間崩潰，恢復流程必須重播或補 ack，而不是建立第二個合法作答；若在 commit 前崩潰，流程必須依照明確的 redo 規則處理。

這把「一次作答」與 UI timer 解耦，避免短延遲前進或重新載入造成重複計數。替代方案是沿用 modal 內的暫存 attempt ID 或只依賴現有多鍵 journal；前者無法跨 reload，後者沒有完整的作答生命週期，因此不採用。

### Diagnosis is deterministic and user-confirmed

診斷引擎只接收可追溯的 QuestionRecord、question links、rating、error type 與 recall 結果，輸出最多 3 個 likely questions、最多 1 個 first prerequisite gap、reason、confidence 與 needsConfirmation。計算題只有在 evidence 支援時才能產生概念弱點；unknown mapping、單純計算失誤或不足證據必須保留 unknown/needs confirmation。

UI 只在成功作答提交後顯示診斷卡，提供確認、修正、none-of-above 與 skip，並依診斷狀態決定是否自動前進。替代方案是由 LLM 在前端自由生成診斷，或在作答提交前預測弱點；前者不可重現且難以測試，後者可能把未完成作答寫進歷史，因此不採用。

### Append-only events feed pure weakness projections

每一個 PE/GK key 各自擁有 issue event stream。事件包含 event ID、attempt ID、QID、exam family、rating、error type、event type、primary/secondary node IDs、候選排名與信心、時間、diagnosis version、graph revision reference 與 supersedes event ID。相同 attempt 的 primary node 最多計數一次；secondary 分開保存；unknown、skip 與 none-of-above 不得虛構 node。

「我的弱點」由純函式 projection 從事件重算，支援 7、30 與 all 的時間範圍、raw count、distinct QIDs、last seen、評分/錯誤/來源分布、確認率、待分類狀態與 drill-down。替代方案是直接累加 mutable counter，或每次診斷立即改寫 node state；兩者在匯入、去重、修正與回復時容易漂移，因此採用 append-only + projection。

### Knowledge review remains separate from question review

知識節點 retrieval 使用獨立的 knowledge review identity 與排程欄位，只有使用者明確進入回想並評分後才建立或更新 SRS state。閱讀筆記、查看診斷或瀏覽 DAG 不會排程知識複習。題目 Recall/SM-2 狀態沿用既有 identity 與規則，不與 node review 混合。

這讓「我看過概念」與「我能從記憶取回概念」有清楚差異。替代方案是用題目答對率代替節點 retrieval，或在開啟節點頁時自動排程；前者無法表達概念回想，後者會產生未經使用者意願的複習負擔，因此不採用。

### Candidate patches are revision-aware and review-gated

Codex context packet 只提供選定弱點節點、相關題目、最短必要歷史、unknown/none-of-above 與當前 graph revision 的 markdown/JSON 預覽，不自動呼叫網路。AI 輸出的 `KnowledgePatchCandidate` 必須帶 candidate ID、base graph revision、來源 issue event IDs、QID、intent、likely questions、reuse/create/update、question links、confidence、evidence 與 expected node hashes。

驗證器必須拒絕未知 QID/node、錯誤 revision、hash drift、duplicate、dangling edge、cycle、缺 evidence、非法 path、過長 payload 與未審核 update。候選只能進入 review queue，經人工 approve 後 rebase 並產生新的 canonical revision；reject 不改 graph。替代方案是直接接受 AI markdown patch，或只用文字審核不驗證 graph；前者可能破壞資料，後者無法可靠檢查結構，因此不採用。

### Static offline-first remains the runtime boundary

所有 runtime 功能在瀏覽器本地完成，資料以現有 static build、local persistence 與 backup/restore 機制承載。生成器、validator、inventory、golden fixture 與 context packet 在開發工具鏈執行；執行期不引入 backend、vector search 或 network-dependent LLM。PE/GK store、備份與匯入必須維持 exam family isolation，且容量與啟動時間有明確驗收門檻。

這延續 ADR-0001 與 ADR-0002 的部署與資料邊界，減少導入風險。替代方案是建立同步服務或讓 runtime 依賴雲端 AI；這會改變現有產品的離線保證、部署模型與隱私邊界，因此不採用。

## Implementation Contract

### Canonical data contract

- `nodes.json` SHALL validate against `schema.json`; each node SHALL carry a stable node ID, node type, title, exam family, lifecycle state, source/provenance and deterministic revision metadata.
- `edges.json` SHALL contain only known active or historically valid endpoints. Each semantic edge SHALL include relation, why, confidence, evidence and review status. Validators SHALL reject duplicate edges, dangling endpoints, illegal cross-family links and cycles where the relation is acyclic.
- `question-links.json` SHALL be keyed by stable QID and exam family. A link SHALL record node IDs, confidence, evidence, review status and source priority. Unknown is a first-class result and SHALL never be represented by an arbitrary node ID.
- The validator SHALL emit machine-readable errors with stable error codes and a human-readable report. A failed validation SHALL block generation and runtime promotion of the affected graph revision.

### Projection and generation contract

- The website generator SHALL produce deterministic output from canonical data, preserve the existing viewer/tracer entry contract, and fail when a referenced node or question is missing.
- The Obsidian generator SHALL write only generated notes under `🧠 問題驅動知識庫/`, include stable-ID frontmatter and graph revision metadata, and preserve files under `📝 個人知識補充/`. Drift detection SHALL identify generated body changes before regeneration.
- Build integration SHALL make generated artifacts reproducible from a clean checkout. Generated output SHALL include a source hash or equivalent provenance so a mismatch is diagnosable.

### Learning and recovery contract

- Attempt APIs SHALL be idempotent for a stable session ID and SHALL expose active, committed and acknowledged states. Diagnosis SHALL be unavailable until the attempt reaches committed state.
- Issue events SHALL be append-only, scoped by PE/GK key, and deduplicated by attempt ID plus event identity. Corrections SHALL supersede prior events. A projection rebuild SHALL produce the same result from the same event stream.
- Diagnosis output SHALL be deterministic for the same graph revision and inputs, bounded to three likely questions and one prerequisite gap, and explicit about confidence and confirmation needs.
- Knowledge retrieval review SHALL use a separate identity and state from question review. A state change SHALL require explicit recall and a user rating.
- Backup/restore SHALL carry versioned attempt, issue-event, knowledge-review and recovery-journal data. Import SHALL validate before replacing local state and SHALL support rollback on failure.

### AI candidate contract

- Context packets SHALL be exportable as markdown and JSON previews with graph revision, selected evidence and bounded history. Export SHALL be offline and SHALL not mutate graph data.
- Candidates SHALL declare their base graph revision and expected hashes. The validator SHALL reject stale or structurally unsafe candidates before review.
- Review SHALL support inspect, reject and approve. Approval SHALL rebase against the current graph, revalidate all references, append provenance, and produce a new deterministic graph revision. No pasted arbitrary text SHALL write canonical data.

### Verification contract

The implementation SHALL provide unit tests for schema validation, legacy fail-closed mapping, deterministic generators, diagnosis boundaries, event idempotence, pure weakness projections, knowledge retrieval scheduling, backup migration and candidate gates. Integration tests SHALL cover the existing solution modal/daily practice flow, PE/GK isolation, reload/crash recovery, clean build reproducibility, Obsidian drift protection and capacity targets. The golden fixture SHALL contain a reviewed first slice of approximately 20–30 nodes, and the promoted graph SHALL have one approved link for every PE/GK question record or an explicit unknown record with evidence. The release gate SHALL exercise at least 5,000 issue events and a backup payload target near 3 MiB with measured results recorded in the acceptance report.

## Risks / Trade-offs

- [Risk] 新增題目或題解的分類證據可能改變。 → [Mitigation] 保留來源與 confidence，完整覆蓋 gate 與 unknown 報告一起檢查，分類變更以新 revision 發布。
- [Risk] Stable ID lifecycle migrations add schema and backup complexity. → [Mitigation] Require deterministic revision hashes, explicit migration records, round-trip fixtures and rollback tests before promotion.
- [Risk] Post-submit diagnosis adds friction to a fast practice loop. → [Mitigation] Bound output, provide skip/none-of-above, and make auto-advance conditional on the card state.
- [Risk] Append-only events increase local storage. → [Mitigation] Enforce the 5,000-event and approximately 3 MiB release gate, compact only through versioned projections, and surface capacity errors before writes.
- [Risk] Generated Obsidian notes can conflict with manual edits. → [Mitigation] Separate generated and personal paths, store source hashes, detect drift and require explicit regeneration handling.
- [Risk] AI candidates can carry plausible but wrong links. → [Mitigation] Require evidence and expected hashes, reject stale/unsafe structures, and require human approval before rebase.
- [Risk] Existing question SRS behavior regresses during store changes. → [Mitigation] Preserve current QID and PE/GK contracts and run regression tests around Recall/SM-2, daily practice and backup restore.

## Migration Plan

1. Inventory the measured legacy 69-node DAG, 14 core notes, existing QID sources, mappings and backup fields into a migration report; do not change runtime behavior.
2. Add schema, validator and 20–30 reviewed golden nodes/links behind new data paths. Record graph revision and coverage without deleting legacy files.
3. Add the fail-closed adapter and deterministic website generator; compare generated output with the existing viewer and keep the legacy path as a rollback boundary until golden acceptance passes.
4. Add the Obsidian generated/personal path split and drift checks; generate the reviewed graph nodes, preserve existing canonical question notes, and record unresolved links.
5. Add durable attempts, diagnosis events, projections and knowledge retrieval state with versioned local persistence. Gate diagnosis on committed attempts and keep question SRS separate.
6. Add backup migration, capacity fixtures and candidate review/context packet tooling. Approve candidates only after revision and security validation.
7. Promote the full PE/GK graph after measured expansion, publish mapped/unknown/manual-review counts in reports, and keep the fail-closed adapter as the compatibility boundary with equivalent tests and an explicit rollback artifact.

## Resolved Decisions

- The reviewed first slice is recorded in `data/knowledge/golden-fixture.json` as `problem-driven-initial-slice` version `1`. It contains exactly 24 node IDs and 20 PE/GK question IDs. The canonical validator checks the schema version, human review status, uniqueness, graph references and question scope before promotion.
- Weakness priority is deterministic and versioned as `weakness-priority.v1`. For each projected node, `score = 0.35*frequency + 0.25*breadth + 0.20*recency + 0.15*severity + 0.05*acceptance`, where `frequency = rawCount/(rawCount+3)`, `breadth = distinctQids/(distinctQids+3)`, `recency = clamp(1 - ageDays/30, 0, 1)`, `severity = (rating1 + 0.5*rating3)/rawCount`, and `acceptance = confirmedCount/totalCount`. The projection exposes the version, score, component values, `reviewState` and `acceptanceMetrics`, then sorts by score, raw count, node ID and role.

## Open Questions

- The backup schema owner SHALL document the version number and migration order before durable issue events and knowledge review state are enabled for existing users.
- The release acceptance report SHALL record measured build time, reload recovery time, event capacity and backup size; thresholds SHALL be fixed before the final gate rather than inferred from a passing machine.
