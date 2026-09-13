## Purpose

Define the offline Codex context packet and the review-gated `KnowledgePatchCandidate` workflow for proposing changes to the canonical graph without allowing untrusted text or stale revisions to write data.

## ADDED Requirements

### Requirement: Context packets SHALL be bounded and reproducible

The context packet exporter SHALL produce markdown and JSON previews containing the selected graph revision, selected weakness nodes, related QIDs, semantic evidence, unknown or none-of-above outcomes, and the minimum history needed for review. Export SHALL be deterministic for the same inputs and SHALL not mutate local graph or learning state.

#### Scenario: A learner exports one weakness

- **WHEN** the user requests a packet for a selected projected weakness
- **THEN** the exporter SHALL include the selected evidence and graph revision in both formats with matching content identifiers.
##### Example:

- Fixture: `scenario-a-learner-exports-one-weakness` with input `{"scenario":"a-learner-exports-one-weakness","graphRevision":"kg-v1-test"}`.
- Operation: the user requests a packet for a selected projected weakness.
- Expected output: the exporter SHALL include the selected evidence and graph revision in both formats with matching content identifiers..
#### Scenario: A packet is generated offline

- **WHEN** the exporter runs without network access
- **THEN** it SHALL complete from local data and SHALL not attempt an external request or write a graph change.

### Requirement: Patch candidates SHALL carry revision and provenance metadata

A `KnowledgePatchCandidate` SHALL include `candidateVersion`, `candidateId`, `baseGraphRevision`, `sourceIssueEventIds`, QID and exam family, intent, likely questions, reuse/create/update operations, question links, confidence, evidence, and expected node hashes.
##### Example:

- Fixture: `scenario-a-packet-is-generated-offline` with input `{"scenario":"a-packet-is-generated-offline","graphRevision":"kg-v1-test"}`.
- Operation: the exporter runs without network access.
- Expected output: it SHALL complete from local data and SHALL not attempt an external request or write a graph change..
#### Scenario: Codex proposes a reused node link

- **WHEN** a candidate connects a question to an existing node
- **THEN** it SHALL identify the base revision, source issue events, existing node, evidence, confidence, and expected hash for that node.
##### Example:

- Fixture: `scenario-codex-proposes-a-reused-node-link` with input `{"scenario":"codex-proposes-a-reused-node-link","graphRevision":"kg-v1-test"}`.
- Operation: a candidate connects a question to an existing node.
- Expected output: it SHALL identify the base revision, source issue events, existing node, evidence, confidence, and expected hash for that node..
#### Scenario: A candidate omits evidence

- **WHEN** a candidate creates or updates a node without evidence or source issue references required by the schema
- **THEN** candidate validation SHALL reject it with an actionable error and SHALL not enqueue it for approval.

### Requirement: Candidate validation SHALL fail closed on stale or unsafe changes

The candidate validator SHALL reject unknown QIDs or node IDs, exam-family violations, stale graph revisions, expected-hash drift, duplicate nodes or links, dangling edges, forbidden cycles, invalid lifecycle transitions, unsupported paths, oversized fields, and unreviewed update operations.
##### Example:

- Fixture: `scenario-a-candidate-omits-evidence` with input `{"scenario":"a-candidate-omits-evidence","graphRevision":"kg-v1-test"}`.
- Operation: a candidate creates or updates a node without evidence or source issue references required by the schema.
- Expected output: candidate validation SHALL reject it with an actionable error and SHALL not enqueue it for approval..
#### Scenario: The base graph changed after export

- **WHEN** a candidate references a graph revision different from the current validated revision
- **THEN** validation SHALL reject it as stale and SHALL require re-export or explicit rebase before review.
##### Example:

- Fixture: `scenario-the-base-graph-changed-after-export` with input `{"scenario":"the-base-graph-changed-after-export","graphRevision":"kg-v1-test"}`.
- Operation: a candidate references a graph revision different from the current validated revision.
- Expected output: validation SHALL reject it as stale and SHALL require re-export or explicit rebase before review..
#### Scenario: A candidate contains a path traversal

- **WHEN** a candidate names a file path containing traversal, an absolute path, or a write outside the generated data roots
- **THEN** validation SHALL reject the candidate and SHALL not touch the filesystem.
##### Example:

- Fixture: `scenario-a-candidate-contains-a-path-traversal` with input `{"scenario":"a-candidate-contains-a-path-traversal","graphRevision":"kg-v1-test"}`.
- Operation: a candidate names a file path containing traversal, an absolute path, or a write outside the generated data roots.
- Expected output: validation SHALL reject the candidate and SHALL not touch the filesystem..
#### Scenario: A candidate introduces a cycle

- **WHEN** candidate edges would violate an acyclic relation
- **THEN** validation SHALL report the cycle and SHALL reject the complete candidate atomically.

