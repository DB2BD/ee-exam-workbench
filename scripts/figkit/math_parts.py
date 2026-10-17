"""Shared parts for engineering-math figures (subject 03): coloured text, superscripts, dashes, output path.

Per-figure scripts import ``from math_parts import *`` (which re-exports svgkit).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *  # noqa: F401,F403

OUT_DIR = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/03_工程數學/figures'
G_OPEN = '<g fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n'


def ctext(x, y, parts, anchor="start", color=BLUE):
    """text() in an accent colour."""
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{color}"', 1)


def sup_run(parts):
    """Superscript tspans (v = italic variable, n = upright) to splice into a text() result."""
    out = ''
    for kind, s in parts:
        fam, cls, st = (FONT_V, "v", ' font-style="italic"') if kind == "v" else (FONT_N, "n", '')
        out += f'<tspan class="{cls} sup" font-family="{fam}"{st} font-size="12" baseline-shift="super">{s}</tspan>'
    return out


def text_sup(x, y, parts, sup_parts, tail=(), anchor="start", color="#000"):
    """text(parts) + superscript(sup_parts) + tail parts (tail rendered at normal baseline)."""
    t = text(x, y, list(parts) + [("n", "")], anchor)
    head, _, _ = t.rpartition('<tspan class="n"')
    body = head + sup_run(sup_parts)
    if tail:
        tail_t = text(0, 0, list(tail))
        tail_spans = tail_t[tail_t.index('>') + 1: tail_t.rindex('</text>')]
        body += tail_spans
    out = body + '</text>\n'
    if color != "#000":
        out = out.replace('fill="#000"', f'fill="{color}"', 1)
    return out


def dashed(x1, y1, x2, y2, color="#000"):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-dasharray="5 4"/>\n'


def write(name, s):
    out = OUT_DIR / name
    out.write_text(s)
    print(out.name, len(s))


def _spans(parts):
    t = text(0, 0, list(parts))
    return t[t.index('>') + 1: t.rindex('</text>')]


def mtext(x, y, parts, anchor="start", color="#000"):
    """Like text(), but parts may also contain ("sup", s) / ("vsup", s) superscript runs."""
    out = text(x, y, [("n", "")], anchor)
    out = out[:out.index('>') + 1]
    for kind, s in parts:
        if kind == "sup":
            out += sup_run([("n", s)])
        elif kind == "vsup":
            out += sup_run([("v", s)])
        else:
            out += _spans([(kind, s)])
    out += '</text>\n'
    if color != "#000":
        out = out.replace('fill="#000"', f'fill="{color}"', 1)
    return out
