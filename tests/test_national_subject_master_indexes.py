from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
import hashlib
import re
from urllib.parse import urlparse
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_master_national_subject_files as builder


ROOT = Path(__file__).resolve().parents[1]


class BuilderImportSafetyTests(unittest.TestCase):
    def test_import_does_not_run_legacy_exam_writer_in_isolated_fixture(self):
        """Import the real builder in a disposable copy; no annual pages may appear."""
        with tempfile.TemporaryDirectory(prefix="gk-builder-import-") as temporary:
            fixture = Path(temporary)
            scripts = fixture / "scripts"
            scripts.mkdir()
            shutil.copy2(ROOT / "scripts/build_master_national_subject_files.py", scripts)
            shutil.copy2(ROOT / "scripts/generate_all_national_exams.py", scripts)

            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); import build_master_national_subject_files",
                ],
                cwd=scripts,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            generated = list(
                (fixture / "04_國考同級題庫").glob("*/GK_*年_*.md")
            )
            self.assertEqual(generated, [], "builder import invoked legacy annual writer")


class MasterIndexIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_entries()

    def test_manifest_and_official_pdf_directory_are_bidirectionally_consistent(self):
        downloaded = [entry for entry in self.entries if entry["status"] == "downloaded"]
        unavailable = [
            entry for entry in self.entries
            if entry["status"] == "not_available_in_selected_exam_class"
        ]
        self.assertEqual(len(self.entries), 25)
        self.assertEqual(len(downloaded), 23)
        self.assertEqual(len(unavailable), 2)
        builder.verify_pdf_directory(self.entries)

    def test_every_official_annual_page_is_bound_to_its_manifest_pdf(self):
        builder.verify_annual_source_pages(self.entries)
        for entry in self.entries:
            if entry["status"] != "downloaded":
                continue
            subject_dir = builder.SUBJECT_DIRS[entry["subject"]]
            source = (
                builder.MASTER_DIRECTORY
                / subject_dir
                / f"GK_{entry['year']}年_{entry['subject']}.md"
            )
            self.assertTrue(source.is_file(), source)
            metadata = builder.read_front_matter(source)
            self.assertEqual(metadata.get("source_pdf_sha256"), entry["sha256"], source)
            self.assertEqual(metadata.get("official_url"), entry["official_url"], source)
            content = builder.render_master(entry["subject"], self.entries)
            row = next(
                line for line in content.splitlines()
                if line.startswith(f"| {entry['year']} |")
            )
            self.assertIn("[官方年度原題頁]", row)

    def test_missing_official_annual_source_page_fails_closed(self):
        entry = next(item for item in self.entries if item["status"] == "downloaded")
        with tempfile.TemporaryDirectory(prefix="gk-missing-annual-source-") as temporary:
            with mock.patch.object(builder, "MASTER_DIRECTORY", Path(temporary)):
                with self.assertRaisesRegex(ValueError, "Missing official annual source page"):
                    builder.verify_annual_source_pages([entry])

    def test_master_index_links_resolve_from_the_index_directory(self):
        content = builder.render_master("電路學", self.entries)
        for label in ("官方年度原題頁", "MOEX PDF"):
            relative = re.search(rf"\[{label}\]\(([^)]+)\)", content).group(1)
            self.assertTrue((builder.MASTER_DIRECTORY / relative).resolve().is_file(), relative)

        solution_link = re.search(r"\[repo 標記部分驗證\]\(([^)]+)\)", content).group(1)
        self.assertTrue(
            (builder.MASTER_DIRECTORY / solution_link).resolve().is_file(),
            solution_link,
        )

    def test_all_local_links_in_all_five_indexes_resolve(self):
        for path, content in builder.expected_outputs(self.entries).items():
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if urlparse(target).scheme:
                    continue
                with self.subTest(index=path.name, target=target):
                    self.assertTrue((path.parent / target).resolve().is_file(), target)

    def test_matching_solution_pdf_hash_keeps_status_when_identity_metadata_is_incomplete(self):
        content = builder.render_master("工程數學", self.entries)
        row = next(line for line in content.splitlines() if line.startswith("| 112 |"))
        self.assertIn("repo 標記已驗證", row)
        self.assertIn("PDF 雜湊吻合；來源 metadata 待補", row)
        relative = re.search(r"\[repo 標記已驗證[^]]*\]\(([^)]+)\)", row).group(1)
        self.assertTrue((builder.MASTER_DIRECTORY / relative).resolve().is_file(), relative)

    def test_unavailable_selected_class_slots_are_not_linked_as_official_exams(self):
        content = builder.render_master("工程數學", self.entries)
        self.assertIn("所選類科官方原題不可用", content)
        self.assertIn("所選類科未提供官方來源", content)
        self.assertNotIn("GK_113年_工程數學.md", content)
        self.assertNotIn("GK_114年_工程數學.md", content)
        for year in (113, 114):
            row = next(line for line in content.splitlines() if line.startswith(f"| {year} |"))
            self.assertNotIn("[MOEX PDF]", row)

    def test_five_indexes_represent_every_year_subject_slot_exactly_once(self):
        outputs = builder.expected_outputs(self.entries)
        self.assertEqual(len(outputs), 5)
        slots = []
        unavailable_rows = []
        for path, content in outputs.items():
            rows = [line for line in content.splitlines() if re.match(r"\| \d{3} \|", line)]
            self.assertEqual(len(rows), 5, path)
            slots.extend((path.name, int(row.split("|", 2)[1].strip())) for row in rows)
            unavailable_rows.extend(line for line in rows if "所選類科官方原題不可用" in line)
        self.assertEqual(len(slots), 25)
        self.assertEqual(len(unavailable_rows), 2)

    def test_pdf_directory_check_rejects_unmanifested_files(self):
        with tempfile.TemporaryDirectory(prefix="gk-pdf-inventory-") as temporary:
            root = Path(temporary)
            pdf_dir = root / "official"
            pdf_dir.mkdir()
            payload = b"official pdf fixture"
            (pdf_dir / "official.pdf").write_bytes(payload)
            target = root / "official.pdf"
            target.write_bytes(payload)
            entry = {
                "year": 114,
                "subject": "電路學",
                "status": "downloaded",
                "target_path": "official.pdf",
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            with mock.patch.object(builder, "PDF_DIRECTORY", pdf_dir), mock.patch.object(
                builder, "WORKSPACE", root
            ):
                builder.verify_pdf_directory([entry])
                (pdf_dir / "official.pdf").write_bytes(b"mismatched official-directory copy")
                with self.assertRaisesRegex(ValueError, "Official PDF directory SHA-256 mismatch"):
                    builder.verify_pdf_directory([entry])
                (pdf_dir / "official.pdf").write_bytes(payload)
                (pdf_dir / "unmanifested.PDF").write_bytes(b"extra")
                with self.assertRaisesRegex(ValueError, "directory mismatch"):
                    builder.verify_pdf_directory([entry])


if __name__ == "__main__":
    unittest.main()
