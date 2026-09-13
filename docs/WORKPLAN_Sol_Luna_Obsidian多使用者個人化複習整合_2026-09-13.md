# Sol／Luna 多使用者 Obsidian 複習整合工作提案

日期：2026-09-13
適用專案：電機工程技師歷屆試題與詳解工作台
上位提案：[Obsidian 多使用者個人化複習整合提案](PROPOSAL_Obsidian多使用者個人化複習整合_2026-09-13.md)
相關既有變更：[問題驅動 Obsidian 知識圖譜工作計劃](WORKPLAN_Sol_Luna_問題驅動Obsidian知識圖譜_2026-09-12.md)

## 0. 任務目標與放行原則

把目前的「題目網站 → 知識圖譜 → Obsidian」流程整理成可供不同使用者各自複習的產品流程：

```text
共用 canonical graph／生成內容
              │
              ├─→ 題庫網站：作答、診斷、題目 SRS、知識節點 SRS
              │
              └─→ 每位使用者自己的 Obsidian Vault
                         └─→ 個人補充與個人錯題脈絡
```

本工作提案的第一版目標是：

1. 使用者能建立、切換與辨識自己的 profile。
2. 不同 profile 的進度、錯因、SRS、attempt 與弱點資料互不混用。
3. 完成一題後，網站能給出有限、可理解的複習路線。
4. 路線能開啟正確的網站節點與使用者指定的 Obsidian Vault 筆記。
5. Obsidian 無法開啟時，仍能複製相對路徑或匯出個人 Markdown，完成複習。
6. 看筆記不會自動增加掌握度或建立 knowledge SRS。

第一版不包含登入、雲端帳號、多端自動同步或網站任意寫入本機 Vault。這些能力只有在本工作提案的第一版閘門通過後才能另開提案。

## 1. Sol 複查後的架構決策

### 1.1 資料分層

| 層 | 唯一責任 | 可由誰修改 |
| --- | --- | --- |
| `data/knowledge/` | canonical nodes、edges、question links、schema | 受審查的程式／資料變更 |
| `src/data/knowledge-dag.generated.js` | 網站執行期生成投影 | generator |
| `🧠 問題驅動知識庫/` | 生成的共同知識頁 | generator；人工編輯需 fail closed |
| `📝 個人知識補充/` | 使用者自己的困惑、推導與複習紀錄 | 使用者或受控個人匯出流程 |
| profile stores | 每位使用者的題目進度、SRS、attempt、診斷 | 該 profile 的網站操作 |

`data/knowledge/` 是知識關係的 source of truth。生成 Markdown、網站 DAG 與題目診斷都不得各自維護另一份前置關係。

### 1.2 多使用者策略

採用兩種明確模式：

- **Independent Vault（預設）**：每位使用者一個 Vault，完整隔離個人筆記；每個 Vault 可安裝相同 graph revision 的生成內容。
- **Shared Reference Vault（可選）**：多人共用 Obsidian Sync Vault，只放共同生成筆記與共同主線；個人資料仍留在各自 profile／Vault。

不把「同一瀏覽器」當成使用者隔離。瀏覽器 profile、網站 profile 與 Obsidian Vault 是三個不同概念，UI 必須清楚顯示目前是哪一個。

### 1.3 Obsidian 整合策略

網站的整合介面只做三件事：

1. 由 `vaultId` 或 `vaultName` 產生正確編碼的 `obsidian://open` URI。
2. 產生 Vault 內相對筆記路徑並提供複製。
3. 匯出經驗證的個人 Markdown／JSON payload，供使用者主動帶入 Obsidian。

自動建立或追加個人筆記屬於第二版本機整合層；該層必須自己驗證輸入，不能被第一版 UI 隱含承諾。

## 2. Agent 分工與共同規則

### 2.1 Sol：契約、取捨與獨立驗收

Sol 的工作不是替 Luna 重做所有程式，而是固定邊界並阻止不安全的捷徑：

