"""EE-111-06-1 reading the 100:5 excitation curve (log–log), digitized points as in verification/pe/EE-111-06-1.py.

(一) E′ = 7.056 V -> I_e ≈ 0.40 A;  (二) E′ = 24.656 V lies above the curve end (I_e = 30 A, E′ ≈ 22 V) -> I_e ≥ 30 A.
Blue = voltages E′, red = excitation currents I_e.
"""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
CURVE = [(0.360, 6.42), (0.432, 8.54), (0.519, 10.62), (0.623, 12.50), (0.748, 14.33), (0.898, 16.55), (1.295, 18.10),
         (1.555, 18.74), (1.867, 19.34), (2.241, 19.56), (2.691, 19.56), (3.231, 19.72), (3.879, 20.03), (4.658, 20.18),
         (5.593, 20.34), (6.715, 20.50), (8.062, 20.74), (9.680, 20.90), (11.622, 21.07), (13.955, 21.15), (16.755, 21.40),
         (20.117, 21.65), (24.153, 21.82), (29.000, 21.90)]
W, H = 640, 430; s = header(W, H)
X0, Y0, D = 110, 340, 150                      # Ie 0.1..100 A (3 decades), E' 1..100 V (2 decades)
X = lambda ie: X0 + (math.log10(ie) + 1) * D
Y = lambda e: Y0 - math.log10(e) * D
# grid
g = ''
for dec in range(-1, 2):
    for m in range(1, 10):
        v = m * 10 ** dec
        g += f'<path d="M{X(v):.1f} {Y(100):.1f} L{X(v):.1f} {Y0}" stroke="#000" stroke-opacity="{0.35 if m == 1 else 0.18}" stroke-width="{1 if m == 1 else 0.6}"/>\n'
for dec in range(0, 2):
    for m in range(1, 10):
        v = m * 10 ** dec
        g += f'<path d="M{X0} {Y(v):.1f} L{X(100):.1f} {Y(v):.1f}" stroke="#000" stroke-opacity="{0.35 if m == 1 else 0.18}" stroke-width="{1 if m == 1 else 0.6}"/>\n'
s += g + f'<rect x="{X0}" y="{Y(100):.1f}" width="{3 * D}" height="{2 * D}"/>\n'
# curve
s += '<path d="M' + ' L'.join(f'{X(i):.1f} {Y(e):.1f}' for i, e in CURVE) + '" stroke-width="2.2"/>\n'
s += dot(X(29.0), Y(21.9))
# (一) 7.056 V -> 0.40 A
e1, i1 = 7.056, 0.40
s += f'<path d="M{X0} {Y(e1):.1f} L{X(i1):.1f} {Y(e1):.1f}" stroke="{BLUE}" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{X(i1):.1f} {Y(e1):.1f} L{X(i1):.1f} {Y0}" stroke="{RED}" stroke-dasharray="5 4"/>\n'
# (二) 24.656 V above the curve end
e2 = 24.656
s += f'<path d="M{X0} {Y(e2):.1f} L{X(100):.1f} {Y(e2):.1f}" stroke="{BLUE}" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{X(30):.1f} {Y(21.9):.1f} L{X(30):.1f} {Y0}" stroke="{RED}" stroke-dasharray="5 4"/>\n'
s += end_group()
lab = ''
for v, t in ((0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
    lab += text(X(v), Y0 + 22, [("n", t)], anchor="middle")
for v, t in ((1, "1"), (10, "10"), (100, "100")):
    lab += text(X0 - 8, Y(v) + 5, [("n", t)], anchor="end")
lab += text(X0 + 1.5 * D, Y0 + 50, [("t", "激磁電流 "), ("v", "I"), ("vsub", "e"), ("n", "（A）")], anchor="middle")
lab += text(30, Y(10) - 10, [("v", "E"), ("n", "′")], anchor="middle") + text(30, Y(10) + 12, [("n", "（V）")], anchor="middle")
lab += ctext(BLUE, X(i1) + 10, Y(e1) + 22, [("v", "E"), ("n", "′ = 7.056 V（一）")])
lab += ctext(BLUE, X0 + 6, Y(e2) - 8, [("v", "E"), ("n", "′ = 24.656 V（二）")])
lab += ctext(RED, X(i1) + 6, Y0 - 10, [("v", "I"), ("vsub", "e"), ("n", " ≈ 0.40 A")])
lab += ctext(RED, X(30) - 6, Y0 - 10, [("v", "I"), ("vsub", "e"), ("n", " = 30 A")], anchor="end")
lab += text(X(30) - 8, Y(21.9) + 24, [("t", "曲線末端 "), ("n", "≈ 22 V")], anchor="end")
lab += text(X(1.3), Y(18.3) + 26, [("n", "100:5")], anchor="middle")
lab += text(W / 2, 420, [("t", "100:5 激磁曲線（由官方圖數位化）；（二）的水平線高於曲線末端，無交點")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-111-06-1-excitation.svg'), 'w').write(s)
print(len(s))
