# -*- coding: utf-8 -*-
"""Validate canonical knowledge files before they are consumed by generators."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:  # Direct `python scripts/validate_knowledge_graph.py` execution.
    from knowledge_graph import validate_graph_directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph-dir", type=Path, default=Path("data/knowledge"))
    parser.add_argument("--report", type=Path, help="Write the machine-readable result to this path")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print the machine-readable result")
    args = parser.parse_args()

    result = validate_graph_directory(args.graph_dir)
    result["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    result["sourceIdentity"] = {
        "canonicalGraphRevision": result["graphRevision"],
        "schemaVersion": result["schemaVersion"],
    }
    result["outputIdentity"] = {
        "kind": "canonical-validation",
        "path": str(args.report.resolve()) if args.report else "stdout",
    }
    result["checks"] = [{"name": "canonical graph validation", "passed": bool(result["valid"])}]
    result["blockingFailures"] = [error["code"] for error in result["errors"]]
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized + "\n", encoding="utf-8")
    if args.as_json:
        print(serialized)
    else:
        status = "valid" if result["valid"] else "invalid"
        print(f"Knowledge graph: {status} ({result['graphRevision']})")
        for error in result["errors"]:
            print(f"[{error['code']}] {error['path']}: {error['message']}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
