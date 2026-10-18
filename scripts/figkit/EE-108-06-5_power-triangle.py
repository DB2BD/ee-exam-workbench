"""EE-108-06-5 power triangle before / after the 120 kvar shunt capacitor (P = 640 kW unchanged).

Values equal the note's step 1: Q1 = 480, Q2 = 360 kvar; S1 = 800, S2 = 734.3 kVA.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 620, 340; s = header(W, H); k = 0.5
x0, base = 60, 280
P, Q1, Q2 = 640, 480, 360
xe, y1, y2 = x0 + P * k, base - Q1 * k, base - Q2 * k
s += line(x0, base, xe, base) + line(xe, base, xe, y1) + line(x0, base, xe, y1)
s += f'<path d="M{x0} {base} L{xe:.1f} {y2:.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += arrow(xe + 10, y1, xe + 10, y2, BLUE) + dot(xe, y1) + dot(xe, y2) + dot(x0, base)
s += end_group()
lab = text((x0 + xe) / 2, base + 26, [("v", "P"), ("n", " = 640 kW")], anchor="middle")
lab += text(xe + 18, y1 + 6, [("v", "Q"), ("sub", "1"), ("n", " = 480 kvar")])
lab += ctext(BLUE, xe + 18, (y1 + y2) / 2 + 6, [("v", "Q"), ("vsub", "c"), ("n", " = 120 kvar")])
lab += text(xe + 18, y2 + 6, [("v", "Q"), ("sub", "2"), ("n", " = 360 kvar")])
lab += text(150, 128, [("v", "S"), ("sub", "1"), ("n", " = 800 kVA")], anchor="end")
lab += ctext(BLUE, 250, 214, [("v", "S"), ("sub", "2"), ("n", " = 734.3 kVA")], anchor="middle")
lab += text(W / 2, 330, [("t", "黑：補償前；藍虛線：並聯電容器後（只減 "), ("v", "Q"), ("t", "、不改 "), ("v", "P"), ("t", "）")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-108-06-5-power-triangle.svg'), 'w').write(s)
print(len(s))
