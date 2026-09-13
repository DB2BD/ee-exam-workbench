## Purpose

Define durable attempt recovery, versioned backup and restore, atomic state replacement, capacity gates, and PE/GK isolation for the expanded learning data model.

## ADDED Requirements

### Requirement: Attempts SHALL use a durable envelope and stable session identity

Every learning attempt SHALL have a stable session ID, QID, exam family, lifecycle state, and versioned envelope. The lifecycle SHALL distinguish `active`, `committed`, and `acknowledged`; `beginOrResume`, `submit`, `ack`, and `recover` SHALL be safe to retry for the same session.

#### Scenario: A learner reloads during an active attempt

- **WHEN** the application reloads before submission
- **THEN** `beginOrResume` SHALL recover the same active session or return a documented redo state without creating a second committed attempt.
##### Example:

- Fixture: `scenario-a-learner-reloads-during-an-active-attempt` with input `{"scenario":"a-learner-reloads-during-an-active-attempt","graphRevision":"kg-v1-test"}`.
- Operation: the application reloads before submission.
- Expected output: `beginOrResume` SHALL recover the same active session or return a documented redo state without creating a second committed attempt..
#### Scenario: A committed attempt is acknowledged twice

- **WHEN** the same session receives repeated acknowledgement requests
- **THEN** `ack` SHALL be idempotent and SHALL retain one committed result and one acknowledgement outcome.

### Requirement: Diagnosis data SHALL be written after durable attempt commit

The persistence layer SHALL commit the attempt result before accepting any issue event or diagnosis-linked learning write. A failure before commit SHALL not leave a valid diagnosis event; a failure after commit and before acknowledgement SHALL be recoverable without replaying a legal attempt.
##### Example:

- Fixture: `scenario-a-committed-attempt-is-acknowledged-twice` with input `{"scenario":"a-committed-attempt-is-acknowledged-twice","graphRevision":"kg-v1-test"}`.
- Operation: the same session receives repeated acknowledgement requests.
- Expected output: `ack` SHALL be idempotent and SHALL retain one committed result and one acknowledgement outcome..
#### Scenario: The browser crashes before commit

- **WHEN** the process stops before the attempt result is durably committed
- **THEN** recovery SHALL mark the session incomplete or redoable and SHALL expose no committed attempt or issue event for it.
##### Example:

- Fixture: `scenario-the-browser-crashes-before-commit` with input `{"scenario":"the-browser-crashes-before-commit","graphRevision":"kg-v1-test"}`.
- Operation: the process stops before the attempt result is durably committed.
- Expected output: recovery SHALL mark the session incomplete or redoable and SHALL expose no committed attempt or issue event for it..
#### Scenario: The browser crashes after commit before acknowledgement

- **WHEN** the process stops after commit but before UI acknowledgement
- **THEN** recovery SHALL find the committed result, complete or retry acknowledgement, and preserve the original attempt ID for downstream diagnosis.

### Requirement: Backup records SHALL be versioned and complete

A backup SHALL include a schema version and validated sections for question review state, knowledge review state, attempts, issue events, graph references, recovery journal records, and PE/GK store metadata. The exporter SHALL record graph revision and migration provenance.
##### Example:

- Fixture: `scenario-the-browser-crashes-after-commit-before-acknowledgement` with input `{"scenario":"the-browser-crashes-after-commit-before-acknowledgement","graphRevision":"kg-v1-test"}`.
- Operation: the process stops after commit but before UI acknowledgement.
- Expected output: recovery SHALL find the committed result, complete or retry acknowledgement, and preserve the original attempt ID for downstream diagnosis..
#### Scenario: A current user exports a backup

- **WHEN** the user exports local learning data
- **THEN** the backup SHALL contain every enabled learning section, schema version, exam-family metadata, and the graph revision needed to interpret node IDs.
##### Example:

- Fixture: `scenario-a-current-user-exports-a-backup` with input `{"scenario":"a-current-user-exports-a-backup","graphRevision":"kg-v1-test"}`.
- Operation: the user exports local learning data.
- Expected output: the backup SHALL contain every enabled learning section, schema version, exam-family metadata, and the graph revision needed to interpret node IDs..
#### Scenario: An older backup is imported

- **WHEN** an older supported schema version is imported
- **THEN** the importer SHALL apply deterministic migrations, validate the migrated structure, and report the source and target versions.

### Requirement: Restore SHALL validate before replacing local state

Import SHALL parse and validate the complete backup before replacing local state. Restore SHALL be atomic across attempts, issue events, knowledge reviews, question reviews, and journals, and SHALL support rollback when validation or migration fails.
##### Example:

- Fixture: `scenario-an-older-backup-is-imported` with input `{"scenario":"an-older-backup-is-imported","graphRevision":"kg-v1-test"}`.
- Operation: an older supported schema version is imported.
- Expected output: the importer SHALL apply deterministic migrations, validate the migrated structure, and report the source and target versions..
#### Scenario: A backup contains malformed issue events

- **WHEN** validation finds an invalid event, unknown exam family, or dangling graph reference
- **THEN** restore SHALL reject the backup before replacement and SHALL leave the current local state unchanged.
##### Example:

