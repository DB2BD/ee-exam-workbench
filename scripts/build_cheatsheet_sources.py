#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract K6 cheatsheet source material from canonical notes.

Outputs data/cheatsheet/sources.json with, per canonical note, the 「失分點」
bullets and 「條件與疑義」 text, plus the condition-question cards and the
命題疑點 table. Curation agents read this file to write data/cheatsheet/0X.json.
"""
import glob
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES_GLOB = str(ROOT / "📝 個人題解與錯題本" / "0*" / "canonical" / "EE-*.md")
CARDS_DOC = ROOT / "docs" / "上榜精確解答邊界_條件題處理.md"
AUDIT_DOC = ROOT / "reports" / "題幹稽核_2026-10-03.md"
OUT = ROOT / "data" / "cheatsheet" / "sources.json"
QID_RE = re.compile(r"EE-\d{3}-\d{2}-\d+")


def sort_key(qid):
    _, y, s, n = qid.split("-")
    return (int(s), int(y), int(n))


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


def section(text, title):
    m = re.search(r"^## " + re.escape(title) + r"[ \t]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip("\n") if m else ""


def bullets(body):
    items = []
    for ln in body.splitlines():
        if ln.startswith("- "):
            items.append(ln[2:].strip())
        elif ln.strip() and items:
            items[-1] += "\n" + ln.strip()
    return items


def extract_notes():
    notes = []
    for f in glob.glob(NOTES_GLOB):
        p = Path(f)
        text = p.read_text(encoding="utf-8")
        fm = frontmatter(text)
        qid = fm.get("qid") or p.stem
        notes.append({
            "qid": qid,
            "subject_id": p.parent.parent.name.split("_")[0],
            "subject": fm.get("subject", ""),
            "year": int(fm.get("year", 0) or 0),
            "chapter": fm.get("chapter", ""),
            "audit_status": fm.get("audit_status", ""),
            "pitfalls": bullets(section(text, "失分點")),
            "conditions": section(text, "條件與疑義").strip(),
        })
    notes.sort(key=lambda n: sort_key(n["qid"]))
    return notes


def table_rows(text):
    for ln in text.splitlines():
        if ln.startswith("|"):
            yield ln


def extract_cards():
    cards = []
    for ln in table_rows(CARDS_DOC.read_text(encoding="utf-8")):
        m = re.match(r"^\| \[`(EE-\d{3}-\d{2}-\d+)`\]\([^)]*\) \| (.*) \|\s*$", ln)
        if not m:
            continue
        parts = m.group(2).split(" | ")
        gap, card = parts[0], " | ".join(parts[1:])
        cards.append({"qid": m.group(1), "gap": gap.strip(), "card": card.strip()})
    return cards


def extract_doubts():
    text = AUDIT_DOC.read_text(encoding="utf-8")
    m = re.search(r"^## 命題疑點[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    rows = []
    for ln in table_rows(m.group(1) if m else ""):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        if len(cells) >= 2 and QID_RE.fullmatch(cells[0]):
            rows.append({"qid": cells[0], "doubt": " | ".join(cells[1:])})
    return rows


def build():
    return OrderedDict([
        ("generated_by", "scripts/build_cheatsheet_sources.py"),
        ("notes", extract_notes()),
        ("condition_cards", extract_cards()),
        ("question_doubts", extract_doubts()),
    ])


def render(doc):
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def main():
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(doc), encoding="utf-8")
    stats = {}
    for n in doc["notes"]:
        s = stats.setdefault(n["subject_id"] + " " + n["subject"], [0, 0, 0, 0])
        s[0] += 1
        s[1] += len(n["pitfalls"])
        s[2] += 1 if n["conditions"] else 0
        s[3] += 0 if n["pitfalls"] else 1
    print("subject  notes  pitfalls  with-conditions  no-pitfall-section")
    for k in sorted(stats):
        print(k, *stats[k])
    print(f"total notes {len(doc['notes'])}, condition cards {len(doc['condition_cards'])}, "
          f"question doubts {len(doc['question_doubts'])}")
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
