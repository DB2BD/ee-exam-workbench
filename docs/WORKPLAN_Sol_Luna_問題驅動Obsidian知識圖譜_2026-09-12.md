# Sol／Luna 工作計劃：問題驅動 Obsidian 知識圖譜

日期：2026-09-12
上位提案：[`PROPOSAL_問題驅動Obsidian知識圖譜_2026-09-12.md`](PROPOSAL_問題驅動Obsidian知識圖譜_2026-09-12.md)
適用專案：電機工程技師歷屆試題與詳解工作台

## 0. 任務目標

將目前的「題庫網站 + 69-node Knowledge DAG + Obsidian 核心考點 + Recall/SM-2」收斂成同一套問題驅動知識系統：

```text
真實考題 / 作答結果
       ↓
具體困惑 question
       ↓
缺失前提 prerequisite
       ↓
核心機制 mechanism
       ↓
可重用算法 procedure
       ↓
科目主線 mainline
```

第一個可交付版本必須做到：

1. canonical knowledge graph 成為單一真相來源。
2. 網站 DAG 與 Obsidian Markdown 都由 canonical data 生成。
3. 題目無法可靠映射時回傳 `unknown`，不得再 fallback 到該科第一節點。
4. 黃金樣本能從題目指出 1–3 個具體困惑與第一個前置缺口。
5. 所有 Obsidian wikilink 都附「點過去會解決什麼」的語義。
6. 現有四段蓋牌、attempt transaction、Recall、SM-2、PE/GK 隔離維持成立。
7. 使用者確認過的「具體問題點」要能獨立累積，不只留下粗粒度 `errorType`。
8. 網站新增「我的弱點」檢視，可看高頻問題點、最近發生時間、對應 QID 與目前複習狀態。
9. 任一具體弱點可產生可直接貼給 Codex 的結構化 context packet，不要求 runtime LLM 或後端。
10. Codex 深入解析後若提出知識圖譜修改，只能回到 `KnowledgePatchCandidate` 驗證流程，不得直接寫正式 graph。
11. 個人學習歷史以不可變事件為正式來源；弱點次數、優先度、命中率等皆由 projection 重建，不另外保存不可追溯的計數器。
12. knowledge node ID 永久穩定；改名、合併、退休不得重用 ID，歷史事件仍可追溯當時的 node 與 graph revision。
13. 診斷後操作不得與既有「自評後自動跳下一題」競爭；有弱點訊號時先完成確認／跳過，再前進。
14. Codex candidate 必須攜帶 `baseGraphRevision`；graph 已變更時不得把 stale candidate 直接套用。
15. Generated Obsidian 筆記與個人補充筆記分離；generator 不把人工心得當生成來源，也不靜默覆蓋非生成檔。
16. 新增的事件、SRS、receipt、backup 狀態必須有容量與 crash-recovery 測試；第一版仍維持 static offline-first，不因這些需求導入 runtime backend。

本計劃不含 GitHub push、公開發布或版本 Tag；完成候選版後交使用者驗收。

---

## 0.1 再驗證結論與已確認風險

2026-09-12 依目前 worktree 再檢查後，方案仍可在現有 static offline-first 架構內完成，不需要改成後端服務或向量資料庫。現有基礎與缺口如下：

- `build_workbench.py` 已以明確順序載入 domain／state／component 模組，可新增 knowledge state / diagnosis module 而不需要改變執行模型。
- `submitLearningAttempt()` 已有 multi-key recovery journal、衝突 fingerprint 與同頁面冪等；但成功 attempt 只用記憶體 `Map` 保留，且 `createLearningAttemptId()` 每次開啟 modal 產生新 UUID。故「跨 reload／crash 後是否為同一次作答」目前沒有 durable lifecycle，不能只加一個 receipt 就宣稱已解決。
- backup import 已先做整包 validation，寫入失敗時也會回復已寫 keys；這是擴充新 store 的良好基礎，但目前沒有 crash 中斷後的 import recovery journal。新增多個學習 store 後必須補齊。
- 每日練習已有持久化 session 與 `createdAt`；可擴充 stable `sessionId` / attempt envelope，而不必另做 runtime backend。
- 非每日練習自評成功後目前約 600ms 自動前進；每日練習成功後會立即關閉 modal / 進下一題。這與「自評後讓使用者確認具體問題點」直接衝突，必須改成明確 post-submit flow。
- legacy `mapQuestionToDagNodes()` 無命中時確實 fallback 到該科第一個節點；新診斷層必須 fail closed 為 `unknown`。
- `data/knowledge/` 與 `🧠 問題驅動知識庫/` 目前尚未存在，因此可用新路徑建立 canonical / generated 邊界，不需覆寫既有 14 篇核心總覽筆記。
- 目前 attempt、backup、recall、SM-2、knowledge DAG 的相關 baseline 測試共 41 個，重跑全數通過；因此本計劃是在綠色基線上增量修改，而不是先掩蓋既有失敗。
- Knowledge Issue Event Log 做了保守容量估算：若每筆重複保存完整 node hash map / label / candidate list，代表事件約 837 bytes，5,000 筆約 3.84 MiB，太接近常見 localStorage 壓力區；改用 stable node ID、graph revision dictionary 與精簡診斷摘要後，代表事件約 520 bytes，5,000 筆約 2.47 MiB。故第一版 localStorage **有條件可行**，但容量測試是 release gate，不能假設無限成長。

### Source of truth 分層

完成後只允許下列正式來源：

```text
靜態正式來源
  data/knowledge/*              = canonical knowledge graph

個人正式來源
  Learning Attempt state        = 題目自評／Recall／SM-2 的既有正式狀態
  Knowledge Issue Event Log     = PE / GK 各自隔離的使用者確認／修正／否定事件
  Knowledge Review state        = knowledge-node retrieval / SRS

可重建衍生物
  Website DAG / Obsidian Markdown
  我的弱點統計 / priority score
  diagnosis acceptance metrics
  Codex context packet
```

任何可由上述正式來源重建的資料，不再新增另一份可獨立漂移的 localStorage cache。

---

## 0.2 建議的 deep modules 與 seam

避免把所有邏輯堆進 `solutionModal.js` / `reviewPage.js`。以下 module 的 interface 是主要測試面；UI component 只負責收集輸入、render result、觸發下一步。

