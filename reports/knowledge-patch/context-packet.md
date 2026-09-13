# Knowledge Context Packet

- graphRevision: `kg-v1-e30faed9d5b5e0f0`
- selected nodes: 3

## Selected nodes
- `ct-procedure-thevenin-controlled-source` — 含受控源的戴維寧等效求解流程 (procedure, PE)
- `ct-thevenin-norton` — 戴維寧與諾頓等效定理 (mechanism, PE)
- `ps-per-unit` — 標么值 Per Unit 系統換算 (mechanism, PE)

## Related evidence
```json
{
  "edges": [
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ct-thevenin-norton"
      ],
      "from": "ct-divider-equiv",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-thevenin-norton",
      "why": "Thevenin/Norton reduction uses equivalent resistance and divider relations."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ct-thevenin-norton"
      ],
      "from": "ct-node-mesh",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-thevenin-norton",
      "why": "The open-circuit and test-source calculations require node or mesh analysis."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ct-first-order-rc-rl"
      ],
      "from": "ct-thevenin-norton",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-first-order-rc-rl",
      "why": "The first-order time constant uses the equivalent network seen by the storage element."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ct-thevenin-norton"
      ],
      "from": "ct-thevenin-norton",
      "relation": "enables",
      "reviewStatus": "approved",
      "to": "ct-procedure-thevenin-controlled-source",
      "why": "The controlled-source procedure applies the equivalent theorem with a test source."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "golden:domain-power-system"
      ],
      "from": "pe-mainline-power",
      "relation": "mainline_precedes",
      "reviewStatus": "approved",
      "to": "ps-per-unit",
      "why": "The power-system mainline starts by normalizing values on a common base."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ps-power-analysis"
      ],
      "from": "ps-per-unit",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ps-power-analysis",
      "why": "Power and phasor quantities are compared consistently after per-unit conversion."
    },
    {
      "confidence": 0.98,
      "evidence": [
        "src/data/knowledge-dag.js:ps-three-phase-fault"
      ],
      "from": "ps-per-unit",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ps-three-phase-fault",
      "why": "Symmetrical fault calculations use a common per-unit impedance base."
    }
  ],
  "questionLinks": {
    "PE:EE-114-01-2": {
      "confidence": 0.98,
      "evidence": [
        "dashboard-data.js:EE-114-01-2",
        "src/data/knowledge-dag.js:ct-thevenin-norton"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ct-thevenin-norton",
        "ct-procedure-thevenin-controlled-source"
      ],
      "qid": "EE-114-01-2",
      "reviewStatus": "approved",
      "sourcePriority": "manual"
    },
    "PE:EE-114-05-1": {
      "confidence": 0.96,
      "evidence": [
        "dashboard-data.js:EE-114-05-1",
        "src/data/knowledge-dag.js:ps-per-unit"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ps-per-unit"
      ],
      "qid": "EE-114-05-1",
      "reviewStatus": "approved",
      "sourcePriority": "deterministic"
    }
  }
}
```

## Bounded issue history
