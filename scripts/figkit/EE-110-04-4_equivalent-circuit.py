"""EE-110-04-4 fig 1: PM dc motor armature circuit, I_a flows from the 180 V supply into the armature."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 270; YT, YB = 60, 210; XS, XM = 120, 450
s = header(W, H)
s += f'<circle cx="{XS}" cy="135" r="24"/>\n'                 # dc supply
s += f'<circle cx="{XM}" cy="135" r="24"/>\n'                 # armature
s += line(XS, 111, XS, YT) + line(XS, YT, 230, YT)
s += resistor(230, YT, 330, YT)
s += line(330, YT, XM, YT) + line(XM, YT, XM, 111)
s += line(XS, 159, XS, YB) + line(XS, YB, XM, YB) + line(XM, 159, XM, YB)
s += arrow(170, YT - 16, 215, YT - 16, color=RED)
s += end_group()
s += text(XS, 129, [("n", "+")], anchor="middle")
s += text(XS, 153, [("n", "−")], anchor="middle")
s += ctext(BLUE, XS - 34, 140, [("v", "V"), ("vsub", "t"), ("n", " = 180 V")], anchor="end")
s += text(XM, 129, [("n", "+")], anchor="middle")
s += text(XM, 153, [("n", "−")], anchor="middle")
s += ctext(BLUE, XM + 34, 140, [("v", "E"), ("vsub", "a")])
s += ctext(RED, 192, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
s += text(280, YT + 32, [("v", "R"), ("vsub", "a"), ("n", " = 2.01 Ω")], anchor="middle")
s += text(XM - 34, 170, [("t", "永磁場："), ("v", "ϕ"), ("t", " 固定")], anchor="end")
s += text(XM - 34, 190, [("t", "（無場繞組）")], anchor="end")
s += text(285, 250, [("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a"), ("t", "，"), ("v", "E"), ("vsub", "a"), ("n", " = "), ("v", "K"), ("v", "n")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-110-04-4-equivalent-circuit.svg'), 'w').write(s)
print(len(s))
