"""Official GK PDF inventory and provenance-manifest contract tests."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
import build_master_national_subject_files as builder


class OfficialPDFManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_entries()

    def test_manifest_covers_all_25_year_subject_slots(self):
        expected_subjects = {"電路學", "電子學", "工程數學", "電機機械", "電力系統"}
        expected_years = set(range(110, 115))
        keys = {(entry["year"], entry["subject"]) for entry in self.entries}
        self.assertEqual(len(self.entries), 25)
        self.assertEqual(keys, {(year, subject) for year in expected_years for subject in expected_subjects})

        downloaded = [entry for entry in self.entries if entry["status"] == "downloaded"]
        unavailable = [
            entry for entry in self.entries
            if entry["status"] == "not_available_in_selected_exam_class"
        ]
        self.assertEqual(len(downloaded), 23)
        self.assertEqual(
            {(entry["year"], entry["subject"]) for entry in unavailable},
            {(113, "工程數學"), (114, "工程數學")},
        )
        for entry in unavailable:
            self.assertIsNone(entry["official_url"])
            self.assertNotIn("target_path", entry)
            self.assertNotIn("sha256", entry)

    def test_directory_and_every_pdf_copy_match_the_manifest_bidirectionally(self):
        builder.verify_pdf_directory(self.entries)
        official = [entry for entry in self.entries if entry["status"] == "downloaded"]
        expected_names = {Path(entry["target_path"]).name for entry in official}
        actual_names = {
            path.name
            for path in builder.PDF_DIRECTORY.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        }
        self.assertEqual(actual_names, expected_names)
        for entry in official:
            target = builder.WORKSPACE / entry["target_path"]
            directory_copy = builder.PDF_DIRECTORY / target.name
            self.assertEqual(builder.sha256(target), entry["sha256"], target)
            self.assertEqual(builder.sha256(directory_copy), entry["sha256"], directory_copy)


if __name__ == "__main__":
    unittest.main()
