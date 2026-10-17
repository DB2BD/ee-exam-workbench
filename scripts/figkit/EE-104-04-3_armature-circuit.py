"""EE-104-04-3 fig 1: permanent-magnet dc motor armature loop (motor convention); flux fixed by the magnets."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 560, 290; YT, YB = 70, 220; XS, XM = 120, 380
s = header(W, H)
s += f'<circle cx="{XS}" cy="145" r="24"/>\n'                 # dc supply V_t
s += f'<circle cx="{XM}" cy="145" r="24"/>\n'                 # back emf E_a
s += line(XS, 121, XS, YT) + line(XS, YT, 210, YT)
s += resistor(210, YT, 300, YT)
s += line(300, YT, XM, YT) + line(XM, YT, XM, 121)
s += line(XS, 169, XS, YB) + line(XS, YB, XM, YB) + line(XM, 169, XM, YB)
s += arrow(160, YT - 16, 205, YT - 16, color=RED)
s += end_group()
s += text(XS, 139, [("n", "+")], anchor="middle")
s += text(XS, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XS - 34, 151, [("v", "V"), ("vsub", "t")], anchor="end")
s += text(XM, 139, [("n", "+")], anchor="middle")
s += text(XM, 163, [("n", "−")], anchor="middle")
s += ctext(BLUE, XM + 34, 140, [("v", "E"), ("vsub", "a"), ("n", " = "), ("v", "K"), ("vsub", "ϕ"), ("v", "ω")])
s += text(XM + 34, 164, [("v", "T"), ("n", " = "), ("v", "K"), ("vsub", "ϕ"), ("v", "I"), ("vsub", "a")])
s += ctext(RED, 182, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
s += text(255, YT + 32, [("v", "R"), ("vsub", "a"), ("n", " = 0.05 Ω")], anchor="middle")
s += text(XM + 34, 196, [("t", "永久磁鐵：Φ 固定")])
s += text(250, 262, [("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a"), ("t", "（電動機慣例）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-104-04-3-armature-circuit.svg'), 'w').write(s)
print(len(s))
