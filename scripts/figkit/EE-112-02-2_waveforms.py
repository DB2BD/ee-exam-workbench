"""EE-112-02-2: Schmitt relaxation oscillator, v_o (square wave) and v_X (RC exponential) over two periods.

v_o = +5 V for 0 < t < t_H (v_X charges from V_TL = -5/3 V toward +5 V until it reaches V_TH = +5/3 V),
then -5 V for t_H < t < T (v_X discharges from V_TH toward -5 V until V_TL).  Only values derived
before the figure (thresholds, asymptotes) carry numbers; t_H and T are symbols."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 640, 470
X0, XE = 140, 600                      # time axis start / end
TH = math.log(2)                       # t_H in units of tau
XS = 400 / (4 * TH)                    # px per tau: two periods = 400 px
YO, SO = 95, 9.0                       # v_o axis and px per volt
YX, SX = 300, 16.0                     # v_X axis and px per volt


def xt(t):
    return X0 + XS * t


s = header(W, H)
# axes
s += arrow(X0, YO, XE, YO) + arrow(X0, YO + 58, X0, 28)
s += arrow(X0, YX, XE, YX) + arrow(X0, YX + 95, X0, 195)
# v_o square wave
pts = []
for k in range(4):
    v = 5 if k % 2 == 0 else -5
    pts += [(xt(k * TH), YO - SO * v), (xt((k + 1) * TH), YO - SO * v)]
s += poly(pts, w=2.2, color=BLUE)
# v_X exponential segments
vx = []
for k in range(4):
    vinf = 5 if k % 2 == 0 else -5
    v0 = -5 / 3 if k % 2 == 0 else 5 / 3
    for j in range(41):
        t = TH * j / 40
        vx.append((xt(k * TH + t), YX - SX * (vinf + (v0 - vinf) * math.exp(-t))))
s += poly(vx, w=2.2, color=BLUE)
# thresholds and asymptotes
for v in (5 / 3, -5 / 3):
    s += dashed(X0, YX - SX * v, xt(4 * TH), YX - SX * v)
for v in (5, -5):
    s += dashed(X0, YX - SX * v, xt(4 * TH), YX - SX * v, w=0.8)
# switching instants (both panels)
for k in (1, 2, 3, 4):
    s += dashed(xt(k * TH), YO - SO * 5 - 6, xt(k * TH), YX + SX * 5 + 4, w=0.8)
s += end_group()

t = []
t.append(btext(X0 + 10, 36, [("v", "v"), ("vsub", "o")]))
t.append(text(X0 - 8, YO - SO * 5 + 5, [("n", "+5 V")], anchor="end"))
t.append(text(X0 - 8, YO + SO * 5 + 5, [("n", "−5 V")], anchor="end"))
t.append(text(XE + 4, YO + 5, [("v", "t")]))
t.append(btext(X0 + 10, 204, [("v", "v"), ("vsub", "X")]))
t.append(text(X0 - 8, YX - SX * 5 + 5, [("n", "+5 V")], anchor="end"))
t.append(text(X0 - 8, YX + SX * 5 + 5, [("n", "−5 V")], anchor="end"))
t.append(text(X0 - 8, YX - SX * 5 / 3 + 1, [("v", "V"), ("vsub", "TH"), ("n", " = 5/3 V")], anchor="end"))
t.append(text(X0 - 8, YX + SX * 5 / 3 + 11, [("v", "V"), ("vsub", "TL"), ("n", " = −5/3 V")], anchor="end"))
t.append(text(XE + 4, YX + 5, [("v", "t")]))
t.append(text(X0 - 2, YX + SX * 5 + 30, [("n", "0")], anchor="middle"))
t.append(text(xt(TH), YX + SX * 5 + 30, [("v", "t"), ("vsub", "H")], anchor="middle"))
t.append(text(xt(2 * TH), YX + SX * 5 + 30, [("v", "T")], anchor="middle"))
t.append(text(xt(4 * TH), YX + SX * 5 + 30, [("n", "2"), ("v", "T")], anchor="middle"))
t.append(text(xt(0.5 * TH), YO - SO * 5 + 22, [("t", "高電位")], anchor="middle"))
t.append(text(xt(1.5 * TH), YO + SO * 5 - 10, [("t", "低電位")], anchor="middle"))
t.append(text(20, 455, [("t", "虛線：臨界 "), ("v", "V"), ("vsub", "TH"), ("t", "／"), ("v", "V"), ("vsub", "TL"), ("t", "；細虛線：充放電漸近值 ±5 V（即 "),
                        ("v", "v"), ("vsub", "o"), ("t", "）")]))
s += ''.join(t) + footer()
write('EE-112-02-2-waveforms.svg', s)
