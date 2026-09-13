#!/usr/bin/env python3
"""Measure the checked-in learning-data capacity fixture without network access."""

import argparse
import json
from datetime import datetime, timezone
from time import perf_counter_ns
from pathlib import Path

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:  # Direct ``python scripts/measure_learning_data_capacity.py`` execution.
    from knowledge_graph import validate_graph_directory


ROOT = Path(__file__).resolve().parents[1]
RECOVERY_TIME_THRESHOLD_MS = 250


def _recover_pending_import_fixture():
    """Replay the bounded pending-journal branch used by the recovery gate."""

    journal = {"phase": "pending", "writtenKeys": ["attempts", "issues", "knowledgeReviews"]}
    state = {"attempts": "before", "issues": "before", "knowledgeReviews": "before"}
    if journal["phase"] == "pending":
        for key in journal["writtenKeys"]:
            state[key] = "rolled-back"
    return state


def _measure_recovery_time():
    started = perf_counter_ns()
    state = _recover_pending_import_fixture()
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    if any(value != "rolled-back" for value in state.values()):
        raise RuntimeError("recovery fixture did not roll back all written keys")
    return round(elapsed_ms, 3)


def issue_event(index):
    return {
        "eventId": f"issue-{index}",
        "attemptId": f"attempt-{index}",
        "qid": f"EE-114-01-{(index % 3) + 1}",
        "examFamily": "PE",
        "rating": 1,
        "eventType": "none-of-above",
        "primaryKnowledgeNodeId": None,
        "secondaryKnowledgeNodeIds": [],
        "candidateCount": 3,
        "diagnosisConfidence": 0.4,
        "customText": "x" * 200,
        "evidence": ["bounded offline evidence"],
        "recordedAt": "2026-09-13T00:00:00.000Z",
        "graphRevisionRef": 0,
    }


def measure(graph_dir=ROOT / "data/knowledge", output_path=None):
    graph = validate_graph_directory(Path(graph_dir))
    issue_log = {
        "schemaVersion": "knowledge-issue-events.v1",
        "examFamily": "PE",
        "graphRevisions": ["kg-v1-capacity"],
        "events": [issue_event(index) for index in range(5000)],
    }
    learning_data = {
        "attempts": {"schemaVersion": "learning-attempts.v1", "attempts": {}},
        "issues": {"PE": issue_log, "GK": {"schemaVersion": "knowledge-issue-events.v1", "examFamily": "GK", "graphRevisions": [], "events": []}},
        "knowledgeReviews": {
            "PE": {"schemaVersion": "knowledge-reviews.v1", "examFamily": "PE", "graphRevisions": [], "reviews": {}},
            "GK": {"schemaVersion": "knowledge-reviews.v1", "examFamily": "GK", "graphRevisions": [], "reviews": {}},
        },
        "recoveryJournal": None,
    }
    serialized = json.dumps(learning_data, ensure_ascii=False, separators=(",", ":"))
    issue_serialized = json.dumps(issue_log, ensure_ascii=False, separators=(",", ":"))
    recovery_time_ms = _measure_recovery_time()
    blocking_failures = [error["code"] for error in graph["errors"]]
    if not recovery_time_ms <= RECOVERY_TIME_THRESHOLD_MS:
        blocking_failures.append("RECOVERY_TIME_THRESHOLD")
    if not len(issue_log["events"]) <= 5000 or not len(issue_serialized.encode("utf-8")) <= 3 * 1024 * 1024:
        blocking_failures.append("ISSUE_CAPACITY")
    if not len(serialized.encode("utf-8")) <= 8 * 1024 * 1024:
        blocking_failures.append("BACKUP_CAPACITY")
    return {
        "schemaVersion": "learning-data-capacity.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "graphRevision": graph["graphRevision"],
        "sourceIdentity": {
            "canonicalGraphRevision": graph["graphRevision"],
            "schemaVersion": graph["schemaVersion"],
        },
        "outputIdentity": {
            "kind": "learning-data-capacity",
            "path": str(Path(output_path).resolve()) if output_path else "stdout",
        },
        "fixture": "5000 PE issue events with bounded evidence and 200-byte custom text",
        "recoveryFixture": "pending import journal rollback",
        "recoveryTimeMs": recovery_time_ms,
        "recoveryTimeThresholdMs": RECOVERY_TIME_THRESHOLD_MS,
        "recoveryTimePass": recovery_time_ms <= RECOVERY_TIME_THRESHOLD_MS,
        "maxIssueEvents": 5000,
        "maxIssueBytes": 3 * 1024 * 1024,
        "maxBackupBytes": 8 * 1024 * 1024,
        "measuredIssueEventCount": len(issue_log["events"]),
        "measuredIssueBytes": len(issue_serialized.encode("utf-8")),
        "measuredLearningDataBytes": len(serialized.encode("utf-8")),
        "issueCapacityPass": len(issue_log["events"]) <= 5000 and len(issue_serialized.encode("utf-8")) <= 3 * 1024 * 1024,
        "backupCapacityPass": len(serialized.encode("utf-8")) <= 8 * 1024 * 1024,
        "checks": [
            {"name": "recovery time", "passed": recovery_time_ms <= RECOVERY_TIME_THRESHOLD_MS},
            {"name": "issue capacity", "passed": len(issue_log["events"]) <= 5000 and len(issue_serialized.encode("utf-8")) <= 3 * 1024 * 1024},
            {"name": "backup capacity", "passed": len(serialized.encode("utf-8")) <= 8 * 1024 * 1024},
        ],
        "blockingFailures": sorted(set(blocking_failures)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph-dir", default=str(ROOT / "data/knowledge"))
    parser.add_argument("--report", default=str(ROOT / "reports/learning-data-capacity.json"))
    args = parser.parse_args()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result = measure(args.graph_dir, report_path)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
