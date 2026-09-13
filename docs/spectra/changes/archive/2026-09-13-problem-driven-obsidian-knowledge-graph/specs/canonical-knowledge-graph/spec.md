## Purpose

Define the canonical, versioned knowledge graph that provides shared meaning to the website DAG, question diagnosis, weakness projections, knowledge retrieval review, Obsidian generation and Codex context packets.

## ADDED Requirements

### Requirement: The canonical graph SHALL use stable typed records

Every canonical node SHALL have a stable `nodeId`, one of `question`, `mechanism`, `procedure`, or `mainline` as `nodeType`, a title, an `examFamily`, provenance, lifecycle state, and deterministic revision metadata. A question record SHALL retain its stable QID and tuple compatibility fields.

#### Scenario: A reviewed mechanism node is stored

- **WHEN** a mechanism is added to the canonical graph
- **THEN** the stored record SHALL include a stable node ID, `nodeType: mechanism`, its exam family, provenance, active lifecycle state, and a reproducible node revision hash.
##### Example:

- Fixture: `scenario-a-reviewed-mechanism-node-is-stored` with input `{"scenario":"a-reviewed-mechanism-node-is-stored","graphRevision":"kg-v1-test"}`.
- Operation: a mechanism is added to the canonical graph.
- Expected output: the stored record SHALL include a stable node ID, `nodeType: mechanism`, its exam family, provenance, active lifecycle state, and a reproducible node revision hash..
#### Scenario: A node omits its required identity

- **WHEN** the validator reads a node without a stable ID, supported type, or exam family
- **THEN** validation SHALL fail with a machine-readable error code and the graph revision SHALL not be promoted.

### Requirement: Semantic edges SHALL be evidence-bearing and bounded

Each semantic edge SHALL contain `from`, `relation`, `to`, `why`, `confidence`, `evidence`, and `reviewStatus`. The validator SHALL reject duplicate edges, dangling endpoints, illegal cross-exam-family links, and cycles for relations declared acyclic by the schema.
##### Example:

- Fixture: `scenario-a-node-omits-its-required-identity` with input `{"scenario":"a-node-omits-its-required-identity","graphRevision":"kg-v1-test"}`.
- Operation: the validator reads a node without a stable ID, supported type, or exam family.
- Expected output: validation SHALL fail with a machine-readable error code and the graph revision SHALL not be promoted..
#### Scenario: An edge explains a prerequisite

- **WHEN** a reviewed edge connects a procedure to its prerequisite mechanism
- **THEN** it SHALL include a non-empty reason, evidence reference, confidence value, review status, and endpoints that resolve to valid nodes.
##### Example:

- Fixture: `scenario-an-edge-explains-a-prerequisite` with input `{"scenario":"an-edge-explains-a-prerequisite","graphRevision":"kg-v1-test"}`.
- Operation: a reviewed edge connects a procedure to its prerequisite mechanism.
- Expected output: it SHALL include a non-empty reason, evidence reference, confidence value, review status, and endpoints that resolve to valid nodes..
#### Scenario: An edge forms an invalid cycle

- **WHEN** a new acyclic prerequisite edge closes a directed cycle
- **THEN** validation SHALL fail with a stable cycle error and SHALL leave the prior valid graph revision available.

### Requirement: Question links SHALL be isolated by exam family

A question link SHALL identify a stable QID, its exam family, one or more canonical node IDs, confidence, evidence, review status, and source priority. The link resolver SHALL reject a QID that belongs to another exam family and SHALL represent an unresolved mapping as `unknown` with a reason.
##### Example:

- Fixture: `scenario-an-edge-forms-an-invalid-cycle` with input `{"scenario":"an-edge-forms-an-invalid-cycle","graphRevision":"kg-v1-test"}`.
- Operation: a new acyclic prerequisite edge closes a directed cycle.
- Expected output: validation SHALL fail with a stable cycle error and SHALL leave the prior valid graph revision available..
#### Scenario: A question is linked to a concept in the same family

- **WHEN** a reviewed PE question link references a PE question and PE nodes
- **THEN** the resolver SHALL return the linked nodes with their evidence and review metadata.
##### Example:

- Fixture: `scenario-a-question-is-linked-to-a-concept-in-the-same-family` with input `{"scenario":"a-question-is-linked-to-a-concept-in-the-same-family","graphRevision":"kg-v1-test"}`.
- Operation: a reviewed PE question link references a PE question and PE nodes.
- Expected output: the resolver SHALL return the linked nodes with their evidence and review metadata..
#### Scenario: A question has no defensible mapping

