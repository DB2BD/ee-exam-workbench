"""Keep the Norton source arrow distinct from the external short-circuit current."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "📝 個人題解與錯題本/01_電路學/canonical/EE-114-01-2.md"
SPEC = ROOT / "data/circuit_specs/EE-114-01-2-norton.json"
REPORT = ROOT / "reports/EE-114-01-2-norton-diagram.json"


class TestNortonDirection114(unittest.TestCase):
    def test_unreviewed_draft_is_not_in_the_release_image_inventory(self):
        draft_name = "114年_電路學_第2題_諾頓等效電路.svg"
        self.assertFalse((ROOT / "依考科分類/01_電路學/images" / draft_name).exists())
        bundle = (ROOT / "solutions-bundle.js").read_text(encoding="utf-8")
        self.assertNotIn(draft_name, bundle)

    def test_score_answer_distinguishes_source_and_short_directions(self):
        note = NOTE.read_text(encoding="utf-8")
        self.assertIn(r"I_{sc}=10\ \mathrm A", note)
        self.assertIn(r"V_{ab}=+10\,\mathrm V", note)
        self.assertIn(r"b\to a", note)
        self.assertIn(r"a\to b", note)
        self.assertIn("**並聯**", note)

    def test_draft_equivalent_spec_has_two_parallel_branches(self):
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["valid"])
        self.assertEqual(report["warnings"], [])
        branches = {part["ref"]: part for part in spec["components"] if part["type"] in {"current-source", "resistor"}}
        self.assertEqual(set(branches), {"IN", "RN"})
        for part in branches.values():
            self.assertEqual(part["pins"], {"1": "b", "2": "a"})
        self.assertEqual(branches["IN"]["arrow"], "1->2")
        source_amperes = float(re.search(r"= ([\d.]+) A", branches["IN"]["label"]).group(1))
        resistor_ohms = float(re.search(r"= ([\d.]+) Ω", branches["RN"]["label"]).group(1))
        self.assertEqual(source_amperes * resistor_ohms, 10.0)  # V_ab at open circuit


if __name__ == "__main__":
    unittest.main()
