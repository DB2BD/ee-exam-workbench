## Purpose

Define one current-revision identity for acceptance, canonical graph, website, Obsidian, capacity, and recovery reports.

## ADDED Requirements

### Requirement: Acceptance reports SHALL be generated from current graph revision

Acceptance and generated-output reports SHALL include `generatedAt`, `graphRevision`, source identity, output identity, checks, and blocking failures. The gate SHALL reject missing or mismatched revision/hash metadata as stale.

#### Scenario: All reports refer to the current graph

- **WHEN** canonical validation, website generation, and Obsidian generation complete for the same graph revision
- **THEN** the acceptance report SHALL record that revision and pass the freshness check.

##### Example:

Input reports all carrying `graphRevision: "kg-v1-97a9a9a3fcd6334b"` produce `freshnessPass: true`.

#### Scenario: An old report is mixed into a new acceptance run

- **WHEN** one report carries `kg-v1-old` while canonical validation carries `kg-v1-current`
- **THEN** the gate SHALL mark the report stale, identify the mismatched artifact, and block promotion.

##### Example:

Input revisions `{ "canonical": "kg-v1-current", "obsidian": "kg-v1-old" }` produces error code `STALE_REPORT_REVISION` and `passed: false`.

### Requirement: Recovery acceptance SHALL record measured time and thresholds

Recovery fixtures SHALL record measured recovery time, configured threshold, pass/fail, event capacity, issue bytes, and backup bytes in machine-readable reports. An absent measurement SHALL fail the recovery acceptance gate.

#### Scenario: Recovery completes within the configured threshold

- **WHEN** a crash recovery takes 42 ms against a 250 ms threshold
- **THEN** the report SHALL record both values and set `recoveryTimePass: true`.

##### Example:

Input `{ "recoveryTimeMs": 42, "recoveryTimeThresholdMs": 250 }` produces `{ "recoveryTimePass": true }`.

#### Scenario: Recovery time is not measured

- **WHEN** a capacity run reports event count and bytes but no recovery time
- **THEN** the acceptance gate SHALL fail with an actionable missing-measurement code.

##### Example:

Input `{ "measuredIssueEventCount": 5000, "measuredIssueBytes": 2757890 }` produces error code `RECOVERY_TIME_MISSING`.