| Module | Interface 責任 | 不應知道 |
| --- | --- | --- |
| `attemptStore`（深化既有） | begin/resume、submit、recover、acknowledge learning attempt | DOM、知識圖譜內容 |
| `knowledgeGraph` | 讀 canonical nodes/edges/question links、resolve lifecycle、graph revision | 個人學習歷史 |
| `knowledgeDiagnosis` | `diagnose(question, assessment, graph, recall)` 回傳候選／前置缺口／confidence | localStorage、DOM、Codex |
| `knowledgeIssueStore` | record decision、append correction、validate schema、避免等價重複 decision | 弱點排行算法、DOM |
| `weaknessProjection` | 由 event log + graph + review state 純計算統計／priority | storage 寫入 |
| `knowledgeReviewStore` | knowledge-node retrieval attempt 與 SRS | question attempt transaction |
| `contextPacketBuilder` | 從選定 issue 建 deterministic Markdown/JSON preview | 外部網路呼叫、graph 寫入 |
| `knowledgePatchValidator` | 驗 candidate schema/revision/duplicate/cycle/evidence | UI 決策 |
| `knowledgePatchApplier` | 只對已核准 candidate 更新 canonical source，再觸發 generator | 任意 AI prose / 任意路徑 |

原則：

- UI 與 tests 都跨同一個 module interface，不另做只有測試才用的隱藏行為。
- 邏輯能 pure function 就 pure function；尤其 diagnosis、projection、candidate validation 優先不碰 storage。
- 只有真的出現第二種 storage implementation 才建立 storage adapter seam；第一版不要為假想 IndexedDB 加一堆 interface。
- 新功能若需要 UI 同時知道五個 store 的內部格式，代表 module 太淺，先收斂 interface 再實作。

---

## 1. 固定分工

### Sol：架構、判斷、獨立審查

Sol 負責：

- 定義 schema、edge 語意、遷移策略與資料不變量。
- 決定一個候選節點應 reuse／create／update／unknown。
- 審查黃金樣本的知識粒度與 prerequisite 是否合理。
- 核准跨模組介面與 localStorage / backup 契約變更。
- 每批完成後獨立驗證，不只採信 Luna 的測試結果。
- Luna 遇到矛盾、兩次失敗、無法驗證或高影響決策時介入。

### Luna：調查、實作、測試、整理證據

Luna 負責：

- 例行資料盤點、QID 對照、候選節點整理。
- schema validator、generator、adapter、UI 與測試實作。
- 依 Sol 核准契約製作黃金樣本與 migration fixture。
- 每批提供修改檔案、測試、失敗前／修正後證據與未解項。

推理強度：

- Luna medium：資料盤點、固定格式轉換、生成器、文件同步、機械性 migration。
- Luna high：schema 設計落地、graph migration、診斷規則、attempt/SRS 接線、跨狀態 UI。
- Sol：自行依風險選擇推理強度，不固定級別。

---

## 2. 所有 Agent 開工前必讀

依序讀：

1. `AGENTS.md`
2. `CONTEXT.md`
3. `docs/PROPOSAL_問題驅動Obsidian知識圖譜_2026-09-12.md`
4. 與本批相關的 `docs/adr/`
5. `AGENT-SPEC.md`
6. `AGENT-CODE.md`
7. 涉及題解內容時再讀 `AGENT-SOLVE.md`
8. 目標程式與現有測試

共同不變量：

- 穩定 QID 與 provenance 不受知識圖譜重構影響。
- PE／GK 題庫、bundle、localStorage 邊界維持隔離。
- 生成檔由來源與 generator 產生，不直接手改。
- reveal step 只代表看過哪一段，不代表能力。
- SRS 排程只能由明確 recall 自評觸發。
- 一次題目作答仍由既有單一 attempt transaction 負責。
- AI 候選資料不得直接覆寫 reviewed 節點。
- `errorType` 是作答錯因；具體 `knowledge issue` 是使用者確認的問題點。兩者分開保存，不互相覆蓋。
- 同一 attempt 的問題點確認必須冪等；重新整理、重按不得重複灌高弱點次數。

---

## 3. 執行模式

每批固定走：

```text
Sol 定義 Task Packet
  ↓
Luna 建立失敗案例 / fixture
  ↓
Luna 實作 + targeted tests
  ↓
Luna Result Packet
  ↓
Sol 獨立檢查實際資料與正式接線
  ├─ reject → Luna 依具體問題修正
  └─ approve → 下一批
```

同一檔案或同一 schema 的寫入保持串行。可平行的只限：只讀盤點、不同科黃金樣本調查、互不相依的 fixture 準備。

Result Packet 至少包含：

- 修改檔案。
- 資料來源與假設。
- 新增／改變的公開契約。
- 執行過的測試與結果。
- 一個正常案例與一個反例。
- 未驗證與人工 review queue。
- 下一個安全步驟。

---

# Phase 0｜先固定語言與黃金樣本

## P0-A｜現況 inventory 與命名對照

**Owner**：Luna medium
**Reviewer**：Sol

### Luna 工作

盤點並輸出 machine-readable inventory：

- 現有 69 個 `KNOWLEDGE_DAG` 節點。
- 14 篇 `🧠 核心考點知識庫` 筆記。
- 各節點 prereqs、公式、keyTrap。
- 題目目前如何透過 `mapQuestionToDagNodes()` 命中。
- 既有 taxonomy / formulaTags 可重用資訊。
- 三個黃金領域相關的真實 QID。

先只讀，不改正式 DAG。

### 交付

建議新增：

```text
data/knowledge/migration-inventory.json
reports/knowledge-graph-inventory.md
```

### Sol 驗收

- 69 個 legacy node 全部可追蹤。
- 14 篇舊核心筆記都有對應狀態：reuse / split / overview-only / unresolved。
- 找出所有 fallback-to-first-node 路徑。
- 不把文字相似直接視為概念相同。

**退出條件**：任何 legacy node 都能回答「來源在哪、現在被哪些功能使用」。

---

## P0-B｜Canonical schema contract

**Owner**：Sol
**Implementer**：Luna high

### Sol 先定義

只保留四種 node type：

- `question`
- `mechanism`
- `procedure`
- `mainline`

最少需要的 edge 語意：

- `prerequisite_of`
- `explained_by`
- `uses_procedure`
- `belongs_to_mainline`
- `next_question`
- `question_uses_node`

每條 semantic link 必須能攜帶：

```text
from
relation
to
why
confidence
evidence
reviewStatus
```

`why` 是 Obsidian 顯示文字的來源，必須回答「點過去會解決什麼」。

每個 node 另外必須有穩定生命週期欄位：

```text
id                 # 永久 ID，不因 title 改名
type
subjectId
title
aliases[]
status: active | retired | merged
supersededBy[]      # merged 時使用；split 時可多值但不可自動改寫歷史事件
reviewStatus
```

`nodeRevision` 不採容易忘記手動遞增的流水號；generator / validator 對 canonical node 正規化後計算 deterministic `nodeRevisionHash`，並對整份 graph 計算 `graphRevision`。使用者事件與 Codex candidate 只引用 ID + revision hash，不引用檔名當識別碼。

題目映射需明確包含 `examFamily`。PE／GK 的 QuestionRecord、attempt 與 provenance 持續隔離；`mechanism` / `procedure` 可跨 PE／GK 共用，不因資料庫隔離複製兩份相同知識節點。

### Luna 實作

建立：

