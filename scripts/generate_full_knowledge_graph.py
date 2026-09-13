# -*- coding: utf-8 -*-
"""Generate the complete PE/GK canonical knowledge graph.

The website's question bundles and the legacy DAG remain source data.  This
script turns those sources into the family-isolated canonical graph consumed
by ``build_knowledge_graph.py``.  It is deliberately deterministic so a
future taxonomy or source update can be regenerated and reviewed as a diff.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

try:
    from scripts.question_schema import load_questions_from_bundle
except ModuleNotFoundError:
    from question_schema import load_questions_from_bundle


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "data" / "knowledge"
LEGACY_DAG = ROOT / "src" / "data" / "knowledge-dag.js"
PE_BUNDLE = ROOT / "dashboard-data.js"
GK_BUNDLE = ROOT / "national-exams-data.js"


SUBJECTS = {
    "01": ("電路學", "電路學主線", "circuit"),
    "02": ("電子學", "電子學主線", "electronics"),
    "03": ("工程數學", "工程數學主線", "math"),
    "04": ("電機機械", "電機機械主線", "machines"),
    "05": ("電力系統", "電力系統主線", "power"),
    "06": ("工業配電", "工業配電主線", "distribution"),
}

# These classifications are semantic metadata used by diagnosis routing.  A
# missing item gets the conservative mechanism type; the question link still
# carries the exact legacy topic and evidence.
PROCEDURE_NODES = {
    "ct-node-mesh", "ct-max-power", "ct-superposition", "ct-two-port",
    "ct-laplace-circuit", "el-pe-buck-boost", "el-pe-inverter-spwm",
    "el-pe-thyristor-rectifier", "em-second-order-ode-nonhomogeneous",
    "em-laplace-transform", "em-pde-separation", "em-svd-linear-systems",
    "emach-single-phase-transformer", "emach-autotransformer",
    "emach-three-phase-transformer", "emach-dc-motor-generator",
    "emach-induction-motor-torque", "emach-synchronous-generator-round",
    "emach-synchronous-salient-pole", "ps-load-flow-admittance",
    "ps-power-analysis", "ps-economic-dispatch", "ps-transmission-line-models",
    "ps-three-phase-fault", "ps-unsymmetrical-faults",
    "ps-transient-stability-equal-area", "ps-system-protection-relay",
    "ps-state-estimation-wls", "dist-lighting-design", "dist-motor-installation",
    "dist-voltage-drop", "dist-power-factor-correction",
    "dist-short-circuit-capacity", "dist-protection-coordination",
    "dist-harmonics-mitigation", "dist-arc-flash-ieee80",
}

# The 19 GK records without a compiler-provided PE cross-reference.  Each
# entry was checked against its official question crop and validated solution
# section; the source paths are retained in the generated link evidence.
GK_UNRELATED_MAPPING = {
    "GK-112-01-3": ["ct-divider-equiv"],
    "GK-112-02-4": ["el-bjt-bias-small-signal"],
    "GK-112-03-3": ["em-vector-analysis"],
    "GK-112-03-MC04": ["em-matrix-det-inv"],
    "GK-112-03-MC11": ["em-complex-cauchy-residue"],
    "GK-112-03-MC18": ["em-laplace-transform"],
    "GK-111-01-3": ["ct-phasor-ac", "ct-node-mesh"],
    "GK-111-02-2": ["el-mosfet-bias-small-signal", "el-bjt-bias-small-signal"],
    "GK-111-03-MC01": ["em-matrix-det-inv"],
    "GK-111-03-MC02": ["em-matrix-det-inv"],
    "GK-111-03-MC04": ["em-eigen-diagonal"],
    "GK-111-03-MC06": ["em-vector-analysis"],
    "GK-111-03-MC07": ["em-matrix-det-inv"],
    "GK-111-03-MC13": ["em-first-order-ode"],
    "GK-110-02-3": ["el-mosfet-bias-small-signal"],
    "GK-110-03-MC02": ["em-svd-linear-systems"],
    "GK-110-03-MC03": ["em-matrix-det-inv"],
    "GK-110-03-MC09": ["em-complex-cauchy-residue"],
    "GK-110-03-MC15": ["em-second-order-ode-nonhomogeneous"],
}


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _load_js_binding(path: Path, binding: str) -> Any:
    script = r"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const sandbox = { console: { log() {} } };
vm.runInNewContext(source + `\nglobalThis.__value = ${process.argv[2]};`, sandbox);
process.stdout.write(JSON.stringify(sandbox.__value));
"""
    result = subprocess.run(
        ["node", "-e", script, str(path), binding],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _load_sources() -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]], dict[str, list], dict[str, list]]:
    legacy = _load_js_binding(LEGACY_DAG, "KNOWLEDGE_DAG")
    pe_taxonomy = _load_js_binding(PE_BUNDLE, "QUESTION_TAXONOMY_MAP")
    pe_questions = load_questions_from_bundle(PE_BUNDLE)
    gk_questions = load_questions_from_bundle(GK_BUNDLE)
    return legacy, pe_taxonomy, pe_questions, gk_questions