- Fixture: `scenario-a-backup-contains-malformed-issue-events` with input `{"scenario":"a-backup-contains-malformed-issue-events","graphRevision":"kg-v1-test"}`.
- Operation: validation finds an invalid event, unknown exam family, or dangling graph reference.
- Expected output: restore SHALL reject the backup before replacement and SHALL leave the current local state unchanged..
#### Scenario: A valid backup is restored

- **WHEN** all migrations, schema checks, graph compatibility checks, and capacity checks pass
- **THEN** restore SHALL replace the complete local state atomically and SHALL make the restored projection reproducible.

### Requirement: Recovery journal replay SHALL be bounded and observable

The recovery journal SHALL carry operation ID, session identity, affected store keys, operation stage, payload version, and checksums or equivalent integrity metadata. Replay and rollback SHALL emit actionable failure information and SHALL be safe to retry.
##### Example:

- Fixture: `scenario-a-valid-backup-is-restored` with input `{"scenario":"a-valid-backup-is-restored","graphRevision":"kg-v1-test"}`.
- Operation: all migrations, schema checks, graph compatibility checks, and capacity checks pass.
- Expected output: restore SHALL replace the complete local state atomically and SHALL make the restored projection reproducible..
#### Scenario: A multi-store write is interrupted

- **WHEN** the process stops after writing one store but before completing the operation
- **THEN** recovery SHALL use the journal to finish or roll back the operation atomically and SHALL avoid duplicate events or reviews.
##### Example:

- Fixture: `scenario-a-multi-store-write-is-interrupted` with input `{"scenario":"a-multi-store-write-is-interrupted","graphRevision":"kg-v1-test"}`.
- Operation: the process stops after writing one store but before completing the operation.
- Expected output: recovery SHALL use the journal to finish or roll back the operation atomically and SHALL avoid duplicate events or reviews..
#### Scenario: A journal record is corrupt

- **WHEN** replay detects an invalid checksum or unsupported journal version
- **THEN** recovery SHALL stop that operation, preserve existing valid state, and report the operation ID and repair action.

### Requirement: Capacity gates SHALL protect local stability

The implementation SHALL measure issue event count, serialized payload size, backup size, and recovery time. It SHALL enforce the release gate of at least 5,000 issue events and a backup payload target near 3 MiB using configured thresholds, with clear errors before an unsafe write.
##### Example:

- Fixture: `scenario-a-journal-record-is-corrupt` with input `{"scenario":"a-journal-record-is-corrupt","graphRevision":"kg-v1-test"}`.
- Operation: replay detects an invalid checksum or unsupported journal version.
- Expected output: recovery SHALL stop that operation, preserve existing valid state, and report the operation ID and repair action..
#### Scenario: A backup exceeds its configured limit

- **WHEN** serialization produces a backup larger than the configured local limit
- **THEN** export or restore SHALL fail with measured size and limit and SHALL leave source state intact.
##### Example:

- Fixture: `scenario-a-backup-exceeds-its-configured-limit` with input `{"scenario":"a-backup-exceeds-its-configured-limit","graphRevision":"kg-v1-test"}`.
- Operation: serialization produces a backup larger than the configured local limit.
- Expected output: export or restore SHALL fail with measured size and limit and SHALL leave source state intact..
#### Scenario: The issue event gate is exercised

- **WHEN** the capacity fixture writes 5,000 valid events under the configured target
- **THEN** append, projection rebuild, backup export, and restore SHALL complete within the recorded acceptance thresholds.

### Requirement: PE and GK data SHALL remain isolated through all operations

Attempt envelopes, question reviews, knowledge reviews, issue events, projections, backups, restore migrations, and recovery journal keys SHALL carry and enforce exam-family scope. Cross-family IDs or queries SHALL fail closed.
##### Example:

- Fixture: `scenario-the-issue-event-gate-is-exercised` with input `{"scenario":"the-issue-event-gate-is-exercised","graphRevision":"kg-v1-test"}`.
- Operation: the capacity fixture writes 5,000 valid events under the configured target.
- Expected output: append, projection rebuild, backup export, and restore SHALL complete within the recorded acceptance thresholds..
#### Scenario: A backup contains mixed exam families

- **WHEN** a backup includes valid PE and GK sections
- **THEN** restore SHALL preserve their separation and SHALL rebuild each projection only from its own family.
##### Example:

- Fixture: `scenario-a-backup-contains-mixed-exam-families` with input `{"scenario":"a-backup-contains-mixed-exam-families","graphRevision":"kg-v1-test"}`.
- Operation: a backup includes valid PE and GK sections.
- Expected output: restore SHALL preserve their separation and SHALL rebuild each projection only from its own family..
#### Scenario: A cross-family event is submitted

- **WHEN** an event's QID, node ID, and exam-family fields do not agree
- **THEN** persistence SHALL reject the event before writing any store.
##### Example:

- Fixture: `scenario-a-cross-family-event-is-submitted` with input `{"scenario":"a-cross-family-event-is-submitted","graphRevision":"kg-v1-test"}`.
- Operation: an event's QID, node ID, and exam-family fields do not agree.
- Expected output: persistence SHALL reject the event before writing any store..