```text
data/knowledge/schema.json
data/knowledge/nodes.json
data/knowledge/edges.json
data/knowledge/question-links.json
scripts/validate_knowledge_graph.py
tests/test_knowledge_graph_schema.py
```

validator 至少檢查：

- node id 唯一。
- type 合法。
- edge 兩端存在。
- prerequisite graph 無 cycle。
- question link 的 QID 真實存在。
- `confidence` / `reviewStatus` 格式合法。
- semantic edge 必須有 `why`。
- reviewed node 不能被未 review patch 靜默覆蓋。
- node ID 不得重用 retired / merged ID。
- `supersededBy` 目標存在且不得形成 lifecycle cycle。
- question link 的 `examFamily` 與 QID 一致。
- deterministic `graphRevision` / `nodeRevisionHash` 重跑穩定。

### Sol 驗收

故意製造 duplicate id、dangling edge、prerequisite cycle、lifecycle cycle、未知 QID、PE/GK family mismatch、缺 `why`、非法 confidence、重用 retired ID 等 fixture，全部必須 fail closed。

**退出條件**：schema 能表達提案中的四種節點與語義 link，且 validator 能可靠拒絕壞資料。

---

## P0-C｜30-node 黃金樣本

**Owner**：Luna high
**Reviewer / Editor**：Sol

### 範圍

先做約 20–30 個節點，不追求全題庫：

1. 電力系統：Per Unit、對稱分量、SLG。
2. 電路學：Thevenin、受控源、一階暫態。
3. 工程數學：二階 ODE、線性代數。

每個 `question` node 必須包含：

- 真正困惑。
- 目標。
- 缺失前提。
- 核心機制。
- 使用 procedure。
- 反例／失效條件。
- 真實 QID。
- retrieval prompt。

### Sol 審查規則

逐節點判斷：

- 這是一個完整困惑，還是章節標題？
- 能否由至少一題真實考題觸發？
- 是否已存在近義節點？
- prerequisite 是必要前提，還是只有「相關」？
- mechanism 是否能支援多個 question？
- procedure 是否真的是可重複算法？
- link 的 `why` 是否具體說明下一頁用途？

### 退出條件

- 同一 mechanism 至少能被兩個不同 question / QID 重用的案例存在。
- 同一困惑不產生平行近義頁。
- 所有 semantic links 有 `why`。
- 30-node 人工 review 清單全部有明確狀態。

Phase 0 未通過前，禁止批次擴全 321 題。

---

## P0-D｜Learning Attempt durable lifecycle

**Owner**：Sol
**Implementer**：Luna high

這是 Phase 2 以前的 reliability blocker。目標不是把每次重開同一題都當成同一次 attempt，而是能區分「同一個仍在進行／剛提交但 UI 尚未確認的 attempt」與「使用者真的開始另一輪作答」。

目前 `currentLearningAttemptId` 每次開 modal 都重新產生 UUID；現有 recovery journal 能處理 multi-key 寫入失敗，但不能單靠記憶體 `Map` 解釋 reload 後的 attempt lifecycle。

優先深化現有 `attemptStore.js`，不要另包一層只轉呼叫的 shallow module。最小 interface 應能表達：

```text
beginOrResumeLearningAttempt(context)
submitLearningAttempt(payload)
acknowledgeLearningAttempt(attemptId)
recoverLearningAttempt()
```

durable attempt envelope 至少包含：

```text
attemptId
qid
examFamily
sourceMode
scopeId
state: active | committed | acknowledged
startedAt
committedAt?
fingerprint?
```

規則：

- `scopeId` 代表這一次練習情境；每日練習新增 stable `sessionId`，不要只靠時間字串猜 session identity。
- reload 後只有「qid + sourceMode + scopeId 完全相同且 envelope 尚未終結」才能 resume 同一 attempt。
- 已 `committed` 但未 `acknowledged` 的 envelope 要先告知「上一筆自評已儲存」，避免 crash-after-commit 後使用者誤以為沒寫入而立刻重複評分。
- 已 acknowledged、scope 不同、或明確重新作答時建立新 UUID；不得用 `qid + 日期` 當 attemptId，否則合法的同日重做會被吞掉。
- committed receipt / envelope 與 Recall、SM-2、daily progress 的正式 commit 必須由同一 recovery journal 保護；成功後才更新記憶體 projection。
- receipt / active envelope 是可靠性 metadata，不計入個人弱點、不當作學習歷史；可 bounded retention，且不因清理 receipt 刪除正式學習資料。

### 驗收

- 同頁面連按相同 payload 仍只提交一次。
- 同 attemptId 改 rating / errorType 仍回 `attempt_conflict`。
- 模擬「資料已 commit、UI 尚未 acknowledge 就 reload」後，不會靜默再加一次 Recall／SM-2。
- reload 一個尚未提交的每日練習題，可在同 practice `sessionId` 下 resume attempt。
- 使用者完成後真的重新做同一題，可以產生新 attempt，而不是永遠被舊 receipt 擋住。
- stale active envelope 可安全終止；清理它不改變正式學習紀錄。
- quota / storage write failure 仍 fail closed，且 recovery 後可再次提交。

**退出條件**：Sol 能用 crash-before-commit、crash-after-commit-before-ack、正常重做三組 fixture 清楚證明 attempt identity 不會把「重複提交」和「合法重做」混為一談。

### Phase 0 整體放行條件

Phase 1 只能在 P0-A～P0-D 全部通過後開始。特別是 P0-D 屬於 blocker：若 attempt identity 尚不能跨 reload／crash 正確區分「同一次提交」與「合法重做」，不得先接 Knowledge Issue Event Log、弱點統計或 Knowledge SRS，否則後續所有個人資料都可能建立在重複學習事件上。

---

# Phase 1｜Canonical Graph 與生成管線

## P1-A｜Legacy DAG compatibility adapter

**Owner**：Luna high
**Reviewer**：Sol

目標是在不一次重寫 69-node DAG 的前提下，讓新 canonical graph 可以逐步接管。

### 實作方向

- 黃金樣本節點由 canonical data 生成。
- 尚未遷移的 legacy node 暫時透過明確 compatibility layer 保留。
- 新 mapping 找不到可信節點時回傳 `unknown`，移除「該科第一節點」fallback。
- compatibility layer 必須可量測「還有多少 legacy node 未遷移」。

### 驗收

- 現有 DAG viewer / tracer 不因部分遷移失效。
- golden QID 命中 canonical node。
- 無命中題得到 `unknown`。
- PE/GK 題目不交叉污染。
- legacy coverage 有明確數字，不假裝 100% 已遷移。

---

## P1-B｜Generator：canonical → Website DAG

**Owner**：Luna medium
**Reviewer**：Sol

新增 deterministic generator，例如：

```text
scripts/build_knowledge_graph.py
  → src/data/knowledge-dag.generated.js
```

正式 runtime 不應手工維護一份與 canonical 重複的 prerequisite 資料。

### 驗收

