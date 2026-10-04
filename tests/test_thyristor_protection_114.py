"""Ensure 114 thyristor protection does not assign the full source twice."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "02_題解/技師題解/02_電子學_含電力電子/canonical/EE-114-02-4.md"


class TestThyristorProtection114(unittest.TestCase):
    def test_blocking_and_conducting_states_obey_kvl(self):
        note = NOTE.read_text(encoding="utf-8")
        self.assertIn("$V_S=V_T+V_L$", note)
        self.assertIn("$V_T\\approx V_S$", note)
        self.assertIn("$V_L\\approx0$", note)
        self.assertIn("不能同時各取 $V_S$", note)
        self.assertNotIn("$V_S$ 突然加到閘流體 $T$ 與負載", note)


if __name__ == "__main__":
    unittest.main()
