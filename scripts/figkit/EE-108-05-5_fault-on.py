import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 360
YT, YM, YB = 80, 175, 290
XE, XA, XF, XB, XI = 60, 240, 350, 560, 650
s = header(W, H)
s += line(XE, YT, XE, 168) + ac_source(XE, 182) + line(XE, 196, XE, YB)          # E'
s += coil(XE, YT, XA, YT, turns=5)                                              # j0.30
s += coil(XA, YT, XB, YT, turns=6)                                              # healthy line j0.5
s += line(XA, YT, XA, YM) + coil(XA, YM, XF, YM, turns=3)                       # j0.15
s += coil(XF, YM, XB, YM, turns=5) + line(XB, YM, XB, YT)                       # j0.35
s += line(XB, YT, XI, YT) + line(XI, YT, XI, 168) + ac_source(XI, 182) + line(XI, 196, XI, YB)   # infinite bus
s += f'<path d="M{XF} {YM} L{XF} {YB}" stroke="{RED}"/>\n'                       # bolted fault
s += line(XE, YB, XI, YB)
s += line(450, YB, 450, YB + 8) + ground(450, YB + 8)
for x, y in ((XA, YT), (XB, YT), (XF, YM), (XF, YB)): s += dot(x, y)
s += end_group()
s += text((XE + XA) / 2, YT - 16, [("v", "j"), ("n", "0.30")], anchor="middle")
s += text((XE + XA) / 2, YT + 34, [("t", "（"), ("v", "X"), ("vsub", "d"), ("n", "′ + "), ("v", "X"), ("vsub", "T"), ("t", "）")], anchor="middle")
s += text((XA + XB) / 2, YT - 16, [("v", "j"), ("n", "0.5"), ("t", "（健全線）")], anchor="middle")
s += text((XA + XF) / 2, YM - 16, [("v", "j"), ("n", "0.15")], anchor="middle")
s += text((XF + XB) / 2, YM - 16, [("v", "j"), ("n", "0.35")], anchor="middle")
s += text(XA - 8, YT - 10, [("n", "A")], anchor="end")
s += text(XB + 4, YT - 10, [("n", "B")])
s += text(XF - 8, YM + 22, [("n", "F")], anchor="end")
s += ctext(RED, XF + 8, 240, [("t", "三相故障")])
s += ctext(BLUE, XE + 20, 187, [("v", "E"), ("n", "′∠"), ("v", "δ")])
s += ctext(BLUE, XI - 20, 187, [("n", "1∠0°")], anchor="end")
s += text(350, 336, [("t", "故障中：A 對地分路 "), ("v", "j"), ("n", "0.15"), ("t", "；"), ("v", "j"), ("n", "0.35"), ("t", " 跨接於無限匯流排與地，不影響轉移電抗")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-5-fault-on.svg'), 'w').write(s)
print(len(s))