- 同一份 canonical input 重跑輸出 byte-stable 或 canonical-stable。
- generator 不產生 dangling node。
- build_workbench 正式載入生成結果。
- 現有 DAG tests + 新 graph tests 通過。

---

## P1-C｜Generator：canonical → Obsidian

**Owner**：Luna medium
**Reviewer**：Sol

生成目標：

```text
🧠 問題驅動知識庫/
├── 00_主線/
├── 01_電路學/
├── 03_工程數學/
├── 05_電力系統/
└── ...
```

### 生成規則

- 實體檔名使用 stable node ID，例如 `q-ct-dependent-source-rth.md`；中文 title 放 H1 / alias，不用 title 當識別碼。
- frontmatter 保存 stable node ID、type、subject、reviewStatus、`graphRevision`、`nodeRevisionHash`、`generated: true`。
- `question` 頁使用提案固定模板。
- wikilink 旁直接輸出 edge 的 `why`。
- wikilink 以 stable ID 為 target、中文 title 為 display alias，改標題不造成大規模斷鏈。
- 每頁可回科目 mainline。
- 題目只列 QID / deep link，不複製整份題幹與詳解。
- overview 舊筆記保留為總覽入口，不讓它重新成為 canonical source。
- generated note body 產生 deterministic `generatedBodyHash`；重建前若現有檔宣稱是 generated，但 body 已被人工修改而 hash 不符，generator fail closed，不靜默吃掉人工文字。
- 個人心得另放非生成路徑，例如 `📝 個人知識補充/<nodeId>.md`；只透過 node ID 與 generated note 雙鏈，generator 永遠不寫該目錄。
- 若目標檔缺 `generated: true`、node ID 不一致或路徑被非生成檔占用，停止並回報 collision。

### 驗收

- 生成 Markdown 再跑不產生無意義 diff。
- 每個 wikilink 都能解析到現有 generated note。
- 不存在 orphan mainline。
- 30-node 黃金樣本在 Obsidian 中可沿 prerequisite → mechanism → procedure → mainline 導覽。
- 改中文 title 後檔名與 inbound links 維持穩定，只更新顯示文字／alias。
- 人工修改 generated body 的 fixture 會讓 generator fail closed；`📝 個人知識補充/` 內容重建前後 byte-identical。

---

# Phase 2｜題目映射與弱點診斷

## P2-A｜Question links

**Owner**：Luna high
**Reviewer**：Sol

建立 deterministic `question-links.json` 正式接線。每筆至少包含：

```text
qid
nodeIds
confidence
evidence
reviewStatus
```

來源優先序：

```text
人工 reviewed mapping
> 已核准 AI candidate
> 高信心 deterministic rule
> unknown
```

不要再使用「有結果比 unknown 好」的策略。

### 驗收

- 黃金 QID 映射與人工答案一致。
- 低 confidence 不進正式診斷，只進 review queue。
- unknown 不影響題目本身正常作答。
- 映射 evidence 可追溯。

---

## P2-B｜Knowledge Diagnosis engine

**Owner**：Luna high
**Reviewer**：Sol

輸入：

```text
QuestionRecord
+ question-links
+ selfAssessment 1/3/5
+ errorType
+ recall state
```

輸出只需要：

```text
likelyQuestions: 最多 3 個
firstPrerequisiteGap: 最多 1 個
reason: 為什麼推薦
confidence
needsConfirmation: 是否需要使用者確認
```

第一版使用 deterministic rules，不在 runtime 呼叫 LLM。

錯因路由沿用提案：

- 題型辨識錯 → procedure / 適用條件。
- 起手式不會 → question + procedure 第一判斷。
- 公式忘記 → mechanism / 公式來源。
- 計算錯 → 優先重算 procedure，避免亂建概念頁。
- 觀念混淆 → 兩個 mechanism / question 的邊界與反例。

### Sol 驗收

至少用每科黃金樣本建立：

- rating 1 + 起手式不會。
- rating 3 + 公式忘記。
- rating 1 + 觀念混淆。
- rating 1 + 計算錯但沒有知識缺口。
- unknown mapping。

系統不得對最後兩種情況硬造「核心觀念不熟」。

另外必須測低信心情境：系統只能提出 2–3 個候選問題點供使用者選擇，並提供「都不是」；未經確認的低信心候選不得直接計入個人弱點統計。

---

## P2-C｜作答後三個診斷入口

**Owner**：Luna high
**Reviewer**：Sol

只新增：

1. 「我為什麼卡住？」
2. 「先補哪個前提？」
3. 「回到主線」

### UI 原則

- 診斷顯示在完成第④段並自評之後。
- 一次最多 3 個具體困惑。
- 第一個前置缺口只顯示 1 個。
- 每個連結顯示 `why`。
- unknown 時明說目前無可靠診斷，不以 fallback 假裝命中。
- 高信心診斷仍需讓使用者能改選／否定；低信心診斷優先顯示候選選項而非單一結論。
- 不改變既有 attempt transaction 成功／失敗語意。
- post-submit navigation 改成條件式流程：rating=5 且沒有 errorType／無診斷需求時可維持快速前進；rating=1/3、使用者已選 errorType、或 deterministic diagnosis 有候選時，先停在 diagnosis card。
- diagnosis card 必須提供「確認主要問題」、「可選次要問題」、「都不是」、「跳過診斷／下一題」。確認或跳過後才執行原本的 advance action。
- attempt commit 失敗時不得顯示可確認的 diagnosis card；先讓正式學習紀錄成功，才允許 issue event 連到該 `attemptId`。
- 若使用者在 diagnosis card 關閉／離開，題目 attempt 仍保持已成功；issue confirmation 可保持缺省，不得倒推 attempt 失敗。

### 驗收

一題完成後，從自評到確認問題點或跳過不超過 2 次主要操作；確認後可直接「先補這個」或進下一題。browse 純查看不能產生新的學習完成紀錄。

另外建立 UI regression：

- 非每日 due-review 不再在 600ms timer 還沒讓使用者操作診斷卡前自動跳題。
- 每日練習 rating=1/3 時不會由 `dailyPracticeApplyCompletedAttempt()` 立即關 modal 而吃掉診斷步驟。
- rating=5、無 errorType、無診斷候選的 happy path 不被新流程拖慢。

---

## P2-D｜Knowledge Issue Event Log

**Owner**：Luna high
**Reviewer**：Sol

新增獨立於題目 attempt 的 **append-only Knowledge Issue Event Log**。它描述「系統當時提出什麼、使用者最後確認／否定／修正什麼」，並透過 `attemptId` 與原始作答連結。

不要直接保存 `nodeId → count`。正式 localStorage 只保存 versioned event log；「我的弱點」與診斷命中率皆由純函式 projection 重建。為維持既有 PE/GK localStorage 邊界，使用 **每個 examFamily 一個 canonical event-log key**，而不是把 PE/GK events 混在同一 key；跨 family 的弱點總覽只在 projection 階段合併。每個 family 仍只寫一個正式 log key，避免 confirmation 同時更新多個 count cache 而需要另一套 multi-key transaction。若實際容量量測證明超出 localStorage 預算，再保持同一 interface 換 storage adapter，不先導入 IndexedDB。

