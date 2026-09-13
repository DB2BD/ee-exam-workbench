## Purpose

Define concrete example coverage for Spectra requirements so implementers and analyzers can connect each scenario to observable input and output.

## ADDED Requirements

### Requirement: Spectra scenarios SHALL include concrete examples

Every scenario introduced or modified by this change SHALL include one `##### Example:` block with a bounded input, an operation or condition, and an observable output. The existing problem-driven graph specs affected by this change SHALL receive equivalent examples.

#### Scenario: A new requirement is authored

- **WHEN** an author adds a requirement with one or more scenarios
- **THEN** each scenario SHALL include a concrete example that can be mapped to a test, fixture, or CLI result.

##### Example:

Input `{ "requirement": "Projection time anchor SHALL be explicit and auditable", "scenarioCount": 2 }` is invalid until both scenarios contain `##### Example:` blocks.

#### Scenario: The analyzer checks the completed change

- **WHEN** `spectra analyze problem-driven-obsidian-warning-remediation --json` runs after artifacts are complete
- **THEN** it SHALL find no missing example suggestion for the new capability scenarios and SHALL report any remaining affected existing scenario explicitly.

##### Example:

Input analyzer output with `missingExamples: []` produces a clean example-coverage result for this change.
