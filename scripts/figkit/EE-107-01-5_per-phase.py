"""EE-107-01-5: a-phase equivalent of the Y generator feeding the Delta load (Delta converted to Y)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 720, 330
XS, XA, XAP, XL = 80, 300, 540, 640
YT, YB = 90, 270
s = header(W, H)
# source with polarity
s += line(XS, YT, XS, 166) + ac_source(XS, 180) + line(XS, 194, XS, YB)
# generator impedance Zg and line impedance Zl (R then jX)
s += line(XS, YT, 110, YT) + resistor(110, YT, 170, YT, lead=6) + coil(170, YT, 240, YT, turns=3) + line(240, YT, XA, YT)
s += line(XA, YT, 340, YT) + resistor(340, YT, 400, YT, lead=6) + coil(400, YT, 470, YT, turns=3) + line(470, YT, XL, YT)
# load ZY vertical
s += line(XL, YT, XL, 120) + resistor(XL, 120, XL, 180, lead=6) + coil(XL, 180, XL, 240, turns=3) + line(XL, 240, XL, YB)
s += line(XS, YB, XL, YB)
s += terminal(XA, YT) + terminal(XAP, YT)
s += tint_arrow(560, YT - 14, 610, YT - 14)
s += end_group()
s += text(20, 28, [("v", "a"), ("t", " 相單相等效（Δ 已換成 Y；"), ("v", "n"), ("t", " 與 "), ("v", "n"), ("n", "′"), ("t", " 同電位）")])
s += ttext(XS - 22, 172, [("n", "+")], color=BLUE) + ttext(XS - 22, 200, [("n", "−")], color=BLUE)
s += ttext(XS + 26, 176, [("v", "E"), ("vsub", "an"), ("n", " = 120∠0° V")], color=BLUE)
s += text(175, YT - 22, [("v", "Z"), ("vsub", "g"), ("n", " = 0.2 + "), ("v", "j"), ("n", "0.5 Ω")], anchor="middle")
s += text(405, YT - 22, [("v", "Z"), ("vsub", "ℓ"), ("n", " = 0.3 + "), ("v", "j"), ("n", "0.9 Ω")], anchor="middle")
s += text(XA, YT + 24, [("v", "a")], anchor="middle")
s += text(XAP, YT + 24, [("v", "a"), ("n", "′")], anchor="middle")
s += ttext(585, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle", color=RED)
s += text(XL - 16, 172, [("v", "Z"), ("vsub", "Y")], anchor="end")
s += text(XL - 16, 196, [("n", "= 39.50 + "), ("v", "j"), ("n", "28.60 Ω")], anchor="end")
s += text(XS, YB + 24, [("v", "n")], anchor="middle")
s += text(XL, YB + 24, [("v", "n"), ("n", "′")], anchor="middle")
s += text(175, YB + 46, [("t", "發電機（每相）")], anchor="middle")
s += text(405, YB + 46, [("t", "線路")], anchor="middle")
s += text(XL - 20, YB + 46, [("t", "等效 Y 負載")], anchor="middle")
s += footer()
write('EE-107-01-5-per-phase.svg', s)