每個 event 最少包含：

```text
eventId
attemptId
qid
examFamily
rating
errorType
eventType: confirm | correct | none-of-above | skip
primaryKnowledgeNodeId?
secondaryKnowledgeNodeIds[]
customText?
systemTopNodeId?
candidateCount
selectedCandidateRank?
diagnosisConfidence
recordedAt
diagnosisVersion
graphRevisionRef
supersedesEventId?
```

event-log header 另外保存去重後的 `graphRevisions[]`；event 只存 `graphRevisionRef` index。因 node ID 永久保留且 retired / merged metadata 不刪除，歷史事件不需要每筆複製 `nodeRevisionHashes` 或 `nodeLabelSnapshot`。candidate concurrency 才需要 `expectedNodeHashes`，不要把該成本灌進每個學習事件。

規則：

- `confirm` 才能建立正式 node-based 弱點；AI／規則猜測但使用者沒確認的候選不得算個人弱點。診斷品質只保存 top candidate、候選數量與使用者最後選擇 rank，不為 analytics 重複保存完整 candidate payload。
- 一個 attempt 最多一個 `primaryKnowledgeNodeId`；可有少量 secondary issues，但 raw 弱點次數以 attempt 為基本單位，不能選三個就把同一題灌成三倍嚴重。
- secondary issue 另顯示 `secondaryCount`，不加入 primary `rawCount`；後續若證明有學習價值再另定權重，不先暗中加分。
- 使用者改選時 append `correct` event 並用 `supersedesEventId` 指向前一事件，不原地覆寫 audit trail。
- `none-of-above` 可附一段短 `customText`（長度上限 + plain-text normalization），不硬配 node；它進「待分類問題」，並可直接成為 Codex packet 的核心輸入。文字可包含正常中文、數學符號與單位，但永遠只當資料，不當 path / HTML / script。
- 使用者明確按「跳過診斷」時可 append `skip`，保留 system top / candidate count 供診斷品質分析但不計入弱點；單純關頁／瀏覽器中斷而沒有明確決定，不產生任何 decision event。
- node 後來 `merged` 時 projection 可沿 `supersededBy` 聚合到 active node，但 raw event 不改寫；node `split` 時不得自動猜應分到哪一個新 node，維持舊 ID 或進人工 remap queue。
- event 透過 `graphRevisionRef` 保存當時 graph snapshot；node ID 的 lifecycle metadata 永久保留，因此日後改名／merge 仍能解釋歷史事件。
- eventId / attemptId / QID / nodeId / free text 全部有 schema 與長度限制；任意文字不被當成檔案路徑或可執行 markup。
- `knowledgeIssueStore` 依「目前有效 decision」判斷等價重送：同一 attempt 再送完全相同決定回 duplicate/no-op；若先改成別的問題再改回來，才 append 新 correction event。caller 不自行決定是否為 correction。

### Event Store 驗收

- 同一 attempt 重複送同一 confirmation 得到 duplicate/no-op，不 append 第二筆等價事件。
- 使用者改選會留下 correction event；projection 只採最後有效選擇，audit trail 仍完整。
- `none-of-above` + custom text 不建立虛假 knowledge node。
- node merge 後 raw event 不變、projection 能聚合；node split 後不做未經確認的自動歸類。
- localStorage quota failure 不顯示假成功；舊 event log 保持可讀。
- 以代表性 event 大小做容量預估與壓力測試；第一版 release gate 固定測 **5,000 筆 issue events + 現有所有 user stores**。目標是 issue-log serialized payload 約 3 MiB 以下且整體 `setItem` 在目標瀏覽器成功；若失敗，先再減 payload／分離非必要 analytics，仍不足才開 ADR 將 `knowledgeIssueStore` 換成 IndexedDB adapter。不得靜默刪 confirmed history。
- 另測 10,000 筆只作為 headroom 指標；若已接近 quota，要在產品中提供 storage health / export 提示，不宣稱 localStorage 可無限累積。

---

## P2-E｜Weakness Projection 與「我的弱點」

**Owner**：Luna high
**Reviewer**：Sol

建立 pure projection，例如：

```text
buildWeaknessProjection(issueEvents, graph, knowledgeReviews, now)
```

輸出至少區分 **原始事實** 與 **排序建議**：

```text
rawCount
distinctQids
lastSeenAt
ratingDistribution
errorTypeDistribution
PE/GK source distribution
top1Accepted / alternativeAccepted / noneOfAbove / skipped
knowledgeReviewState
priorityScore
priorityVersion
```

`priorityScore` 可以納入近期性、rating 嚴重度、跨不同 QID 重複發生、knowledge SRS 狀態，但 UI 一定同時顯示 rawCount / distinctQids，不把演算法分數偽裝成「你錯了幾次」。公式由 Sol 在黃金樣本上定義並 version；改公式只重建 projection，不改歷史 event。

網站新增「我的弱點」檢視，第一版至少提供：

- 最近 7 天／30 天／全部期間切換。
- 依具體 `knowledgeNodeId` 排序的發生次數。
- 每個問題點的最近發生時間、不同 QID 數、對應粗粒度 `errorType` 分布。
- 點進問題點可看曾發生的 QID、rating、日期與 knowledge SRS 狀態。
- 可從問題點直接進「先補這個」、「做另一題驗證」、「丟給 Codex 深入解析」。
- 統計以個人確認事件為來源，不以 Graph degree、題目熱門度或 AI 猜測次數冒充個人弱點。
- 提供「待分類問題」區，集中 `none-of-above + customText`，可後續丟 Codex 分析。
- 顯示診斷接受率：候選有多少被選中、多少被否定／都不是，讓規則品質可量測。

### 驗收

- 同一 attempt 在 projection 中最多貢獻一次主要問題點。
- 使用者改選問題點後，舊確認不再被 active projection 統計但 audit trail 仍可追溯。
- `none-of-above` 不建立虛假弱點。
- 一個問題點跨 3 個不同 QID 發生時，統計能顯示「3 個不同題目」，而不是只有總次數。
- 清除／匯入 backup 後，弱點統計能由正式紀錄重建，不依賴不可追溯的衍生 cache。
- 只改 priority 公式版本，不改 event log，也能完整重建新排行。
- 系統規則常被使用者否定時，diagnosis acceptance 指標會下降，不能被 raw weakness count 掩蓋。

---

# Phase 3｜Knowledge Node Retrieval / SRS

## P3-A｜知識節點回想資料模型

**Owner**：Sol
**Implementer**：Luna high

先定義 knowledge-node review 與 question review 的邊界。

需要獨立識別：

```text
questionId review
knowledgeNodeId review
```

禁止因「開過 Markdown／看過問題頁」直接建立排程或增加 mastery。