- 審查 profile schema、storage key 命名、migration 與 backup 邊界。
- 審查 Obsidian URI 的 Vault 選擇與 path encoding。
- 審查路線卡是否在正確的 recall 階段出現，且不提前洩漏答案。
- 審查 independent Vault 與 shared Vault 是否被產品文字混為一談。
- 獨立執行 negative controls、雙 profile 交叉污染測試與瀏覽器人工驗收。
- 只在所有 blocker 通過後標記「可交使用者試用」。

### 2.2 Luna：調查、實作與證據

Luna 依工作包順序執行，不跨越依賴：

- `Luna medium`：inventory、欄位盤點、測試資料整理、文件與報告。
- `Luna high`：profile store、storage migration、路線卡、URI adapter、整合測試。
- 發生連續兩次失敗、遇到未定義資料語意、需要修改 attempt／backup／PE-GK 邊界或無法驗證 URI 目標時，停止擴大並交 Sol。

### 2.3 每個工作包的固定交付格式

每個工作包完成時，Luna 必須提供一份 Result Packet，包含：

```text
Scope：實際改了哪些檔案與介面
Data：使用了哪些來源、profile、Vault 與 graph revision
Behavior：使用者如何操作、成功與失敗如何顯示
Tests：實際執行的命令與結果
Negative controls：至少一個錯誤或隔離案例
Unverified：仍需人工或外部環境驗證的項目
Next gate：是否符合進入下一工作包的條件
```

禁止只回報「功能完成」或只附測試數字而沒有操作證據。

## 3. 開工前必讀與現況基線

所有 Agent 開工前讀取：

1. `CONTEXT.md`
2. `AGENT-SPEC.md`
3. `AGENT-CODE.md`
4. `docs/PROPOSAL_Obsidian多使用者個人化複習整合_2026-09-13.md`
5. 本文件
6. `docs/WORKPLAN_Sol_Luna_問題驅動Obsidian知識圖譜_2026-09-12.md`
7. `docs/spectra/changes/problem-driven-obsidian-knowledge-graph/specs/` 下與 graph、diagnosis、SRS、backup、generation 相關的 spec

現況基線必須以實際檔案確認，不從本文件猜測：

- 題庫網站是靜態 bundle，沒有登入與 runtime backend。
- 題目、SRS、attempt、診斷與弱點資料目前由瀏覽器端 storage 保存。
- `data/knowledge/` 已有 canonical graph；目前生成報告包含 145 個 nodes、126 條 edges、482 筆題目 links。
- 生成 Obsidian 筆記在 `🧠 問題驅動知識庫/`，個人補充根目錄是 `📝 個人知識補充/`。
- PE／GK 必須維持既有獨立資料與 storage 語意。

若 inventory 與以上基線不同，先更新 Result Packet 與本工作提案中的假設，再由 Sol 決定是否調整範圍。

## 4. Phase 0：契約、inventory 與 migration plan

### P0-A｜現有 storage inventory

**Owner：Luna medium**
**Reviewer：Sol**

#### 操作要求

1. 搜尋所有 `localStorage.getItem`、`setItem`、`removeItem`、backup export/import 與直接使用 storage key 的程式碼。
2. 建立表格，逐筆記錄：base key、資料用途、PE/GK 邊界、是否包含個人資料、讀寫模組、backup 是否包含、是否能在 runtime 重新 render。
3. 特別標出 `attempt`、`recovery journal`、`issue events`、`knowledge reviews`、題目進度、收藏、daily practice、mock timer 與 manual labels。
4. 找出不應被 profile namespace 包住的共用資料，例如 canonical graph、題庫 bundle 與 build-time source。
5. 盤點已有舊資料，確認沒有任何程式在讀取時靜默覆蓋壞資料。

#### 交付

```text
data/profile-storage-inventory.json
reports/profile-storage-inventory.md
```

#### 驗證

- inventory 覆蓋所有 runtime storage 操作；可由 `rg` 結果逐項回溯。
- 每個個人資料 key 都有分類、migration 策略與 backup 策略。
- PE、GK、共用 graph 三者沒有誤分類。
- Sol 抽查至少 10 個 key，檔案位置、讀寫方向與報告一致。

#### 完成條件

所有會影響學習結果的 storage key 都能回答「屬於哪個 profile、哪個考別、由哪個 store 負責、如何備份與還原」。

