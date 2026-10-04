# Knowledge Context Packet

- graphRevision: `kg-v1-94aec3f278d6e297`
- selected nodes: 3

## Selected nodes
- `ct-procedure-thevenin-controlled-source` — 含受控源的戴維寧等效求解流程 (procedure, PE)
- `ct-thevenin-norton` — 戴維寧與諾頓等效定理 (mechanism, PE)
- `ps-per-unit` — 標么值 (Per-Unit) 系統換算 (mechanism, PE)

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
        "src/data/knowledge-dag.js:ct-first-order-rc-rl"
      ],
      "from": "ct-thevenin-norton",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-first-order-rc-rl",
      "why": "The first-order time constant uses the equivalent network seen by the storage element."
    },
    {
      "confidence": 0.95,
      "evidence": [
        "src/data/knowledge-dag.js:ct-max-power",
        "migration:explicit-legacy-prereq"
      ],
      "from": "ct-thevenin-norton",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-max-power",
      "why": "掌握「最大功率轉移定理」前，先建立「戴維寧與諾頓等效定理」這個前置概念。"
    },
    {
      "confidence": 0.95,
      "evidence": [
        "src/data/knowledge-dag.js:ct-two-port",
        "migration:explicit-legacy-prereq"
      ],
      "from": "ct-thevenin-norton",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ct-two-port",
      "why": "掌握「雙埠網路參數 (ABCD, Z, Y, H)」前，先建立「戴維寧與諾頓等效定理」這個前置概念。"
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
      "confidence": 0.95,
      "evidence": [
        "src/data/knowledge-dag.js:ps-economic-dispatch",
        "migration:explicit-legacy-prereq"
      ],
      "from": "ps-per-unit",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ps-economic-dispatch",
      "why": "掌握「經濟調度與發電協調方程式」前，先建立「標么值 (Per-Unit) 系統換算」這個前置概念。"
    },
    {
      "confidence": 0.95,
      "evidence": [
        "src/data/knowledge-dag.js:ps-load-flow-admittance",
        "migration:explicit-legacy-prereq"
      ],
      "from": "ps-per-unit",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ps-load-flow-admittance",
      "why": "掌握「電力潮流與導納矩陣」前，先建立「標么值 (Per-Unit) 系統換算」這個前置概念。"
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
      "confidence": 0.95,
      "evidence": [
        "src/data/knowledge-dag.js:ps-symmetrical-components",
        "migration:explicit-legacy-prereq"
      ],
      "from": "ps-per-unit",
      "relation": "prerequisite",
      "reviewStatus": "approved",
      "to": "ps-symmetrical-components",
      "why": "掌握「對稱分量法 (正序、負序、零序網)」前，先建立「標么值 (Per-Unit) 系統換算」這個前置概念。"
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
    "PE:EE-104-01-1": {
      "confidence": 0.9,
      "evidence": [
        "dashboard-data.js:EE-104-01-1",
        "data/taxonomy/alias-map.json:ct-thevenin-norton"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ct-thevenin-norton"
      ],
      "qid": "EE-104-01-1",
      "reviewStatus": "approved",
      "sourcePriority": "deterministic"
    },
    "PE:EE-105-01-2": {
      "confidence": 0.9,
      "evidence": [
        "dashboard-data.js:EE-105-01-2",
        "data/taxonomy/alias-map.json:ct-thevenin-norton"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ct-thevenin-norton"
      ],
      "qid": "EE-105-01-2",
      "reviewStatus": "approved",
      "sourcePriority": "deterministic"
    },
    "PE:EE-112-01-3": {
      "confidence": 0.9,
      "evidence": [
        "dashboard-data.js:EE-112-01-3",
        "data/taxonomy/alias-map.json:ct-thevenin-norton"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ct-thevenin-norton"
      ],
      "qid": "EE-112-01-3",
      "reviewStatus": "approved",
      "sourcePriority": "deterministic"
    },
    "PE:EE-114-01-2": {
      "confidence": 0.9,
      "evidence": [
        "dashboard-data.js:EE-114-01-2",
        "data/taxonomy/alias-map.json:ct-thevenin-norton"
      ],
      "examFamily": "PE",
      "nodeIds": [
        "ct-thevenin-norton"
      ],
      "qid": "EE-114-01-2",
      "reviewStatus": "approved",
      "sourcePriority": "deterministic"
    }
  }
}
```

## Bounded issue history