### 最小行為

knowledge node 顯示 retrieval prompt，例如：

> 不看筆記，解釋為什麼含受控源時不能關閉受控源求 Rth，並說出兩種正確求法。

使用者先回答／回想，再揭露，再做 1/3/5 自評。

### 契約

- 沿用既有本地日曆日規則。
- storage schema 與 backup schema 有版本與 migration。
- 題目 SRS 與 knowledge SRS 分開統計。
- 題目 attempt transaction 不被 knowledge review 偷改。
- knowledge review 使用 stable `knowledgeNodeId`，並保存 `nodeRevisionHashAtReview` / `graphRevisionAtReview`；node title 改名不會把排程變成新項目。
- active node 被 `merged` 時，review projection 可遷移到 canonical active target；`split` 時不得自動把舊 mastery 複製到所有新節點，應保留舊狀態並要求一次 retrieval / 人工選擇後再建立新排程。
- review state 只保存排程需要的最小資料；閱讀次數、開頁次數不是 mastery evidence。
- knowledge review 的 attemptId / receipt 與 question attempt 使用不同 namespace，避免同 ID 誤判重複。

---

## P3-B｜Knowledge SRS 實作

**Owner**：Luna high
**Reviewer**：Sol

先只接黃金樣本，不擴全 graph。

### 驗收

- 閱讀頁面不建立排程。
- 明確評分後才建立／更新排程。
- 同一次 knowledge attempt 連點只記一次。
- storage failure 不顯示假成功。
- backup export/import 往返一致。
- question review 與 knowledge review 可分開查詢。
- node rename 後原排程仍存在；merge/split 的 migration 行為符合上面契約。
- 同一 knowledge attempt 在 reload / retry 情境不重複加 repetitions。

---

## P3-C｜Backup / Restore 與 crash recovery 升級

**Owner**：Sol
**Implementer**：Luna high

新增 Knowledge Issue Event Log、Knowledge SRS、attempt reliability metadata 後，backup schema 必須正式升版；版本號由 Sol 依向下相容範圍決定，但不得把新欄位偷偷塞進既有 version 而不更新 validator / tests。

正式 backup 至少包含：

```text
progressByCategory
starredByCategory
question SM-2
question Recall
dailyPractice / mockTimer
manual labels
knowledgeIssueEventsByCategory
knowledgeReviewState
```

active attempt envelope、短期 committed receipt、derived weakness projection、Codex packet cache 屬於可恢復／可重建 metadata，預設不需要進跨裝置 backup；若 Sol 決定納入，必須明確定義 restore 語意，不能混入學習歷史而沒有契約。

目前 `applyUserDataBackup()` 已做到「先整包 validate，再逐 key 寫入，寫入失敗 best-effort rollback」。在 store 數量增加後，補 `BACKUP_IMPORT_RECOVERY` journal：

```text
validated snapshot
  ↓
write import recovery journal (before/after + writtenKeys)
  ↓
逐 key 寫入
  ↓
commit marker
  ↓
同步 memory state
  ↓
clear journal
```

app 初始化或下一次 import 前若看到 pending journal，先 rollback；若看到 committed journal，先完成 memory / metadata reconciliation 再清除。不得在 recovery 未完成時接受新的 learning write。

### 驗收

- 舊支援版本可依既有 migration 規則升到新版；未知未來版本 fail closed。
- replace / merge 對 Knowledge Issue Event Log 有明確語意：同 `eventId` 同 payload 去重，不同 payload 視為 conflict，不以陣列 concat 靜默製造重複事件。
- node 已 retired/merged 的舊 backup 可匯入 raw event，projection 再依目前 lifecycle 解析；未知 node ID 保留成 unresolved queue 或依契約拒絕，不靜默改成其他 node。
- 任一新 store validation 失敗時，所有 store 零修改。
- 模擬第 N 個 key 寫入 throw，所有已寫 key 回復。
- 模擬瀏覽器在 import 中途重啟，下一次初始化可由 journal 回到一致狀態。
- backup export → replace import → export 的正式學習資料 canonical-equivalent。
- PE/GK 題目狀態仍隔離；shared knowledge node 不因來源 family 被複製。

---

# Phase 4｜AI Parser Spec 與擴充流程

## P4-A｜KnowledgePatchCandidate spec

**Owner**：Sol
**Implementer**：Luna high

AI 不直接寫 `nodes.json` 或 Markdown，只產 candidate：

```json
{
  "candidateVersion": 1,
  "candidateId": "...",
  "baseGraphRevision": "...",
  "sourceIssueEventIds": ["..."],
  "qid": "...",
  "intent": "...",
  "likelyQuestions": [],
  "reuse": [],
  "create": [],
  "update": [],
  "questionLinks": [],
  "confidence": 0.0,
  "evidence": [],
  "expectedNodeHashes": {}
}
```

validator / reviewer 再決定是否 merge。

### Candidate gate

至少檢查：

- QID 是否存在。
- reuse node 是否存在。
- `baseGraphRevision` 是否仍等於目前 canonical graph；不同時 candidate 進 rebase/review，不直接 apply。
- update 的 `expectedNodeHashes` 是否仍吻合；被別的修改更新過的 node 不得 lost update。
- create 是否與現有 title / aliases / semantic signature 近義重複。
- prerequisite 是否形成 cycle。
- evidence 是否對應題幹／已驗證題解。
- update 目標若為 reviewed，必須進人工 review。
- confidence 低於 Sol 設定門檻則留 queue。
- candidate schema 不接受任意 filesystem path、輸出檔名、script / HTML 欄位；generator 只從 node ID 決定正式輸出位置。
- ID、title、alias、`why`、evidence、custom text 都有型別與長度上限；渲染 Markdown / HTML 時一律走既有 escape / generator 規則。
- candidate 來源只被視為不可信建議資料；通過 schema 不等於知識內容正確，仍需 evidence / review gate。

### 驗收

用黃金樣本反覆跑 parser，不能每次產生新的近義 node；同一題相同輸入應得到結構上穩定的 patch。另測 stale graph revision、stale node hash、超長文字、非法 path-like payload、試圖修改 reviewed node，全部不得直接污染 canonical graph。

---

## P4-B｜Codex 深入解析 context packet

**Owner**：Luna medium/high
**Reviewer**：Sol

網站不直接呼叫 runtime LLM。對每個已確認弱點提供「丟給 Codex 深入解析」入口，產生可複製的 Markdown 與可機讀 JSON 兩種 context packet。

packet 必須包含足夠資訊讓 Codex 不必重新猜背景：

```text
packetSchemaVersion / packetId
graphRevision
sourceIssueEventIds
使用目標：準備電機技師考試
knowledgeNodeId / 問題標題
本次 qid / 題目 taxonomy
selfAssessment / errorType
此問題點累積次數、不同 QID 數、最近發生時間
最近幾次同 node 的 issue events（含 qid / rating / errorType）
目前 prerequisite / mechanism / procedure
目前 Recall / knowledge SRS 狀態
已驗證題解與 canonical node 的本地引用
明確要求：找真正缺失前提、核心機制、反例、另一題驗證
```

