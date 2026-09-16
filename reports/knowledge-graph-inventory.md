# 問題驅動知識圖譜 migration inventory

> 本報告是對現有來源的實測盤點；它不是 canonical graph，也不會改動 runtime。

## Measured counts

- Legacy `KNOWLEDGE_DAG` nodes: **69**
- Core Obsidian notes: **14**
- PE question records: **323** (323 unique QIDs)
- GK question records: **161** (161 unique QIDs)
- Specific mapping rules: **14**
- Manual topic labels: **23**
- Subject fallback present: **False**

## Mapping and backup observations

- The current question mapper is keyword/rule based and contains a subject fallback. Unknown coverage must be measured before replacing it.
- Backup storage keys are collected from `src/state/*.js`; the canonical migration must decide which keys become versioned sections.
- PE and GK question records are counted from separate generated bundles and remain separate migration inputs.

## Backup storage keys

- `EE_EXAM_ATTEMPT_ENVELOPES_V1`
- `EE_EXAM_ATTEMPT_RECOVERY_V1`
- `EE_EXAM_BACKUP_META_V1`
- `EE_EXAM_DAILY_PRACTICE_V1`
- `EE_EXAM_PROGRESS_V1`
- `EE_EXAM_RECALL_V1`
- `EE_EXAM_SM2_SCHEDULE_V1`
- `EE_EXAM_STARRED_V1`
- `EE_KNOWLEDGE_ISSUES_PE_V1`
- `EE_KNOWLEDGE_REVIEWS_PE_V1`
- `EE_MANUAL_TOPIC_LABELS_V1`
- `EE_MOCK_EXAM_TIMER_V1`
- `GK_EXAM_PROGRESS_V1`
- `GK_EXAM_STARRED_V1`
- `GK_KNOWLEDGE_ISSUES_GK_V1`
- `GK_KNOWLEDGE_REVIEWS_GK_V1`

## Source paths

- `src/data/knowledge-dag.js`
- `src/data/manualTopicLabels.js`
- `src/state/attemptStore.js`
- `src/state/sm2Store.js`
- `dashboard-data.js`
- `national-exams-data.js`
- `🧠 核心考點知識庫/`

## Review queue

- Review every legacy mapping that depends on the subject fallback before enabling a fail-closed adapter.
- Select the first golden QID slice from the measured PE/GK records and attach evidence before canonical promotion.
- Preserve generated bundles and existing Obsidian notes until the replacement projection passes its regression checks.
