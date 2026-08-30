# -*- coding: utf-8 -*-
"""Regression locks for the source-reconstructed PE questions."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "📝 個人題解與錯題本"


class TestReconstructedPESolutions(unittest.TestCase):
    def test_verified_notes_do_not_claim_pending_manual_review(self):
        """A verified answer must not contain its own unresolved-review warning."""
        warning_phrases = (
            "尚未完成獨立逐步重算",
            "needs_manual_review",
            "人工複核",
            "待人工",
            "資料不足",
            "無法確認",
        )
        for path in CANONICAL.glob("*/canonical/EE-*.md"):
            text = path.read_text(encoding="utf-8")
            status = re.search(r"^audit_status:\s*(\S+)\s*$", text, re.M)
            if status and status.group(1) == "verified":
                hits = [phrase for phrase in warning_phrases if phrase in text]
                self.assertFalse(hits, f"verified note contains unresolved warning {hits}: {path.name}")

    def test_every_pe_qid_has_one_canonical_note_and_crop(self):
        """Question-level provenance must stay complete after regeneration."""
        dashboard = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        records = json.loads(re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", dashboard, re.S).group(1))
        expected = {row[0] for row in records}
        found = {}
        for path in CANONICAL.glob("*/canonical/EE-*.md"):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^qid:\s*(\S+)\s*$", text, re.M)
            if not match:
                continue
            qid = match.group(1)
            self.assertNotIn(qid, found, f"duplicate canonical note: {qid}")
            found[qid] = path
            crop = re.search(r"^source_crop:\s*(\S+)\s*$", text, re.M)
            self.assertIsNotNone(crop, f"missing source_crop: {qid}")
            self.assertTrue((ROOT / crop.group(1)).is_file(), f"invalid source_crop: {qid}")
            self.assertNotRegex(text, r"_p[12]\\.png", f"whole-page embed remains: {qid}")
        self.assertEqual(found.keys(), expected)

    def test_109_electronics_has_four_independent_question_records(self):
        dashboard = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        records = json.loads(re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", dashboard, re.S).group(1))
        qids = [row[0] for row in records if row[0].startswith("EE-109-02-")]
        self.assertEqual(qids, ["EE-109-02-1", "EE-109-02-2", "EE-109-02-3", "EE-109-02-4"])
        self.assertEqual(records[[row[0] for row in records].index("EE-109-02-1")][5], ["BJT 偏壓", "電子學"])
        self.assertIn("Boost 轉換器", records[[row[0] for row in records].index("EE-109-02-2")][5])
        self.assertIn("MOSFET 偏壓", records[[row[0] for row in records].index("EE-109-02-4")][5])

    def test_112_math_reconstruction_keeps_official_counts_and_free_parameters(self):
        q6 = (CANONICAL / "03_工程數學" / "canonical" / "EE-112-03-6.md").read_text(encoding="utf-8")
        self.assertIn("x=(1-3t-2s,\\ t,\\ 6-4s,\\ s)^T", q6)
        self.assertIn("t,s\\in\\mathbb R", q6)
        q3 = (CANONICAL / "03_工程數學" / "canonical" / "EE-112-03-3.md").read_text(encoding="utf-8")
        self.assertIn("(1-p_A)^{50}", q3)
        self.assertIn("(1-p_B)^{53}", q3)
        self.assertIn("(1-p_C)^{60}", q3)


if __name__ == "__main__":
    unittest.main()
