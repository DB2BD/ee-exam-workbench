import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 400
YT, YR = 150, 360                      # top wire, reference line
XG, XT, XB, XS = 40, 236, 450, 690     # gen source, V_t node, bus, system source
s = header(W, H)
for X in (XG, XS):
    s += line(X, YT, X, 241) + ac_source(X, 255) + line(X, 269, X, YR)
s += line(XG, YT, 80, YT) + coil(80, YT, 190, YT, turns=4) + line(190, YT, XT, YT)          # G j0.25
s += line(XT, YT, 266, YT) + coil(266, YT, 376, YT, turns=4) + line(376, YT, XB, YT)        # MT_R j0.15
s += line(XB, YT, 545, YT) + coil(545, YT, 645, YT, turns=4) + line(645, YT, XS, YT)        # system j0.025
for X in (XT, XB):                                                                         # shunt branches
    s += line(X, YT, X, 170) + coil(X, 170, X, 220, turns=3) + line(X, 220, X, 232)
    s += resistor(X, 232, X, 292) + line(X, 292, X, 302) + coil(X, 302, X, 348, turns=3) + line(X, 348, X, YR)
s += line(XG, YR, XS, YR) + line(345, YR, 345, YR + 6) + ground(345, YR + 6)
s += dot(XT, YT) + dot(XB, YT) + dot(XT, YR) + dot(XB, YR)
s += arrow(282, 100, 362, 100, color=RED)                                                   # I_MT
s += arrow(556, 100, 636, 100, color=RED)                                                   # I_sys
s += arrow(XB - 12, 180, XB - 12, 230, color=RED)                                                   # I_B (beside ST branch)
s += arrow(XT - 30, YR - 4, XT - 30, YT + 8, color=BLUE)                                   # V_t: reference -> node
s += arrow(XB + 72, YR - 4, XB + 72, YT + 8, color=BLUE)                                   # V: reference -> bus
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
# element names (above) and values (below)
s += lab(135, 128, [("v", "G")]) + lab(135, 180, [("v", "j"), ("n", "0.25")])
s += lab(321, 128, [("v", "MT"), ("vsub", "R")]) + lab(321, 180, [("v", "j"), ("n", "0.15")])
s += lab(595, 128, [("t", "系統")]) + lab(595, 180, [("v", "j"), ("n", "0.025")])
for X, nm, ld, x1, r, x2 in ((XT, "AT", "A", "1.6", "16", "12"), (XB, "ST", "B", "1.0", "8", "6")):
    s += lab(X + 14, 190, [("v", nm), ("vsub", "R")], "start")
    s += lab(X + 14, 212, [("v", "j"), ("n", x1)], "start")
    s += lab(X + 14, 258, [("t", "負載 "), ("n", ld)], "start")
    s += lab(X + 14, 280, [("n", r)], "start")
    s += lab(X + 14, 330, [("v", "j"), ("n", x2)], "start")
# voltages (blue)
s += ctext(BLUE, XT - 38, 238, [("v", "V"), ("vsub", "t")], anchor="end")
s += ctext(BLUE, XT - 38, 260, [("n", "= 1.09673∠6.21°")], anchor="end")
s += ctext(BLUE, XB + 80, 250, [("v", "V"), ("n", " = 1∠0°")])
s += ctext(BLUE, XG + 20, 300, [("v", "E"), ("vsub", "g")])
s += ctext(BLUE, XS - 20, 300, [("v", "E"), ("vsub", "sys")], anchor="end")
# currents (red)
s += ctext(RED, 322, 86, [("v", "I"), ("vsub", "MT"), ("n", " = 0.7908 − "), ("v", "j"), ("n", "0.6019")], anchor="middle")
s += ctext(RED, 596, 86, [("v", "I"), ("vsub", "sys"), ("n", " = 0.72 − "), ("v", "j"), ("n", "0.54")], anchor="middle")
s += ctext(RED, XB - 20, 200, [("v", "I"), ("vsub", "B"), ("n", " = 0.070796")], anchor="end")
s += ctext(RED, XB - 20, 222, [("n", "− "), ("v", "j"), ("n", "0.061947")], anchor="end")
s += text(700, 54, [("v", "S"), ("vsub", "sys"), ("n", " = 0.72 + "), ("v", "j"), ("n", "0.54")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-1-positive.svg'), 'w').write(s)
print(len(s))
