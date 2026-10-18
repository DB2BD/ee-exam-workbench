"""EE-114-04-2 fig 1: circuit referred to the primary through the ideal a:1 transformer (a = N1/N2):
source V_s with internal jX_s = j1 ohm in series with R_L' = a^2 R_L; I_1 is the primary current, V_1 the primary terminal voltage."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext

W, H = 560, 270; XS, XL, YT, YB = 120, 400, 60, 200
s = header(W, H)
s += ac_source(XS, 130, r=22)
s += line(XS, 108, XS, YT) + line(XS, YT, 180, YT) + coil(180, YT, 270, YT, turns=4) + line(270, YT, XL, YT)
s += line(XL, YT, XL, 90) + resistor(XL, 90, XL, 170) + line(XL, 170, XL, YB)
s += line(XL, YB, XS, YB) + line(XS, YB, XS, 152)
s += dot(XL, YT) + dot(XL, YB)
s += arrow(300, YT - 14, 360, YT - 14, color=RED)
s += end_group()
s += text(XS - 14, 106, [("n", "+")], anchor="end") + text(XS - 14, 166, [("n", "−")], anchor="end")
s += ttext(XS - 30, 128, [("v", "V"), ("vsub", "s")], anchor="end", color=BLUE)
s += ttext(XS - 30, 150, [("n", "110√2 V")], anchor="end", color=BLUE)
s += text(225, YT - 18, [("v", "jX"), ("vsub", "s"), ("n", " = "), ("v", "j"), ("n", "1 Ω")], anchor="middle")
s += ttext(330, YT - 24, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += text(XL - 14, 124, [("v", "R"), ("vsub", "L"), ("n", "′")], anchor="end")
s += text(XL - 14, 148, [("n", "= "), ("v", "a"), ("n", "²"), ("v", "R"), ("vsub", "L")], anchor="end")
s += ttext(XL + 22, 104, [("n", "+")], color=BLUE)
s += ttext(XL + 22, 136, [("v", "V"), ("sub", "1"), ("n", " = "), ("v", "aV"), ("vsub", "o")], color=BLUE)
s += ttext(XL + 22, 168, [("n", "−")], color=BLUE)
s += text(270, 246, [("t", "二次側負載經理想變壓器 "), ("v", "a"), ("n", " : 1"), ("t", " 折算到一次側")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-114-04-2-referred-circuit.svg'
out.write_text(s)
print(out.name, len(s))
