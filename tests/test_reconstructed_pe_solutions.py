# -*- coding: utf-8 -*-
"""Regression locks for the source-reconstructed PE questions."""

import json
import hashlib
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
                legacy_status = re.search(r"^status:\s*(\S+)\s*$", text, re.M)
                if legacy_status:
                    self.assertEqual(legacy_status.group(1), "verified", f"conflicting legacy status: {path.name}")
                verified_at = re.search(r"^verified_at:\s*(\S+)\s*$", text, re.M)
                self.assertIsNotNone(verified_at, f"verified note lacks verified_at: {path.name}")
                self.assertNotEqual(verified_at.group(1), "null", f"verified note has null verified_at: {path.name}")
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

    def test_canonical_solution_bodies_are_not_accidentally_reused(self):
        """Different questions must not silently inherit an identical answer body."""
        bodies = {}
        for path in CANONICAL.glob("*/canonical/EE-*.md"):
            text = path.read_text(encoding="utf-8")
            body = re.sub(r"^---.*?---\s*", "", text, flags=re.S)
            body = re.sub(r"^# .*?\n", "", body, count=1, flags=re.M)
            body = re.sub(r"EE-\d{3}-\d{2}-\d+", "EE-Q", body)
            body = re.sub(r"\d{3} 年", "YEAR 年", body)
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            self.assertNotIn(digest, bodies, f"identical canonical solution body reused: {path.name} and {bodies.get(digest)}")
            bodies[digest] = path.name

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

    def test_corrected_gic_and_lv_fault_notes_keep_distinct_verified_results(self):
        """Guard against the earlier band-stop/short-circuit answer substitutions."""
        gic = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-108-02-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", gic)
        self.assertIn("10sRC", gic)
        self.assertIn("二階帶通", gic)
        self.assertNotIn("二階帶阻（陷波）", gic)

        fault = (CANONICAL / "06_工業配電" / "canonical" / "EE-112-06-4.md").read_text(encoding="utf-8")
        self.assertIn("19\\,478.754", fault)
        self.assertIn("0.4827765", fault)
        self.assertIn("\\boxed{0.48}", fault)

        interleaved = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-108-02-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", interleaved)
        self.assertIn("\\mathbf{0.75\\text{ A}}", interleaved)
        self.assertIn("3.375\\text{ A}", interleaved)
        self.assertIn("2.625\\text{ A}", interleaved)
        self.assertNotIn("0.3\\text{ A}", interleaved)

        double_line = (CANONICAL / "05_電力系統" / "canonical" / "EE-108-05-5.md").read_text(encoding="utf-8")
        self.assertIn("2.2859614\\sin\\delta", double_line)
        self.assertIn("0.7526946\\sin\\delta", double_line)
        self.assertIn("1.4695465\\sin\\delta", double_line)

        synchronous = (CANONICAL / "04_電機機械" / "canonical" / "EE-110-04-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", synchronous)
        self.assertIn("178.70\\text{ V/相}", synchronous)
        self.assertIn("0.8379\\text{ 落後}", synchronous)
        self.assertIn("15.000\\,\\mathrm{kW}", synchronous)

        autotransformer = (CANONICAL / "04_電機機械" / "canonical" / "EE-110-04-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", autotransformer)
        self.assertIn("I_L-I_H=323.86-187.50=136.36", autotransformer)
        self.assertIn("\\sqrt3\\times71.25=123.41", autotransformer)

        starter = (CANONICAL / "04_電機機械" / "canonical" / "EE-110-04-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", starter)
        self.assertIn("0.3425\\ \\Omega", starter)
        self.assertIn("38.32\\text{ N}\\cdot\\text{m}", starter)

        dc_machine = (CANONICAL / "04_電機機械" / "canonical" / "EE-109-04-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", dc_machine)
        self.assertIn("131.061\\text{ A}", dc_machine)
        self.assertIn("101.914\\text{ A}", dc_machine)
        self.assertIn("8202.27", dc_machine)

        induction = (CANONICAL / "04_電機機械" / "canonical" / "EE-109-04-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", induction)
        self.assertIn("72.67\\text{ N}\\cdot\\text{m}", induction)
        self.assertIn("18.66\\text{ N}\\cdot\\text{m}", induction)

        rotating_mmfs = (CANONICAL / "04_電機機械" / "canonical" / "EE-109-04-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", rotating_mmfs)
        self.assertIn("1.5 N I \\angle 0^\\circ", rotating_mmfs)
        self.assertIn("1.5 N I \\angle 60^\\circ", rotating_mmfs)
        self.assertIn("50\\text{ Hz}", rotating_mmfs)

        reluctance = (CANONICAL / "04_電機機械" / "canonical" / "EE-109-04-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", reluctance)
        self.assertIn("1.3572 \\times 10^{-3}", reluctance)
        self.assertIn("0.2714\\text{ N}\\cdot\\text{m}", reluctance)

        buck_auto = (CANONICAL / "04_電機機械" / "canonical" / "EE-108-04-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", buck_auto)
        self.assertIn("一次側接 $600", buck_auto)
        self.assertIn("S_{auto}=600 I_{in}=480 I_{out}=25.0", buck_auto)
        self.assertIn("S_{cond}=V_{load}I_{in}=480(41.6667)=20.0", buck_auto)

        dc_motor_108 = (CANONICAL / "04_電機機械" / "canonical" / "EE-108-04-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", dc_motor_108)
        self.assertIn("I_a=\\frac{V_t-E_a}{R_a}=\\frac{128-125}{0.03}=100", dc_motor_108)
        self.assertIn("P_{em}=E_aI_a=125(100)=12.5", dc_motor_108)
        self.assertIn("39.79\\,\\mathrm{N\\cdot m}", dc_motor_108)

        induction_108 = (CANONICAL / "04_電機機械" / "canonical" / "EE-108-04-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", induction_108)
        self.assertIn("P_{ag}=3|I_2'|^2\\frac{R_2'}s=5747.72", induction_108)
        self.assertIn("42.47\\,\\mathrm{N\\cdot m}", induction_108)
        self.assertIn("0.8637", induction_108)

        synchronous_108 = (CANONICAL / "04_電機機械" / "canonical" / "EE-108-04-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", synchronous_108)
        self.assertIn("2628.18", synchronous_108)
        self.assertIn("3.0999\\,\\mathrm{MW}", synchronous_108)
        self.assertIn("1.2334\\times10^5", synchronous_108)

        transformer_107 = (CANONICAL / "04_電機機械" / "canonical" / "EE-107-04-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", transformer_107)
        self.assertIn("I_L=\\frac{S_L}{\\sqrt3V_{LL}}", transformer_107)
        self.assertIn("8.725\\,\\mathrm A", transformer_107)
        self.assertIn("83.33\\%", transformer_107)

        series_107 = (CANONICAL / "04_電機機械" / "canonical" / "EE-107-04-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", series_107)
        self.assertIn("n=1200\\frac{49.5}{40}=1485", series_107)
        self.assertIn("76.394\\,\\mathrm{N\\cdot m}", series_107)

        induction_107 = (CANONICAL / "04_電機機械" / "canonical" / "EE-107-04-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", induction_107)
        self.assertIn("34.40\\text{ N}\\cdot\\text{m}", induction_107)
        self.assertIn("42.78\\text{ N}\\cdot\\text{m}", induction_107)

        synchronous_107 = (CANONICAL / "04_電機機械" / "canonical" / "EE-107-04-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", synchronous_107)
        self.assertIn("396.35\\,\\mathrm V", synchronous_107)
        self.assertIn("94.12\\%", synchronous_107)

        vf_107 = (CANONICAL / "04_電機機械" / "canonical" / "EE-107-04-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", vf_107)
        self.assertIn("1425\\,\\mathrm{rpm}", vf_107)
        self.assertIn("120\\,\\mathrm V", vf_107)
        self.assertIn("855\\,\\mathrm{rpm}", vf_107)

        flyback_109 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-109-02-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: needs_manual_review", flyback_109)
        self.assertIn("DCM 三角波", flyback_109)
        self.assertIn("60\\text{ A}", flyback_109)
        self.assertIn("274.4\\ \\mu\\text{H}", flyback_109)
        self.assertIn("93.75\\%", flyback_109)

        fault_109 = (CANONICAL / "06_工業配電" / "canonical" / "EE-109-06-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", fault_109)
        self.assertIn("11.659\\,\\mathrm{kA}", fault_109)

        lighting_109 = (CANONICAL / "06_工業配電" / "canonical" / "EE-109-06-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", lighting_109)
        self.assertIn("43.41", lighting_109)
        self.assertIn("304.05\\,\\mathrm{lx}", lighting_109)

        pf_109 = (CANONICAL / "06_工業配電" / "canonical" / "EE-109-06-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", pf_109)
        self.assertIn("242.968\\,\\mathrm{kvar}", pf_109)
        self.assertIn("0.84805", pf_109)

        magnetic_110 = (CANONICAL / "04_電機機械" / "canonical" / "EE-110-04-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", magnetic_110)
        self.assertIn("0.07603\\text{ T}", magnetic_110)
        self.assertIn("0.4704\\text{ mJ}", magnetic_110)


if __name__ == "__main__":
    unittest.main()
