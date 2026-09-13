# 問題驅動 Obsidian 知識圖譜整合提案

日期：2026-09-12
適用專案：電機工程技師歷屆試題與詳解工作台

## 1. 結論

這個方向可行，而且適合直接建立在目前工作庫上，不需要重做題庫網站或新增執行期後端。

目前專案已經具備四個關鍵基礎：

1. 321 題 PE 與 161 筆 GK 的穩定 QID、題解、來源與 taxonomy。
2. 69 個節點的 `KNOWLEDGE_DAG` 與前置關係。
3. 四段蓋牌、Recall Level、SM-2、錯因、自評與單一 attempt transaction。
4. 已存在的 Obsidian Vault、核心考點知識庫與錯題筆記。

真正缺的不是「再做一套 Obsidian 筆記」，而是把現有的 **題庫 → DAG → 錯因 → SRS → Obsidian** 接成同一個問題驅動知識模型。

目前 `🧠 核心考點知識庫/` 只有 14 篇核心筆記，而且這 14 篇內部目前沒有 Obsidian wikilink；內容主要是章節式公式與 SOP。另一方面，`knowledge-dag.js` 已有 69 個節點，但題目對節點的映射仍主要靠文字關鍵字，無命中時甚至會退回該科第一個節點。這兩件事正是目前最需要修正的地方：**網站知道一些 prerequisite，Obsidian 知道一些章節，但兩者都還不知道「考生為什麼會卡住」。**

建議目標不是建立更多章節筆記，而是建立：

> 大量具體困惑 → 少量核心機制 → 題型／算法 → 真實考題 → 作答紀錄與複習排程

並且讓網站與 Obsidian 共用同一份 canonical knowledge graph。

## 2. 為什麼值得做

這個設計與目前已採用的四段蓋牌、Recall 與 SM-2 是互補關係。

- Retrieval practice 對延遲記憶通常優於單純重讀，因此目前「先作答、再揭露」的方向應保留，而 Obsidian 不應變成先看答案的入口。參考：Roediger & Karpicke, *Test-enhanced learning*（2006），PubMed：https://pubmed.ncbi.nlm.nih.gov/16507066/
- 測驗本身除了評量，也能強化之後的提取；因此知識圖譜應服務「下一次如何重新想出來」，而不是只服務閱讀。參考：Roediger & Karpicke, *The Power of Testing Memory*（2006），PubMed：https://pubmed.ncbi.nlm.nih.gov/26151629/
- 對算法題而言，只有記住完整 worked solution 不夠；把「為什麼這一步成立、什麼前提缺失、何時失效」獨立出來，才能讓不同題目的共同機制匯流，而不是每題重新記一份解法。

因此 Obsidian 的定位應改成：

> **概念診斷與推理路徑庫**，不是第二個題庫網站，也不是電子版講義。

## 3. 現況問題

### 3.1 核心考點粒度太大

目前核心筆記例如「直流電路與戴維寧諾頓等效」、「標么系統與對稱成分故障分析」，一頁同時放定義、公式、SOP、年份。

這適合考前總覽，但不適合回答：

- 為什麼含受控源時不能直接關閉電源求 `Rth`？
- 為什麼 PU 的 Base Voltage 要跟變壓器匝數比一起變？
- 為什麼 SLG 故障的三個序網要串聯？
- 為什麼二階 ODE 重根會多一個 `x`？

這些才是實際刷題時會卡住的「完整困惑」。

### 3.2 DAG 是程式資料，不是學習內容

`KNOWLEDGE_DAG` 已經有 `prereqs`、公式與陷阱，但它目前只能說：

> `ps-unsymmetrical-faults` 需要先懂 `ps-symmetrical-components`

它還不能說：

> 你這題錯在「不知道為什麼零序網路取決於接地路徑」，所以應先看哪一頁，以及看完後能解掉什麼。

### 3.3 題目映射不夠可信

目前 `mapQuestionToDagNodes()` 主要靠關鍵字命中；沒有命中時會 fallback 到該科第一個節點。這對導覽尚可，但若拿來自動產生個人弱點、SRS 或 AI 知識鏈，會造成假關聯。

新的知識層必須允許：

- `unknown`：寧可不判，也不要亂連。
- `confidence`：自動映射與人工／AI 確認要能區分。
- `evidence`：為什麼這題連到這個知識節點。

### 3.4 網站、DAG、Obsidian 可能逐漸分叉

如果直接讓 AI 寫 Markdown，同時又人工維護 `knowledge-dag.js`，久了會出現：

- Obsidian 有節點但網站沒有。
- 網站 prereq 已改，Obsidian 還是舊鏈。
- 同一概念出現三個近義頁。
- AI 每題都重寫「Per Unit」而不是連到既有核心。

所以必須先解決 source of truth。

## 4. 建議的知識模型

新增 canonical 資料層：

```text
data/knowledge/
├── nodes.json
├── edges.json
├── question-links.json
└── schema.json
```

由這份資料生成：

```text
data/knowledge/*
      │
      ├─> src/data/knowledge-dag.generated.js   → 題庫網站
      │
      └─> 🧠 問題驅動知識庫/*.md               → Obsidian
```

