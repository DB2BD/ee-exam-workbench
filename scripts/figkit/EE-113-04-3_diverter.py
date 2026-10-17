import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 330; YT, YB, YD = 100, 260, 50
def panel(x0, diverter):
    s = ''
    xs, xr1, xr2, xf1, xf2, xa = x0 + 40, x0 + 70, x0 + 130, x0 + 160, x0 + 240, x0 + 300
    s += f'<circle cx="{xs}" cy="180" r="16"/>\n'
    s += line(xs, YT, xs, 164) + line(xs, 196, xs, YB)
    s += line(xs, YT, xr1, YT) + resistor(xr1, YT, xr2, YT) + line(xr2, YT, xf1, YT)
    s += coil(xf1, YT, xf2, YT, turns=5) + line(xf2, YT, xa, YT)
    s += line(xa, YT, xa, 162) + f'<circle cx="{xa}" cy="180" r="18"/>\n' + line(xa, 198, xa, YB)
    s += line(xs, YB, xa, YB)
    if diverter:
        s += dot(xf1 - 10, YT) + dot(xf2 + 10, YT)
        s += line(xf1 - 10, YT, xf1 - 10, YD) + resistor(xf1 - 10, YD, xf2 + 10, YD) + line(xf2 + 10, YD, xf2 + 10, YT)
        s += arrow(x0 + 70, YT + 22, x0 + 115, YT + 22, color=RED)
        s += arrow(xf1 + 10, YT + 40, xf1 + 60, YT + 40, color=RED)
        s += arrow(xf1 + 10, YD - 14, xf1 + 60, YD - 14, color=RED)
    else:
        s += arrow(x0 + 70, YT + 22, x0 + 115, YT + 22, color=RED)
    return s
s = header(W, H)
s += panel(10, False) + panel(370, True)
s += end_group()
for x0, sub in ((10, "1"), (370, "2")):
    xs, xa = x0 + 40, x0 + 300
    s += text(xs, 186, [("n", "+")], anchor="middle") if False else ''
    s += text(xs - 22, 168, [("n", "+")], anchor="middle") + text(xs - 22, 204, [("n", "−")], anchor="middle")
    s += ctext(BLUE, xs + 22, 186, [("v", "V"), ("vsub", "t")])
    s += ctext(BLUE, xs + 22, 206, [("n", "300 V")])
    s += text(x0 + 100, YT - 18, [("v", "R"), ("vsub", "a")], anchor="middle")
    s += text(x0 + 200, YT - 18 if x0 == 10 else YT + 26, [("v", "R"), ("vsub", "s")], anchor="middle")
    s += text(xa, 186, [("n", "M")], anchor="middle")
    s += ctext(BLUE, xa - 22, 160, [("n", "+")], anchor="middle") + ctext(BLUE, xa - 22, 212, [("n", "−")], anchor="middle")
    s += ctext(BLUE, xa - 30, 190, [("v", "E"), ("vsub", "a"), ("sub", sub)], anchor="end")
s += ctext(RED, 102, YT + 44, [("v", "I"), ("vsub", "a"), ("sub", "1"), ("n", " = 60 A")], anchor="middle")
s += text(170, 300, [("t", "(a) 分流前：場電流 "), ("v", "I"), ("vsub", "f"), ("sub", "1"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "1")], anchor="middle")
s += ctext(RED, 462, YT + 44, [("v", "I"), ("vsub", "a"), ("sub", "2")], anchor="middle")
s += ctext(RED, 565, YT + 64, [("v", "I"), ("vsub", "f"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "a"), ("sub", "2"), ("n", "/2")], anchor="middle")
s += ctext(RED, 640, YD - 20, [("v", "I"), ("vsub", "a"), ("sub", "2"), ("n", "/2")])
s += text(560, YD + 26, [("v", "R"), ("vsub", "d")], anchor="middle")
s += text(530, 300, [("t", "(b) 分流後："), ("v", "R"), ("vsub", "d"), ("n", " ∥ "), ("v", "R"), ("vsub", "s"), ("n", " = 0.05 Ω")], anchor="middle")
s += text(360, 324, [("v", "R"), ("vsub", "a"), ("n", " = "), ("v", "R"), ("vsub", "s"), ("n", " = "), ("v", "R"), ("vsub", "d"), ("n", " = 0.10 Ω")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-113-04-3-diverter.svg'), 'w').write(s)
print(len(s))
