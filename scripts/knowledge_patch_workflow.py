#!/usr/bin/env python3
"""Offline context packets and review-gated KnowledgePatchCandidate workflow."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

try:
    from scripts.knowledge_graph import _canonical_json, _graph_revision, validate_graph_directory
except ModuleNotFoundError:
    from knowledge_graph import _canonical_json, _graph_revision, validate_graph_directory


CANDIDATE_SCHEMA = "knowledge-patch-candidate.v1"
PACKET_SCHEMA = "knowledge-context-packet.v1"
REVIEW_SCHEMA = "knowledge-patch-review.v1"
QID_RE = re.compile(r"^(EE|GK)-[0-9]{3}-[0-9]{2}-(?:[0-9]+|MC[0-9]+)$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
NODE_TYPES = {"question", "mechanism", "procedure", "mainline"}
LIFECYCLES = {"active", "retired", "merged"}
FAMILIES = {"PE", "GK"}
DEFAULT_PACKET_BYTES = 120_000
DEFAULT_CANDIDATE_BYTES = 250_000


class WorkflowError(ValueError):
    """A safe, user-actionable workflow rejection."""


def _clone(value: Any) -> Any:
    return copy.deepcopy(value)


def _bytes(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()[:16]


def _error(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def load_graph_bundle(graph_dir: Path | str) -> Dict[str, Any]:
    root = Path(graph_dir)
    validation = validate_graph_directory(root)
    if not validation["valid"]:
        raise WorkflowError("canonical graph validation failed: " + ", ".join(error["code"] for error in validation["errors"]))
    schema = json.loads((root / "schema.json").read_text(encoding="utf-8"))
    nodes_payload = json.loads((root / "nodes.json").read_text(encoding="utf-8"))
    edges_payload = json.loads((root / "edges.json").read_text(encoding="utf-8"))
    links_payload = json.loads((root / "question-links.json").read_text(encoding="utf-8"))
    return {
        "schema": schema,
        "nodes": {node["nodeId"]: node for node in nodes_payload["nodes"]},
        "edges": edges_payload["edges"],
        "questionLinks": links_payload["links"],
        "graphRevision": validation["graphRevision"],
    }


def _bounded_text(value: Any, limit: int) -> str:
    return str(value or "").replace("\x00", "").strip()[:limit]


def _event_preview(event: Mapping[str, Any]) -> Dict[str, Any]:
    fields = (
        "eventId", "attemptId", "qid", "examFamily", "eventType", "primaryKnowledgeNodeId",
        "secondaryKnowledgeNodeIds", "rating", "errorType", "diagnosisConfidence", "recordedAt",
        "graphRevisionRef", "evidence", "customText", "sourceMode",
    )
    preview: Dict[str, Any] = {}
    for field in fields:
        if field not in event:
            continue
        value = event[field]
        if field in {"evidence", "secondaryKnowledgeNodeIds"} and isinstance(value, list):
            preview[field] = [_bounded_text(item, 200) for item in value[:10]]
        elif field == "customText":
            preview[field] = _bounded_text(value, 500)
        elif isinstance(value, (str, int, float, bool)) or value is None:
            preview[field] = value
    return preview


def build_context_packet(
    graph: Mapping[str, Any],
    selected_node_ids: Iterable[str] | None = None,
    issue_events: Iterable[Mapping[str, Any]] | None = None,
    *,
    max_history: int = 20,
    max_bytes: int = DEFAULT_PACKET_BYTES,
) -> Dict[str, Any]:
    nodes = graph.get("nodes", {})
    selected = sorted(set(selected_node_ids or sorted(nodes)))
    selected = [node_id for node_id in selected if node_id in nodes][:20]
    selected_set = set(selected)
    selected_nodes = [_clone(nodes[node_id]) for node_id in selected]
    selected_edges = [
        _clone(edge) for edge in graph.get("edges", [])
        if edge.get("from") in selected_set or edge.get("to") in selected_set
    ]
    selected_links = {
        key: _clone(link) for key, link in sorted(graph.get("questionLinks", {}).items())
        if any(node_id in selected_set for node_id in link.get("nodeIds", []))
    }
    previews = [_event_preview(event) for event in (issue_events or []) if isinstance(event, Mapping)]
    previews.sort(key=lambda event: (str(event.get("recordedAt") or ""), str(event.get("eventId") or "")))
    history = previews[-max(0, min(max_history, 50)):]
    packet = {
        "schemaVersion": PACKET_SCHEMA,
        "graphRevision": graph.get("graphRevision"),
        "selectedNodeIds": selected,
        "nodes": selected_nodes,
        "edges": selected_edges,
        "questionLinks": selected_links,
        "issueHistory": history,
        "bounds": {"maxNodes": 20, "maxHistory": max(0, min(max_history, 50)), "maxBytes": max_bytes},
    }
    payload_bytes = _bytes(packet)
    if payload_bytes > max_bytes:
        raise WorkflowError(f"context packet exceeds {max_bytes} bytes")
    markdown_lines = [
        "# Knowledge Context Packet",
        "",
        f"- graphRevision: `{packet['graphRevision']}`",
        f"- selected nodes: {len(selected)}",
        "",
        "## Selected nodes",
    ]
    for node in selected_nodes:
        markdown_lines.extend([f"- `{node['nodeId']}` — {node['title']} ({node['nodeType']}, {node['examFamily']})"])
    markdown_lines.extend(["", "## Related evidence", "```json", json.dumps({"edges": selected_edges, "questionLinks": selected_links}, ensure_ascii=False, sort_keys=True, indent=2), "```", "", "## Bounded issue history"])
    for event in history:
        markdown_lines.append(f"- `{event.get('eventId')}` · {event.get('qid')} · {event.get('eventType')} · {event.get('recordedAt', '')}")
        if event.get("evidence"):
            markdown_lines.append(f"  - evidence: {'; '.join(event['evidence'])}")
    packet["payloadBytes"] = payload_bytes
    packet["markdown"] = "\n".join(markdown_lines) + "\n"
    return packet


def _operation_arrays(candidate: Mapping[str, Any]) -> Dict[str, list[Any]]:
    operations = candidate.get("operations")
    if not isinstance(operations, Mapping):
        return {"upsertNodes": [], "addEdges": [], "upsertQuestionLinks": []}
    return {name: operations.get(name, []) if isinstance(operations.get(name, []), list) else [] for name in ("upsertNodes", "addEdges", "upsertQuestionLinks")}


def _qid_family(qid: Any) -> str | None:
    if not isinstance(qid, str) or not QID_RE.fullmatch(qid):
        return None
    return "PE" if qid.startswith("EE-") else "GK"


def inspect_candidate(candidate: Mapping[str, Any], graph: Mapping[str, Any], *, max_bytes: int = DEFAULT_CANDIDATE_BYTES) -> Dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(candidate, Mapping):
        return {"valid": False, "errors": [{"code": "INVALID_CANDIDATE", "path": "$", "message": "candidate must be an object"}]}
    try:
        candidate_bytes = _bytes(candidate)
    except (TypeError, ValueError):
        candidate_bytes = max_bytes + 1
    if candidate_bytes > max_bytes:
        _error(errors, "CANDIDATE_TOO_LARGE", "$", f"candidate exceeds {max_bytes} bytes")
    if candidate.get("schemaVersion") != CANDIDATE_SCHEMA:
        _error(errors, "SCHEMA_VERSION", "schemaVersion", f"expected {CANDIDATE_SCHEMA}")
    if candidate.get("candidateVersion") != 1:
        _error(errors, "CANDIDATE_VERSION", "candidateVersion", "expected candidateVersion 1")
    candidate_id = candidate.get("candidateId")
    if not isinstance(candidate_id, str) or not ID_RE.fullmatch(candidate_id):
        _error(errors, "CANDIDATE_ID", "candidateId", "candidateId must be a bounded stable ID")
    family = candidate.get("examFamily")
    if family not in FAMILIES:
        _error(errors, "FAMILY", "examFamily", "examFamily must be PE or GK")
    qid = candidate.get("qid")
    qid_family = _qid_family(qid)
    if qid_family is None:
        _error(errors, "CANDIDATE_QID", "qid", "candidate qid must be a supported question ID")
    elif family in FAMILIES and qid_family != family:
        _error(errors, "CROSS_FAMILY", "qid", "candidate qid crosses exam family")
    elif f"{family}:{qid}" not in graph.get("questionLinks", {}):
        _error(errors, "UNKNOWN_QID", "qid", "candidate qid is not present in the current graph")
    if candidate.get("baseGraphRevision") != graph.get("graphRevision"):
        _error(errors, "STALE_GRAPH_REVISION", "baseGraphRevision", "candidate must be rebased to the current graph revision")
    if not isinstance(candidate.get("intent"), str) or not _bounded_text(candidate.get("intent"), 500):
        _error(errors, "INTENT", "intent", "intent must be a non-empty bounded string")
    evidence = candidate.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not _bounded_text(item, 300) for item in evidence[:20]):
        _error(errors, "EVIDENCE_REQUIRED", "evidence", "candidate evidence must be a non-empty bounded list")
    source_events = candidate.get("sourceIssueEventIds", [])
    if not isinstance(source_events, list) or not source_events or len(source_events) > 50 or any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in source_events):
        _error(errors, "SOURCE_EVENT_IDS", "sourceIssueEventIds", "source issue event IDs are invalid or too many")
    for field in ("likelyQuestions", "reuse", "create", "update", "questionLinks"):
        value = candidate.get(field)
        if not isinstance(value, list) or len(value) > 50:
            _error(errors, "CANDIDATE_FIELD", field, f"{field} must be a bounded array")
            continue
        if field == "likelyQuestions" and any(_qid_family(item) is None for item in value):
            _error(errors, "CANDIDATE_LIKELY_QUESTIONS", field, "likelyQuestions must contain supported question IDs")
        if field in {"reuse", "create", "update"} and any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in value):
            _error(errors, "CANDIDATE_NODE_REFS", field, f"{field} must contain bounded node IDs")
    for unsafe_key in ("pastedText", "rawText", "markdownPatch", "freeformPatch"):
        if candidate.get(unsafe_key):
            _error(errors, "UNSAFE_ARBITRARY_TEXT", unsafe_key, "arbitrary pasted text cannot enter the canonical workflow")

    nodes = graph.get("nodes", {})
    expected_hashes = candidate.get("expectedNodeHashes", {})
    if not isinstance(expected_hashes, Mapping):
        _error(errors, "EXPECTED_HASHES", "expectedNodeHashes", "expectedNodeHashes must be an object")
        expected_hashes = {}
    for node_id, expected_hash in expected_hashes.items():
        if node_id not in nodes:
            _error(errors, "UNKNOWN_NODE", f"expectedNodeHashes.{node_id}", "expected node does not exist")
        elif nodes[node_id].get("nodeRevisionHash") != expected_hash:
            _error(errors, "NODE_HASH_DRIFT", f"expectedNodeHashes.{node_id}", "node revision hash changed; rebase or regenerate candidate")

    operations = _operation_arrays(candidate)
    if not isinstance(candidate.get("operations"), Mapping):
        _error(errors, "OPERATIONS", "operations", "operations must be an object")
    known_nodes = set(nodes)
    operation_node_ids: set[str] = set()
    for index, node in enumerate(operations["upsertNodes"]):
        path = f"operations.upsertNodes[{index}]"
        if not isinstance(node, Mapping):
            _error(errors, "NODE_OPERATION", path, "node must be an object")
            continue
        node_id = node.get("nodeId")
        operation_node_ids.add(str(node_id))
        if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id): _error(errors, "NODE_ID", f"{path}.nodeId", "invalid node ID")
        if node.get("nodeType") not in NODE_TYPES: _error(errors, "NODE_TYPE", f"{path}.nodeType", "invalid node type")
        if not isinstance(node.get("title"), str) or not _bounded_text(node.get("title"), 300): _error(errors, "NODE_TITLE", f"{path}.title", "node title is required")
        if node.get("examFamily") != family: _error(errors, "CROSS_FAMILY", f"{path}.examFamily", "candidate node crosses exam family")
        if node.get("lifecycle") not in LIFECYCLES: _error(errors, "NODE_LIFECYCLE", f"{path}.lifecycle", "invalid lifecycle")
        if not isinstance(node.get("provenance"), Mapping): _error(errors, "PROVENANCE", f"{path}.provenance", "candidate node provenance is required")
        if not isinstance(node.get("nodeRevisionHash"), str) or not node.get("nodeRevisionHash"): _error(errors, "NODE_REVISION_HASH", f"{path}.nodeRevisionHash", "node revision hash is required")
        if node.get("lifecycle") == "merged" and not isinstance(node.get("successorNodeIds"), list): _error(errors, "LIFECYCLE_SUCCESSOR", f"{path}.successorNodeIds", "merged node requires successorNodeIds")
        if node_id in nodes and node_id not in expected_hashes: _error(errors, "EXPECTED_HASH_REQUIRED", path, "updates must declare the current expected node hash")
    if len(operation_node_ids) != len(operations["upsertNodes"]): _error(errors, "DUPLICATE_NODE_ID", "operations.upsertNodes", "candidate contains duplicate node IDs")
    known_after = known_nodes | operation_node_ids
    existing_edges = {(edge.get("from"), edge.get("relation"), edge.get("to")) for edge in graph.get("edges", [])}
    proposed_edges: list[Mapping[str, Any]] = []
    for index, edge in enumerate(operations["addEdges"]):
        path = f"operations.addEdges[{index}]"
        if not isinstance(edge, Mapping): _error(errors, "EDGE_OPERATION", path, "edge must be an object"); continue
        source, target, relation = edge.get("from"), edge.get("to"), edge.get("relation")
        if source not in known_after: _error(errors, "UNKNOWN_NODE", f"{path}.from", "edge source is unknown")
        if target not in known_after: _error(errors, "UNKNOWN_NODE", f"{path}.to", "edge target is unknown")
        endpoint_family = [nodes.get(item, {}).get("examFamily") for item in (source, target) if item in nodes]
        operation_families = [node.get("examFamily") for node in operations["upsertNodes"] if node.get("nodeId") in (source, target)]
        if any(item != family for item in endpoint_family + operation_families): _error(errors, "CROSS_FAMILY", path, "edge endpoints must share candidate exam family")
        if not isinstance(relation, str) or not relation: _error(errors, "EDGE_RELATION", f"{path}.relation", "edge relation is required")
        if not isinstance(edge.get("why"), str) or not _bounded_text(edge.get("why"), 500): _error(errors, "EDGE_WHY", f"{path}.why", "edge rationale is required")
        if not isinstance(edge.get("confidence"), (int, float)) or not 0 <= edge.get("confidence", -1) <= 1: _error(errors, "EDGE_CONFIDENCE", f"{path}.confidence", "confidence must be between 0 and 1")
        if not isinstance(edge.get("evidence"), list) or not edge.get("evidence"): _error(errors, "EVIDENCE_REQUIRED", f"{path}.evidence", "edge evidence is required")
        if (source, relation, target) in existing_edges: _error(errors, "DUPLICATE_EDGE", path, "edge already exists")
        proposed_edges.append(edge)
    links = graph.get("questionLinks", {})
    for index, link in enumerate(operations["upsertQuestionLinks"]):
        path = f"operations.upsertQuestionLinks[{index}]"
        if not isinstance(link, Mapping): _error(errors, "LINK_OPERATION", path, "question link must be an object"); continue
        qid = link.get("qid")
        qid_family = _qid_family(qid)
        if qid_family is None: _error(errors, "UNKNOWN_QID", f"{path}.qid", "unsupported QID")
        elif qid_family != family: _error(errors, "CROSS_FAMILY", f"{path}.qid", "question link crosses exam family")
        if not isinstance(link.get("nodeIds"), list) or not link.get("nodeIds"): _error(errors, "LINK_NODE_IDS", f"{path}.nodeIds", "question link needs node IDs")
        else:
            for node_id in link["nodeIds"]:
                if node_id not in known_after: _error(errors, "UNKNOWN_NODE", f"{path}.nodeIds", "question link references unknown node")
                elif node_id in nodes and nodes[node_id].get("examFamily") != family: _error(errors, "CROSS_FAMILY", f"{path}.nodeIds", "question link crosses exam family")
        if not isinstance(link.get("evidence"), list) or not link.get("evidence"): _error(errors, "EVIDENCE_REQUIRED", f"{path}.evidence", "question link evidence is required")
        if not isinstance(link.get("confidence"), (int, float)) or not 0 <= link.get("confidence", -1) <= 1: _error(errors, "LINK_CONFIDENCE", f"{path}.confidence", "confidence must be between 0 and 1")
        if link.get("reviewStatus") not in {"approved", "draft", "unknown"}: _error(errors, "LINK_REVIEW_STATUS", f"{path}.reviewStatus", "invalid review status")
        if link.get("sourcePriority") not in {"manual", "approved_ai", "deterministic", "unknown"}: _error(errors, "LINK_SOURCE_PRIORITY", f"{path}.sourcePriority", "invalid source priority")
    link_keys = [link.get("qid") for link in operations["upsertQuestionLinks"] if isinstance(link, Mapping)]
    if len(link_keys) != len(set(link_keys)): _error(errors, "DUPLICATE_LINK", "operations.upsertQuestionLinks", "candidate contains duplicate question links")
    adjacency: dict[str, list[str]] = {}
    for edge in list(graph.get("edges", [])) + proposed_edges:
        if edge.get("relation") == "prerequisite": adjacency.setdefault(edge.get("from"), []).append(edge.get("to"))
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            _error(errors, "CYCLE", "operations.addEdges", f"prerequisite cycle reaches {node_id}")
            return
        if node_id in visited: return
        visiting.add(node_id)
        for target in adjacency.get(node_id, []): visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in adjacency: visit(node_id)
    errors.sort(key=lambda item: (item["code"], item["path"], item["message"]))
    return {
        "valid": not errors,
        "errors": errors,
        "candidateId": candidate_id,
        "candidateVersion": candidate.get("candidateVersion"),
        "baseGraphRevision": candidate.get("baseGraphRevision"),
        "candidateBytes": candidate_bytes,
        "candidateHash": _hash(candidate),
    }


def _apply_candidate(graph: Mapping[str, Any], candidate: Mapping[str, Any]) -> Dict[str, Any]:
    operations = _operation_arrays(candidate)
    nodes = _clone(graph.get("nodes", {}))
    for node in operations["upsertNodes"]: nodes[node["nodeId"]] = _clone(node)
    edges = _clone(graph.get("edges", [])) + [_clone(edge) for edge in operations["addEdges"]]
    links = _clone(graph.get("questionLinks", {}))
    for link in operations["upsertQuestionLinks"]: links[f"{candidate['examFamily']}:{link['qid']}"] = _clone(link)
    revision = _graph_revision(graph["schema"], nodes, edges, links)
    return {"schema": _clone(graph["schema"]), "nodes": nodes, "edges": edges, "questionLinks": links, "graphRevision": revision}


def rebase_candidate(candidate: Mapping[str, Any], graph: Mapping[str, Any], *, max_bytes: int = DEFAULT_CANDIDATE_BYTES) -> Dict[str, Any]:
    rebased = _clone(candidate)
    rebased["baseGraphRevision"] = graph.get("graphRevision")
    report = inspect_candidate(rebased, graph, max_bytes=max_bytes)
    return {"ok": report["valid"], "candidate": rebased if report["valid"] else None, "report": report}


def _safe_child_path(path: Path | str, parent: Path | str) -> Path:
    root = Path(parent).resolve()
    target = Path(path).resolve()
    try: target.relative_to(root)
    except ValueError as exc: raise WorkflowError(f"output path must remain under {root}") from exc
    return target


def _safe_project_path(path: Path | str, project_root: Path | str, allowed_prefixes: tuple[str, ...]) -> Path:
    root = Path(project_root).resolve()
    target = Path(path).resolve()
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise WorkflowError(f"output path must remain under project root {root}") from exc
    if not any(relative == Path(prefix) or Path(prefix) in relative.parents for prefix in allowed_prefixes):
        raise WorkflowError(f"output path must be under one of: {', '.join(allowed_prefixes)}")
    return target


def _write_json_temp(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return temporary
    except Exception:
        if temporary.exists(): temporary.unlink()
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _atomic_write_json(path: Path, value: Any) -> None:
    temporary = _write_json_temp(path, value)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists(): temporary.unlink()


def _review_path(queue_dir: Path | str, candidate_id: str) -> Path:
    queue = Path(queue_dir).resolve()
    if not ID_RE.fullmatch(candidate_id): raise WorkflowError("invalid candidate ID")
    return _safe_child_path(queue / f"{candidate_id}.review.json", queue)


def _review_receipt(
    candidate: Mapping[str, Any],
    candidate_hash: str,
    reviewer_id: str,
    reviewed_at: str | None,
    decision: str,
    *,
    reason: str | None = None,
    notes: str | None = None,
    graph_revision: str | None = None,
) -> Dict[str, Any]:
    reviewer = _bounded_text(reviewer_id, 100)
    if not reviewer: raise WorkflowError("reviewer ID is required")
    timestamp = reviewed_at or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    timestamp = _bounded_text(timestamp, 64)
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WorkflowError("reviewedAt must be an ISO timestamp") from exc
    receipt = {
        "schemaVersion": REVIEW_SCHEMA,
        "candidateId": candidate.get("candidateId"),
        "candidateHash": candidate_hash,
        "baseGraphRevision": candidate.get("baseGraphRevision"),
        "decision": decision,
        "status": decision,
        "reviewerId": reviewer,
        "reviewedAt": timestamp,
        "reason": _bounded_text(reason, 500) if reason is not None else "",
        "notes": _bounded_text(notes, 500) if notes is not None else "",
    }
    if graph_revision is not None: receipt["graphRevision"] = graph_revision
    return receipt


def reject_candidate(
    candidate: Mapping[str, Any],
    queue_dir: Path | str,
    reason: str,
    *,
    reviewer_id: str,
    reviewed_at: str | None = None,
    notes: str | None = None,
) -> Dict[str, Any]:
    candidate_id = str(candidate.get("candidateId") or "")
    if not ID_RE.fullmatch(candidate_id): raise WorkflowError("invalid candidate ID")
    bounded_reason = _bounded_text(reason, 500)
    if not bounded_reason: raise WorkflowError("reject reason is required")
    record = _review_receipt(candidate, _hash(candidate), reviewer_id, reviewed_at, "rejected", reason=bounded_reason, notes=notes)
    _atomic_write_json(_review_path(queue_dir, candidate_id), record)
    return record


def _write_graph_directory(path: Path, graph: Mapping[str, Any]) -> None:
    _atomic_write_json(path / "schema.json", graph["schema"])
    _atomic_write_json(path / "nodes.json", {"schemaVersion": graph["schema"]["schemaVersion"], "nodes": [graph["nodes"][key] for key in sorted(graph["nodes"])]})
    _atomic_write_json(path / "edges.json", {"schemaVersion": graph["schema"]["schemaVersion"], "edges": sorted(graph["edges"], key=lambda item: (str(item.get("from")), str(item.get("relation")), str(item.get("to"))))})
    _atomic_write_json(path / "question-links.json", {"schemaVersion": graph["schema"]["schemaVersion"], "links": {key: graph["questionLinks"][key] for key in sorted(graph["questionLinks"])}})


def approve_candidate(
    candidate: Mapping[str, Any],
    graph: Mapping[str, Any],
    output_dir: Path | str,
    queue_dir: Path | str,
    *,
    reviewer_id: str,
    reviewed_at: str | None = None,
    notes: str | None = None,
) -> Dict[str, Any]:
    report = inspect_candidate(candidate, graph)
    if not report["valid"]: return {"status": "blocked", "candidateId": candidate.get("candidateId"), "errors": report["errors"]}
    candidate_id = candidate["candidateId"]
    rebased_graph = _apply_candidate(graph, candidate)
    reviewer_receipt = _review_receipt(candidate, report["candidateHash"], reviewer_id, reviewed_at, "approved", notes=notes, graph_revision=rebased_graph["graphRevision"])
    output = _safe_child_path(output_dir, Path(output_dir).resolve().parent)
    if output.exists(): return {"status": "blocked", "candidateId": candidate_id, "errors": [{"code": "OUTPUT_EXISTS", "path": str(output), "message": "output revision already exists"}]}
    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=parent))
    receipt_path = _review_path(queue_dir, candidate_id)
    receipt_temporary = None
    output_committed = False
    try:
        _write_graph_directory(temporary, rebased_graph)
        graph_check = validate_graph_directory(temporary)
        if not graph_check["valid"]:
            raise WorkflowError("approved candidate produced an invalid graph: " + ", ".join(error["code"] for error in graph_check["errors"]))
        _atomic_write_json(temporary / "candidate.json", candidate)
        receipt_temporary = _write_json_temp(receipt_path, reviewer_receipt)
        os.replace(temporary, output)
        output_committed = True
        os.replace(receipt_temporary, receipt_path)
    except Exception:
        if temporary.exists(): shutil.rmtree(temporary)
        if receipt_temporary is not None and receipt_temporary.exists(): receipt_temporary.unlink()
        if output_committed and output.exists(): shutil.rmtree(output)
        raise
    return {"status": "approved", "candidateId": candidate_id, "graphRevision": rebased_graph["graphRevision"], "outputDir": str(output)}


def _load_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    packet = subparsers.add_parser("packet")
    packet.add_argument("--graph-dir", default="data/knowledge")
    packet.add_argument("--output-dir", default="reports/knowledge-patch")
    packet.add_argument("--node-id", action="append", dest="node_ids")
    packet.add_argument("--issues-json")
    packet.add_argument("--max-bytes", type=int, default=DEFAULT_PACKET_BYTES)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--graph-dir", default="data/knowledge")
    inspect.add_argument("--candidate", required=True)
    reject = subparsers.add_parser("reject")
    reject.add_argument("--candidate", required=True)
    reject.add_argument("--queue-dir", default="reports/knowledge-patch/queue")
    reject.add_argument("--reason", required=True)
    reject.add_argument("--reviewer-id", required=True)
    reject.add_argument("--reviewed-at")
    reject.add_argument("--notes")
    approve = subparsers.add_parser("approve")
    approve.add_argument("--graph-dir", default="data/knowledge")
    approve.add_argument("--candidate", required=True)
    approve.add_argument("--output-dir", required=True)
    approve.add_argument("--queue-dir", default="reports/knowledge-patch/queue")
    approve.add_argument("--reviewer-id", required=True)
    approve.add_argument("--reviewed-at")
    approve.add_argument("--notes")
    rebase = subparsers.add_parser("rebase")
    rebase.add_argument("--graph-dir", default="data/knowledge")
    rebase.add_argument("--candidate", required=True)
    args = parser.parse_args()
    try:
        if args.command == "packet":
            graph = load_graph_bundle(args.graph_dir)
            issues = _load_json(args.issues_json) if args.issues_json else []
            if isinstance(issues, Mapping): issues = issues.get("events", [])
            result = build_context_packet(graph, args.node_ids, issues, max_bytes=args.max_bytes)
            output = _safe_project_path(args.output_dir, Path.cwd(), ("reports/knowledge-patch", "data/knowledge/candidate-packets"))
            _atomic_write_json(output / "context-packet.json", {key: value for key, value in result.items() if key != "markdown"})
            (output / "context-packet.md").write_text(result["markdown"], encoding="utf-8")
            print(json.dumps({"ok": True, "graphRevision": graph["graphRevision"], "payloadBytes": result["payloadBytes"], "outputDir": str(output)}, ensure_ascii=False))
        elif args.command == "inspect":
            result = inspect_candidate(_load_json(args.candidate), load_graph_bundle(args.graph_dir))
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result["valid"] else 2
        elif args.command == "reject":
            queue = _safe_project_path(args.queue_dir, Path.cwd(), ("reports/knowledge-patch/queue",))
            print(json.dumps(reject_candidate(_load_json(args.candidate), queue, args.reason, reviewer_id=args.reviewer_id, reviewed_at=args.reviewed_at, notes=args.notes), ensure_ascii=False))
        elif args.command == "approve":
            output = _safe_project_path(args.output_dir, Path.cwd(), ("data/knowledge/candidate-revisions", "reports/knowledge-patch/revisions"))
            queue = _safe_project_path(args.queue_dir, Path.cwd(), ("reports/knowledge-patch/queue",))
            result = approve_candidate(_load_json(args.candidate), load_graph_bundle(args.graph_dir), output, queue, reviewer_id=args.reviewer_id, reviewed_at=args.reviewed_at, notes=args.notes)
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result["status"] == "approved" else 2
        elif args.command == "rebase":
            result = rebase_candidate(_load_json(args.candidate), load_graph_bundle(args.graph_dir))
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result["ok"] else 2
    except (OSError, json.JSONDecodeError, WorkflowError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
