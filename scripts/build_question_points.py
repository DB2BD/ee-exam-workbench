#!/usr/bin/env python3
"""Build per-question score data (配分) for the PE question bank.

Sources, priority order:
  1. data/question-points.overrides.json  (manual; {"QID": {"total":N,"parts":[{"label":..,"points":..}],"reason":".."}})
  2. sub-question scores parsed from the official stem (dashboard-data.js)
       - per-part "（10 分）" or header "（每小題 10 分，共 20 分）"
  3. whole-question score in the stem (e.g. "（25 分）", "（各 10 分，共 20 分）")
  4. paper default: "每題 N 分" read from the paper PDF header (PyMuPDF)
Validation (exit 1): every QID present; each paper (year+subject) totals 100;
parts sum == total when parts present.

Outputs: data/question-points.json, src/data/questionPoints.generated.js
Usage: python3 scripts/build_question_points.py [--check]
"""
import collections
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES = ROOT / "data" / "question-points.overrides.json"
OUT_JSON = ROOT / "data" / "question-points.json"
OUT_JS = ROOT / "src" / "data" / "questionPoints.generated.js"
CN = "一二三四五六七八九十"
EXPECTED = 323

NODE_DUMP = r"""
const fs=require("fs"),vm=require("vm");
const c={};vm.runInNewContext(fs.readFileSync("dashboard-data.js","utf8")+";this.D=DB_DATA",c);
process.stdout.write(JSON.stringify(c.D.questions.map(q=>[q[0],q[1],q[2],q[3],q[4]])));
"""


def load_questions():
    r = subprocess.run(["node", "-"], input=NODE_DUMP, capture_output=True,
                       text=True, cwd=ROOT, check=True)
    return json.loads(r.stdout)


def _val(s):
    return CN.index(s[0]) + 1 if s[0] in CN else int(s)


def find_labels(t):
    """Sequential sub-question labels (一)(二).. or (1)(2).. ; line-start preferred."""
    pats = [r'(?m)^[\s*]*\*{0,2}\s*[（(]([一二三四五六七八九十]+|\d+)[）)]',
            r'[（(]([一二三四五六七八九十]+|\d+)[）)]']
    for p in pats:
        out, exp = [], 1
        for m in re.finditer(p, t):
            if _val(m.group(1)) == exp:
                out.append((m.start(), "（%s）" % m.group(1)))
                exp += 1
        if len(out) >= 2:
            return out
    return []


SC = re.compile(r'[（(][^（()）]*?(\d+)\s*分\s*[）)]')


def parse_stem(t):
    """-> (total|None, [(label,points)], kind) kind in parts/whole/none"""
    labs = find_labels(t)
    h = re.search(r'每小題\s*(\d+)\s*分[，,]\s*共\s*(\d+)\s*分', t)
    if h:
        a, M = int(h[1]), int(h[2])
        if labs and a * len(labs) == M:
            return M, [(l, a) for _, l in labs], "parts"
        return M, [], "whole"
    h = re.search(r'各\s*\d+\s*分[，,]\s*共\s*(\d+)\s*分', t)
    if h:
        return int(h[1]), [], "whole"
    toks = [(m.start(), int(m.group(1))) for m in SC.finditer(t)]
    if labs and toks:
        bounds = [p for p, _ in labs] + [len(t)]
        segs = [[s for p, s in toks if bounds[i] <= p < bounds[i + 1]]
                for i in range(len(labs))]
        if all(len(s) == 1 for s in segs):
            return None, [(labs[i][1], segs[i][0]) for i in range(len(labs))], "parts"
    if toks:
        return sum(s for _, s in toks), [], "whole"
    return None, [], "none"


def paper_defaults():
    """(year, subject-name-fragment) -> per-question points from PDF header, best effort."""
    out = {}
    try:
        import fitz
    except ImportError:
        return out
    for pdf in glob.glob(str(ROOT / "依年度分類" / "*年" / "*.pdf")):
        m = re.match(r"(\d+)年_電機工程技師_(.+)\.pdf", Path(pdf).name)
        if not m:
            continue
        try:
            txt = fitz.open(pdf)[0].get_text()
        except Exception:
            continue
        h = re.search(r'每題\s*(\d+)\s*分', txt)
        if h:
            out[(int(m.group(1)), m.group(2))] = int(h.group(1))
    return out


SUBJ = {"01": "電路學", "02": "電子學", "03": "工程數學", "04": "電機機械",
        "05": "電力系統", "06": "工業配電"}


def build():
    qs = load_questions()
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    pdefs = None
    res, src, errors = {}, {}, []
    for qid, subj, year, no, stem in qs:
        if qid in overrides:
            o = overrides[qid]
            parts = [{"label": p["label"], "points": int(p["points"])} for p in o.get("parts", [])]
            total = int(o["total"]) if "total" in o else sum(p["points"] for p in parts)
            res[qid], src[qid] = {"total": total, "parts": parts}, "override"
            continue
        total, parts, kind = parse_stem(stem)
        if kind == "none":
            if pdefs is None:
                pdefs = paper_defaults()
            d = next((v for (y, n), v in pdefs.items()
                      if y == year and n.startswith(SUBJ[subj])), None)
            if d is None:
                errors.append("%s: no score in stem and no paper default (add override)" % qid)
                continue
            res[qid], src[qid] = {"total": d, "parts": []}, "paper_default"
            continue
        plist = [{"label": l, "points": p} for l, p in parts]
        res[qid] = {"total": total if total is not None else sum(p["points"] for p in plist),
                    "parts": plist}
        src[qid] = "parsed_parts" if plist else "stem_whole"
    # validation
    ids = [q[0] for q in qs]
    if len(ids) != EXPECTED:
        errors.append("expected %d questions, found %d" % (EXPECTED, len(ids)))
    paper = collections.defaultdict(int)
    for qid, subj, year, no, _ in qs:
        if qid not in res:
            continue
        r = res[qid]
        if r["parts"] and sum(p["points"] for p in r["parts"]) != r["total"]:
            errors.append("%s: parts sum != total" % qid)
        paper[(year, subj)] += r["total"]
    for k, v in sorted(paper.items()):
        if v != 100:
            errors.append("paper %s-%s totals %d != 100" % (k[0], k[1], v))
    return ids, res, src, errors


def main():
    ids, res, src, errors = build()
    if errors:
        print("VALIDATION FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    ordered = {qid: res[qid] for qid in ids}
    OUT_JSON.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js = ("// Generated by scripts/build_question_points.py. Do not edit.\n"
          "// Sources: data/question-points.overrides.json > dashboard-data.js stems > paper default\n"
          "// questions: %d\n"
          "const QUESTION_POINTS = %s;\n") % (len(ordered), json.dumps(ordered, ensure_ascii=False, indent=2))
    OUT_JS.write_text(js, encoding="utf-8")
    print("questions:", len(ordered), dict(collections.Counter(src.values())))


if __name__ == "__main__":
    main()
