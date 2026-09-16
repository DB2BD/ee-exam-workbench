#!/usr/bin/env python3
"""Run the offline acceptance matrix and write a compact, reproducible report."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:  # Direct ``python scripts/run_change_acceptance.py`` execution.
    from knowledge_graph import validate_graph_directory


ROOT = Path(__file__).resolve().parents[1]


def run_check(name, command):
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output = (completed.stdout + completed.stderr).strip()
    return {
        "name": name,
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "outputTail": output[-1200:],
    }


def build_acceptance_report(checks, graph_revision, generated_at, output_path, *, capacity_report=None):
    blocking_failures = [item["name"] for item in checks if not item["ok"]]
    freshness_check = next((item for item in checks if item["name"] == "acceptance report freshness"), None)
    report = {
        "schemaVersion": "problem-driven-obsidian-acceptance.v1",
        "change": "problem-driven-obsidian-warning-remediation",
        "offline": True,
        "generatedAt": generated_at,
        "graphRevision": graph_revision,
        "sourceIdentity": {"canonicalGraphRevision": graph_revision},
        "outputIdentity": {"kind": "acceptance-report", "path": str(Path(output_path).resolve())},
        "checks": checks,
        "freshnessPass": bool(freshness_check and freshness_check["ok"]),
        "blockingFailures": blocking_failures,
        "passed": not blocking_failures,
    }
    if capacity_report is not None:
        report["capacity"] = {
            key: capacity_report.get(key)
            for key in (
                "maxIssueEvents", "maxIssueBytes", "maxBackupBytes", "measuredIssueEventCount",
                "measuredIssueBytes", "measuredLearningDataBytes", "issueCapacityPass", "backupCapacityPass",
            )
        }
        report["recovery"] = {
            key: capacity_report.get(key)
            for key in ("recoveryFixture", "recoveryTimeMs", "recoveryTimeThresholdMs", "recoveryTimePass")
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=str(ROOT / "reports/problem-driven-obsidian-acceptance.json"))
    args = parser.parse_args()
    checks = [
        ("targeted learning tests", ["python3", "-m", "unittest", "tests.test_knowledge_graph_schema", "tests.test_knowledge_graph_validator_cli", "tests.test_knowledge_issue_store", "tests.test_weakness_projection", "tests.test_weakness_view", "tests.test_knowledge_review_store", "tests.test_backup_restore", "tests.test_knowledge_patch_workflow"]),
        ("full unittest suite", ["python3", "-m", "unittest", "discover", "-s", "tests"]),
        ("full solution coverage audit", ["python3", "scripts/audit_all_solutions_vs_exams.py"]),
        ("annual canonical alignment", ["python3", "scripts/audit_annual_canonical_alignment.py"]),
        ("canonical graph validator", ["python3", "scripts/validate_knowledge_graph.py", "--graph-dir", "data/knowledge", "--report", "reports/knowledge-graph-validation.json", "--json"]),
        ("canonical graph build", ["python3", "scripts/build_knowledge_graph.py", "--graph-dir", "data/knowledge", "--output", "src/data/knowledge-dag.generated.js", "--report", "reports/knowledge-graph-build.json", "--json"]),
        ("Obsidian knowledge generation", ["python3", "scripts/generate_obsidian_knowledge.py", "--graph-dir", "data/knowledge", "--output-root", "🧠 問題驅動知識庫", "--personal-root", "📝 個人知識補充", "--report", "reports/obsidian-knowledge-build.json", "--json"]),
        ("workbench build", ["python3", "scripts/build_workbench.py"]),
        ("HTML and JavaScript syntax", ["python3", "scripts/check_html_js_syntax.py"]),
        ("learning capacity measurement", ["python3", "scripts/measure_learning_data_capacity.py"]),
        ("acceptance report freshness", ["python3", "scripts/acceptance_freshness.py", "--graph-dir", "data/knowledge", "--report", "canonical=reports/knowledge-graph-validation.json", "--report", "website=reports/knowledge-graph-build.json", "--report", "obsidian=reports/obsidian-knowledge-build.json", "--report", "capacity=reports/learning-data-capacity.json"]),
        ("unresolved and manual-review report", ["python3", "scripts/write_unresolved_report.py"]),
    ]
    results = [run_check(name, command) for name, command in checks]
    path = Path(args.report)
    path.parent.mkdir(parents=True, exist_ok=True)
    graph = validate_graph_directory(ROOT / "data" / "knowledge")
    capacity_path = ROOT / "reports" / "learning-data-capacity.json"
    capacity_report = json.loads(capacity_path.read_text(encoding="utf-8")) if capacity_path.exists() else None
    report = build_acceptance_report(
        results,
        graph["graphRevision"],
        datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        path,
        capacity_report=capacity_report,
    )
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "blockingFailures": report["blockingFailures"], "report": str(path)}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
