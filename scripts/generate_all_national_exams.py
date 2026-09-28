# -*- coding: utf-8 -*-
"""Retired synthetic GK generator.

The previous embedded EXAM_DATA transcription was not a trustworthy source
for official questions and has been withdrawn. Use the MOEX manifest, official
PDFs, and ``build_master_national_subject_files.py`` instead.

Importing this compatibility module is side-effect free. The legacy command
intentionally fails closed and cannot write annual question pages.
"""

SUBJECT_DIRS = {
    "01": "01_電路學",
    "02": "02_電子學_含電力電子",
    "03": "03_工程數學",
    "04": "04_電機機械",
    "05": "05_電力系統",
}
EXAM_DATA: dict = {}


def main() -> int:
    raise SystemExit(
        "Retired: synthetic GK exam text was withdrawn. "
        "Use official MOEX sources and scripts/build_master_national_subject_files.py."
    )


if __name__ == "__main__":
    main()
