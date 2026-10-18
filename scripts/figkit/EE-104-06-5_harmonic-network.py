"""EE-104-06-5 fifth-harmonic equivalent (per unit, S_b = 2 MVA, V_b = 380 V).

Rectifier = current source I_5 injected from the reference into the 380 V bus; three branches from the bus to the
reference: Z_up,5 (source + transformer, j0.345), Z_A,5 (reactor + 400 kvar, net j0.5), Z_B,5 (reactor + 200 kvar,
net j1). Branch current reference directions: bus -> reference (as in the note). Values equal note steps 2-3.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *  # svgkit + cap()
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')

W, H = 720, 400; s = header(W, H); lab = ''
yb, yr = 80, 330                       # bus, reference
xi, xu, xa, xb = 110, 280, 440, 590     # current source, Z_up, Z_A, Z_B
s += busbar(60, 690, yb)
s += line(60, yr, 690, yr) + ground(355, yr)
# current source (arrow up, into the bus)
s += line(xi, yb, xi, 186) + f'<circle cx="{xi}" cy="205" r="19"/>\n' + line(xi, 224, xi, yr)
s += arrow(xi, 216, xi, 192)
s += arrow(xi + 30, 160, xi + 30, 110, RED)
# Z_up: one coil
s += line(xu, yb, xu, 150) + coil(xu, 150, xu, 240, turns=5) + line(xu, 240, xu, yr)
# A, B: coil + capacitor in series
for x in (xa, xb):
    s += line(x, yb, x, 120) + coil(x, 120, x, 190, turns=4) + line(x, 190, x, 230) + cap(x, 230, x, 270) + line(x, 270, x, yr)
# branch current arrows (reference: bus -> reference)
for x in (xu, xa, xb):
    s += arrow(x - 22, 96, x - 22, 128, RED)
for x in (xi, xu, xa, xb):
    s += dot(x, yb) + dot(x, yr)
# V_5 between bus and reference (right edge)
s += line(690, yb, 690, yr) + dot(690, yb) + dot(690, yr)
s += end_group()
lab += ctext(BLUE, 700, yb + 10, [("n", "+")]) + ctext(BLUE, 700, yr - 2, [("n", "−")])
lab += ctext(BLUE, 700, (yb + yr) / 2 + 6, [("v", "V"), ("sub", "5")])
lab += text(60, 62, [("n", "380 V"), ("t", " 匯流排")])
lab += text(355, 372, [("t", "諧波參考點（電源電動勢對諧波短路）")], anchor="middle")
lab += ctext(RED, xi + 40, 140, [("v", "I"), ("sub", "5")]) + ctext(RED, xi + 40, 160, [("n", "= 0.05 pu")])
lab += text(xi - 26, 262, [("t", "整流器")], anchor="end")
lab += ctext(RED, xu - 28, 120, [("v", "I"), ("vsub", "up"), ("sub", ",5")], anchor="end")
lab += ctext(RED, xa - 28, 120, [("v", "I"), ("vsub", "A"), ("sub", ",5")], anchor="end")
lab += ctext(RED, xb - 28, 120, [("v", "I"), ("vsub", "B"), ("sub", ",5")], anchor="end")
lab += text(xu + 16, 190, [("v", "Z"), ("vsub", "up"), ("sub", ",5")]) + text(xu + 16, 212, [("n", "= "), ("v", "j"), ("n", "0.345 pu")])
lab += text(xu + 16, 270, [("t", "電源＋變壓器")])
for x, n, v, q in ((xa, "A", "0.5", "400 kvar"), (xb, "B", "1", "200 kvar")):
    lab += text(x + 16, 160, [("n", "6%")]) + text(x + 22, 256, [("n", q)])
    lab += text(x + 16, 296, [("v", "Z"), ("vsub", n), ("sub", ",5")]) + text(x + 16, 316, [("n", "= "), ("v", "j"), ("n", v + " pu")])
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-104-06-5-harmonic-network.svg'
out.write_text(s); print(out.name, len(s))
