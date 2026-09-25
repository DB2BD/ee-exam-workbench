"""Regression coverage for the completed score-oriented core path."""

import json
import math
import re
import unittest
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

from scripts.question_schema import load_questions_from_bundle


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = ROOT / "📝 個人題解與錯題本"
PATH_DOC = ROOT / "docs" / "上榜預設24時段_核心題路徑.md"

COMPLETED_QIDS = (
    "EE-114-01-3",
    "EE-110-02-3",
    "EE-113-03-6",
    "EE-112-04-5",
    "EE-114-05-2",
    "EE-113-06-4",
    "EE-112-01-4",
    "EE-111-01-3",
    "EE-106-02-4",
    "EE-104-02-3",
    "EE-104-03-4",
    "EE-107-03-5",
    "EE-107-04-2",
    "EE-111-04-3",
    "EE-109-05-3",
    "EE-105-05-2",
    "EE-112-06-3",
    "EE-114-06-3",
    "EE-112-01-2",
    "EE-107-02-3",
    "EE-113-03-3",
    "EE-114-04-4",
    "EE-114-05-5",
    "EE-110-06-4",
    "EE-111-01-2",
    "EE-113-01-3",
    "EE-112-02-3",
    "EE-106-02-5",
    "EE-111-03-5",
    "EE-112-03-4",
    "EE-113-04-2",
    "EE-112-04-3",
    "EE-112-05-4",
    "EE-110-05-5",
    "EE-104-06-3",
    "EE-113-06-3",
)

REQUIRED_SECTIONS = (
    "## 考場標準作答",
    "## 得分點拆解",
    "## 完整教學推導",
    "## 獨立驗算",
    "## 常見失分",
)


