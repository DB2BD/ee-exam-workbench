#!/usr/bin/env python3
"""Reject broken bare LaTeX commands in canonical notes on the passive route."""

from __future__ import annotations

import re

try:
    from scripts.audit_passive_route_status import QID_RE, ROOT, ROUTE_DOCS, load_entries
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repo root package.
    from audit_passive_route_status import QID_RE, ROOT, ROUTE_DOCS, load_entries


BARE_COMMAND = re.compile(
    r"(?<!\\)(?:"
    r"\b(?:qquad|quad)\b|"
    r"\b(?:mathrm|mathbf|operatorname|begin|end|frac|sqrt|text)(?=\{)"
    r")"
)


def route_qids() -> set[str]:
    return set().union(
        *(
            set(QID_RE.findall(path.read_text(encoding="utf-8")))
            for path in ROUTE_DOCS
        )
    )


def visible_lines(source: str):
    """Yield non-fenced lines so labels such as ```text are not false positives."""
    in_fence = False
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line_number, line


def audit() -> list[str]:
    entries = load_entries()
    errors: list[str] = []
    qids = route_qids()
    if len(qids) != 94:
        errors.append(f"passive route expected 94 unique qids, found {len(qids)}")

    for qid in sorted(qids):
        entry = entries.get(qid)
        if entry is None:
            errors.append(f"{qid}: missing audit-manifest entry")
            continue
        path = ROOT / entry["solution_link"]
        if not path.is_file():
            errors.append(f"{qid}: missing canonical note {entry['solution_link']}")
            continue
        for line_number, line in visible_lines(path.read_text(encoding="utf-8")):
            for match in BARE_COMMAND.finditer(line):
                errors.append(
                    f"{qid}:{line_number}: bare LaTeX command {match.group()!r}"
                )
    return errors


def main() -> int:
    errors = audit()
    if errors:
        print(f"Passive-route math markup audit failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Passive-route math markup audit: 94/94 routed canonical notes are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
