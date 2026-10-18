"""EE-113-04-1 fig 2: transformer equivalent circuit with copper loss (R1, R2) and core loss (R_c),
leakage inductances on their own sides, magnetising branch (R_c // jwL_m) on the primary side, ideal N1:N2.
Reference directions as in the crop: I1 enters the primary dot, I2 enters the secondary dot (from the V2 + terminal)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext, terminal

W, H = 720, 320; YT, YB = 80, 230
XL, XN, XC, XM, XP, XS, XR = 30, 250, 250, 320, 392, 448, 690
s = header(W, H)
s += line(XL, YT, 75, YT) + resistor(75, YT, 140, YT) + line(140, YT, 155, YT) + coil(155, YT, 215, YT, turns=4) + line(215, YT, XP, YT)
s += line(XC, YT, XC, 115) + resistor(XC, 115, XC, 195) + line(XC, 195, XC, YB)
s += line(XM, YT, XM, 120) + coil(XM, 120, XM, 190, turns=4) + line(XM, 190, XM, YB)
s += line(XP, YT, XP, 115) + coil(XP, 115, XP, 195, turns=5, r=8).replace('rotate(90.00)', 'rotate(90.00) scale(1 -1)') + line(XP, 195, XP, YB)
s += line(XS, YT, XS, 115) + coil(XS, 115, XS, 195, turns=5, r=8) + line(XS, 195, XS, YB)
s += line(416, 108, 416, 202) + line(424, 108, 424, 202)
s += line(XL, YB, XP, YB) + line(XS, YB, XR, YB)
s += line(XS, YT, 490, YT) + coil(490, YT, 550, YT, turns=4) + line(550, YT, 570, YT) + resistor(570, YT, 635, YT) + line(635, YT, XR, YT)
s += dot(XC, YT) + dot(XC, YB) + dot(XM, YT) + dot(XM, YB)
s += terminal(XL, YT) + terminal(XL, YB) + terminal(XR, YT) + terminal(XR, YB)
s += '<circle cx="402" cy="106" r="3" fill="#000" stroke="none"/>\n<circle cx="438" cy="106" r="3" fill="#000" stroke="none"/>\n'
s += arrow(36, YT - 10, 66, YT - 10, color=RED)
s += arrow(684, YT - 10, 654, YT - 10, color=RED)
s += end_group()
s += ttext(51, YT - 26, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += ttext(669, YT - 26, [("v", "I"), ("sub", "2")], anchor="middle", color=RED)
s += text(XL + 2, YT + 26, [("n", "+")], anchor="middle") + text(XL + 2, YB - 12, [("n", "−")], anchor="middle")
s += ttext(XL + 2, 160, [("v", "V"), ("sub", "1")], anchor="middle", color=BLUE)
s += text(XR - 2, YT + 26, [("n", "+")], anchor="middle") + text(XR - 2, YB - 12, [("n", "−")], anchor="middle")
s += ttext(XR - 2, 160, [("v", "V"), ("sub", "2")], anchor="middle", color=BLUE)
s += text(108, YT - 18, [("v", "R"), ("sub", "1")], anchor="middle")
s += text(185, YT - 18, [("v", "jωL"), ("vsub", "l"), ("sub", "1")], anchor="middle")
s += text(XC - 12, 160, [("v", "R"), ("vsub", "c")], anchor="end")
s += text(XM + 14, 160, [("v", "jωL"), ("vsub", "m")])
s += text(420, YT - 10, [("v", "N"), ("sub", "1"), ("n", " : "), ("v", "N"), ("sub", "2")], anchor="middle")
s += text(420, YB + 24, [("t", "理想")], anchor="middle")
s += text(520, YT - 18, [("v", "jωL"), ("vsub", "l"), ("sub", "2")], anchor="middle")
s += text(602, YT - 18, [("v", "R"), ("sub", "2")], anchor="middle")
s += text(360, 280, [("v", "R"), ("sub", "1"), ("t", "、"), ("v", "R"), ("sub", "2"), ("t", "：銅損　"), ("v", "R"), ("vsub", "c"), ("t", "：鐵損　"), ("v", "L"), ("vsub", "m"), ("t", "：激磁（折算至一次側）")], anchor="middle")
s += text(360, 304, [("t", "激磁電流 "), ("v", "I"), ("vsub", "φ"), ("n", " = "), ("v", "I"), ("sub", "1"), ("n", " + "), ("v", "I"), ("sub", "2"), ("n", "/"), ("v", "a"), ("t", "，"), ("v", "a"), ("n", " = "), ("v", "N"), ("sub", "1"), ("n", "/"), ("v", "N"), ("sub", "2")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-113-04-1-equivalent-circuit.svg'
out.write_text(s)
print(out.name, len(s))