def _node_type(node_id: str) -> str:
    return "procedure" if node_id in PROCEDURE_NODES else "mechanism"


def _legacy_node(node_id: str, legacy: Mapping[str, Mapping[str, Any]], family: str = "PE") -> dict[str, Any]:
    source = legacy[node_id]
    prefix = "" if family == "PE" else "gk-"
    canonical_id = f"{prefix}{node_id}"
    return {
        "nodeId": canonical_id,
        "nodeType": _node_type(node_id),
        "title": source["name"],
        "examFamily": family,
        "lifecycle": "active",
        "subject": source["subject"],
        "subjectName": source["subjectName"],
        "level": source["level"],
        "prereqs": [f"{prefix}{item}" for item in source["prereqs"]],
        "coreFormula": source["coreFormula"],
        "keyTrap": source["keyTrap"],
        "provenance": {
            "sourceType": "legacy-dag" if family == "PE" else "family-isolated-legacy-dag",
            "sourcePath": "src/data/knowledge-dag.js",
            "legacyNodeId": node_id,
            **({} if family == "PE" else {"familyIsolation": "GK"}),
        },
        "nodeRevisionHash": f"{family.lower()}-legacy-{node_id}-v1",
    }


def _topic_node_ids(evidence: Mapping[str, Any]) -> list[str]:
    primary = evidence.get("primaryChapter")
    secondary = evidence.get("secondaryTopicIds", [])
    ids = [primary] if isinstance(primary, str) else []
    ids.extend(item for item in secondary if isinstance(item, str))
    return list(dict.fromkeys(ids))


def _link(
    qid: str,
    family: str,
    node_ids: list[str],
    evidence: list[str],
    confidence: float,
    source_priority: str,
) -> dict[str, Any]:
    prefix = "gk-" if family == "GK" else ""
    return {
        "qid": qid,
        "examFamily": family,
        "nodeIds": [f"{prefix}{node_id}" for node_id in node_ids],
        "confidence": confidence,
        "evidence": evidence,
        "reviewStatus": "approved",
        "sourcePriority": source_priority,
    }


def _edge(
    from_id: str,
    to_id: str,
    family: str,
    prerequisite: Mapping[str, Any],
    target: Mapping[str, Any],
) -> dict[str, Any]:
    prefix = "gk-" if family == "GK" else ""
    return {
        "from": f"{prefix}{from_id}",
        "relation": "prerequisite",
        "to": f"{prefix}{to_id}",
        "why": f"掌握「{target['name']}」前，先建立「{prerequisite['name']}」這個前置概念。",
        "confidence": 0.95,
        "evidence": [f"src/data/knowledge-dag.js:{to_id}", "migration:explicit-legacy-prereq"],
        "reviewStatus": "approved",
    }


def _mainline_edge(mainline_id: str, topic_id: str, family: str, subject: str) -> dict[str, Any]:
    prefix = "gk-" if family == "GK" else ""
    return {
        "from": mainline_id,
        "relation": "mainline_precedes",
        "to": f"{prefix}{topic_id}",
        "why": f"{SUBJECTS[subject][1]}從此主題開始建立可追蹤的考點路徑。",
        "confidence": 0.93,
        "evidence": ["migration:legacy-dag-subject-root"],
        "reviewStatus": "approved",
    }


