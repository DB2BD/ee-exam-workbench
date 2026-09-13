## Purpose

Define deterministic projections from a validated canonical graph to the existing website DAG and to generated Obsidian notes while preserving personal notes and making drift observable.

## ADDED Requirements

### Requirement: The website DAG generator SHALL be deterministic

The generator SHALL read only a validated canonical graph revision and SHALL produce a stable `src/data/knowledge-dag.generated.js` or equivalent bundle with node IDs, supported node types, semantic relations, mainline ordering, and question references required by the existing viewer and tracer.

#### Scenario: A validated graph is bundled

- **WHEN** the website generator receives a validated graph revision
- **THEN** it SHALL produce a bundle whose serialized output and ordering are reproducible for the same inputs.
##### Example:

- Fixture: `scenario-a-validated-graph-is-bundled` with input `{"scenario":"a-validated-graph-is-bundled","graphRevision":"kg-v1-test"}`.
- Operation: the website generator receives a validated graph revision.
- Expected output: it SHALL produce a bundle whose serialized output and ordering are reproducible for the same inputs..
#### Scenario: A bundle references an unknown node

- **WHEN** a graph record or projection references a node absent from the validated revision
- **THEN** generation SHALL fail with the missing ID and SHALL not replace the prior generated bundle.

### Requirement: The compatibility projection SHALL preserve existing viewer entry points

The generated website data SHALL preserve the existing viewer, tracer, question detail and PE/GK isolation contracts needed by the current workbench. New canonical IDs and provenance SHALL remain available to diagnosis and drill-down consumers.
##### Example:

- Fixture: `scenario-a-bundle-references-an-unknown-node` with input `{"scenario":"a-bundle-references-an-unknown-node","graphRevision":"kg-v1-test"}`.
- Operation: a graph record or projection references a node absent from the validated revision.
- Expected output: generation SHALL fail with the missing ID and SHALL not replace the prior generated bundle..
#### Scenario: An existing question detail view opens

- **WHEN** a question detail view requests its mapped graph nodes
- **THEN** the compatibility projection SHALL return the canonical mapping or an explicit unknown result without breaking the existing view contract.
##### Example:

- Fixture: `scenario-an-existing-question-detail-view-opens` with input `{"scenario":"an-existing-question-detail-view-opens","graphRevision":"kg-v1-test"}`.
- Operation: a question detail view requests its mapped graph nodes.
- Expected output: the compatibility projection SHALL return the canonical mapping or an explicit unknown result without breaking the existing view contract..
#### Scenario: A GK question is loaded

- **WHEN** a GK question requests graph data
- **THEN** the projection SHALL expose only GK-compatible graph records and SHALL not leak PE nodes or links.

### Requirement: Generated Obsidian notes SHALL use stable identity and semantic links

The Obsidian generator SHALL write canonical generated notes under `🧠 問題驅動知識庫/`. Each generated note SHALL contain stable-ID frontmatter, node type, exam family, graph revision, source hash, and semantic wikilinks for approved relations and linked questions.
##### Example:

- Fixture: `scenario-a-gk-question-is-loaded` with input `{"scenario":"a-gk-question-is-loaded","graphRevision":"kg-v1-test"}`.
- Operation: a GK question requests graph data.
- Expected output: the projection SHALL expose only GK-compatible graph records and SHALL not leak PE nodes or links..
#### Scenario: A golden mainline node is generated

- **WHEN** the generator processes an active mainline node
- **THEN** it SHALL create a stable-ID note with the required frontmatter and links to its approved prerequisite and related nodes.
##### Example:

- Fixture: `scenario-a-golden-mainline-node-is-generated` with input `{"scenario":"a-golden-mainline-node-is-generated","graphRevision":"kg-v1-test"}`.
- Operation: the generator processes an active mainline node.
- Expected output: it SHALL create a stable-ID note with the required frontmatter and links to its approved prerequisite and related nodes..
#### Scenario: A note has a retired target

- **WHEN** an approved edge points through a lifecycle migration to a retired target
- **THEN** the generated note SHALL resolve the successor according to the migration metadata and retain enough provenance to explain the historical target.

### Requirement: Personal notes SHALL be protected from generation

The generator SHALL treat `📝 個人知識補充/` as user-owned content. It SHALL not overwrite, rename, or delete personal files and SHALL reference personal notes only through explicit, user-defined links or metadata.
##### Example:

