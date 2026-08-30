---
name: engineering-math-solution-audit
title: 工程數學 PE 全年度詳解查核與修訂
status: active
---

# 工程數學 PE 全年度詳解查核與修訂

## Purpose

針對電機工程技師（PE）工程數學 104–114 年共 64 題，將官方題目裁切圖、題庫記錄與詳解逐題對齊，使用獨立 Solver／Verifier 路徑重算，消除共用模板與錯置答案。

## Trigger

- 初始執行：一次完成 104–114 年全量查核。
- 後續事件：工程數學題目裁切、題庫 topic、詳解 Markdown、驗算器或查核 manifest 變更時重跑受影響題目。

## Source of truth

- 題目條件：官方 PE PDF 與對應的 `images/questions/PE_*_Q*.png` 裁切圖。
- 題目主鍵：`EE-{year}-03-{questionNumber}`。
- 既有題解只作待查核輸入，不得作為驗證依據。

## Batch policy

- 依教科書章節集中處理，每批 8–12 題。
- 第一批：常微分方程（ODE）與拉氏轉換。
- 每批完成 Solver、Verifier、差異報告及自動測試後設置人工 checkpoint。

## Per-question run

1. 讀取 QID 對應的官方裁切圖、PDF 頁碼、題庫 topic 與目前詳解。
2. Solver 建立題目變數、邊界／初始條件與獨立推導。
3. Verifier 使用不同方法（代回、矩陣殘差、初末值、極限或數值積分等）交叉驗算。
4. 產出標準四區塊詳解：題目與已知條件、核心考點、步驟式詳細推導、滿分結論。
5. 公式只用標準 LaTeX（行內 `\(…\)`、獨立 `\[…\]`）；保留精確結果、至少四位有效數字近似值、SI 單位。
6. 計算結果以相對誤差 ≤ `1e-6`（或題目指定有效位數）判定數值一致。

## Status and evidence

每題寫入 `data/engineering-math-audit.json`，狀態只能是：

- `verified`：Solver／Verifier 與詳解一致，且通過人工摘要 checkpoint。
- `suspected_error`：存在明確不一致證據。
- `needs_manual_review`：題意、掃描或數值不足以自動判定。
- `not_attempted`：尚未完成。

每筆至少保存：`qid`、`solution_version`、`audit_status`、`verified_at`、`method`、`evidence_hash`、`solver_output`、`review_note`、`supersedes`、`source_crop`、`source_pages`。

## Publishing gate

- 新詳解只在 `verified` 且人工摘要確認後取代 `solutionLink`。
- 舊模板移至 `archive/engineering-math/`，標記 `superseded`，不得刪除。
- normalized solution hash 若被不同 QID 共用，CI 標為 `suspected_error`；允許共用必須列入白名單並附理由。
- CI 不阻擋其他科目部署，但阻止虛假 `verified`、無證據 `verified` 與未授權重複 hash。

## Checkpoint brief

每批只提供決策摘要：已完成題數、verified／suspected_error／needs_manual_review 分布、每題最終答案、差異證據、受影響檔案與下一批範圍。人工只需確認題目對應、最終答案與疑似錯誤處理。

## Required commands

```text
python3 scripts/audit_engineering_math.py --batch ode-laplace
python3 scripts/run_all_tests.py
python3 scripts/check_html_js_syntax.py
python3 scripts/health_check_codebase.py
```