### P0-B｜Profile schema 與公開介面

**Owner：Sol 定義；Luna high 實作**
**Reviewer：Sol**

#### 必須固定的 schema

新增 profile metadata，至少包含：

```json
{
  "schemaVersion": "profiles.v1",
  "activeProfileId": "profile-local",
  "profiles": {
    "profile-local": {
      "profileId": "profile-local",
      "displayName": "此裝置使用者",
      "obsidianVaultId": null,
      "obsidianVaultName": null,
      "graphRevision": null,
      "createdAt": "2026-09-13T00:00:00.000Z",
      "updatedAt": "2026-09-13T00:00:00.000Z"
    }
  }
}
```

欄位規則：

- `profileId` 是穩定內部識別碼，不使用顯示名稱當 key。
- `displayName` 只用於 UI，不可直接拼入 HTML、URI 或 storage key。
- `obsidianVaultId` 優先於 `obsidianVaultName`；兩者都可為空。
- `graphRevision` 只記錄使用者最後確認的內容版本，不改變 canonical graph。
- timestamp 必須是可驗證的 ISO timestamp。
- profile ID、Vault 設定與顯示名稱都要有長度、字元與 HTML escaping 限制。

#### 建議公開介面

建立小而深的 profile module，至少提供：

```text
readProfiles()
getActiveProfile()
createProfile(input)
switchProfile(profileId)
updateProfileSettings(profileId, patch)
profileStorageKey(baseKey, profileId)
```

各 store 只透過 `profileStorageKey()` 取得個人資料 key，不在各處自行拼接 namespace。

#### 驗證

- schema fixture：正常 profile、空 profile、重複 ID、非法 ID、過長名稱、錯誤 timestamp、錯誤 Vault ID。
- profile switch 後，所有依賴 store 的 view 都能重新 render。
- 不存在的 profile 不可切換，且不得改變 active profile。
- `profileStorageKey()` 對同一 base key 與兩個 profile 產生不同 key；PE/GK base key 仍分開。

#### P0 閘門

Sol 必須明確確認 schema、key 規則與 backup 邊界後，才可開始改寫現有 stores。

### P0-C｜Obsidian Vault identity contract

**Owner：Sol 定義；Luna medium 整理**
**Reviewer：Sol**

#### 操作要求

1. 定義 Vault identity 優先序：`vaultId` → `vaultName` → 尚未設定。
2. 所有筆記連結只使用 Vault 內相對路徑，例如：

```text
🧠 問題驅動知識庫/05_電力系統/ps-symmetrical-components.md
```

3. 絕對路徑只能在本機診斷或人工設定畫面短暫顯示，不得寫進 canonical graph、生成內容或可分享 payload。
4. URI 的 `vault`、`file`、`path`、`query` 全部使用標準 URI encoding。
5. 未設定 Vault 時，UI 顯示「請先設定 Obsidian Vault」，並保留網站路線與複製相對路徑能力。

#### 驗證

- `vaultId` 含特殊字元、Vault 名稱含空格與中文字時，URI parse 後值能完整還原。
- note path 含空格、斜線與中文時不產生截斷 query。
- profile A 與 profile B 設定不同 Vault 時，各自產生不同 URI。
- 缺少 Vault、URI 被阻擋或檔案不存在時，網站不顯示假成功。

#### 完成條件

所有 Obsidian 連結都能追溯到「哪個 profile、哪個 Vault identity、哪個相對 note path、哪個 graph revision」。

## 5. Phase 1：Profile namespace 與個人資料隔離

### P1-A｜建立 profile store

**Owner：Luna high**
**Reviewer：Sol**

#### 操作要求

1. 新增 `src/state/profileStore.js`，並在 `scripts/build_workbench.py` 的 bundle 順序中放在所有依賴它的 store 之前。
2. 第一次啟動時建立單一 `profile-local`，只在沒有 profile metadata 時建立。
3. 提供 UI 可建立 profile、切換 profile、修改顯示名稱與 Vault 設定。
4. Profile 切換後關閉當前暫存 modal、清空 view-level current question／current recall，重新載入所有 profile stores，再重畫統計與頁面。
5. 切換 profile 不得改變 canonical graph、題庫 bundle、generated notes 或其他 profile 的 storage。
6. 若 profile metadata 損壞，顯示可恢復錯誤；不得覆蓋未知內容或把其他 profile 當成空資料。