def generate() -> dict[str, Any]:
    legacy, pe_taxonomy, pe_questions, gk_questions = _load_sources()
    existing_nodes = json.loads((GRAPH / "nodes.json").read_text(encoding="utf-8"))["nodes"]
    existing_edges = json.loads((GRAPH / "edges.json").read_text(encoding="utf-8"))["edges"]
    # Drop edges produced by an earlier run before rebuilding them.  This
    # keeps regeneration idempotent while preserving hand-authored golden
    # edges whose evidence does not use the migration marker.
    existing_edges = [
        edge for edge in existing_edges
        if not any(str(item).startswith("migration:") for item in edge.get("evidence", []))
    ]

    nodes_by_id = {node["nodeId"]: node for node in existing_nodes}
    for node_id in sorted(legacy):
        nodes_by_id[node_id] = _legacy_node(node_id, legacy, "PE")

    # GK has subjects 01–05.  Keep its nodes separate so an answer in one exam
    # family cannot create a weakness event in the other family.
    gk_subjects = {row[1] for row in gk_questions}
    for node_id, source in sorted(legacy.items()):
        if source["subject"] in gk_subjects:
            nodes_by_id[f"gk-{node_id}"] = _legacy_node(node_id, legacy, "GK")

    # Add one explicit mainline per subject and per exam family.
    for family, subjects in (("PE", set(SUBJECTS)), ("GK", gk_subjects)):
        for subject in sorted(subjects):
            mainline_id = f"{family.lower()}-mainline-{SUBJECTS[subject][2]}"
            if mainline_id not in nodes_by_id:
                nodes_by_id[mainline_id] = {
                    "nodeId": mainline_id,
                    "nodeType": "mainline",
                    "title": SUBJECTS[subject][1],
                    "examFamily": family,
                    "lifecycle": "active",
                    "subject": subject,
                    "subjectName": SUBJECTS[subject][0],
                    "level": 0,
                    "provenance": {
                        "sourceType": "migration-subject-mainline",
                        "sourcePath": "src/data/knowledge-dag.js",
                    },
                    "nodeRevisionHash": f"{family.lower()}-mainline-{subject}-v1",
                }

    edges_by_key = {(edge["from"], edge["relation"], edge["to"]): edge for edge in existing_edges}
    for family, subjects in (("PE", set(SUBJECTS)), ("GK", gk_subjects)):
        for node_id, source in sorted(legacy.items()):
            if source["subject"] not in subjects:
                continue
            for prereq in source["prereqs"]:
                edge = _edge(prereq, node_id, family, legacy[prereq], source)
                edges_by_key.setdefault((edge["from"], edge["relation"], edge["to"]), edge)

        for subject in sorted(subjects):
            candidates = [
                source for source in legacy.values()
                if source["subject"] == subject and not source["prereqs"]
            ]
            if not candidates:
                candidates = [source for source in legacy.values() if source["subject"] == subject]
            min_level = min(source["level"] for source in candidates)
            roots = sorted(source["id"] for source in candidates if source["level"] == min_level)
            mainline_id = f"{family.lower()}-mainline-{SUBJECTS[subject][2]}"
            for root_id in roots:
                edge = _mainline_edge(mainline_id, root_id, family, subject)
                edges_by_key.setdefault((edge["from"], edge["relation"], edge["to"]), edge)

    links: dict[str, dict[str, Any]] = {}
    pe_by_id = {row[0]: row for row in pe_questions}
    for qid, row in sorted(pe_by_id.items()):
        evidence = pe_taxonomy.get(qid)
        if not isinstance(evidence, dict):
            raise RuntimeError(f"PE question has no taxonomy evidence: {qid}")
        node_ids = _topic_node_ids(evidence)
        if not node_ids or any(node_id not in legacy for node_id in node_ids):
            raise RuntimeError(f"PE taxonomy references a missing legacy node: {qid} -> {node_ids}")
        source = evidence.get("source")
        source_priority = "manual" if source == "manual-topic-confirmed" else "deterministic"
        confidence = 0.96 if source == "manual-topic-confirmed" else 0.92 if source == "canonical-title-override" else 0.90
        links[f"PE:{qid}"] = _link(
            qid,
            "PE",
            node_ids,
            [f"dashboard-data.js:{qid}", f"data/taxonomy/alias-map.json:{node_ids[0]}"],
            confidence,
            source_priority,
        )

    for row in sorted(gk_questions, key=lambda item: item[0]):
        qid = row[0]
        related = row[13]
        if related:
            pe_evidence = pe_taxonomy.get(related)
            if not isinstance(pe_evidence, dict):
                raise RuntimeError(f"GK related PE question has no taxonomy evidence: {qid} -> {related}")
            node_ids = _topic_node_ids(pe_evidence)
            evidence = [
                f"national-exams-data.js:{qid}",
                f"national-exams-data.js:{qid}:relatedPEId={related}",
                f"dashboard-data.js:{related}",
            ]
            links[f"GK:{qid}"] = _link(qid, "GK", node_ids, evidence, 0.90, "deterministic")
        else:
            node_ids = GK_UNRELATED_MAPPING.get(qid)
            if not node_ids:
                raise RuntimeError(f"GK question has no mapping rule: {qid}")
            solution = str(row[6])
            links[f"GK:{qid}"] = _link(
                qid,
                "GK",
                node_ids,
                [f"national-exams-data.js:{qid}", solution, f"official-solution-reviewed:{qid}"],
                0.93,
                "approved_ai",
            )

    expected_qids = {row[0] for row in pe_questions} | {row[0] for row in gk_questions}
    if set(link["qid"] for link in links.values()) != expected_qids:
        raise RuntimeError("canonical link coverage does not equal PE/GK question coverage")

    nodes = sorted(nodes_by_id.values(), key=lambda node: node["nodeId"])
    edges = sorted(edges_by_key.values(), key=lambda edge: (edge["from"], edge["relation"], edge["to"]))
    (GRAPH / "nodes.json").write_text(
        json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "nodes": nodes}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (GRAPH / "edges.json").write_text(
        json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "edges": edges}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (GRAPH / "question-links.json").write_text(
        json.dumps({"schemaVersion": "canonical-knowledge-graph.v1", "links": {key: links[key] for key in sorted(links)}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "questionLinkCount": len(links),
        "peQuestionCount": len(pe_questions),
        "gkQuestionCount": len(gk_questions),
        "graphInputHash": _json_hash({"nodes": nodes, "edges": edges, "links": links}),
    }


if __name__ == "__main__":
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
