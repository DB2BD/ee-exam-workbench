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
    parts = re.split(r"(?=\n##\s+(?:第\s*[一二三四五六七八九十\d]+\s*[大題題]|[一二三四五六七八九十\d]+\s*[、.：:]))", raw)
    if len(parts) <= 1: return raw
    cmap = {c:i for i,c in enumerate("一二三四五六七八九十", 1)}
    for part in parts[1:]:
        m = re.search(r"##\s+(?:第\s*([一二三四五六七八九十\d]+)\s*[大題題]|([一二三四五六七八九十\d]+)\s*[、.：:])", part)
        if not m: continue
        token = m.group(1) or m.group(2)
        n = int(token) if token.isdigit() else cmap.get(token)
        if n == qnum: return part
    return raw

def metadata(path: Path):
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not text.startswith("---"): return {}
    return {k.strip(): v.strip().strip("'\"") for k,v in (line.split(":",1) for line in text.split("---",2)[1].splitlines() if ":" in line)}

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
        status=meta.get("audit_status") or prev.get("audit_status") or ("suspected_error" if len(groups[digest])>1 else "not_attempted")
        entries.append({"qid":qid,"subject_id":sid,"year":year,"question_number":num,"chapter":topic,"solution_link":link,"audit_status":status,"verified_at":meta.get("verified_at") or prev.get("verified_at") or (date.today().isoformat() if status=="verified" else None),"method":meta.get("method",prev.get("method","template_hash_screening")),"solution_hash":digest,"duplicate_qids":groups[digest] if len(groups[digest])>1 else [],"source_crop":prev.get("source_crop","")})
    result={"schema_version":1,"scope":"PE 非工程數學 104-114","generated_at":date.today().isoformat(),"status_policy":["verified","suspected_error","needs_manual_review","not_attempted"],"entries":entries,"summary":{k:sum(e["audit_status"]==k for e in entries) for k in ("questions","verified","suspected_error","needs_manual_review","not_attempted")}}
    result["summary"]["questions"]=len(entries)
    if args.write: output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False))

if __name__ == "__main__": raise SystemExit(main())
