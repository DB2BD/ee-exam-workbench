# -*- coding: utf-8 -*-
"""Schema helpers for the static PE/GK question bundles.

The bundles intentionally remain JSON-compatible JavaScript for offline use.
This module validates their positional compatibility contract while exposing a
single, named-field view for future domain modules.
"""

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Dict, List


PE_SUBJECTS = {"01", "02", "03", "04", "05", "06"}
GK_SUBJECTS = {"01", "02", "03", "04", "05"}
VALID_STATUSES = {"verified", "in_progress", "pending", "ambiguous", "unavailable"}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    count: int
    errors: List[str]


def load_questions_from_bundle(path: Path, end_marker: str = "") -> List[list]:
    """Extract the first JSON array following ``questions:`` from a bundle."""

    text = Path(path).read_text(encoding="utf-8")
    # Anchor at a property line so comments such as "Total ... questions:"
    # cannot be mistaken for the data field.
    match = re.search(r"^\s*questions\s*:\s*", text, re.MULTILINE)
    if not match:
        raise ValueError(f"questions array not found in {path}")
    payload = text[match.end():].lstrip()
    questions, _ = json.JSONDecoder().raw_decode(payload)
    if not isinstance(questions, list):
        raise ValueError(f"questions is not an array in {path}")
    return questions


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_source_pages(value: Any) -> bool:
    """Validate crop-manifest page descriptors emitted by the national compiler."""

    if not isinstance(value, list):
        return False
    return all(
        isinstance(item, dict)
        and _is_int(item.get("page"))
        and isinstance(item.get("crop_rect"), list)
        and len(item["crop_rect"]) == 4
        and all(isinstance(coord, (int, float)) for coord in item["crop_rect"])
        for item in value
    )


def validate_question_records(records: List[list], exam_family: str) -> ValidationResult:
    """Validate PE/GK positional records at the bundle boundary."""

    errors: List[str] = []
    expected_subjects = PE_SUBJECTS if exam_family == "PE" else GK_SUBJECTS
    prefix = "EE-" if exam_family == "PE" else "GK-"
    minimum_length = 12 if exam_family == "PE" else 18

    if not isinstance(records, list):
        return ValidationResult(False, 0, ["records must be a list"])

    seen = set()
    for index, record in enumerate(records):
        label = f"record[{index}]"
        if not isinstance(record, list) or len(record) < minimum_length:
            errors.append(f"{label}: expected list with at least {minimum_length} fields")
            continue

        qid, sid, year, number, topic, tags = record[:6]
        if not isinstance(qid, str) or not qid.startswith(prefix):
            errors.append(f"{label}: invalid {exam_family} question id")
        elif qid in seen:
            errors.append(f"{label}: duplicate question id {qid}")
        else:
            seen.add(qid)
        if sid not in expected_subjects:
            errors.append(f"{label}: unknown subject {sid!r}")
        if not _is_int(year) or year < 100:
            errors.append(f"{label}: invalid year")
        if not _is_int(number) or number < 1:
            errors.append(f"{label}: invalid question number")
        if not isinstance(topic, str) or not topic.strip():
            errors.append(f"{label}: topic must be non-empty text")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append(f"{label}: tags must be a list of strings")

        if not isinstance(record[6], str) or not isinstance(record[7], str):
            errors.append(f"{label}: solution/source links must be strings")
        if not _is_int(record[8]) or not 1 <= record[8] <= 5:
            errors.append(f"{label}: difficulty must be an integer from 1 to 5")
        if record[9] not in VALID_STATUSES:
            errors.append(f"{label}: invalid solution status {record[9]!r}")
        if not isinstance(record[10], list) or not all(isinstance(tag, str) for tag in record[10]):
            errors.append(f"{label}: formula tags must be a list of strings")
        if not isinstance(record[11], bool):
            errors.append(f"{label}: dedicated-solution flag must be boolean")

        if exam_family == "GK":
            if not isinstance(record[12], str) or not record[12]:
                errors.append(f"{label}: national category id is required")
            if not isinstance(record[13], str):
                errors.append(f"{label}: related PE id must be a string")
            if not isinstance(record[14], str):
                errors.append(f"{label}: question crop path must be a string")
            if not isinstance(record[15], list) or not all(isinstance(item, str) for item in record[15]):
                errors.append(f"{label}: figure crops must be a list of strings")
            if not _valid_source_pages(record[16]):
                errors.append(f"{label}: source pages must be crop page descriptors")
            if not isinstance(record[17], str):
                errors.append(f"{label}: source PDF hash must be a string")

    return ValidationResult(not errors, len(records), errors)


def question_record_view(record: list, exam_family: str) -> Dict[str, Any]:
    """Convert a legacy tuple into the stable named-field domain view."""

    if exam_family == "GK" and len(record) < 18:
        raise ValueError("GK record is missing provenance fields")
    view: Dict[str, Any] = {
        "id": record[0],
        "examFamily": exam_family,
        "subjectId": record[1],
        "year": record[2],
        "number": record[3],
        "stem": record[4],
        "tags": record[5],
        "solutionLink": record[6],
        "sourceLink": record[7],
        "difficulty": record[8],
        "solutionStatus": record[9],
        "formulaTags": record[10],
        "hasDedicatedSolution": record[11],
    }
    if exam_family == "GK":
        view.update({
            "categoryId": record[12],
            "relatedPEId": record[13],
            "questionCrop": record[14],
            "figureCrops": record[15],
            "sourcePages": record[16],
            "sourcePdfSha256": record[17],
        })
    return view
