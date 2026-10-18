"""EE-109-04-5 fig 1: equivalent magnetic circuit of the variable-reluctance system.
Iron mu_r -> inf (zero reluctance); the flux crosses the two rotor gaps in series, each gap of
length g and overlap area A(theta) = r1 * theta * h:  R_g = g / (mu0 r1 theta h),  R = 2 R_g."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 620, 320; XL, XR, YT, YB = 130, 420, 60, 220
s = header(W, H)
s += vsrc(XL, YT, XL, YB, r=22)
s += line(XL, YT, 230, YT) + resistor(230, YT, 320, YT) + line(320, YT, XR, YT)
s += line(XR, YT, XR, YB)
s += line(XR, YB, 320, YB) + resistor(320, YB, 230, YB) + line(230, YB, XL, YB)
s += arrow(345, YT - 16, 400, YT - 16)
s += end_group()
s += ttext(XL - 32, 136, [("v", "ℱ"), ("n", " = "), ("v", "Ni")], anchor="end", color=BLUE)
s += text(275, YT - 22, [("v", "ℛ"), ("vsub", "g")], anchor="middle")
s += text(275, YT + 34, [("t", "氣隙 1")], anchor="middle")
s += text(275, YB + 34, [("v", "ℛ"), ("vsub", "g")], anchor="middle")
s += text(275, YB - 18, [("t", "氣隙 2")], anchor="middle")
s += text(372, YT - 26, [("n", "Φ")], anchor="middle")
s += text(XR + 14, 132, [("t", "定子、轉子鐵心")])
s += text(XR + 14, 156, [("v", "μ"), ("vsub", "r"), ("n", " → ∞"), ("t", "，磁阻 = 0")])
s += text(275, 146, [("v", "ℛ"), ("vsub", "g"), ("n", " = "), ("v", "g"), ("n", "/("), ("v", "μ"), ("sub", "0"), ("v", "r"), ("sub", "1"), ("v", "θh"), ("n", ")")], anchor="middle")
s += text(310, 298, [("t", "兩氣隙串聯："), ("v", "ℛ"), ("n", "("), ("v", "θ"), ("n", ") = 2"), ("v", "ℛ"), ("vsub", "g"), ("t", "，"), ("v", "L"), ("n", " = "), ("v", "N"), ("n", "²/"), ("v", "ℛ"), ("n", "("), ("v", "θ"), ("n", ")")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-109-04-5-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
