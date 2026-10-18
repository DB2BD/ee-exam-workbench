"""EE-104-02-4: (a) load equivalent: square-wave v_o = +/-V_dc across series R-L, reference i_o;
(b) periodic steady state: v_o square wave and i_o exponential segments between -I_max and +I_max,
asymptotes +/-V_dc/R (dashed).  Symbols only for I_max (its value is derived after the figure)."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 720, 480
s = header(W, H)
# ---- (a) equivalent circuit ----
XS, XL, YT, YB = 60, 200, 110, 250
s += vsrc(XS, YT, XS, YB) + line(XS, YT, 90, YT) + resistor(90, YT, 150, YT, zigs=6, lead=8) + line(150, YT, XL, YT)
s += coil(XL, YT, XL, YB, turns=4) + line(XS, YB, XL, YB)
s += red_arrow(158, YT - 14, 192, YT - 14)
# ---- (b) waveforms ----
X = lambda t: 330 + 34 * t          # t in ms, 0..10 (+ a little)
YV, AV = 100, 45                    # v_o baseline, px per V_dc
YI, AI = 320, 12                    # i_o baseline, px per A
s += arrow(X(0), YV, X(11.2), YV) + arrow(X(0), YV + AV + 10, X(0), YV - AV - 16)
s += arrow(X(0), YI, X(11.2), YI) + arrow(X(0), YI + 10 * AI + 12, X(0), YI - 10 * AI - 16)
s += poly([(X(0), YV - AV), (X(5), YV - AV), (X(5), YV + AV), (X(10), YV + AV), (X(10), YV - AV), (X(10.8), YV - AV)], w=2.2, color=BLUE)
for a in (10, -10):
    s += dashed(X(0), YI - a * AI, X(10.8), YI - a * AI)
A0 = 10 * (1 - math.exp(-2.5)) / (1 + math.exp(-2.5)) + 10


def io(t):
    t = t % 10
    return 10 - A0 * math.exp(-t / 2) if t < 5 else -10 + A0 * math.exp(-(t - 5) / 2)


s += poly([(X(k * 0.05), YI - AI * io(k * 0.05)) for k in range(217)], w=2.2, color=RED)
Im = A0 - 10
for t in (5, 10):
    s += dashed(X(t), YV - AV - 6, X(t), YI + 10 * AI + 6, w=0.8)
s += dashed(X(0), YI + Im * AI, X(10), YI + Im * AI, w=0.8) + dashed(X(0), YI - Im * AI, X(5), YI - Im * AI, w=0.8)
s += end_group()
s += dot(X(0), YI + Im * AI) + dot(X(5), YI - Im * AI) + dot(X(10), YI + Im * AI)
t = []
t.append(text(10, 26, [("t", "(a) 負載等效電路")]))
t.append(text(XS - 22, (YT + YB) / 2 + 5, [("v", "v"), ("vsub", "o")], anchor="end"))
t.append(text(120, YT - 16, [("v", "R"), ("n", " = 10 Ω")], anchor="middle"))
t.append(text(XL + 14, (YT + YB) / 2 + 5, [("v", "L")]))
t.append(text(XL + 14, (YT + YB) / 2 + 25, [("n", "20 mH")]))
t.append(ctext(176, YT - 22, [("v", "i"), ("vsub", "o")], anchor="middle"))
t.append(text(10, 320, [("v", "S"), ("sub", "1"), ("n", "、"), ("v", "S"), ("sub", "2"), ("t", " 導通："), ("v", "v"), ("vsub", "o"), ("n", " = +"), ("v", "V"), ("vsub", "dc")]))
t.append(text(10, 346, [("v", "S"), ("sub", "3"), ("n", "、"), ("v", "S"), ("sub", "4"), ("t", " 導通："), ("v", "v"), ("vsub", "o"), ("n", " = −"), ("v", "V"), ("vsub", "dc")]))
t.append(text(10, 372, [("v", "V"), ("vsub", "dc"), ("n", " = 100 V")]))
t.append(text(270, 26, [("t", "(b) 週期穩態波形")]))
t.append(ctext(X(0) - 8, YV - AV + 5, [("n", "+"), ("v", "V"), ("vsub", "dc")], anchor="end", color=BLUE))
t.append(ctext(X(0) - 8, YV + AV + 5, [("n", "−"), ("v", "V"), ("vsub", "dc")], anchor="end", color=BLUE))
t.append(ctext(X(2.5), YV - AV - 10, [("v", "v"), ("vsub", "o")], anchor="middle", color=BLUE))
t.append(text(X(11.2), YV + 20, [("v", "t")], anchor="end"))
t.append(text(X(11.2), YI + 20, [("v", "t")], anchor="end"))
t.append(text(X(0) - 8, YI - 10 * AI + 1, [("v", "V"), ("vsub", "dc"), ("n", "/"), ("v", "R")], anchor="end"))
t.append(text(X(0) - 8, YI + 10 * AI + 9, [("n", "−"), ("v", "V"), ("vsub", "dc"), ("n", "/"), ("v", "R")], anchor="end"))
t.append(ctext(X(0) - 8, YI + Im * AI + 5, [("n", "−"), ("v", "I"), ("vsub", "max")], anchor="end"))
t.append(ctext(X(0) - 8, YI - Im * AI + 5, [("n", "+"), ("v", "I"), ("vsub", "max")], anchor="end"))
t.append(ctext(X(3.2), YI - 22, [("v", "i"), ("vsub", "o")], anchor="middle"))
for tt, lab in ((0, "0"), (5, "5"), (10, "10 ms")):
    t.append(text(X(tt) + 4, YI + 10 * AI + 26, [("n", lab)], anchor="start" if tt == 10 else "middle"))
t.append(text(X(5) + 6, YV - AV + 18, [("v", "T"), ("n", "/2")]))
t.append(text(X(10) + 6, YV - AV + 18, [("v", "T")]))
s += ''.join(t) + footer()
write('EE-104-02-4-waveforms.svg', s)
