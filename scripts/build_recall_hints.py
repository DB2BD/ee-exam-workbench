# -*- coding: utf-8 -*-
"""Build per-question hints for the four-stage recall reveal.

Stage ② (起手式) uses the first scoring move from the 起手式急救卡 where a
card exists; stage ③ (陷阱) uses the question's own 「## 失分點」 bullets from
its canonical note.  Questions without either keep the chapter template in
src/state/recallStore.js.

Writes src/data/recallHints.generated.js (const RECALL_HINTS).
"""

import json
import subprocess
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_GLOB = "📝 個人題解與錯題本/0*/canonical/EE-*.md"
RESCUE_CARDS = ROOT / "docs" / "上榜起手式急救卡_114-108.md"
OUTPUT = ROOT / "src" / "data" / "recallHints.generated.js"
WRITTEN_HINTS_DIR = ROOT / "data" / "recall-hints"  # per-subject first moves (0X.json)

SECTION_RE = r"^## {name}\s*$(.*?)(?=^## |\Z)"
CARD_RE = re.compile(r"^### `(EE-\d{3}-\d{2}-\d+)`.*?$(.*?)(?=^### |^## |\Z)", re.M | re.S)
FIRST_MOVE_RE = re.compile(r"第一個[^：\n]{2,8}：")  # 可得分動作／部分分結構


def section(text, name):
    match = re.search(SECTION_RE.format(name=re.escape(name)), text, re.M | re.S)
    return match.group(1).strip() if match else ""


RESULT_NUMBER_RE = re.compile(r"((?:=|≈|\\approx|得|答成|算成|變成|誤為|成為)\s*\$?\s*)(-?\d+(?:\.\d+)?)")


STEM_DUMP = r"""
const fs=require("fs"),vm=require("vm");
const c={};vm.runInNewContext(fs.readFileSync("dashboard-data.js","utf8")+";this.D=DB_DATA",c);
process.stdout.write(JSON.stringify(Object.fromEntries(c.D.questions.map(q=>[q[0],String(q[4]||"")]))));
"""
_STEMS = None


def official_stems():
    """Official question text per QID (from dashboard-data.js)."""
    global _STEMS
    if _STEMS is None:
        done = subprocess.run(["node", "-"], input=STEM_DUMP, capture_output=True, text=True, cwd=ROOT, check=True)
        _STEMS = json.loads(done.stdout)
    return _STEMS


def given_numbers(note_text, stem_text=""):
    known = section(note_text, "已知與所求") + "\n" + stem_text
    given = set(NUMBER_RE.findall(known))
    for pct in re.findall(r"(\d+(?:\.\d+)?)\s*\\?[%％]", known):
        given.add(f"{float(pct) / 100:g}")
    return given


def mask_trap_numbers(bullet, note_text, stem_text=""):
    """Stage ③ shows before the full solution, so hide computed values.

    Every multi-digit or decimal number that is not given in the question
    (official stem or 已知與所求) becomes 「□」, as do numbers in a result
    position (after =, ≈, 得, 答成 …); the method wording stays intact.
    """
    given = given_numbers(note_text, stem_text)
    masked = RESULT_NUMBER_RE.sub(lambda m: m.group(0) if m.group(2) in given else m.group(1) + "□", bullet)
    # Subscripts and exponents (Y_{22}, 10^{-3}) are labels, not results.
    masked = re.sub(r"(?<![\d.])(?<!_\{)(?<!\^\{)(?<!_)(?<!\^)(\d+\.\d+|\d{2,})(?![\d])", lambda m: m.group(0) if m.group(0) in given else "□", masked)
    for value in answer_numbers(note_text):
        masked = re.sub(rf"(?<![\d.]){re.escape(value)}(?![\d])", "□", masked)
    return masked


def traps_from_note(text, stem_text=""):
    body = section(text, "失分點")
    bullets = [mask_trap_numbers(line, text, stem_text) for line in body.splitlines() if line.startswith("- ")]
    return "\n".join(bullets)


def activations_from_cards(text):
    cards = {}
    for qid, body in CARD_RE.findall(text):
        found = FIRST_MOVE_RE.search(body)
        if not found:
            raise SystemExit(f"{qid}: rescue card has no 「第一個…：」 first move")
        move = body[found.end():]
        move = re.split(r"^\[完整題解核對\]", move, flags=re.M)[0].strip()
        cards[qid] = move
    return cards


BOXED_RE = re.compile(r"\\boxed\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}")
NUMBER_RE = re.compile(r"\d+\.\d+|\d{2,}")


def answer_numbers(note_text):
    """Numbers inside \\boxed{} answers that are not given in 已知與所求."""
    boxed = {n for body in BOXED_RE.findall(note_text) for n in NUMBER_RE.findall(body)}
    known = section(note_text, "已知與所求")
    given = set(NUMBER_RE.findall(known))
    # A given "5%" also legitimately appears as 0.05 in a first move.
    for pct in re.findall(r"(\d+(?:\.\d+)?)\s*\\?[%％]", known):
        given.add(f"{float(pct) / 100:g}")
    return boxed - given


def leaked_numbers(hint, note_text):
    return sorted(n for n in answer_numbers(note_text) if re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", hint))


def written_hints():
    merged = {}
    for path in sorted(WRITTEN_HINTS_DIR.glob("0*.json")):
        for qid, entry in json.loads(path.read_text(encoding="utf-8")).items():
            if qid in merged:
                raise SystemExit(f"{qid}: duplicate first move in {path.name}")
            merged[qid] = entry["activationMd"].strip()
    return merged


def build():
    hints = {}
    notes = {path.stem: path.read_text(encoding="utf-8") for path in sorted(ROOT.glob(CANONICAL_GLOB))}
    stems = official_stems()
    for qid, text in notes.items():
        traps = traps_from_note(text, stems.get(qid, ""))
        if traps:
            hints.setdefault(qid, {})["trapsMd"] = traps
    for qid, move in written_hints().items():
        if qid not in notes:
            raise SystemExit(f"{qid}: written first move has no canonical note")
        leaks = leaked_numbers(move, notes[qid])
        if leaks:
            raise SystemExit(f"{qid}: first move reveals answer value(s) {leaks}")
        hints.setdefault(qid, {})["activationMd"] = move
    # Rescue cards are curated and take precedence over written first moves.
    for qid, move in activations_from_cards(RESCUE_CARDS.read_text(encoding="utf-8")).items():
        if not any(ROOT.glob(f"📝 個人題解與錯題本/0*/canonical/{qid}.md")):
            raise SystemExit(f"{qid}: rescue card has no canonical note")
        hints.setdefault(qid, {})["activationMd"] = move
    return dict(sorted(hints.items()))


def render_js(hints):
    payload = json.dumps(hints, ensure_ascii=False, indent=1)
    return (
        "// AUTO-GENERATED by scripts/build_recall_hints.py — do not edit.\n"
        "// Per-question hints for the four-stage recall reveal: activationMd from\n"
        "// docs/上榜起手式急救卡_114-108.md or data/recall-hints/0X.json, trapsMd from\n"
        "// each note's 「## 失分點」.\n"
        f"const RECALL_HINTS = {payload};\n"
    )


def main():
    hints = build()
    OUTPUT.write_text(render_js(hints), encoding="utf-8")
    traps = sum(1 for h in hints.values() if "trapsMd" in h)
    moves = sum(1 for h in hints.values() if "activationMd" in h)
    print(f"wrote {OUTPUT.relative_to(ROOT)}: traps {traps}, activations {moves}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
