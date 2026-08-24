---
name: improve-codebase-architecture
description: Conducts periodic codebase health checks, calculates architecture entropy score, and proactively eliminates architectural debt.
---

# 🏛️ Improve Codebase Architecture Skill

Fights **software entropy** by conducting systematic, periodic codebase health checks and architectural refactoring.

## 🩺 Periodic Health Check Routine

Run `python3 scripts/health_check_codebase.py` to evaluate:

1. **Dead & Stale File Detection**: Identifies temporary scratch scripts, unlinked assets, and deprecated generator scripts.
2. **Database Integrity & Bundling Health**: Verifies that 100% of raw markdown documents and images are compiled into the offline database bundles.
3. **Architectural Drift Detection**: Verifies that the codebase still adheres to `CONTEXT.md` invariants (zero-backend, dual database isolation, golden standard solution formatting).
4. **Automated Entropy Scoring**: Outputs an Architecture Health Score (0 ~ 100).
5. **Actionable Refactoring Plan**: Generates concrete cleanup commands to maintain codebase pristine condition.
