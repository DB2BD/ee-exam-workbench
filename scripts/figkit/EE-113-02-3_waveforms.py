"""EE-113-02-3: Buck BCM waveforms v_L, i_L, i_C over one period; shaded charge area gives Delta V_o."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X0, X2, XE = 110, 590, 640
DUTY = 0.4
X1 = X0 + DUTY * (X2 - X0)               # t = DTs
XA = X0 + DUTY / 2 * (X2 - X0)           # i_L = I_o on the rise
XB = X1 + (1 - DUTY) / 2 * (X2 - X0)     # i_L = I_o on the fall


def axes(y0, ytop, ybot):
    return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)


W, H = 680, 480
s = header(W, H)
# shaded positive i_C area (charge Delta Q): triangle XA..XB, apex at X1
yc0, ycp = 400, 360
s += f'<path d="M{XA:.1f} {yc0} L{X1:.1f} {ycp} L{XB:.1f} {yc0} Z" fill="{FILL_RED}" stroke="none"/>\n'
s += dashed(X1, 36, X1, 448) + dashed(X2, 36, X2, 448)
# v_L panel: zero at 95
s += axes(95, 28, 150) + poly([(X0, 62), (X1, 62), (X1, 132), (X2, 132)])
# i_L panel: zero at 290, peak at 190, I_o at 240
s += axes(290, 168, 300) + poly([(X0, 290), (X1, 190), (X2, 290)])
s += dashed(X0, 240, X2 + 20, 240, 1.2) + dashed(X0, 190, X1, 190, 1)
# i_C panel: zero at 400, 40 px per I_o
s += axes(yc0, 318, 450) + poly([(X0, 440), (X1, ycp), (X2, 440)])
s += dashed(XA, 240, XA, yc0, 1) + dashed(XB, 240, XB, yc0, 1)
s += end_group()
s += text(X0 + 8, 36, [("v", "v"), ("vsub", "L")])
s += text(X0 + 8, 176, [("v", "i"), ("vsub", "L")])
s += text(X0 + 8, 326, [("v", "i"), ("vsub", "C"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("n", " − "), ("v", "I"), ("vsub", "o")])
for y in (114, 308, 418):
    s += text(XE + 6, y, [("v", "t")])
s += text(104, 67, [("v", "V"), ("vsub", "s"), ("n", " − "), ("v", "V"), ("vsub", "o")], anchor="end")
s += text(104, 100, [("n", "0")], anchor="end")
s += text(104, 137, [("n", "−"), ("v", "V"), ("vsub", "o")], anchor="end")
s += text(104, 195, [("v", "I"), ("vsub", "L"), ("sub", "max")], anchor="end")
s += text(104, 245, [("v", "I"), ("vsub", "o")], anchor="end")
s += text(104, 295, [("n", "0")], anchor="end")
s += text(X2 + 24, 245, [("t", "平均 = "), ("v", "I"), ("vsub", "o")])
s += text(104, 365, [("v", "I"), ("vsub", "o")], anchor="end")
s += text(104, 405, [("n", "0")], anchor="end")
s += text(104, 445, [("n", "−"), ("v", "I"), ("vsub", "o")], anchor="end")
s += ctext(X1 + 22, 352, [("n", "Δ"), ("v", "Q"), ("n", " = ½·"), ("v", "T"), ("vsub", "s"), ("n", "/2·"), ("v", "I"), ("vsub", "o")])
s += text(X0, 470, [("n", "0")], anchor="middle")
s += text(XA, 470, [("v", "DT"), ("vsub", "s"), ("n", "/2")], anchor="middle")
s += text(X1 + 6, 470, [("v", "DT"), ("vsub", "s")], anchor="middle")
s += text(XB, 470, [("n", "(1 + "), ("v", "D"), ("n", ")"), ("v", "T"), ("vsub", "s"), ("n", "/2")], anchor="middle")
s += text(X2, 470, [("v", "T"), ("vsub", "s")], anchor="middle")
s += footer()
write('EE-113-02-3-waveforms.svg', s)
