"""EE-108-06-3 secondary voltage phasors of the V-V bank, potentials drawn with Y = 0:
V_XY = 220∠0° (arrow Y->X), V_YZ = 220∠-120° (arrow Z->Y), V_ZX = 220∠120° (arrow X->Z),
N = midpoint of XY, high leg V_ZN = j110√3 = 190.53 V (arrow N->Z).  Values as in note step 2.
"""
import sys, math, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
k = 1.25
W, H = 600, 380; s = header(W, H); lab = ''
Y = (160, 320); X = (Y[0] + 220 * k, 320); N = ((Y[0] + X[0]) / 2, 320); Z = (N[0], 320 - 110 * math.sqrt(3) * k)
def toward(p, q, d=10):
    L = math.hypot(q[0] - p[0], q[1] - p[1]); return (q[0] - d * (q[0] - p[0]) / L, q[1] - d * (q[1] - p[1]) / L)
s += arrow(*Y, *toward(Y, X, 3), BLUE) + arrow(*Z, *toward(Z, Y, 3), BLUE) + arrow(*X, *toward(X, Z, 3), BLUE)
s += f'<path d="M{N[0]:.1f} {N[1]:.1f} L{Z[0]:.1f} {Z[1] + 12:.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n' + arrow(Z[0], Z[1] + 14, Z[0], Z[1] + 3, BLUE)
for p in (X, Y, Z, N):
    s += dot(*p)
s += f'<path d="M{N[0]:.1f} {N[1] - 12:.1f} L{N[0] + 12:.1f} {N[1] - 12:.1f} L{N[0] + 12:.1f} {N[1]:.1f}" stroke-width="1"/>\n'
s += end_group()
lab += text(X[0] + 10, X[1] + 6, [("v", "X")]) + text(Y[0] - 10, Y[1] + 6, [("v", "Y")], anchor="end")
lab += text(Z[0], Z[1] - 12, [("v", "Z")], anchor="middle") + text(N[0], N[1] + 24, [("v", "N")], anchor="middle")
lab += ctext(BLUE, (Y[0] + N[0]) / 2, 346, [("v", "V"), ("vsub", "YN"), ("n", " = 110 V")], anchor="middle")
lab += ctext(BLUE, (X[0] + N[0]) / 2, 346, [("v", "V"), ("vsub", "XN"), ("n", " = 110 V")], anchor="middle")
lab += ctext(BLUE, N[0], 370, [("v", "V"), ("vsub", "XY"), ("n", " = 220∠0° V（"), ("v", "Y"), ("n", "→"), ("v", "X"), ("n", "）")], anchor="middle")
lab += ctext(BLUE, (Y[0] + Z[0]) / 2 - 14, (Y[1] + Z[1]) / 2, [("v", "V"), ("vsub", "YZ"), ("n", " = 220∠−120° V")], anchor="end")
lab += ctext(BLUE, (X[0] + Z[0]) / 2 + 22, (X[1] + Z[1]) / 2 - 10, [("v", "V"), ("vsub", "ZX"), ("n", " = 220∠120° V")])
lab += ctext(BLUE, N[0] + 8, 236, [("v", "V"), ("vsub", "ZN"), ("n", " =")])
lab += ctext(BLUE, N[0] + 8, 258, [("n", "190.53 V")])
lab += text(N[0] + 8, 280, [("t", "高腳相")])
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-108-06-3-phasor.svg'
out.write_text(s); print(out.name, len(s))
