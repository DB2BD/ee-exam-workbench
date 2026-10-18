"""EE-110-02-4: one period of the square-wave inverter output v_o = +/-V_dc (S1S2 on, then S3S4 on) with its
fundamental (dashed, peak 4V_dc/pi), and the steady-state RL load current i_o: exponential segments between
-I_max and +I_max, (T/2)/tau = 2.  Symbols only (values are derived in the text)."""
import math
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 680, 380
X0, XT = 90, 590                      # t = 0 ... T
XH = (X0 + XT) / 2
YV, KV = 100, 46                       # v panel zero, V_dc in px
YI, KI = 285, 4.6                      # i panel zero, px per ampere
A = 148.9153 / 12
K = math.tanh(1)
IM = A * K


def xi(u):                             # u = t / T
    return X0 + (XT - X0) * u


def i_of(u):                           # steady-state current, (T/2)/tau = 2  ->  t/tau = 4u
    if u <= 0.5:
        return A - (A + IM) * math.exp(-4 * u)
    return -(A - (A + IM) * math.exp(-4 * (u - 0.5)))


s = header(W, H)
s += arrow(X0, YV + 70, X0, YV - 75) + arrow(X0, YV, XT + 40, YV)
s += arrow(X0, YI + 75, X0, YI - 80) + arrow(X0, YI, XT + 40, YI)
s += dashed(XH, YV - 60, XH, YI + 70) + dashed(XT, YV - 60, XT, YI + 70)
s += poly([(X0, YV - KV), (XH, YV - KV), (XH, YV + KV), (XT, YV + KV)])
fund = [(xi(k / 200), YV - KV * 4 / math.pi * math.sin(2 * math.pi * k / 200)) for k in range(201)]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in fund) + '" stroke-width="1.2" stroke-dasharray="5 3"/>\n'
cur = [(xi(k / 200), YI - KI * i_of(k / 200)) for k in range(201)]
s += poly(cur, color=RED)
s += dashed(X0, YI - KI * IM, XH, YI - KI * IM) + dashed(X0, YI + KI * IM, XT, YI + KI * IM)
for y in (YV - KV, YV + KV, YV - KV * 4 / math.pi, YI - KI * IM, YI + KI * IM):
    s += line(X0 - 4, y, X0, y)
s += dot(XH, YI - KI * IM) + dot(XT, YI + KI * IM) + dot(X0, YI + KI * IM)
s += end_group()
t = []
t.append(text(X0 + 8, YV - 78, [("v", "v"), ("vsub", "o")]))
t.append(ctext(X0 + 8, YI - 82, [("v", "i"), ("vsub", "o")]))
t.append(text(X0 - 8, YV - KV * 4 / math.pi + 2, [("n", "4"), ("v", "V"), ("vsub", "dc"), ("n", "/π")], anchor="end"))
t.append(text(X0 - 8, YV - KV + 16, [("v", "V"), ("vsub", "dc")], anchor="end"))
t.append(text(X0 - 8, YV + KV + 5, [("n", "−"), ("v", "V"), ("vsub", "dc")], anchor="end"))
t.append(ctext(X0 - 8, YI - KI * IM + 5, [("v", "I"), ("sub", "max")], anchor="end"))
t.append(ctext(X0 - 8, YI + KI * IM + 5, [("n", "−"), ("v", "I"), ("sub", "max")], anchor="end"))
t.append(text(XT + 44, YV + 5, [("v", "t")]))
t.append(text(XT + 44, YI + 5, [("v", "t")]))
t.append(text(XH + 6, YV + 18, [("v", "T"), ("n", "/2")]))
t.append(text(XT + 6, YV + 18, [("v", "T")]))
t.append(text(XH + 6, YI + 18, [("v", "T"), ("n", "/2")]))
t.append(text(XT + 6, YI - 8, [("v", "T")]))
t.append(text((X0 + XH) / 2, YV - KV + 24, [("v", "S"), ("sub", "1"), ("v", "S"), ("sub", "2"), ("t", " 導通")], anchor="middle"))
t.append(text((XH + XT) / 2, YV + KV - 10, [("v", "S"), ("sub", "3"), ("v", "S"), ("sub", "4"), ("t", " 導通")], anchor="middle"))
t.append(text(XT - 4, YV - 30, [("t", "虛線：基本波 "), ("v", "v"), ("sub", "1")], anchor="end"))
t.append(text(X0 + 14, YI + 66, [("t", "前半週 "), ("v", "i"), ("vsub", "o"), ("n", " = "), ("v", "V"), ("vsub", "dc"), ("n", "/"), ("v", "R"),
                                  ("n", " + (−"), ("v", "I"), ("sub", "max"), ("n", " − "), ("v", "V"), ("vsub", "dc"), ("n", "/"), ("v", "R"),
                                  ("n", ") exp(−"), ("v", "t"), ("n", "/"), ("v", "τ"), ("n", ")")]))
s += ''.join(t) + footer()
write('EE-110-02-4-waveforms.svg', s)
