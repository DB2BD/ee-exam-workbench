"""EE-104-06-3 per-unit divider: E = 1∠0° — Z_up (source X_S + 69 kV line + main transformer) — 11.4 kV bus — R + jX_down.

S_b = 15 MVA. Values equal the note (steps 2–3). The voltage |V| is taken between the 11.4 kV bus and the return line.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 330; s = header(W, H); lab = ''
yt, yb, xs, xb = 90, 260, 70, 470
# source
s += line(xs, yb, xs, 189) + ac_source(xs, 175) + line(xs, 161, xs, yt)
# Z_up = R_up + jX_up on the top wire
s += line(xs, yt, 140, yt) + resistor(140, yt, 210, yt) + line(210, yt, 250, yt) + coil(250, yt, 330, yt) + line(330, yt, xb, yt)
s += dot(xb, yt)
# shunt branch: variable R then jX_down
s += line(xb, yt, xb, 112) + resistor(xb, 112, xb, 170) + line(xb, 170, xb, 180) + coil(xb, 180, xb, 236, turns=4) + line(xb, 236, xb, yb)
s += arrow(xb - 20, 160, xb + 20, 122)                       # variable-resistor arrow
s += line(xs, yb, xb, yb) + dot(xb, yb)
# measured voltage: bus node to return line
s += line(xb, yt, 600, yt) + line(xb, yb, 600, yb) + dot(600, yt) + dot(600, yb)
s += end_group()
lab += ctext(BLUE, 612, yt + 8, [("n", "+")]) + ctext(BLUE, 612, yb + 6, [("n", "−")])
lab += ctext(BLUE, 612, (yt + yb) / 2 + 6, [("v", "V")])
lab += text(xs + 22, 170, [("v", "E")]) + text(xs + 22, 192, [("n", "1∠0°")])
lab += text(175, 66, [("v", "R"), ("vsub", "up")], anchor="middle") + text(175, 122, [("n", "1.7747×10"), ("n", "⁻⁴")], anchor="middle")
lab += text(290, 66, [("v", "jX"), ("vsub", "up")], anchor="middle") + text(290, 122, [("v", "j"), ("n", "0.079744")], anchor="middle")
lab += text(xb, 62, [("t", "爐變一次側（11.4 kV 匯流排）")], anchor="middle")
lab += text(xb - 32, 136, [("v", "R"), ("vsub", "pu")], anchor="end") + text(xb - 32, 158, [("n", "0～1.1542")], anchor="end")
lab += text(xb + 16, 205, [("v", "jX"), ("vsub", "down")]) + text(xb + 16, 226, [("v", "j"), ("n", "0.6012")])
lab += text(W / 2, 300, [("v", "S"), ("vsub", "b"), ("n", " = 15 MVA"), ("t", "；"), ("v", "Z"), ("vsub", "up"), ("t", "＝電源＋69 kV 線路＋主變，"), ("v", "R"), ("vsub", "pu"), ("n", " = "), ("v", "R"), ("n", "/8.664")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-104-06-3-divider.svg'), 'w').write(s)
print(len(s))
