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
    def test_engineering_math_annual_notes_use_canonical_bodies(self):
        """Annual engineering-math pages must expose solved canonical questions."""
        math_dir = CANONICAL / "03_工程數學"
        generic_markers = (
            "精確識別題型屬於常微分方程",
            "完整數學推導完成，步驟條理分明",
            "套用拉氏反轉換、Gram-Schmidt 正交化程序或留數計算公式",
        )
        for year in range(104, 115):
            notes = sorted(math_dir.glob(f"canonical/EE-{year:03d}-03-*.md"))
            annual = math_dir / f"{year}年_工程數學_全卷完整詳細題解.md"
            self.assertTrue(notes, f"missing canonical engineering-math notes for {year}")
            self.assertTrue(annual.is_file(), f"missing annual engineering-math note for {year}")
            annual_text = annual.read_text(encoding="utf-8")
            for marker in generic_markers:
                self.assertNotIn(marker, annual_text, f"generic template remains in {annual.name}")
            for note in notes:
                title = next((line for line in note.read_text(encoding="utf-8").splitlines() if line.startswith("# ")), note.stem)
                self.assertIn(title, annual_text, f"canonical question missing from annual note: {note.name}")
            self.assertIn("題級校驗狀態", annual_text, f"audit state missing from annual note: {annual.name}")

    def test_explicit_crop_questions_align_with_annual_notes(self):
        """Annual notes must not silently contain another year's numeric template."""
        ordinal = "一二三四五六七八九十"
        checked = 0
        for path in CANONICAL.glob("*/canonical/EE-*.md"):
            text = path.read_text(encoding="utf-8")
            qid = re.search(r"^qid:\s*(EE-\d{3}-\d{2}-(\d+))\s*$", text, re.M)
            prompt = re.search(r"^## 官方題目.*?\n(.*?)(?=\n## |\Z)", text, re.S | re.M)
            if not qid or not prompt:
                continue
            year = qid.group(1).split("-")[1]
            question_number = int(qid.group(2))
            annual_candidates = [
                candidate
                for candidate in CANONICAL.glob(f"*/{year}年_*全卷完整詳細題解.md")
                if candidate.parent.name == path.parent.parent.name
            ]
            self.assertTrue(annual_candidates, f"missing annual note for {qid.group(1)}")
            annual = annual_candidates[0].read_text(encoding="utf-8")
            headings = list(re.finditer(r"^## ([一二三四五六七八九十]+)、", annual, re.M))
            target = ordinal[question_number - 1]
            candidates = []
            official_values = {
                value
                for value in re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", prompt.group(1))
                if value not in {str(year), "104", "105", "106", "107", "108", "109", "110", "111", "112", "113", "114"}
            }
            if len(official_values) < 4:
                continue
            for index, heading in enumerate(headings):
                if heading.group(1) != target:
                    continue
                end = headings[index + 1].start() if index + 1 < len(headings) else len(annual)
                block = annual[heading.start():end]
                annual_values = set(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", block))
                overlap = len(official_values & annual_values) / len(official_values)
                candidates.append(overlap)
            self.assertTrue(candidates, f"missing question section in annual note: {qid.group(1)}")
            checked += 1
            self.assertGreaterEqual(
                max(candidates),
                0.35,
                f"annual note appears to use a mismatched template: {qid.group(1)}",
            )
        self.assertGreaterEqual(checked, 50, "alignment guard unexpectedly covers too few explicit crop questions")

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

    def test_manual_review_notes_have_actionable_disposition(self):
        """Every unresolved question must explain the blocker and next check."""
        manifests = [
            ROOT / "data" / "pe-solution-audit.json",
            ROOT / "data" / "engineering-math-audit.json",
        ]
        manual = []
        for manifest in manifests:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            manual.extend(entry for entry in data["entries"] if entry.get("audit_status") == "needs_manual_review")
        self.assertEqual(len(manual), 27, "manual-review count changed; update the explicit review register")
        for entry in manual:
            path = ROOT / entry["solution_link"]
            text = path.read_text(encoding="utf-8")
            for key in ("review_disposition", "review_blocker", "review_action"):
                match = re.search(rf"^{key}:\s*(.+)$", text, re.M)
                self.assertIsNotNone(match, f"{entry['qid']} lacks {key}")
                self.assertNotEqual(match.group(1).strip().lower(), "todo", f"{entry['qid']} has placeholder {key}")
            self.assertNotIn("尚未完成獨立逐步重算", text, f"{entry['qid']} was left as an unworked placeholder")

    def test_dashboard_exposes_manual_review_metadata_to_solution_modal(self):
        """The UI must be able to show why a conditional answer is unresolved."""
        dashboard = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("const SOLUTION_REVIEW_METADATA", dashboard)
        self.assertIn('"EE-112-05-4"', dashboard)
        self.assertIn('"impedance_type_branches"', dashboard)
        self.assertIn("function renderSolutionReviewCard", index)
        self.assertIn("renderSolutionReviewCard(currentModalQid)", index)

    def test_review_center_can_filter_manual_review_queue(self):
        """The review center must expose a dedicated queue for unresolved items."""
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<option value="manual">待人工覆核</option>', index)
        self.assertIn("reviewFilter === 'manual'", index)
        self.assertIn("isManualReviewQuestion(q)", index)

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

        ccvs_107 = (CANONICAL / "01_電路學" / "canonical" / "EE-107-01-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", ccvs_107)
        self.assertIn("V_2=15i_\\phi", ccvs_107)
        self.assertIn("P_{4\\Omega}=I_4^2(4)=2^2(4)=16", ccvs_107)

        inductors_107 = (CANONICAL / "01_電路學" / "canonical" / "EE-107-01-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", inductors_107)
        self.assertIn("-4.8-3.2e^{-2t}", inductors_107)
        self.assertIn("1.28e^{-2t}", inductors_107)

        transformer_107_circuit = (CANONICAL / "01_電路學" / "canonical" / "EE-107-01-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", transformer_107_circuit)
        self.assertIn("R_L = R_{th} = \\mathbf{35", transformer_107_circuit)
        self.assertIn("315\\text{ W}", transformer_107_circuit)

        three_phase_107 = (CANONICAL / "01_電路學" / "canonical" / "EE-107-01-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", three_phase_107)
        self.assertIn("39.5 + j28.6", three_phase_107)
        self.assertIn("2.4\\angle -36.87", three_phase_107)

        pn_107 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-107-02-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", pn_107)
        self.assertIn("0.738", pn_107)
        self.assertIn("0.259\\ \\mu\\text{m}", pn_107)

        nmos_107 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-107-02-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", nmos_107)
        self.assertIn("0.64\\text{ mA/V}", nmos_107)
        self.assertIn("390.6\\text{ k}\\Omega", nmos_107)

        boost_107 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-107-02-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", boost_107)
        self.assertIn("32.66\\%", boost_107)
        self.assertIn("不連續導通模式", boost_107)

        cuk_107 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-107-02-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", cuk_107)
        self.assertIn("0.03125\\text{ V}", cuk_107)
        self.assertIn("3.25\\text{ A}", cuk_107)

        transmission_107 = (CANONICAL / "05_電力系統" / "canonical" / "EE-107-05-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", transmission_107)
        self.assertIn("1.0805", transmission_107)
        self.assertIn("1.6512", transmission_107)

        generator_107 = (CANONICAL / "05_電力系統" / "canonical" / "EE-107-05-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", generator_107)
        self.assertIn("-84.0", generator_107)
        self.assertIn("804.40", generator_107)

        transformer_107_power = (CANONICAL / "05_電力系統" / "canonical" / "EE-107-05-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", transformer_107_power)
        self.assertIn("21.937", transformer_107_power)
        self.assertIn("8697.5", transformer_107_power)

        sequence_107 = (CANONICAL / "05_電力系統" / "canonical" / "EE-107-05-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", sequence_107)
        self.assertIn("601.051", sequence_107)
        self.assertIn("73.613", sequence_107)

        diversity_107 = (CANONICAL / "06_工業配電" / "canonical" / "EE-107-06-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", diversity_107)
        self.assertIn("127.533", diversity_107)
        self.assertIn("2025.72", diversity_107)

        capacitor_107 = (CANONICAL / "06_工業配電" / "canonical" / "EE-107-06-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", capacitor_107)
        self.assertIn("655.547", capacitor_107)
        self.assertIn("13.31", capacitor_107)

        differential_107 = (CANONICAL / "06_工業配電" / "canonical" / "EE-107-06-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", differential_107)
        self.assertIn("5.8539", differential_107)
        self.assertIn("1.399", differential_107)

        state_filter_106 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-106-02-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", state_filter_106)
        self.assertIn("v_X}{v_{out}}(s) = -", state_filter_106)
        self.assertIn("R_5 (R_3 + R_6)", state_filter_106)

        rectifier_106 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-106-02-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", rectifier_106)
        self.assertIn("I_o = \\frac{V_{o,avg}}{R}", rectifier_106)
        self.assertIn("PF = \\frac{2}{\\pi}", rectifier_106)

        boost_106 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-106-02-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", boost_106)
        self.assertIn("V_o}{V_{in}} = \\frac{D}{1 - D}", boost_106)
        self.assertIn("(\\Delta I_L)^2}{12}", boost_106)

        auto_106 = (CANONICAL / "04_電機機械" / "canonical" / "EE-106-04-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", auto_106)
        self.assertIn("550.0\\text{ kVA}", auto_106)
        self.assertIn("99.81\\%", auto_106)

        grounding_106 = (CANONICAL / "06_工業配電" / "canonical" / "EE-106-06-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", grounding_106)
        self.assertIn("遮斷容量", grounding_106)
        self.assertIn("接觸電壓", grounding_106)

        transformer_106 = (CANONICAL / "06_工業配電" / "canonical" / "EE-106-06-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", transformer_106)
        self.assertIn("Δ–Y", transformer_106)
        self.assertIn("3150 V 一次分接頭、210 V 二次分接頭", transformer_106)

        resonance_106 = (CANONICAL / "06_工業配電" / "canonical" / "EE-106-06-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", resonance_106)
        self.assertIn("\\sqrt{49}=7", resonance_106)
        self.assertIn("第 7 次諧波", resonance_106)

        nonlinear_105 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-105-02-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", nonlinear_105)
        self.assertIn("300\\sqrt{3}", nonlinear_105)
        self.assertIn("0.9242", nonlinear_105)

        stability_105 = (CANONICAL / "05_電力系統" / "canonical" / "EE-105-05-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", stability_105)
        self.assertIn("同步調相機", stability_105)
        self.assertIn("虛擬慣性", stability_105)

        sequence_104 = (CANONICAL / "06_工業配電" / "canonical" / "EE-104-06-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", sequence_104)
        self.assertIn("1.16036", sequence_104)
        self.assertIn("0.99741", sequence_104)

        open_neutral_105 = (CANONICAL / "06_工業配電" / "canonical" / "EE-105-06-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", open_neutral_105)
        self.assertIn("183.482", open_neutral_105)
        self.assertIn("36.5185", open_neutral_105)

        harmonic_105 = (CANONICAL / "06_工業配電" / "canonical" / "EE-105-06-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", harmonic_105)
        self.assertIn("390.7", harmonic_105)
        self.assertIn("第 7 次", harmonic_105)

        lighting_105 = (CANONICAL / "06_工業配電" / "canonical" / "EE-105-06-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", lighting_105)
        self.assertIn("1{,}978{,}022", lighting_105)
        self.assertIn("1501.5", lighting_105)

        circuit_105_1 = (CANONICAL / "01_電路學" / "canonical" / "EE-105-01-1.md").read_text(encoding="utf-8")
        circuit_105_2 = (CANONICAL / "01_電路學" / "canonical" / "EE-105-01-2.md").read_text(encoding="utf-8")
        circuit_105_3 = (CANONICAL / "01_電路學" / "canonical" / "EE-105-01-3.md").read_text(encoding="utf-8")
        circuit_105_4 = (CANONICAL / "01_電路學" / "canonical" / "EE-105-01-4.md").read_text(encoding="utf-8")
        circuit_105_5 = (CANONICAL / "01_電路學" / "canonical" / "EE-105-01-5.md").read_text(encoding="utf-8")
        for note in (circuit_105_1, circuit_105_2, circuit_105_3, circuit_105_4, circuit_105_5):
            self.assertIn("audit_status: verified", note)
        self.assertIn("-\\frac{4}{3}", circuit_105_1)
        self.assertIn("10000}{7}", circuit_105_2)
        self.assertIn("93.6", circuit_105_3)
        self.assertIn("48.62", circuit_105_4)
        self.assertIn("1\\text{ H}", circuit_105_5)

        mutual_104 = (CANONICAL / "01_電路學" / "canonical" / "EE-104-01-2.md").read_text(encoding="utf-8")
        transient_104 = (CANONICAL / "01_電路學" / "canonical" / "EE-104-01-4.md").read_text(encoding="utf-8")
        gparam_104 = (CANONICAL / "01_電路學" / "canonical" / "EE-104-01-5.md").read_text(encoding="utf-8")
        for note in (mutual_104, transient_104, gparam_104):
            self.assertIn("audit_status: verified", note)
        self.assertIn("0.6634", mutual_104)
        self.assertIn("(s+100)^2", transient_104)
        self.assertIn("0.04 - j0.02", gparam_104)

        inverter_104 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-104-02-4.md").read_text(encoding="utf-8")
        oscillator_104 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-104-02-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", inverter_104)
        self.assertIn("8.483", inverter_104)
        self.assertIn("audit_status: verified", oscillator_104)
        self.assertIn("2.166", oscillator_104)

        rectifier_104 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-104-02-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", rectifier_104)
        self.assertIn("17.121", rectifier_104)
        self.assertIn("9.885", rectifier_104)

        induction_104 = (CANONICAL / "04_電機機械" / "canonical" / "EE-104-04-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", induction_104)
        self.assertIn("11.006", induction_104)
        self.assertIn("$(1-s)r_r/s$", induction_104)

        opamp_105 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-105-02-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", opamp_105)
        self.assertIn("-79.9676", opamp_105)
        self.assertIn("-0.0405\\%", opamp_105)

        freq_105 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-105-02-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", freq_105)
        self.assertIn("1750.7", freq_105)
        self.assertIn("1.607", freq_105)

        limiter_105 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-105-02-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", limiter_105)
        self.assertIn("3.84", limiter_105)
        self.assertIn("-4.625", limiter_105)
        self.assertIn("1.156", limiter_105)

        buck_boost_112 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-112-02-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", buck_boost_112)
        self.assertIn("13.33", buck_boost_112)
        self.assertIn("120\\,\\mu\\text{F}", buck_boost_112)
        self.assertIn("V_o=-36", buck_boost_112)

        rectifier_fourier_112 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-112-02-4.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", rectifier_fourier_112)
        self.assertIn("0.4962", rectifier_fourier_112)
        self.assertIn("72.2704", rectifier_fourier_112)
        self.assertIn("91.7538", rectifier_fourier_112)

        motor_drop_105 = (CANONICAL / "06_工業配電" / "canonical" / "EE-105-06-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", motor_drop_105)
        self.assertIn("2.2013", motor_drop_105)
        self.assertIn("20.5206", motor_drop_105)
        self.assertIn("5.5I_{rated}", motor_drop_105)

        gs_105 = (CANONICAL / "05_電力系統" / "canonical" / "EE-105-05-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", gs_105)
        self.assertIn("0.913486", gs_105)
        self.assertIn("0.921111", gs_105)
        self.assertIn("0.904925-j0.124770", gs_105)

        penalty_105 = (CANONICAL / "05_電力系統" / "canonical" / "EE-105-05-5.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", penalty_105)
        self.assertIn("IC}_2=9", penalty_105)
        self.assertIn("發電廠 2", penalty_105)

        pmos_104 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-104-02-1.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", pmos_104)
        self.assertIn("-1.66144", pmos_104)
        self.assertIn("1+g_mR_S", pmos_104)

        cb_104 = (CANONICAL / "02_電子學_含電力電子" / "canonical" / "EE-104-02-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", cb_104)
        self.assertIn("14.3479", cb_104)
        self.assertIn("R_L\\parallel R_B", cb_104)

        parallel_104 = (CANONICAL / "05_電力系統" / "canonical" / "EE-104-05-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", parallel_104)
        self.assertIn("169.369", parallel_104)
        self.assertIn("2.73182", parallel_104)
        self.assertIn("TR1+TR2", parallel_104)

        capacity_104 = (CANONICAL / "06_工業配電" / "canonical" / "EE-104-06-2.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", capacity_104)
        self.assertIn("406.84", capacity_104)
        self.assertIn("402.7673", capacity_104)

        fault_105 = (CANONICAL / "06_工業配電" / "canonical" / "EE-105-06-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", fault_105)
        self.assertIn("34.366", fault_105)
        self.assertIn("37.373", fault_105)
        self.assertIn("0.0643678", fault_105)

        thevenin_104 = (CANONICAL / "01_電路學" / "canonical" / "EE-104-01-1.md").read_text(encoding="utf-8")
        power_104 = (CANONICAL / "01_電路學" / "canonical" / "EE-104-01-3.md").read_text(encoding="utf-8")
        self.assertIn("audit_status: verified", thevenin_104)
        self.assertIn("1.8 +", thevenin_104)
        self.assertIn("audit_status: verified", power_104)
        self.assertIn("4912.23", power_104)


if __name__ == "__main__":
    unittest.main()
