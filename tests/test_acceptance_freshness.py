# -*- coding: utf-8 -*-
"""Acceptance report freshness contract tests."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.acceptance_freshness import validate_report_freshness
from scripts.run_change_acceptance import build_acceptance_report


class TestAcceptanceFreshness(unittest.TestCase):
    def _report(self, revision="kg-v1-current"):
        return {
            "schemaVersion": "test-report.v1",
            "generatedAt": "2026-09-13T10:00:00.000Z",
            "graphRevision": revision,
            "sourceIdentity": {"canonicalGraphRevision": revision},
            "outputIdentity": {"kind": "test"},
            "checks": [],
            "blockingFailures": [],
        }

    def test_reports_with_one_current_revision_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = {}
            for name in ("canonical", "website", "obsidian"):
                path = root / f"{name}.json"
                path.write_text(json.dumps(self._report()), encoding="utf-8")
                paths[name] = path
            result = validate_report_freshness(paths, "kg-v1-current")
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["freshnessPass"], True)

    def test_stale_report_revision_blocks_freshness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = {}
            for name in ("canonical", "website", "obsidian"):
                report = self._report("kg-v1-old" if name == "obsidian" else "kg-v1-current")
                path = root / f"{name}.json"
                path.write_text(json.dumps(report), encoding="utf-8")
                paths[name] = path
            result = validate_report_freshness(paths, "kg-v1-current")
        self.assertFalse(result["valid"])
        self.assertIn("STALE_REPORT_REVISION", {error["code"] for error in result["errors"]})

    def test_acceptance_report_has_current_revision_identity(self):
        report = build_acceptance_report([], "kg-v1-current", "2026-09-13T10:00:00.000Z", Path("reports/acceptance.json"))
        self.assertEqual(report["change"], "problem-driven-obsidian-warning-remediation")
        self.assertEqual(report["graphRevision"], "kg-v1-current")
        self.assertEqual(report["sourceIdentity"]["canonicalGraphRevision"], "kg-v1-current")
        self.assertEqual(report["outputIdentity"]["kind"], "acceptance-report")
        self.assertEqual(report["generatedAt"], "2026-09-13T10:00:00.000Z")

    def test_missing_report_contract_fields_block_freshness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "incomplete.json"
            incomplete = self._report()
            incomplete.pop("schemaVersion")
            incomplete.pop("checks")
            incomplete.pop("blockingFailures")
            path.write_text(json.dumps(incomplete), encoding="utf-8")
            result = validate_report_freshness({"incomplete": path}, "kg-v1-current")
        self.assertFalse(result["valid"])
        self.assertIn("REPORT_SCHEMA_VERSION", {error["code"] for error in result["errors"]})
        self.assertIn("REPORT_CHECKS", {error["code"] for error in result["errors"]})
        self.assertIn("REPORT_BLOCKING_FAILURES", {error["code"] for error in result["errors"]})

    def test_acceptance_report_exposes_structured_capacity_gate(self):
        capacity = {
            "recoveryTimeMs": 42,
            "recoveryTimeThresholdMs": 250,
            "recoveryTimePass": True,
            "measuredIssueEventCount": 5000,
            "measuredIssueBytes": 100,
            "measuredLearningDataBytes": 200,
            "issueCapacityPass": True,
            "backupCapacityPass": True,
        }
        report = build_acceptance_report(
            [], "kg-v1-current", "2026-09-13T10:00:00.000Z", Path("reports/acceptance.json"), capacity_report=capacity
        )
        self.assertEqual(report["recovery"]["recoveryTimeMs"], 42)
        self.assertEqual(report["recovery"]["recoveryTimeThresholdMs"], 250)
        self.assertTrue(report["recovery"]["recoveryTimePass"])
        self.assertEqual(report["capacity"]["measuredIssueEventCount"], 5000)

    def test_capacity_report_without_recovery_measurement_blocks_freshness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capacity.json"
            path.write_text(json.dumps(self._report()), encoding="utf-8")
            result = validate_report_freshness({"capacity": path}, "kg-v1-current")
        self.assertFalse(result["valid"])
        self.assertIn("RECOVERY_TIME_MISSING", {error["code"] for error in result["errors"]})

    def test_acceptance_entrypoint_supports_direct_script_execution(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_change_acceptance.py"
        completed = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=script.parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--report", completed.stdout)


if __name__ == "__main__":
    unittest.main()
