#!/usr/bin/env python3
"""Audit the depth of the 「考場標準作答」 section of every canonical PE note.

For each note the section is split into sub-questions (（一）（二）… headings,
or the whole section when there are none).  Per sub-question the script
computes display-math blocks, substitution equations, intermediate results,
a concept-sentence heuristic and body characters per mark, and raises flags:

    missing-concept   no sentence naming a theorem / law / model / method
                      before the first display formula
    no-substitution   a numeric answer is boxed but no equation with data
                      numbers on its right-hand side precedes it
    jump              a \\boxed{} follows only symbolic formulas (no numeric
                      line between the last formula and the answer)
    no-intermediate   the numeric expression has many operations yet nothing
                      lies between the substitution and the answer
    too-short         body characters per mark below the corpus threshold

v1.5.0 solution-logic flags (WORKPLAN_v1.5.0):

    no-logic          non-compact note without ``**解題邏輯**：`` (flag on the
                      first sub-question) or a sub-question without ``**邏輯**：``
    orphan-number     a number (integers <= 3, subscripts, exponents and unit
                      scalers ignored) in the first substitution of a display
                      equation that appears neither earlier in the note nor in the
                      question stem / 「已知與所求」 -- a "where did this come from?" number

Notes are ranked by ``severity = sum(flag weight x sub-question marks / 10)``.

Usage::

    python3 scripts/audit_solution_depth.py                 # write report + JSON
    python3 scripts/audit_solution_depth.py --show EE-104-01-1   # metrics of one note
    python3 scripts/audit_solution_depth.py --stats         # print summary only

The script is read-only with respect to canonical notes.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_canonical_notes as lint  # noqa: E402

ROOT = lint.ROOT
DEFAULT_REPORT = ROOT / "reports/題解深度稽核_2026-10-14.md"   # only written with an explicit --report
DEFAULT_JSON = ROOT / ".agents/results/V150-LOGIC/candidates.json"

# --------------------------------------------------------------------------
# Tunable parameters (calibrated on the 323-note corpus, see the report).
# --------------------------------------------------------------------------
WEIGHTS = {
    "no-substitution": 3.0,
    "jump": 2.0,
    "no-intermediate": 2.0,
    "missing-concept": 1.5,
    "too-short": 2.0,
}
# v1.5.0 flags are scored on top of the v1.4.0 weights.
LOGIC_WEIGHTS = {
    "no-logic": 2.0,
    "orphan-number": 2.0,
}
ORPHAN_IGNORED = {"10", "100", "1000", "180", "360"}   # unit scalers / half and full turns
TOO_SHORT_CPP = 14.0      # body characters (non-whitespace, math source included) per mark
INTERMEDIATE_OPS = 3      # a numeric expression with this many operations should show a step
CUT_SEVERITY = 3.0        # severity at or above this value is on the recommended rewrite list

# Words that make a sentence a theorem / law / model / method statement.
CONCEPT_WORDS = (
    "定理", "定律", "定則", "定義", "等效", "守恆", "模型", "原理", "法則", "近似", "假設", "利用", "根據", "依據",
    "適用", "因為", "由於", "可知", "套用", "KCL", "KVL", "節點電壓", "節點法", "網目", "迴路電流", "戴維寧", "戴維南", "諾頓",
    "疊加", "重疊", "互易", "拉氏", "拉普拉斯", "傅立葉", "傅氏", "反轉換", "特徵值", "特徵向量", "對角化", "極點", "零點",
    "穩態", "暫態", "瞬態", "初值", "終值", "分壓", "分流", "相量", "複數功率", "功率因數", "最大功率", "諧振", "共振",
    "時間常數", "互感", "磁路", "標么", "對稱分量", "序網", "序阻抗", "Y-Δ", "Δ-Y", "星形", "等增量", "等面積", "短路容量",
    "電壓調整", "轉差", "電樞", "激磁", "反電勢", "反電動勢", "偏壓", "小信號", "米勒", "密勒", "迴授", "回授", "虛短",
    "運算放大", "BJT", "MOSFET", "二極體", "電晶體", "降壓", "升壓", "工作週期", "責任週期", "整流", "濾波", "換流", "諧波",
    "矩陣", "行列式", "微分方程", "齊次", "通解", "特解", "級數", "變數分離", "留數", "柯西", "格林", "高斯", "史托克",
    "散度", "旋度", "梯度", "機率", "期望", "插值", "牛頓", "迭代", "收斂", "需量", "需要因數", "負載因數", "電驛", "過電流",
    "熔絲", "斷路器", "功因改善", "電容器", "補償", "壓降", "電壓降", "阻抗匹配", "公式", "轉換", "短路電流", "啟斷",
    "等效電路", "戴維", "線性", "單位階", "卷積", "迴旋", "頻率響應", "波德", "奈氏", "羅斯", "穩定度", "根軌跡",
    "變壓器", "磁通", "感應電勢", "感應電動勢", "導納", "阻抗", "功率因素", "能量", "功率平衡", "功率守恆", "電荷",
    "叉積", "內積", "法向", "切線", "線積分", "面積分", "體積分", "參數化", "極座標", "座標",
    "分離變數", "方程", "展開", "餘因子", "正交", "奇函數", "偶函數", "開路", "短路", "串聯", "並聯", "不變", "固定", "平衡", "對稱", "視為", "忽略", "所見電阻",
    "正序", "負序", "零序", "雅可比", "Jacobian", "牛頓", "匯流排阻抗", "標么值", "分流定則", "分壓定則",
)
# Words that merely announce a calculation; they do not count towards an explanatory sentence.
ANNOUNCE = re.compile(r"代入|計算|求得|求出|可得|得到|得出|如下|數值|結果|答案|最後|同上|同理|其中|所以|因此|即|得")
EXPLAIN_MIN_CHARS = 10    # a lead sentence with this many reasoning characters counts as explanatory

ANALYTIC = re.compile(r"\\int|\\sum|\\lim|e\s*\^|\\exp|\\begin|⟦|\\partial|\\mathcal\{L\}|\\mathbf|\\vec|\\nabla")
ROW_BREAK =re.compile(r"\\\\(?:\[[^\]]*\])?")
SPLIT_ARROWS = re.compile(r"\\(?:Rightarrow|Longrightarrow|implies|Leftrightarrow|therefore)\b|\\qquad|\\quad")
MATH_TOKEN = re.compile(
    r"\$\$(?P<dd>.+?)\$\$|\\\[(?P<db>.+?)\\\]|\\\((?P<i1>.+?)\\\)|(?<![\\$])\$(?P<i2>[^$\n]+?)\$",
    re.S,
)
STEM_LABEL = re.compile(r"[（(]\s*([一二三四五六七八九十])\s*[）)]")
POINT_MARK = re.compile(r"[（(]\s*(\d+)\s*分\s*[）)]")
NUM_ORDER = "一二三四五六七八九十"


# --------------------------------------------------------------------------
# Math handling
# --------------------------------------------------------------------------
def brace_group(text: str, start: int) -> tuple[str, int]:
    """Return (content, index after closing brace) for the group opening at ``start``."""

    depth, index = 0, start
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
        index += 1
    return text[start + 1:], len(text)


def unbox(text: str) -> tuple[str, bool]:
    """Replace ``\\boxed{X}`` by ``X``; report whether a box was present."""

    found = False
    while True:
        match = re.search(r"\\boxed\s*\{", text)
        if not match:
            return text, found
        found = True
        inner, end = brace_group(text, match.end() - 1)
        text = text[:match.start()] + " " + inner + " " + text[end:]


def protect_environments(math: str) -> str:
    """Collapse matrices / cases so their row breaks do not split segments."""

    def repl(match: re.Match) -> str:
        body = re.sub(r"_\{[^}]*\}|_\w", "", match.group(2))
        return " ⟦N⟧ " if re.search(r"\d", body) else " ⟦M⟧ "

    return re.sub(r"\\begin\{(p|b|v|B|V)?matrix\}(.*?)\\end\{(?:p|b|v|B|V)?matrix\}", repl, math, flags=re.S)


def strip_noise(piece: str) -> str:
    """Drop subscripts and typesetting; units become the marker `` U ``."""

    piece = re.sub(r"\\(?:mathrm|text|operatorname|mathbf|mathit|textbf|mbox)\s*\{[^{}]*\}", " U ", piece)
    piece = re.sub(r"_\{[^{}]*\}|_\\?[A-Za-z0-9]", "", piece)  # subscripts
    piece = re.sub(r"\^\s*\{?\s*\\circ\s*\}?|\\Omega|\\%|%", " U ", piece)
    piece = re.sub(r"\\left|\\right|\\displaystyle|\\,|\\;|\\!|\\ |\\:|&", " ", piece)
    return piece


CONSTANTS = re.compile(
    r"\\frac\s*\{?1\}?\s*\{?[23]\}?|\\sqrt\s*\{?[23]\}?|\d*\s*\\pi|\\frac\s*\{?[23]\}?\s*\{?2\}?"
)


def data_tokens(piece: str) -> list[str]:
    """Numbers that look like measured / given data.

    Excluded: subscripts, exponents, formula constants (``\\frac12``, ``\\sqrt3``,
    ``2\\pi``) and lone digits that are coefficients or indices.  A lone digit
    counts only when a unit follows (``5\\ \\mathrm A``); decimals and integers of
    two or more digits always count.
    """

    piece = CONSTANTS.sub(" C ", strip_noise(piece))
    tokens = []
    for match in re.finditer(r"(?<![A-Za-z\\^_\d.])(\d+(?:\.\d+)?)", piece):
        token = match.group(1)
        if token == "0":                       # a zero result carries no computation to show
            continue
        if re.search(r"\^\s*\{?\s*[-+]?$", piece[:match.start()]):  # exponent digits
            continue
        if "." in token or len(token) >= 2:
            tokens.append(token)
        elif re.match(r"\s*U\b", piece[match.end():match.end() + 4]):
            tokens.append(token)
    return tokens


def operation_count(piece: str) -> int:
    piece = strip_noise(piece)
    piece = re.sub(r"\\times\s*10\s*\^\s*\{?\s*[-+]?\d+\s*\}?", " ", piece)            # scientific notation
    piece = re.sub(r"[-+]?\s*\d+(?:\.\d+)?\s*[-+]\s*j\s*\d+(?:\.\d+)?", " 1 ", piece)   # rectangular complex number
    piece = piece.replace("\\angle", " ").strip()
    piece = re.sub(r"^[-+]", "", piece)
    return len(re.findall(r"\\frac|\\sqrt|\\times|\\cdot|\\parallel|\\div|/|\^|(?:\\sin|\\cos|\\tan|\\ln|\\log|\\exp)(?=\s*\(?\s*[-\d])|⟦N⟧|[-+]", piece))


def split_pieces(segment: str) -> list[str]:
    """Split a segment on top-level ``=`` (and ``\\approx``)."""

    segment = segment.replace("\\approx", "=").replace("\\simeq", "=")
    pieces: list[str] = []
    current: list[str] = []
    depth = 0
    for char in segment:
        if char in "{([":
            depth += 1
        elif char in "})]":
            depth -= 1
        if char == "=" and depth <= 0:
            prior = "".join(current).rstrip()
            if prior.endswith(("\\neq", "\\leq", "\\geq", "\\ne", "\\le", "\\ge", "<", ">", "!")):
                current.append(char)
            else:
                pieces.append("".join(current))
                current = []
        else:
            current.append(char)
    pieces.append("".join(current))
    return [piece.strip() for piece in pieces]


class Segment:
    """One equation line (or chain) extracted from display or inline math."""

    def __init__(self, raw: str, boxed: bool, display: bool):
        self.raw = raw
        self.boxed = boxed
        self.display = display
        self.pieces = split_pieces(raw)
        # pieces that carry data numbers (``20\log_{10}20000=86.02`` has two, ``V_c=0`` has one)
        self.numeric_pieces = [i for i, piece in enumerate(self.pieces) if data_tokens(piece)]
        self.has_data = bool(data_tokens(raw))
        self.verbal = bool(re.search(r"[一-鿿]", raw))


def math_segments(math: str, display: bool) -> list[Segment]:
    math = protect_environments(math)
    math = re.sub(
        r"\\begin\{(?:aligned|align\*?|gathered|split|array)\}(\{[^}]*\})?|\\end\{(?:aligned|align\*?|gathered|split|array)\}",
        " ", math)
    result = []
    for row in ROW_BREAK.split(math):
        for part in SPLIT_ARROWS.split(row):
            text, boxed = unbox(part)
            if "=" in text or "\\approx" in text or boxed:
                result.append(Segment(text.strip(), boxed, display))
    return result


# --------------------------------------------------------------------------
# Section / sub-question splitting
# --------------------------------------------------------------------------
def standard_section(body: str) -> str:
    match = re.search(r"^##\s+考場標準作答\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return match.group(1) if match else ""


HEADING = re.compile(r"^(#{3,4})\s+(.+?)\s*$", re.M)
LABELED_LINE = re.compile(r"^\s*(?:\*\*)?\s*[（(]\s*([一二三四五六七八九十])\s*[）)][^\n]*$", re.M)


def split_subquestions(section: str) -> tuple[str, list[dict]]:
    """Return (shared preamble, [{label, heading, text}])."""

    section = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", section)
    heads = list(HEADING.finditer(section))
    if heads:
        preamble = section[:heads[0].start()]
        chunks = []
        for index, match in enumerate(heads):
            end = heads[index + 1].start() if index + 1 < len(heads) else len(section)
            title = match.group(2)
            label = STEM_LABEL.match(title.lstrip("*"))
            chunks.append({"label": label.group(1) if label else None, "heading": title, "text": section[match.end():end]})
        return preamble, chunks
    labels = [m for m in LABELED_LINE.finditer(section) if len(m.group(0).strip()) < 60]
    if len(labels) >= 2:
        preamble = section[:labels[0].start()]
        chunks = []
        for index, match in enumerate(labels):
            end = labels[index + 1].start() if index + 1 < len(labels) else len(section)
            chunks.append({"label": match.group(1), "heading": match.group(0).strip(), "text": section[match.end():end]})
        return preamble, chunks
    return "", [{"label": None, "heading": "", "text": section}]


def merge_boxless(chunks: list[dict]) -> list[dict]:
    """Chunks that never state an answer feed the next chunk (setup steps)."""

    merged: list[dict] = []
    pending: list[dict] = []

    def fold(items: list[dict]) -> dict:
        return {
            "label": items[0]["label"] or items[-1]["label"],
            "heading": " / ".join(c["heading"] for c in items if c["heading"]),
            "text": "\n".join(c["text"] for c in items),
        }

    for chunk in chunks:
        pending.append(chunk)
        if "\\boxed" in chunk["text"]:
            merged.append(fold(pending))
            pending = []
    if pending:
        if merged:
            merged[-1]["text"] += "\n" + "\n".join(c["text"] for c in pending)
        else:
            merged.append(fold(pending))
    return merged


def stem_points(stem: str) -> tuple[int, dict[str, int]]:
    """Total marks and marks per （一）… label from the question stem."""

    total = lint.total_points(stem) or 20
    labels = list(STEM_LABEL.finditer(stem))
    per: dict[str, int] = {}
    for index, match in enumerate(labels):
        end = labels[index + 1].start() if index + 1 < len(labels) else len(stem)
        marks = POINT_MARK.findall(stem[match.end():end])
        if marks:
            per.setdefault(match.group(1), int(marks[0]))
    return total, per


# --------------------------------------------------------------------------
# Per sub-question analysis
# --------------------------------------------------------------------------
def prose_of(text: str) -> str:
    """Text with math removed (display -> ∎, inline -> ◇)."""

    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = MATH_TOKEN.sub(lambda m: " ∎ " if (m.group("dd") or m.group("db")) else " ◇ ", text)
    return re.sub(r"[*>`#]", "", text)


def has_concept(prose: str) -> bool:
    cleaned = prose.replace("∎", " ").replace("◇", " ")
    return any(word in cleaned for word in CONCEPT_WORDS)


def explanatory_chars(prose: str) -> int:
    """Chinese characters of reasoning text (calculation announcements removed)."""

    cleaned = ANNOUNCE.sub("", prose.replace("∎", " ").replace("◇", " "))
    return len(re.findall(r"[一-鿿]", cleaned))


def analyse(text: str, heading: str, preamble_concept: bool) -> dict:
    segments: list[Segment] = []
    display_blocks = 0
    lead_end = None
    for match in MATH_TOKEN.finditer(text):
        is_display = bool(match.group("dd") or match.group("db"))
        math = match.group("dd") or match.group("db") or match.group("i1") or match.group("i2")
        if is_display:
            display_blocks += 1
            if lead_end is None:
                lead_end = match.start()
        segments.extend(math_segments(math, is_display))
    lead = prose_of(text[:lead_end] if lead_end is not None else text)
    prose = prose_of(text)
    flat = re.sub(r"\s+", "", re.sub(r"```.*?```", "", text, flags=re.S))

    # an answer window = the equation lines from the previous box (exclusive) to this box (inclusive)
    windows: list[list[Segment]] = []
    current: list[Segment] = []
    for index, segment in enumerate(segments):
        current.append(segment)
        following = segments[index + 1] if index + 1 < len(segments) else None
        if segment.boxed and not (following and following.boxed):   # consecutive boxes share one window
            windows.append(current)
            current = []

    substitutions = intermediates = jump_windows = skipped = worst_ops = bare_assertions = 0
    answer_numeric = any(s.boxed and s.has_data for s in segments)
    for window in windows:
        boxes = [s for s in window if s.boxed]
        pieces: list[int] = []   # operation counts of the numeric pieces, in order; the last is the answer
        analytic: list[bool] = []
        for segment in window:
            pieces.extend(operation_count(segment.pieces[i]) for i in segment.numeric_pieces)
            analytic.extend(bool(ANALYTIC.search(segment.pieces[i])) for i in segment.numeric_pieces)
        if not any(s.has_data for s in boxes) or any(s.verbal for s in boxes):
            continue                              # symbolic / verbal answer: not judged for substitution
        compound = [i for i, ops in enumerate(pieces) if ops >= 1]
        has_formula = any(not s.boxed and len(s.pieces) > 1 for s in window) or any(len(s.pieces) > 2 for s in boxes)
        if not compound and len(pieces) <= 1:
            if has_formula:
                jump_windows += 1
            else:
                bare_assertions += 1              # a conclusion stated in prose, e.g. 「轉矩不變故電流不變」
            continue
        substitutions += 1
        if compound:
            first = compound[0]
            between = max(len(pieces) - first - 2, 0)   # numeric pieces strictly between substitution and answer
            intermediates += between
            # closed-form results (integrals, exponentials, matrices) are not step-by-step arithmetic
            ops = max([pieces[i] for i in compound if not analytic[i]] or [0])
            worst_ops = max(worst_ops, ops)
            if ops >= INTERMEDIATE_OPS and between == 0:
                skipped += 1
        else:
            intermediates += len(pieces) - 2
    return {
        "display_blocks": display_blocks,
        "equations": len(segments),
        "substitutions": substitutions,
        "intermediates": intermediates,
        "boxed": sum(1 for s in segments if s.boxed),
        "jump_windows": jump_windows,
        "bare_assertions": bare_assertions,
        "skipped_windows": skipped,
        "worst_ops": worst_ops,
        "answer_numeric": answer_numeric,
        "concept_lead": has_concept(lead),
        "concept_any": has_concept(prose) or preamble_concept,
        "explained": explanatory_chars(lead) >= EXPLAIN_MIN_CHARS,
        "chars": len(flat),
    }


def subquestion_flags(metrics: dict, marks: float) -> list[str]:
    flags = []
    if not metrics["concept_lead"] and not metrics["concept_any"] and not metrics["explained"]:
        flags.append("missing-concept")
    if metrics["answer_numeric"]:
        if metrics["substitutions"] == 0 and metrics["jump_windows"]:
            flags.append("no-substitution")
        if metrics["jump_windows"]:
            flags.append("jump")
        if metrics["skipped_windows"]:
            flags.append("no-intermediate")
    if (metrics["chars"] / marks if marks else 0) < TOO_SHORT_CPP:
        flags.append("too-short")
    return flags


def describe(flag: str, metrics: dict) -> str:
    return {
        "missing-concept": "缺觀念句",
        "no-substitution": "缺代入式",
        "jump": f"跳步（{metrics['jump_windows']} 個 boxed 直接接符號式）",
        "no-intermediate": f"缺中間結果（{metrics['worst_ops']} 個運算一步到位）",
        "too-short": f"過短（{metrics['chars']} 字，{metrics['chars_per_mark']} 字/分）",
        "no-logic": "缺邏輯句",
        "orphan-number": "來源不明數字：" + "、".join(metrics.get("orphan_numbers", [])),
    }[flag]


def section_text(body: str, heading: str) -> str:
    match = re.search(r"^##\s+" + re.escape(heading) + r"\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return match.group(1) if match else ""


def number_key(token: str) -> str:
    try:
        return repr(float(token))
    except ValueError:
        return token


def given_numbers(stem: str, given_section: str) -> set[str]:
    """Numbers copied from the question stem or 「已知與所求」 (shown as given)."""

    text = stem + "\n" + given_section
    return {number_key(m.group(0)) for m in re.finditer(r"\d+(?:\.\d+)?", text)}


def math_numbers(math: str) -> list[str]:
    """Decimal literals of a math string, without subscripts, exponents, units and sizes."""

    math = re.sub(r"\\(?:mathrm|text|operatorname|mathbf|mathit|textbf|mbox|tag|hspace|rule|color)\s*\{[^{}]*\}", " ", math)
    math = re.sub(r"_\s*\{[^{}]*\}|_\s*\\?[A-Za-z0-9]", " ", math)
    math = re.sub(r"\^\s*\{[^{}]*\}|\^\s*[-+]?\d", " ", math)
    math = re.sub(r"\\\\\[[^\]]*\]", " ", math)
    return re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])|(?<![\w.])\.\d+(?![\w.])", math)


def rounding_audit(body: str, stem: str) -> dict:
    """Computed non-integers in 考場標準作答 / 驗算 math not shown with exactly two decimals."""

    given = given_numbers(stem, section_text(body, "已知與所求"))
    total = bad = 0
    offending: list[str] = []
    for heading in ("考場標準作答", "驗算"):
        text = re.sub(r"```.*?```", "", section_text(body, heading), flags=re.S)
        for match in MATH_TOKEN.finditer(text):
            math = match.group("dd") or match.group("db") or match.group("i1") or match.group("i2")
            for token in math_numbers(math):
                if number_key(token) in given:
                    continue
                total += 1
                if len(token.split(".")[1]) != 2:
                    bad += 1
                    if token not in offending:
                        offending.append(token)
    return {"computed_decimals": total, "not_two_decimals": bad, "numbers": offending[:10]}


NUMBER_TOKEN = re.compile(r"(?<![A-Za-z\\\d.])(\d+(?:\.\d+)?)")


IMAGINARY_J = re.compile(r"(?<![A-Za-z\\])j(?=\d|\.\d)")
THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")


# commands that may be written flush against a number (``\times12``)
LATEX_NUMBER_GLUE = {"\\times", "\\cdot", "\\div", "\\parallel", "\\pm", "\\angle", "\\approx", "\\Rightarrow", "\\quad", "\\qquad",
                     "\\left", "\\right", "\\sqrt", "\\frac", "\\mathrm", "\\Omega", "\\text", "\\boxed", "\\circ"}


class _Normalizer:
    """``IMAGINARY.sub(" ", text)``: drop the imaginary unit j and thousands separators."""

    @staticmethod
    def sub(_replacement: str, text: str) -> str:
        text = re.sub(r"\\[A-Za-z]+", lambda m: " " if m.group(0) in LATEX_NUMBER_GLUE else m.group(0), text)
        return IMAGINARY_J.sub(" ", THOUSANDS.sub("", text))


IMAGINARY = _Normalizer()


def numbers_in(text: str) -> set[str]:
    """Every number written in ``text`` (any position), normalised."""

    text = IMAGINARY.sub(" ", text)
    return {number_key(m.group(1)) for m in NUMBER_TOKEN.finditer(text)}


def piece_numbers(piece: str) -> list[str]:
    """Candidate 'new' numbers of one expression: no subscripts, exponents, units, small integers."""

    piece = strip_noise(IMAGINARY.sub(" ", piece))
    piece = re.sub(r"\\times\s*10\s*(?=\^)", " ", piece)
    piece = re.sub(r"\^\s*\{[^{}]*\}|\^\s*[-+]?\d+(?:\.\d+)?", " ", piece)
    piece = re.sub(r"\\sqrt\s*\[[^\]]*\]", " ", piece)
    found = []
    for match in NUMBER_TOKEN.finditer(piece):
        token = match.group(1)
        if "." not in token and (int(token) <= 3 or token in ORPHAN_IGNORED):
            continue
        found.append(token)
    return found


def orphan_numbers(text: str, seen: set[str]) -> list[str]:
    """Walk ``text`` in order; return numbers of display substitutions never seen before.

    ``seen`` is updated in place with every number of the text, so later
    sub-questions may rely on earlier ones.
    """

    orphans: list[str] = []
    position = 0
    for match in MATH_TOKEN.finditer(text):
        seen |= numbers_in(re.sub(r"```.*?```", "", text[position:match.start()], flags=re.S))
        position = match.end()
        math = match.group("dd") or match.group("db") or match.group("i1") or match.group("i2")
        if match.group("dd") or match.group("db"):
            for segment in math_segments(math, True):
                if segment.boxed:
                    continue
                for piece in segment.pieces:
                    if piece_numbers(piece) and operation_count(IMAGINARY.sub(" ", piece)) >= 1:
                        for token in piece_numbers(piece):
                            if number_key(token) not in seen and token not in orphans:
                                orphans.append(token)
                        break                      # later pieces are derived from this substitution
        seen |= numbers_in(math)
    seen |= numbers_in(text[position:])
    return orphans


def audit_note(path: Path, stem: str, subject: str) -> dict:
    fields, body = lint.frontmatter(path.read_text(encoding="utf-8"))
    rounding = rounding_audit(body, stem)
    total, per_label = stem_points(stem)
    preamble, chunks = split_subquestions(standard_section(body))
    chunks = merge_boxless(chunks)
    preamble_concept = has_concept(prose_of(preamble))
    compact = fields.get("compact") == "true"
    section = standard_section(body)
    lead = section[:HEADING.search(section).start()] if HEADING.search(section) else section
    note_flags = []
    if not compact and lint.LOGIC_OVERALL not in lead:
        note_flags.append("no-logic")
    seen = given_numbers(stem, section_text(body, "已知與所求")) | numbers_in(preamble)
    unlabeled = [c for c in chunks if c["label"] not in per_label]
    rest = total - sum(per_label[c["label"]] for c in chunks if c["label"] in per_label)
    subs = []
    for index, chunk in enumerate(chunks):
        if chunk["label"] in per_label:
            marks = per_label[chunk["label"]]
        else:
            marks = rest / len(unlabeled) if unlabeled and rest > 0 else total / len(chunks)
        metrics = analyse(chunk["text"], chunk["heading"], preamble_concept)
        metrics.update({
            "label": chunk["label"] or (NUM_ORDER[index] if len(chunks) > 1 and index < 10 else ""),
            "heading": chunk["heading"][:60],
            "marks": round(marks, 1),
            "chars_per_mark": round(metrics["chars"] / marks, 1) if marks else 0,
        })
        metrics["flags"] = subquestion_flags(metrics, marks)
        orphans = orphan_numbers(chunk["text"], seen)
        metrics["orphan_numbers"] = orphans[:10]
        if orphans:
            metrics["flags"].append("orphan-number")
        if not compact and chunk["heading"] and lint.LOGIC_SUB not in chunk["text"]:
            metrics["flags"].append("no-logic")
        subs.append(metrics)
    severity = 0.0
    for sub in subs:
        active = set(sub["flags"])
        if "no-substitution" in active:
            active.discard("jump")       # same defect, count once
        severity += sum({**WEIGHTS, **LOGIC_WEIGHTS}[f] for f in active) * sub["marks"] / 10.0
    severity += LOGIC_WEIGHTS["no-logic"] * len(note_flags) * total / 10.0
    chars = sum(s["chars"] for s in subs)
    return {
        "qid": fields.get("qid", path.stem),
        "subject": subject,
        "severity": round(severity, 2),
        "points": total,
        "compact": compact,
        "note_flags": note_flags,
        "chars": chars,
        "chars_per_point": round(chars / total, 1) if total else 0,
        "rounding": rounding,
        "subs": subs,
        "path": str(path.relative_to(ROOT)),
    }


def run_audit() -> list[dict]:
    stems = lint.stems()
    return [audit_note(path, stems.get(path.stem, ""), path.parent.parent.name.split("_", 1)[1]) for path in lint.canonical_paths([])]


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
SUBJECT_ORDER = ["電路學", "電子學", "工程數學", "電機機械", "電力系統", "工業配電"]


def subject_key(subject: str) -> str:
    for name in SUBJECT_ORDER:
        if subject.startswith(name[:3]):
            return name
    return subject or "未知"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    low = int(pos)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def candidate_record(note: dict) -> dict:
    flags_by_sub, notes = {}, []
    for sub in note["subs"]:
        if not sub["flags"]:
            continue
        key = f"（{sub['label']}）" if sub["label"] else "全文"
        flags_by_sub[key] = sub["flags"]
        title = re.sub(r"^\s*[（(][一二三四五六七八九十][）)]\s*", "", sub["heading"])[:18]
        notes.append(f"{key}{title}：" + "；".join(describe(f, sub) for f in sub["flags"]))
    if note["note_flags"]:
        notes.insert(0, "整題缺解題邏輯")
    return {
        "qid": note["qid"],
        "subject": subject_key(note["subject"]),
        "severity": note["severity"],
        "points": note["points"],
        "compact": note["compact"],
        "note_flags": note["note_flags"],
        "flags_by_subquestion": flags_by_sub,
        "orphan_numbers": {(f"（{sub['label']}）" if sub["label"] else "全文"): sub["orphan_numbers"]
                           for sub in note["subs"] if sub["orphan_numbers"]},
        "notes": notes,
        "rounding": {
            "not_two_decimals": note["rounding"]["not_two_decimals"],
            "computed_decimals": note["rounding"]["computed_decimals"],
            "numbers": note["rounding"]["numbers"],
        },
    }


def build_report(results: list[dict]) -> str:
    ranked = sorted(results, key=lambda n: (-n["severity"], n["qid"]))
    subjects = [s for s in SUBJECT_ORDER if any(subject_key(n["subject"]) == s for n in results)]
    flag_names = list(WEIGHTS)
    all_subs = [s for n in results for s in n["subs"]]
    cut = [n for n in results if n["severity"] >= CUT_SEVERITY]
    cpps = [s["chars_per_mark"] for s in all_subs]
    out = ["# 題解深度稽核（W2 / Agent B1）｜2026-10-14", ""]
    out += [
        "本報告由 `scripts/audit_solution_depth.py` 產生（唯讀，不修改任何 canonical 題解）。"
        f"範圍：{len(results)} 份 canonical 題解、{len(all_subs)} 個子題的「考場標準作答」。",
        "對照標準為 `lean-v1` 增訂：觀念一句 → 符號公式 → 數值代入式 → 中間結果 → `\\boxed{}`。",
        "",
        "## 一、判定方法",
        "",
        "- 子題切分：「考場標準作答」內的 `###` 小標（`（一）…`）；沒有小標則整段視為一個子題；"
        "沒有 `\\boxed` 的小標（如「步驟一」）併入下一個子題。配分取自題幹 `（N 分）`，缺漏時均分總分。",
        "- 顯示式數：`$$…$$` 與 `\\[…\\]` 區塊數。等式行由區塊依 `\\\\`、`\\Rightarrow`、`\\quad` 拆開，再加行內等式；每行再依 `=` 拆成片段。",
        "- 代入式：某個 `\\boxed` 之前（自上一個 boxed 之後起算）含「已知數值」且帶運算（`\\frac`、`+`、`\\times`、`\\sqrt`…）的等式片段。"
        "下標、指數、`\\frac{1}{2}`、`\\sqrt3`、`2\\pi`、緊貼字母的單位數字係數不算數值。",
        "- 中間結果：第一個含運算的數值片段與最終答案之間，鏈式等號或獨立行中的數值片段個數。",
        f"- 觀念句：首個顯示式之前的文字（含小標前的共用前言），或子題任一處文字，出現定理／定律／模型／方法關鍵詞（{len(CONCEPT_WORDS)} 個，見腳本 `CONCEPT_WORDS`）；"
        f"或首個顯示式前至少有 {EXPLAIN_MIN_CHARS} 個說明性中文字（扣除「代入」「計算」「可得」等宣告詞）。",
        "- 答案為文字或純符號式（如「穩定」「y(t)=…」）的子題不判代入／跳步，只看觀念句與篇幅。",
        "- 旗標：",
        "  - `missing-concept`：子題與共用前言都沒有觀念關鍵詞。",
        "  - `no-substitution`：答案為數值，但沒有任何代入式。",
        "  - `jump`：某個 `\\boxed` 之前只有符號式（沒有含數值的行）。",
        f"  - `no-intermediate`：代入式運算數 ≥ {INTERMEDIATE_OPS} 卻直接接到答案。",
        f"  - `too-short`：字數／配分 < {TOO_SHORT_CPP:g}。",
        "- 嚴重度 = Σ（旗標權重 × 子題配分 ÷ 10）。權重："
        + "、".join(f"`{k}` {v:g}" for k, v in WEIGHTS.items())
        + "（同一子題 `no-substitution` 與 `jump` 只計一次）。",
        "",
        "## 二、各科總表",
        "",
        "| 科目 | 題數 | 子題數 | 有旗標題數 | 建議改寫 | " + " | ".join(f"`{f}`" for f in flag_names) + " |",
        "| --- | ---: | ---: | ---: | ---: | " + " | ".join("---:" for _ in flag_names) + " |",
    ]
    total_row = [0] * (4 + len(flag_names))
    for subject in subjects:
        group = [n for n in results if subject_key(n["subject"]) == subject]
        subs = [s for n in group for s in n["subs"]]
        flagged = sum(1 for n in group if any(s["flags"] for s in n["subs"]))
        picked = sum(1 for n in group if n["severity"] >= CUT_SEVERITY)
        counts = [sum(1 for s in subs if f in s["flags"]) for f in flag_names]
        row = [len(group), len(subs), flagged, picked] + counts
        out.append(f"| {subject} | " + " | ".join(map(str, row)) + " |")
        total_row = [a + b for a, b in zip(total_row, row)]
    out += ["| **合計** | " + " | ".join(f"**{v}**" for v in total_row) + " |", "",
            "旗標欄為「子題數」，其餘為題數。", ""]

    out += ["## 三、分布與門檻校準", "",
            "子題「正文字數（不含空白，含數學式原始碼）÷ 配分」分布：", "",
            "| 百分位 | P5 | P10 | P15 | P25 | P50 | P75 | P90 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            "| 字／分 | " + " | ".join(f"{percentile(cpps, q):.1f}" for q in (0.05, 0.10, 0.15, 0.25, 0.50, 0.75, 0.90)) + " |", "",
            "各科子題的平均指標：", "",
            "| 科目 | 字／分 中位 | 字／分 P15 | 顯示式 | 代入式 | 中間結果 | 缺觀念句比例 | 跳步比例 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for subject in subjects:
        subs = [s for n in results if subject_key(n["subject"]) == subject for s in n["subs"]]
        c = [s["chars_per_mark"] for s in subs]
        out.append(
            f"| {subject} | {statistics.median(c):.1f} | {percentile(c, .15):.1f} | "
            f"{statistics.mean(s['display_blocks'] for s in subs):.2f} | {statistics.mean(s['substitutions'] for s in subs):.2f} | "
            f"{statistics.mean(s['intermediates'] for s in subs):.2f} | "
            f"{sum('missing-concept' in s['flags'] for s in subs) / len(subs):.0%} | "
            f"{sum('jump' in s['flags'] or 'no-substitution' in s['flags'] for s in subs) / len(subs):.0%} |")
    sev = [n["severity"] for n in results]
    edges = [0, 2, 3, 4, 6, 8]
    labels = ["0", "(0,2)", "[2,3)", "[3,4)", "[4,6)", "[6,8)", "≥8"]
    counts = [sum(1 for v in sev if v == 0)]
    for low, high in zip(edges, edges[1:] + [10 ** 9]):
        counts.append(sum(1 for v in sev if (low < v < high if low == 0 else low <= v < high)))
    out += ["", "嚴重度分布（題數）：", "", "| 嚴重度 | " + " | ".join(labels) + " |", "| --- | " + " | ".join("---:" for _ in labels) + " |",
            "| 題數 | " + " | ".join(map(str, counts)) + " |", "",
            "### 建議門檻", "",
            f"- `too-short`：{TOO_SHORT_CPP:g} 字／分（落在全體子題約 P{sum(1 for v in cpps if v < TOO_SHORT_CPP) / len(cpps) * 100:.0f}）。",
            f"- `no-intermediate`：代入式運算數 ≥ {INTERMEDIATE_OPS}。",
            f"- 改寫切線：嚴重度 ≥ {CUT_SEVERITY:g}（見第五節）；人力有餘可降到 2 或 1。", ""]

    out += ["## 四、嚴重度前 60 名", "",
            "| # | QID | 科目 | 配分 | compact | 嚴重度 | 缺漏（逐子題） |", "| ---: | --- | --- | ---: | :---: | ---: | --- |"]
    for rank, note in enumerate(ranked[:60], 1):
        record = candidate_record(note)
        out.append(f"| {rank} | {note['qid']} | {record['subject']} | {note['points']} | {'是' if note['compact'] else ''} | "
                   f"{note['severity']:.1f} | {'<br>'.join(record['notes']) or '—'} |")
    out += ["", "## 五、建議改寫切線", "",
            f"切線：嚴重度 ≥ {CUT_SEVERITY:g}，共 **{len(cut)}** 題（{len(cut) / len(results):.0%}）。", "",
            "| 科目 | 建議改寫題數 | 其中 compact | 合計配分 |", "| --- | ---: | ---: | ---: |"]
    for subject in subjects:
        group = [n for n in cut if subject_key(n["subject"]) == subject]
        out.append(f"| {subject} | {len(group)} | {sum(n['compact'] for n in group)} | {sum(n['points'] for n in group)} |")
    out.append(f"| **合計** | **{len(cut)}** | **{sum(n['compact'] for n in cut)}** | **{sum(n['points'] for n in cut)}** |")
    out += ["", "不同切線下的題數：", "", "| 嚴重度切線 | " + " | ".join(subjects) + " | 合計 |", "| --- | " + " | ".join("---:" for _ in subjects) + " | ---: |"]
    for threshold in (8, 6, 4, 3, 2, 1):
        per = [sum(1 for n in results if subject_key(n["subject"]) == s and n["severity"] >= threshold) for s in subjects]
        out.append(f"| ≥ {threshold} | " + " | ".join(map(str, per)) + f" | {sum(per)} |")
    out += ["", "## 六、人工抽查與精確率", "",
            "第一輪（調校前）抽查 10 題、27 個旗標，真實 18 個（67%）。誤報來源：解析式／分段函數被當成數值運算（`no-intermediate`）、"
            "只有單位數字的瑣碎代入（`jump`）、觀念詞表漏掉「分離變數」「方程」「展開」等。已據此調整：解析式（積分、指數、矩陣、cases）不計運算數、"
            "弱數字（單個 0～9 且無單位）不當作數據、`\\boxed` 含中文字視為文字答案、補詞表。", "",
            "調校後以全新抽樣再查 10 題、22 個旗標，真實 20 個（91%）；誤報主要是已用「沿第一列展開」「只需對 [0,π] 積分」等"
            "非標準詞點出方法、但詞表未收錄的觀念句。`missing-concept` 為最寬鬆的旗標（約 30% 子題），"
            "它與「新規範要求每個子題有觀念一句」一致，被標示者幾乎都真的沒有以定理／模型／方法開頭的句子；"
            "`too-short`、`jump`、`no-substitution` 精確率最高（抽查中皆為真實）；`no-intermediate` 偶有誤報（運算數 ≥ 3 但答案式本身是設定方程）。",
            "", "## 七、數值位數稽核（小數兩位規則）", "",
            "規則：`AGENT-SOLVE.md` 「三之一、數值位數」──計算所得數字一律顯示到小數點後第二位。"
            "本稽核掃描「考場標準作答」與「驗算」兩段的數學式，找出帶小數點、但小數位數 ≠ 2 的數字；"
            "整數、下標、指數、單位，以及題幹／「已知與所求」中出現過的數值（視為題目給定）不計。"
            "科學記號的尾數照同一規則檢查。", "",
            "| 科目 | 題數 | 有違規題數 | 計算小數總數 | 非兩位小數 | 違規比例 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    totals = [0, 0, 0, 0]
    for subject in subjects:
        group = [n for n in results if subject_key(n["subject"]) == subject]
        row = [len(group), sum(1 for n in group if n["rounding"]["not_two_decimals"]),
               sum(n["rounding"]["computed_decimals"] for n in group), sum(n["rounding"]["not_two_decimals"] for n in group)]
        totals = [a + b for a, b in zip(totals, row)]
        out.append(f"| {subject} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[3] / row[2]:.0%} |" if row[2] else f"| {subject} | {row[0]} | 0 | 0 | 0 | — |")
    out.append(f"| **合計** | **{totals[0]}** | **{totals[1]}** | **{totals[2]}** | **{totals[3]}** | **{totals[3] / max(totals[2], 1):.0%}** |")
    worst = sorted(results, key=lambda n: -n["rounding"]["not_two_decimals"])[:10]
    out += ["", "違規數最多的 10 題：", "", "| QID | 科目 | 非兩位小數 | 範例（最多 10 個） |", "| --- | --- | ---: | --- |"]
    for note in worst:
        out.append(f"| {note['qid']} | {subject_key(note['subject'])} | {note['rounding']['not_two_decimals']} | "
                   f"{'、'.join(note['rounding']['numbers'])} |")
    out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, nargs="?", const=DEFAULT_REPORT, default=None,
                        help="also write the Markdown report (legacy 2026-10-14 path when no value is given)")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON,
                        help="candidate list JSON path (default .agents/results/V150-LOGIC/candidates.json); '-' prints to stdout")
    parser.add_argument("--show", nargs="*", help="print metrics for these QIDs and exit")
    parser.add_argument("--stats", action="store_true", help="print the summary and exit without writing files")
    args = parser.parse_args(argv)

    results = run_audit()
    if args.show:
        for note in results:
            if note["qid"] in args.show:
                print(json.dumps(note, ensure_ascii=False, indent=1))
        return 0

    ranked = sorted(results, key=lambda n: (-n["severity"], n["qid"]))
    cut = [n for n in results if n["severity"] >= CUT_SEVERITY]
    cpps = [s["chars_per_mark"] for n in results for s in n["subs"]]
    out = sys.stderr if str(args.json) == "-" else sys.stdout
    sys.stdout, saved = out, sys.stdout
    print(f"notes={len(results)} subs={len(cpps)} chars/mark P5/P15/P50 = "
          f"{percentile(cpps, .05):.1f}/{percentile(cpps, .15):.1f}/{percentile(cpps, .5):.1f}")
    print("sub-question flags:", dict(Counter(f for n in results for s in n["subs"] for f in s["flags"])))
    print(f"recommended rewrite (severity >= {CUT_SEVERITY:g}): {len(cut)} notes")
    for subject in SUBJECT_ORDER:
        print(f"  {subject}: {sum(1 for n in cut if subject_key(n['subject']) == subject)}"
              f" / {sum(1 for n in results if subject_key(n['subject']) == subject)}")
    print("rounding (not two decimals): "
          + ", ".join(f"{s} {sum(n['rounding']['not_two_decimals'] for n in results if subject_key(n['subject']) == s)}"
                      f"/{sum(n['rounding']['computed_decimals'] for n in results if subject_key(n['subject']) == s)}"
                      for s in SUBJECT_ORDER)
          + f"; notes affected {sum(1 for n in results if n['rounding']['not_two_decimals'])}")
    sys.stdout = saved
    if args.stats:
        return 0
    payload = [candidate_record(n) for n in ranked if n["severity"] > 0 or n["rounding"]["not_two_decimals"]]
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if str(args.json) == "-":
        sys.stdout.write(text)
    else:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
        print(f"wrote {args.json} ({len(payload)} candidates)")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(build_report(results), encoding="utf-8")
        print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
