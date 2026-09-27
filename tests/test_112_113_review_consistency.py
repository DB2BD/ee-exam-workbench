"""Cross-check source, canonical, and compiled review data for EE-112/113."""

import json
import re
import unittest
from pathlib import Path

from scripts.question_schema import load_questions_from_bundle, question_record_view


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "📝 個人題解與錯題本" / "06_工業配電" / "canonical"
Q112_FORMULA = re.compile(
    r"T_s\s*=\s*\\d?frac\s*\{\s*k\s*\\times\s*80\s*\}"
    r"\s*\{\s*\(I/I_s\)\^2\s*-\s*1\s*\}\s*"
    r"\\times\s*\\d?frac\s*\{\s*1\s*\}\s*\{\s*0\.808\s*\}"
)
Q112_WRONG_FORMULA = re.compile(
    r"T_s\s*=\s*\\d?frac\s*\{\s*k\s*\\times\s*80\s*\}"
    r"\s*\{\s*\(I/I_s\)\^2\s*-\s*1\s*\}\s*(?:\\times|×)\s*0\.808"
)


def year_question_four(text, year):
    year_heading = re.search(rf"(?m)^##[ \t]*{year}[ \t]*年", text)
    if not year_heading:
        raise AssertionError(f"missing {year} year section")
    tail = text[year_heading.end():]
    next_year = re.search(r"(?m)^##[ \t]*\d{3}[ \t]*年", tail)
    year_section = tail[:next_year.start()] if next_year else tail
    question = re.search(
        r"(?ms)^####[ \t]*四、.*?(?=^####[ \t]|^##[ \t]|\Z)",
        year_section,
    )
    if not question:
        raise AssertionError(f"missing question four in {year} year section")
    return question.group(0)


def frontmatter(text):
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s|$)", text, re.DOTALL)
    if not match:
        raise AssertionError("canonical note has no YAML frontmatter")
    return {
        key.strip(): value.strip().strip("'\"")
        for line in match.group(1).splitlines()
        if ":" in line
        for key, value in (line.split(":", 1),)
    }


class Test112113ReviewConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "依考科分類" / "06_工業配電.md").read_text(encoding="utf-8")
        cls.anthology = (
            ROOT / "依考科分類" / "06_工業配電"
            / "06_工業配電_歷屆試題彙編_104-114年.md"
        ).read_text(encoding="utf-8")
        cls.audit_entries = {
            item["qid"]: item
            for item in json.loads(
                (ROOT / "data" / "pe-solution-audit.json").read_text(encoding="utf-8")
            )["entries"]
        }
        cls.questions = {
            view["id"]: view
            for view in (
                question_record_view(row, "PE")
                for row in load_questions_from_bundle(ROOT / "dashboard-data.js")
            )
        }
        bundle = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        metadata_match = re.search(r"const SOLUTION_REVIEW_METADATA\s*=\s*", bundle)
        if not metadata_match:
            raise AssertionError("dashboard is missing SOLUTION_REVIEW_METADATA")
        cls.review_metadata, _ = json.JSONDecoder().raw_decode(bundle[metadata_match.end():])

    def test_112_relay_formula_stays_aligned_across_question_sources(self):
        note = (CANONICAL / "EE-112-06-4.md").read_text(encoding="utf-8")
        canonical_stem = note.split("## 官方題目", 1)[1].split("## 考場標準作答", 1)[0]
        compiled_stem = self.questions["EE-112-06-4"]["stem"]
        stems = {
            "official subject source": year_question_four(self.source, 112),
            "question anthology": year_question_four(self.anthology, 112),
            "canonical question": canonical_stem,
            "compiled dashboard stem": compiled_stem,
        }
        for label, stem in stems.items():
            with self.subTest(source=label):
                self.assertRegex(stem, Q112_FORMULA)
                self.assertNotRegex(stem, Q112_WRONG_FORMULA)

        self.assertIn(r"\left(\frac{I}{I_s}\right)^2-1=159.3321923", note)
        self.assertIn(r"\boxed{0.48}", note)

    def test_113_manual_review_status_values_and_dashboard_metadata_stay_aligned(self):
        note = (CANONICAL / "EE-113-06-4.md").read_text(encoding="utf-8")
        fields = frontmatter(note)
        expected_status = "needs_manual_review"
        self.assertEqual(fields.get("audit_status"), expected_status)
        self.assertEqual(fields.get("status"), expected_status)
        self.assertEqual(fields.get("verified_at"), "null")

        audit = self.audit_entries["EE-113-06-4"]
        self.assertEqual(audit["audit_status"], expected_status)
        self.assertIsNone(audit["verified_at"])
        self.assertEqual(self.questions["EE-113-06-4"]["solutionStatus"], expected_status)

        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        for exact_value_and_unit in (
            r"15.475381\,\mathrm{MVA}",
            r"18.613991\,\mathrm{kA}",
            r"17.475381\,\mathrm{MVA}",
            r"21.019617\,\mathrm{kA}",
        ):
            with self.subTest(value=exact_value_and_unit):
                self.assertIn(exact_value_and_unit, standard)

        review = self.review_metadata["EE-113-06-4"]
        for dashboard_key, canonical_key in (
            ("disposition", "review_disposition"),
            ("blocker", "review_blocker"),
            ("action", "review_action"),
            ("evidence", "review_evidence"),
            ("officialSourceUrl", "official_source_url"),
        ):
            with self.subTest(review_field=canonical_key):
                self.assertEqual(review.get(dashboard_key), fields.get(canonical_key))

    def test_113_supplemental_research_reference_is_local_and_not_a_dead_workbench_link(self):
        report = ROOT / "reports" / "113年工業配電Q4啟斷容量口徑研究.md"
        canonical = (CANONICAL / "EE-113-06-4.md").read_text(encoding="utf-8")
        annual = (
            ROOT / "📝 個人題解與錯題本" / "06_工業配電"
            / "113年_工業配電_全卷完整詳細題解.md"
        ).read_text(encoding="utf-8")
        self.assertTrue(report.is_file())
        for note in (canonical, annual):
            self.assertIn("reports/113年工業配電Q4啟斷容量口徑研究.md", note)
            self.assertIn("尚未加入 Pages 靜態套件", note)
            self.assertNotRegex(note, r"\[[^\]]+\]\([^)]*113年工業配電Q4啟斷容量口徑研究\.md\)")


if __name__ == "__main__":
    unittest.main()
