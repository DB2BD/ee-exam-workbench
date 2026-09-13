# -*- coding: utf-8 -*-
"""Validation and deterministic identity helpers for canonical knowledge data."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


GRAPH_SCHEMA_VERSION = "canonical-knowledge-graph.v1"
GOLDEN_SCHEMA_VERSION = "canonical-knowledge-golden.v1"
NODE_TYPES = {"question", "mechanism", "procedure", "mainline"}
LIFECYCLE_STATES = {"active", "retired", "merged"}
REQUIRED_NODE_FIELDS = {
    "nodeId",
    "nodeType",
    "title",
    "examFamily",
    "lifecycle",
    "provenance",
    "nodeRevisionHash",
}
REQUIRED_EDGE_FIELDS = {
    "from",
    "relation",
    "to",
    "why",
    "confidence",
    "evidence",
    "reviewStatus",
}
REQUIRED_LINK_FIELDS = {
    "qid",
    "examFamily",
    "nodeIds",
    "confidence",
    "evidence",
    "reviewStatus",
    "sourcePriority",
}
QID_RE = re.compile(r"^(EE|GK)-[0-9]{3}-[0-9]{2}-(?:[0-9]+|MC[0-9]+)$")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _error(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def _is_confidence(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def _qid_family(qid: str) -> str | None:
    if not isinstance(qid, str) or not QID_RE.fullmatch(qid):
        return None
    return "PE" if qid.startswith("EE-") else "GK"


def _record_envelope(record: Any, field: str, expected_version: str, errors: list[dict[str, str]]) -> list[Any] | dict[str, Any] | None:
    if not isinstance(record, dict):
        _error(errors, "INVALID_ENVELOPE", field, "record must be an object")
        return None
    if record.get("schemaVersion") != expected_version:
        _error(errors, "SCHEMA_VERSION", f"{field}.schemaVersion", f"expected {expected_version}")
    return record


def _validate_nodes(payload: Mapping[str, Any], errors: list[dict[str, str]]) -> dict[str, Mapping[str, Any]]:
    nodes = payload.get("nodes")
    if not isinstance(nodes, list):
        _error(errors, "INVALID_NODES", "nodes.json.nodes", "nodes must be an array")
        return {}
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, node in enumerate(nodes):
        path = f"nodes.json.nodes[{index}]"
        if not isinstance(node, dict):
            _error(errors, "INVALID_NODE", path, "node must be an object")
            continue
        missing = sorted(REQUIRED_NODE_FIELDS - set(node))
        if missing:
            _error(errors, "NODE_REQUIRED_FIELDS", path, f"missing fields: {', '.join(missing)}")
        node_id = node.get("nodeId")
        if not isinstance(node_id, str) or not node_id.strip():
            _error(errors, "NODE_ID", f"{path}.nodeId", "nodeId must be a non-empty string")
            continue
        if node_id in by_id:
            _error(errors, "DUPLICATE_NODE_ID", f"{path}.nodeId", f"duplicate nodeId {node_id}")
            continue
        if node.get("nodeType") not in NODE_TYPES:
            _error(errors, "NODE_TYPE", f"{path}.nodeType", f"unsupported nodeType {node.get('nodeType')!r}")
        if node.get("examFamily") not in {"PE", "GK"}:
            _error(errors, "NODE_FAMILY", f"{path}.examFamily", "examFamily must be PE or GK")
        if node.get("lifecycle") not in LIFECYCLE_STATES:
            _error(errors, "NODE_LIFECYCLE", f"{path}.lifecycle", "unsupported lifecycle")
        if not isinstance(node.get("title"), str) or not node.get("title", "").strip():
            _error(errors, "NODE_TITLE", f"{path}.title", "title must be non-empty")
        if not isinstance(node.get("provenance"), dict):
            _error(errors, "NODE_PROVENANCE", f"{path}.provenance", "provenance must be an object")
        if not isinstance(node.get("nodeRevisionHash"), str) or not node.get("nodeRevisionHash"):
            _error(errors, "NODE_REVISION_HASH", f"{path}.nodeRevisionHash", "nodeRevisionHash must be non-empty")
        if node.get("lifecycle") == "merged":
            successors = node.get("successorNodeIds")
            if not isinstance(successors, list) or not successors or not all(isinstance(item, str) and item for item in successors):
                _error(errors, "LIFECYCLE_SUCCESSOR", f"{path}.successorNodeIds", "merged node requires successorNodeIds")
        by_id[node_id] = node
    for node_id, node in by_id.items():
        for index, successor in enumerate(node.get("successorNodeIds", [])):
            if successor not in by_id:
                _error(errors, "DANGLING_SUCCESSOR", f"nodes.{node_id}.successorNodeIds[{index}]", f"unknown successor {successor}")
    return by_id


def _validate_edges(payload: Mapping[str, Any], nodes: Mapping[str, Mapping[str, Any]], schema: Mapping[str, Any], errors: list[dict[str, str]]) -> list[Mapping[str, Any]]:
    edges = payload.get("edges")
    if not isinstance(edges, list):
        _error(errors, "INVALID_EDGES", "edges.json.edges", "edges must be an array")
        return []
    acyclic = set(schema.get("acyclicRelations", ["prerequisite"]))
    seen: set[tuple[str, str, str]] = set()
    graph: dict[str, list[str]] = {}
    valid_edges: list[Mapping[str, Any]] = []
    for index, edge in enumerate(edges):
        path = f"edges.json.edges[{index}]"
        if not isinstance(edge, dict):
            _error(errors, "INVALID_EDGE", path, "edge must be an object")
            continue
        missing = sorted(REQUIRED_EDGE_FIELDS - set(edge))
        if missing:
            _error(errors, "EDGE_REQUIRED_FIELDS", path, f"missing fields: {', '.join(missing)}")
        source, target, relation = edge.get("from"), edge.get("to"), edge.get("relation")
        key = (str(source), str(relation), str(target))
        if key in seen:
            _error(errors, "DUPLICATE_EDGE", path, f"duplicate edge {key}")
        seen.add(key)
        if source not in nodes:
            _error(errors, "DANGLING_EDGE", f"{path}.from", f"unknown node {source}")
        if target not in nodes:
            _error(errors, "DANGLING_EDGE", f"{path}.to", f"unknown node {target}")
        if source in nodes and target in nodes and nodes[source].get("examFamily") != nodes[target].get("examFamily"):
            _error(errors, "CROSS_FAMILY_EDGE", path, "edge endpoints must share examFamily")
        if not isinstance(edge.get("why"), str) or not edge.get("why", "").strip():
            _error(errors, "EDGE_WHY", f"{path}.why", "why must be non-empty")
        if not _is_confidence(edge.get("confidence")):
            _error(errors, "EDGE_CONFIDENCE", f"{path}.confidence", "confidence must be between 0 and 1")
        if not isinstance(edge.get("evidence"), list) or not edge.get("evidence"):
            _error(errors, "EDGE_EVIDENCE", f"{path}.evidence", "evidence must be a non-empty array")
        if not isinstance(edge.get("reviewStatus"), str) or not edge.get("reviewStatus"):
            _error(errors, "EDGE_REVIEW_STATUS", f"{path}.reviewStatus", "reviewStatus must be non-empty")
        valid_edges.append(edge)
        if relation in acyclic and source in nodes and target in nodes:
            graph.setdefault(source, []).append(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            _error(errors, "CYCLE", "edges.json.edges", f"acyclic relation cycle reaches {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in graph.get(node_id, []):
            visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in graph:
        visit(node_id)
    return valid_edges


def _validate_links(payload: Mapping[str, Any], nodes: Mapping[str, Mapping[str, Any]], errors: list[dict[str, str]]) -> dict[str, Mapping[str, Any]]:
    links = payload.get("links")
    if not isinstance(links, dict):
        _error(errors, "INVALID_LINKS", "question-links.json.links", "links must be an object keyed by family:QID")
        return {}
    result: dict[str, Mapping[str, Any]] = {}
    for key, link in links.items():
        path = f"question-links.json.links[{key!r}]"
        if not isinstance(link, dict):
            _error(errors, "INVALID_QUESTION_LINK", path, "question link must be an object")
            continue
        missing = sorted(REQUIRED_LINK_FIELDS - set(link))
        if missing:
            _error(errors, "LINK_REQUIRED_FIELDS", path, f"missing fields: {', '.join(missing)}")
        qid, family = link.get("qid"), link.get("examFamily")
        qid_family = _qid_family(qid)
        if qid_family is None:
            _error(errors, "UNKNOWN_QID", f"{path}.qid", f"unsupported QID {qid!r}")
        elif qid_family != family:
            _error(errors, "QID_FAMILY_MISMATCH", path, f"QID {qid} belongs to {qid_family}, not {family}")
        if key != f"{family}:{qid}":
            _error(errors, "LINK_KEY", path, "link key must be examFamily:qid")
        node_ids = link.get("nodeIds")
        if not isinstance(node_ids, list) or not node_ids:
            _error(errors, "LINK_NODE_IDS", f"{path}.nodeIds", "nodeIds must be a non-empty array")
            node_ids = []
        for index, node_id in enumerate(node_ids):
            if node_id not in nodes:
                _error(errors, "DANGLING_QUESTION_LINK", f"{path}.nodeIds[{index}]", f"unknown node {node_id}")
            elif nodes[node_id].get("examFamily") != family:
                _error(errors, "CROSS_FAMILY_LINK", f"{path}.nodeIds[{index}]", "question and node must share examFamily")
        if not _is_confidence(link.get("confidence")):
            _error(errors, "LINK_CONFIDENCE", f"{path}.confidence", "confidence must be between 0 and 1")
        if not isinstance(link.get("evidence"), list) or not link.get("evidence"):
            _error(errors, "LINK_EVIDENCE", f"{path}.evidence", "evidence must be a non-empty array")
        if not isinstance(link.get("reviewStatus"), str) or not link.get("reviewStatus"):
            _error(errors, "LINK_REVIEW_STATUS", f"{path}.reviewStatus", "reviewStatus must be non-empty")
        if link.get("sourcePriority") not in {"manual", "approved_ai", "deterministic", "unknown"}:
            _error(errors, "LINK_SOURCE_PRIORITY", f"{path}.sourcePriority", "unsupported source priority")
        result[str(key)] = link
    return result


def _validate_golden_fixture(
    root: Path,
    nodes: Mapping[str, Mapping[str, Any]],
    links: Mapping[str, Mapping[str, Any]],
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    """Validate the reviewed first slice when a graph directory provides one."""

    path = root / "golden-fixture.json"
    if not path.exists():
        return None
    try:
        fixture = _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        _error(errors, "INVALID_JSON", "golden-fixture.json", str(exc))
        return None
    if not isinstance(fixture, dict):
        _error(errors, "INVALID_GOLDEN_FIXTURE", "golden-fixture.json", "fixture must be an object")
        return None
    if fixture.get("schemaVersion") != GOLDEN_SCHEMA_VERSION:
        _error(errors, "GOLDEN_SCHEMA_VERSION", "golden-fixture.json.schemaVersion", f"expected {GOLDEN_SCHEMA_VERSION}")
    if fixture.get("reviewStatus") != "human-reviewed":
        _error(errors, "GOLDEN_REVIEW_STATUS", "golden-fixture.json.reviewStatus", "reviewStatus must be human-reviewed")

    node_ids = fixture.get("nodeIds")
    if not isinstance(node_ids, list) or not all(isinstance(item, str) and item for item in node_ids):
        _error(errors, "GOLDEN_NODE_IDS", "golden-fixture.json.nodeIds", "nodeIds must be a non-empty array of strings")
        node_ids = []
    elif not 20 <= len(node_ids) <= 30:
        _error(errors, "GOLDEN_NODE_COUNT", "golden-fixture.json.nodeIds", "reviewed first slice must contain 20 to 30 node IDs")
    if len(node_ids) != len(set(node_ids)):
        _error(errors, "GOLDEN_DUPLICATE_NODE_ID", "golden-fixture.json.nodeIds", "nodeIds must be unique")
    for index, node_id in enumerate(node_ids):
        if node_id not in nodes:
            _error(errors, "GOLDEN_DANGLING_NODE", f"golden-fixture.json.nodeIds[{index}]", f"unknown node {node_id}")

    question_ids = fixture.get("questionIds")
    if not isinstance(question_ids, list) or not all(isinstance(item, str) and item for item in question_ids):
        _error(errors, "GOLDEN_QUESTION_IDS", "golden-fixture.json.questionIds", "questionIds must be a non-empty array of strings")
        question_ids = []
    if len(question_ids) != len(set(question_ids)):
        _error(errors, "GOLDEN_DUPLICATE_QUESTION_ID", "golden-fixture.json.questionIds", "questionIds must be unique")
    golden_nodes = set(node_ids)
    for index, qid in enumerate(question_ids):
        family = _qid_family(qid)
        key = f"{family}:{qid}" if family else None
        link = links.get(key) if key else None
        if link is None:
            _error(errors, "GOLDEN_DANGLING_QUESTION", f"golden-fixture.json.questionIds[{index}]", f"unknown question link {qid}")
        elif not golden_nodes.intersection(link.get("nodeIds", [])):
            _error(errors, "GOLDEN_QUESTION_OUT_OF_SCOPE", f"golden-fixture.json.questionIds[{index}]", f"question {qid} does not link to a golden node")

    return {
        "fixtureId": fixture.get("fixtureId"),
        "fixtureVersion": fixture.get("fixtureVersion"),
        "reviewStatus": fixture.get("reviewStatus"),
        "nodeCount": len(node_ids),
        "questionCount": len(question_ids),
    }


def _graph_revision(schema: Mapping[str, Any], nodes: Mapping[str, Mapping[str, Any]], edges: Iterable[Mapping[str, Any]], links: Mapping[str, Mapping[str, Any]]) -> str:
    payload = {
        "schema": schema,
        "nodes": sorted(nodes.values(), key=lambda item: item.get("nodeId", "")),
        "edges": sorted(edges, key=lambda item: (str(item.get("from")), str(item.get("relation")), str(item.get("to")))),
        "links": {key: links[key] for key in sorted(links)},
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return f"kg-v1-{digest[:16]}"


def validate_graph_directory(graph_dir: Path | str) -> Dict[str, Any]:
    """Validate canonical files and return a stable machine-readable report."""

    root = Path(graph_dir)
    errors: list[dict[str, str]] = []
    required_files = ["schema.json", "nodes.json", "edges.json", "question-links.json"]
    payloads: dict[str, Any] = {}
    for filename in required_files:
        path = root / filename
        if not path.exists():
            _error(errors, "MISSING_FILE", filename, "required canonical file is missing")
            continue
        try:
            payloads[filename] = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            _error(errors, "INVALID_JSON", filename, str(exc))

    schema = payloads.get("schema.json", {})
    if not isinstance(schema, dict):
        _error(errors, "INVALID_SCHEMA", "schema.json", "schema must be an object")
        schema = {}
    if schema.get("schemaVersion") != GRAPH_SCHEMA_VERSION:
        _error(errors, "SCHEMA_VERSION", "schema.json.schemaVersion", f"expected {GRAPH_SCHEMA_VERSION}")
    declared_types = set(schema.get("nodeTypes", [])) if isinstance(schema.get("nodeTypes"), list) else set()
    if not NODE_TYPES.issubset(declared_types):
        _error(errors, "SCHEMA_NODE_TYPES", "schema.json.nodeTypes", "schema must declare all supported node types")
    declared_lifecycle = set(schema.get("lifecycleStates", [])) if isinstance(schema.get("lifecycleStates"), list) else set()
    if not LIFECYCLE_STATES.issubset(declared_lifecycle):
        _error(errors, "SCHEMA_LIFECYCLE", "schema.json.lifecycleStates", "schema must declare all lifecycle states")

    nodes_payload = _record_envelope(payloads.get("nodes.json"), "nodes.json", GRAPH_SCHEMA_VERSION, errors)
    edges_payload = _record_envelope(payloads.get("edges.json"), "edges.json", GRAPH_SCHEMA_VERSION, errors)
    links_payload = _record_envelope(payloads.get("question-links.json"), "question-links.json", GRAPH_SCHEMA_VERSION, errors)
    nodes = _validate_nodes(nodes_payload or {}, errors) if isinstance(nodes_payload, dict) else {}
    edges = _validate_edges(edges_payload or {}, nodes, schema, errors) if isinstance(edges_payload, dict) else []
    links = _validate_links(links_payload or {}, nodes, errors) if isinstance(links_payload, dict) else {}
    golden_fixture = _validate_golden_fixture(root, nodes, links, errors)
    revision = _graph_revision(schema, nodes, edges, links)
    return {
        "valid": not errors,
        "graphRevision": revision,
        "schemaVersion": GRAPH_SCHEMA_VERSION,
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "questionLinkCount": len(links),
        "goldenFixture": golden_fixture,
        "errors": sorted(errors, key=lambda item: (item["code"], item["path"], item["message"])),
    }


def validate_and_write_report(graph_dir: Path | str, report_path: Path | str) -> Dict[str, Any]:
    result = validate_graph_directory(graph_dir)
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
