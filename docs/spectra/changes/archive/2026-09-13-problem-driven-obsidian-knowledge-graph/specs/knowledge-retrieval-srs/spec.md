## Purpose

Define knowledge-node retrieval practice as an independent spaced-repetition workflow while preserving the existing question Recall and SM-2 behavior.

## ADDED Requirements

### Requirement: Knowledge retrieval SHALL use an independent review identity

Each knowledge-node review SHALL use a stable knowledge review ID keyed to a canonical node ID, exam family, and learner scope. Its state SHALL be stored separately from question review state and SHALL include schedule, interval, ease or equivalent parameters, last recall, rating, and graph revision metadata.

#### Scenario: A learner starts retrieval for a mechanism node

- **WHEN** the learner explicitly starts a knowledge-node recall session
- **THEN** the system SHALL create or resume the node's independent review state without changing the question's Recall/SM-2 record.
##### Example:

- Fixture: `scenario-a-learner-starts-retrieval-for-a-mechanism-node` with input `{"scenario":"a-learner-starts-retrieval-for-a-mechanism-node","graphRevision":"kg-v1-test"}`.
- Operation: the learner explicitly starts a knowledge-node recall session.
- Expected output: the system SHALL create or resume the node's independent review state without changing the question's Recall/SM-2 record..
#### Scenario: A question and node share a title

- **WHEN** a question review and knowledge review use records with the same display title
- **THEN** their identities and schedule updates SHALL remain distinct.

### Requirement: Knowledge SRS SHALL schedule only after explicit recall and rating

Reading a generated note, opening a DAG node, viewing a diagnosis, or browsing a link SHALL not create or advance a knowledge review schedule. A schedule update SHALL require an explicit retrieval prompt and learner rating.
##### Example:

- Fixture: `scenario-a-question-and-node-share-a-title` with input `{"scenario":"a-question-and-node-share-a-title","graphRevision":"kg-v1-test"}`.
- Operation: a question review and knowledge review use records with the same display title.
- Expected output: their identities and schedule updates SHALL remain distinct..
#### Scenario: A learner reads a note

- **WHEN** the learner opens or reads a generated Obsidian or website node note
- **THEN** the system SHALL leave knowledge review state unchanged.
##### Example:

- Fixture: `scenario-a-learner-reads-a-note` with input `{"scenario":"a-learner-reads-a-note","graphRevision":"kg-v1-test"}`.
- Operation: the learner opens or reads a generated Obsidian or website node note.
- Expected output: the system SHALL leave knowledge review state unchanged..
#### Scenario: A learner rates a recall attempt

- **WHEN** the learner completes an explicit node retrieval prompt and submits a supported rating
- **THEN** the system SHALL persist the new node review state and compute its next due time using the versioned scheduling rule.

### Requirement: Knowledge retrieval SHALL honor node lifecycle migrations

Knowledge review state SHALL resolve rename, merge, split, and retire migrations through explicit lifecycle metadata. Historical reviews SHALL remain readable, and future scheduling SHALL use the active successor mapping according to the migration rule.
##### Example:

- Fixture: `scenario-a-learner-rates-a-recall-attempt` with input `{"scenario":"a-learner-rates-a-recall-attempt","graphRevision":"kg-v1-test"}`.
- Operation: the learner completes an explicit node retrieval prompt and submits a supported rating.
- Expected output: the system SHALL persist the new node review state and compute its next due time using the versioned scheduling rule..
#### Scenario: A reviewed node is renamed

- **WHEN** a node title changes while its stable node ID remains active
- **THEN** the existing review identity and schedule SHALL continue under the same node ID with updated display metadata.
##### Example:

- Fixture: `scenario-a-reviewed-node-is-renamed` with input `{"scenario":"a-reviewed-node-is-renamed","graphRevision":"kg-v1-test"}`.
- Operation: a node title changes while its stable node ID remains active.
- Expected output: the existing review identity and schedule SHALL continue under the same node ID with updated display metadata..
#### Scenario: A reviewed node is merged

