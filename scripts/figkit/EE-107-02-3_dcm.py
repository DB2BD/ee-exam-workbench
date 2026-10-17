"""EE-107-02-3: buck-boost in DCM, one period of v_L and i_L (rise DT, fall D2 T, idle)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X0, XE = 110, 690
K = 13.5                       # px per microsecond (T = 40 us -> 540 px)
def X(us): return X0 + K * us
X1, X2, XT = X(13.06), X(32.66), X(40)


def axes(y0, ytop, ybot): return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)
def tick_y(y): return line(X0 - 4, y, X0, y)


W, H = 720, 380
s = header(W, H)
# shaded energy-release triangle (diode current to the output)
s += f'<path d="M{X1:.1f} 300 L{X1:.1f} 192.2 L{X2:.1f} 300 Z" fill="{FILL_RED}" stroke="none"/>\n'
for x in (X1, X2, XT):
    s += dashed(x, 34, x, 314)
# v_L panel: zero y = 95, 3 px/V
s += axes(95, 26, 150) + tick_y(50) + tick_y(125)
s += poly([(X0, 50), (X1, 50), (X1, 125), (X2, 125), (X2, 95), (XT, 95)])
# i_L panel: zero y = 300, 22 px/A
s += axes(300, 168, 310) + tick_y(192.2)
s += poly([(X0, 300), (X1, 192.2), (X2, 300), (XT, 300)])
s += dashed(X0, 192.2, X1, 192.2)
s += end_group()
s += text(X0 + 8, 34, [("v", "v"), ("vsub", "L")])
s += text(104, 55, [("n", "15 V")], anchor="end")
s += text(104, 100, [("n", "0")], anchor="end")
s += text(104, 130, [("n", "−10 V")], anchor="end")
s += text(170, 44, [("n", "+"), ("v", "V"), ("vsub", "d"), ("t", "（開關導通）")])
s += text(320, 146, [("n", "−"), ("v", "V"), ("vsub", "o"), ("t", "（二極體導通）")])
s += text(600, 86, [("t", "電流為零")], anchor="middle")
s += text(X0 + 8, 176, [("v", "i"), ("vsub", "L")])
s += text(104, 197, [("n", "4.899 A")], anchor="end")
s += text(104, 305, [("n", "0")], anchor="end")
s += text(X1 + 10, 190, [("v", "I"), ("sub", "pk"), ("n", " = "), ("v", "V"), ("vsub", "d"), ("v", "DT"), ("n", "/"), ("v", "L")])
s += ctext(X1 + 70, 252, [("t", "送往輸出的電荷")])
s += text(600, 290, [("v", "i"), ("vsub", "L"), ("n", " = 0")], anchor="middle")
for y in (100, 305):
    s += text(XE + 4, y - 8, [("v", "t")])
s += text(X0, 334, [("n", "0")], anchor="middle")
s += text(X1, 334, [("v", "DT"), ("n", " = 13.06 μs")], anchor="middle")
s += text(X2, 358, [("n", "("), ("v", "D"), ("n", " + "), ("v", "D"), ("sub", "2"), ("n", ")"), ("v", "T"), ("n", " = 32.66 μs")], anchor="middle")
s += text(XT, 334, [("v", "T"), ("n", " = 40 μs")], anchor="middle")
s += footer()
write('EE-107-02-3-dcm.svg', s)
