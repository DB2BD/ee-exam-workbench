"""EE-106-06-5 harmonic equivalent at the rectifier bus: current source I_h, system jhX_s, capacitor −jX_c/h.

Symbols only (no bus voltage given, so X_s and X_c stay symbolic: X_s = V²/S_sc, X_c = V²/Q_c).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *  # svgkit + cap()
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')

W, H = 600, 340; s = header(W, H); lab = ''
yb, yr = 70, 280
xi, xs, xc = 110, 300, 460
s += busbar(60, 540, yb) + line(60, yr, 540, yr) + ground(380, yr)
s += line(xi, yb, xi, 156) + f'<circle cx="{xi}" cy="175" r="19"/>\n' + line(xi, 194, xi, yr)
s += arrow(xi, 186, xi, 162) + arrow(xi + 30, 150, xi + 30, 100, RED)
s += line(xs, yb, xs, 135) + coil(xs, 135, xs, 215, turns=5) + line(xs, 215, xs, yr)
s += line(xc, yb, xc, 155) + cap(xc, 155, xc, 195, gap=10, w=30) + line(xc, 195, xc, yr)
for x in (xi, xs, xc):
    s += dot(x, yb) + dot(x, yr)
s += end_group()
lab += text(60, 52, [("t", "變壓器二次側匯流排（"), ("v", "S"), ("vsub", "sc"), ("n", " = 15.68 MVA"), ("t", "）")])
lab += ctext(RED, xi + 40, 130, [("v", "I"), ("vsub", "h")])
lab += text(xi - 26, 180, [("t", "整流器")], anchor="end")
lab += text(xs + 18, 170, [("v", "jhX"), ("vsub", "s")]) + text(xs + 18, 192, [("t", "系統側")])
lab += text(xc + 24, 170, [("n", "−"), ("v", "jX"), ("vsub", "c"), ("n", "/"), ("v", "h")]) + text(xc + 24, 192, [("v", "Q"), ("vsub", "c"), ("n", " = 320 kvar")])
lab += text(380, 320, [("t", "參考點（電源電動勢對諧波短路）")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-106-06-5-resonance.svg'
out.write_text(s); print(out.name, len(s))
