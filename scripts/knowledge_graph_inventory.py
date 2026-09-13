# -*- coding: utf-8 -*-
"""Measure the legacy knowledge sources before canonical graph migration.

The inventory is deliberately source-oriented.  It does not import the browser
bundles or execute application code, so running it cannot mutate runtime state.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


INVENTORY_SCHEMA = "knowledge-graph-inventory.v1"
LEGACY_DAG_NODE_RE = re.compile(r"^\s*'([^']+)'\s*:\s*\{", re.MULTILINE)
STORAGE_KEY_RE = re.compile(r"['\"]([A-Z][A-Z0-9_]+_V\d+)['\"]")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_embedded_array(text: str, pattern: str) -> list[Any]:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not find embedded question array using {pattern!r}")
    return json.loads(match.group(1))


def _question_counts(root: Path) -> Dict[str, Dict[str, Any]]:
    pe_text = _read(root / "dashboard-data.js")
    gk_text = _read(root / "national-exams-data.js")
    pe_questions = _load_embedded_array(
        pe_text, r"questions:\s*(\[[\s\S]+?\]),\s*\n\s*sevenLayers:"
    )
    gk_questions = _load_embedded_array(
        gk_text, r"questions:\s*(\[[\s\S]+?\])\s*\}\;"
    )
    return {
        "PE": {
            "recordCount": len(pe_questions),
            "uniqueQidCount": len({record[0] for record in pe_questions}),
            "sourcePath": "dashboard-data.js",
        },
        "GK": {
            "recordCount": len(gk_questions),
            "uniqueQidCount": len({record[0] for record in gk_questions}),
            "sourcePath": "national-exams-data.js",
        },
    }


def _core_note_paths(root: Path) -> list[str]:
    note_root = root / "🧠 核心考點知識庫"
    paths = []
    for path in sorted(note_root.rglob("*.md")):
        if path.name == "README.md" or path.name.startswith("📊_"):
            continue
        paths.append(path.relative_to(root).as_posix())
    return paths


def _backup_storage_keys(root: Path) -> list[str]:
    keys: set[str] = set()
    state_root = root / "src" / "state"
    for path in sorted(state_root.glob("*.js")):
        keys.update(STORAGE_KEY_RE.findall(_read(path)))
    return sorted(keys)


def collect_inventory(root: Path | str) -> Dict[str, Any]:
    """Return measured legacy source metadata for *root*."""

    workspace = Path(root).resolve()
    dag_path = workspace / "src/data/knowledge-dag.js"
    dag_text = _read(dag_path)
    node_ids = LEGACY_DAG_NODE_RE.findall(dag_text)
    core_notes = _core_note_paths(workspace)
    mapping_rules = re.findall(r"nodeId\s*===\s*'([^']+)'", dag_text)
    manual_labels_text = _read(workspace / "src/data/manualTopicLabels.js")
    source_paths = [
        "src/data/knowledge-dag.js",
        "src/data/manualTopicLabels.js",
        "src/state/attemptStore.js",
        "src/state/sm2Store.js",
        "dashboard-data.js",
        "national-exams-data.js",
        "🧠 核心考點知識庫/",
    ]

    return {
        "schemaVersion": INVENTORY_SCHEMA,
        "workspace": str(workspace),
        "measuredAt": "source-scan",
        "legacyDag": {
            "nodeCount": len(node_ids),
            "nodeIds": node_ids,
            "sourcePath": "src/data/knowledge-dag.js",
        },
        "obsidian": {
            "coreNoteCount": len(core_notes),
            "coreNotePaths": core_notes,
            "excludedFiles": [
                "README.md",
                "📊_電機工程技師_6大考科11年高頻考點統計與命中率分析.md",
            ],
            "sourcePath": "🧠 核心考點知識庫/",
        },
        "questions": _question_counts(workspace),
        "mapping": {
            "ruleCount": len(set(mapping_rules)),
            "specificRuleNodeIds": sorted(set(mapping_rules)),
            "manualLabelCount": len(re.findall(r"['\"]EE-[0-9]{3}-[0-9]{2}-[0-9]+['\"]", manual_labels_text)),
            "hasSubjectFallback": "Fallback to first level-1/2 node of subject" in dag_text,
            "fallbackSource": "src/data/knowledge-dag.js",
        },
        "backup": {
            "storageKeys": _backup_storage_keys(workspace),
            "sourcePaths": ["src/state/attemptStore.js", "src/state/sm2Store.js"],
        },
        "sourcePaths": source_paths,
    }


def _markdown_report(inventory: Dict[str, Any]) -> str:
    dag = inventory["legacyDag"]
    obsidian = inventory["obsidian"]
    questions = inventory["questions"]
    mapping = inventory["mapping"]
    backup = inventory["backup"]
    lines = [
        "# 問題驅動知識圖譜 migration inventory",
        "",
        "> 本報告是對現有來源的實測盤點；它不是 canonical graph，也不會改動 runtime。",
        "",
        "## Measured counts",
        "",
        f"- Legacy `KNOWLEDGE_DAG` nodes: **{dag['nodeCount']}**",
        f"- Core Obsidian notes: **{obsidian['coreNoteCount']}**",
        f"- PE question records: **{questions['PE']['recordCount']}** ({questions['PE']['uniqueQidCount']} unique QIDs)",
        f"- GK question records: **{questions['GK']['recordCount']}** ({questions['GK']['uniqueQidCount']} unique QIDs)",
        f"- Specific mapping rules: **{mapping['ruleCount']}**",
        f"- Manual topic labels: **{mapping['manualLabelCount']}**",
        f"- Subject fallback present: **{mapping['hasSubjectFallback']}**",
        "",
        "## Mapping and backup observations",
        "",
        "- The current question mapper is keyword/rule based and contains a subject fallback. Unknown coverage must be measured before replacing it.",
        "- Backup storage keys are collected from `src/state/*.js`; the canonical migration must decide which keys become versioned sections.",
        "- PE and GK question records are counted from separate generated bundles and remain separate migration inputs.",
        "",
        "## Backup storage keys",
        "",
    ]
    lines.extend(f"- `{key}`" for key in backup["storageKeys"])
    lines.extend(["", "## Source paths", ""])
    lines.extend(f"- `{path}`" for path in inventory["sourcePaths"])
    lines.extend([
        "",
        "## Review queue",
        "",
        "- Review every legacy mapping that depends on the subject fallback before enabling a fail-closed adapter.",
        "- Select the first golden QID slice from the measured PE/GK records and attach evidence before canonical promotion.",
        "- Preserve generated bundles and existing Obsidian notes until the replacement projection passes its regression checks.",
        "",
    ])
    return "\n".join(lines)


def write_inventory(
    inventory: Dict[str, Any], output_dir: Path | str, report_dir: Path | str | None = None
) -> Tuple[Path, Path]:
    """Write JSON inventory and Markdown report, returning both paths."""

    json_dir = Path(output_dir)
    markdown_dir = Path(report_dir) if report_dir is not None else json_dir
    json_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / "migration-inventory.json"
    report_path = markdown_dir / "knowledge-graph-inventory.md"
    json_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report_path.write_text(_markdown_report(inventory), encoding="utf-8")
    return json_path, report_path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    output_dir = args.output_dir or workspace / "data/knowledge"
    report_dir = args.report_dir or workspace / "reports"
    json_path, report_path = write_inventory(
        collect_inventory(workspace), output_dir, report_dir
    )
    print(f"Wrote inventory: {json_path}")
    print(f"Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
