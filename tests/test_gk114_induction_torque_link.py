"""Official induction-motor question stays on the same-topic PE bridge."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_national_exams import build_cross_references
from question_schema import load_questions_from_bundle, question_record_view


class TestGK114InductionTorqueLink(unittest.TestCase):
    def test_public_record_links_to_induction_motor_starting_torque(self):
        rows = load_questions_from_bundle(ROOT / "national-exams-data.js")
        record = next(row for row in rows if row[0] == "GK-114-04-4")
        self.assertEqual(question_record_view(record, "GK")["relatedPEId"], "EE-105-04-3")

    def test_compiler_corrects_the_character_overlap_to_a_same_topic_bridge(self):
        rows = load_questions_from_bundle(ROOT / "national-exams-data.js")
        record = next(row for row in rows if row[0] == "GK-114-04-4")
        record[13] = "EE-114-04-5"

        build_cross_references([record], pe_data_path=str(ROOT / "dashboard-data.js"))

        self.assertEqual(record[13], "EE-105-04-3")

    def test_scoped_baseline_preserves_all_other_existing_bridges(self):
        rows = [list(row) for row in load_questions_from_bundle(ROOT / "national-exams-data.js")]
        expected = {row[0]: row[13] for row in rows}
        target = next(row for row in rows if row[0] == "GK-114-04-4")
        target[13] = "EE-114-04-5"
        expected[target[0]] = "EE-105-04-3"

        build_cross_references(
            rows,
            pe_data_path=str(ROOT / "dashboard-data.js"),
            baseline_path=str(ROOT / "national-exams-data.js"),
        )

        self.assertEqual({row[0]: row[13] for row in rows}, expected)

    def test_scoped_baseline_rejects_a_bridge_to_another_subject(self):
        rows = load_questions_from_bundle(ROOT / "national-exams-data.js")
        record = list(next(row for row in rows if row[0] == "GK-114-04-3"))
        record[13] = "EE-114-03-1"

        with tempfile.TemporaryDirectory() as temp_dir:
            baseline = Path(temp_dir) / "baseline.js"
            baseline.write_text(
                "questions: " + json.dumps([record], ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "cross-subject"):
                build_cross_references(
                    [list(record)],
                    pe_data_path=str(ROOT / "dashboard-data.js"),
                    baseline_path=str(baseline),
                )

    def test_canonical_link_routes_to_gk_induction_motor_torque(self):
        links = json.loads((ROOT / "data/knowledge/question-links.json").read_text(encoding="utf-8"))["links"]
        self.assertEqual(links["GK:GK-114-04-4"]["nodeIds"], ["gk-emach-induction-motor-torque"])


if __name__ == "__main__":
    unittest.main()
