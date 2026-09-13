## Purpose

Define an auditable time anchor for weakness projections so replay, UI filtering, and future-dated events have deterministic semantics.

## ADDED Requirements

### Requirement: Projection time anchor SHALL be explicit and auditable

The weakness projection SHALL accept an explicit ISO `now` for user-facing time filters and SHALL expose `timeAnchor` and `timeAnchorMode` in its output. A deterministic replay without `now` SHALL be permitted only when the output marks the latest event fallback as replay mode.

#### Scenario: The user opens the 30-day weakness view

- **WHEN** the UI calls `buildWeaknessProjection` with `range: "30d"` and `now: "2026-09-13T00:00:00.000Z"`
- **THEN** the result SHALL use that timestamp as `timeAnchor`, mark `timeAnchorMode` as explicit, and include only events inside the calculated window.

##### Example:

Input `{ "range": "30d", "now": "2026-09-13T00:00:00.000Z", "event.recordedAt": "2026-08-15T00:00:00.000Z" }` produces `{ "timeAnchor": "2026-09-13T00:00:00.000Z", "timeAnchorMode": "explicit", "included": true }`.

#### Scenario: A replay omits the wall-clock time

- **WHEN** a test rebuilds a projection without `now`
- **THEN** the result SHALL use the latest valid event timestamp only as a replay fallback and SHALL label the mode so it cannot be mistaken for a live query.

##### Example:

Input events ending at `2026-09-12T00:00:00.000Z` produce `{ "timeAnchor": "2026-09-12T00:00:00.000Z", "timeAnchorMode": "latest-event-replay" }`.

### Requirement: Time filters SHALL classify future and out-of-window events deterministically

Events later than the explicit time anchor or earlier than the selected cutoff SHALL be excluded from the active range and SHALL remain explainable through a stable exclusion or pending summary.

#### Scenario: An event is dated in the future

- **WHEN** an event is recorded at `2026-09-14T00:00:00.000Z` and the explicit anchor is `2026-09-13T00:00:00.000Z`
- **THEN** the event SHALL not enter the current weakness totals and the result SHALL expose a deterministic future-event exclusion reason.

##### Example:

Input `{ "recordedAt": "2026-09-14T00:00:00.000Z", "now": "2026-09-13T00:00:00.000Z" }` produces `totals.effectiveEventCount: 0` and exclusion code `FUTURE_THAN_TIME_ANCHOR`.

#### Scenario: An event is outside the selected range

- **WHEN** a 7-day projection is anchored at `2026-09-13T00:00:00.000Z` and an event is dated `2026-09-01T00:00:00.000Z`
- **THEN** the event SHALL be excluded from the active range without changing the all-time replay result.

##### Example:

Input `{ "range": "7d", "recordedAt": "2026-09-01T00:00:00.000Z" }` produces `included: false` for 7-day and remains present for `range: "all"`.
