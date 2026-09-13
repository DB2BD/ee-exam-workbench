# Obsidian 多使用者個人化複習整合提案

- 日期：2026-09-13
- 適用專案：電機工程技師歷屆試題與詳解工作台
- 狀態：可行性研究與下一階段建議

## 1. 結論

引用對話提出的「具體疑問 → 缺失前提 → 核心機制 → 解題程序 → 真實題目 → 回到主線」方向可行，而且適合目前的技師考試工作庫。

建議採用以下分工：

```text
題庫網站
  = 作答、四段蓋牌、自評、錯因、題目 SRS、弱點統計

Canonical Knowledge Graph
  = 穩定節點、語義連結、前置關係、題目映射、graph revision

Obsidian Vault
  = 可閱讀、可補充、可用雙鏈回到主線的個人知識網
```

多使用者也可行，但推薦「每位使用者一個自己的 Vault」，共用的是由 canonical graph 生成的知識內容；個人的錯題、診斷、複習排程與補充筆記要保持分離。

目前不應把所有人直接放進同一份個人學習資料。這個專案是靜態網站，沒有登入系統與執行期後端；若兩個人使用同一個瀏覽器 profile，目前的 `localStorage` 會共用。因此多使用者需求必須先加入網站的 profile namespace，才能在同一台電腦上安全並行。

## 2. 引用對話中值得保留的設計

引用對話把 Obsidian 的最小學習單位定義為「一個完整困惑」，而不是只建立一頁章節名或公式名。例如：

> 為什麼含受控源時不能直接關閉所有電源求 Thevenin 等效電阻？

每頁固定回答：

1. 我真正卡住的是什麼。
2. 這頁要解決什麼。
3. 缺失的前提是什麼。
4. 核心機制如何成立。
5. 解題程序怎麼做。
6. 為什麼這樣做。
7. 反例、替代方案與失效條件。
8. 哪些歷屆題會用到。
9. 下一個問題與回到科目主線的路徑。

這個結構應與目前的四段蓋牌互補：先在網站嘗試提取與作答，再由診斷決定要補哪一個問題頁；Obsidian 不應成為先看完整答案的捷徑。知識節點只有在使用者明確完成回想並自評後，才進入獨立的 knowledge SRS。

## 3. 目前工作庫已具備的基礎

目前程式與生成報告顯示：

- PE 題庫有穩定 QID，GK 題庫也有獨立 QID 與資料邊界。
- `data/knowledge/` 已有 `nodes.json`、`edges.json`、`question-links.json` 與 schema。
- 目前生成報告有 145 個 canonical nodes、126 條 edges、482 筆題目連結。
- 網站已有四段蓋牌、題目自評、錯因診斷、弱點 projection、題目 SRS 與知識節點 SRS 的分離方向。
- `🧠 問題驅動知識庫/` 已能由 canonical graph 生成 Markdown。
- 生成筆記已標示 stable node ID、graph revision，並要求把個人補充放到 `📝 個人知識補充/`。
- 現有 Obsidian Vault 位於此工作庫根目錄，存在 `.obsidian/` 設定資料。

因此這不是從零開始開發，而是把「網站作答結果」接到「適合個人使用的 Vault 與 profile」上。

## 4. 多使用者與 Vault 的可行性

### 4.1 推薦方案：每人一個 Vault，共用生成規格

每位使用者擁有自己的 Vault，例如：

```text
使用者 A：EE-技師複習-A/
使用者 B：EE-技師複習-B/
```

每個 Vault 都可以放入相同版本的：

```text
🧠 問題驅動知識庫/        ← 由 canonical graph 生成的共用知識內容
00_主線/                  ← 各科主線
📝 個人知識補充/          ← 該使用者自己的疑問、推導與錯題補充
```

每個使用者在網站中有自己的 profile：

```text
profileId
displayName
obsidianVaultName 或 obsidianVaultId
graphRevision
```

網站的題目進度、收藏、題目 SRS、知識 SRS、attempt、診斷事件與弱點 projection 全部以 `profileId` 分隔。使用者可以用備份 JSON 在不同裝置搬移自己的資料，不需要把別人的學習資料放進同一個 Vault。

這個方案最符合「同一套教材、各自複習」的需求，也最容易處理個人隱私與錯題差異。

### 4.2 可行但有邊界：Obsidian Sync 共用一個團隊 Vault

Obsidian 官方支援以 Sync 分享 remote vault。官方目前說明的條件包括：所有協作者都需要有效的 Sync 訂閱；共用 Vault 上限為 20 位使用者；細緻權限尚未支援，協作者大致擁有與擁有者相同的權限，只有擁有者能邀請其他人；同一檔案不支援即時協同編輯，同時修改會在同步時合併，並可用版本歷史查看與還原。

因此共用 Vault 適合放：

- 經審查後的共同課程筆記。
- canonical graph 生成的共同知識頁。
- 全體都要看的考試主線與公式索引。

不適合直接放：

- 每個人的作答進度與 SRS。
- 個人錯因與診斷事件。
- 尚未審查的 AI patch。
- 多人同時編輯的同一篇個人補充。

