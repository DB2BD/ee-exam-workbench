# -*- coding: utf-8 -*-
"""Build the K3 "一鍵開始今天" schedule data from the plan Markdown docs.

Sources (docs/): 上榜逐日開工表_115年 (v1.3: 41 天日程、關卡、每日時數預算),
上榜預設24時段_核心題路徑, 上榜被動模考_114年六科執行包, 上榜被動複測_108年六科執行包.
WEAK／REINF／WRAP／BUFFER 沒有固定題目，其階段定義在本檔常數（內容說明見日程文件的「任務代碼」表）。
MIX 與 EXT 已於 v1.3 退休，不再排入。
Outputs: src/data/dailySchedule.generated.js and data/daily-schedule.json.
Exits non-zero on any parse mismatch.

    python3 scripts/build_daily_schedule.py [--check]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DOCS = WORKSPACE / "docs"
PLAN = DOCS / "上榜逐日開工表_115年.md"
CORE = DOCS / "上榜預設24時段_核心題路徑.md"
MOCK = DOCS / "上榜被動模考_114年六科執行包.md"
BLIND = DOCS / "上榜被動複測_108年六科執行包.md"
OUT_JS = WORKSPACE / "src" / "data" / "dailySchedule.generated.js"
OUT_JSON = WORKSPACE / "data" / "daily-schedule.json"

QID_RE = re.compile(r"EE-\d{3}-\d{2}-\d+")
DAY_RE = re.compile(
    r"^\| (?P<date>2026-\d{2}-\d{2})（[^）]+） \| "
    r"(?P<budget>\d+(?:\.5)?) \| (?P<task>.+) \|$",
    re.MULTILINE,
)
MILESTONE_RE = re.compile(
    r"^\| (?P<date>2026-\d{2}-\d{2})（[^）]+） \| (?P<label>.+?) \| (?P<hard>是|否) \| (?P<note>.+) \|$",
    re.MULTILINE,
)
ITEM_RE = re.compile(r"`([A-Z0-9-]+)`(?:（(第 [12] 天|一次做完)[^）]*）)?")
NON_WORK = {"EXAM-CHECK", "STOP"}
BUDGET = {"weekday": 2, "weekend": 4}
HOURS_TOLERANCE = 0.5  # a day may exceed its budget by this much (WEAK rounds are 1.25 h)
FIRST_DATE = date(2026, 10, 4)
LAST_DATE = date(2026, 11, 13)
FIRST_WORK_CODES_DONE = [f"CORE-{i:02d}" for i in range(1, 7)]  # done on paper; kept in the task list only
GROUP_COUNTS = {"WEAK": 14, "REINF": 9, "WRAP": 3}
PAPER_PREFIXES = ("MOCK114", "BLIND108")

LAUNCH_BALANCED = "random-balanced"
LAUNCH_REINFORCE = "random-reinforce"


class ParseError(Exception):
    pass


def _need(cond: bool, message: str) -> None:
    if not cond:
        raise ParseError(message)


def _read(path: Path) -> str:
    _need(path.exists(), f"missing source doc: {path}")
    return path.read_text(encoding="utf-8")


def _is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def budget_for(d: date) -> int:
    return BUDGET["weekend"] if _is_weekend(d) else BUDGET["weekday"]


def parse_days(text: str) -> list[dict]:
    """41 dated rows 2026-10-04..2026-11-13: [{date, dow, budget, codes, items:[{code, part}]}]."""
    days = []
    for m in DAY_RE.finditer(text):
        d = date.fromisoformat(m.group("date"))
        items = []
        for code, marker in ITEM_RE.findall(m.group("task")):
            part = {"第 1 天": "closed", "第 2 天": "review"}.get(marker, "full")
            items.append({"code": code, "part": part})
        _need(items, f"no task code in day row {m.group('date')}")
        codes = []
        for it in items:
            if it["code"] not in codes:
                codes.append(it["code"])
        days.append({
            "date": m.group("date"), "dow": (d.weekday() + 1) % 7,
            "budget": float(m.group("budget")), "codes": codes, "items": items,
        })
    expected = [(FIRST_DATE + timedelta(days=i)).isoformat() for i in range((LAST_DATE - FIRST_DATE).days + 1)]
    _need([x["date"] for x in days] == expected, f"day rows must be continuous {expected[0]}..{expected[-1]} ({len(expected)} rows), got {len(days)}")
    for day in days:
        d = date.fromisoformat(day["date"])
        non_work = [c for c in day["codes"] if c in NON_WORK]
        if non_work:
            _need(day["codes"] == non_work and day["budget"] == 0, f"{day['date']}: non-work row must hold only {non_work} with budget 0")
        else:
            _need(day["budget"] == budget_for(d), f"{day['date']}: budget {day['budget']} != {budget_for(d)} (weekday 2 / weekend 4)")
    _need(days[-2]["codes"] == ["EXAM-CHECK"] and days[-1]["codes"] == ["STOP"], "last two days must be EXAM-CHECK then STOP")
    return days


def parse_milestones(text: str) -> list[dict]:
    section = text.split("## 關卡", 1)
    _need(len(section) == 2, "missing 「## 關卡」 section")
    body = section[1].split("\n## ", 1)[0]
    out = []
    for m in MILESTONE_RE.finditer(body):
        out.append({"date": m.group("date"), "label": m.group("label"), "hard": m.group("hard") == "是"})
    _need(len(out) == 3, f"expected 3 milestones, got {len(out)}")
    _need([x["date"] for x in out] == sorted(x["date"] for x in out), "milestones must be in date order")
    _need(sum(1 for x in out if x["hard"]) == 1, "exactly one hard (不可延後) milestone expected")
    return out


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
            "title": topic, "qids": qids, "variant": kind != "母題", "phases": phases,
        })
    _need([t["code"] for t in tasks] == [f"CORE-{i:02d}" for i in range(1, 25)],
          f"CORE rows mismatch: {[t['code'] for t in tasks]}")
    return tasks


def practice_tasks(days: list[dict]) -> list[dict]:
    """WEAK／REINF／WRAP／BUFFER: no fixed qids.  `launch` tells the UI which 隨機練習 mode to open."""
    tasks: list[dict] = []
    for n in range(1, GROUP_COUNTS["WEAK"] + 1):
        tasks.append({
            "code": f"WEAK-{n:02d}", "kind": "practice", "launch": LAUNCH_BALANCED,
            "title": f"弱題分析｜隨機練習 第 {n} 輪（各科輪流）", "qids": [],
            "phases": [
                {"label": "隨機練習 3 題（各科輪流）", "minutes": 60, "closed": False, "launch": LAUNCH_BALANCED,
                 "note": "按「開啟隨機練習」，用各科輪流模式作答 3 題；每題先閉卷再核對，並記錄作答結果。"},
                {"label": "一句話錯因整理", "minutes": 15, "closed": False,
                 "note": "只寫一句：這 3 題最常錯在哪一步、下次最先要改的動作。不必回填。"},
            ],
        })
    for n in range(1, GROUP_COUNTS["REINF"] + 1):
        tasks.append({
            "code": f"REINF-{n:02d}", "kind": "practice", "launch": LAUNCH_REINFORCE,
            "title": f"補強｜隨機練習 第 {n} 輪", "qids": [],
            "phases": [
                {"label": "補強隨機練習（模考 △／× 題優先）", "minutes": 90, "closed": False, "launch": LAUNCH_REINFORCE,
                 "note": "按「開啟補強練習」：優先抽兩套模考標 △／× 的題與其同章同型題，其次成績頁錯因最多的章。"},
                {"label": "重做錯題與錯因回顧", "minutes": 30, "closed": False,
                 "note": "把這一輪做錯的題蓋牌重寫一次；時間到就停。"},
            ],
        })
    wrap = [
        ("速查手冊", "讀速查手冊（失分點速查卡）", "閉卷默寫公式與起手式", "只讀不抄，讀完立即闔上默寫。"),
        ("條件題卡", "複習條件題處理卡", "標示條件寫法", "確認每個條件題的前提與可接受答案寫法。"),
        ("錯因回顧", "回顧錯因修復索引", "重寫最後三題", "只重寫索引中最常錯的 3 題，不擴張成整理專案。"),
    ]
    for n, (name, p1, p2, note) in enumerate(wrap, 1):
        tasks.append({
            "code": f"WRAP-{n:02d}", "kind": "review", "title": f"收尾｜{name}", "qids": [],
            "phases": [
                {"label": p1, "minutes": 90, "closed": False, "note": note},
                {"label": p2, "minutes": 30, "closed": False, "note": "不開新題。"},
            ],
        })
    tasks.append({
        "code": "BUFFER", "kind": "review", "launch": LAUNCH_REINFORCE, "title": "緩衝日｜補考或開始補強", "qids": [],
        "phases": [
            {"label": "補考：未完成的模考卷（沒有就跳過）", "minutes": 120, "closed": False,
             "note": "若 12 份卷還有沒做完的，到「模考」分頁補做；全部完成就直接進下一步。"},
            {"label": "補強隨機練習", "minutes": 120, "closed": False, "launch": LAUNCH_REINFORCE,
             "note": "按「開啟補強練習」開始補強。"},
        ],
    })
    for t in tasks:
        t["hours"] = sum(p["minutes"] for p in t["phases"]) / 60
    first = {}
    for day in days:
        for c in day["codes"]:
            first.setdefault(re.sub(r"-\d+$", "", c), day["date"])
    for t in tasks:
        group = re.sub(r"-\d+$", "", t["code"])
        if group in ("REINF", "WRAP", "BUFFER") and group in first:
            t["notBefore"] = first[group]
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


def _day_hours(day: dict, tasks: dict) -> float:
    total = 0.0
    for it in day["items"]:
        task = tasks.get(it["code"])
        if not task:
            continue
        if task["kind"] in ("mock114", "blind108"):
            total += {"closed": task["phases"][0]["minutes"], "review": sum(p["minutes"] for p in task["phases"][1:]),
                      "full": sum(p["minutes"] for p in task["phases"])}[it["part"]] / 60
        else:
            total += task["hours"]
    return total


def build_schedule() -> dict:
    plan_text = _read(PLAN)
    days = parse_days(plan_text)
    milestones = parse_milestones(plan_text)
    papers = parse_paper(_read(MOCK), "MOCK114", "mock114", "114 年") + parse_paper(_read(BLIND), "BLIND108", "blind108", "108 年")
    core = parse_core(_read(CORE))
    for t in core + papers:
        t["hours"] = sum(p["minutes"] for p in t["phases"]) / 60
    tasks = core + practice_tasks(days) + papers
    by_code = {t["code"]: t for t in tasks}
    _need(len(by_code) == len(tasks), "duplicate task codes")
    for t in tasks:
        total = sum(p["minutes"] for p in t["phases"])
        expect = {"core": 60, "mock114": 180, "blind108": 180}.get(t["kind"])
        if expect is not None:
            _need(total == expect, f"{t['code']}: phases sum {total} != {expect}")

    # Every dated code is known, appears exactly once (papers: full, or closed on a weekday + review the next day).
    seen_parts: dict[str, list[tuple[str, str]]] = {}
    order: list[str] = []
    due: dict[str, str] = {}
    for day in days:
        for it in day["items"]:
            code = it["code"]
            if code in NON_WORK:
                continue
            _need(code in by_code, f"day table references unknown code {code}")
            _need(code not in FIRST_WORK_CODES_DONE, f"{code} is already done on paper and must not be dated")
            seen_parts.setdefault(code, []).append((day["date"], it["part"]))
            if code not in order:
                order.append(code)
            due[code] = day["date"]
    scheduled = [c for c in by_code if c not in FIRST_WORK_CODES_DONE]
    _need(sorted(order) == sorted(scheduled), "day table does not cover every task exactly once: "
          f"missing {sorted(set(scheduled) - set(order))} extra {sorted(set(order) - set(scheduled))}")
    for code, parts in seen_parts.items():
        kinds = [k for _, k in parts]
        if by_code[code]["kind"] in ("mock114", "blind108"):
            if kinds == ["full"]:
                _need(_is_weekend(date.fromisoformat(parts[0][0])), f"{code}: single-sitting paper must be on a weekend ({parts[0][0]})")
            else:
                _need(kinds == ["closed", "review"], f"{code}: paper must be full or closed+review, got {kinds}")
                d1, d2 = (date.fromisoformat(d) for d, _ in parts)
                _need(d2 - d1 == timedelta(days=1) and not _is_weekend(d1),
                      f"{code}: weekday paper needs closed (weekday) then review the next day, got {parts}")
        else:
            _need(kinds == ["full"], f"{code}: expected one dated slot, got {parts}")
    for prefix, count in GROUP_COUNTS.items():
        found = [c for c in order if c.startswith(prefix + "-")]
        _need(found == [f"{prefix}-{i:02d}" for i in range(1, count + 1)], f"{prefix} codes must be 01..{count:02d} in order, got {found}")
    _need([c for c in order if c.startswith(PAPER_PREFIXES)] ==
          [f"MOCK114-0{i}" for i in range(1, 7)] + [f"BLIND108-0{i}" for i in range(1, 7)], "paper order must be MOCK114-01..06 then BLIND108-01..06")
    _need(order.index("BUFFER") > max(order.index(c) for c in order if c.startswith(PAPER_PREFIXES)), "BUFFER must follow every paper")

    # Daily hours fit the budget (with the small tolerance) and every milestone is reachable.
    for day in days:
        hours = _day_hours(day, by_code)
        _need(hours <= day["budget"] + HOURS_TOLERANCE + 1e-9, f"{day['date']}: {hours} h exceeds budget {day['budget']} h")
        day["hours"] = hours
    all_papers = [c for c in order if c.startswith(PAPER_PREFIXES)]
    for ms in milestones:
        ms["codes"] = [c for c in FIRST_WORK_CODES_DONE + order if due.get(c, "2026-10-03") <= ms["date"]]
        need = sum(by_code[c]["hours"] for c in ms["codes"] if c not in FIRST_WORK_CODES_DONE)
        have = sum(d["budget"] for d in days if d["date"] <= ms["date"])
        _need(need <= have + HOURS_TOLERANCE + 1e-9, f"milestone {ms['date']}: {need} h of work exceeds {have} h of budget")
        if ms["hard"]:
            _need(all(c in ms["codes"] for c in all_papers), f"hard milestone {ms['date']} must include all 12 papers")
    _need(all(due[c] <= next(m["date"] for m in milestones if m["hard"]) for c in all_papers), "a paper is dated after the hard milestone")
    return {
        "budget": dict(BUDGET),
        "milestones": milestones,
        "tasks": {t["code"]: t for t in tasks},
        "days": days,
        "order": FIRST_WORK_CODES_DONE + order,
        "due": {c: due.get(c, (FIRST_DATE - timedelta(days=1)).isoformat()) for c in FIRST_WORK_CODES_DONE + order},
    }


def render_js(schedule: dict) -> str:
    body = json.dumps(schedule, ensure_ascii=False, indent=2, sort_keys=False)
    return (
        "// Generated by scripts/build_daily_schedule.py. Do not edit.\n"
        "// Source: docs/上榜逐日開工表_115年.md and the 上榜 task-pack docs (v1.3 compact schedule).\n"
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