#### 建議 UI 操作

```text
目前使用者：此裝置使用者 ▾
  ├─ 新增使用者
  ├─ 切換使用者
  └─ 設定 Obsidian Vault
```

UI 要用「使用者」與「Obsidian Vault」兩個不同欄位，避免使用者以為切換 Vault 就會切換網站作答資料。

#### 驗證

- 建立 A、B 兩個 profile，確認 metadata 有不同 profileId。
- 在 A 寫入一筆 PE 進度、一筆 GK 進度、一筆 issue、一筆 knowledge review。
- 切到 B，確認四筆資料均不可見且統計為 B 的值。
- 在 B 寫入不同資料，再切回 A，確認 A 資料仍完整。
- 重新載入頁面，active profile 與兩組資料仍正確。

### P1-B｜既有 storage migration

**Owner：Luna high**
**Reviewer：Sol**

#### 操作要求

1. 先讀取既有未命名 storage keys，通過現有 validator 後才可視為可遷移資料。
2. 將既有資料放入明確的 `profile-local`，保留來源 key，直到 migration 完成並驗證成功。
3. migration 必須是可重跑且冪等；重跑不能複製事件、延後 SRS 日期或覆蓋較新的 profile data。
4. 任何一個 store 寫入失敗時，保留 migration journal，下一次啟動可以恢復或阻止新的 migration。
5. 損壞或未知 shape 的舊資料要進 error state，不得當成空資料覆蓋。
6. migration 完成後才允許新程式只讀 namespaced keys；舊 key 的清理另列明確 maintenance task，不在本階段刪除。

#### 驗證

- 既有 PE/GK 進度、收藏、題目 SRS、daily practice、mock timer、manual labels、attempt、issue 與 knowledge review 都能 round-trip。
- migration 中途故意讓一個 key 寫入失敗，確認 journal 可被下次啟動處理。
- 連續執行 migration 兩次，輸出與事件數完全一致。
- 舊資料含未知題號、壞 JSON、壞日期與跨考別資料時，系統 fail closed 且不清空原始 key。
- 現有 backup import/export 測試全部仍通過。

### P1-C｜所有個人 store 接入 namespace

**Owner：Luna high**
**Reviewer：Sol**

#### 操作要求

依 P0 inventory 逐項接線，至少包含：

- 題目 progress。
- starred。
- 題目 SM-2。
- recall state。
- daily practice。
- mock exam timer。
- attempt envelope 與 recovery journal。
- knowledge issue events。
- knowledge reviews。
- manual topic labels。
- backup metadata。

所有 store 必須保留現有公開行為：

- 題目與 knowledge SRS 分離。
- PE/GK 分離。
- attempt transaction 的 commit、rollback、recovery 與 idempotency 不變。
- storage failure 不顯示假成功。
- projection 由事件重算，不以 UI 暫存值當 source of truth。

#### 驗證

- 用 fake storage 設定 A、B，逐一讀寫上述 stores，確認底層 key 不交叉。
- 現有所有 store 單元測試與 backup／recovery 測試通過。
- 同一 `attemptId` 在 A 重試不會出現在 B，也不會在 A 重複灌事件。
- 切換 profile 後再開啟複習中心、弱點頁、圖譜頁與統計頁，畫面只反映 active profile。

#### P1 放行條件

在雙 profile 的自動測試與 migration 測試通過前，不得開始宣稱「多使用者可並行使用」。

## 6. Phase 2：題目到複習路線

### P2-A｜路線 resolver

**Owner：Luna high**
**Reviewer：Sol**

#### 操作要求

建立單一 resolver，輸入 `qid` 與 canonical graph，輸出有限、可解釋的路線資料：