class TestScoreOrientedCorePath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_qid = {
            path.stem: path
            for path in CANONICAL_ROOT.glob("*/canonical/EE-*.md")
        }
        cls.path_doc = PATH_DOC.read_text(encoding="utf-8")
        bundle = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
        match = re.search(
            r"const QUESTION_TAXONOMY_MAP\s*=\s*(\{.*?\});\nconst SOLUTION_REVIEW_METADATA",
            bundle,
            re.DOTALL,
        )
        if not match:
            raise AssertionError("dashboard-data.js is missing QUESTION_TAXONOMY_MAP")
        cls.taxonomy = json.loads(match.group(1))
        cls.questions = load_questions_from_bundle(ROOT / "dashboard-data.js")

    def test_completed_questions_follow_the_scoring_structure(self):
        self.assertEqual(len(COMPLETED_QIDS), 36)
        self.assertEqual(len(set(COMPLETED_QIDS)), 36)
        for qid in COMPLETED_QIDS:
            with self.subTest(qid=qid):
                self.assertIn(qid, self.by_qid)
                text = self.by_qid[qid].read_text(encoding="utf-8")
                self.assertIn("audit_status: verified", text)
                positions = []
                for heading in REQUIRED_SECTIONS:
                    self.assertEqual(text.count(heading), 1, f"{qid}: {heading}")
                    positions.append(text.index(heading))
                self.assertEqual(positions, sorted(positions), qid)
                self.assertIn(qid, self.path_doc)

    def test_each_subject_uses_exactly_its_two_highest_year_coverage_chapters(self):
        chapter_rows = defaultdict(list)
        for row in self.questions:
            chapter = self.taxonomy[row[0]]["primaryChapter"]
            chapter_rows[(row[1], chapter)].append(row)

        expected_top_two = {}
        for subject in ("01", "02", "03", "04", "05", "06"):
            ranked = sorted(
                (
                    (chapter, rows)
                    for (chapter_subject, chapter), rows in chapter_rows.items()
                    if chapter_subject == subject
                ),
                key=lambda item: (
                    -len({row[2] for row in item[1]}),
                    -len(item[1]),
                    item[0],
                ),
            )
            expected_top_two[subject] = {chapter for chapter, _ in ranked[:2]}

        selected = defaultdict(Counter)
        for qid in COMPLETED_QIDS:
            subject = qid.split("-")[2]
            selected[subject][self.taxonomy[qid]["primaryChapter"]] += 1

        self.assertEqual(set(selected), set(expected_top_two))
        for subject, expected_chapters in expected_top_two.items():
            with self.subTest(subject=subject):
                self.assertEqual(set(selected[subject]), expected_chapters)
                self.assertEqual(sorted(selected[subject].values()), [3, 3])

    def test_each_question_has_separate_question_and_solution_links(self):
        links = re.findall(
            r"\[(題目|核對) (EE-\d{3}-\d{2}-\d+)\]\(([^)]+)\)",
            self.path_doc,
        )
        by_qid = defaultdict(dict)
        for label, qid, raw_target in links:
            self.assertNotIn(label, by_qid[qid], f"duplicate {label} link for {qid}")
            by_qid[qid][label] = raw_target

        self.assertEqual(set(by_qid), set(COMPLETED_QIDS))
        for qid in COMPLETED_QIDS:
            with self.subTest(qid=qid):
                self.assertEqual(set(by_qid[qid]), {"題目", "核對"})
                question = unquote(by_qid[qid]["題目"])
                solution = unquote(by_qid[qid]["核對"])
                self.assertTrue(question.endswith(".png"), question)
                self.assertTrue(solution.endswith(f"canonical/{qid}.md"), solution)
                self.assertTrue((PATH_DOC.parent / question).resolve().is_file(), question)
                self.assertTrue((PATH_DOC.parent / solution).resolve().is_file(), solution)

        self.assertIn("題目入口（先開）", self.path_doc)
        self.assertIn("題解核對（停筆後開）", self.path_doc)
        self.assertIn("避免作答前誤看答案", self.path_doc)

    def test_rectifier_route_starts_with_a_rectifier_and_changes_one_condition(self):
        rows = {int(match.group(1)): match.group(2) for match in re.finditer(r"^\| (\d+) \| ([^\n]+)$", self.path_doc, re.MULTILINE)}
        self.assertIn("母題", rows[2])
        self.assertIn("EE-110-02-3", rows[2])
        self.assertIn("EE-106-02-4", rows[8])
        self.assertIn("EE-104-02-3", rows[8])
        self.assertNotIn("EE-113-02-1", self.path_doc)
        for qid in ("EE-110-02-3", "EE-106-02-4", "EE-104-02-3"):
            note = self.by_qid[qid].read_text(encoding="utf-8")
            with self.subTest(qid=qid):
                self.assertIn("整流", note)
                for heading in REQUIRED_SECTIONS:
                    self.assertEqual(note.count(heading), 1)

        mother = self.by_qid["EE-110-02-3"].read_text(encoding="utf-8")
        standard = mother.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"i_s(\theta)=i_L(\theta)=v_o(\theta)/R", standard)
        self.assertIn("負半週負載與電源電流都為零", standard)

        waveform_note = self.by_qid["EE-106-02-4"]
        waveform_text = waveform_note.read_text(encoding="utf-8")
        match = re.search(r"!\[輸出電壓與兩顆二極體電流的同軸波形\]\(([^)]+\.svg)\)", waveform_text)
        self.assertIsNotNone(match)
        waveform = (waveform_note.parent / unquote(match.group(1))).resolve()
        self.assertTrue(waveform.is_file(), waveform)
        root = ET.parse(waveform).getroot()
        ns = "{http://www.w3.org/2000/svg}"
        self.assertEqual(root.tag, f"{ns}svg")
        self.assertEqual(len(root.findall(f"{ns}polyline")), 1)
        self.assertGreaterEqual(len(root.findall(f".//{ns}path")), 4)

    def test_six_pulse_resistive_rms_uses_pulse_integral_and_symmetry(self):
        note = self.by_qid["EE-104-02-3"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"\int_{-\pi/6}^{\pi/6}\cos^2\phi", standard)
        self.assertIn(r"\frac\pi6+\frac{\sqrt3}{4}", standard)
        self.assertIn("每顆的均方值是負載的", standard)
        self.assertIn("一條相線另有對稱的正、負兩段", standard)
        self.assertIn("不能僅憑導通時間比例", note)

    def test_joint_density_mother_proves_independence_in_standard_answer(self):
        note = self.by_qid["EE-113-03-6"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"p_X(x)=\int_0^\infty", standard)
        self.assertIn(r"p(x,y)=p_X(x)p_Y(y)", standard)
        self.assertIn(r"\boxed{48}", standard)
        self.assertNotIn("(p_X(x)p_Y(y))", note)

    def test_dc_motor_mother_links_magnetization_curve_and_checks_speed_direction(self):
        note_path = self.by_qid["EE-112-04-5"]
        note = note_path.read_text(encoding="utf-8")
        match = re.search(r"!\[官方題目與 1200 rpm 磁化曲線\]\(([^)]+\.png)\)", note)
        self.assertIsNotNone(match)
        self.assertTrue((note_path.parent / unquote(match.group(1))).resolve().is_file())
        self.assertIn("轉速必須高於", note)
        self.assertIn(r"232.6\,\mathrm V", note)

    def test_power_flow_mother_states_angle_branch_before_q_limit(self):
        note = self.by_qid["EE-114-05-2"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("低功角分支", standard)
        self.assertIn(r"|\delta_2|<90^\circ", standard)
        self.assertLess(standard.index("低功角分支"), standard.index(r"Q_{g2}=0.11314"))
        self.assertIn("不能宣稱這是數學上的唯一根", standard)

    def test_short_circuit_mother_separates_fault_total_from_breaker_branch(self):
        note_path = self.by_qid["EE-113-06-4"]
        note = note_path.read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        match = re.search(r"!\[官方單線圖與故障點 F\]\(([^)]+\.png)\)", note)
        self.assertIsNotNone(match)
        self.assertTrue((note_path.parent / unquote(match.group(1))).resolve().is_file())
        self.assertIn(r"S_{\mathrm{CB},F}", standard)
        self.assertIn(r"15.42\,\mathrm{MVA}", standard)
        self.assertIn(r"18.55\,\mathrm{kA}", standard)
        self.assertIn("馬達向 F 的倒灌不流過該 CB 接點", standard)

    def test_parallel_rlc_same_type_keeps_step_forcing_in_equation(self):
        note_path = self.by_qid["EE-112-01-4"]
        note = note_path.read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"+250i=-1500", standard)
        self.assertNotIn(r"+250i=0", standard)
        self.assertIn(r"i_p=-6\,\mathrm A", note)
        self.assertIn(r"\tilde i=i-i_p=i+6", note)
        match = re.search(r"!\[官方並聯 RLC 題圖\]\(([^)]+\.png)\)", note)
        self.assertIsNotNone(match)
        self.assertTrue((note_path.parent / unquote(match.group(1))).resolve().is_file())

    def test_notch_variation_links_official_topology_without_stale_annual_conflict(self):
        note_path = self.by_qid["EE-111-01-3"]
        note = note_path.read_text(encoding="utf-8")
        match = re.search(r"!\[官方 RLC 帶拒電路題圖\]\(([^)]+\.png)\)", note)
        self.assertIsNotNone(match)
        self.assertTrue((note_path.parent / unquote(match.group(1))).resolve().is_file())
        self.assertIn("現行單題與年度題解均採上方的並聯負載分壓式", note)
        self.assertNotIn("年度整卷解答將本題當成串聯", note)
        self.assertNotIn(r"\`verified\`", note)

    def test_probability_pair_shows_marginal_proof_and_complete_pmf_support(self):
        density = self.by_qid["EE-104-03-4"].read_text(encoding="utf-8")
        density_standard = density.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"f_X(x)=\int_0^1", density_standard)
        self.assertIn(r"f_Y(y)=\int_0^1", density_standard)
        self.assertIn("區間外為零", density_standard)
        sampling = self.by_qid["EE-107-03-5"].read_text(encoding="utf-8")
        sampling_standard = sampling.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"x\notin\{0,1,2,3\}", sampling_standard)
        self.assertIn("時均為 \(0\)", sampling_standard)

    def test_dc_motor_external_torque_does_not_erase_no_load_loss(self):
        note = self.by_qid["EE-106-04-3"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("外接軸負載轉矩", note)
        self.assertIn("空載損失轉矩近似不變", note)
        self.assertIn(r"I_a=4+\frac{100}{1.8907607}=56.89", standard)
        self.assertIn(r"n=1000\frac{171.56}{198}=866.4", standard)
        self.assertIn("52.89", standard)
        self.assertIn("不能單獨推出其在所有轉速的函數", note)
        self.assertIn("原 106 年外接軸負載題因缺旋轉損失模型", self.path_doc)
        self.assertNotIn("[題目 EE-106-04-3]", self.path_doc)
        k_phi = 198 / (2 * math.pi * 1000 / 60)
        armature_current = 4 + 100 / k_phi
        load_speed = (200 - 0.5 * armature_current) / k_phi * 60 / (2 * math.pi)
        self.assertAlmostEqual(armature_current, 56.8887652, places=6)
        self.assertAlmostEqual(load_speed, 866.4425121, places=6)

    def test_dc_motor_same_type_uses_a_fully_specified_magnetization_question(self):
        note = self.by_qid["EE-107-04-2"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("[題目 EE-107-04-2]", self.path_doc)
        # Fixed inputs transcribed from the official crop, not parsed from the solution.
        for current, reference_emf, shown_speed, shown_torque in (
            (10, 40, "1485", "3.183"),
            (200, 48, "1000", "76.394"),
        ):
            with self.subTest(current=current):
                operating_emf = 50 - current * 0.05
                speed = 1200 * operating_emf / reference_emf
                torque = operating_emf * current / (2 * math.pi * speed / 60)
                self.assertIn(rf"{shown_speed}\,\mathrm{{rpm}}", standard)
                self.assertIn(rf"{shown_torque}\,\mathrm{{N\cdot m}}", standard)
                self.assertAlmostEqual(speed, float(shown_speed), places=6)
                self.assertAlmostEqual(torque, float(shown_torque), places=3)
        self.assertIn("題目問感應轉矩", standard)

    def test_dc_dc_route_uses_real_converter_topologies_and_checks_dcm(self):
        self.assertIn("[題目 EE-112-02-3]", self.path_doc)
        self.assertIn("[題目 EE-107-02-3]", self.path_doc)
        self.assertIn("[題目 EE-106-02-5]", self.path_doc)
        self.assertNotIn("[題目 EE-114-02-3]", self.path_doc)
        self.assertNotIn("[題目 EE-109-02-2]", self.path_doc)
        self.assertIn("114 年第 3 題是開關 RL 暫態", self.path_doc)
        mother = self.by_qid["EE-112-02-3"].read_text(encoding="utf-8")
        same_topology = self.by_qid["EE-107-02-3"].read_text(encoding="utf-8")
        self.assertIn("![官方題目裁切圖]", mother)
        self.assertIn("![官方題目裁切圖]", same_topology)
        standard = same_topology.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"L_B=", standard)
        self.assertIn(r"\boxed{\mathrm{DCM}}", standard)
        self.assertIn(r"D+D_2=0.8165<1", standard)
        load = 10**2 / 12
        candidate_duty = 10 / (15 + 10)
        boundary_l = (1 - candidate_duty) ** 2 * load / (2 * 25_000)
        duty = math.sqrt(2 * 40e-6 * 25_000 * 12 / 15**2)
        release_fraction = 15 * duty / 10
        self.assertAlmostEqual(boundary_l * 1e6, 60, places=6)
        self.assertAlmostEqual(duty, 0.3265986, places=6)
        self.assertLess(duty + release_fraction, 1)
        variant = self.by_qid["EE-106-02-5"].read_text(encoding="utf-8")
        variant_standard = variant.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("三角形電感電流", variant_standard)
        self.assertIn(r"\frac{1}{12}", variant_standard)

    def test_boost_critical_capacitance_requires_an_external_ripple_limit(self):
        note = self.by_qid["EE-109-02-2"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("audit_status: needs_manual_review", note)
        self.assertIn(r"C_c(\varepsilon)", standard)
        self.assertIn("無唯一數值", standard)
        self.assertNotIn(r"\boxed{C_c=200", standard)
        # The known 200 µF is the installed capacitor; it cannot independently
        # establish the missing design limit for a minimum capacitor.
        duty, resistance, frequency = 0.5, 10, 25_000
        installed_capacitance = 200e-6
        actual_ripple_ratio = duty / (resistance * frequency * installed_capacitance)
        self.assertAlmostEqual(actual_ripple_ratio, 0.01)
        self.assertAlmostEqual(duty / (resistance * frequency * 0.01), installed_capacitance)

    def test_synchronous_buck_boost_rms_keeps_the_ripple_term(self):
        note = self.by_qid["EE-106-02-5"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"\frac{V_o}{V_{in}}=\frac{D}{1-D}", standard)
        self.assertIn(r"\frac{1}{12}", standard)
        self.assertIn("小漣波近似", standard)
        input_voltage, duty, resistance = 12, 0.4, 10
        inductance, frequency = 100e-6, 25_000
        output_voltage = input_voltage * duty / (1 - duty)
        average_inductor_current = output_voltage / ((1 - duty) * resistance)
        ripple = input_voltage * duty / (inductance * frequency)
        exact_rms = math.sqrt(duty * (average_inductor_current**2 + ripple**2 / 12))
        approximate_rms = average_inductor_current * math.sqrt(duty)
        self.assertAlmostEqual(output_voltage, 8)
        self.assertGreater(exact_rms, approximate_rms)

    def test_compound_generator_does_not_borrow_later_condition_as_unique_answer(self):
        note = self.by_qid["EE-111-04-3"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("![官方題目裁切圖]", note)
        self.assertIn("第（二）題本身未給場控電阻", standard)
        self.assertIn("附加條件下的精細近似", standard)
        self.assertIn("約1.25", standard.replace("\\approx", "約"))
        self.assertIn("111 年第（二）小題未單獨給場控電阻", self.path_doc)
        # The official table has 214 V at 1.25 A and 222 V at 1.48 A.
        for shunt_current in (0.0, 1.0, 200 / 150):
            generated_emf = 200 + 0.14 * (100 + shunt_current)
            equivalent_field = 1.25 + (generated_emf - 214) * (1.48 - 1.25) / (222 - 214)
            self.assertLessEqual(equivalent_field, 1.25537)
            self.assertGreaterEqual(equivalent_field, 1.25)
        self.assertAlmostEqual(1.25 + 0.14 * 0.23 / 8, 1.254025, places=6)

    def test_flicker_route_does_not_mix_in_harmonic_resonance(self):
        rows = {
            int(match.group(1)): match.group(2)
            for match in re.finditer(r"^\| (\d+) \| ([^\n]+)$", self.path_doc, re.MULTILINE)
        }
        self.assertIn("電弧爐電壓閃爍", rows[18])
        self.assertIn("EE-110-06-4", rows[18])
        self.assertIn("EE-104-06-3", rows[24])
        self.assertIn("EE-113-06-3", rows[24])
        self.assertNotIn("EE-106-06-5", self.path_doc)
        for qid in ("EE-110-06-4", "EE-104-06-3", "EE-113-06-3"):
            note = self.by_qid[qid].read_text(encoding="utf-8")
            with self.subTest(qid=qid):
                self.assertIn("電弧爐", note)
                for heading in REQUIRED_SECTIONS:
                    self.assertEqual(note.count(heading), 1)
        mother = self.by_qid["EE-110-06-4"].read_text(encoding="utf-8")
        variation = self.by_qid["EE-113-06-3"].read_text(encoding="utf-8")
        self.assertIn("題目未指定串聯電抗器位置", mother)
        self.assertIn("基準電流", variation)
        self.assertIn("0.449", variation)

    def test_cross_method_variations_name_the_first_move(self):
        self.assertIn("111 年題是頻域橋接變式", self.path_doc)
        self.assertIn("轉移函數", self.path_doc)
        self.assertIn("107 年題是離散抽樣跨型變式", self.path_doc)
        self.assertIn("二項／超幾何分布", self.path_doc)

    def test_frequency_variation_shows_the_cutoff_scoring_equation(self):
        note = self.by_qid["EE-111-01-3"].read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn(r"|\omega_0^2-\omega^2|=\alpha\omega", standard)
        self.assertIn(r"\omega_1\omega_2=\omega_0^2", standard)
        self.assertIn("2400", standard)

    def test_discrete_probability_variation_answers_arbitrary_x(self):
        qid = "EE-107-03-5"
        canonical = self.by_qid[qid].read_text(encoding="utf-8")
        annual = (CANONICAL_ROOT / "03_工程數學" / "107年_工程數學_全卷完整詳細題解.md").read_text(encoding="utf-8")
        for label, note in (("canonical", canonical), ("annual", annual)):
            with self.subTest(note=label):
                self.assertIn("題目要求任意", note)
                self.assertIn("不必額外求指定", note)
                self.assertIn("只是驗算示例", note)
                self.assertNotIn("兩種情況都要分別代入", note)

    def test_joint_density_same_type_has_short_score_path_and_direct_check(self):
        qid = "EE-104-03-4"
        canonical = self.by_qid[qid].read_text(encoding="utf-8")
        annual = (CANONICAL_ROOT / "03_工程數學" / "104年_工程數學_全卷完整詳細題解.md").read_text(encoding="utf-8")
        for label, note in (("canonical", canonical), ("annual", annual)):
            with self.subTest(note=label):
                self.assertIn("先求邊際密度", note)
                self.assertIn("故 \\(X,Y\\) 獨立", note)
                self.assertIn("不用獨立性，直接由原聯合密度核對", note)
                self.assertIn("1/18>0", note)


if __name__ == "__main__":
    unittest.main()