- Fixture: `scenario-a-note-has-a-retired-target` with input `{"scenario":"a-note-has-a-retired-target","graphRevision":"kg-v1-test"}`.
- Operation: an approved edge points through a lifecycle migration to a retired target.
- Expected output: the generated note SHALL resolve the successor according to the migration metadata and retain enough provenance to explain the historical target..
#### Scenario: A personal note shares a concept title

- **WHEN** a personal note has the same display title as a generated node
- **THEN** generation SHALL keep the personal file unchanged and SHALL use stable generated identity for canonical links.
##### Example:

- Fixture: `scenario-a-personal-note-shares-a-concept-title` with input `{"scenario":"a-personal-note-shares-a-concept-title","graphRevision":"kg-v1-test"}`.
- Operation: a personal note has the same display title as a generated node.
- Expected output: generation SHALL keep the personal file unchanged and SHALL use stable generated identity for canonical links..
#### Scenario: A personal note contains unsupported content

- **WHEN** a personal note is not valid canonical graph input
- **THEN** generation SHALL ignore it as graph source data and SHALL still report the generated graph result.

### Requirement: Generated drift SHALL fail closed with an actionable report

The generator SHALL compare the recorded source hash or generation marker for existing generated notes before overwriting them. Unexpected body drift SHALL stop that note's rewrite, identify the path and node ID, and explain the required recovery action.
##### Example:

- Fixture: `scenario-a-personal-note-contains-unsupported-content` with input `{"scenario":"a-personal-note-contains-unsupported-content","graphRevision":"kg-v1-test"}`.
- Operation: a personal note is not valid canonical graph input.
- Expected output: generation SHALL ignore it as graph source data and SHALL still report the generated graph result..
#### Scenario: A generated note is unchanged

- **WHEN** its source hash matches the validated graph inputs
- **THEN** the generator SHALL update it deterministically if the graph revision changed and SHALL preserve its generated marker.
##### Example:

- Fixture: `scenario-a-generated-note-is-unchanged` with input `{"scenario":"a-generated-note-is-unchanged","graphRevision":"kg-v1-test"}`.
- Operation: its source hash matches the validated graph inputs.
- Expected output: the generator SHALL update it deterministically if the graph revision changed and SHALL preserve its generated marker..
#### Scenario: A generated note was manually edited

- **WHEN** its recorded source hash does not match the generated body
- **THEN** generation SHALL fail for that note, leave the edited file intact, and report the drift before any destructive write.

### Requirement: Build integration SHALL verify reproducibility and coverage

The project build SHALL expose commands for inventory, validation, website generation, Obsidian generation, and drift checking. The integration SHALL record source counts, mapped question counts, unknown counts, and graph revision in a report.
##### Example:

- Fixture: `scenario-a-generated-note-was-manually-edited` with input `{"scenario":"a-generated-note-was-manually-edited","graphRevision":"kg-v1-test"}`.
- Operation: its recorded source hash does not match the generated body.
- Expected output: generation SHALL fail for that note, leave the edited file intact, and report the drift before any destructive write..
#### Scenario: A clean checkout runs the knowledge build

- **WHEN** inventory, validation, generation and the existing workbench build run from the same canonical inputs
- **THEN** the commands SHALL succeed in a documented order and produce reproducible generated artifacts.
##### Example:

- Fixture: `scenario-a-clean-checkout-runs-the-knowledge-build` with input `{"scenario":"a-clean-checkout-runs-the-knowledge-build","graphRevision":"kg-v1-test"}`.
- Operation: inventory, validation, generation and the existing workbench build run from the same canonical inputs.
- Expected output: the commands SHALL succeed in a documented order and produce reproducible generated artifacts..
#### Scenario: Coverage regresses below the reviewed slice

- **WHEN** a generated revision maps fewer reviewed golden questions than the acceptance threshold
- **THEN** the build SHALL fail with coverage details and SHALL retain the last accepted generated artifacts.
##### Example:

- Fixture: `scenario-coverage-regresses-below-the-reviewed-slice` with input `{"scenario":"coverage-regresses-below-the-reviewed-slice","graphRevision":"kg-v1-test"}`.
- Operation: a generated revision maps fewer reviewed golden questions than the acceptance threshold.
- Expected output: the build SHALL fail with coverage details and SHALL retain the last accepted generated artifacts..
