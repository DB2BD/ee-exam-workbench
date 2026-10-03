#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build learner-facing answer corrections (K1) from wave reports.

Sources: reports/題解精確化_wave-*.md "## 答案更正" tables (user-confirmed only).
Cross-check: .agents/results/WAVE-*/*.json records with answer_change == corrected.
Outputs: data/answer-corrections.json, src/data/answerCorrections.generated.js
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QID_RE = re.compile(r"^EE-\d{3}-\d{2}-\d+$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
OUT_JSON = ROOT / "data" / "answer-corrections.json"
OUT_JS = ROOT / "src" / "data" / "answerCorrections.generated.js"


class ParseError(Exception):
    pass


def report_paths():
    def key(p):
        return int(re.search(r"wave-(\d+)", p.name).group(1))
    return sorted((Path(p) for p in glob.glob(str(ROOT / "reports" / "題解精確化_wave-*.md"))
                   if re.search(r"wave-(\d+)\.md$", p)), key=key)


def sort_key(qid):
    _, y, s, n = qid.split("-")
    return (-int(y), int(s), int(n))


def parse_report(path):
    """Return list of dicts: qid, old, new, reason, pending, carryover."""
    wave = int(re.search(r"wave-(\d+)", path.name).group(1))
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # decision date: first date on a summary line mentioning 答案更正 and 同意
    date = None
    for ln in lines:
        if "答案更正" in ln and "同意" in ln and DATE_RE.search(ln):
            date = DATE_RE.search(ln).group(0)
            break
    if not date:
        raise ParseError(f"{path.name}: no decision date found for 答案更正")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == "## 答案更正")
    except StopIteration:
        raise ParseError(f"{path.name}: missing '## 答案更正'")
    rows = []
    header = None
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s.startswith("## "):
            break
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if header[:3] == ["題號", "舊答案", "新答案"] and len(cells) >= 4:
            qcell, old, new, reason = cells[0], cells[1], cells[2], cells[3]
        elif header[:2] == ["題號", "變更"] and len(cells) >= 3:
            qcell, change, reason = cells[0], cells[1], cells[2]
            if " → " in change:
                old, new = change.split(" → ", 1)
            else:
                old, new = "", change
        else:
            raise ParseError(f"{path.name}: unknown table header {header}")
        pending = "待確認" in qcell
        carry = bool(re.search(r"Wave\s*\d", qcell))
        for raw in re.split(r"[、,，]", qcell):
            qid = re.sub(r"[（(].*?[）)]", "", raw).strip()
            if not QID_RE.match(qid):
                raise ParseError(f"{path.name}: bad QID {raw!r}")
            rows.append({"qid": qid, "old": old.strip(), "new": new.strip(),
                         "reason": reason.strip(), "pending": pending,
                         "carryover": carry})
    if not rows:
        raise ParseError(f"{path.name}: no rows parsed")
    return wave, date, rows


def dashboard_qids():
    txt = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
    return set(re.findall(r'"(EE-\d{3}-\d{2}-\d+)"', txt))


def json_corrected():
    found = set()
    for f in sorted(glob.glob(str(ROOT / ".agents" / "results" / "WAVE-*" / "*.json"))):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(data, list):
            for r in data:
                if isinstance(r, dict) and r.get("answer_change") == "corrected" and r.get("qid"):
                    found.add(r["qid"])
    return found


def build():
    paths = report_paths()
    if not paths:
        raise ParseError("no wave reports found")
    records = {}
    pending = {}
    table_qids = set()
    for p in paths:
        wave, date, rows = parse_report(p)
        for r in rows:
            q = r["qid"]
            table_qids.add(q)
            if r["pending"]:
                pending[q] = (wave, r)
                continue
            if q in records or q in pending:
                # carryover / confirmation of an earlier row: keep earlier
                # specific old/new/reason, take the confirming decision date.
                base = records.get(q)
                if base is None:
                    w0, r0 = pending.pop(q)
                    base = {"qid": q, "wave": w0, "old_answer": r0["old"],
                            "new_answer": r0["new"], "reason": r0["reason"]}
                base["decided_at"] = date
                records[q] = base
                continue
            records[q] = {"qid": q, "wave": wave, "old_answer": r["old"],
                          "new_answer": r["new"], "reason": r["reason"],
                          "decided_at": date}
    warnings = [f"WARNING: {q} 待確認 and never confirmed; not emitted" for q in pending]
    known = dashboard_qids()
    bad = sorted(q for q in records if q not in known)
    if bad:
        raise ParseError(f"QIDs missing from dashboard-data.js: {bad}")
    jc = json_corrected()
    for q in sorted(table_qids - jc, key=sort_key):
        warnings.append(f"WARNING: {q} in report table but no worker JSON answer_change=corrected")
    unreported = sorted(jc - table_qids, key=sort_key)
    out = sorted(records.values(), key=lambda r: sort_key(r["qid"]))
    doc = {"schema_version": 1,
           "generated_from": [str(p.relative_to(ROOT)) for p in paths],
           "corrections": out, "unreported": unreported}
    return doc, warnings


def render_js(doc):
    mapping = {c["qid"]: {k: v for k, v in c.items() if k != "qid"}
               for c in doc["corrections"]}
    body = json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=False)
    return ("// Generated by scripts/build_answer_corrections.py. Do not edit.\n"
            "// Sources: " + ", ".join(doc["generated_from"]) + "\n"
            f"// corrections: {len(mapping)}\n"
            f"const ANSWER_CORRECTIONS = {body};\n")


def main():
    try:
        doc, warnings = build()
    except ParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_JS.write_text(render_js(doc), encoding="utf-8")
    for w in warnings:
        print(w)
    print(f"corrections: {len(doc['corrections'])}")
    print(f"unreported: {' '.join(doc['unreported']) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
