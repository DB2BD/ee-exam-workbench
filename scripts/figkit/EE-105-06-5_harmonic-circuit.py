"""EE-105-06-5 harmonic equivalent circuit at the 480 V bus.

Harmonic load = current source I_h injected from the reference into the bus. Source EMF shorted for harmonics, so the
source side is R_T + j h X_T (system R_S + jX_S plus transformer jX_Tr) to the reference; capacitor C in parallel.
Values equal the boxed results of note (一): R_T = 0.86 mΩ, X_T = 9.05 mΩ, C = 6.91 mF.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *  # svgkit + cap()
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')

W, H = 640, 380; s = header(W, H); lab = ''
yb, yr = 80, 320
xi, xs, xc, xv = 110, 300, 470, 590
s += busbar(60, 580, yb) + line(60, yr, 580, yr) + ground(380, yr)
s += line(xi, yb, xi, 181) + f'<circle cx="{xi}" cy="200" r="19"/>\n' + line(xi, 219, xi, yr)
s += arrow(xi, 211, xi, 187)
s += arrow(xi + 30, 160, xi + 30, 110, RED)
s += line(xs, yb, xs, 110) + resistor(xs, 110, xs, 170) + line(xs, 170, xs, 185) + coil(xs, 185, xs, 255, turns=4) + line(xs, 255, xs, yr)
s += line(xc, yb, xc, 180) + cap(xc, 180, xc, 220, gap=10, w=30) + line(xc, 220, xc, yr)
for x in (xi, xs, xc):
    s += dot(x, yb) + dot(x, yr)
s += end_group()
lab += text(60, 62, [("n", "480 V"), ("t", " 匯流排")])
lab += ctext(RED, xi + 40, 140, [("v", "I"), ("vsub", "h")])
lab += text(xi - 26, 205, [("t", "諧波負載")], anchor="end")
lab += text(xs + 18, 136, [("v", "R"), ("vsub", "T")]) + text(xs + 18, 158, [("n", "= 0.86 mΩ")])
lab += text(xs + 18, 216, [("v", "jhX"), ("vsub", "T")]) + text(xs + 18, 238, [("v", "X"), ("vsub", "T"), ("n", " = 9.05 mΩ")])
lab += text(xs + 18, 290, [("t", "電源側（電動勢短路）")])
lab += text(xc + 24, 196, [("v", "C"), ("n", " = 6.91 mF")]) + text(xc + 24, 218, [("n", "−"), ("v", "jX"), ("vsub", "C"), ("n", "/"), ("v", "h")])
lab += text(380, 362, [("t", "參考點")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-105-06-5-harmonic-circuit.svg'
out.write_text(s); print(out.name, len(s))