若未來選用 Obsidian Sync 的共用 Vault，應把共用內容和個人內容分成不同資料夾，並以使用者子目錄保存個人筆記；但若目標是完全隔離個人資料，仍以每人一個 Vault 更簡單、更安全。

### 4.3 不建議：用一般共享資料夾直接承擔多人編輯

不要把同一 Vault 同時交給多個雲端同步工具、網路共享資料夾與 Obsidian Sync 管理。這會增加檔案衝突、設定檔衝突與生成檔被覆蓋的風險。共用內容應由 canonical graph 生成，個人內容由各自 Vault 保存。

## 5. 網站與 Obsidian 的整合邊界

### 5.1 網站可以可靠做到的事

第一階段應先完成這些低耦合功能：

1. 題目完成後顯示「建議複習路線」。
2. 顯示本題命中的問題節點、第一個前置缺口與可解決的困惑。
3. 一鍵切到網站知識圖譜並聚焦該節點。
4. 產生該節點在 Vault 內的相對路徑，例如 `🧠 問題驅動知識庫/05_電力系統/ps-symmetrical-components.md`。
5. 一鍵開啟 Obsidian 筆記；若作業系統或瀏覽器阻擋自訂 URI，則提供複製筆記位置的後備按鈕。
6. 讓使用者明確開始知識節點回想、揭露、評分，再建立 knowledge SRS。
7. 在「我的弱點」中直接提供「開始回想」、「查看網站路線」與「開啟 Obsidian」三個動作。

### 5.2 靜態網站不應假裝具備的能力

瀏覽器中的靜態網站不能可靠地任意讀寫使用者電腦上的 Vault 檔案。因此「開啟筆記」與「複製路徑」可以先做；「自動把診斷寫進指定 Markdown」則不應直接宣稱已完成。

若未來需要自動寫入，可另做一個明確的本機整合層：

```text
網站
  → export / deep link / validated payload
  → 本機腳本或 Obsidian plugin
  → 使用者指定 Vault 的個人筆記
```

該整合層必須使用 `profileId`、`vaultId`、QID、nodeId 與 graph revision，且只能追加或建立經過驗證的個人內容，不得直接覆寫 canonical generated note。

## 6. 建議的使用流程

```text
第一次使用
  ↓
選擇或建立 profile
  ↓
設定 Obsidian Vault 名稱／ID
  ↓
確認網站與 Vault 的 graph revision
  ↓
開始今日練習
  ↓
四段蓋牌與作答
  ↓
1 / 3 / 5 自評 + 錯因
  ↓
看到「我為什麼卡住？」與「先補哪個前提？」
  ↓
開始知識節點回想
  ↓
需要時開啟 Obsidian 問題頁
  ↓
完成個人補充後回網站明確自評
  ↓
knowledge SRS 排入下次回想
  ↓
回到原題重做，再回到科目主線
```

其中有三個資料邊界必須保持：

- 看過 Obsidian 不等於已掌握。
- 打開網站節點不等於已完成 knowledge review。
- 個人補充不等於修改 canonical graph；若要改共用知識，應產生 patch candidate，經審查後再重新生成。

## 7. 針對目前專案的實作階段

### Phase A：Profile 與個人資料隔離

- 將現有 localStorage key 統一經過 `profileId` namespace。
- 新增目前使用者 profile 的建立、切換與顯示。
- 舊資料只遷移到使用者明確選定的預設 profile，不自動覆蓋或清空。
- 備份 JSON 加入 profile metadata、graph revision 與 Vault 設定，但不把 Vault 個人筆記內容混進題目進度備份。

### Phase B：題目到複習路線

- 從 `question-links.json` 解析本題主要節點與前置鏈。
- 在完整揭露與自評後顯示最多一個首要補強點，以及有限的後續路線。
- 把 `why` 文字直接顯示在連結旁，讓使用者知道下一頁能解決什麼。
- unknown mapping 時明確顯示「目前沒有可靠診斷」，不以科目第一節點代替。

### Phase C：Obsidian Deep Link 與後備操作

- 儲存每個 profile 的 Vault name 或 Vault ID。
- 使用 URI encode 產生 `obsidian://open?vault=...&file=...`。
- 提供「開啟 Obsidian 筆記」與「複製筆記位置」兩個獨立按鈕。
- 只使用 Vault 內相對路徑，不把 `/Users/...` 這類本機絕對路徑寫進 canonical data。
- 題目、知識節點與主線都使用穩定 ID，避免檔案搬移或顯示名稱調整造成斷鏈。

### Phase D：個人筆記寫入的可選整合層

只有在前面三階段穩定後才評估：

- 匯出一份可貼入 Obsidian 的個人診斷 Markdown。
- 使用 Obsidian URI 的 `new`／`append` 行為建立個人紀錄。
- 或建立本機 Obsidian plugin，負責驗證 payload 後寫入個人資料夾。

這一階段不直接讓 AI 或網站自由改寫 generated notes。

## 8. 驗收條件

第一版完成前至少要證明：