packet 預設只取解決該問題所需的最小歷史：本次 issue event + 少量同 node 近期 issue events + 現有 Recall/SM-2 aggregate + 必要 prerequisite/mechanism/procedure；不預設塞整份個人作答歷史。現有系統並沒有完整 append-only question attempt history，第一版也不為了 context packet 額外建立一套大型 attempt history。產生後先顯示可閱讀 preview，讓使用者自行複製；第一版網站不自動傳送任何內容到外部模型。

若來源是 `none-of-above + customText`，packet 應把該原句放在「使用者描述」區，並把既有 diagnosis 標成未確認，要求 Codex 先定位問題而不是順著錯誤 node 繼續解釋。

預設 Markdown prompt 應要求 Codex：

1. 先判斷目前診斷是否正確，不直接接受既有標籤。
2. 指出最可能缺失的前提。
3. 解釋核心機制與為什麼。
4. 給反例／失效條件。
5. 用另一題或 retrieval prompt 驗證是否真的理解。
6. 若知識圖譜需要修改，另輸出 `KnowledgePatchCandidate`，不可宣稱已直接修改正式資料。

### 驗收

- context packet 不含無關整庫內容，仍足以定位原 QID、弱點與既有知識鏈。
- 相同正式資料生成的 packet 結構穩定。
- 使用者可一鍵複製 Markdown；JSON 可供後續工具流程使用。
- preview 能清楚看到會複製哪些 QID、attempt 摘要與個人文字；取消時沒有外部 side effect。
- unknown／none-of-above 也能產生 packet，但要明確標示「診斷未確認」，要求 Codex 先協助定位問題。
- 不需要 API key、runtime 後端或直接連 Codex 才能完成第一版。

---

## P4-C｜Codex 回傳 candidate 的安全回路

**Owner**：Sol
**Implementer**：Luna high

若使用者把 Codex 的結果帶回工作庫，只接受結構化 `KnowledgePatchCandidate` 進 review queue：

```text
Codex 深入解析
  ↓
KnowledgePatchCandidate
  ↓
schema / revision / duplicate / cycle / QID / evidence validator
  ↓
Sol 或人工 review
  ├─ reject → 保留原因
  └─ approve → canonical graph
```

candidate 可建議：

- reuse 既有節點。
- 新增 question / mechanism / procedure。
- 修正 question-link。
- 補 semantic edge 的 `why`。
- 標記目前診斷其實應為另一個 prerequisite。

### 驗收

- 貼回任意文字不能直接改 graph；只有合法 candidate 能進 queue。
- candidate 想改 reviewed node 時一定需要人工 review。
- reject 不影響既有正式 graph。
- approve 後重新生成 Website DAG / Obsidian，並保留 candidate 來源與 review evidence。
- candidate 基於舊 `baseGraphRevision` 時只進 rebase/review；重新驗證後產生新 candidate revision，不能把舊 patch 強套到新 graph。
- candidate 中任何 path-like 字串都不能決定 repository 寫入位置。

---

## P4-D｜批次擴充優先序

**Owner**：Luna medium/high
**Reviewer**：Sol

只有 Phase 0–3 的黃金樣本使用流程穩定後才開始。

優先序：

```text
個人反覆錯題
> 歷屆高頻 mechanism
> 跨科共用 mechanism
> 低頻單題知識
```

每批最多新增一個可人工完整審查的節點量，建議 20–40 nodes；不以 321 題全覆蓋為目標。

每批都要重新計算：

- mechanism reuse rate。
- near-duplicate rate。
- unknown rate。
- review queue size。
- question-to-node diagnosis acceptance。
- none-of-above rate。
- candidate stale/rebase rate。

若 duplicate rate 或人工 reject rate 明顯上升，停止擴充，回 Sol 調整 parser spec。

每一批除了正向黃金樣本，至少保留一組 **negative controls**：

- 文字相似但核心機制不同。
- 純計算失誤，不應硬造 conceptual weakness。
- 兩個候選都合理，需要使用者確認。
- 資訊不足，正確答案就是 `unknown`。
- legacy keyword 會誤命中的題。

擴充品質以「正確 abstain」與「使用者接受診斷」和正確命中同等重要。

---

# Phase 5｜最終整合驗收

## Sol 最終驗收矩陣

### 資料完整性

- canonical graph 無 duplicate / dangling / cycle。
- 所有正式 question link 的 QID 存在。
- reviewed / candidate / unknown 狀態可區分。
- PE/GK 邊界維持。
- stable node ID / lifecycle 規則成立；rename 不改 ID、merge 可追、split 不亂複製歷史 mastery。
- 每個正式 issue event 可回到 attemptId、QID、當時 graphRevision 與使用者確認狀態。
- 弱點 raw count、priority、diagnosis acceptance 都能只靠正式 event + graph + review state 重建。
- attempt crash/reload、backup import crash 都有 deterministic recovery，不依賴只存在記憶體的成功旗標。

### 生成一致性

- Website DAG 與 Obsidian 都由 canonical data 生成。
- 重建不產生非決定性 diff。
- Obsidian wikilink 無 broken target。
- legacy compatibility coverage 有明確殘量。
- generated note 使用 stable-ID filename；title rename 不斷鏈。
- generated body drift / 非生成路徑 collision 會 fail closed；個人補充筆記重建後不變。
- Website DAG / Obsidian 內含同一 `graphRevision`，可追到同一 canonical snapshot。

### 學習流程

```text
題目 → 四段 → 自評 → 診斷 → 使用者確認問題點
                         ↓
             Issue Event → 我的弱點 projection
                         ↓
              問題頁 → 前置頁 → 回主線
                         ↓
                  Codex 深入解析
                         ↓
              Patch Candidate / 換題驗證
```

完整走通。

- unknown 可以正常存在。
- 看筆記不算完成。
- question SRS 與 knowledge SRS 分離。
- 同 in-flight attempt 冪等，reload/crash 不把重複提交與合法重做混淆。
- storage failure 不假成功。
- 未確認的 AI／規則候選不進正式弱點統計。
- 個人弱點可從 issue event log 重建，不依賴 mutable count cache。
- `none-of-above + customText` 可留待分類，不被強迫映射。
- rating=1/3 的診斷卡不會被原本自動 advance 流程吃掉；掌握題仍可快速前進。
- 任一已確認弱點可產生 Codex context packet。
- context packet 有 preview，預設不含整庫個人歷史，也不自動送網路。
- Codex 回傳內容不能繞過 revision-aware candidate validator 直接污染 canonical graph。
- stale candidate 只能 rebase/review，不能 lost update。
- backup replace/merge/import-crash 後，event log / knowledge SRS / PE-GK state 維持一致。

