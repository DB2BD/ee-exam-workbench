## Purpose

Define deterministic post-submit diagnosis, user confirmation, append-only issue events, and the rebuildable weakness projection that turns practice evidence into actionable knowledge gaps.

## ADDED Requirements

### Requirement: Diagnosis SHALL be deterministic and bounded

The diagnosis engine SHALL accept a QuestionRecord, validated question links, answer rating, error type, recall result, exam family, and graph revision. It SHALL return at most three `likelyQuestions`, at most one `firstPrerequisiteGap`, a reason, confidence, and `needsConfirmation`.

#### Scenario: A mapped conceptual error is submitted

- **WHEN** a committed attempt has an approved question link and a conceptual error type
- **THEN** the engine SHALL return a deterministic ranked list within the bounds and include evidence-backed reasons and confidence.
##### Example:

- Fixture: `scenario-a-mapped-conceptual-error-is-submitted` with input `{"scenario":"a-mapped-conceptual-error-is-submitted","graphRevision":"kg-v1-test"}`.
- Operation: a committed attempt has an approved question link and a conceptual error type.
- Expected output: the engine SHALL return a deterministic ranked list within the bounds and include evidence-backed reasons and confidence..
#### Scenario: A calculation-only error is submitted

- **WHEN** a committed attempt records only a calculation error without conceptual evidence
- **THEN** the engine SHALL avoid asserting a conceptual weakness and SHALL return an explicit confirmation-needed or unknown result.

### Requirement: Diagnosis SHALL be gated on a committed attempt

The system SHALL make diagnosis available only after the attempt envelope reaches committed state and the submitted result is associated with the stable attempt ID and graph revision used for diagnosis.
##### Example:

- Fixture: `scenario-a-calculation-only-error-is-submitted` with input `{"scenario":"a-calculation-only-error-is-submitted","graphRevision":"kg-v1-test"}`.
- Operation: a committed attempt records only a calculation error without conceptual evidence.
- Expected output: the engine SHALL avoid asserting a conceptual weakness and SHALL return an explicit confirmation-needed or unknown result..
#### Scenario: The answer is still active

- **WHEN** a user opens the post-submit flow before the attempt commit succeeds
- **THEN** the system SHALL not create a diagnosis or issue event and SHALL show the recovery or retry state.
##### Example:

- Fixture: `scenario-the-answer-is-still-active` with input `{"scenario":"the-answer-is-still-active","graphRevision":"kg-v1-test"}`.
- Operation: a user opens the post-submit flow before the attempt commit succeeds.
- Expected output: the system SHALL not create a diagnosis or issue event and SHALL show the recovery or retry state..
#### Scenario: The answer is committed

- **WHEN** the attempt is committed and its question links are available
- **THEN** the system SHALL expose the bounded diagnosis for user review.

### Requirement: The post-submit UI SHALL require an explicit classification outcome

The diagnosis card SHALL offer confirm, correct, none-of-above, and skip. It SHALL show the candidate reason and confidence, allow a correction to select another supported node, and condition automatic advance on the selected outcome.
##### Example:

- Fixture: `scenario-the-answer-is-committed` with input `{"scenario":"the-answer-is-committed","graphRevision":"kg-v1-test"}`.
- Operation: the attempt is committed and its question links are available.
- Expected output: the system SHALL expose the bounded diagnosis for user review..
#### Scenario: The user confirms the primary diagnosis

- **WHEN** the user selects confirm
- **THEN** the UI SHALL record the selected primary diagnosis outcome and continue according to the configured auto-advance behavior.
##### Example:

- Fixture: `scenario-the-user-confirms-the-primary-diagnosis` with input `{"scenario":"the-user-confirms-the-primary-diagnosis","graphRevision":"kg-v1-test"}`.
- Operation: the user selects confirm.
- Expected output: the UI SHALL record the selected primary diagnosis outcome and continue according to the configured auto-advance behavior..
#### Scenario: The user finds no matching diagnosis

