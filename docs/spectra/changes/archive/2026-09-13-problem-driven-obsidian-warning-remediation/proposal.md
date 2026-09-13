## Problem

Critical 問題已修正，但複查仍發現幾個會降低複習可信度與後續維護效率的 Warning：弱點時間範圍的基準不夠明確、修正事件在投影中難以追溯、候選 patch 的版本與審查來源未被完整強制、驗收報告可能沿用舊 revision，且 recovery 時間尚未量測。Spectra analyzer 另外指出現有規格情境缺少具體範例，讓下位模型難以從契約推導可驗證行為。

## Root Cause

- `buildWeaknessProjection` 在未提供 `now` 時以事件最新時間作為 reference，重播資料與使用者查看「最近 30 天」的語意沒有明確區分。
- superseded event 會從有效事件集合排除，雖然 raw stream 仍在，但 projection drill-down 沒有穩定的完整修正鏈介面。
- `knowledge_patch_workflow.py` 已有候選內容檢查，但 `candidateVersion`、完整候選欄位與 reviewer/provenance receipt 沒有形成一致的強制契約。
- acceptance、canonical graph 與 Obsidian build 報告由不同命令產生，缺少同一個 graph revision、產生時間與 source hash 的 freshness gate。
- capacity 報告有事件數與大小，但缺少 recovery time 的實測欄位與固定門檻；規格情境也沒有逐一附上具體輸入與輸出例子。

## Proposed Solution

- 建立可稽核的 projection time anchor，區分使用者即時查詢與 deterministic replay，並為事件落在未來或範圍外時定義明確結果。
- 在不改寫 append-only raw events 的前提下，提供可遍歷的 `supersessionChain` 與 effective/historical 狀態，讓使用者能從修正後結論回看原始判斷。
- 強制候選 schema 版本、完整 metadata 與來源事件；審查結果寫入帶 reviewer identity、時間、decision、candidate hash 與 graph revision 的 receipt。
- 將 acceptance、canonical graph、website 與 Obsidian 產物綁定同一 revision，加入 stale report 檢查與 recovery time/threshold 量測。
- 為本次新增規格與現有問題驅動知識圖譜規格補上可執行的 `##### Example:`，讓 analyzer 與下位模型能對照輸入、操作與結果。

## Non-Goals

- 不在本 change 導入雲端同步、Obsidian 多人協作服務或 runtime backend。
- 不改寫既有 append-only event、既有 canonical node ID、題目 SRS 演算法或已完成的 Critical 修正。
- 不在本 change 直接核准任何 AI candidate；仍由人工 review gate 決定是否進入 canonical graph。

## Success Criteria

- projection 的 UI 呼叫帶有明確 time anchor，replay 與即時查詢的結果可由輸出欄位區分，且固定時間測試可重現。
- correction projection 能在同一筆 weakness 下列出原始與修正事件，並標示哪一筆 effective。
- 缺少 `candidateVersion`、來源事件或 reviewer receipt 的 candidate/review 結果會 fail closed；合法流程可產生可稽核 receipt。
- acceptance report、graph validation、website build 與 Obsidian build 具有相同 graph revision；stale report 會阻擋 promotion。
- acceptance report 包含 measured recovery time、configured threshold 與 pass/fail；5000 events 與約 3 MiB gate 仍通過。
- 新增與既有規格的 scenario 都有 concrete example，`spectra analyze` 不再以缺少範例作為未處理建議。

## Impact

- Affected code:
  - Modified: `src/domain/weaknessProjection.js`, `scripts/knowledge_patch_workflow.py`, `scripts/run_change_acceptance.py`, `scripts/measure_learning_data_capacity.py`, acceptance/build report writers and related tests.
  - New: `docs/spectra/changes/problem-driven-obsidian-warning-remediation/` specifications, fixtures and freshness/recovery checks.
  - Removed: none.

## Capabilities

### New Capabilities

- `weakness-time-semantics`
- `weakness-correction-trace`
- `candidate-review-provenance`
- `acceptance-report-freshness`
- `spec-scenario-examples`

### Modified Capabilities

- none; the current completed change remains the compatibility baseline until this Warning change is explicitly applied.
