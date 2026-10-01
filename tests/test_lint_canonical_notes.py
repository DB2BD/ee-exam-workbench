"""Contract tests for the canonical-note precision/redundancy linter."""

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
source_crop: 依考科分類/05_電力系統/images/questions/PE_999年_電力系統_Q01.png
---
"""

LEAN_BODY = r"""
# 999 年電力系統第 1 題｜經濟調度

![官方題目裁切圖](../../../依考科分類/05_電力系統/images/questions/PE_999年_電力系統_Q01.png)

## 已知與所求

\(C_1, C_2\)；需求 550 MW。

## 解答

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

    def test_unmigrated_note_only_gets_universal_checks(self):
        front = FRONT.replace("template: lean-v1\n", "")
        body = LEAN_BODY + "\n## 完整教學推導\n"
        self.assertEqual(self.run_lint(body, front=front), [])


if __name__ == "__main__":
    unittest.main()
