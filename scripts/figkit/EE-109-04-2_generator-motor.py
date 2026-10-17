"""EE-109-04-2 fig 1: armature loop as generator (I_a leaves E_a) and as motor (I_a enters E_a)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 305; YT, YB = 85, 215
s = header(W, H)
def panel(x0, gen):
    xa, xt = x0 + 50, x0 + 260          # armature (E_a) and terminals
    out = f'<circle cx="{xa}" cy="150" r="24"/>\n'
    out += line(xa, 126, xa, YT) + line(xa, YT, xa + 50, YT)
    out += resistor(xa + 50, YT, xa + 130, YT)
    out += line(xa + 130, YT, xt - 4, YT) + line(xa, 174, xa, YB) + line(xa, YB, xt - 4, YB)
    out += f'<circle cx="{xt}" cy="{YT}" r="4" fill="#fff"/>\n<circle cx="{xt}" cy="{YB}" r="4" fill="#fff"/>\n'
    if gen:
        out += arrow(xa + 140, YT - 16, xa + 185, YT - 16, color=RED)
    else:
        out += arrow(xa + 185, YT - 16, xa + 140, YT - 16, color=RED)
    return out
s += panel(20, True) + panel(370, False)
s += end_group()
for x0, gen in ((20, True), (370, False)):
    xa, xt = x0 + 50, x0 + 260
    s += text(xa, 144, [("n", "+")], anchor="middle") + text(xa, 168, [("n", "−")], anchor="middle")
    s += text(xa + 30, 155, [("v", "E"), ("vsub", "a")])
    s += text(xa + 90, YT + 30, [("v", "R"), ("vsub", "a"), ("n", " = 0.02 Ω")], anchor="middle")
    s += ctext(RED, xa + 162, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
    s += ctext(BLUE, xt + 10, YT + 22, [("n", "+")]) + ctext(BLUE, xt + 10, YB - 8, [("n", "−")])
    s += ctext(BLUE, xt + 10, 155, [("v", "V"), ("vsub", "t")])
s += text(40, 247, [("t", "(a) 發電機："), ("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " − "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a")])
s += text(40, 271, [("t", "輸出 "), ("v", "P"), ("vsub", "out"), ("n", " = "), ("v", "V"), ("vsub", "t"), ("v", "I"), ("vsub", "a"), ("n", " = 21.5 kW")])
s += text(390, 247, [("t", "(b) 電動機："), ("v", "V"), ("vsub", "t"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a")])
s += text(390, 271, [("v", "V"), ("vsub", "t"), ("n", " = 213 V，"), ("v", "E"), ("vsub", "a"), ("v", "I"), ("vsub", "a"), ("n", " = 21.5 kW")])
s += text(W / 2, 26, [("t", "固定激磁："), ("v", "E"), ("vsub", "a"), ("n", " = "), ("v", "Kn"), ("t", "，"), ("v", "K"), ("n", " = 125/3000 V/rpm")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-109-04-2-generator-motor.svg'), 'w').write(s)
print(len(s))
