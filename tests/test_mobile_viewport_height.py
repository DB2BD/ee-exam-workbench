"""Phone overlays must size to the dynamic viewport so iOS Safari's toolbar never hides their bottom edge."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MobileViewportHeightTests(unittest.TestCase):
    def test_solution_modal_uses_dynamic_viewport_height(self):
        css = (ROOT / "src/styles/modal.css").read_text(encoding="utf-8")
        block = re.search(r"#solution-modal\s*\{(.*?)\}", css, re.S).group(1)
        self.assertIn("100dvh", block)
        # dvh must come after the vh fallback so supporting browsers use it.
        self.assertGreater(block.index("100dvh"), block.index("100vh"))

    def test_phone_modal_container_fills_the_overlay(self):
        css = (ROOT / "src/styles/modal.css").read_text(encoding="utf-8")
        phone = css[css.index("@media (max-width: 760px)"):]
        self.assertRegex(phone, r"#solution-modal\s*\{[^}]*align-items:\s*stretch")
        self.assertRegex(phone, r"\.modal-container\s*\{[^}]*height:\s*100dvh")


if __name__ == "__main__":
    unittest.main()
