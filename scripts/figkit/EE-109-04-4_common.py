"""Shared drawing for EE-109-04-4 mmf space-vector figures.
Phase axes a 0 deg, b 120 deg, c 240 deg (math sense, counter-clockwise); each phase mmf N*i lies on its
own axis, on the negative side when the current is negative. Components are drawn from O (black),
their head-to-tail sum dashed, and the resultant F in blue."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

K = 140                     # pixels per NI
OX, OY = 200, 220
W, H = 620, 470
FN = "KaTeX_Main, 'Times New Roman', serif"


def P(mag, deg, x0=OX, y0=OY):
    a = math.radians(deg)
    return x0 + K * mag * math.cos(a), y0 - K * mag * math.sin(a)


def bold(svg):
    """Bold upright vector symbol F (matches \\mathbf F in the text)."""
    return svg.replace(f'<tspan class="n" font-family="{FN}">F</tspan>',
                       f'<tspan class="n" font-family="{FN}" font-weight="bold">F</tspan>')


def dashed(x1, y1, x2, y2, w=1):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke-dasharray="5 4" stroke-width="{w}"/>\n'


def figure(comps, chain, res_deg, labels, res_label, axis_note, out_name):
    """comps: [(mag, deg)] for a, b, c; chain: order of component indices for the head-to-tail sum."""
    s = header(W, H)
    for deg, L in ((0, 2.0), (120, 1.35), (240, 1.35)):
        x, y = P(L, deg)
        s += dashed(OX, OY, x, y)
    # resultant (blue, thick) first so overlapping components stay visible on top
    rx, ry = P(1.5, res_deg)
    s += f'<g stroke-width="3">' + arrow(OX, OY, rx, ry, color=BLUE) + '</g>\n'
    for mag, deg in comps:
        x, y = P(mag, deg)
        s += arrow(OX, OY, x, y)
    # head-to-tail construction
    x0, y0 = OX, OY
    for k in chain:
        mag, deg = comps[k]
        x1, y1 = P(mag, deg, x0, y0)
        if (x0, y0) != (OX, OY):
            s += dashed(x0, y0, x1, y1)
        x0, y0 = x1, y1
    s += dot(OX, OY)
    s += end_group()
    for deg, L, name in ((0, 2.0, "a"), (120, 1.35, "b"), (240, 1.35, "c")):
        x, y = P(L, deg)
        anchor = "end" if deg == 0 else "middle"
        dy = -10 if deg == 0 else (-8 if deg == 120 else 22)
        s += text(x, y + dy, [("v", name), ("t", " 相軸")], anchor=anchor)
    s += text(OX - 12, OY + 6, [("v", "O")], anchor="end")
    for (x, y, parts, anchor) in labels:
        s += bold(text(x, y, parts, anchor=anchor))
    x, y, parts, anchor = res_label
    s += bold(text(x, y, parts, anchor=anchor, color=BLUE))
    s += bold(text(W / 2, H - 16, axis_note, anchor="middle"))
    s += footer()
    out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures' / out_name
    out.write_text(s)
    print(out.name, len(s))
