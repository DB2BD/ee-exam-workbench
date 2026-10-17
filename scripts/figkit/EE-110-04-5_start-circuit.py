"""EE-110-04-5 fig 1: per-phase equivalent circuit at start (s = 1, R_2/s = R_2).
jX_st in series between the source and R_1, bypassed by SW (closed in (一), open in (二)).
Z_p = jX_m // (R_2 + jX_2) is the dashed box; I_s and I_2' follow the reference directions used in the text."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext
from power_parts import switch, dashed

W, H = 720, 310; YT, YB = 80, 240
XS, XA, XB, XN, XR = 112, 150, 236, 440, 590
s = header(W, H)
s += vsrc(XS, YT, XS, YB, r=20)
s += line(XS, YT, XA, YT) + coil(XA, YT, XB, YT, turns=4) + line(XB, YT, 256, YT)
s += line(XA, YT, XA, 125) + switch(XA, 125, XB, 125, closed=True) + line(XB, 125, XB, YT)
s += dot(XA, YT) + dot(XB, YT)
s += resistor(256, YT, 320, YT) + line(320, YT, 345, YT) + coil(345, YT, 405, YT, turns=4) + line(405, YT, XN, YT)
s += line(XN, YT, XN, 125) + coil(XN, 125, XN, 195, turns=4) + line(XN, 195, XN, YB)
s += line(XN, YT, 480, YT) + coil(480, YT, 540, YT, turns=4) + line(540, YT, XR, YT)
s += line(XR, YT, XR, 125) + resistor(XR, 125, XR, 195) + line(XR, 195, XR, YB)
s += line(XS, YB, XR, YB) + dot(XN, YT) + dot(XN, YB)
s += dashed(427, 36, 708, 36) + dashed(708, 36, 708, 262) + dashed(708, 262, 427, 262) + dashed(427, 262, 427, 36)
s += arrow(264, YT + 22, 312, YT + 22, color=RED)
s += arrow(486, YT + 22, 534, YT + 22, color=RED)
s += end_group()
s += ttext(XS - 26, 156, [("v", "V"), ("vsub", "φ")], anchor="end", color=BLUE)
s += ttext(XS - 26, 178, [("n", "120.089 V")], anchor="end", color=BLUE)
s += text((XA + XB) / 2, YT - 18, [("v", "jX"), ("vsub", "st")], anchor="middle")
s += text((XA + XB) / 2, 160, [("v", "SW")], anchor="middle")
s += text(288, YT - 34, [("v", "R"), ("sub", "1")], anchor="middle")
s += text(288, YT - 16, [("n", "0.10 Ω")], anchor="middle")
s += text(375, YT - 34, [("v", "jX"), ("sub", "1")], anchor="middle")
s += text(375, YT - 16, [("v", "j"), ("n", "0.21 Ω")], anchor="middle")
s += ttext(288, YT + 50, [("v", "I"), ("vsub", "s")], anchor="middle", color=RED)
s += text(XN + 16, 156, [("v", "jX"), ("vsub", "m")])
s += text(XN + 16, 178, [("v", "j"), ("n", "10 Ω")])
s += text(510, YT - 34, [("v", "jX"), ("sub", "2")], anchor="middle")
s += text(510, YT - 16, [("v", "j"), ("n", "0.21 Ω")], anchor="middle")
s += ttext(510, YT + 50, [("v", "I"), ("sub", "2"), ("n", "′")], anchor="middle", color=RED)
s += text(XR + 14, 150, [("v", "R"), ("sub", "2"), ("n", "/"), ("v", "s")])
s += text(XR + 14, 172, [("n", "= 0.07 Ω")])
s += text(XR + 14, 194, [("t", "（"), ("v", "s"), ("n", " = 1"), ("t", "）")])
s += text(XR - 8, 228, [("v", "Z"), ("vsub", "p")], anchor="end")
s += text(360, 294, [("t", "（一）SW 閉合："), ("v", "jX"), ("vsub", "st"), ("t", " 被短路　（二）SW 打開："), ("v", "jX"), ("vsub", "st"), ("t", " 串入")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-110-04-5-start-circuit.svg'
out.write_text(s)
print(out.name, len(s))
