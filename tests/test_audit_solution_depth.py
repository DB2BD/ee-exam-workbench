"""Contract tests for the v1.5.0 flags of scripts/audit_solution_depth.py."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import audit_solution_depth as audit  # noqa: E402

FRONT = "---\nqid: EE-999-05-1\nyear: 999\nsubject: 電力系統\ntemplate: lean-v1\n{extra}---\n"

GOOD = r"""
# t

## 已知與所求

電阻 \(R=12\ \Omega\)、電壓 \(V=240\ \mathrm{V}\)，求電流與功率。

## 考場標準作答

**解題邏輯**：先由歐姆定律求電流，再求功率。

### （一）電流（10 分）

**邏輯**：歐姆定律。

\[
I=\frac{V}{R}=\frac{240}{12}=20\ \mathrm{A}
\]
\[
\boxed{I=20\ \mathrm{A}}
\]

### （二）功率（10 分）

**邏輯**：功率等於電流平方乘電阻，電流取自（一）。

\[
P=I^2R=20^2\times12=400\times12=4800
\]
\[
\boxed{P=4800\ \mathrm{W}}
\]

## 驗算

略。
"""

STEM = "（一）求電流。（10 分）（二）求功率。（10 分）R=12 Ω，V=240 V。"


class AuditV150FlagTests(unittest.TestCase):
    def audit_text(self, body, stem=STEM, extra=""):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EE-999-05-1.md"
            path.write_text(FRONT.format(extra=extra) + body, encoding="utf-8")
            audit.ROOT, root = Path(tmp), audit.ROOT   # audit_note only uses ROOT for display
            try:
                return audit.audit_note(path, stem, "電力系統")
            finally:
                audit.ROOT = root

    def flags(self, note):
        return {sub["label"]: set(sub["flags"]) for sub in note["subs"]}

    def orphans(self, note):
        return [number for sub in note["subs"] for number in sub["orphan_numbers"]]

    def test_complete_note_has_no_orphan_flags(self):
        note = self.audit_text(GOOD)
        self.assertEqual(note["note_flags"], [])
        for flags in self.flags(note).values():
            self.assertFalse(flags & {"no-logic", "orphan-number"})

    def test_no_logic_flag_is_retired(self):
        # v1.9.0: 解題邏輯／邏輯 labels are gone; a note without them is not flagged.
        body = GOOD.replace("**解題邏輯**：", "").replace("**邏輯**：歐姆定律。", "")
        note = self.audit_text(body)
        self.assertEqual(note["note_flags"], [])
        self.assertNotIn("no-logic", audit.LOGIC_WEIGHTS)
        for flags in self.flags(note).values():
            self.assertNotIn("no-logic", flags)

    def test_orphan_number_in_display_substitution_is_flagged(self):
        body = GOOD.replace(r"P=I^2R=20^2\times12=400\times12=4800", r"P=I^2R=20^2\times15=400\times15=6000")
        note = self.audit_text(body)
        self.assertEqual(self.orphans(note), ["15"])
        self.assertIn("orphan-number", self.flags(note)["二"])

    def test_numbers_from_earlier_text_stem_and_small_integers_are_not_orphans(self):
        # 12 and 240 come from the stem, 20 from the previous result, 2 and 3 are ignored.
        body = GOOD.replace(r"20^2\times12=400\times12", r"20^2\times12\times3-2=400\times12")
        self.assertEqual(self.orphans(self.audit_text(body)), [])

    def test_subscripts_exponents_and_units_are_ignored(self):
        self.assertEqual(audit.piece_numbers(r"Z_{31}\times10^{-3}\ \mathrm{V}\times 0.5^{4}"), ["0.5"])

    def test_imaginary_prefix_and_thousands_separator(self):
        self.assertEqual(audit.piece_numbers(r"j0.16+j0.11"), ["0.16", "0.11"])
        self.assertEqual(audit.numbers_in("26,057.78"), {audit.number_key("26057.78")})

    def test_jump_flag_is_kept(self):
        body = GOOD.replace(r"I=\frac{V}{R}=\frac{240}{12}=20\ \mathrm{A}", r"I=\frac{V}{R}")
        self.assertIn("jump", self.flags(self.audit_text(body))["一"])

    def test_gold_example_is_clean(self):
        note = next(n for n in audit.run_audit() if n["qid"] == "EE-106-05-2")
        self.assertEqual(note["note_flags"], [])
        self.assertEqual(self.orphans(note), [])
        for flags in self.flags(note).values():
            self.assertFalse(flags & {"no-logic", "orphan-number"})


if __name__ == "__main__":
    unittest.main()


class NumberRuleTests(unittest.TestCase):
    """AGENT-SOLVE 三之一 (2026-10-17): boxed answers 2 dp (stem precision wins), no ×10^-1/-2 for |x| >= 0.01."""

    mod = audit

    def note(self, standard):
        return "## 已知與所求\n\n電源 220 V。\n\n## 考場標準作答\n\n" + standard + "\n\n## 驗算\n\n無。\n"

    def test_intermediate_four_significant_figures_are_allowed(self):
        r = self.mod.rounding_audit(self.note("\\[V=0.8333\\times1.2=0.9999,\\quad \\boxed{V=1.00\\ \\mathrm{V}}\\]"), "")
        self.assertEqual(r["not_two_decimals"], 0)

    def test_boxed_answer_needs_two_decimals(self):
        r = self.mod.rounding_audit(self.note("\\[\\boxed{I=0.24561\\ \\mathrm{A}}\\]"), "")
        self.assertEqual(r["not_two_decimals"], 1)

    def test_stem_precision_wins(self):
        r = self.mod.rounding_audit(self.note("\\[\\boxed{\\mathrm{PF}=0.9803}\\]"), "（本題計算過程中，小數點請採計至第 4 位）")
        self.assertEqual(r["not_two_decimals"], 0)

    def test_scientific_notation_for_large_values_is_flagged_but_not_tiny_constants(self):
        r = self.mod.rounding_audit(self.note("\\[x=1.44\\times10^{-2},\\quad \\varepsilon_0=8.854\\times10^{-12}\\]"), "")
        self.assertEqual(r["numbers"], ["1.44\\times10^{-2}"])
