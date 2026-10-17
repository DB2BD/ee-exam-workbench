import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 360; s = header(W, H); y, g, sy = 90, 290, 240
xs = [70, 220, 370, 520]
s += busbar(50, 660, y)
for x in xs:
    s += dot(x, y) + ac_source(x, sy) + line(x, sy + 14, x, g)
s += coil(70, y, 70, 226) + coil(220, y, 220, 226) + coil(370, y, 370, 226)
s += coil(520, y, 520, 158, turns=3) + coil(520, 158, 520, 226, turns=3)
s += f'<path d="M640 {y} L640 {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n'
s += line(50, g, 660, g)
for x in xs:
    s += arrow(x - 14, 200, x - 14, 120, RED)
s += arrow(652, 140, 652, 230, RED)
s += end_group()
s += text(70, 72, [("n", "3.45 kV "), ("t", "母線")], anchor="start")
s += text(640, 72, [("n", "F1")], anchor="middle")
lab = [(70, [("v", "X"), ("vsub", "src")], "j1.467", "0.6818"),
       (220, [("v", "X"), ("vsub", "SM")], "j7.50", "0.1333"),
       (370, [("v", "X"), ("vsub", "IM"), ("sub", "1")], "j20", "0.05")]
for x, nm, xv, iv in lab:
    s += text(x + 14, 150, nm) + text(x + 14, 170, [("v", "j"), ("n", xv[1:])])
    s += ctext(RED, x - 20, 120, [("n", iv)], anchor="end")
s += text(534, 128, [("v", "X"), ("vsub", "T"), ("sub", "2"), ("n", " = "), ("v", "j"), ("n", "3.833")])
s += text(534, 196, [("v", "X"), ("vsub", "IM"), ("sub", "2"), ("n", "″ = "), ("v", "j"), ("n", "16.67")])
s += ctext(RED, 500, 120, [("n", "0.04878")], anchor="end")
s += ctext(RED, 664, 200, [("n", "0.9139")], anchor="start")
for x, nm in zip(xs, ["電力公司＋T1", "S/M", "I/M1", "T2＋I/M2"]):
    s += text(x, 312, [("t", nm)], anchor="middle")
for x in xs:
    s += text(x + 18, sy + 24, [("n", "1∠0°")])
s += text(360, 342, [("t", "支路電流 1/"), ("v", "X"), ("t", "（pu）相加："), ("n", "0.6818 + 0.1333 + 0.05 + 0.04878 = 0.9139")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-110-06-5-parallel-sources.svg'), 'w').write(s)
print(len(s))
