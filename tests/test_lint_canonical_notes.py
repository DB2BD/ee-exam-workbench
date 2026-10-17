"""Contract tests for the canonical-note precision/redundancy linter."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import lint_canonical_notes as lint  # noqa: E402


FRONT = """---
qid: EE-999-05-1
year: 999
subject: 電力系統
template: lean-v1
audit_status: verified
verified_at: 2026-10-01
method: test
source_crop: 01_原始試題/依考科/05_電力系統/images/questions/PE_999年_電力系統_Q01.png
---
"""

LEAN_BODY = r"""
# 999 年電力系統第 1 題｜經濟調度

![官方題目裁切圖](../../../01_原始試題/依考科/05_電力系統/images/questions/PE_999年_電力系統_Q01.png)

## 已知與所求

\(C_1, C_2\)；需求 550 MW。

## 考場標準作答

### （一）

\[
\boxed{P_1=250\ \mathrm{MW}}
\]

### （二）

\[
\boxed{\lambda=8}
\]

## 驗算

\(6+0.008(250)=8\)。

## 失分點

- 本題二次項微分漏乘 2。
"""


class LintCanonicalNotesTests(unittest.TestCase):
    def run_lint(self, body, stem="（一）求 P。（二）求 λ。", front=FRONT):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EE-999-05-1.md"
            path.write_text(front + body, encoding="utf-8")
            return lint.lint(path, stem)["errors"]

    def test_clean_lean_note_passes(self):
        self.assertEqual(self.run_lint(LEAN_BODY), [])

    def test_lost_backslash_and_lost_delimiters_are_errors(self):
        errors = self.run_lint(LEAN_BODY + "\n半徑 (1,ldots,10)，電阻 (2\\,\\Omega)。\n")
        self.assertIn("broken-latex:ldots", errors)
        self.assertTrue(any(error.startswith("latex-outside-math") for error in errors))

    def test_row_spacing_is_not_an_unbalanced_display(self):
        body = LEAN_BODY + "\n\\[\n\\begin{bmatrix}1\\\\[4pt]2\\end{bmatrix}\n\\]\n"
        self.assertFalse(any(error.startswith("unbalanced") for error in self.run_lint(body)))

    def test_each_subitem_needs_a_boxed_answer(self):
        body = LEAN_BODY.replace(r"\boxed{\lambda=8}", r"\lambda=8")
        self.assertIn("boxed-coverage:1<2", self.run_lint(body))

    def test_redundant_sections_history_and_repeated_answers_are_errors(self):
        body = LEAN_BODY + "\n## 完整教學推導\n\n狀態升級為 verified。\\(\\boxed{P_1=250\\ \\mathrm{MW}}\\)\n"
        errors = self.run_lint(body)
        self.assertIn("section-not-allowed:完整教學推導", errors)
        self.assertTrue(any(error.startswith("meta-history") for error in errors))
        self.assertTrue(any(error.startswith("boxed-duplicate") for error in errors))

    def test_manual_review_note_requires_condition_section(self):
        front = FRONT.replace("audit_status: verified", "audit_status: needs_manual_review")
        self.assertIn("section-missing:條件與疑義", self.run_lint(LEAN_BODY, front=front))

    def test_trap_list_is_capped(self):
        body = LEAN_BODY + "- 二\n- 三\n- 四\n"
        self.assertIn("too-many-traps>3", self.run_lint(body))

    def test_compact_short_question_may_omit_givens_and_traps(self):
        front = FRONT.replace("template: lean-v1\n", "template: lean-v1\ncompact: true\n")
        body = re.sub(r"## 已知與所求.*?(?=## 考場標準作答)", "", LEAN_BODY, flags=re.S)
        body = body.split("## 失分點")[0]
        self.assertEqual(self.run_lint(body, stem="（一）求 P。（二）求 λ。（10 分）", front=front), [])
        long_stem = "（一）求 P。（二）求 λ。（20 分）"
        self.assertEqual(self.run_lint(body, stem=long_stem, front=front), [])  # still short body
        padded = body + "\n" + "說明。" * 400
        self.assertIn("compact-not-allowed:20分", self.run_lint(padded, stem=long_stem, front=front))

    def test_total_points_reads_shared_marks(self):
        self.assertEqual(lint.total_points("（每小題 10 分，共 20 分）"), 20)
        self.assertEqual(lint.total_points("（一）…（5 分）（二）…（15 分）"), 20)
        self.assertEqual(lint.total_points("求 E[A]。(10分)"), 10)

    def test_unmigrated_note_only_gets_universal_checks(self):
        front = FRONT.replace("template: lean-v1\n", "")
        body = LEAN_BODY + "\n## 完整教學推導\n"
        self.assertEqual(self.run_lint(body, front=front), [])


LOGIC_BODY = LEAN_BODY.replace(
    "## 考場標準作答\n",
    "## 考場標準作答\n\n**解題邏輯**：等增量成本加功率平衡，先求 \\(P_1\\) 再求 \\(\\lambda\\)。\n",
).replace(
    "### （一）\n", "### （一）出力（10 分）\n\n**邏輯**：等增量成本法。\n"
).replace(
    "### （二）\n", "### （二）增量成本（10 分）\n\n**邏輯**：代回任一機組。\n"
)


class RequireLogicTests(unittest.TestCase):
    def run_lint(self, body, stem="（一）求 P。（二）求 λ。", front=FRONT, require=True):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EE-999-05-1.md"
            path.write_text(front + body, encoding="utf-8")
            return lint.lint(path, stem, require)["errors"]

    def test_default_is_off_so_legacy_notes_still_pass(self):
        self.assertFalse(lint.REQUIRE_LOGIC_DEFAULT)
        self.assertEqual(self.run_lint(LEAN_BODY, require=False), [])

    def test_complete_logic_note_passes(self):
        self.assertEqual(self.run_lint(LOGIC_BODY), [])

    def test_missing_overall_logic_is_an_error(self):
        body = LOGIC_BODY.replace("**解題邏輯**：", "")
        self.assertIn("no-logic:解題邏輯", self.run_lint(body))

    def test_overall_logic_must_precede_first_subheading(self):
        body = LOGIC_BODY.replace("**解題邏輯**：", "").replace("## 驗算", "**解題邏輯**：太晚。\n\n## 驗算")
        self.assertIn("no-logic:解題邏輯", self.run_lint(body))

    def test_scored_subquestion_needs_its_own_logic_line(self):
        body = LOGIC_BODY.replace("**邏輯**：代回任一機組。", "")
        errors = self.run_lint(body)
        self.assertIn("no-logic:（二）", errors)
        self.assertNotIn("no-logic:（一）", errors)

    def test_unscored_headings_do_not_need_logic(self):
        self.assertEqual(self.run_lint(LOGIC_BODY.replace("（10 分）", "")), [])

    def test_legacy_note_fails_with_both_codes(self):
        errors = self.run_lint(LEAN_BODY.replace("### （一）", "### （一）出力（10 分）"))
        self.assertIn("no-logic:解題邏輯", errors)
        self.assertIn("no-logic:（一）", errors)

    def test_compact_limit_is_five_marks_and_ignores_length(self):
        front = FRONT.replace("template: lean-v1\n", "template: lean-v1\ncompact: true\n")
        body = re.sub(r"## 已知與所求.*?(?=## 考場標準作答)", "", LEAN_BODY, flags=re.S).split("## 失分點")[0]
        self.assertEqual(self.run_lint(body, stem="求 P。（5 分）", front=front), [])
        self.assertIn("compact-not-allowed:6分", self.run_lint(body, stem="求 P。（6 分）", front=front))
        # Without the flag the legacy 700-character rule still governs.
        self.assertEqual(self.run_lint(body, stem="求 P。（6 分）", front=front, require=False), [])


if __name__ == "__main__":
    unittest.main()
