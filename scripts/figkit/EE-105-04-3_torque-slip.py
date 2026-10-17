"""EE-105-04-3 fig 2: T(s) for increasing rotor-circuit resistance r = R_2' + R_ext' (shape only;
illustrative R_th = 0.3, X = 1). T_max is the same for every r; s_max = r / sqrt(R_th^2 + X^2) moves toward s = 1;
r_3 = sqrt(R_th^2 + X^2) puts T_max at start; r_4 > r_3 lowers T_st again."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from power_parts import dashed, poly
from circuit_parts import ttext

Rth, X = 0.3, 1.0
Z = math.hypot(Rth, X)
T = lambda r, s: (r / s) / ((Rth + r / s) ** 2 + X ** 2)
Tmax = 1 / (2 * (Rth + Z))
rs = [0.08, 0.25, Z, 2.5]
W, H = 640, 360; XL, XRt, Y0, KY = 90, 560, 300, 620.0
P = lambda s, t: (XRt - (XRt - XL) * s, Y0 - KY * t)          # s = 1 at the left, s = 0 at the right
s_ = header(W, H)
s_ += arrow(XL, Y0, XRt + 30, Y0) + arrow(XL, Y0, XL, 40)
s_ += dashed(XL, Y0 - KY * Tmax, XRt, Y0 - KY * Tmax)
for k, r in enumerate(rs):
    pts = [P(0, 0)] + [P(j / 150, T(r, j / 150)) for j in range(1, 151)]
    s_ += poly(pts, w=2.2 if k == 2 else 1.4, color=BLUE if k == 2 else None)
    s_ += dot(*P(1, T(r, 1)))
s_ += end_group()
s_ += text(XRt + 30, Y0 + 24, [("v", "s")], anchor="end")
s_ += text(XL, Y0 + 22, [("n", "1")], anchor="middle") + text(XL, Y0 + 42, [("t", "（起動）")], anchor="middle")
s_ += text(XRt, Y0 + 22, [("n", "0")], anchor="middle")
s_ += text(XL + 10, 44, [("v", "T")])
s_ += text(XL + 180, Y0 - KY * Tmax - 8, [("v", "T"), ("vsub", "max"), ("t", "（與 "), ("v", "r"), ("t", " 無關）")])
for k, r in enumerate(rs):
    x, y = P(1, T(r, 1))
    parts = [("v", "r"), ("sub", str(k + 1))]
    if k == 2:
        s_ += ttext(x + 10, y + 26, parts + [("n", " = "), ("n", "√"), ("v", "R"), ("vsub", "th"), ("n", "² + "), ("v", "X"), ("n", "²")], color=BLUE)
    else:
        s_ += text(x + 10, y + 16, parts)
s_ += text(XL + 110, Y0 - 14, [("v", "r"), ("sub", "1"), ("n", " &lt; "), ("v", "r"), ("sub", "2"), ("n", " &lt; "), ("v", "r"), ("sub", "3"), ("n", " &lt; "), ("v", "r"), ("sub", "4"), ("t", "，"), ("v", "r"), ("n", " = "), ("v", "R"), ("sub", "2"), ("n", "′ + "), ("v", "R"), ("vsub", "ext"), ("n", "′")])
s_ += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-105-04-3-torque-slip.svg'
out.write_text(s_)
print(out.name, len(s_))
