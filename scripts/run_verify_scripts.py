#!/usr/bin/env python3
"""Run the independent per-question verification scripts in ``verification/pe/``.

Each ``verification/pe/EE-YYY-SS-N.py`` solves its question from the official
crop's givens (SymPy/NumPy), asserts every boxed answer of the canonical note
and exits non-zero on mismatch.  A lean-v1 note whose status is ``verified``
or ``reference_book_verified`` must have one.

Usage::

    python3 scripts/run_verify_scripts.py               # run all scripts
    python3 scripts/run_verify_scripts.py EE-114-05-3   # run selected QIDs
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_DIR = ROOT / "verification" / "pe"
NOTES = ROOT / "02_題解/技師題解"
TIMEOUT_SECONDS = 120
NEEDS_SCRIPT = {"verified", "reference_book_verified"}


def lean_notes_needing_scripts() -> list[str]:
    qids = []
    for path in sorted(NOTES.glob("0*/canonical/EE-*.md")):
        head = path.read_text(encoding="utf-8").split("---", 2)[1]
        lean = re.search(r"^template:\s*lean-v1\s*$", head, re.M)
        status = re.search(r"^audit_status:\s*(\S+)", head, re.M)
        if lean and status and status.group(1) in NEEDS_SCRIPT:
            qids.append(path.stem)
    return qids


def run(script: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout after {TIMEOUT_SECONDS}s"
    output = (result.stdout + result.stderr).strip().splitlines()
    return result.returncode == 0, output[-1] if output else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qids", nargs="*")
    args = parser.parse_args(argv)

    scripts = sorted(VERIFY_DIR.glob("EE-*.py"))
    if args.qids:
        scripts = [script for script in scripts if script.stem in set(args.qids)]
    failures = []
    for script in scripts:
        ok, tail = run(script)
        print(f"{'PASS' if ok else 'FAIL'} {script.stem}: {tail}")
        if not ok:
            failures.append(script.stem)

    available = {script.stem for script in VERIFY_DIR.glob("EE-*.py")}
    required = lean_notes_needing_scripts()
    if args.qids:
        required = [qid for qid in required if qid in set(args.qids)]
    missing = [qid for qid in required if qid not in available]
    for qid in missing:
        print(f"MISSING {qid}: lean-v1 verified note has no verification script")

    print(f"scripts={len(scripts)} failed={len(failures)} missing={len(missing)}")
    return 1 if failures or missing else 0


if __name__ == "__main__":
    sys.exit(main())
