"""EE-106-02-5: inductor current i_L (triangle about I_L) and switch current i_Q1 (= i_L during DT_s), symbolic."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X0, XE = 150, 690
X1, XT = 150 + 0.4 * 500, 650     # D = 0.4 drawn


def axes(y0, ytop, ybot): return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)
def tick_y(y): return line(X0 - 4, y, X0, y)


W, H = 720, 380
s = header(W, H)
s += f'<path d="M{X0} 310 L{X0} 250 L{X1} 190 L{X1} 310 Z" fill="{FILL_RED}" stroke="none"/>\n'
s += dashed(X1, 40, X1, 324) + dashed(XT, 40, XT, 324)
# i_L panel: zero y = 150; valley 110, mean 90, peak 70
s += axes(160, 26, 170) + tick_y(60) + tick_y(90) + tick_y(120)
s += dashed(X0, 90, XT, 90, 1.2)
s += poly([(X0, 120), (X1, 60), (XT, 120)])
s += dashed(X1, 60, 700, 60) + dashed(XT, 120, 700, 120)
s += arrow(690, 90, 690, 62) + arrow(690, 90, 690, 118)
# i_Q1 panel: zero y = 290, same scale (valley 230, peak 190)
s += axes(310, 172, 320) + tick_y(190) + tick_y(250)
s += poly([(X0, 310), (X0, 250), (X1, 190), (X1, 310), (XT, 310)])
s += end_group()
s += text(X0 + 8, 34, [("v", "i"), ("vsub", "L")])
s += text(144, 65, [("v", "I"), ("vsub", "L"), ("n", " + Δ"), ("v", "I"), ("vsub", "L"), ("n", "/2")], anchor="end")
s += text(144, 95, [("v", "I"), ("vsub", "L")], anchor="end")
s += text(144, 125, [("v", "I"), ("vsub", "L"), ("n", " − Δ"), ("v", "I"), ("vsub", "L"), ("n", "/2")], anchor="end")
s += text(144, 165, [("n", "0")], anchor="end")
s += text(682, 50, [("n", "Δ"), ("v", "I"), ("vsub", "L")], anchor="end")
s += text(250, 50, [("t", "斜率 "), ("v", "V"), ("vsub", "in"), ("n", "/"), ("v", "L")], anchor="middle")
s += text(520, 142, [("t", "斜率 −"), ("v", "V"), ("vsub", "o"), ("n", "/"), ("v", "L")], anchor="middle")
s += text(X0 + 8, 180, [("v", "i"), ("vsub", "Q"), ("sub", "1")])
s += text(144, 195, [("v", "I"), ("vsub", "L"), ("n", " + Δ"), ("v", "I"), ("vsub", "L"), ("n", "/2")], anchor="end")
s += text(144, 255, [("v", "I"), ("vsub", "L"), ("n", " − Δ"), ("v", "I"), ("vsub", "L"), ("n", "/2")], anchor="end")
s += text(144, 315, [("n", "0")], anchor="end")
s += ctext(X0 + 12, 292, [("t", "導通段 "), ("v", "i"), ("vsub", "Q"), ("sub", "1"), ("n", " = "), ("v", "i"), ("vsub", "L")])
s += text(480, 292, [("v", "Q"), ("sub", "1"), ("t", " 截止，"), ("v", "i"), ("vsub", "Q"), ("sub", "1"), ("n", " = 0")], anchor="middle")
for y in (165, 315):
    s += text(XE + 4, y - 8, [("v", "t")])
s += text(X0, 346, [("n", "0")], anchor="middle")
s += text(X1, 346, [("v", "DT"), ("vsub", "s")], anchor="middle")
s += text(XT, 346, [("v", "T"), ("vsub", "s")], anchor="middle")
s += footer()
write('EE-106-02-5-currents.svg', s)
