"""EE-105-04-2 fig 1: 110 V source on the 240 V (HV) winding of a 240/120 V transformer (a = 2);
LV output 55 V; winding currents limited to the rated I_H = 50 A and I_L = 100 A."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import terminal, ttext

W, H = 600, 300; YT, YB = 80, 220; XS, XH, XL, XO = 110, 250, 330, 470
s = header(W, H)
s += ac_source(XS, 150, r=22)
s += line(XS, 128, XS, YT) + line(XS, YT, XH, YT) + line(XH, YT, XH, 110)
s += coil(XH, 110, XH, 190, turns=5, r=8).replace('rotate(90.00)', 'rotate(90.00) scale(1 -1)')
s += line(XH, 190, XH, YB) + line(XH, YB, XS, YB) + line(XS, YB, XS, 172)
s += line(283, 100, 283, 200) + line(297, 100, 297, 200)          # iron core
s += coil(XL, 110, XL, 190, turns=5, r=8)
s += line(XL, 110, XL, YT) + line(XL, YT, XO, YT) + line(XL, 190, XL, YB) + line(XL, YB, XO, YB)
s += terminal(XO, YT) + terminal(XO, YB)
s += arrow(160, YT - 14, 210, YT - 14, color=RED)
s += arrow(370, YT - 14, 420, YT - 14, color=RED)
s += end_group()
s += text(XS - 30, 140, [("n", "+")], anchor="end") + text(XS - 30, 172, [("n", "−")], anchor="end")
s += ttext(XS - 30, 158, [("v", "V"), ("vsub", "H"), ("n", " = 110 V")], anchor="end", color=BLUE)
s += text(XO + 8, YT + 5, [("n", "+")]) + text(XO + 8, YB + 5, [("n", "−")])
s += ttext(XO + 8, 156, [("v", "V"), ("vsub", "L"), ("n", " = 55 V")], color=BLUE)
s += ttext(185, YT - 24, [("v", "I"), ("vsub", "H"), ("n", " ≤ 50 A")], anchor="middle", color=RED)
s += ttext(395, YT - 24, [("v", "I"), ("vsub", "L"), ("n", " ≤ 100 A")], anchor="middle", color=RED)
s += text(XH - 14, 174, [("v", "V"), ("vsub", "H"), ("sub", ","), ("vsub", "rated")], anchor="end")
s += text(XH - 14, 196, [("n", "= 240 V")], anchor="end")
s += text(XL + 14, 174, [("v", "V"), ("vsub", "L"), ("sub", ","), ("vsub", "rated")])
s += text(XL + 14, 196, [("n", "= 120 V")])
s += text(290, 250, [("v", "a"), ("n", " = 240 / 120 = 2")], anchor="middle")
s += text(290, 276, [("t", "高壓側（240 V 繞組）接電源，低壓側輸出")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-105-04-2-connection.svg'
out.write_text(s)
print(out.name, len(s))
