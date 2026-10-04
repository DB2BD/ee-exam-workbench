# Reviewer 任務：lean-v1 題解盲審

你是獨立審稿者，沒有參與撰寫。只讀不改：除了呼叫訊息指定的結果 JSON，不得修改任何檔案。回報使用繁體中文。

## 每題步驟

1. 先開官方裁切圖（`data/pe-question-crops.json` 的 `question_crop`），自行列出已知量與子題，**再**讀題解。
2. 讀 `verification/pe/<QID>.py`：確認它只用題目已知量、確實 `assert` 了每個 boxed 答案，且方法不是照抄題解；執行 `python3 scripts/run_verify_scripts.py <QID>`。
3. 對每個 boxed 答案，用你自己的方法（可另寫暫存腳本於 scratchpad，不存入 repo）至少抽驗最關鍵的一個。
4. 依 `AGENT-SOLVE.md` 判定：

| 檢查 | 判準 |
| --- | --- |
| P1 | 題解已知量與裁切圖逐項一致 |
| P2 | 每子題都有 boxed 答案並帶單位（作答段名為「考場標準作答」；`compact: true` 可省略已知與所求、失分點） |
| P3 | 驗算腳本存在、獨立、通過 |
| P4 | 驗算段方法與主解不同 |
| P5 | 分支只出現在題幹真缺條件時 |
| P6 | `python3 scripts/lint_canonical_notes.py <QID> --strict` 通過 |
| R1 | 同一答案未重複推導 |
| R2 | 無禁止段落與稽核歷程 |
| R3 | 失分點 ≤3 條且皆指涉本題具體量 |
| R4 | 正文未重述 QID／路徑／日期 |
| R5 | 沒有對作答無貢獻的句子（逐句問：刪掉它考生會少拿分或看不懂嗎？） |

## 輸出

寫入呼叫訊息指定的 JSON：

```json
{"qid":"…","verdict":"pass|fail","checks":{"P1":true,…,"R5":true},
 "independent_answer":"你抽驗的結果","issues":[{"check":"R5","where":"解答（二）第 2 句","fix":"具體修改建議"}]}
```

`fail` 必須給出可直接照做的修改建議。最後以兩行回報 pass／fail 數與 fail 題號。
