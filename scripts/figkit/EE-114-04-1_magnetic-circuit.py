"""EE-114-04-1 fig 1: equivalent magnetic circuit of the two-pole structure.
mu_c -> inf: iron reluctances are zero (the two halves of the outer ring are short circuits);
the flux crosses two identical air gaps in series: R_eq = 2 R_g, Phi = NI / R_eq."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 600, 312; XL, XR, YT, YB = 130, 420, 60, 220
s = header(W, H)
s += vsrc(XL, YT, XL, YB, r=22)
s += line(XL, YT, 230, YT) + resistor(230, YT, 320, YT) + line(320, YT, XR, YT)
s += line(XR, YT, XR, YB)
s += line(XR, YB, 320, YB) + resistor(320, YB, 230, YB) + line(230, YB, XL, YB)
s += arrow(345, YT - 16, 400, YT - 16)
s += end_group()
s += ttext(XL - 32, 136, [("v", "ℱ"), ("n", " = "), ("v", "NI")], anchor="end", color=BLUE)
s += text(275, YT - 22, [("v", "ℛ"), ("vsub", "g")], anchor="middle")
s += text(275, YT + 34, [("t", "氣隙 1")], anchor="middle")
s += text(275, YB + 34, [("v", "ℛ"), ("vsub", "g")], anchor="middle")
s += text(275, YB - 18, [("t", "氣隙 2")], anchor="middle")
s += text(372, YT - 26, [("n", "Φ")], anchor="middle")
s += text(XR + 14, 132, [("t", "鐵心 "), ("v", "μ"), ("vsub", "c"), ("n", " → ∞")])
s += text(XR + 14, 156, [("t", "鐵心磁阻 = 0")])
s += text(275, 140, [("v", "ℛ"), ("vsub", "g"), ("n", " = "), ("v", "l"), ("vsub", "g"), ("n", "/("), ("v", "μ"), ("sub", "0"), ("v", "A"), ("vsub", "g"), ("n", ")")], anchor="middle")
s += text(300, 298, [("t", "兩氣隙串聯："), ("v", "ℛ"), ("vsub", "eq"), ("n", " = 2"), ("v", "ℛ"), ("vsub", "g"), ("t", "，"), ("n", "Φ = "), ("v", "NI"), ("n", "/"), ("v", "ℛ"), ("vsub", "eq")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-114-04-1-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
