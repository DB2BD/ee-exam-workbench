# weakness-correction-trace Specification

## Purpose

Define a bounded, inspectable supersession chain for corrected diagnosis events while preserving append-only raw history and effective counting.

## Requirements

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


<!-- @trace
source: problem-driven-obsidian-warning-remediation
updated: 2026-09-13
code:
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-complex-power.md
  - 🧠 問題驅動知識庫/01_電路學/q-ee-114-01-2.md
  - 🧠 問題驅動知識庫/03_工程數學/q-ee-114-03-1.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-autotransformer.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-three-phase-transformer.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-magnetic-circuits.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-active-filter.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-math.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-active-filter.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-matrix-det-inv.md
  - 🧠 問題驅動知識庫/01_電路學/ct-laplace-circuit.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-single-phase-transformer.md
  - index.html
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-math.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-arc-flash-ieee80.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-distribution-equipment.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-system-protection-relay.md
  - scripts/run_change_acceptance.py
  - 🧠 問題驅動知識庫/01_電路學/ct-divider-equiv.md
  - 🧠 問題驅動知識庫/01_電路學/ct-max-power.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-synchronous-salient-pole.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-power-analysis.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-svd-linear-systems.md
  - 🧠 問題驅動知識庫/03_工程數學/em-first-order-ode.md
  - 🧠 問題驅動知識庫/03_工程數學/em-second-order-ode-homogeneous.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-synchronous-generator-round.md
  - docs/WORKPLAN_Sol_Luna_Obsidian多使用者個人化複習整合_2026-09-13.md
  - scripts/knowledge_graph_inventory.py
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-power.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-motor-installation.md
  - 🧠 問題驅動知識庫/01_電路學/ct-superposition.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-machines.md
  - 🧠 問題驅動知識庫/01_電路學/ct-mutual-inductance.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-second-order-rlc.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-per-unit.md
  - docs/PROPOSAL_問題驅動Obsidian知識圖譜_2026-09-12.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-protection-coordination.md
  - data/knowledge/question-links.json
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-unsymmetrical-faults.md
  - scripts/acceptance_freshness.py
  - src/styles/components.css
  - scripts/generate_full_knowledge_graph.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-mosfet-bias-small-signal.md
  - .agents/skills/spectra-discuss/SKILL.md
  - data/knowledge/migration-inventory.json
  - reports/learning-data-capacity.json
  - scripts/validate_knowledge_graph.py
  - 🧠 問題驅動知識庫/03_工程數學/em-complex-cauchy-residue.md
  - 🧠 問題驅動知識庫/01_電路學/ct-complex-power.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q05.png
  - 🧠 問題驅動知識庫/05_電力系統/ps-transmission-line-params.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-power-analysis.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-vector-analysis.md
  - .spectra.yaml
  - 🧠 問題驅動知識庫/01_電路學/ct-thevenin-norton.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-induction-motor-equiv.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-transmission-line-models.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-economic-dispatch.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-bjt-bias-small-signal.md
  - scripts/generate_obsidian_knowledge.py
  - 🧠 問題驅動知識庫/01_電路學/ct-first-order-rc-rl.md
  - .agents/skills/spectra-review/SKILL.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-system-protection-relay.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-diff-amp.md
  - 🧠 問題驅動知識庫/03_工程數學/em-svd-linear-systems.md
  - .obsidian/graph.json
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-inverter-spwm.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-short-circuit-capacity.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-induction-motor-equiv.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-unsymmetrical-faults.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-induction-motor-torque.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-laplace-transform.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-load-flow-admittance.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-analyze/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-buck-boost.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-dc-motor-generator.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-max-power.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-feedback-stability.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-node-mesh.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-dc-motor-generator.md
  - data/knowledge/schema.json
  - 🧠 問題驅動知識庫/01_電路學/ct-procedure-thevenin-controlled-source.md
  - src/main.js
  - reports/knowledge-graph-validation.json
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-first-order-ode.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-harmonics-mitigation.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-symmetrical-components.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-two-port.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-load-characteristics.md
  - docs/PROPOSAL_Obsidian多使用者個人化複習整合_2026-09-13.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-superposition.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-load-flow-admittance.md
  - reports/problem-driven-obsidian-acceptance.json
  - src/domain/weaknessProjection.js
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q04.png
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-machines.md
  - scripts/crop_pe_questions.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-thyristor-rectifier.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-second-order-ode-nonhomogeneous.md
  - 🧠 問題驅動知識庫/03_工程數學/em-second-order-ode-nonhomogeneous.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-complex-cauchy-residue.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-state-estimation-wls.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-procedure-slg-sequence-networks.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-symmetrical-components.md
  - 🧠 問題驅動知識庫/05_電力系統/q-ee-114-05-4.md
  - 🧠 問題驅動知識庫/01_電路學/ct-second-order-rlc.md
  - .agents/skills/spectra-verify/SKILL.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q03.png
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-opamp-ideal.md
  - scripts/build_knowledge_graph.py
  - 🧠 問題驅動知識庫/05_電力系統/ps-per-unit.md
  - solutions-bundle.js
  - .obsidian/workspace.json
  - 🧠 問題驅動知識庫/04_電機機械/emach-three-phase-transformer.md
  - src/components/dagTracer.js
  - src/data/knowledge-dag.js
  - 🧠 問題驅動知識庫/03_工程數學/em-vector-analysis.md
  - 🧠 問題驅動知識庫/01_電路學/ct-three-phase.md
  - data/knowledge/nodes.json
  - data/pe-question-crops.json
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-probability-statistics.md
  - .agents/skills/spectra-commit/SKILL.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-thevenin-norton.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-power-factor-correction.md
  - reports/knowledge-graph-build.json
  - .agents/skills/spectra-ingest/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-diode-rectifier.md
  - src/state/sm2Store.js
  - .agents/skills/spectra-audit/SKILL.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-pde-separation.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-economic-dispatch.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transmission-line-models.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-state-estimation-wls.md
  - scripts/write_unresolved_report.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-inverter-spwm.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q06.png
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-second-order-ode-homogeneous.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-circuit.md
  - .agents/skills/spectra-drift/SKILL.md
  - 🧠 問題驅動知識庫/01_電路學/ct-node-mesh.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-thyristor-rectifier.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-divider-equiv.md
  - scripts/knowledge_graph.py
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-first-order-rc-rl.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-phasor-ac.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-voltage-drop.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transmission-line-params.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-three-phase-fault.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-power.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-ohm-kcl-kvl.md
  - reports/knowledge-patch/context-packet.md
  - reports/problem-driven-unresolved.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-mosfet-bias-small-signal.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transient-stability-equal-area.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-three-phase.md
  - 🧠 問題驅動知識庫/03_工程數學/em-matrix-det-inv.md
  - 🧠 問題驅動知識庫/03_工程數學/em-procedure-linear-systems.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-electronics.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-zener-regulator.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-opamp-ideal.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-autotransformer.md
  - reports/knowledge-graph-inventory.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-laplace-circuit.md
  - src/state/attemptStore.js
  - src/components/solutionModal.js
  - src/state/knowledgeIssueStore.js
  - reports/knowledge-patch/context-packet.json
  - docs/WORKPLAN_Sol_Luna_問題驅動Obsidian知識圖譜_2026-09-12.md
  - 🧠 問題驅動知識庫/03_工程數學/em-probability-statistics.md
  - 🧠 問題驅動知識庫/03_工程數學/em-laplace-transform.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-fourier-series.md
  - scripts/knowledge_patch_workflow.py
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-mutual-inductance.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-lighting-design.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-grounding-system.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-three-phase-fault.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-electronics.md
  - 🧠 問題驅動知識庫/03_工程數學/em-eigen-diagonal.md
  - src/state/knowledgeReviewStore.js
  - src/domain/knowledgeDiagnosis.js
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-zener-regulator.md
  - 🧠 問題驅動知識庫/01_電路學/ct-two-port.md
  - .agents/skills/spectra-archive/SKILL.md
  - scripts/build_workbench.py
  - src/components/weaknessView.js
  - AGENTS.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-magnetic-circuits.md
  - 🧠 問題驅動知識庫/01_電路學/ct-ohm-kcl-kvl.md
  - src/components/dagGraphViewer.js
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-bjt-bias-small-signal.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-induction-motor-torque.md
  - 🧠 問題驅動知識庫/01_電路學/ct-phasor-ac.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-diff-amp.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-transient-stability-equal-area.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-circuit.md
  - src/components/topTopics.js
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-single-phase-transformer.md
  - data/knowledge/golden-fixture.json
  - src/components/questionList.js
  - 🧠 問題驅動知識庫/03_工程數學/em-fourier-series.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-synchronous-generator-round.md
  - src/data/knowledge-dag.generated.js
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-synchronous-salient-pole.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-diode-rectifier.md
  - reports/obsidian-knowledge-build.json
  - 🧠 問題驅動知識庫/03_工程數學/em-pde-separation.md
  - data/knowledge/edges.json
  - .agents/skills/spectra-propose/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-feedback-stability.md
  - src/components/reviewPage.js
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-eigen-diagonal.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-buck-boost.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-distribution.md
  - 🧠 問題驅動知識庫/01_電路學/q-ee-114-01-3.md
  - .agents/skills/spectra-debug/SKILL.md
  - scripts/measure_learning_data_capacity.py
