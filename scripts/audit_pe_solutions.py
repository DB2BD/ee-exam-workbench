#!/usr/bin/env python3
"""Conservative audit manifest for non-engineering-math PE solutions.

Annual notes are screened for copy/paste question bodies.  A solution becomes
verified only when a question-level canonical note carries verified frontmatter.
"""
from __future__ import annotations

import argparse, hashlib, json, re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "pe-solution-audit.json"

def load_questions():
    text = (ROOT / "dashboard-data.js").read_text(encoding="utf-8")
    m = re.search(r"questions:\s*(\[.*?\]),\s*\n\s*sevenLayers:", text, re.S)
    return json.loads(m.group(1))

def section(raw: str, qnum: int) -> str:
    # Only annual question headings use an ordinal followed by ``、`` (or a
    # full ``第 … 題`` heading).  Canonical notes legitimately use numbered
    # section headings such as ``## 1.``; treating those as question
    # boundaries would fingerprint only one subsection and leave the rest of
    # the answer unprotected by the audit manifest.
    parts = re.split(r"(?=\n##\s+(?:第\s*[一二三四五六七八九十\d]+\s*[大題題]|[一二三四五六七八九十\d]+\s*[、：:]))", raw)
    if len(parts) <= 1: return raw
    cmap = {c:i for i,c in enumerate("一二三四五六七八九十", 1)}
    for part in parts[1:]:
        m = re.search(r"##\s+(?:第\s*([一二三四五六七八九十\d]+)\s*[大題題]|([一二三四五六七八九十\d]+)\s*[、：:])", part)
        if not m: continue
        token = m.group(1) or m.group(2)
        n = int(token) if token.isdigit() else cmap.get(token)
        if n == qnum: return part
    return raw

def metadata(path: Path):
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not text.startswith("---"): return {}
    values = {}
    for line in text.split("---", 2)[1].splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        value = value.strip("'\"")
        # YAML null is a missing value, not the literal string "null".  Keep
        # the manifest machine-readable so manual-review rows cannot look as
        # though they were verified on a date named "null".
        values[key] = None if value.lower() in {"", "null", "none", "~"} else value
    return values

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); ap.add_argument("--output", type=Path, default=OUT); args = ap.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    old = {x["qid"]: x for x in json.loads(output.read_text(encoding="utf-8")).get("entries",[])} if output.is_file() else {}
    rows = [q for q in load_questions() if q[1] != "03"]
    prepared=[]; groups=defaultdict(list)
    for q in rows:
        qid,sid,year,num,topic,tags,link=q[:7]; path=ROOT/link; raw=path.read_text(encoding="utf-8") if path.is_file() else ""; body=re.sub(r"\s+"," ",section(raw,num)).strip(); digest=hashlib.sha256(body.encode()).hexdigest(); groups[digest].append(qid); prepared.append((q,digest,path))
    entries=[]
    for q,digest,path in prepared:
        qid,sid,year,num,topic,tags,link=q[:7]; meta=metadata(path); prev=old.get(qid,{})
        # Canonical notes historically used both ``status`` and the newer
        # ``audit_status`` key.  Treat either as authoritative so newly
        # reconstructed notes are not silently demoted to not_attempted.
        status=meta.get("audit_status") or meta.get("status") or prev.get("audit_status") or ("suspected_error" if len(groups[digest])>1 else "not_attempted")
        previous_verified_at = prev.get("verified_at")
        if isinstance(previous_verified_at, str) and previous_verified_at.lower() in {"", "null", "none", "~"}:
            previous_verified_at = None
        entry = {"qid":qid,"subject_id":sid,"year":year,"question_number":num,"chapter":topic,"solution_link":link,"audit_status":status,"verified_at":meta.get("verified_at") or previous_verified_at or (date.today().isoformat() if status=="verified" else None),"method":meta.get("method",prev.get("method","template_hash_screening")),"solution_hash":digest,"duplicate_qids":groups[digest] if len(groups[digest])>1 else [],"source_crop":meta.get("source_crop") or prev.get("source_crop","")}
        # Keep the machine-readable manifest aligned with the canonical note's
        # explicit disposition.  These fields explain why a manual item is
        # still unresolved without changing its conservative audit status.
        for key in ("review_disposition", "review_blocker", "review_action", "review_evidence", "official_source_url", "public_reference_urls", "public_reference_note"):
            if meta.get(key):
                entry[key] = meta[key]
        entries.append(entry)
    result={"schema_version":1,"scope":"PE 非工程數學 104-114","generated_at":date.today().isoformat(),"status_policy":["verified","suspected_error","needs_manual_review","not_attempted"],"entries":entries,"summary":{k:sum(e["audit_status"]==k for e in entries) for k in ("questions","verified","suspected_error","needs_manual_review","not_attempted")}}
    result["summary"]["questions"]=len(entries)
    if args.write: output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False))

if __name__ == "__main__": raise SystemExit(main())
