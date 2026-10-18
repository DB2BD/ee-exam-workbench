"""EE-108-06-1 CVT: (left) original circuit of Fig. 1 — V1 across C1 (top) + C2 (bottom), midpoint a
-> L in series with Z_B to ground, V2 across Z_B; (right) Thevenin equivalent seen from a:
V_th = V1 C1/(C1+C2) in series with Z_th = 1/(s(C1+C2)), then sL and Z_B.  Symbols only.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *
def vind(x, y1, y2):
    """voltage indicator (not a wire): dashed blue from reference (y1) to node (y2), head at the node."""
    return (f'<path d="M{x} {y1} L{x} {y2 + 12}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="5 4"/>\n'
            + arrow(x, y2 + 16, x, y2 + 3, BLUE))
def box(x, y1, y2, w=22):
    m = (y1 + y2) / 2
    return line(x, y1, x, m - 22) + f'<rect x="{x - w / 2}" y="{m - 22}" width="{w}" height="44"/>\n' + line(x, m + 22, x, y2)
W, H = 720, 340; s = header(W, H); lab = ''
yt, ya, yb = 60, 170, 280
# ---- left: original circuit
xc, xz = 130, 290
s += line(60, yt, 210, yt) + cap(xc, yt, xc, ya) + cap(xc, ya, xc, yb)
s += line(xc, ya, 160, ya) + coil(160, ya, 230, ya) + line(230, ya, xz, ya) + box(xz, ya, yb)
s += line(60, yb, xz, yb) + ground(xc, yb + 14) + line(xc, yb, xc, yb + 14)
s += dot(xc, yt) + dot(xc, ya) + dot(xc, yb) + dot(250, ya) + dot(250, yb)
s += vind(60, yb, yt) + vind(250, yb, ya)
# ---- right: Thevenin equivalent
xs, xa, xz2 = 420, 520, 670
s += line(xs, yb, xs, 251) + f'<circle cx="{xs}" cy="236" r="15"/>\n' + line(xs - 4, 229, xs + 4, 229) + line(xs, 225, xs, 233) + line(xs - 4, 244, xs + 4, 244)
s += line(xs, 221, xs, ya) + cap(xs, ya, xa - 10, ya) + line(xa - 10, ya, xa, ya)
s += line(xa, ya, 550, ya) + coil(550, ya, 620, ya) + line(620, ya, xz2, ya) + box(xz2, ya, yb)
s += line(xs, yb, xz2, yb) + dot(xa, ya) + dot(625, ya) + dot(625, yb)
s += vind(625, yb, ya)
s += f'<path d="M352 30 L352 320" stroke-width="1" stroke-dasharray="3 4"/>\n'
s += end_group()
lab += text(xc - 24, 110, [("v", "C"), ("sub", "1")], anchor="end") + text(xc - 24, 232, [("v", "C"), ("sub", "2")], anchor="end")
lab += text(195, ya - 18, [("v", "L")], anchor="middle") + text(xz + 18, 232, [("v", "Z"), ("vsub", "B")])
lab += text(xc - 8, ya - 8, [("v", "a")], anchor="end")
lab += ctext(70, 175, [("v", "V"), ("sub", "1")], color=BLUE) + ctext(256, 236, [("v", "V"), ("sub", "2")], color=BLUE)
lab += text(180, 330, [("t", "（左）圖一原電路")], anchor="middle")
lab += text(xs - 22, 230, [("v", "V"), ("vsub", "th")], anchor="end")
lab += text(465, ya - 24, [("v", "Z"), ("vsub", "th")], anchor="middle") + text(470, ya + 34, [("n", "1/["), ("v", "s"), ("n", "("), ("v", "C"), ("sub", "1"), ("n", "+"), ("v", "C"), ("sub", "2"), ("n", ")]")], anchor="middle")
lab += text(xa, ya - 12, [("v", "a")], anchor="middle") + text(585, ya - 18, [("v", "sL")], anchor="middle")
lab += text(xz2 + 18, 232, [("v", "Z"), ("vsub", "B")]) + ctext(617, 236, [("v", "V"), ("sub", "2")], anchor="end", color=BLUE)
lab += text(540, 330, [("t", "（右）由 "), ("v", "a"), ("t", " 看入的戴維寧等效")], anchor="middle")
lab += text(540, 36, [("v", "V"), ("vsub", "th"), ("n", " = "), ("v", "V"), ("sub", "1"), ("v", "C"), ("sub", "1"), ("n", "/("), ("v", "C"), ("sub", "1"), ("n", "+"), ("v", "C"), ("sub", "2"), ("n", ")")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-108-06-1-thevenin.svg'
out.write_text(s); print(out.name, len(s))
