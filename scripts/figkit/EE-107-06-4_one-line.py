"""EE-107-06-4 one-line diagram (results of (一)(二)): 3φ 220 V source -> feeder breaker 150 AT, feeder 60 mm²
-> branch bus -> branch 1: 50 AT, 8 mm², 10 HP (27 A); branch 2: 125 AT, 38 mm², 30 HP (78 A).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def breaker(x, y, h=24):
    return f'<rect x="{x - 10}" y="{y - h / 2}" width="20" height="{h}" fill="#fff"/>\n'
def motor(x, y, r=20):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/>\n'
W, H = 640, 470; s = header(W, H); lab = ''
xF, yS, yB = 320, 50, 220
s += busbar(240, 400, yS)
s += line(xF, yS, xF, yB) + breaker(xF, 100)
s += busbar(170, 470, yB)
x1, x2 = 200, 440
for x in (x1, x2):
    s += line(x, yB, x, 380) + breaker(x, 260) + motor(x, 400)
s += end_group()
lab += text(410, yS + 5, [("n", "3φ 220 V")])
lab += text(xF + 20, 105, [("t", "幹線保護 "), ("n", "150 AT")])
lab += text(xF + 20, 160, [("t", "幹線 "), ("n", "60 mm²")]) + text(xF + 20, 182, [("v", "I"), ("vsub", "w,F"), ("n", " = 124.50 A")])
lab += text(xF + 20, 126, [("v", "I"), ("vsub", "OC,F"), ("n", " = 144 A")])
for x, at, mm, hp, i, sub, iw, ioc in ((x1, "50 AT", "8 mm²", "10 HP", "27 A", "10", "33.75 A", "40.50 A"), (x2, "125 AT", "38 mm²", "30 HP", "78 A", "30", "97.50 A", "117 A")):
    lab += text(x + 18, 258, [("n", at)]) + text(x + 18, 280, [("v", "I"), ("vsub", "OC,"), ("sub", sub), ("n", " = " + ioc)])
    lab += text(x + 18, 320, [("t", "分路 "), ("n", mm)]) + text(x + 18, 342, [("v", "I"), ("vsub", "w,"), ("sub", sub), ("n", " = " + iw)])
    lab += text(x, 406, [("n", "M")], anchor="middle")
    lab += text(x, 446, [("n", hp + "，"), ("v", "I"), ("vsub", "FL"), ("n", " = " + i)], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-107-06-4-one-line.svg'
out.write_text(s); print(out.name, len(s))