### 黃金案例

至少實測：

- Per Unit / SLG。
- Thevenin / 受控源。
- 二階 ODE / 線性代數。

每個領域至少一題必須證明：

1. 題目命中正確具體困惑。
2. 可追到真正必要 prerequisite。
3. 多題會匯流到同一 mechanism。
4. procedure 可被另一題重用。
5. 回 mainline 後能看出整體位置。

另外至少實測下列 negative / reliability cases：

1. 純計算錯：不硬造 conceptual weakness。
2. keyword 很像但 mechanism 不同：允許 `unknown` / 使用者否定。
3. `none-of-above`：可留下自述並產生未確認 Codex packet。
4. crash-after-attempt-commit-before-UI-ack：不重複加 Recall / SM-2。
5. candidate 建立後 graph 先被別人修改：舊 candidate 被擋下而非覆蓋新資料。
6. generated Obsidian note 被人工改 body：重建 fail closed，不吞文字。
7. backup import 中途失敗／中斷：下次啟動能恢復一致狀態。

---

## 4. 測試與驗證指令

各批先跑 targeted tests；整合批再跑完整檢核。

最終至少：

```bash
python3 scripts/validate_knowledge_graph.py
python3 scripts/build_knowledge_graph.py
# targeted：attempt lifecycle / issue event / projection / knowledge SRS / backup recovery / candidate revision
python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/verify_slicing_and_links.py
python3 scripts/health_check_codebase.py
git diff --check
```

若本批實際改到 PE/GK 題庫來源，再追加對應 compiler；純 knowledge graph / UI 變更不為了形式重寫題庫 bundle。

驗收報告固定分三欄：

- 已通過自動檢核。
- 仍需人工判定。
- 尚未驗證。

---

## 5. Sol 介入條件

Luna 發生以下任一情況立即停止擴大修改並交 Sol：

- 同一問題連續兩種實作策略失敗。
- schema 無法表達真實案例而需要新增 node/edge type。
- 兩個資料來源互相矛盾。
- 無法判斷 reuse 還是 create。
- migration 可能破壞現有 69-node DAG 使用者功能。
- 需要改 attempt transaction、backup schema 或 PE/GK 邊界。
- validator / generator 報完成但無法用正式 runtime 驗證。
- AI candidate 想修改 reviewed mechanism。
- 弱點統計需要改成不可由 attemptId 冪等重建的資料模型。
- Codex context export 需要送出本機資料到外部服務，而不是只在本機產生可複製 packet。
- localStorage 實測容量在合理練習事件量下不足，且無法先以減 payload / export 解決；此時才評估 IndexedDB adapter / ADR。
- node split 需要自動搬移舊 mastery，但缺乏可證明的一對一語意。
- stale candidate 無法安全 rebase，卻需要直接覆蓋 current reviewed graph。

Sol 介入後只能做三件事之一：

1. 明確修正契約並退回 Luna。
2. 直接完成高風險小範圍變更並交 Luna 驗證。
3. 需求本身存在產品取捨時整理成具體選項交使用者決定。

---

## 6. 明確延後項目

本輪不做：

- 向量資料庫。
- runtime 後端。
- runtime LLM 診斷。
- LLM 自訂 SM-2 間隔。
- 一次生成 321 題全部問題頁。
- 用 graph degree 當學習重要度。
- 直接把 legacy 69 nodes 全部變成 69 篇 Obsidian 文章。
- 自動覆寫 reviewed mechanism。
- 網站直接呼叫 Codex／OpenAI API。
- 把完整個人作答歷史自動傳送到外部模型；第一版只由使用者主動複製／匯出 context packet。
- 預先導入 IndexedDB；只有容量／效能量測證明 localStorage 不足時才透過既有 store interface 換 adapter。
- 自動把 split 前的 knowledge mastery 複製到所有 split 後節點。
- 把 priority score 當成真實錯誤次數；UI 必須保留 raw count / distinct QID。

這些只有在黃金樣本證明現有方案不足時才另開 ADR／提案。

---

## 7. 完成定義

第一版不是「筆記很多」就算完成。必須同時滿足：

- 30-node 黃金圖譜經 Sol 人工審查。
- canonical graph 驗證器可 fail closed。
- node lifecycle、`graphRevision`、`nodeRevisionHash` 契約有測試。
- Website DAG 與 Obsidian 同源生成。
- fallback-to-first-node 已消失。
- generated / personal Obsidian 筆記分離，stable-ID link 與 drift guard 通過。
- durable attempt lifecycle 能處理 crash-before-commit / crash-after-commit-before-ack / 正常重做。
- 三個網站診斷入口正式接線，rating=1/3 不會被 auto-advance 吃掉診斷；無弱點訊號的 rating=5 保持快速流程。
- Knowledge Issue Event Log 的 `confirm / correct / none-of-above / skip` 語意可用，且同 attempt 不重複灌等價事件。
- 自評後 post-submit flow 已取代既有會搶先前進的路徑：有弱點訊號時可完成確認／跳過再進下一題；沒有弱點訊號時仍可快速前進。
- attempt lifecycle 已通過 crash-before-commit、crash-after-commit-before-ack、reload resume 與合法重做測試。
- backup/import 已通過 multi-store validation、寫入失敗 rollback 與 crash-recovery journal 測試。
- Knowledge Issue Event Log 已通過至少 5,000 筆代表性事件 + 現有使用者資料的容量 gate；若不通過，先在既定 store interface 後更換 adapter，不縮減 confirmed history。
- knowledge node rename / merge / split / retire 的歷史事件與 Knowledge SRS 行為有測試，stable ID 不被重用。
- stale `KnowledgePatchCandidate`（`baseGraphRevision` / `expectedNodeHashes` 不符）會 fail closed，不得覆寫較新的 canonical graph。
- 「我的弱點」完全由 projection 生成，可做 7／30／全部期間、QID drill-down、raw count / distinct QID / priority / diagnosis acceptance。
- 至少三類真題能從錯誤追到具體困惑與 prerequisite。
- knowledge-node recall 可獨立排程且閱讀不算完成。
- backup 新版能 round-trip issue events / knowledge SRS，import crash 有 recovery journal。
- AI parser 只能產生 revision-aware patch candidate，不能直接污染正式 graph。
- 已確認弱點與 none-of-above 都能產生可預覽 Codex Markdown／JSON context packet；Codex 回傳只能走 candidate review queue。
- stale candidate、非法 path-like payload、超長／非法欄位、reviewed-node update 都有拒絕或人工 review 測試。
- 正向黃金樣本與 negative controls 都通過，並回報 diagnosis acceptance / none-of-above / unknown rate。
- 全部自動測試與 `git diff --check` 通過。
- 未遷移 legacy nodes、unknown mappings、人工 review queue 均有明確清單。

達到以上條件後，Sol 才把候選版標記為「可交使用者試用」。是否 commit、push、Tag 或發布，由使用者另行授權。
