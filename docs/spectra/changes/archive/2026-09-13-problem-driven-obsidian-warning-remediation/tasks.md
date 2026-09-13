<!--
每項任務都寫出可觀察行為與驗證目標。本 change 是 Warning 修正提案；
在使用者明確 apply 前，任務維持未勾選。
-->

## 1. Projection 時間與 correction trace

- [x] 1.1 實作 **Explicit evaluation clock is part of projection input**，使 `buildWeaknessProjection` 輸出 `timeAnchor` 與 `timeAnchorMode`，區分即時明確時間與 latest-event replay，並 deterministic 分類未來／範圍外事件；驗證：執行 `python3 -m unittest tests.test_weakness_projection` 與固定 timestamp fixtures。
- [x] 1.2 實作 **Supersession chains remain inspectable without changing raw events**，使修正後 weakness 輸出有界的 `supersessionChain`、effective/historical IDs 與 predecessor 缺失警告，同時 raw event stream 保持不變；驗證：執行 correction trace regression tests 與 append-only stream equality assertion。
- [x] 1.3 完成 **Projection time anchor SHALL be explicit and auditable** 與 **Time filters SHALL classify future and out-of-window events deterministically**；驗證：以 `tests.test_weakness_projection` 檢查 7-day/30-day/all、PE/GK、未來日期與 replay output。
- [x] 1.4 完成 **Correction projection SHALL retain a traversable supersession chain** 與 **Correction state SHALL distinguish effective and historical evidence**；驗證：檢查 original-plus-correction drill-down ordering、missing predecessor 與 repeated projection deterministic 結果。

## 2. Candidate 與 reviewer provenance

- [x] 2.1 實作 **Candidate and review records use versioned provenance**，使 candidate inspection 強制要求 `candidateVersion: 1` 與完整有界 metadata；無效 candidate 必須 fail closed 且不寫入 filesystem；驗證：以 `tests.test_knowledge_patch_workflow` 檢查 missing-version、missing-evidence、stale-revision 與 unsafe-field fixtures。
- [x] 2.2 加入 reviewer receipt，包含 candidate hash、reviewer identity、decision、review time、base revision、reason/notes 與 approval result revision；驗證：以 `tests.test_knowledge_patch_workflow` 檢查 reject/approve atomicity 與 receipt contents。
- [x] 2.3 完成 **Candidate schema SHALL enforce versioned metadata** 與 **Review records SHALL preserve reviewer and provenance metadata**；驗證：檢查 CLI inspect/reject/approve output 與 repeated runs 的 candidate hash stability。

## 3. Acceptance freshness 與 recovery measurements

- [x] 3.1 實作 **Acceptance artifacts share one freshness identity**，使 canonical、website、Obsidian、capacity 與 acceptance reports 都輸出一致的 `generatedAt`、graph revision、source identity 與 blocking freshness errors；驗證：執行 current-revision/stale-report fixtures 與 `python3 scripts/validate_knowledge_graph.py`。
- [x] 3.2 實作 **Recovery acceptance uses measured time and fixed thresholds**，使 recovery reports 記錄 `recoveryTimeMs`、`recoveryTimeThresholdMs`、`recoveryTimePass`、event count、issue bytes 與 backup bytes；驗證：執行 crash/reload fixtures 與 `python3 scripts/measure_learning_data_capacity.py`。
- [x] 3.3 完成 **Acceptance reports SHALL be generated from current graph revision** 與 **Recovery acceptance SHALL record measured time and thresholds**；驗證：執行 `python3 scripts/run_change_acceptance.py`、stale report rejection 與 machine-readable blocking failures。

## 4. 規格 example coverage

- [x] 4.1 依 **Scenario examples are contract evidence**，為每個新增或修改的 scenario 與受影響的既有 graph scenario 加入有界 `##### Example:`；驗證：執行 scenario coverage checker，並 content review 所有 touched spec files。
- [x] 4.2 完成 **Spectra scenarios SHALL include concrete examples**；驗證：執行 `spectra analyze problem-driven-obsidian-warning-remediation --json`，確認本 change 沒有 missing example suggestion，並明確列出任何 legacy suggestion。

## 5. 整合驗證與交接

- [x] 5.1 所有 warning implementation 完成後執行 full acceptance handoff：`python3 -m unittest discover -s tests`、`python3 scripts/check_html_js_syntax.py`、`spectra analyze problem-driven-obsidian-warning-remediation --json` 與 `spectra validate problem-driven-obsidian-warning-remediation`；驗證：所有 blocking failures 為零且 report revisions 一致。
- [x] 5.2 將 **Recovery acceptance uses measured time and fixed thresholds** 與 **Acceptance artifacts share one freshness identity** gates 套用到 final release report；驗證：promotion 前檢查 clean-checkout reproducibility、PE/GK isolation、Obsidian drift protection 與 rollback behavior。
