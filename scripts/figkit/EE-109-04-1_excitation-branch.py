"""EE-109-04-1 fig 1: primary side of the given equivalent circuit (R_P = 0) at rated voltage.
mu -> inf makes X_M -> inf (open), so the excitation current I_phi flows only through R_C (I_phi = I_C, I_M = 0)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext, terminal

W, H = 660, 300; YT, YB = 70, 220; XS, XC, XM, XT = 60, 290, 400, 520
s = header(W, H)
s += line(XS, YT, 120, YT) + coil(120, YT, 200, YT, turns=4) + line(200, YT, XT, YT)
s += line(XS, YB, XT, YB)
s += terminal(XS, YT) + terminal(XS, YB)
s += line(XC, YT, XC, 105) + resistor(XC, 105, XC, 185) + line(XC, 185, XC, YB)
# X_M branch (X_M -> inf behaves as an open circuit; labelled, not redrawn)
s += line(XM, YT, XM, 110) + coil(XM, 110, XM, 180, turns=4) + line(XM, 180, XM, YB)
s += dot(XC, YT) + dot(XC, YB) + dot(XM, YT) + dot(XM, YB)
# ideal-transformer primary winding N_P
s += line(XT, YT, XT, 110) + coil(XT, 110, XT, 180, turns=4).replace('rotate(90.00)', 'rotate(90.00) scale(1 -1)') + line(XT, 180, XT, YB)
s += arrow(215, YT - 12, 275, YT - 12, color=RED)
s += arrow(XC + 18, 120, XC + 18, 170, color=RED)
s += arrow(XS - 2, YB - 10, XS - 2, YT + 10, color=BLUE)
s += end_group()
s += text(XS - 14, YT + 6, [("n", "+")], anchor="end") + text(XS - 14, YB + 6, [("n", "−")], anchor="end")
s += ttext(XS + 10, 150, [("v", "V"), ("vsub", "P"), ("n", " = 2400 V")], color=BLUE)
s += text(160, YT - 18, [("v", "jX"), ("vsub", "P")], anchor="middle")
s += text(160, YT + 30, [("t", "（"), ("v", "R"), ("vsub", "P"), ("n", " = 0"), ("t", "）")], anchor="middle")
s += ttext(245, YT - 26, [("v", "I"), ("vsub", "P"), ("n", " = "), ("v", "I"), ("vsub", "ϕ")], anchor="middle", color=RED)
s += text(XC - 14, 150, [("v", "R"), ("vsub", "C")], anchor="end")
s += ttext(XC + 26, 150, [("v", "I"), ("vsub", "C")], color=RED)
s += text(XM + 14, 150, [("v", "jX"), ("vsub", "M"), ("n", " → ∞")])
s += text(XM + 14, 126, [("t", "（開路）")])
s += ttext(XM + 14, 176, [("v", "I"), ("vsub", "M"), ("n", " = 0")], color=RED)
s += text(XT + 16, 150, [("v", "N"), ("vsub", "P")])
s += text(XT + 16, 176, [("t", "（理想變壓器，")])
s += text(XT + 16, 198, [("t", "二次側開路）")])
s += text(330, YB + 44, [("t", "鐵心 "), ("v", "μ"), ("n", " → ∞"), ("t", "：主磁路磁阻 → 0，"), ("v", "X"), ("vsub", "M"), ("n", " → ∞"), ("t", "，激磁支路只剩 "), ("v", "R"), ("vsub", "C")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-109-04-1-excitation-branch.svg'
out.write_text(s)
print(out.name, len(s))
