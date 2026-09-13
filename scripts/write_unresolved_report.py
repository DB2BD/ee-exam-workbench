#!/usr/bin/env python3
"""Write the measured legacy, coverage and manual-review migration report."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def build_report():
    inventory = read_json(ROOT / "data/knowledge/migration-inventory.json", {})
    build = read_json(ROOT / "reports/knowledge-graph-build.json", {})
    validation = read_json(ROOT / "reports/knowledge-graph-validation.json", {})
    legacy = int(inventory.get("legacyDag", {}).get("nodeCount", 0))
    canonical = int(build.get("sourceCounts", {}).get("canonicalNodeCount", 0))
    canonical_payload = read_json(ROOT / "data/knowledge/nodes.json", {})
    canonical_legacy = sum(
        1 for node in canonical_payload.get("nodes", [])
        if isinstance(node, dict) and node.get("provenance", {}).get("legacyNodeId")
        and node.get("examFamily") == "PE"
    )
    unknown = int(build.get("unknownQuestionCount", 0))
    manual = int(inventory.get("mapping", {}).get("manualLabelCount", 0))
    links = read_json(ROOT / "data/knowledge/question-links.json", {}).get("links", {})
    priority_counts = {}
    for link in links.values() if isinstance(links, dict) else []:
        priority = link.get("sourcePriority", "unknown") if isinstance(link, dict) else "unknown"
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    return "\n".join([
        "# 問題驅動知識圖譜 unresolved / manual review",
        "",
        "> 這份報告記錄 canonical graph 的完整覆蓋與仍需人工處理的來源；unknown 不會被任意 fallback 節點取代。",
        "",
        "## 測量結果",
        "",
        f"- Legacy DAG 節點：{legacy}",
        f"- Canonical graph 節點：{canonical}",
        f"- Legacy DAG 已鏡射為 PE canonical 主題節點：{canonical_legacy}/{legacy}",
        f"- 尚未建立 approved canonical question link：{unknown} 題",
        f"- Link 來源：deterministic {priority_counts.get('deterministic', 0)}、manual {priority_counts.get('manual', 0)}、approved_ai {priority_counts.get('approved_ai', 0)}",
        f"- 現有人工 topic labels：{manual} 筆",
        f"- Canonical graph revision：`{build.get('graphRevision', validation.get('graphRevision', 'unknown'))}`",
        "",
        "## 處理規則",
        "",
        "- unknown QID 保留 unknown 狀態，等待 evidence 與人工 review。",
        "- manual topic labels 保留在既有使用者資料，不由 canonical generator 覆寫。",
        "- PE/GK 題目連結都必須通過 validator 與完整覆蓋 gate；新增來源若證據不足，保留 unknown 並列入人工複核。",
        "",
    ])


def main():
    target = ROOT / "reports/problem-driven-unresolved.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_report(), encoding="utf-8")
    print(f"Wrote unresolved report: {target}")


if __name__ == "__main__":
    main()
