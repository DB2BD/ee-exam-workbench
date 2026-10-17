import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap(x1, y1, x2, y2, gap=6, plate=12):
    """Capacitor centred on the segment: two plates perpendicular to it."""
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    a = (mx - ux * gap, my - uy * gap); b = (mx + ux * gap, my + uy * gap)
    o = line(x1, y1, *a) + line(*b, x2, y2)
    for px, py in (a, b):
        o += line(px - nx * plate, py - ny * plate, px + nx * plate, py + ny * plate)
    return o
W, H = 560, 350; s = header(W, H)
ys = {"a": 50, "b": 80, "c": 110}
A, B, Cn = (280, 150), (180, 290), (380, 290)
for n, y in ys.items():
    s += line(40, y, 520, y)
s += line(A[0], ys["a"], *A) + dot(A[0], ys["a"])
s += line(110, ys["b"], 110, B[1]) + line(110, B[1], *B) + dot(110, ys["b"])
s += line(480, ys["c"], 480, Cn[1]) + line(480, Cn[1], *Cn) + dot(480, ys["c"])
s += cap(*A, *B) + cap(*A, *Cn) + cap(*B, *Cn)
s += dot(*A) + dot(*B) + dot(*Cn)
s += arrow(150, ys["a"] - 12, 200, ys["a"] - 12, RED)
s += arrow(230, 312, 330, 312, RED)
s += end_group()
for n, y in ys.items():
    s += text(28, y + 5, [("v", n)], anchor="end")
s += ctext(RED, 210, 30, [("v", "I"), ("vsub", "L"), ("n", " = 57.35 A")], anchor="start")
s += ctext(RED, 280, 336, [("v", "I"), ("vsub", "ϕ"), ("n", " = 33.11 A")], anchor="middle")
s += text(252, 234, [("v", "C")], anchor="middle") + text(308, 234, [("v", "C")], anchor="middle")
s += text(280, 266, [("v", "C"), ("n", " = 13.31 μF")], anchor="middle")
s += ctext(BLUE, 352, 214, [("v", "V"), ("vsub", "LL"), ("n", " = 6600 V")], anchor="start")
s += ctext(BLUE, A[0] + 10, A[1] - 2, [("n", "+")]) + ctext(BLUE, Cn[0] + 4, Cn[1] - 10, [("n", "−")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-107-06-5-delta-bank.svg'), 'w').write(s)
print(len(s))