```json
{
  "qid": "EE-109-05-4",
  "examFamily": "PE",
  "targetNode": {
    "nodeId": "ps-symmetrical-components",
    "title": "對稱分量法 (正序、負序、零序網)"
  },
  "firstPrerequisite": null,
  "chain": [],
  "notePath": "🧠 問題驅動知識庫/05_電力系統/ps-symmetrical-components.md",
  "confidence": 0.92,
  "status": "resolved"
}
```

解析規則：

- 先使用 `question-links.json` 的 exam-family scoped link。
- 只沿 approved prerequisite edges 追蹤。
- 第一個前置缺口最多回傳一個。
- 路線最多呈現一個 target 加有限前置節點，避免把完整 DAG 倒給使用者。
- `unknown`、低信心或跨 PE/GK link 時回傳明確狀態，不猜測、不 fallback 到科目第一節點。
- `reason`／`why` 必須能回答「下一頁會解決什麼」。

#### 驗證

- `EE-109-05-4` 命中 `ps-symmetrical-components`，且 exam family 是 PE。
- 一題沒有可靠 mapping 時回傳 `unknown`，不產生假節點。
- 同一 node 被多題使用時 resolver 輸出相同 nodeId，不複製節點。
- prerequisite graph 有 cycle 或 edge 未 approved 時，resolver 不沿該 edge 產生路線。
- GK 題不能命中 PE-only node；PE 題不能命中 GK-only node。

### P2-B｜題目完成後的路線卡

**Owner：Luna high**
**Reviewer：Sol**

#### 操作要求

在題目完成、第四段揭露與自評／診斷資料可用後顯示：

```text
🧭 建議複習路線
1. 先回想本題使用的節點
2. 查看你可能卡住的前置觀念
3. 需要時開啟 Obsidian 問題頁
4. 回到原題重做
```

操作按鈕固定為：

- `🧠 開始節點回想`。
- `🕸️ 在網站查看路線`。
- `🗒️ 開啟 Obsidian 筆記`。
- `📋 複製筆記位置`。

行為規則：

- active recall 尚未到第四段時，不顯示完整解答或路線中的答案內容。
- browse 純查看不產生 attempt、issue event 或 SRS。
- `開始節點回想` 必須先建立 knowledge recall session，評分成功後才建立 knowledge SRS。
- unknown mapping 顯示「目前沒有可靠診斷」，仍保留回題與網站基本詳解。
- 路線卡只顯示有限節點與清楚的下一步，不取代題目詳解或 Obsidian。

#### 驗證

- 四段蓋牌測試證明答案與路線卡不會在前置階段洩漏。
- 正常完成一題後，從自評到路線卡不超過兩次主要操作即可開始補強。
- browse 開啟路線後，attempt／issue／SRS 的 snapshot 不變。
- rating=1、rating=3 有診斷時不會被 auto-advance 吃掉；rating=5 且無弱點訊號仍可快速前進。
- 路線卡中的 target、prerequisite、note path 都能追溯到同一 graph revision。

### P2-C｜知識圖譜與弱點頁的快捷入口

**Owner：Luna medium/high**
**Reviewer：Sol**

#### 操作要求

知識圖譜：

- 到期節點排在前面。
- 每個節點提供 `開始回想`、`開啟 Obsidian`、`複製路徑`。
- 從題目路線進入時，切到正確考科並聚焦 target node。
- current recall panel 顯示節點標題、目前考別與回想操作，不只顯示內部 nodeId。

我的弱點：

- 每個主要問題／前置缺口提供 `查看題目`、`開始回想`、`查看網站路線`、`開啟 Obsidian`。
- 保留 raw count、distinct QID、確認率、時間範圍與事件 drill-down。
- next action 與實際可按的按鈕一致；不顯示無效或沒有 handler 的操作。

#### 驗證

- 從題目路線進入圖譜後，畫面在正確 subject filter 與 target node。
- due node 先出現；閱讀節點不會被標成 reviewed。
- 弱點頁的事件 QID 可打開原題，node action 可開始正確的 knowledge recall。
- 無事件、unknown、retired node 與 secondary prerequisite 都有可理解的空狀態。

## 7. Phase 3：Obsidian URI、匯出與失敗後備

