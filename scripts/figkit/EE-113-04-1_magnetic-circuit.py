"""EE-113-04-1 fig 1: magnetic equivalent circuit of the two-winding transformer.
Both currents enter dotted ends, so N1 I1 and N2 I2 drive phi_M the same way round the core (clockwise here).
Each leakage reluctance sits directly across its own MMF source (leakage flux links only that winding):
phi_l1 = N1 I1 / R_l1, phi_l2 = N2 I2 / R_l2, phi_M = (N1 I1 + N2 I2) / R_M."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 680, 330; YT, YB = 70, 230
X1, XA, XC, X2 = 110, 230, 450, 570
s = header(W, H)
s += vsrc(X1, YT, X1, YB, r=22)                        # + at top: pushes flux up
s += vsrc(X2, YB, X2, YT, r=22)                        # + at bottom: pushes flux down
s += line(X1, YT, 290, YT) + resistor(290, YT, 390, YT) + line(390, YT, X2, YT)
s += line(X1, YB, X2, YB)
s += line(XA, YT, XA, 105) + resistor(XA, 105, XA, 195) + line(XA, 195, XA, YB)
s += line(XC, YT, XC, 105) + resistor(XC, 105, XC, 195) + line(XC, 195, XC, YB)
s += dot(XA, YT) + dot(XA, YB) + dot(XC, YT) + dot(XC, YB)
s += arrow(305, YT - 18, 375, YT - 18)
s += arrow(375, YB + 16, 305, YB + 16)
s += arrow(XA + 22, 125, XA + 22, 175)
s += arrow(XC - 22, 175, XC - 22, 125)
s += end_group()
s += ttext(X1 - 32, 146, [("v", "N"), ("sub", "1"), ("v", "I"), ("sub", "1")], anchor="end", color=BLUE)
s += ttext(X2 + 32, 146, [("v", "N"), ("sub", "2"), ("v", "I"), ("sub", "2")], color=BLUE)
s += text(340, YT - 26, [("v", "ϕ"), ("vsub", "M")], anchor="middle")
s += text(340, YT + 32, [("v", "ℛ"), ("vsub", "M")], anchor="middle")
s += text(340, YB + 44, [("v", "ϕ"), ("vsub", "M")], anchor="middle")
s += text(XA - 12, 156, [("v", "ℛ"), ("vsub", "l"), ("sub", "1")], anchor="end")
s += text(XA + 30, 156, [("v", "ϕ"), ("vsub", "l"), ("sub", "1")])
s += text(XC + 12, 156, [("v", "ℛ"), ("vsub", "l"), ("sub", "2")])
s += text(XC - 30, 156, [("v", "ϕ"), ("vsub", "l"), ("sub", "2")], anchor="end")
s += text(340, 310, [("t", "兩磁動勢對 "), ("v", "ϕ"), ("vsub", "M"), ("t", " 同向（電流皆由打點端流入）；漏磁阻直接跨在各自磁動勢上")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-113-04-1-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
