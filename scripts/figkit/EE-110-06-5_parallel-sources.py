import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 360; s = header(W, H); y, g, sy = 90, 290, 240
xs = [130, 275, 420, 565]; xf = 688
s += busbar(110, 700, y)
for x in xs:
    s += dot(x, y) + ac_source(x, sy) + line(x, sy + 14, x, g)
s += coil(xs[0], y, xs[0], 226) + coil(xs[1], y, xs[1], 226) + coil(xs[2], y, xs[2], 226)
s += coil(xs[3], y, xs[3], 158, turns=3) + coil(xs[3], 158, xs[3], 226, turns=3)
s += f'<path d="M{xf} {y} L{xf} {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n'
s += line(110, g, 700, g)
for x in xs:
    s += arrow(x - 14, 200, x - 14, 120, RED)
s += arrow(702, 140, 702, 230, RED)
s += end_group()
s += text(110, 72, [("n", "3.45 kV "), ("t", "母線")], anchor="start")
s += ctext(RED, 715, 72, [("n", "F1："), ("v", "I"), ("vsub", "F"), ("sub", "1"), ("n", " = 0.9139 pu")], anchor="end")
lab = [(xs[0], [("v", "X"), ("vsub", "src"), ("n", " = 1.467")], [("v", "I"), ("vsub", "src"), ("n", " = 0.6818")]),
       (xs[1], [("v", "X"), ("vsub", "SM"), ("n", " = 7.50")], [("v", "I"), ("vsub", "SM"), ("n", " = 0.1333")]),
       (xs[2], [("v", "X"), ("vsub", "IM"), ("sub", "1"), ("n", " = 20")], [("v", "I"), ("vsub", "IM"), ("sub", "1"), ("n", " = 0.05")]),
       (xs[3], None, [("v", "I"), ("vsub", "IM"), ("sub", "2"), ("n", " = 0.04878")])]
for x, nm, iv in lab:
    if nm: s += text(x + 14, 164, nm)
    s += ctext(RED, x - 20, 124, iv, anchor="end")
s += text(xs[3] + 14, 128, [("v", "X"), ("vsub", "T"), ("sub", "2"), ("n", " = 3.833")])
s += text(xs[3] + 14, 196, [("v", "X"), ("vsub", "IM"), ("sub", "2"), ("n", "″ = 16.67")])
for x, nm in zip(xs, ["電力公司＋T1", "S/M", "I/M1", "T2＋I/M2"]):
    s += text(x, 312, [("t", nm)], anchor="middle")
    s += text(x + 18, sy + 24, [("v", "E"), ("n", "″ = 1∠0°")])
s += text(400, 344, [("v", "I"), ("vsub", "F"), ("sub", "1"), ("n", " = Σ 1/"), ("v", "X"), ("n", " = 0.6818 + 0.1333 + 0.05 + 0.04878 = 0.9139 pu")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-110-06-5-parallel-sources.svg'), 'w').write(s)
print(len(s))
