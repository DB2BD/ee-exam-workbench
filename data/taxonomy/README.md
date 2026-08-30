# 題型分類資料層

這個目錄保存可審核、可版本化的題型分類資料，不直接修改複習頁的呈現邏輯。

| 檔案 | 用途 |
| --- | --- |
| `alias-map.json` | 教科書章節的 canonical ID、顯示名稱與中英文同義詞。分類器先做文字正規化，再使用這份 map。 |
| `golden-set.json` | 人工確認的正例與容易混淆的反例；以穩定 QID 追溯原題。 |
| `overrides.json` | 人工覆寫紀錄的資料檔，目前為空佇列。 |
| `override-schema.json` | 覆寫紀錄的 JSON Schema，限制欄位、狀態與版本格式。 |

`taxonomyVersion` 變更時，應重新執行 taxonomy 測試與完整 build。golden set 的
`questionIds` 只引用題庫中已存在的 QID；不存在或跨科目的 ID 會讓品質閘門失敗。

目前 `golden-set.json` 先收錄 PE 題庫可從題幹、tags 或公式明確驗證的案例。
`coverageExceptions` 明確記錄題庫目前沒有足夠正例的 DAG 節點，避免以自動分類結果
冒充人工標註；後續人工複核後可逐步補齊至每章五題。
