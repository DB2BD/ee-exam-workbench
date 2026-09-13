# -*- coding: utf-8 -*-
"""Build the validated canonical knowledge graph into the website bundle.

The canonical JSON files are the source of truth.  This command validates
them first and atomically replaces the generated JavaScript only after every
validation and coverage gate passes.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:  # Direct ``python scripts/build_knowledge_graph.py``.
    from knowledge_graph import validate_graph_directory


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH_DIR = WORKSPACE / "data" / "knowledge"
DEFAULT_OUTPUT = WORKSPACE / "src" / "data" / "knowledge-dag.generated.js"
DEFAULT_REPORT = WORKSPACE / "reports" / "knowledge-graph-build.json"
DEFAULT_INVENTORY = WORKSPACE / "data" / "knowledge" / "migration-inventory.json"
DEFAULT_REQUIRED_QUESTION_LINKS = 482


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_inventory(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = _load_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _source_counts(graph_dir: Path, inventory_path: Path) -> dict[str, int]:
    inventory = _load_inventory(inventory_path)
    counts: dict[str, int] = {}
    if inventory:
        legacy = inventory.get("legacyDag", {})
        obsidian = inventory.get("obsidian", {})
        questions = inventory.get("questions", {})
        if isinstance(legacy, dict) and isinstance(legacy.get("nodeCount"), int):
            counts["legacyDagNodeCount"] = legacy["nodeCount"]
        if isinstance(obsidian, dict) and isinstance(obsidian.get("coreNoteCount"), int):
            counts["coreNoteCount"] = obsidian["coreNoteCount"]
        if isinstance(questions, dict):
            counts["questionRecordCount"] = sum(
                item.get("recordCount", 0)
                for item in questions.values()
                if isinstance(item, dict) and isinstance(item.get("recordCount", 0), int)
            )
    return counts


def _read_validated_payloads(graph_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    nodes = _load_json(graph_dir / "nodes.json")
    edges = _load_json(graph_dir / "edges.json")
    links = _load_json(graph_dir / "question-links.json")
    return nodes, edges, links


def _build_bundle(result: Mapping[str, Any], graph_dir: Path, inventory_path: Path) -> tuple[str, dict[str, Any]]:
    nodes_payload, edges_payload, links_payload = _read_validated_payloads(graph_dir)
    nodes = sorted(nodes_payload["nodes"], key=lambda item: item["nodeId"])
    edges = sorted(
        edges_payload["edges"],
        key=lambda item: (item["from"], item["relation"], item["to"]),
    )
    links = {key: links_payload["links"][key] for key in sorted(links_payload["links"])}
    source_counts = _source_counts(graph_dir, inventory_path)
    mapped_question_count = len(links)
    question_record_count = source_counts.get("questionRecordCount", mapped_question_count)
    unknown_question_count = max(question_record_count - mapped_question_count, 0)
    required_question_links = question_record_count or DEFAULT_REQUIRED_QUESTION_LINKS
    coverage = {
        "actual": mapped_question_count,
        "required": required_question_links,
        "status": "passed" if mapped_question_count == required_question_links else "failed",
    }
    report = {
        "schemaVersion": "knowledge-graph-build.v1",
        "valid": bool(result["valid"]) and coverage["status"] == "passed",
        "graphRevision": result["graphRevision"],
        "sourceCounts": {
            **source_counts,
            "canonicalNodeCount": len(nodes),
            "canonicalEdgeCount": len(edges),
            "canonicalQuestionLinkCount": len(links),
        },
        "mappedQuestionCount": mapped_question_count,
        "unknownQuestionCount": unknown_question_count,
        "coverage": coverage,
        "errors": list(result["errors"]),
    }
    if mapped_question_count != required_question_links:
        report["errors"].append(
            {
                "code": "COVERAGE_INCOMPLETE",
                "path": "question-links.json.links",
                "message": (
                    f"canonical question link coverage is {mapped_question_count}; "
                    f"the question inventory requires exactly {required_question_links}"
                ),
            }
        )
    report["errors"] = sorted(
        report["errors"], key=lambda item: (item["code"], item["path"], item["message"])
    )

    bundle = {
        "schemaVersion": result["schemaVersion"],
        "graphRevision": result["graphRevision"],
        "nodes": {node["nodeId"]: node for node in nodes},
        "edges": edges,
        "questionLinks": links,
        "mainlineOrder": [
            node["nodeId"]
            for node in nodes
            if node.get("nodeType") == "mainline" and node.get("lifecycle") == "active"
        ],
        "questionIds": [link["qid"] for _, link in sorted(links.items())],
        "coverage": {
            "mappedQuestionCount": mapped_question_count,
            "unknownQuestionCount": unknown_question_count,
        },
    }
    serialized = json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    source_hash = result["graphRevision"]
    header = (
        "// Generated by scripts/build_knowledge_graph.py. Do not edit.\n"
        f"// graphRevision: {source_hash}\n"
        "globalThis.CANONICAL_GRAPH_ENABLED = true;\n"
        f"globalThis.CANONICAL_KNOWLEDGE_GRAPH = {serialized}"
    )
    return header, report


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_knowledge_graph(
    graph_dir: Path | str = DEFAULT_GRAPH_DIR,
    output: Path | str = DEFAULT_OUTPUT,
    report_path: Path | str | None = DEFAULT_REPORT,
    inventory: Path | str = DEFAULT_INVENTORY,
) -> dict[str, Any]:
    graph_root = Path(graph_dir)
    result = validate_graph_directory(graph_root)
    if result["valid"]:
        _, report = _build_bundle(result, graph_root, Path(inventory))
    else:
        source_counts = _source_counts(graph_root, Path(inventory))
        mapped_question_count = result["questionLinkCount"]
        required_question_links = source_counts.get("questionRecordCount", DEFAULT_REQUIRED_QUESTION_LINKS)
        report = {
            "schemaVersion": "knowledge-graph-build.v1",
            "valid": False,
            "graphRevision": result["graphRevision"],
            "sourceCounts": {
                **source_counts,
                "canonicalNodeCount": result["nodeCount"],
                "canonicalEdgeCount": result["edgeCount"],
                "canonicalQuestionLinkCount": result["questionLinkCount"],
            },
            "mappedQuestionCount": mapped_question_count,
            "unknownQuestionCount": max(required_question_links - mapped_question_count, 0),
            "coverage": {
                "actual": mapped_question_count,
                "required": required_question_links,
                "status": "blocked",
            },
            "errors": list(result["errors"]),
        }
        if mapped_question_count != required_question_links:
            report["errors"].append(
                {
                    "code": "COVERAGE_INCOMPLETE",
                    "path": "question-links.json.links",
                    "message": (
                        f"canonical question link coverage is {mapped_question_count}; "
                        f"the question inventory requires exactly {required_question_links}"
                    ),
                }
            )
    report.update(
        {
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "sourceIdentity": {
                "canonicalGraphRevision": result["graphRevision"],
                "schemaVersion": result["schemaVersion"],
            },
            "outputIdentity": {"kind": "website-bundle", "path": str(Path(output).resolve())},
        }
    )
    report["checks"] = [
        {"name": "canonical graph validation", "passed": bool(result["valid"])},
        {"name": "question-link coverage", "passed": report["coverage"]["status"] == "passed"},
    ]
    report["blockingFailures"] = [error["code"] for error in report["errors"]]
    if not report["valid"]:
        report["errors"] = sorted(
            report["errors"], key=lambda item: (item["code"], item["path"], item["message"])
        )
    if report_path is not None:
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["valid"]:
        bundle, _ = _build_bundle(result, graph_root, Path(inventory))
        _atomic_write(Path(output), bundle)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph-dir", type=Path, default=DEFAULT_GRAPH_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--json", action="store_true", help="Print the machine-readable build report.")
    args = parser.parse_args()
    report = build_knowledge_graph(args.graph_dir, args.output, args.report, args.inventory)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["valid"] else "FAIL"
        print(f"{status}: {report['graphRevision']} ({report['mappedQuestionCount']} mapped questions)")
        for error in report["errors"]:
            print(f"- {error['code']} at {error['path']}: {error['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
