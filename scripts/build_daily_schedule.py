# -*- coding: utf-8 -*-
"""Build the K3 "一鍵開始今天" schedule data from the plan Markdown docs.

Sources (docs/): 上榜逐日開工表_115年, 上榜預設24時段_核心題路徑,
上榜混合橋接_六科12題, 上榜被動模考_114年六科執行包, 上榜被動複測_108年六科執行包.
Outputs: src/data/dailySchedule.generated.js and data/daily-schedule.json.
Exits non-zero on any parse mismatch.

    python3 scripts/build_daily_schedule.py [--check]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DOCS = WORKSPACE / "docs"
PLAN = DOCS / "上榜逐日開工表_115年.md"
CORE = DOCS / "上榜預設24時段_核心題路徑.md"
MIX = DOCS / "上榜混合橋接_六科12題.md"
MOCK = DOCS / "上榜被動模考_114年六科執行包.md"
BLIND = DOCS / "上榜被動複測_108年六科執行包.md"
OUT_JS = WORKSPACE / "src" / "data" / "dailySchedule.generated.js"
OUT_JSON = WORKSPACE / "data" / "daily-schedule.json"

QID_RE = re.compile(r"EE-\d{3}-\d{2}-\d+")
DAY_RE = re.compile(
    r"^\| (?P<date>2026-\d{2}-\d{2})（[^）]+） \| "
    r"(?P<task>.+?) \| (?P<hours>\d+(?:\.5)?) \| (?P<entry>.+) \|$",
    re.MULTILINE,
)
CODE_RE = re.compile(r"`([A-Z0-9-]+)`")
NON_WORK = {"RECOVERY", "EXAM-CHECK", "STOP"}


class ParseError(Exception):
    pass


def _need(cond: bool, message: str) -> None:
    if not cond:
        raise ParseError(message)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _read(path: Path) -> str:
    _need(path.exists(), f"missing source doc: {path}")
    return path.read_text(encoding="utf-8")


def parse_days(text: str) -> list[dict]:
    days = []
    for m in DAY_RE.finditer(text):
        codes = CODE_RE.findall(m.group("task"))
        _need(codes, f"no task code in day row {m.group('date')}")
        days.append({"date": m.group("date"), "codes": codes, "hours": float(m.group("hours"))})
    _need(len(days) == 52, f"expected 52 day rows, got {len(days)}")
    return days


def parse_core(text: str) -> list[dict]:
    tasks = []
    for line in text.splitlines():
        m = re.match(r"^\| (\d{1,2}) \| (.+?) \| (母題|同型＋變式) \| (.+?) \| (.+) \|$", line)
        if not m:
            continue
        n, topic, kind, qcell = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        qids = QID_RE.findall(qcell)
        subject = topic.split("／", 1)[0]
        if kind == "母題":
            _need(len(qids) == 1, f"CORE-{n:02d}: 母題 needs 1 qid, got {qids}")
            phases = [
                {"label": "閉卷作答", "minutes": 35, "closed": True, "qids": qids},
                {"label": "核對", "minutes": 20, "closed": False},
                {"label": "下次動作", "minutes": 5, "closed": False},
            ]
        else:
            _need(len(qids) == 2, f"CORE-{n:02d}: 同型＋變式 needs 2 qids, got {qids}")
            phases = [
                {"label": "同型題", "minutes": 20, "closed": True, "qids": [qids[0]]},
                {"label": "變式題", "minutes": 20, "closed": True, "qids": [qids[1]]},
                {"label": "三題對照", "minutes": 15, "closed": False},
                {"label": "下次動作", "minutes": 5, "closed": False},
            ]
        tasks.append({
            "code": f"CORE-{n:02d}", "kind": "core", "subject": subject,
            "title": topic, "qids": qids, "phases": phases,
        })
    _need([t["code"] for t in tasks] == [f"CORE-{i:02d}" for i in range(1, 25)],
          f"CORE rows mismatch: {[t['code'] for t in tasks]}")
    return tasks


def parse_mix(text: str) -> list[dict]:
    tasks = []
    for line in text.splitlines():
        m = re.match(r"^\| (\d) \| (.+?) \| (\[EE-.+?) \| (\[EE-.+?) \|$", line)
        if not m:
            continue
        n, subject = int(m.group(1)), m.group(2)
        qids = QID_RE.findall(m.group(3)) + QID_RE.findall(m.group(4))
        _need(len(qids) == 2, f"MIX-{n:02d}: expected 2 qids, got {qids}")
        tasks.append({
            "code": f"MIX-{n:02d}", "kind": "mix", "subject": subject,
            "title": f"{subject}混合橋接", "qids": qids,
            "phases": [
                {"label": "閉卷", "minutes": 50, "closed": True, "qids": qids},
                {"label": "得分證據核對", "minutes": 20, "closed": False},
                {"label": "重寫", "minutes": 20, "closed": False},
            ],
        })
    _need([t["code"] for t in tasks] == [f"MIX-0{i}" for i in range(1, 7)],
          f"MIX rows mismatch: {[t['code'] for t in tasks]}")
    return tasks


def parse_paper(text: str, prefix: str, kind: str, label: str) -> list[dict]:
    tasks = []
    for line in text.splitlines():
        m = re.match(r"^\| (\d) \| (.+?) \| (.+?) \| \[(.+?)\]\((.+?)\) \| \[.+?\]\(.+?\) \|$", line)
        if not m:
            continue
        n, subject, qcell, _, pdf = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
        qids = QID_RE.findall(qcell)
        _need(qids, f"{prefix}-{n:02d}: no qids")
        _need(pdf.startswith("../") and pdf.lower().endswith(".pdf"), f"{prefix}-{n:02d}: bad pdf path {pdf}")
        task = {
            "code": f"{prefix}-{n:02d}", "kind": kind, "subject": subject,
            "title": f"{label}{subject}計時演練", "qids": qids,
            "pdf": pdf[3:],
            "phases": [
                {"label": "閉卷模考", "minutes": 120, "closed": True, "qids": qids},
                {"label": "得分證據核對", "minutes": 30, "closed": False},
                {"label": "單題修復", "minutes": 30, "closed": False},
            ],
        }
        if "不列預設計分" in qcell or prefix == "MOCK114" and n == 6:
            task["scoringNote"] = qcell.replace("`", "")
        tasks.append(task)
    _need([t["code"] for t in tasks] == [f"{prefix}-0{i}" for i in range(1, 7)],
          f"{prefix} rows mismatch: {[t['code'] for t in tasks]}")
    return tasks


def build_schedule() -> dict:
    days = parse_days(_read(PLAN))
    tasks = (
        parse_core(_read(CORE)) + parse_mix(_read(MIX))
        + parse_paper(_read(MOCK), "MOCK114", "mock114", "114 年")
        + parse_paper(_read(BLIND), "BLIND108", "blind108", "108 年")
    )
    by_code = {t["code"]: t for t in tasks}
    _need(len(by_code) == len(tasks), "duplicate task codes")
    order = []
    for day in days:
        for code in day["codes"]:
            if code in NON_WORK:
                continue
            _need(code in by_code, f"day table references unknown code {code}")
            order.append(code)
    _need(sorted(order) == sorted(by_code), "day table does not cover every task exactly once")
    for t in tasks:
        total = sum(p["minutes"] for p in t["phases"])
        expect = {"core": 60, "mix": 90}.get(t["kind"], 180)
        _need(total == expect, f"{t['code']}: phases sum {total} != {expect}")
    return {
        "tasks": {t["code"]: t for t in tasks},
        "days": days,
        "order": order,
    }


def render_js(schedule: dict) -> str:
    body = json.dumps(schedule, ensure_ascii=False, indent=2, sort_keys=False)
    return (
        "// Generated by scripts/build_daily_schedule.py. Do not edit.\n"
        "// Source: docs/上榜逐日開工表_115年.md and the four 上榜 task-pack docs.\n"
        f"const DAILY_SCHEDULE = {body};\n"
    )


def render_json(schedule: dict) -> str:
    return json.dumps(schedule, ensure_ascii=False, indent=2) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if outputs are stale")
    args = parser.parse_args(argv)
    try:
        schedule = build_schedule()
    except ParseError as exc:
        print(f"build_daily_schedule: {exc}", file=sys.stderr)
        return 1
    js, js_json = render_js(schedule), render_json(schedule)
    if args.check:
        ok = OUT_JS.exists() and OUT_JS.read_text(encoding="utf-8") == js \
            and OUT_JSON.exists() and OUT_JSON.read_text(encoding="utf-8") == js_json
        if not ok:
            print("build_daily_schedule: generated files are stale", file=sys.stderr)
            return 1
        return 0
    OUT_JS.write_text(js, encoding="utf-8")
    OUT_JSON.write_text(js_json, encoding="utf-8")
    print(f"wrote {OUT_JS.relative_to(WORKSPACE)} and {OUT_JSON.relative_to(WORKSPACE)} "
          f"({len(schedule['tasks'])} tasks, {len(schedule['days'])} days)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