不要讓 Markdown 或 JS 單獨成為另一份真相。

### 4.1 節點只保留四種

避免分類過多，先用四種就夠：

| type | 用途 | 範例 |
| --- | --- | --- |
| `question` | 一頁解一個完整困惑 | 為什麼含受控源時不能直接關源求 Rth？ |
| `mechanism` | 多個疑問最後匯流的核心機制 | 線性電路端口等效的本質 |
| `procedure` | 可重複套用的算法／判斷流程 | 含受控源 Thevenin 求解流程 |
| `mainline` | 一科的完整主線 | 電路學主線 |

考古題本身不必複製成知識頁，直接用穩定 QID 連回既有 QuestionRecord。

### 4.2 每個節點的最小 schema

```json
{
  "id": "q-ct-dependent-source-rth",
  "type": "question",
  "subjectId": "01",
  "title": "為什麼含受控源時不能直接關閉所有電源求 Rth？",
  "goal": "理解受控源仍受端口變數控制，因此不能被關閉。",
  "prerequisites": ["m-linear-port-model"],
  "resolves": ["misconception-dependent-source-off"],
  "mechanisms": ["m-thevenin-one-port-equivalence"],
  "procedures": ["p-thevenin-test-source"],
  "counterexamples": ["僅含獨立源時可關源求等效阻抗"],
  "questionIds": ["EE-109-01-1"],
  "confidence": "reviewed"
}
```

其中真正重要的是 `prerequisites / mechanisms / procedures / questionIds`，因為這四組關係可以同時支援 Obsidian、網站與弱點追蹤。

## 5. 每頁固定格式

`question` 頁固定使用同一套解析模板：

```markdown
# 為什麼含受控源時不能直接關閉所有電源求 Rth？

## 我真正卡住的是什麼
...

## 這頁要解決什麼
...

## 缺失的前提
→ [[線性一埠網路為什麼可以被兩個端口量描述？]]
這頁會補上「Thevenin 等效到底在等效什麼」。

## 核心機制
→ [[Thevenin 的本質是端口 V-I 關係等效]]

## 怎麼做
...

## 為什麼這樣做
...

## 反例／失效條件
...

## 在題目裡怎麼辨認
- EE-109-01-1

## 常見錯法
...

## 下一個問題
→ [[為什麼測試源可以任意選 1V 或 1A？]]
這頁會解決「測試源大小為什麼不影響等效阻抗」。

← [[電路學主線]]
```

關鍵規則：**每一個 wikilink 都必須附上「點過去會解掉什麼」的語義。** 單純「相關：[[Thevenin]]」不算合格連結。

## 6. AI Parser 不直接寫筆記

AI 每次解析題目應先讀：

1. QuestionRecord 與官方題幹。
2. 已驗證題解。
3. 既有 knowledge nodes。
4. 使用者本題的 reveal/selfAssessment/errorType（若有）。

然後先輸出一份 `KnowledgePatchCandidate`，例如：

```json
{
  "qid": "EE-114-05-2",
  "intent": "單線接地故障序網連接與故障電流",
  "likelyQuestions": [
    "為什麼 SLG 的正負零序電流相等？",
    "為什麼三個序網在 SLG 要串聯？"
  ],
  "reuse": ["m-symmetrical-components"],
  "create": ["q-ps-slg-series-sequence-network"],
  "update": [],
  "questionLinks": [],
  "confidence": 0.88,
  "evidence": ["題幹要求單線接地故障電流", "題解建立正負零序網"]
}
```

再由 deterministic validator 決定：

- ID 是否重複。
- 是否有近義節點。
- prereq 是否存在。
- 是否形成 cycle。
- QID 是否存在。
- 是否有 evidence。
- 低 confidence 是否進人工 review queue。

只有通過後才生成 Markdown 與網站資料。

這可以避免 AI 最常見的三種污染：重複建頁、亂連 prerequisite、把相似名詞當成同一概念。

## 7. 與現有作答系統的整合

不需要改掉目前四段蓋牌與 SM-2，而是在成功 attempt 後增加「診斷層」。

```text
做題
 ↓
四段蓋牌
 ↓
1 / 3 / 5 自評 + 錯因
 ↓
submitLearningAttempt()
 ↓
Knowledge Diagnosis
 ├─ 這題用了哪些 mechanism/procedure？
 ├─ errorType 對應哪個疑問？
 ├─ prerequisite 哪一層最可能薄弱？
 └─ 下一步該重做題，還是先補一個問題頁？
 ↓
SM-2 / 弱點頁 / Obsidian 深入閱讀
```

建議把現有錯因與知識節點結合：

| 現有錯因 | 優先診斷 |
| --- | --- |
| 題型辨識錯 | `procedure`：何時用哪個模型 |
| 起手式不會 | `question` + `procedure`：第一個判斷缺失 |
| 公式忘記 | `mechanism`：公式由什麼關係推出 |
| 計算錯 | 不一定新增知識頁；優先回到相同 procedure 重算 |
| 觀念混淆 | 對照兩個 `question/mechanism`，要求建立反例或邊界 |

