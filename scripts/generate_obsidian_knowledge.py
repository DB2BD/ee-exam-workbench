# -*- coding: utf-8 -*-
"""Generate stable, reviewable Obsidian notes from the canonical graph.

Generated notes have their own path and marker.  The generator performs a
complete drift/conflict preflight before writing any note, so an edited note
cannot be silently replaced by a later graph build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:  # Direct ``python scripts/generate_obsidian_knowledge.py``.
    from knowledge_graph import validate_graph_directory


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH_DIR = WORKSPACE / "data" / "knowledge"
DEFAULT_OUTPUT_ROOT = WORKSPACE / "🧠 問題驅動知識庫"
DEFAULT_PERSONAL_ROOT = WORKSPACE / "📝 個人知識補充"
DEFAULT_REPORT = WORKSPACE / "reports" / "obsidian-knowledge-build.json"
SAFE_NODE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CATEGORY_NAMES = {
    "ct": "01_電路學",
    "el": "02_電子學_含電力電子",
    "em": "03_工程數學",
    "emach": "04_電機機械",
    "ps": "05_電力系統",
    "dist": "06_工業配電",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def _category_for_node(node: Mapping[str, Any]) -> str:
    node_id = str(node["nodeId"])
    if node.get("nodeType") == "mainline":
        return "00_主線"
    if node_id.startswith("q-"):
        qid = str(node.get("qid", ""))
        parts = qid.split("-")
        if len(parts) >= 3:
            subject = parts[2]
            category = {
                "01": "01_電路學",
                "02": "02_電子學_含電力電子",
                "03": "03_工程數學",
                "04": "04_電機機械",
                "05": "05_電力系統",
                "06": "06_工業配電",
            }.get(subject)
            if category:
                return category
        return "99_題目"
    prefix = node_id.split("-", 1)[0]
    if prefix == "gk":
        prefix = node_id[3:].split("-", 1)[0]
    return CATEGORY_NAMES.get(prefix, "99_其他")


def _successor_ids(node_id: str, nodes: Mapping[str, Mapping[str, Any]], trail: tuple[str, ...] = ()) -> list[str]:
    if node_id in trail:
        return [node_id]
    node = nodes[node_id]
    if node.get("lifecycle") not in {"retired", "merged"}:
        return [node_id]
    successors = node.get("successorNodeIds", [])
    if not successors:
        return [node_id]
    resolved: list[str] = []
    for successor in successors:
        resolved.extend(_successor_ids(successor, nodes, trail + (node_id,)))
    return list(dict.fromkeys(resolved))


def _frontmatter(content: str) -> tuple[dict[str, str], str] | None:
    if not content.startswith("---\n"):
        return None
    delimiter = "\n---\n"
    end = content.find(delimiter, 4)
    if end < 0:
        return None
    values: dict[str, str] = {}
    for line in content[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values, content[end + len(delimiter) :]


def _error(code: str, path: Path, message: str, node_id: str | None = None) -> dict[str, str]:
    error = {"code": code, "path": str(path), "message": message}
    if node_id:
        error["nodeId"] = node_id
    return error


def _render_note(
    node: Mapping[str, Any],
    nodes: Mapping[str, Mapping[str, Any]],
    edges: list[Mapping[str, Any]],
    links: Mapping[str, Mapping[str, Any]],
    graph_revision: str,
) -> tuple[str, str]:
    node_id = str(node["nodeId"])
    outgoing = sorted(
        [edge for edge in edges if edge.get("from") == node_id and edge.get("reviewStatus") == "approved"],
        key=lambda edge: (str(edge.get("relation")), str(edge.get("to")), str(edge.get("why"))),
    )
    linked_questions = sorted(
        [link for key, link in links.items() if node_id in link.get("nodeIds", [])],
        key=lambda link: str(link.get("qid", "")),
    )
    source_payload = {
        "node": node,
        "approvedEdges": outgoing,
        "linkedQuestions": linked_questions,
    }
    source_hash = _hash(source_payload)

    body_lines = [
        f"# {node['title']}",
        "",
        "> 此檔案由 canonical knowledge graph 產生；請將個人補充寫在 `📝 個人知識補充/`。",
        "",
        "## Canonical identity",
        f"- node: `{node_id}`",
        f"- type: `{node['nodeType']}`",
        f"- exam family: `{node['examFamily']}`",
        f"- lifecycle: `{node['lifecycle']}`",
        "",
        "## Semantic links",
    ]
    if outgoing:
        for edge in outgoing:
            target = str(edge["to"])
            resolved = _successor_ids(target, nodes)
            if resolved != [target]:
                target_text = (
                    f"retired target `{target}` resolved to "
                    + ", ".join(f"[[{item}]]" for item in resolved)
                )
            else:
                target_text = f"[[{target}]]"
            body_lines.append(f"- `{edge['relation']}` → {target_text} — {edge['why']}")
    else:
        body_lines.append("- 尚無已核准的語意邊。")

    body_lines.extend(["", "## Linked questions"])
    if linked_questions:
        for link in linked_questions:
            body_lines.append(f"- [[{link['qid']}]]（confidence: {link['confidence']}）")
    else:
        body_lines.append("- 尚無已核准的題目連結。")

    body_lines.extend(["", "## Provenance"])
    provenance = node.get("provenance", {})
    if isinstance(provenance, dict):
        for key in sorted(provenance):
            value = provenance[key]
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            body_lines.append(f"- {key}: {value}")
    if node.get("lifecycle") in {"retired", "merged"}:
        body_lines.append(f"- successorNodeIds: {', '.join(f'[[{item}]]' for item in node.get('successorNodeIds', []))}")
    body = "\n".join(body_lines).rstrip() + "\n"
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    frontmatter = "\n".join(
        [
            "---",
            "generated: true",
            "generator: scripts/generate_obsidian_knowledge.py",
            f"nodeId: {node_id}",
            f"nodeType: {node['nodeType']}",
            f"examFamily: {node['examFamily']}",
            f"lifecycle: {node['lifecycle']}",
            f"graphRevision: {graph_revision}",
            f"sourceHash: {source_hash}",
            f"generatedBodyHash: {body_hash}",
            "---",
            "",
        ]
    )
    return frontmatter + body, source_hash


def generate_obsidian_knowledge(
    graph_dir: Path | str = DEFAULT_GRAPH_DIR,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    report_path: Path | str | None = DEFAULT_REPORT,
    personal_root: Path | str = DEFAULT_PERSONAL_ROOT,
) -> dict[str, Any]:
    graph_root = Path(graph_dir)
    destination = Path(output_root)
    personal = Path(personal_root)
    validation = validate_graph_directory(graph_root)
    report: dict[str, Any] = {
        "schemaVersion": "obsidian-knowledge-build.v1",
        "valid": False,
        "graphRevision": validation["graphRevision"],
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "sourceIdentity": {"canonicalGraphRevision": validation["graphRevision"]},
        "outputIdentity": {"kind": "obsidian-generated-notes", "path": str(destination.resolve())},
        "generatedNoteCount": 0,
        "preservedPersonalRoot": str(personal),
        "errors": list(validation["errors"]),
    }
    if validation["valid"]:
        nodes_payload = _load_json(graph_root / "nodes.json")
        edges_payload = _load_json(graph_root / "edges.json")
        links_payload = _load_json(graph_root / "question-links.json")
        nodes_list = sorted(nodes_payload["nodes"], key=lambda item: item["nodeId"])
        nodes = {node["nodeId"]: node for node in nodes_list}
        edges = edges_payload["edges"]
        links = links_payload["links"]
        rendered: dict[Path, str] = {}
        source_hashes: dict[str, str] = {}
        for node in nodes_list:
            node_id = str(node["nodeId"])
            if not SAFE_NODE_ID.fullmatch(node_id):
                report["errors"].append(
                    _error(
                        "INVALID_OUTPUT_ID",
                        destination,
                        f"nodeId {node_id!r} cannot be used as a stable filename",
                        node_id,
                    )
                )
                continue
            path = destination / _category_for_node(node) / f"{node_id}.md"
            content, source_hash = _render_note(node, nodes, edges, links, validation["graphRevision"])
            rendered[path] = content
            source_hashes[node_id] = source_hash

        # Preflight every destination before writing any generated note.
        for path, expected in sorted(rendered.items(), key=lambda item: str(item[0])):
            if not path.exists():
                continue
            current = path.read_text(encoding="utf-8")
            parsed = _frontmatter(current)
            node_id = path.stem
            if parsed is None or parsed[0].get("generated") != "true":
                report["errors"].append(
                    _error(
                        "GENERATED_PATH_CONFLICT",
                        path,
                        "existing file is not marked as generated; move it to the personal-note path before generating",
                        node_id,
                    )
                )
                continue
            metadata, body = parsed
            recorded_hash = metadata.get("generatedBodyHash")
            actual_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
            if metadata.get("nodeId") != node_id or recorded_hash != actual_hash:
                report["errors"].append(
                    _error(
                        "GENERATED_NOTE_DRIFT",
                        path,
                        "generated note body or identity changed; review the edit, then regenerate the note",
                        node_id,
                    )
                )

        report["sourceCounts"] = {
            "canonicalNodeCount": len(nodes_list),
            "canonicalEdgeCount": len(edges),
            "canonicalQuestionLinkCount": len(links),
        }
        report["sourceHashes"] = {key: source_hashes[key] for key in sorted(source_hashes)}
        report["generatedNoteCount"] = len(rendered)
        report["generatedPaths"] = [str(path) for path in sorted(rendered)]
        report["valid"] = not report["errors"]
        if report["valid"]:
            for path in sorted(rendered):
                _atomic_write(path, rendered[path])

    report["errors"] = sorted(
        report["errors"], key=lambda item: (item.get("code", ""), item.get("path", ""), item.get("message", ""))
    )
    report["checks"] = [
        {"name": "canonical graph validation", "passed": bool(validation["valid"])},
        {"name": "generated note preflight", "passed": not any(
            error.get("code") in {"GENERATED_PATH_CONFLICT", "GENERATED_NOTE_DRIFT", "INVALID_OUTPUT_ID"}
            for error in report["errors"]
        )},
    ]
    report["blockingFailures"] = [error["code"] for error in report["errors"]]
    if report_path is not None:
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph-dir", type=Path, default=DEFAULT_GRAPH_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--personal-root", type=Path, default=DEFAULT_PERSONAL_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", action="store_true", help="Print the machine-readable build report.")
    args = parser.parse_args()
    report = generate_obsidian_knowledge(args.graph_dir, args.output_root, args.report, args.personal_root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["valid"] else "FAIL"
        print(f"{status}: {report['graphRevision']} ({report['generatedNoteCount']} generated notes)")
        for error in report["errors"]:
            print(f"- {error['code']} at {error['path']}: {error['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
