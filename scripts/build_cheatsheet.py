#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the K6 失分點速查卡 from curated data/cheatsheet/0X.json files.

Outputs: docs/02_考場策略/失分點速查卡_六科.md, src/data/cheatsheet.generated.js
Exit code is non-zero when validation fails.
"""
import glob
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "cheatsheet"
DASHBOARD = ROOT / "dashboard-data.js"
OUT_MD = ROOT / "docs" / "02_考場策略" / "失分點速查卡_六科.md"
OUT_JS = ROOT / "src" / "data" / "cheatsheet.generated.js"

CATEGORIES = [
    ("polarity_direction", "極性／方向／參考方向"),
    ("per_unit_base", "標么基準換算"),
    ("reading_figures_tables", "讀圖讀表與題幹條件"),
    ("approximation_convention", "近似口徑與教科書慣例"),
    ("units_rms_peak", "單位、有效值／峰值"),
    ("method_trap", "方法選擇陷阱"),
    ("calc_check", "計算與驗算習慣"),
]
CATEGORY_IDS = [c for c, _ in CATEGORIES]
SUBJECTS = {"01": "電路學", "02": "電子學", "03": "工程數學",
            "04": "電機機械", "05": "電力系統", "06": "工業配電"}
SUBJECT_DIRS = {"01": "01_電路學", "02": "02_電子學_含電力電子", "03": "03_工程數學",
                "04": "04_電機機械", "05": "05_電力系統", "06": "06_工業配電"}
MAX_ITEMS = 22
MAX_TEMPLATES = 6
MAX_TEXT = 80
MAX_SITUATION = 60
MAX_HOW = 120
QID_RE = re.compile(r"^EE-\d{3}-(0[1-6])-\d+$")


def dashboard_qids():
    text = DASHBOARD.read_text(encoding="utf-8")
    return set(re.findall(r'^    "(EE-\d{3}-\d{2}-\d+)",$', text, re.M))


def load_files():
    docs = {}
    for f in sorted(glob.glob(str(DATA_DIR / "0[1-6].json"))):
        docs[Path(f).stem] = json.loads(Path(f).read_text(encoding="utf-8"))
    return docs


def validate(docs, known_qids):
    errors = []

    def check_qids(where, qids):
        if not isinstance(qids, list) or not qids:
            errors.append(f"{where}: qids must be a non-empty list")
            return
        for q in qids:
            if q not in known_qids:
                errors.append(f"{where}: unknown qid {q}")

    for sid, doc in docs.items():
        if doc.get("subject") != sid:
            errors.append(f"{sid}.json: subject must be {sid!r}")
        items = doc.get("items", [])
        real = [it for it in items if not it.get("example")]
        if len(real) > MAX_ITEMS:
            errors.append(f"{sid}.json: {len(real)} items exceeds limit {MAX_ITEMS}")
        for i, it in enumerate(items):
            where = f"{sid}.json items[{i}]"
            if it.get("category") not in CATEGORY_IDS:
                errors.append(f"{where}: unknown category {it.get('category')!r}")
            text = it.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{where}: text missing")
            elif len(text) > MAX_TEXT:
                errors.append(f"{where}: text length {len(text)} exceeds {MAX_TEXT}")
            check_qids(where, it.get("qids"))
        tpls = doc.get("assumption_templates", [])
        if len(tpls) > MAX_TEMPLATES:
            errors.append(f"{sid}.json: {len(tpls)} assumption_templates exceeds limit {MAX_TEMPLATES}")
        for i, t in enumerate(tpls):
            where = f"{sid}.json assumption_templates[{i}]"
            for key, lim in (("situation", MAX_SITUATION), ("how_to_write", MAX_HOW)):
                v = t.get(key)
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"{where}: {key} missing")
                elif len(v) > lim:
                    errors.append(f"{where}: {key} length {len(v)} exceeds {lim}")
            check_qids(where, t.get("qids"))
    return errors


def note_link(qid):
    sid = QID_RE.match(qid).group(1)
    rel = f"../../02_題解/技師題解/{SUBJECT_DIRS[sid]}/canonical/{qid}.md"
    return f"[`{qid}`]({quote(rel, safe='/')})"


def curated(docs):
    """Return (subjects, templates) with example items removed."""
    subjects, templates = [], []
    for sid in sorted(docs):
        doc = docs[sid]
        cats = []
        for cid, label in CATEGORIES:
            its = [{"text": it["text"], "qids": it["qids"]} for it in doc.get("items", [])
                   if not it.get("example") and it["category"] == cid]
            if its:
                cats.append({"id": cid, "label": label, "items": its})
        if cats:
            subjects.append({"id": sid, "name": SUBJECTS[sid], "categories": cats})
        for t in doc.get("assumption_templates", []):
            templates.append({"subject": sid, "situation": t["situation"],
                              "how_to_write": t["how_to_write"], "qids": t["qids"]})
    return subjects, templates


def render_md(subjects, templates):
    out = ["# 上榜失分點速查卡（六科）", "",
           "> 由 `scripts/build_cheatsheet.py` 從 `data/cheatsheet/0X.json` 產生，請勿手改。每條都附題目連結，可追溯到 canonical 題解。", ""]
    if not subjects and not templates:
        out += ["尚無策展資料。", ""]
    for idx, s in enumerate(subjects):
        if idx:
            out += ['<div style="page-break-before: always"></div>', ""]
        out += [f"## {s['name']}", ""]
        for c in s["categories"]:
            out += [f"### {c['label']}", ""]
            for it in c["items"]:
                links = "　".join(note_link(q) for q in it["qids"])
                out.append(f"- {it['text']} {links}")
            out.append("")
    if templates:
        if subjects:
            out += ['<div style="page-break-before: always"></div>', ""]
        out += ["## 缺條件時怎麼寫假設", "",
                "| 科目 | 情境 | 考場寫法 | 題目 |", "| --- | --- | --- | --- |"]
        for t in templates:
            cell = lambda x: x.replace("|", "\\|")
            links = "　".join(note_link(q) for q in t["qids"])
            out.append(f"| {SUBJECTS[t['subject']]} | {cell(t['situation'])} | {cell(t['how_to_write'])} | {links} |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def render_js(subjects, templates, sources):
    data = {"categories": [{"id": c, "label": l} for c, l in CATEGORIES],
            "subjects": subjects,
            "assumption_templates": [dict(t, subject_name=SUBJECTS[t["subject"]]) for t in templates]}
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return ("// Generated by scripts/build_cheatsheet.py. Do not edit.\n"
            f"// Sources: {sources}\n"
            f"const CHEATSHEET_DATA = {body};\n")


def build(docs=None, known_qids=None):
    """Return (md, js, errors)."""
    docs = load_files() if docs is None else docs
    known = dashboard_qids() if known_qids is None else known_qids
    errors = validate(docs, known)
    if errors:
        return None, None, errors
    subjects, templates = curated(docs)
    sources = ", ".join(f"data/cheatsheet/{k}.json" for k in sorted(docs)) or "(none)"
    return render_md(subjects, templates), render_js(subjects, templates, sources), []


def main():
    md, js, errors = build()
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    OUT_MD.write_text(md, encoding="utf-8")
    OUT_JS.write_text(js, encoding="utf-8")
    docs = load_files()
    for sid in sorted(docs):
        real = [i for i in docs[sid].get("items", []) if not i.get("example")]
        print(f"{sid} {SUBJECTS[sid]}: {len(real)} items, {len(docs[sid].get('assumption_templates', []))} templates")
    print("wrote", OUT_MD.relative_to(ROOT), "and", OUT_JS.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
