"""The published GK bundle must never expose quarantined legacy content."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "import compile_national_exams as c; c.generate_bundle_js()"


class NationalBundleUnverifiedSourceTests(unittest.TestCase):
    def test_quarantined_markdown_and_images_are_excluded_but_official_assets_remain(self):
        with tempfile.TemporaryDirectory(prefix="national-bundle-quarantine-") as temporary:
            fixture = Path(temporary)
            scripts = fixture / "scripts"
            scripts.mkdir()
            shutil.copy2(ROOT / "scripts/compile_national_exams.py", scripts)
            shutil.copy2(ROOT / "scripts/difficulty_evaluator.py", scripts)

            source_root = fixture / "04_國考同級題庫/03_工程數學"
            solution_root = fixture / "02_題解/國考同級題解/03_工程數學"
            quarantined_source = source_root / "_unverified_pre_moex"
            quarantined_solution = solution_root / "_unverified_pre_moex"
            for directory in (quarantined_source, quarantined_solution):
                directory.mkdir(parents=True)

            (quarantined_source / "fabricated.md").write_text(
                "DO NOT PUBLISH fabricated source", encoding="utf-8"
            )
            (quarantined_solution / "fabricated-solution.md").write_text(
                "DO NOT PUBLISH fabricated solution", encoding="utf-8"
            )
            (quarantined_source / "quarantined.png").write_bytes(b"fake question image")
            (quarantined_solution / "quarantined-answer.png").write_bytes(b"fake solution image")

            (source_root / "official.md").write_text("official source", encoding="utf-8")
            (solution_root / "reviewed.md").write_text("reviewed solution", encoding="utf-8")
            (source_root / "images").mkdir()
            (solution_root / "images").mkdir()
            (source_root / "images" / "official.png").write_bytes(b"official question image")
            (solution_root / "images" / "reviewed.png").write_bytes(b"reviewed solution image")
            (source_root / "legacy-source-alias.md").symlink_to(
                quarantined_source / "fabricated.md"
            )
            (solution_root / "legacy-solution-alias.md").symlink_to(
                quarantined_solution / "fabricated-solution.md"
            )
            (source_root / "images" / "legacy-question-alias.png").symlink_to(
                quarantined_source / "quarantined.png"
            )
            (solution_root / "images" / "legacy-answer-alias.png").symlink_to(
                quarantined_solution / "quarantined-answer.png"
            )

            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(scripts)
            completed = subprocess.run(
                [sys.executable, "-c", SCRIPT],
                cwd=scripts,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            bundle_path = fixture / "national-solutions-bundle.js"
            bundle_text = bundle_path.read_text(encoding="utf-8")
            match = re.fullmatch(
                r"const NATIONAL_BUNDLED_MD = (.*);\n"
                r"const NATIONAL_IMAGE_MAP = (.*);\n",
                bundle_text,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(match, bundle_text[:300])
            bundled_markdown = json.loads(match.group(1))
            image_map = json.loads(match.group(2))

            self.assertIn("04_國考同級題庫/03_工程數學/official.md", bundled_markdown)
            self.assertIn("02_題解/國考同級題解/03_工程數學/reviewed.md", bundled_markdown)
            self.assertIn("official source", bundled_markdown.values())
            self.assertIn("reviewed solution", bundled_markdown.values())
            self.assertIn("official.png", image_map)
            self.assertIn("reviewed.png", image_map)
            self.assertFalse(
                any("_unverified_pre_moex" in path for path in bundled_markdown),
                bundled_markdown.keys(),
            )
            self.assertFalse(
                any("_unverified_pre_moex" in path for path in image_map),
                image_map.keys(),
            )
            self.assertFalse(
                any("_unverified_pre_moex" in path for path in image_map.values()),
                image_map.values(),
            )
            self.assertNotIn("DO NOT PUBLISH", bundle_text)
            self.assertNotIn("quarantined.png", image_map)
            self.assertNotIn("quarantined-answer.png", image_map)
            self.assertFalse(
                any("legacy-" in path for path in bundled_markdown),
                bundled_markdown.keys(),
            )
            self.assertFalse(any("legacy-" in path for path in image_map), image_map.keys())
            self.assertFalse(
                any("legacy-" in path for path in image_map.values()),
                image_map.values(),
            )


if __name__ == "__main__":
    unittest.main()
