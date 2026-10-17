#!/usr/bin/env python3
"""Rebuild data/solution-logic-registry.json.

The registry lists every QID whose canonical note already carries the
``**解題邏輯**：`` paragraph; lint_canonical_notes.py enforces the v1.5.0
solution-logic rules on those QIDs permanently.  Run this after rewriting notes.

    python3 scripts/update_solution_logic_registry.py          # rewrite registry
    python3 scripts/update_solution_logic_registry.py --check  # exit 1 if stale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "02_題解/技師題解"
REGISTRY = ROOT / "data/solution-logic-registry.json"
MARKER = "**解題邏輯**："
DESCRIPTION = (
    "QIDs whose canonical note was rewritten to the v1.5.0 solution-logic standard; "
    "lint_canonical_notes.py enforces 解題邏輯/邏輯 on them. Regenerate with "
    "scripts/update_solution_logic_registry.py."
)


def scan(notes: Path = NOTES) -> list[str]:
    return sorted(
        path.stem
        for path in notes.glob("0*/canonical/EE-*.md")
        if MARKER in path.read_text(encoding="utf-8")
    )


def render(qids: list[str]) -> str:
    return json.dumps({"version": 1, "description": DESCRIPTION, "qids": qids}, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 if the registry is stale")
    args = parser.parse_args(argv)
    qids = scan()
    current = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    if args.check:
        try:
            registered = set(json.loads(current).get("qids", []))
        except ValueError:
            registered = set()
        lost = sorted(registered - set(qids))
        added = sorted(set(qids) - registered)
        if lost:
            print(f"registered notes lost {MARKER}: {', '.join(lost)}")
        if added:
            print(f"notes missing from registry: {', '.join(added)}")
        if lost or added:
            print("run: python3 scripts/update_solution_logic_registry.py")
            return 1
        print(f"solution-logic registry OK ({len(qids)} qids)")
        return 0
    REGISTRY.write_text(render(qids), encoding="utf-8")
    print(f"registry: {len(qids)} qids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
