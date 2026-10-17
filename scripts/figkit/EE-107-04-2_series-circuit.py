"""EE-107-04-2 fig 1: series dc motor; field winding in series with the armature, R_AS lumps both resistances."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 620, 290; YT, YB = 70, 220; XS, XM = 110, 480
s = header(W, H)
s += f'<circle cx="{XS}" cy="145" r="24"/>\n'
s += f'<circle cx="{XM}" cy="145" r="24"/>\n'
s += line(XS, 121, XS, YT) + line(XS, YT, 180, YT)
s += resistor(180, YT, 260, YT)
s += line(260, YT, 300, YT) + coil(300, YT, 390, YT, turns=5) + line(390, YT, XM, YT) + line(XM, YT, XM, 121)
s += line(XS, 169, XS, YB) + line(XS, YB, XM, YB) + line(XM, 169, XM, YB)
s += arrow(130, YT - 16, 170, YT - 16, color=RED)
s += end_group()
s += text(XS, 139, [("n", "+")], anchor="middle")
s += text(XS, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XS - 34, 140, [("v", "V"), ("vsub", "t")], anchor="end")
s += ctext(BLUE, XS - 34, 162, [("n", "= 50 V")], anchor="end")
s += text(XM, 139, [("n", "+")], anchor="middle")
s += text(XM, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XM + 34, 150, [("v", "E"), ("vsub", "a")])
s += ctext(RED, 150, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
s += text(220, YT + 32, [("v", "R"), ("vsub", "AS"), ("n", " = 0.05 Ω")], anchor="middle")
s += text(345, YT + 32, [("t", "串激場繞組")], anchor="middle")
s += text(345, YT + 52, [("t", "（電流＝"), ("v", "I"), ("vsub", "a"), ("t", "）")], anchor="middle")
s += text(295, 262, [("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "AS"), ("t", "；"), ("v", "R"), ("vsub", "AS"), ("t", "＝電樞＋串激場電阻")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-107-04-2-series-circuit.svg'), 'w').write(s)
print(len(s))