### P3-A｜Deep link adapter

**Owner：Luna high**
**Reviewer：Sol**

#### 建議介面

```text
getKnowledgeNotePath(nodeId, graph)
buildObsidianOpenUri(profile, notePath)
openKnowledgeNoteInObsidian(profile, notePath)
copyKnowledgeNotePath(notePath)
```

#### 操作要求

1. `getKnowledgeNotePath()` 只回傳 Vault 內相對路徑。
2. `buildObsidianOpenUri()` 優先使用 `vaultId`，沒有才使用 `vaultName`。
3. `openKnowledgeNoteInObsidian()` 是 best-effort；呼叫後不能直接顯示「已成功寫入」或「已保存」。
4. 開啟按鈕旁始終保留複製相對路徑後備。
5. clipboard 不可用時，顯示可選取的純文字路徑。
6. 不把本機絕對路徑寫入 `data/knowledge/`、generated note 或可分享 backup。

#### 驗證

- 以 Vault ID、Vault name、空 Vault 設定各跑一次。
- URI 產生後用 parser 驗證 `vault`／`file` 值，確認中文、空格與 `/` 正確編碼。
- mock `window.location`、`window.open`、clipboard 成功與失敗情境。
- 按開啟後不會修改 profile learning data、issue events 或 SRS。
- 未安裝 Obsidian 的環境仍能完成網站路線與複製路徑。

### P3-B｜個人 Markdown／JSON 匯出

**Owner：Luna medium/high**
**Reviewer：Sol**

#### 操作要求

匯出資料至少包含：

```text
profileId
examFamily
qid
nodeId
graphRevision
recordedAt
diagnosis outcome
user note placeholder
source note path
```

匯出內容必須：

- 明確標示這是個人補充草稿。
- 只引用 QID、nodeId 與相對 path，不複製未授權的完整題庫內容。
- 不把其他 profile 的資料混入。
- 不把未確認診斷寫成事實；`unknown`、`none-of-above` 與 pending 狀態要保留。
- 可由使用者主動複製或下載，再放入 `📝 個人知識補充/`。

#### 驗證

- A、B profile 各匯出一次，檔案內容不交叉。
- 匯出再匯入既有個人筆記流程不修改 canonical generated note。
- unknown 與 none-of-above 匯出後仍保持未確認語意。
- path-like 欄位、過長文字與 HTML／Markdown 特殊字元經過 escaping 或 validator。

### P3-C｜第二版本機寫入層的界線

**Owner：Sol 先審查；本輪不實作**

只有在 P0–P3-B 全部通過後，才可另開 ADR 評估：

- Obsidian URI `new`／`append`。
- 本機 CLI 或本機 helper。
- Obsidian plugin。

任何第二版方案都必須：

- 明確指定輸入 schema。
- 驗證 `profileId`、`vaultId`、relative path、nodeId、QID 與 graph revision。
- 防止 `../`、絕對路徑與跨 Vault 寫入。
- 只寫個人資料夾或新增個人檔案。
- 對 generated note、reviewed canonical node 與其他 profile fail closed。
- 提供寫入前 preview、成功／失敗回報與 recovery。

## 8. Phase 4：測試矩陣與人工驗收

### 8.1 Targeted tests

新增或更新測試：

```text
tests/test_profile_store.py
tests/test_profile_storage_namespace.py
tests/test_profile_migration.py
tests/test_knowledge_review_guide.py
tests/test_obsidian_deep_links.py
tests/test_personal_learning_export.py
```

各測試至少覆蓋：

- schema 正常與壞資料。
- profile A/B 隔離。
- migration 冪等、journal、寫入失敗與壞資料保留。
- PE/GK 隔離。
- question → node → prerequisite → note path 的可追溯性。
- unknown／none-of-above／low confidence。
- no auto SRS on read/open。
- Obsidian URI encoding 與 fallback。
- generated／personal note 邊界。

### 8.2 瀏覽器人工驗收腳本

在本機建置後，Sol 或指定 reviewer 依以下步驟操作：

