"""EE-104-04-2 fig 1: qualitative magnetization curve Phi_m(I_ex) of the core.
Rated V/f puts Phi_m,60 near the knee; at 50 Hz Phi_m,50 = 1.20 Phi_m,60 lies in saturation, so the
excitation current I_ex grows far more than 20 %. Curve shape is illustrative (no B-H data in the stem)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from power_parts import dashed, poly
from circuit_parts import ttext

phi = lambda i: 1.06 * math.tanh(1.25 * i) + 0.05 * i       # normalized, Phi_m,60 = 1


def inv(target):
    lo, hi = 0.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if phi(mid) < target else (lo, mid)
    return lo


W, H = 600, 360; X0, Y0, KX, KY = 90, 300, 95.0, 180.0
P = lambda i, f: (X0 + KX * i, Y0 - KY * f)
i60, i50 = inv(1.0), inv(1.2)
s = header(W, H)
s += arrow(X0, Y0, X0 + KX * 4.9, Y0) + arrow(X0, Y0, X0, 40)
s += poly([P(k * 0.02, phi(k * 0.02)) for k in range(0, 236)], w=1.8)
for i, f in ((i60, 1.0), (i50, 1.2)):
    x, y = P(i, f)
    s += dashed(X0, y, x, y) + dashed(x, y, x, Y0) + dot(x, y)
x60, _ = P(i60, 1.0); x50, _ = P(i50, 1.2)
s += arrow(x60, Y0 + 30, x50, Y0 + 30, color=RED)
s += end_group()
s += text(X0 + KX * 4.9, Y0 + 24, [("v", "I"), ("vsub", "ex")], anchor="end")
s += text(X0 + 10, 44, [("n", "Φ"), ("vsub", "m")])
s += ttext(X0 - 8, Y0 - KY * 1.0 + 5, [("n", "Φ"), ("vsub", "m"), ("sub", ",60")], anchor="end", color=BLUE)
s += ttext(X0 - 8, Y0 - KY * 1.2 + 5, [("n", "1.20"), ("n", "Φ"), ("vsub", "m"), ("sub", ",60")], anchor="end", color=BLUE)
s += ttext(x60, Y0 + 20, [("v", "I"), ("vsub", "ex"), ("sub", ",60")], anchor="middle", color=RED)
s += ttext(x50, Y0 + 20, [("v", "I"), ("vsub", "ex"), ("sub", ",50")], anchor="middle", color=RED)
s += text((x60 + x50) / 2, Y0 + 50, [("t", "激磁電流大增")], anchor="middle")
s += text(x60 + 14, Y0 - KY * 1.0 + 22, [("t", "60 Hz：膝點附近")])
s += text(x50 + 12, Y0 - KY * 1.2 - 18, [("t", "50 Hz：飽和區")])
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-104-04-2-magnetization.svg'
out.write_text(s)
print(out.name, len(s), round(i60, 3), round(i50, 3))
