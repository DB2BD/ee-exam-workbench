---
name: diagnose
description: Transforms bug fixing into a disciplined, 5-phase scientific loop instead of blind guessing.
---

# 🩺 Scientific Diagnose Skill

Eliminates "shotgun debugging" and blind trial-and-error by enforcing a **5-step scientific debugging loop**:

## 🔄 The 5-Phase Diagnostic Loop

```
1. 🔍 Observe & Reproduce ──► 2. 💡 Formulate Hypotheses ──► 3. 🔬 Minimal Instrumentation
                                                                    │
   5. 🛡️ Regression Test  ◄── 4. 🎯 Atomic Root-Cause Fix ◄───────┘
```

### Phase 1: Observe & Minimal Reproduction (觀察與極簡復現)
- Do NOT edit code immediately.
- Write a minimal script (`scripts/reproduce_*.py`) or command that reliably triggers the failure.
- Log the exact observed behavior vs expected behavior.

### Phase 2: Formulate Hypotheses (提出假說清單)
- Write down 1~3 explicit, falsifiable hypotheses regarding the root cause (e.g., "Hypothesis A: stale bundle key is shadowed by pre-loaded bundle", "Hypothesis B: regex failed on unicode escape").

### Phase 3: Minimal Instrumentation (最小探針度量)
- Add targeted print/log probes to inspect runtime variable states.
- Reject or confirm each hypothesis based on concrete evidence.

### Phase 4: Atomic Root-Cause Fix (針對根因之原子修復)
- Apply the minimal code change that directly addresses the proven root cause.
- Avoid wide, collateral changes.

### Phase 5: Regression Test & Verification (迴歸驗證與固化)
- Run `python3 scripts/run_all_tests.py` to confirm the fix and ensure zero regression across all 423 questions.