### Requirement: Candidate review SHALL be explicit and auditable

The review queue SHALL support inspect, reject, and approve states. Rejection SHALL preserve the candidate and reason without changing canonical data. Approval SHALL rebase against the current graph, rerun validation, append reviewer and provenance metadata, and produce a new deterministic graph revision.
##### Example:

- Fixture: `scenario-a-candidate-introduces-a-cycle` with input `{"scenario":"a-candidate-introduces-a-cycle","graphRevision":"kg-v1-test"}`.
- Operation: candidate edges would violate an acyclic relation.
- Expected output: validation SHALL report the cycle and SHALL reject the complete candidate atomically..
#### Scenario: A reviewer rejects a candidate

- **WHEN** the reviewer selects reject and supplies a reason
- **THEN** the candidate SHALL become rejected, the reason SHALL be retained, and nodes, edges, and question links SHALL remain unchanged.
##### Example:

- Fixture: `scenario-a-reviewer-rejects-a-candidate` with input `{"scenario":"a-reviewer-rejects-a-candidate","graphRevision":"kg-v1-test"}`.
- Operation: the reviewer selects reject and supplies a reason.
- Expected output: the candidate SHALL become rejected, the reason SHALL be retained, and nodes, edges, and question links SHALL remain unchanged..
#### Scenario: A reviewer approves a current candidate

- **WHEN** the reviewer approves a candidate whose revision, hashes, evidence, and structure still validate
- **THEN** the system SHALL apply it atomically, record approval metadata, and publish the resulting validated revision to generators.
##### Example:

- Fixture: `scenario-a-reviewer-approves-a-current-candidate` with input `{"scenario":"a-reviewer-approves-a-current-candidate","graphRevision":"kg-v1-test"}`.
- Operation: the reviewer approves a candidate whose revision, hashes, evidence, and structure still validate.
- Expected output: the system SHALL apply it atomically, record approval metadata, and publish the resulting validated revision to generators..
#### Scenario: Approval finds a new conflict

- **WHEN** rebase discovers new graph drift or a duplicate introduced since inspection
- **THEN** approval SHALL stop without partial writes and SHALL return the candidate to a state requiring review.

### Requirement: Arbitrary pasted text SHALL never write canonical data

The workflow SHALL parse only the versioned candidate schema. Markdown, JSON, or text pasted outside that schema SHALL remain an untrusted review attachment and SHALL not be interpreted as a graph mutation.
##### Example:

- Fixture: `scenario-approval-finds-a-new-conflict` with input `{"scenario":"approval-finds-a-new-conflict","graphRevision":"kg-v1-test"}`.
- Operation: rebase discovers new graph drift or a duplicate introduced since inspection.
- Expected output: approval SHALL stop without partial writes and SHALL return the candidate to a state requiring review..
#### Scenario: A user pastes a plausible markdown note

- **WHEN** the pasted text lacks a valid candidate envelope
- **THEN** the system SHALL store or display it only as review input and SHALL make no canonical graph, link, note, or event change.

### Requirement: Candidate size and output paths SHALL be enforced

The workflow SHALL enforce configured field, evidence, packet, and candidate size limits. Generated outputs SHALL be restricted to approved canonical, generated-note, and review-queue roots, with stable filenames derived from validated IDs.
##### Example:

- Fixture: `scenario-a-user-pastes-a-plausible-markdown-note` with input `{"scenario":"a-user-pastes-a-plausible-markdown-note","graphRevision":"kg-v1-test"}`.
- Operation: the pasted text lacks a valid candidate envelope.
- Expected output: the system SHALL store or display it only as review input and SHALL make no canonical graph, link, note, or event change..
#### Scenario: A candidate exceeds the configured payload limit

- **WHEN** a candidate or context packet exceeds its configured size limit
- **THEN** validation or export SHALL fail with the measured size and limit and SHALL leave existing data unchanged.
##### Example:

- Fixture: `scenario-a-candidate-exceeds-the-configured-payload-limit` with input `{"scenario":"a-candidate-exceeds-the-configured-payload-limit","graphRevision":"kg-v1-test"}`.
- Operation: a candidate or context packet exceeds its configured size limit.
- Expected output: validation or export SHALL fail with the measured size and limit and SHALL leave existing data unchanged..
#### Scenario: A valid candidate writes a generated note

- **WHEN** approval creates a generated note for a validated node ID
- **THEN** the path SHALL be deterministically derived under the generated-note root and SHALL pass the personal-note protection checks.
##### Example:

- Fixture: `scenario-a-valid-candidate-writes-a-generated-note` with input `{"scenario":"a-valid-candidate-writes-a-generated-note","graphRevision":"kg-v1-test"}`.
- Operation: approval creates a generated note for a validated node ID.
- Expected output: the path SHALL be deterministically derived under the generated-note root and SHALL pass the personal-note protection checks..
