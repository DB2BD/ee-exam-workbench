"""Regression coverage for official engineering-math question alignment.

These checks protect against the failure mode where a canonical derivation is
mathematically sound but attached to another year's question number.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "📝 個人題解與錯題本" / "03_工程數學" / "canonical"


def dashboard_questions():
    text = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
    match = re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", text, re.S)
    return {row[0]: row for row in json.loads(match.group(1))}


class TestEngineeringMathOfficialAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = dashboard_questions()

    def assert_stem_and_note(self, qid, stem_markers, note_markers):
        self.assertIn(qid, self.questions)
        stem = self.questions[qid][4]
        note = (CANONICAL / f"{qid}.md").read_text(encoding="utf-8")
        for marker in stem_markers:
            self.assertIn(marker, stem, qid)
        for marker in note_markers:
            self.assertIn(marker, note, qid)

    def test_question_counts_include_official_108_q6_and_110_q7(self):
        math = [row for row in self.questions.values() if row[1] == "03"]
        self.assertEqual(len(math), 67)
        self.assertEqual(
            sum(row[2] == 108 for row in math),
            6,
        )
        self.assertEqual(
            sum(row[2] == 110 for row in math),
            7,
        )

    def test_104_official_question_forms(self):
        self.assert_stem_and_note(
            "EE-104-03-3",
            ["3x+2", "x(x-4)(x^2+9)"],
            ["needs_manual_review", "-\\frac{14\\pi}{225}", "普通廣義積分不存在"],
        )
        self.assert_stem_and_note(
            "EE-104-03-4",
            ["y+\\frac32"],
            ["\\frac23", "\\frac{13}{24}", "\\frac{13}{36}"],
        )
        note_104_q4 = (CANONICAL / "EE-104-03-4.md").read_text(encoding="utf-8")
        self.assertNotIn("\\boxed{\\frac38}", note_104_q4)
        self.assert_stem_and_note(
            "EE-104-03-5",
            ["\\cos(yz)", "xyz"],
            ["\\frac32", "因 \\(dy=0\\)"],
        )

    def test_108_official_question_forms(self):
        self.assert_stem_and_note(
            "EE-108-03-3",
            ["溫度函數", "3\\mathbf i-4\\mathbf k"],
            ["\\boxed{-\\frac25}", "梯度"],
        )
        self.assert_stem_and_note(
            "EE-108-03-5",
            ["1/(z²−1)", "圓心 (±1,0)"],
            ["\\boxed{I_1=2\\pi i", "\\boxed{I_2=2\\pi i\\left(-\\frac12\\right)=-\\pi i}"],
        )
        self.assert_stem_and_note(
            "EE-108-03-6",
            ["E[X(X-4)]"],
            ["\\boxed{E[X^2]=13}", "\\operatorname{Var}(-4X+10)=(-4)^2\\operatorname{Var}(X)=144"],
        )

    def test_109_and_110_official_question_forms(self):
        self.assert_stem_and_note(
            "EE-109-03-3",
            ["P(X>Y)"],
            ["\\boxed{P(X>Y)=0.7}"],
        )
        self.assert_stem_and_note(
            "EE-109-03-4",
            ["\\frac{x}{\\pi}", "傅立葉級數"],
            ["\\frac{2(-1)^{n+1}}{\\pi n}"],
        )
        self.assert_stem_and_note(
            "EE-110-03-1",
            ["f(t) = 2t^2", "e^{-\\tau}"],
            ["\\boxed{f(t)=2t^2+\\frac23t^3}"],
        )
        self.assert_stem_and_note(
            "EE-110-03-2",
            ["y'=y^2e^{-2x}"],
            ["\\boxed{y(x)=\\frac{1}{C+\\frac12e^{-2x}}}", "y\\equiv0"],
        )
        self.assert_stem_and_note(
            "EE-110-03-4",
            ["x=t^3", "e^z"],
            ["\\frac{111}{4}+e^4-e"],
        )
        self.assert_stem_and_note(
            "EE-110-03-5",
            ["x^2y-xy^2+xz^2", "(1,-1,1)"],
            ["\\boxed{-\\sqrt6}"],
        )
        self.assert_stem_and_note(
            "EE-110-03-7",
            ["p(x)=a(x+1)", "0\\le x\\le2"],
            ["\\frac{11}{36}"],
        )

    def test_113_q6_keeps_the_official_exponent_and_three_subproblems(self):
        self.assert_stem_and_note(
            "EE-113-03-6",
            ["e^{-x-y/2}", "邊際平均值", "E\\{X^3Y^2\\}"],
            ["\\boxed{k=\\frac12}", "\\boxed{E[Y]=2}", "\\boxed{48}"],
        )
        stem = self.questions["EE-113-03-6"][4]
        self.assertNotIn("e^{-x-2y}", stem)
        self.assertNotIn("邊際機率密度函數", stem)
        self.assertNotIn("P(0 \\le X \\le 1", stem)

    def test_113_q3_keeps_the_official_scaled_quartic_integral(self):
        self.assert_stem_and_note(
            "EE-113-03-3",
            ["\\frac{\\sqrt{2}}{1+16x^4}"],
            ["\\boxed{I=\\frac{\\sqrt2}{2}\\cdot\\frac{\\pi}{\\sqrt2}=\\frac\\pi2}"],
        )
        stem = self.questions["EE-113-03-3"][4]
        self.assertNotIn("\\frac{1}{x^4 + 16}", stem)

    def test_math_audit_tracks_the_manual_ambiguity(self):
        audit = json.loads((ROOT / "data" / "engineering-math-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["summary"], {
            "questions": 67,
            "verified": 66,
            "suspected_error": 0,
            "needs_manual_review": 1,
            "not_attempted": 0,
        })
        entry = next(item for item in audit["entries"] if item["qid"] == "EE-104-03-3")
        self.assertEqual(entry["audit_status"], "needs_manual_review")
        self.assertIsNone(entry["verified_at"])
        self.assertTrue(entry["official_source_url"].startswith("https://wwwq.moex.gov.tw/"))


if __name__ == "__main__":
    unittest.main()
