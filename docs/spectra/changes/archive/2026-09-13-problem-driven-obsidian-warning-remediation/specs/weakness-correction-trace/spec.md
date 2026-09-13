## Purpose

Define a bounded, inspectable supersession chain for corrected diagnosis events while preserving append-only raw history and effective counting.

## ADDED Requirements

### Requirement: Correction projection SHALL retain a traversable supersession chain

For a weakness with one or more correction events, the projection SHALL expose an ordered `supersessionChain` containing the relevant original and correction event summaries, their predecessor IDs, and a boolean `effective` marker.

#### Scenario: A correction replaces an earlier diagnosis

- **WHEN** event `e2` corrects event `e1` through `supersedesEventId`
- **THEN** the weakness SHALL count the effective event once and expose both `e1` and `e2` in a traversable chain.

##### Example:

Input `{ "e1": { "eventId": "e1", "eventType": "confirm" }, "e2": { "eventId": "e2", "eventType": "correct", "supersedesEventId": "e1" } }` produces `rawCount: 1` and `supersessionChain: [{ "eventId": "e1", "effective": false }, { "eventId": "e2", "effective": true }]`.

#### Scenario: A correction predecessor is missing

- **WHEN** a correction references an event ID absent from the imported stream
- **THEN** the projection SHALL preserve the correction evidence, mark the chain incomplete, and report the missing predecessor without inventing a replacement node.

##### Example:

Input `{ "eventId": "e2", "supersedesEventId": "missing-e1" }` produces `traceStatus: "incomplete"` and `missingEventIds: ["missing-e1"]`.

### Requirement: Correction state SHALL distinguish effective and historical evidence

Drill-down output SHALL separate effective events used for counts from historical events retained for audit, and SHALL expose the resulting review state without mutating the raw event stream.

#### Scenario: A user opens a corrected weakness

- **WHEN** the user drills into a weakness after submitting a correction
- **THEN** the UI SHALL show the current review state first and allow the user to expand the historical event evidence.

##### Example:

Input projection for `e1 -> e2` produces `{ "reviewState": "corrected", "effectiveEventIds": ["e2"], "historicalEventIds": ["e1"] }`.

#### Scenario: The same stream is projected twice

- **WHEN** the same correction stream and graph revision are projected twice
- **THEN** both chain ordering and effective/historical classification SHALL be identical.

##### Example:

Two calls with the same JSON bytes produce the same `supersessionChain` array and the same `traceStatus`.