tests:
  - tests/test_full_knowledge_graph.py
  - tests/test_question_facets.py
  - tests/test_backup_restore.py
  - tests/test_knowledge_graph_inventory.py
  - tests/test_weakness_view.py
  - tests/test_knowledge_graph_schema.py
  - tests/test_diagnosis_ui.py
  - tests/test_learning_data_capacity.py
  - tests/test_knowledge_graph_validator_cli.py
  - tests/test_knowledge_graph_generation.py
  - tests/test_knowledge_graph_adapter.py
  - tests/test_pe_question_crops.py
  - tests/test_knowledge_diagnosis.py
  - tests/test_knowledge_review_store.py
  - tests/test_knowledge_issue_store.py
  - tests/test_acceptance_freshness.py
  - tests/test_durable_attempt_store.py
  - tests/test_spectra_scenario_examples.py
  - tests/test_weakness_projection.py
  - tests/test_topic_statistics.py
  - tests/test_obsidian_knowledge_generation.py
  - tests/test_knowledge_patch_workflow.py
-->

---
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

<!-- @trace
source: problem-driven-obsidian-warning-remediation
updated: 2026-09-13
code:
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-complex-power.md
  - 🧠 問題驅動知識庫/01_電路學/q-ee-114-01-2.md
  - 🧠 問題驅動知識庫/03_工程數學/q-ee-114-03-1.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-autotransformer.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-three-phase-transformer.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-magnetic-circuits.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-active-filter.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-math.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-active-filter.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-matrix-det-inv.md
  - 🧠 問題驅動知識庫/01_電路學/ct-laplace-circuit.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-single-phase-transformer.md
  - index.html
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-math.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-arc-flash-ieee80.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-distribution-equipment.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-system-protection-relay.md
  - scripts/run_change_acceptance.py
  - 🧠 問題驅動知識庫/01_電路學/ct-divider-equiv.md
  - 🧠 問題驅動知識庫/01_電路學/ct-max-power.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-synchronous-salient-pole.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-power-analysis.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-svd-linear-systems.md
  - 🧠 問題驅動知識庫/03_工程數學/em-first-order-ode.md
  - 🧠 問題驅動知識庫/03_工程數學/em-second-order-ode-homogeneous.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-synchronous-generator-round.md
  - docs/WORKPLAN_Sol_Luna_Obsidian多使用者個人化複習整合_2026-09-13.md
  - scripts/knowledge_graph_inventory.py
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-power.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-motor-installation.md
  - 🧠 問題驅動知識庫/01_電路學/ct-superposition.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-machines.md
  - 🧠 問題驅動知識庫/01_電路學/ct-mutual-inductance.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-second-order-rlc.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-per-unit.md
  - docs/PROPOSAL_問題驅動Obsidian知識圖譜_2026-09-12.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-protection-coordination.md
  - data/knowledge/question-links.json
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-unsymmetrical-faults.md
  - scripts/acceptance_freshness.py
  - src/styles/components.css
  - scripts/generate_full_knowledge_graph.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-mosfet-bias-small-signal.md
  - .agents/skills/spectra-discuss/SKILL.md
  - data/knowledge/migration-inventory.json
  - reports/learning-data-capacity.json
  - scripts/validate_knowledge_graph.py
  - 🧠 問題驅動知識庫/03_工程數學/em-complex-cauchy-residue.md
  - 🧠 問題驅動知識庫/01_電路學/ct-complex-power.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q05.png
  - 🧠 問題驅動知識庫/05_電力系統/ps-transmission-line-params.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-power-analysis.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-vector-analysis.md
  - .spectra.yaml
  - 🧠 問題驅動知識庫/01_電路學/ct-thevenin-norton.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-induction-motor-equiv.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-transmission-line-models.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-economic-dispatch.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-bjt-bias-small-signal.md
  - scripts/generate_obsidian_knowledge.py
  - 🧠 問題驅動知識庫/01_電路學/ct-first-order-rc-rl.md
  - .agents/skills/spectra-review/SKILL.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-system-protection-relay.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-diff-amp.md
  - 🧠 問題驅動知識庫/03_工程數學/em-svd-linear-systems.md
  - .obsidian/graph.json
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-inverter-spwm.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-short-circuit-capacity.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-induction-motor-equiv.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-unsymmetrical-faults.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-induction-motor-torque.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-laplace-transform.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-load-flow-admittance.md
  - .agents/skills/spectra-apply/SKILL.md
  - .agents/skills/spectra-analyze/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-buck-boost.md
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-dc-motor-generator.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-max-power.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-feedback-stability.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-node-mesh.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-dc-motor-generator.md
  - data/knowledge/schema.json
  - 🧠 問題驅動知識庫/01_電路學/ct-procedure-thevenin-controlled-source.md
  - src/main.js
  - reports/knowledge-graph-validation.json
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-first-order-ode.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-harmonics-mitigation.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-symmetrical-components.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-two-port.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-load-characteristics.md
  - docs/PROPOSAL_Obsidian多使用者個人化複習整合_2026-09-13.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-superposition.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-load-flow-admittance.md
  - reports/problem-driven-obsidian-acceptance.json
  - src/domain/weaknessProjection.js
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q04.png
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-machines.md
  - scripts/crop_pe_questions.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-thyristor-rectifier.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-second-order-ode-nonhomogeneous.md
  - 🧠 問題驅動知識庫/03_工程數學/em-second-order-ode-nonhomogeneous.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-complex-cauchy-residue.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-state-estimation-wls.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-procedure-slg-sequence-networks.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-symmetrical-components.md
  - 🧠 問題驅動知識庫/05_電力系統/q-ee-114-05-4.md
  - 🧠 問題驅動知識庫/01_電路學/ct-second-order-rlc.md
  - .agents/skills/spectra-verify/SKILL.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q03.png
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-opamp-ideal.md
  - scripts/build_knowledge_graph.py
  - 🧠 問題驅動知識庫/05_電力系統/ps-per-unit.md
  - solutions-bundle.js
  - .obsidian/workspace.json
  - 🧠 問題驅動知識庫/04_電機機械/emach-three-phase-transformer.md
  - src/components/dagTracer.js
  - src/data/knowledge-dag.js
  - 🧠 問題驅動知識庫/03_工程數學/em-vector-analysis.md
  - 🧠 問題驅動知識庫/01_電路學/ct-three-phase.md
  - data/knowledge/nodes.json
  - data/pe-question-crops.json
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-probability-statistics.md
  - .agents/skills/spectra-commit/SKILL.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-thevenin-norton.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-power-factor-correction.md
  - reports/knowledge-graph-build.json
  - .agents/skills/spectra-ingest/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-diode-rectifier.md
  - src/state/sm2Store.js
  - .agents/skills/spectra-audit/SKILL.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-pde-separation.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-economic-dispatch.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transmission-line-models.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-state-estimation-wls.md
  - scripts/write_unresolved_report.py
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-inverter-spwm.md
  - 依考科分類/05_電力系統/images/questions/PE_109年_電力系統_Q06.png
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-second-order-ode-homogeneous.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-circuit.md
  - .agents/skills/spectra-drift/SKILL.md
  - 🧠 問題驅動知識庫/01_電路學/ct-node-mesh.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-pe-thyristor-rectifier.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-divider-equiv.md
  - scripts/knowledge_graph.py
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-first-order-rc-rl.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-phasor-ac.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-voltage-drop.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transmission-line-params.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-three-phase-fault.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-power.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-ohm-kcl-kvl.md
  - reports/knowledge-patch/context-packet.md
  - reports/problem-driven-unresolved.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-mosfet-bias-small-signal.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-transient-stability-equal-area.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-three-phase.md
  - 🧠 問題驅動知識庫/03_工程數學/em-matrix-det-inv.md
  - 🧠 問題驅動知識庫/03_工程數學/em-procedure-linear-systems.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-electronics.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-zener-regulator.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-opamp-ideal.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-autotransformer.md
  - reports/knowledge-graph-inventory.md
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-laplace-circuit.md
  - src/state/attemptStore.js
  - src/components/solutionModal.js
  - src/state/knowledgeIssueStore.js
  - reports/knowledge-patch/context-packet.json
  - docs/WORKPLAN_Sol_Luna_問題驅動Obsidian知識圖譜_2026-09-12.md
  - 🧠 問題驅動知識庫/03_工程數學/em-probability-statistics.md
  - 🧠 問題驅動知識庫/03_工程數學/em-laplace-transform.md
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-fourier-series.md
  - scripts/knowledge_patch_workflow.py
  - 🧠 問題驅動知識庫/01_電路學/gk-ct-mutual-inductance.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-lighting-design.md
  - 🧠 問題驅動知識庫/06_工業配電/dist-grounding-system.md
  - 🧠 問題驅動知識庫/05_電力系統/gk-ps-three-phase-fault.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-electronics.md
  - 🧠 問題驅動知識庫/03_工程數學/em-eigen-diagonal.md
  - src/state/knowledgeReviewStore.js
  - src/domain/knowledgeDiagnosis.js
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-zener-regulator.md
  - 🧠 問題驅動知識庫/01_電路學/ct-two-port.md
  - .agents/skills/spectra-archive/SKILL.md
  - scripts/build_workbench.py
  - src/components/weaknessView.js
  - AGENTS.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-magnetic-circuits.md
  - 🧠 問題驅動知識庫/01_電路學/ct-ohm-kcl-kvl.md
  - src/components/dagGraphViewer.js
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-bjt-bias-small-signal.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-induction-motor-torque.md
  - 🧠 問題驅動知識庫/01_電路學/ct-phasor-ac.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-diff-amp.md
  - 🧠 問題驅動知識庫/05_電力系統/ps-transient-stability-equal-area.md
  - 🧠 問題驅動知識庫/00_主線/gk-mainline-circuit.md
  - src/components/topTopics.js
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-single-phase-transformer.md
  - data/knowledge/golden-fixture.json
  - src/components/questionList.js
  - 🧠 問題驅動知識庫/03_工程數學/em-fourier-series.md
  - 🧠 問題驅動知識庫/04_電機機械/emach-synchronous-generator-round.md
  - src/data/knowledge-dag.generated.js
  - 🧠 問題驅動知識庫/04_電機機械/gk-emach-synchronous-salient-pole.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-diode-rectifier.md
  - reports/obsidian-knowledge-build.json
  - 🧠 問題驅動知識庫/03_工程數學/em-pde-separation.md
  - data/knowledge/edges.json
  - .agents/skills/spectra-propose/SKILL.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/el-feedback-stability.md
  - src/components/reviewPage.js
  - 🧠 問題驅動知識庫/03_工程數學/gk-em-eigen-diagonal.md
  - 🧠 問題驅動知識庫/02_電子學_含電力電子/gk-el-pe-buck-boost.md
  - 🧠 問題驅動知識庫/00_主線/pe-mainline-distribution.md
  - 🧠 問題驅動知識庫/01_電路學/q-ee-114-01-3.md
  - .agents/skills/spectra-debug/SKILL.md
  - scripts/measure_learning_data_capacity.py
tests:
  - tests/test_full_knowledge_graph.py
  - tests/test_question_facets.py
  - tests/test_backup_restore.py
  - tests/test_knowledge_graph_inventory.py
  - tests/test_weakness_view.py
  - tests/test_knowledge_graph_schema.py
  - tests/test_diagnosis_ui.py
  - tests/test_learning_data_capacity.py
  - tests/test_knowledge_graph_validator_cli.py
  - tests/test_knowledge_graph_generation.py
  - tests/test_knowledge_graph_adapter.py
  - tests/test_pe_question_crops.py
  - tests/test_knowledge_diagnosis.py
  - tests/test_knowledge_review_store.py
  - tests/test_knowledge_issue_store.py
  - tests/test_acceptance_freshness.py
  - tests/test_durable_attempt_store.py
  - tests/test_spectra_scenario_examples.py
  - tests/test_weakness_projection.py
  - tests/test_topic_statistics.py
  - tests/test_obsidian_knowledge_generation.py
  - tests/test_knowledge_patch_workflow.py
-->