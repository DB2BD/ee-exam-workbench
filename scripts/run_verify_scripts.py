#!/usr/bin/env python3
"""Run the independent per-question verification scripts in ``verification/pe/``.

Each ``verification/pe/EE-YYY-SS-N.py`` solves its question from the official
crop's givens (SymPy/NumPy), asserts every boxed answer of the canonical note
and exits non-zero on mismatch.  A lean-v1 note whose status is ``verified``
or ``reference_book_verified`` must have one.

Usage::

    python3 scripts/run_verify_scripts.py               # run all scripts
    python3 scripts/run_verify_scripts.py EE-114-05-3   # run selected QIDs

Locally, a script whose content passed before (same Python and library versions)
is skipped; the record lives in ``.cache/verify_scripts.json``.  Scripts that
read other files always run.  ``CI`` or ``EE_NO_CACHE`` in the environment
turns the cache off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_DIR = ROOT / "verification" / "pe"
NOTES = ROOT / "02_題解/技師題解"
TIMEOUT_SECONDS = 120
NEEDS_SCRIPT = {"verified", "reference_book_verified"}
CACHE = ROOT / ".cache" / "verify_scripts.json"


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


def cache_enabled() -> bool:
    return not (os.environ.get("CI") or os.environ.get("EE_NO_CACHE"))


def runtime_key() -> str:
    versions = [sys.version]
    for name in ("sympy", "numpy", "mpmath", "scipy"):
        try:
            versions.append(f"{name}={__import__(name).__version__}")
        except ImportError:
            versions.append(f"{name}=none")
    return "|".join(versions)


def script_key(script: Path, runtime: str) -> str | None:
    """Content hash of a self-contained script; None when it reads other files."""
    source = script.read_bytes()
    if b"open(" in source or b"read_text" in source:
        return None
    return hashlib.sha256(runtime.encode() + b"\0" + source).hexdigest()


def load_cache() -> dict[str, str]:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qids", nargs="*")
    args = parser.parse_args(argv)

    scripts = sorted(VERIFY_DIR.glob("EE-*.py"))
    if args.qids:
        scripts = [script for script in scripts if script.stem in set(args.qids)]
    failures = []
    use_cache = cache_enabled()
    runtime = runtime_key() if use_cache else ""
    cache = load_cache() if use_cache else {}
    keys = {script: script_key(script, runtime) if use_cache else None for script in scripts}
    pending = [script for script in scripts if keys[script] is None or cache.get(script.stem) != keys[script]]
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
        outcomes = dict(zip(pending, pool.map(run, pending)))  # scripts are independent
    for script in scripts:
        if script not in outcomes:
            print(f"PASS {script.stem}: (cached)")
            continue
        ok, tail = outcomes[script]
        print(f"{'PASS' if ok else 'FAIL'} {script.stem}: {tail}")
        if not ok:
            failures.append(script.stem)
            cache.pop(script.stem, None)
        elif keys[script]:
            cache[script.stem] = keys[script]
    if use_cache:
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True), encoding="utf-8")

    available = {script.stem for script in VERIFY_DIR.glob("EE-*.py")}
    required = lean_notes_needing_scripts()
    if args.qids:
        required = [qid for qid in required if qid in set(args.qids)]
    missing = [qid for qid in required if qid not in available]
    for qid in missing:
        print(f"MISSING {qid}: lean-v1 verified note has no verification script")

    print(f"scripts={len(scripts)} ran={len(pending)} failed={len(failures)} missing={len(missing)}")
    return 1 if failures or missing else 0


if __name__ == "__main__":
    sys.exit(main())
