import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

RED = "#c0392b"; BLUE_FILL = "#e3eefa"; RED_FILL = "#fde2e0"

def red_arrow(x1, y1, x2, y2):
    return f'<g stroke="{RED}">' + arrow(x1, y1, x2, y2).replace('fill="#000"', f'fill="{RED}"') + '</g>\n'

def red_text(x, y, parts, anchor="start"):
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{RED}"', 1)

def sup(parts):
    """Superscript run (italic variables / upright signs) as raw tspans for use inside text()."""
    out = ''
    for kind, s in parts:
        fam, cls, st = (FONT_V, "v", ' font-style="italic"') if kind == "v" else (FONT_N, "n", '')
        out += f'<tspan class="{cls} sup" font-family="{fam}"{st} font-size="12" baseline-shift="super">{s}</tspan>'
    return out

W, H = 560, 370
O = (120, 300)                       # origin
s = header(W, H)
# first-quadrant support region (unbounded to the right and up)
s += f'<rect x="120" y="50" width="400" height="250" fill="{BLUE_FILL}" stroke="none"/>\n'
# horizontal strip at fixed y
s += f'<rect x="120" y="170" width="390" height="22" fill="{RED_FILL}" stroke="{RED}" stroke-width="1.5"/>\n'
# axes
s += arrow(30, 300, 542, 300) + arrow(120, 350, 120, 30)
s += line(116, 181, 120, 181)
s += end_group()
s += red_arrow(132, 181, 492, 181)
s += text(538, 324, [("v", "x")], anchor="middle")
s += text(132, 36, [("v", "y")])
s += text(108, 320, [("n", "0")], anchor="end")
s += text(108, 187, [("v", "y")], anchor="end")
p = text(180, 92, [("v", "p"), ("n", "("), ("v", "x"), ("n", ","), ("v", "y"), ("n", ") = "), ("v", "k"), ("n", " "), ("v", "e")])
p = p.replace('</text>', sup([("n", "−"), ("v", "x"), ("n", " − "), ("v", "y"), ("n", "/2")]) + '</text>')
s += p
s += text(180, 118, [("t", "支撐區："), ("v", "x"), ("n", " ≥ 0"), ("t", " 且 "), ("v", "y"), ("n", " ≥ 0"), ("t", "（第一象限）")])
s += red_text(180, 216, [("t", "固定 "), ("v", "y"), ("t", "，對 "), ("v", "x"), ("t", " 由 "), ("n", "0"), ("t", " 積到 "), ("n", "∞"), ("t", " → "), ("v", "p"), ("vsub", "Y"), ("n", "("), ("v", "y"), ("n", ")")])
s += text(180, 254, [("v", "x"), ("t", "、"), ("v", "y"), ("t", " 上下限皆為 "), ("n", "0 → ∞")])
s += text(34, 120, [("v", "p"), ("n", " = 0")])
s += text(230, 344, [("v", "p"), ("n", " = 0"), ("t", "（"), ("v", "x"), ("n", " &lt; 0"), ("t", " 或 "), ("v", "y"), ("n", " &lt; 0"), ("t", "）")])
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/03_工程數學/figures/EE-113-03-6-support-region.svg'
out.write_text(s); print(len(s))
