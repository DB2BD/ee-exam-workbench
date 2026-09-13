# -*- coding: utf-8 -*-
"""Validate that generated reports describe the same canonical graph revision."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    from scripts.knowledge_graph import validate_graph_directory
except ModuleNotFoundError:
    from knowledge_graph import validate_graph_directory


def _error(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _latest_source_mtime(source_dir: Path) -> float | None:
    mtimes = [path.stat().st_mtime for path in source_dir.rglob("*") if path.is_file()]
    return max(mtimes) if mtimes else None


def validate_report_freshness(
    report_paths: Mapping[str, Path | str],
    current_graph_revision: str,
    *,
    source_modified_at: float | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    checked: list[str] = []
    for name, raw_path in sorted(report_paths.items()):
        path = Path(raw_path)
        checked.append(name)
        if not path.exists():
            _error(errors, "MISSING_REPORT", str(path), f"{name} report does not exist")
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _error(errors, "INVALID_REPORT", str(path), str(exc))
            continue
        if not isinstance(report, Mapping):
            _error(errors, "INVALID_REPORT", str(path), "report must be an object")
            continue
        generated_at = _timestamp(report.get("generatedAt"))
        if generated_at is None:
            _error(errors, "REPORT_GENERATED_AT", f"{path}.generatedAt", "generatedAt must be an ISO timestamp")
        elif source_modified_at is not None and generated_at.timestamp() < source_modified_at:
            _error(errors, "REPORT_BEFORE_SOURCE", f"{path}.generatedAt", "report was generated before the current source artifact")
        if not isinstance(report.get("schemaVersion"), str) or not report.get("schemaVersion"):
            _error(errors, "REPORT_SCHEMA_VERSION", f"{path}.schemaVersion", "schemaVersion is required")
        if report.get("graphRevision") != current_graph_revision:
            _error(errors, "STALE_REPORT_REVISION", f"{path}.graphRevision", f"expected {current_graph_revision}")
        source = report.get("sourceIdentity")
        if not isinstance(source, Mapping) or source.get("canonicalGraphRevision") != current_graph_revision:
            _error(errors, "STALE_SOURCE_IDENTITY", f"{path}.sourceIdentity", "source identity must name the current canonical graph revision")
        if not isinstance(report.get("outputIdentity"), Mapping):
            _error(errors, "OUTPUT_IDENTITY", f"{path}.outputIdentity", "output identity is required")
        if not isinstance(report.get("checks"), list):
            _error(errors, "REPORT_CHECKS", f"{path}.checks", "checks must be a list")
        if not isinstance(report.get("blockingFailures"), list):
            _error(errors, "REPORT_BLOCKING_FAILURES", f"{path}.blockingFailures", "blockingFailures must be a list")
        if name == "capacity":
            for field in ("recoveryTimeMs", "recoveryTimeThresholdMs", "recoveryTimePass"):
                if field not in report:
                    _error(errors, "RECOVERY_TIME_MISSING", f"{path}.{field}", "capacity report must include measured recovery time and threshold result")
    errors.sort(key=lambda item: (item["code"], item["path"], item["message"]))
    return {
        "valid": not errors,
        "freshnessPass": not errors,
        "currentGraphRevision": current_graph_revision,
        "checkedReports": checked,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph-dir", type=Path, default=Path("data/knowledge"))
    parser.add_argument("--report", action="append", required=True, help="Report mapping in NAME=PATH form")
    args = parser.parse_args()
    report_paths: dict[str, Path] = {}
    for item in args.report:
        name, separator, path = item.partition("=")
        if not separator or not name or not path:
            parser.error("--report must use NAME=PATH")
        report_paths[name] = Path(path)
    graph = validate_graph_directory(args.graph_dir)
    result = validate_report_freshness(
        report_paths,
        graph["graphRevision"],
        source_modified_at=_latest_source_mtime(args.graph_dir),
    )
    result["graphValid"] = graph["valid"]
    if not graph["valid"]:
        result["valid"] = False
        result["freshnessPass"] = False
        result["errors"].extend(graph["errors"])
        result["errors"].sort(key=lambda item: (item["code"], item["path"], item["message"]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