1. 開啟工作台，確認顯示預設 profile。
2. 建立「使用者 A」與「使用者 B」。
3. 為 A 設定 Vault A 的名稱或 ID；為 B 設定 Vault B。
4. 切到 A，開啟 `EE-109-05-4`，完成四段回想與自評。
5. 確認路線卡顯示 `對稱分量法 (正序、負序、零序網)`，且有四個明確操作。
6. 點 `在網站查看路線`，確認圖譜聚焦正確節點。
7. 點 `複製筆記位置`，確認得到相對 path，不含 `/Users/` 或其他絕對路徑。
8. 不點擊外部 Obsidian URI 也要確認網站流程可完成；若環境有 Obsidian，再確認開到 Vault A。
9. 切到 B，確認 A 的進度、弱點與 SRS 不出現；開啟同一 QID 時使用 Vault B 的 URI。
10. 重新載入頁面，確認 B 仍是 active profile；切回 A 後資料仍一致。
11. 開啟「我的弱點」與「複習中心」，確認兩頁都只顯示目前 profile。
12. 匯出 A、B 的個人 Markdown，確認檔案內容、profileId 與 Vault path 各自正確。

### 8.3 Negative controls

以下任何一項失敗都不得放行：

1. A 的 issue event 出現在 B。
2. A 的 knowledge SRS 到期項目出現在 B。
3. Vault name 含 `&`、空格或中文時 URI 被截斷。
4. 未設定 Vault 卻顯示「已開啟 Obsidian」。
5. 打開筆記後自動增加 SRS、mastery 或 issue event。
6. unknown mapping 被補成該科第一個節點。
7. 路線卡在第四段以前洩漏完整答案。
8. generated note 被匯出流程或個人操作覆寫。
9. migration 寫入失敗後原始 key 被清空。
10. PE 題目產生 GK node path，或 GK 題目使用 PE profile data。
11. profile 顯示名稱中的 HTML／URI 特殊字元造成注入或破壞 markup。
12. 同一題重做造成等價 issue event 或 knowledge review 重複寫入。

## 9. 建置與驗證命令

### 9.1 每個工作包完成時

```bash
python3 -m unittest tests.test_profile_store
python3 -m unittest tests.test_profile_storage_namespace
python3 -m unittest tests.test_profile_migration
python3 -m unittest tests.test_knowledge_review_guide
python3 -m unittest tests.test_obsidian_deep_links
python3 -m unittest tests.test_personal_learning_export
git diff --check
```

若某個測試檔尚未建立，Result Packet 必須標示「尚未建立」，不能把命令省略後回報全數通過。

### 9.2 整合批

```bash
python3 scripts/validate_knowledge_graph.py
python3 scripts/build_knowledge_graph.py
python3 scripts/build_workbench.py
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/verify_slicing_and_links.py
python3 scripts/health_check_codebase.py
git diff --check
```

純 UI／profile 變更不為了形式重編 PE／GK 題庫來源；若改動題庫來源，才追加對應 compiler。

### 9.3 驗收報告固定格式

每次 Sol review 報告分成三欄：

| 已通過自動檢核 | 仍需人工判定 | 尚未驗證 |
| --- | --- | --- |
| 命令、測試數量、產物與 snapshot | 瀏覽器、Obsidian 是否實際接到正確 Vault、操作時間 | 尚未建立或無法在目前環境驗證的整合層 |

健康分數、測試通過數或 generator 輸出數量都不能單獨取代人工驗收。

## 10. Phase gates

### Gate 0：契約放行

必須有：

- storage inventory。
- profile schema。
- profile key namespace 規則。
- migration journal 與 rollback 策略。
- Vault identity 與 URI encoding 規則。

未通過時，不得改寫所有 store。

### Gate 1：資料隔離放行

必須有：

- A/B profile 自動隔離測試。
- migration 冪等與失敗測試。
- backup／recovery／PE-GK 現有測試全通過。
- profile switch 後所有主要頁面重新 render。

未通過時，不得宣稱多使用者可並行使用，也不得做自動 Obsidian 寫入。

### Gate 2：複習路線放行

必須有：