- **WHEN** the user selects none-of-above or skip
- **THEN** the UI SHALL preserve an explicit unclassified outcome and SHALL not invent a canonical node assignment.

### Requirement: Issue history SHALL be append-only and idempotent

Each PE/GK issue stream SHALL append events containing event ID, attempt ID, QID, exam family, rating, error type, event type, primary and secondary node IDs, custom text, candidate count and rank, confidence, recorded time, diagnosis version, graph revision reference, and `supersedesEventId` when correcting an earlier event. The same primary node SHALL be counted at most once per attempt.
##### Example:

- Fixture: `scenario-the-user-finds-no-matching-diagnosis` with input `{"scenario":"the-user-finds-no-matching-diagnosis","graphRevision":"kg-v1-test"}`.
- Operation: the user selects none-of-above or skip.
- Expected output: the UI SHALL preserve an explicit unclassified outcome and SHALL not invent a canonical node assignment..
#### Scenario: A primary diagnosis is confirmed twice after reload

- **WHEN** the same stable attempt and classification submission is retried
- **THEN** the store SHALL return the existing event or an equivalent idempotent result and SHALL not increment the raw primary count twice.
##### Example:

- Fixture: `scenario-a-primary-diagnosis-is-confirmed-twice-after-reload` with input `{"scenario":"a-primary-diagnosis-is-confirmed-twice-after-reload","graphRevision":"kg-v1-test"}`.
- Operation: the same stable attempt and classification submission is retried.
- Expected output: the store SHALL return the existing event or an equivalent idempotent result and SHALL not increment the raw primary count twice..
#### Scenario: The user corrects an earlier diagnosis

- **WHEN** a correction selects a different supported node
- **THEN** the store SHALL append a correction event that supersedes the prior event while preserving the prior event unchanged.

### Requirement: Issue events SHALL preserve unknown and secondary outcomes

The event model SHALL keep `unknown`, `none-of-above`, and `skip` as explicit outcomes. Secondary candidates SHALL be stored independently from the primary count, and an unresolved or cross-family candidate SHALL not be persisted as a node ID.
##### Example:

- Fixture: `scenario-the-user-corrects-an-earlier-diagnosis` with input `{"scenario":"the-user-corrects-an-earlier-diagnosis","graphRevision":"kg-v1-test"}`.
- Operation: a correction selects a different supported node.
- Expected output: the store SHALL append a correction event that supersedes the prior event while preserving the prior event unchanged..
#### Scenario: A diagnosis has a secondary prerequisite

- **WHEN** the user confirms a primary node and accepts a separately displayed prerequisite gap
- **THEN** the store SHALL write primary and secondary references with distinct roles and projection rules.
##### Example:

- Fixture: `scenario-a-diagnosis-has-a-secondary-prerequisite` with input `{"scenario":"a-diagnosis-has-a-secondary-prerequisite","graphRevision":"kg-v1-test"}`.
- Operation: the user confirms a primary node and accepts a separately displayed prerequisite gap.
- Expected output: the store SHALL write primary and secondary references with distinct roles and projection rules..
#### Scenario: The mapping is unknown

- **WHEN** diagnosis cannot establish a supported node
- **THEN** the event SHALL contain the unknown reason or custom text and SHALL contain no fabricated node reference.

### Requirement: Weakness projection SHALL be pure and explainable

`buildWeaknessProjection` SHALL rebuild weakness entries from the issue event stream for one PE/GK key. Each entry SHALL expose raw count, distinct QIDs, last seen time, rating distribution, error distribution, source distribution, acceptance metrics, review state, priority, and links to supporting events.
##### Example:

- Fixture: `scenario-the-mapping-is-unknown` with input `{"scenario":"the-mapping-is-unknown","graphRevision":"kg-v1-test"}`.
- Operation: diagnosis cannot establish a supported node.
- Expected output: the event SHALL contain the unknown reason or custom text and SHALL contain no fabricated node reference..
#### Scenario: The same event stream is projected twice