- **WHEN** two reviewed nodes merge into one active successor
- **THEN** the migration SHALL preserve both historical states and apply a documented deterministic merge rule to the successor schedule.
##### Example:

- Fixture: `scenario-a-reviewed-node-is-merged` with input `{"scenario":"a-reviewed-node-is-merged","graphRevision":"kg-v1-test"}`.
- Operation: two reviewed nodes merge into one active successor.
- Expected output: the migration SHALL preserve both historical states and apply a documented deterministic merge rule to the successor schedule..
#### Scenario: A node is split

- **WHEN** one reviewed node is split into multiple active successors
- **THEN** the system SHALL retain the original review history and create successor states through an explicit migration record rather than silently copying an unverified schedule.

### Requirement: Knowledge review ratings SHALL be auditable

A node retrieval rating SHALL record the stable review ID, node ID, prompt instance, rating, timestamp, schedule rule version, graph revision, and source event or session when applicable. Replayed submissions for the same prompt instance SHALL be idempotent.
##### Example:

- Fixture: `scenario-a-node-is-split` with input `{"scenario":"a-node-is-split","graphRevision":"kg-v1-test"}`.
- Operation: one reviewed node is split into multiple active successors.
- Expected output: the system SHALL retain the original review history and create successor states through an explicit migration record rather than silently copying an unverified schedule..
#### Scenario: A rating request is retried

- **WHEN** the same node prompt instance is submitted again after a reload
- **THEN** the store SHALL return the existing review result and SHALL not advance the schedule twice.
##### Example:

- Fixture: `scenario-a-rating-request-is-retried` with input `{"scenario":"a-rating-request-is-retried","graphRevision":"kg-v1-test"}`.
- Operation: the same node prompt instance is submitted again after a reload.
- Expected output: the store SHALL return the existing review result and SHALL not advance the schedule twice..
#### Scenario: A schedule is inspected

- **WHEN** a user opens the node review history
- **THEN** the UI or export SHALL show the rating and scheduling provenance needed to explain the current due state.

### Requirement: Question SRS behavior SHALL remain compatible

The migration SHALL preserve stable question QIDs, existing Recall and SM-2 semantics, daily practice completion, and PE/GK separation. Knowledge retrieval integration SHALL not require changes to question schedule interpretation.
##### Example:

- Fixture: `scenario-a-schedule-is-inspected` with input `{"scenario":"a-schedule-is-inspected","graphRevision":"kg-v1-test"}`.
- Operation: a user opens the node review history.
- Expected output: the UI or export SHALL show the rating and scheduling provenance needed to explain the current due state..
#### Scenario: Existing question review runs

- **WHEN** a learner completes an existing question Recall/SM-2 flow without opening node retrieval
- **THEN** the question schedule and completion behavior SHALL match the pre-integration contract.
##### Example:

- Fixture: `scenario-existing-question-review-runs` with input `{"scenario":"existing-question-review-runs","graphRevision":"kg-v1-test"}`.
- Operation: a learner completes an existing question Recall/SM-2 flow without opening node retrieval.
- Expected output: the question schedule and completion behavior SHALL match the pre-integration contract..
#### Scenario: A daily practice item opens node retrieval

- **WHEN** daily practice offers a related knowledge node after a committed question attempt
- **THEN** the node review SHALL remain an explicit separate action and SHALL not be auto-scheduled by the question completion.
##### Example:

- Fixture: `scenario-a-daily-practice-item-opens-node-retrieval` with input `{"scenario":"a-daily-practice-item-opens-node-retrieval","graphRevision":"kg-v1-test"}`.
- Operation: daily practice offers a related knowledge node after a committed question attempt.
- Expected output: the node review SHALL remain an explicit separate action and SHALL not be auto-scheduled by the question completion..
