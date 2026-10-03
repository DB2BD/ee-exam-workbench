# -*- coding: utf-8 -*-
"""K1 answer-correction data layer tests."""

import json
import re
import unittest
from pathlib import Path

from scripts import build_answer_corrections as bac

ROOT = Path(__file__).resolve().parent.parent


class TestAnswerCorrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.warnings = bac.build()
        cls.by_qid = {c["qid"]: c for c in cls.doc["corrections"]}

    def test_generated_files_fresh(self):
        on_disk = json.loads((ROOT / "data/answer-corrections.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.doc)
        js = (ROOT / "src/data/answerCorrections.generated.js").read_text(encoding="utf-8")
        self.assertEqual(js, bac.render_js(self.doc))

    def test_counts(self):
        wave1_rows = bac.parse_report(ROOT / "reports/題解精確化_wave-1.md")[2]
        wave2_rows = bac.parse_report(ROOT / "reports/題解精確化_wave-2.md")[2]
        self.assertEqual(len(wave1_rows), 9)
        self.assertEqual(len(wave2_rows), 18)  # table: 17 new + 1 Wave 1 carryover
        unique = {r["qid"] for r in wave1_rows + wave2_rows}
        self.assertEqual(len(unique), 26)
        self.assertEqual(len(self.doc["corrections"]), 26)
        self.assertEqual(len(self.by_qid), 26)

    def test_spot_checks(self):
        self.assertIn("612.5", self.by_qid["EE-112-01-2"]["new_answer"])
        self.assertIn("2.011", self.by_qid["EE-114-04-1"]["new_answer"])
        self.assertIn("EE-111-03-1", self.by_qid)
        self.assertEqual(self.by_qid["EE-111-03-4"]["old_answer"], "奇異值 √(2±√2)")
        self.assertEqual(self.by_qid["EE-112-01-2"]["decided_at"], "2026-10-02")
        c = self.by_qid["EE-114-02-3"]
        self.assertEqual(c["decided_at"], "2026-10-03")
        self.assertIn("−15.025", c["old_answer"])

    def test_schema_and_order(self):
        keys = {"qid", "wave", "old_answer", "new_answer", "reason", "decided_at"}
        for c in self.doc["corrections"]:
            self.assertEqual(set(c), keys)
            self.assertRegex(c["qid"], r"^EE-\d{3}-\d{2}-\d+$")
            self.assertRegex(c["decided_at"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(c["new_answer"])
        order = [bac.sort_key(c["qid"]) for c in self.doc["corrections"]]
        self.assertEqual(order, sorted(order))

    def test_qids_exist_in_dashboard(self):
        known = bac.dashboard_qids()
        for q in self.by_qid:
            self.assertIn(q, known)

    def test_unreported_not_emitted(self):
        for q in self.doc["unreported"]:
            self.assertNotIn(q, self.by_qid)
        js = (ROOT / "src/data/answerCorrections.generated.js").read_text(encoding="utf-8")
        self.assertTrue(re.search(r"const ANSWER_CORRECTIONS = \{", js))


if __name__ == "__main__":
    unittest.main()
