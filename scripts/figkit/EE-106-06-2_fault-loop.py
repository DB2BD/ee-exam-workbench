import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 380; s = header(W, H); lab = ''
yt, yb, xs, xf = 90, 250, 60, 620
def zbox(x, y, w=56, h=22): return f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}"/>\n'
names = [[("v", "Z"), ("vsub", "sys")], [("v", "Z"), ("vsub", "T"), ("sub", "1")], [("v", "Z"), ("vsub", "L")]]
xc = [150, 260, 370]
s += line(xs, yb, xs, 184) + ac_source(xs, 170) + line(xs, 156, xs, yt)
pts = [xs] + [v for x in xc for v in (x - 28, x + 28)] + [452, 508, xf]
for i in range(0, len(pts) - 1, 2): s += line(pts[i], yt, pts[i + 1], yt)
for x in xc: s += zbox(x, yt) + zbox(x, yb)
s += zbox(480, yt)
bpts = [xs] + [v for x in xc for v in (x - 28, x + 28)] + [xf]
for i in range(0, len(bpts) - 1, 2): s += line(bpts[i], yb, bpts[i + 1], yb)
s += dot(xf, yt) + dot(xf, yb) + f'<path d="M{xf} {yt} L{xf} {yb}" stroke="{RED}" stroke-dasharray="6 4"/>\n'
s += arrow(530, yt - 14, 600, yt - 14, RED)
s += end_group()
for x, nm in zip(xc, names):
    lab += text(x, yt - 20, nm, anchor="middle") + text(x, yb + 32, nm, anchor="middle")
lab += text(480, yt - 20, [("v", "Z"), ("vsub", "T"), ("sub", "2")], anchor="middle")
lab += text(260, 50, [("t", "去程導體（上游一次）")], anchor="middle") + text(260, 306, [("t", "回程導體（上游再一次）")], anchor="middle")
lab += text(480, yt + 32, [("t", "T2 全繞組")], anchor="middle")
lab += text(xs + 22, 175, [("n", "1∠0° pu")])
lab += text(xf + 10, 175, [("n", "F")])
lab += ctext(RED, 565, yt - 30, [("v", "I"), ("vsub", "sym"), ("n", " = 7.96 kA")], anchor="middle")
lab += text(360, 342, [("v", "Z"), ("vsub", "sys"), ("n", " = "), ("v", "j"), ("n", "0.0003，"), ("v", "Z"), ("vsub", "T"), ("sub", "1"), ("n", " = 0.0009 + "), ("v", "j"), ("n", "0.003675，"),
                       ("v", "Z"), ("vsub", "L"), ("n", " = 0.005142 + "), ("v", "j"), ("n", "0.002244，"), ("v", "Z"), ("vsub", "T"), ("sub", "2"), ("n", " = 0.012 + "), ("v", "j"), ("n", "0.023")], anchor="middle")
lab += text(360, 368, [("v", "Z"), ("vsub", "f"), ("n", " = 0.024084 + "), ("v", "j"), ("n", "0.035438"), ("t", "，"), ("n", "|"), ("v", "Z"), ("vsub", "f"), ("n", "| = 0.042847"), ("t", "（pu，75 kVA／220 V 基準）")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-106-06-2-fault-loop.svg'), 'w').write(s)
print(len(s))
