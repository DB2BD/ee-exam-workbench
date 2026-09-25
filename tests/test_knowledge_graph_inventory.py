# -*- coding: utf-8 -*-
"""Tests for the measured legacy knowledge-graph inventory."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.knowledge_graph_inventory import collect_inventory, write_inventory


ROOT = Path(__file__).resolve().parents[1]


class TestKnowledgeGraphInventory(unittest.TestCase):
    def test_inventory_records_measured_legacy_sources(self):
        inventory = collect_inventory(ROOT)

        self.assertEqual(inventory["legacyDag"]["nodeCount"], 71)
        self.assertEqual(inventory["obsidian"]["coreNoteCount"], 14)
        self.assertEqual(inventory["questions"]["PE"]["recordCount"], 323)
        self.assertEqual(inventory["questions"]["GK"]["recordCount"], 161)
        self.assertGreater(inventory["mapping"]["ruleCount"], 0)
        self.assertIn("EE_EXAM_ATTEMPT_RECOVERY_V1", inventory["backup"]["storageKeys"])
        self.assertIn("EE_EXAM_SM2_SCHEDULE_V1", inventory["backup"]["storageKeys"])

    def test_inventory_and_report_are_written_with_source_metadata(self):
        inventory = collect_inventory(ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            json_path, report_path = write_inventory(inventory, output_dir)

            saved = json.loads(json_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")

        self.assertEqual(saved["schemaVersion"], "knowledge-graph-inventory.v1")
        self.assertEqual(saved["workspace"], str(ROOT))
        self.assertIn("**71**", report)
        self.assertIn("14", report)
        self.assertIn("EE_EXAM_ATTEMPT_RECOVERY_V1", report)
        self.assertIn("Source paths", report)


if __name__ == "__main__":
    unittest.main()
