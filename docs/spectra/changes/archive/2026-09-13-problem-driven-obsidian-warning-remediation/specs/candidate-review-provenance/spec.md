## Purpose

Define versioned candidate metadata and auditable reviewer receipts for the offline knowledge patch workflow.

## ADDED Requirements

### Requirement: Candidate schema SHALL enforce versioned metadata

Candidate validation SHALL require `candidateVersion: 1`, the versioned candidate schema, source issue event IDs, QID and exam family, bounded intent/evidence, likely question data, operation arrays, and expected node hashes. Missing required metadata SHALL fail closed before enqueue or write.

#### Scenario: A candidate omits candidateVersion

- **WHEN** a candidate otherwise looks structurally valid but lacks `candidateVersion`
- **THEN** inspection SHALL return a stable metadata error and SHALL not enqueue, approve, or write canonical data.

##### Example:

Input `{ "schemaVersion": "knowledge-patch-candidate.v1", "candidateId": "c1" }` produces error code `CANDIDATE_VERSION` and no output revision.

#### Scenario: A candidate carries complete versioned metadata

- **WHEN** a candidate includes `candidateVersion: 1`, current graph revision, source issue IDs, bounded operations, evidence, and expected hashes
- **THEN** inspection SHALL accept the metadata and return a reproducible candidate hash for review.

##### Example:

Input candidate `c1` with base revision `kg-v1-test` produces `{ "valid": true, "candidateVersion": 1, "candidateHash": "stable-for-same-input" }`.

### Requirement: Review records SHALL preserve reviewer and provenance metadata

Every reject or approve receipt SHALL include candidate hash, decision, reviewer identity, review timestamp, base graph revision, and a bounded reason or notes field. Approval SHALL also include the resulting graph revision.

#### Scenario: A reviewer rejects a candidate

- **WHEN** reviewer `sol` rejects candidate `c1` with a reason
- **THEN** the receipt SHALL preserve the reviewer, timestamp, candidate hash, decision, and reason while canonical data remains unchanged.

##### Example:

Input `{ "candidateId": "c1", "reviewerId": "sol", "decision": "rejected", "reason": "證據不足" }` produces a receipt with `status: "rejected"` and the same candidate hash.

#### Scenario: A reviewer approves a current candidate

- **WHEN** reviewer `sol` approves a candidate whose revision, hashes, evidence, and structure validate
- **THEN** the receipt SHALL record the base and resulting revisions and approval SHALL be atomic.

##### Example:

Input candidate `c1` at `kg-v1-a` produces a receipt containing `baseGraphRevision: "kg-v1-a"`, `graphRevision: "kg-v1-b"`, and `status: "approved"` only after the output directory validates.
