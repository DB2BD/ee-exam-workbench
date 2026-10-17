"""EE-105-04-5 fig 1: separately excited dc motor; armature loop (motor convention) + independent field circuit."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 300; YT, YB = 70, 220; XS, XM = 110, 370
s = header(W, H)
s += f'<circle cx="{XS}" cy="145" r="24"/>\n'                 # dc supply V_t
s += f'<circle cx="{XM}" cy="145" r="24"/>\n'                 # armature back emf E_a
s += line(XS, 121, XS, YT) + line(XS, YT, 200, YT)
s += resistor(200, YT, 290, YT)
s += line(290, YT, XM, YT) + line(XM, YT, XM, 121)
s += line(XS, 169, XS, YB) + line(XS, YB, XM, YB) + line(XM, 169, XM, YB)
s += arrow(150, YT - 16, 195, YT - 16, color=RED)
# separate field circuit
XF, XL = 545, 630
s += f'<circle cx="{XF}" cy="145" r="18"/>\n'
s += line(XF, 127, XF, YT) + line(XF, YT, XL, YT) + line(XL, YT, XL, 105)
s += coil(XL, 105, XL, 185, turns=4) + line(XL, 185, XL, YB) + line(XL, YB, XF, YB) + line(XF, YB, XF, 163)
s += arrow(565, YT - 14, 605, YT - 14, color=RED)
s += f'<rect x="490" y="30" width="182" height="210" stroke-dasharray="6 4" stroke-width="1"/>\n'
s += end_group()
s += text(XS, 139, [("n", "+")], anchor="middle")
s += text(XS, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XS - 34, 151, [("v", "V"), ("vsub", "t")], anchor="end")
s += text(XM, 139, [("n", "+")], anchor="middle")
s += text(XM, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XM + 34, 151, [("v", "E"), ("vsub", "a"), ("n", " ∝ Φ"), ("v", "n")])
s += ctext(RED, 172, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
s += text(245, YT + 32, [("v", "R"), ("vsub", "a"), ("n", " = 0.1 Ω")], anchor="middle")
s += text(XF, 150, [("v", "V"), ("vsub", "f")], anchor="middle")
s += ctext(RED, 585, YT - 26, [("v", "I"), ("vsub", "f")], anchor="middle")
s += text(XL - 12, 150, [("v", "L"), ("vsub", "f")], anchor="end")
s += text(581, 262, [("t", "獨立場電路："), ("v", "I"), ("vsub", "f"), ("n", " 12 A → 6 A")], anchor="middle")
s += text(240, 262, [("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a"), ("t", "（電動機慣例）")], anchor="middle")
s += text(240, 288, [("v", "T"), ("n", " ∝ Φ"), ("v", "I"), ("vsub", "a")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-105-04-5-armature-circuit.svg'), 'w').write(s)
print(len(s))
