"""EE-109-04-3 fig 1: per-phase equivalent circuit without the magnetizing branch (core effects neglected):
V_phi drives one series loop R_1 + jX_1 + jX_2 + R_2/s, so I_1 = I_2."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext

W, H = 680, 290; YT, YB = 80, 220; XS, XR = 70, 570
s = header(W, H)
s += line(XS, YT, XS, 130) + ac_source(XS, 150, r=20) + line(XS, 170, XS, YB)
s += line(XS, YT, 110, YT) + resistor(110, YT, 190, YT) + line(190, YT, 220, YT)
s += coil(220, YT, 300, YT, turns=4) + line(300, YT, 360, YT)
s += coil(360, YT, 440, YT, turns=4) + line(440, YT, XR, YT)
s += line(XR, YT, XR, 110) + resistor(XR, 110, XR, 190) + line(XR, 190, XR, YB)
s += line(XS, YB, XR, YB)
s += arrow(470, YT - 16, 540, YT - 16, color=RED)
s += end_group()
s += text(XS - 28, 142, [("n", "+")], anchor="middle") + text(XS - 28, 172, [("n", "−")], anchor="middle")
s += ttext(XS + 28, 156, [("v", "V"), ("vsub", "ϕ")], color=BLUE)
s += text(150, YT + 30, [("v", "R"), ("sub", "1"), ("n", " = 0.3 Ω")], anchor="middle")
s += text(260, YT - 22, [("v", "jX"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.5 Ω")], anchor="middle")
s += text(400, YT - 22, [("v", "jX"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "0.4 Ω")], anchor="middle")
s += ttext(505, YT - 26, [("v", "I"), ("sub", "1"), ("n", " = "), ("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += text(XR + 14, 146, [("v", "R"), ("sub", "2"), ("n", "/"), ("v", "s")])
s += text(XR + 14, 170, [("n", "= 0.2/"), ("v", "s"), ("n", " Ω")])
s += text(335, YB + 44, [("t", "不計鐵心效應：無激磁支路，定子與轉子為同一串聯迴路")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-109-04-3-equivalent-circuit.svg'
out.write_text(s)
print(out.name, len(s))