- 使用者 A、B 在同一瀏覽器 profile namespace 下的進度、錯因與 SRS 不互相出現。
- 使用者切換 profile 後，題目統計與弱點頁立即切換到正確資料。
- 使用者 A 的 Obsidian URI 不會開到使用者 B 的 Vault。
- 同一個 canonical graph revision 可生成相同的共用筆記。
- 個人補充檔案不會被 generator 覆寫、重新命名或刪除。
- unknown mapping 不會產生假的節點關聯。
- 讀取或開啟筆記不會自動建立 knowledge SRS；只有明確回想與評分才會排程。
- 同一個題目 attempt 重試不會重複灌入等價診斷事件。
- 備份與還原能保留各 profile 的完整學習資料，且 PE／GK 仍然隔離。
- Obsidian 沒有安裝、URI 被阻擋或 Vault 不存在時，網站仍能用複製路徑與網站知識圖譜完成複習。

若使用共用 Obsidian Sync Vault，另外驗收：

- 共同內容和個人資料夾有明確界線。
- 同檔多人編輯的限制已在使用說明中標示。
- 版本歷史與衝突復原流程可被使用者找到。

## 9. 風險與取捨

| 風險 | 影響 | 建議 |
| --- | --- | --- |
| 靜態網站沒有登入與後端 | 無法在不同裝置自動同步個人進度 | 先做 profile namespace + JSON backup；未來再評估帳號後端 |
| 同一 Vault 放入所有人的個人筆記 | 隱私、誤編輯與同步衝突 | 每人一個 Vault；共用 Vault 只放共同內容 |
| 直接以筆記閱讀取代提取練習 | 使用者看懂但未必能重現解題 | 維持四段蓋牌與明確 knowledge recall |
| 生成筆記被人工直接改動 | 下一次生成可能衝突 | generated 與 personal 分目錄，generator fail closed |
| Vault 名稱重複或搬移 | URI 開錯 Vault | 優先保存 Vault ID，名稱作顯示與後備 |
| 多人同時改同一檔案 | 可能出現合併結果或需要還原 | 不把同檔即時協作當成產品能力，個人檔案分離 |

## 10. 建議先做的最小版本

建議先實作以下五件事，能直接改善目前「按了卻沒有幫助」的使用感：

1. 題目完成後顯示一張可理解的複習路線卡。
2. 路線卡提供「開始節點回想」、「在網站查看路線」、「開啟 Obsidian 筆記」與「複製筆記位置」。
3. 知識圖譜把到期節點排在前面，節點卡直接提供回想入口。
4. 我的弱點頁直接連到前置節點、題目與 Obsidian。
5. 增加 profile namespace，先解決同一台電腦不同使用者的資料隔離。

這五件事不需要引入後端，也不會改變既有 attempt transaction；完成後再根據實際使用回饋決定是否需要本機 plugin 或自動寫入個人筆記。

## 11. 參考資料

- [引用對話：結合 Obsidian 複習算法題目](chatgpt-conversation://6aa502a4-ec3c-83e8-8a94-5f475459d6ba)
- [Obsidian URI：開啟 Vault、筆記與建立筆記](https://help.obsidian.md/Extending%2BObsidian/Obsidian%2BURI)
- [Obsidian Sync：共用 Vault 與協作限制](https://help.obsidian.md/Obsidian%2BSync/Collaborate%2Bon%2Ba%2Bshared%2Bvault)
- [Obsidian Sync：同步與資料安全](https://help.obsidian.md/Obsidian%2BSync/Security%2Band%2Bprivacy)
- [Test-enhanced learning：提取練習與延遲測驗效果](https://pubmed.ncbi.nlm.nih.gov/16507066/)

本提案只定義可行架構與實作順序，不代表已完成 profile namespace、跨使用者同步或自動寫入 Obsidian；這些應依上述驗收條件逐階段實作。

## 12. Sol 複查結論

2026-09-13 複查結果：方向可行，原提案需要補上可執行的資料隔離契約、操作順序、失敗處理與放行條件。複查後採用以下決策：

- 每位使用者一個獨立 Vault 是預設方案；Obsidian Sync 共用 Vault 只放共同生成內容。
- `profileId` namespace 是第一階段 blocker。沒有它，不得宣稱同一台電腦能讓不同使用者安全並行。
- `vaultId` 優先於 Vault 名稱；網站只保存設定與產生 URI，不直接任意讀寫本機檔案。
- 第一版提供題目診斷路線、網站節點回想、Obsidian 開啟、複製筆記路徑與個人 Markdown 匯出。
- 自動寫入個人筆記必須另做本機腳本或 Obsidian plugin，並通過 payload、path、profile 與 graph revision 驗證。
- 所有學習資料仍須通過既有 attempt、backup、PE／GK 隔離與 fail-closed 契約。

細分工作包、每個操作的要求、測試指令與 Sol 放行條件，見 [Sol／Luna 多使用者 Obsidian 複習整合工作提案](WORKPLAN_Sol_Luna_Obsidian多使用者個人化複習整合_2026-09-13.md)。