- **WHEN** no approved or deterministic link meets the configured evidence threshold
- **THEN** the resolver SHALL return `unknown` with a diagnostic reason and SHALL NOT select an arbitrary subject node.

### Requirement: Node lifecycle changes SHALL preserve historical references

The graph SHALL support `active`, `retired`, and `merged` lifecycle states. Rename, merge, split, and retire operations SHALL record explicit migration metadata so historical issue events, review states, and links can resolve without rewriting their original IDs.
##### Example:

- Fixture: `scenario-a-question-has-no-defensible-mapping` with input `{"scenario":"a-question-has-no-defensible-mapping","graphRevision":"kg-v1-test"}`.
- Operation: no approved or deterministic link meets the configured evidence threshold.
- Expected output: the resolver SHALL return `unknown` with a diagnostic reason and SHALL NOT select an arbitrary subject node..
#### Scenario: A mechanism is merged into a replacement

- **WHEN** an approved merge retires two mechanism nodes into one replacement
- **THEN** the graph SHALL retain the original IDs, record the replacement mapping, and resolve future projections to the replacement while preserving historical event references.
##### Example:

- Fixture: `scenario-a-mechanism-is-merged-into-a-replacement` with input `{"scenario":"a-mechanism-is-merged-into-a-replacement","graphRevision":"kg-v1-test"}`.
- Operation: an approved merge retires two mechanism nodes into one replacement.
- Expected output: the graph SHALL retain the original IDs, record the replacement mapping, and resolve future projections to the replacement while preserving historical event references..
#### Scenario: A retired node is referenced by history

- **WHEN** a historical event references a retired node
- **THEN** history queries SHALL remain readable and SHALL expose the lifecycle state and any successor mapping.

### Requirement: Graph revisions SHALL be deterministic and promotable only after validation

A graph revision SHALL be derived deterministically from canonical data and schema version. A revision SHALL record its content hash, source/provenance summary, and validation result. Runtime consumers and generators SHALL use only a validated revision.
##### Example:

- Fixture: `scenario-a-retired-node-is-referenced-by-history` with input `{"scenario":"a-retired-node-is-referenced-by-history","graphRevision":"kg-v1-test"}`.
- Operation: a historical event references a retired node.
- Expected output: history queries SHALL remain readable and SHALL expose the lifecycle state and any successor mapping..
#### Scenario: The same source is built twice

- **WHEN** identical canonical files and schema are processed twice
- **THEN** both builds SHALL produce the same graph revision identifier and equivalent serialized records.
##### Example:

- Fixture: `scenario-the-same-source-is-built-twice` with input `{"scenario":"the-same-source-is-built-twice","graphRevision":"kg-v1-test"}`.
- Operation: identical canonical files and schema are processed twice.
- Expected output: both builds SHALL produce the same graph revision identifier and equivalent serialized records..
#### Scenario: Canonical input is invalid

- **WHEN** validation reports any blocking error
- **THEN** no runtime bundle, generated note set, or promoted revision SHALL be produced from that input.

### Requirement: The validator SHALL produce actionable reports

The validator SHALL emit stable error codes, record paths or IDs, and a human-readable report for malformed nodes, edges, question links, lifecycle migrations, duplicate IDs, dangling references, cycles, and cross-family violations.
##### Example:

- Fixture: `scenario-canonical-input-is-invalid` with input `{"scenario":"canonical-input-is-invalid","graphRevision":"kg-v1-test"}`.
- Operation: validation reports any blocking error.
- Expected output: no runtime bundle, generated note set, or promoted revision SHALL be produced from that input..
#### Scenario: A migration contains a dangling target

- **WHEN** a lifecycle migration names a target node that does not exist
- **THEN** the report SHALL identify the migration and missing target with a stable error code.
##### Example:

- Fixture: `scenario-a-migration-contains-a-dangling-target` with input `{"scenario":"a-migration-contains-a-dangling-target","graphRevision":"kg-v1-test"}`.
- Operation: a lifecycle migration names a target node that does not exist.
- Expected output: the report SHALL identify the migration and missing target with a stable error code..
#### Scenario: A valid golden fixture is checked

- **WHEN** the reviewed golden fixture satisfies the schema and graph constraints
- **THEN** the validator SHALL report success and include coverage and revision metadata.
##### Example:

- Fixture: `scenario-a-valid-golden-fixture-is-checked` with input `{"scenario":"a-valid-golden-fixture-is-checked","graphRevision":"kg-v1-test"}`.
- Operation: the reviewed golden fixture satisfies the schema and graph constraints.
- Expected output: the validator SHALL report success and include coverage and revision metadata..