這樣才能避免所有錯誤都被粗暴歸因成「某個章節不熟」。

## 8. 網站端應新增的三個入口

第一版只需要三個，不要把 UI 做成另一套 Obsidian。

### A.「我為什麼卡住？」

第④段自評後顯示最多 3 個最相關問題頁：

```text
你這題可能卡在：
1. 為什麼 SLG 三個序網要串聯？
2. 為什麼零序阻抗取決於接地路徑？
3. 為什麼故障電流最後要乘 3？
```

### B.「先補哪個前提？」

利用 prerequisite graph 與個人 Recall 狀態，只回傳第一個真正瓶頸，不一次丟整條 DAG。

### C.「回到主線」

每個問題頁、算法頁與網站知識卡都能回到該科 mainline，避免 Graph View 越逛越散。

## 9. SRS 應排「能力」，不要排「閱讀」

Obsidian 頁面不應因為「看過」就進 SM-2。

保留目前的原則：排程仍由明確自評動作觸發。新增兩種可排程單位即可：

1. `questionId`：重新做完整考題。
2. `knowledgeNodeId`：回答該問題頁最上方的 retrieval prompt。

例如：

```text
Prompt：
「不看筆記，解釋為什麼含受控源時不能關閉受控源求 Rth，並說出兩種正確求法。」
```

使用者答完再揭露頁面，而不是把筆記當 flashcard 正面直接閱讀。

## 10. 第一階段不要做的事

暫時不建議：

- 不把所有 321 題一次用 AI 生幾千張卡。
- 不導入向量資料庫或執行期後端。
- 不用 LLM 即時決定 SM-2 間隔。
- 不讓 AI 自動覆寫已 review 的核心機制。
- 不用 Graph View 的「連線數」直接代表學習重要性。
- 不把目前 69-node DAG 全部原封不動轉成 69 篇 Markdown；先把它視為 seed taxonomy。

## 11. 建議實作順序

### Phase 0：定義 schema 與黃金樣本

先選 3 類最適合驗證的題型，各做 3–5 題：

- 電力系統：Per Unit + 對稱分量 + SLG。
- 電路學：Thevenin + 受控源 + 一階暫態。
- 工程數學：二階 ODE + 線性代數。

人工與 AI 磨合出 20–30 個高品質節點後，再固定 parser spec。

驗收：同一機制能被多題重用；同一困惑不會重複建頁；所有 link 有語義。

### Phase 1：canonical graph + generator

新增 `data/knowledge/` schema、validator、Obsidian generator，並讓現有 DAG 從 canonical data 生成或逐步遷移。

驗收：

- 無 dangling edge。
- 無 cycle。
- QID 全存在。
- Markdown 與網站 DAG 由同一份資料生成。
- `unknown` 不再 fallback 成錯誤節點。

### Phase 2：題目與個人錯因接線

把 `question-links` 接到 QuestionRecord / attempt result。

驗收：自評後能看到「本題最可能的 1–3 個困惑」與「第一個前置缺口」，不影響現有 attempt transaction 與 PE/GK 隔離。

### Phase 3：Knowledge Node SRS

新增 knowledge-node retrieval prompt 與排程，沿用既有 localStorage/backup 契約。

驗收：閱讀不自動算完成；只有明確 recall 自評才排程；題目 SRS 與知識節點 SRS 可分開統計。

### Phase 4：批次擴充

再讓 AI 按歷屆高頻與個人錯題優先順序擴充，而不是按 321 題順序全部生成。

優先權建議：

```text
個人反覆錯題
> 歷屆高頻 mechanism
> 跨科共用 mechanism
> 低頻單題知識
```

## 12. 成功指標

不要以「產生幾篇筆記」當 KPI。真正該看：

1. **重用率**：一個 mechanism 平均支援多少考題／困惑。
2. **重複率**：新增節點中多少其實是既有概念的近義重複。
3. **診斷命中率**：使用者是否認為系統指出的前置缺口就是自己真正卡住的地方。
4. **二次作答改善**：看過問題頁後，相同 mechanism 的不同題是否能獨立解出。
5. **導航成本**：從做錯題到找到真正需要補的頁面需要幾次操作。
6. **unknown 比例**：保持可以接受的 unknown，比錯誤自動配對更重要。

第一批黃金樣本建議人工檢查至少 30 個節點與它們對應的真實題目，再決定是否擴大自動生成。

## 13. 最終產品形態

完成後，工作庫的角色會清楚分工：

```text
題庫網站
  = 作答、蓋牌、自評、錯因、SRS、原題與詳解

Canonical Knowledge Graph
  = 問題、核心機制、算法、前置關係、QID 對應

Obsidian
  = 人類可閱讀與可漫遊的推理知識網

AI Parser
  = 從新題／錯題提出知識圖譜 patch，不直接自由生成整個 Vault
```

這樣保留目前工作台最成熟的部分，同時把原本偏「章節式知識庫」升級成真正能回答「我為什麼不會這題、缺哪一層、下一步該補什麼」的複習系統。