- QID → node → prerequisite → note path 可追溯。
- unknown／low confidence fail closed。
- 路線卡不提前洩漏答案。
- browse 不改 learning data。
- knowledge recall 只有明確評分才進 SRS。

### Gate 3：Obsidian 連結放行

必須有：

- Vault ID／名稱正確優先序。
- 中文、空格、特殊字元 URI 測試。
- 開啟失敗與 clipboard 失敗後備。
- profile A/B 不會開到彼此 Vault。
- 匯出內容不含其他 profile 與絕對路徑。

### Gate 4：試用放行

必須有：

- targeted tests、完整測試、HTML／JS 語法、slicing／links、health check 與 diff check。
- 瀏覽器人工腳本完成。
- 所有 negative controls 通過。
- generated／personal note drift guard 通過。
- 尚未驗證的外部 Obsidian 行為與人工 review queue 有明確清單。

## 11. Sol 介入條件

Luna 遇到下列任一情況，停止當前工作包並交 Sol：

- 同一隔離問題連續兩種策略失敗。
- 需要讓不同 profile 共用一個 personal store 才能完成需求。
- migration 可能刪除或覆蓋未驗證的舊資料。
- 需要變更 attempt transaction、backup schema、PE/GK 邊界或 SRS 語意。
- 不清楚某個節點應 reuse、create、unknown 或 retired successor。
- URI 只能靠絕對路徑才能開啟，或無法可靠判斷目標 Vault。
- 需要使用檔案系統權限、外部服務、帳號、付費 Sync 或傳送使用者資料。
- generator 或 UI 報完成，但無法在正式 runtime 或瀏覽器中確認結果。
- 需要直接覆寫 generated note、reviewed node 或別人的 profile。

Sol 介入後只能：

1. 修正契約並退回 Luna。
2. 完成高風險的小範圍變更並交 Luna 驗證。
3. 把產品取捨整理成具體選項，交由使用者決定。

## 12. 明確延後項目

本工作提案完成前不做：

- 登入、帳號、雲端個人同步與 runtime backend。
- 把所有人個人資料放在一份共用 Vault。
- 把 Obsidian Sync 當成同檔即時協同編輯工具。
- 網站直接任意讀寫 `/Users/...` 或其他本機絕對路徑。
- 沒有 preview、validator、recovery 的自動 Markdown 寫入。
- runtime LLM 診斷或把完整個人歷史自動送出本機。
- 用「看過筆記」推定掌握或自動建立 SRS。
- 用 graph degree 代替個人錯誤證據決定複習優先度。

## 13. 完成定義

本工作提案只有在以下條件全部滿足時才算完成：

- profile schema、storage inventory、migration plan 與 Vault identity contract 經 Sol 審查。
- A/B profile 在同一瀏覽器 profile 下的 progress、starred、SRS、attempt、issues、knowledge reviews、daily practice、mock timer、manual labels 與 backup metadata 不互相污染。
- migration 可重跑、可恢復、失敗不清空來源。
- profile switch、reload、backup export/import 後資料仍一致。
- question → knowledge node → prerequisite → Obsidian note path 可追溯，PE/GK 不交叉。
- 路線卡在正確的 reveal／assessment 時點顯示，browse 不改 learning data。
- unknown／low confidence／none-of-above 保持未確認語意，不 fallback 假裝命中。
- knowledge SRS 只由明確 node recall rating 建立或更新。
- Obsidian URI 以 Vault ID 優先、編碼正確、失敗有複製路徑後備。
- 匯出內容只屬於目前 profile，且不含本機絕對路徑或其他使用者資料。
- generated notes 與 personal notes 分離，generator drift guard 與既有 canonical graph 驗證通過。
- 所有 targeted tests、完整測試、HTML／JS 語法、slicing／links、health check 與 `git diff --check` 通過。
- 瀏覽器人工腳本與 negative controls 完成。
- 仍需 Obsidian 實機、Sync 訂閱或使用者決定的項目列在「尚未驗證」與「延後項目」，沒有被誤報成已完成。

Sol 通過 Gate 4 後，才可把版本標記為「可交使用者試用」。commit、push、Tag、公開發布或啟用付費／外部服務，仍需使用者另行授權。
