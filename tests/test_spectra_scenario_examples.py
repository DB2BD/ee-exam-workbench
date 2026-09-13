# -*- coding: utf-8 -*-
"""Ensure every in-scope Spectra scenario has concrete example evidence."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_ROOTS = [
    ROOT / "docs/spectra/changes/problem-driven-obsidian-knowledge-graph/specs",
    ROOT / "docs/spectra/changes/problem-driven-obsidian-warning-remediation/specs",
]


class TestSpectraScenarioExamples(unittest.TestCase):
    def test_every_scenario_has_an_example_block(self):
        missing = []
        for root in SPEC_ROOTS:
            for path in sorted(root.glob("*/spec.md")):
                content = path.read_text(encoding="utf-8")
                blocks = re.findall(r"#### Scenario:.*?(?=\n#### Scenario:|\Z)", content, flags=re.DOTALL)
                for block in blocks:
                    if "##### Example:" not in block:
                        missing.append(str(path.relative_to(ROOT)) + ": " + block.splitlines()[0])
        self.assertEqual(missing, [], "scenario examples missing:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
