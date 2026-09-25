"""Official waveform sampling and chapter boundary for 114 machinery Q3/Q5."""

import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "📝 個人題解與錯題本/04_電機機械/canonical"


class TestRotatingField114(unittest.TestCase):
    def test_official_odd_tick_samples_are_diagonal_not_axis_aligned(self):
        note = (NOTES / "EE-114-04-3.md").read_text(encoding="utf-8")
        standard = note.split("## 考場標準作答", 1)[1].split("## 得分點拆解", 1)[0]
        self.assertIn("![官方題目裁切圖]", note)
        for angle in (45, 135, 225, 315):
            self.assertIn(f"{angle}^\\circ", standard)
        self.assertNotIn("-Phi_m", note)
        for tick, expected_angle in ((1, 45), (3, 135), (5, 225), (7, 315)):
            theta = tick * math.pi / 4
            main_current = -math.cos(theta)
            auxiliary_current = math.sin(theta)
            flux_x, flux_y = -main_current, auxiliary_current
            with self.subTest(tick=tick):
                self.assertAlmostEqual(abs(main_current), 1 / math.sqrt(2))
                self.assertAlmostEqual(abs(auxiliary_current), 1 / math.sqrt(2))
                self.assertAlmostEqual(math.hypot(flux_x, flux_y), 1)
                self.assertAlmostEqual(math.degrees(math.atan2(flux_y, flux_x)) % 360, expected_angle)
                self.assertAlmostEqual(math.degrees(math.atan2(-flux_y, flux_x)) % 360,
                                       (-expected_angle) % 360)

    def test_different_machinery_topics_are_not_equivalent_circuits(self):
        field = (NOTES / "EE-114-04-3.md").read_text(encoding="utf-8")
        reluctance = (NOTES / "EE-114-04-5.md").read_text(encoding="utf-8")
        self.assertIn("chapter: 單相感應電動機二相旋轉磁場", field)
        self.assertIn("chapter: 磁阻電動機磁阻—位置轉矩", reluctance)


if __name__ == "__main__":
    unittest.main()