- **WHEN** the same validated events are passed to the projection function twice
- **THEN** both projections SHALL be equivalent, including ordering after applying the versioned priority formula.
##### Example:

- Fixture: `scenario-the-same-event-stream-is-projected-twice` with input `{"scenario":"the-same-event-stream-is-projected-twice","graphRevision":"kg-v1-test"}`.
- Operation: the same validated events are passed to the projection function twice.
- Expected output: both projections SHALL be equivalent, including ordering after applying the versioned priority formula..
#### Scenario: A correction supersedes a prior event

- **WHEN** the projection reads an original event and its correction
- **THEN** it SHALL apply the correction according to `supersedesEventId`, expose the resulting review state, and retain traceability to both events.

### Requirement: The weakness view SHALL support time filters and drill-down

The “my weaknesses” view SHALL support 7-day, 30-day, and all-time ranges, show pending classification separately, and allow a user to drill from a weakness to the supporting QIDs, event history, diagnosis evidence, and the related knowledge node or unknown reason.
##### Example:

- Fixture: `scenario-a-correction-supersedes-a-prior-event` with input `{"scenario":"a-correction-supersedes-a-prior-event","graphRevision":"kg-v1-test"}`.
- Operation: the projection reads an original event and its correction.
- Expected output: it SHALL apply the correction according to `supersedesEventId`, expose the resulting review state, and retain traceability to both events..
#### Scenario: A user filters recent weaknesses

- **WHEN** the user selects the 7-day range
- **THEN** the view SHALL calculate and display only events in that range while retaining the selected PE/GK isolation.
##### Example:

- Fixture: `scenario-a-user-filters-recent-weaknesses` with input `{"scenario":"a-user-filters-recent-weaknesses","graphRevision":"kg-v1-test"}`.
- Operation: the user selects the 7-day range.
- Expected output: the view SHALL calculate and display only events in that range while retaining the selected PE/GK isolation..
#### Scenario: A user opens a weakness entry

- **WHEN** the user selects a projected weakness
- **THEN** the view SHALL show its evidence trail and provide the next supported action, such as diagnosis review, node retrieval, or manual classification.

### Requirement: Capacity and family isolation SHALL be enforced

The issue store SHALL reject writes that exceed the release capacity gate of 5,000 events or an approximately 3 MiB payload target once measured thresholds are configured. PE and GK streams, projections, and event IDs SHALL remain isolated.
##### Example:

- Fixture: `scenario-a-user-opens-a-weakness-entry` with input `{"scenario":"a-user-opens-a-weakness-entry","graphRevision":"kg-v1-test"}`.
- Operation: the user selects a projected weakness.
- Expected output: the view SHALL show its evidence trail and provide the next supported action, such as diagnosis review, node retrieval, or manual classification..
#### Scenario: The issue stream reaches its configured capacity

- **WHEN** an append would exceed the configured event count or payload threshold
- **THEN** the store SHALL reject the write with a recoverable capacity error and SHALL leave existing events and projections unchanged.
##### Example:

- Fixture: `scenario-the-issue-stream-reaches-its-configured-capacity` with input `{"scenario":"the-issue-stream-reaches-its-configured-capacity","graphRevision":"kg-v1-test"}`.
- Operation: an append would exceed the configured event count or payload threshold.
- Expected output: the store SHALL reject the write with a recoverable capacity error and SHALL leave existing events and projections unchanged..
#### Scenario: A PE event is queried from the GK view

- **WHEN** a GK projection requests its event stream
- **THEN** the projection SHALL exclude PE events even when QIDs or node titles overlap.
##### Example:

- Fixture: `scenario-a-pe-event-is-queried-from-the-gk-view` with input `{"scenario":"a-pe-event-is-queried-from-the-gk-view","graphRevision":"kg-v1-test"}`.
- Operation: a GK projection requests its event stream.
- Expected output: the projection SHALL exclude PE events even when QIDs or node titles overlap..
