import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 380
Y12, Y3 = 120, 290
s = header(W, H)
s += f'<path d="M150 80 L150 160" stroke-width="5"/>\n'          # Bus 1 (vertical busbar)
s += f'<path d="M490 80 L490 160" stroke-width="5"/>\n'          # Bus 2
s += busbar(280, 360, Y3)                                       # Bus 3
s += line(150, Y12, 260, Y12) + coil(260, Y12, 380, Y12, turns=5) + line(380, Y12, 490, Y12)    # 1-2 j0.8
s += line(150, 150, 200, 150) + line(200, 150, 200, Y3 - 40) + coil(200, Y3 - 40, 280, Y3 - 40, turns=3)
s += line(280, Y3 - 40, 300, Y3 - 40) + line(300, Y3 - 40, 300, Y3)                             # 1-3 j0.4
s += line(490, 150, 440, 150) + line(440, 150, 440, Y3 - 40) + coil(440, Y3 - 40, 360, Y3 - 40, turns=3)
s += line(360, Y3 - 40, 340, Y3 - 40) + line(340, Y3 - 40, 340, Y3)                             # 2-3 j0.4
s += line(150, Y12, 100, Y12) + line(100, Y12, 86, Y12) + ac_source(72, Y12)                     # gen at bus 1
s += line(490, Y12, 554, Y12) + ac_source(568, Y12)                                              # gen at bus 2
s += arrow(320, Y3, 320, Y3 + 44)                                                                # load
s += arrow(454, 176, 454, 216)                                                                   # S23 reference direction 2 -> 3
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s += lab(150, 66, [("n", "Bus 1")]) + lab(490, 66, [("n", "Bus 2")]) + lab(370, Y3 + 5, [("n", "Bus 3")], "start")
s += lab(320, Y12 - 14, [("v", "jx"), ("sub", "12"), ("n", " = "), ("v", "j"), ("n", "0.8")])
s += lab(240, Y3 - 58, [("v", "jx"), ("sub", "13"), ("n", " = "), ("v", "j"), ("n", "0.4")])
s += lab(400, Y3 - 58, [("v", "jx"), ("sub", "23"), ("n", " = "), ("v", "j"), ("n", "0.4")])
s += ctext(BLUE, 40, 186, [("t", "平衡（無限）匯流排")], anchor="start")
s += ctext(BLUE, 40, 208, [("v", "V"), ("sub", "1"), ("n", " = 1∠0°")], anchor="start")
s += ctext(BLUE, 600, 186, [("t", "PV 匯流排")], anchor="end")
s += ctext(BLUE, 600, 208, [("v", "P"), ("sub", "2"), ("n", " = 1, |"), ("v", "V"), ("sub", "2"), ("n", "| = 1")], anchor="end")
s += lab(330, Y3 + 62, [("t", "PQ 匯流排　"), ("v", "S"), ("vsub", "L"), ("n", " = 1 + "), ("v", "j"), ("n", "0.9")])
s += lab(464, 202, [("v", "S"), ("sub", "23")], "start")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-106-05-3-network.svg'), 'w').write(s)
print(len(s))
