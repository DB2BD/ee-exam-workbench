"""EE-107-02-4: one period of i_L2, i_C2 (= i_L2 - I_o, shaded charge for the C2 ripple) and the transistor current i_Q."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X0, XE = 110, 690
K = 10.8                      # px per microsecond (T = 50 us -> 540 px)
def X(us): return X0 + K * us
XD, XT = X(10), X(50)


def axes(y0, ytop, ybot):
    return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)


def tick_y(y): return line(X0 - 4, y, X0, y)


W, H = 720, 480
s = header(W, H)
# shaded positive i_C2 area (t = 5 .. 30 us, peak +0.5 A at t = 10 us); panel 2 zero at y = 236, 80 px/A
s += f'<path d="M{X(5):.1f} 236 L{XD:.1f} 196 L{X(30):.1f} 236 Z" fill="{FILL_RED}" stroke="none"/>\n'
s += dashed(XD, 30, XD, 446) + dashed(XT, 30, XT, 446)
# panel 1: i_L2, zero at y = 140, 40 px/A
s += axes(140, 22, 150) + tick_y(40) + tick_y(60) + tick_y(80)
s += dashed(X0, 60, XT, 60, 1.2)
s += poly([(X0, 80), (XD, 40), (XT, 80)])
# panel 2: i_C2
s += axes(236, 172, 286) + tick_y(196) + tick_y(276)
s += poly([(X0, 276), (XD, 196), (XT, 276)])
# panel 3: i_Q, zero at y = 420, 30 px/A
s += axes(420, 300, 430) + tick_y(322.5) + tick_y(367.5)
s += poly([(X0, 420), (X0, 367.5), (XD, 322.5), (XD, 420), (XT, 420)])
s += dashed(XD, 322.5, 300, 322.5)
s += end_group()
# labels
s += text(X0 + 8, 30, [("v", "i"), ("vsub", "L"), ("sub", "2")])
s += text(104, 45, [("n", "2.50 A")], anchor="end")
s += text(104, 65, [("n", "2 A")], anchor="end")
s += text(104, 85, [("n", "1.50 A")], anchor="end")
s += text(104, 145, [("n", "0")], anchor="end")
s += text(150, 122, [("t", "平均 "), ("v", "I"), ("vsub", "L"), ("sub", "2"), ("n", " = "), ("v", "I"), ("vsub", "o"), ("n", " = 2 A")])
s += text(470, 108, [("t", "峰對峰 "), ("n", "Δ"), ("v", "i"), ("vsub", "L"), ("sub", "2"), ("n", " = 1 A")])
s += text(X0 + 8, 182, [("v", "i"), ("vsub", "C"), ("sub", "2"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("sub", "2"), ("n", " − "), ("v", "I"), ("vsub", "o")])
s += text(104, 201, [("n", "0.50 A")], anchor="end")
s += text(104, 241, [("n", "0")], anchor="end")
s += text(104, 281, [("n", "−0.50 A")], anchor="end")
s += text(330, 198, [("t", "充電 "), ("n", "Δ"), ("v", "Q"), ("sub", "2"), ("n", " = 6.25 μC")])
s += text(X(17.5), 258, [("t", "底 "), ("v", "T"), ("n", "/2 = 25 μs")], anchor="middle")
s += text(X0 + 8, 310, [("v", "i"), ("vsub", "Q"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("sub", "1"), ("n", " + "), ("v", "i"), ("vsub", "L"), ("sub", "2")])
s += text(104, 327, [("n", "3.25 A")], anchor="end")
s += text(104, 372, [("n", "1.75 A")], anchor="end")
s += text(104, 425, [("n", "0")], anchor="end")
s += ctext(306, 327, [("t", "峰值 "), ("v", "I"), ("vsub", "p"), ("n", " = 3.25 A")])
s += text(360, 400, [("v", "Q"), ("t", " 截止，"), ("v", "i"), ("vsub", "Q"), ("n", " = 0")])
for y in (145, 241, 425):
    s += text(XE + 4, y - 8, [("v", "t")])
s += text(X0, 468, [("n", "0")], anchor="middle")
s += text(XD, 468, [("v", "DT"), ("n", " = 10 μs")], anchor="middle")
s += text(XT, 468, [("v", "T"), ("n", " = 50 μs")], anchor="middle")
s += footer()
write('EE-107-02-4-ripple.svg', s)
