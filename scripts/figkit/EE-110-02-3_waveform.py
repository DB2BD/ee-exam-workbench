"""EE-110-02-3: half-wave rectifier load current over one period, conduction interval shaded, average dashed."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 600, 380
X0, Y0, XS, YS = 150, 190, 380 / (2 * math.pi), 9.0   # 15.56 A -> 140 px
s = header(W, H)
pos = [(X0 + XS * t, Y0 - YS * 15.56 * math.sin(t)) for t in [k * math.pi / 100 for k in range(101)]]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pos) + f' Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(X0, Y0, X0 + 410, Y0) + arrow(X0, Y0 + 70, X0, 30)
s += poly(pos, w=2.2, color=BLUE)
s += poly([(X0 + XS * math.pi, Y0), (X0 + XS * 2 * math.pi, Y0)], w=2.2, color=BLUE)
neg = [(X0 + XS * t, Y0 - YS * 15.56 * math.sin(t)) for t in [math.pi + k * math.pi / 100 for k in range(101)]]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in neg) + '" stroke-width="1" stroke-dasharray="4 3"/>\n'
ya = Y0 - YS * 4.952
s += dashed(X0, ya, X0 + XS * 2 * math.pi, ya)
s += dashed(X0, Y0 - YS * 15.56, X0 + XS * math.pi / 2, Y0 - YS * 15.56)
for k in (1, 2):
    s += line(X0 + XS * math.pi * k, Y0, X0 + XS * math.pi * k, Y0 + 5)
s += end_group()
t = []
t.append(text(X0 + 12, 36, [("v", "i"), ("n", "("), ("v", "θ"), ("n", ") = "), ("v", "v"), ("vsub", "o"), ("n", "/"), ("v", "R")]))
t.append(text(X0 - 8, Y0 - YS * 15.56 + 5, [("v", "I"), ("vsub", "m"), ("n", " = 15.56 A")], anchor="end"))
t.append(text(X0 - 8, ya + 5, [("v", "I"), ("vsub", "avg"), ("n", " = 4.952 A")], anchor="end"))
t.append(text(X0 + XS * math.pi, Y0 + 22, [("v", "π")], anchor="middle"))
t.append(text(X0 + XS * 2 * math.pi + 14, Y0 + 22, [("n", "2"), ("v", "π")], anchor="middle"))
t.append(text(X0 + 414, Y0 + 5, [("v", "θ")]))
t.append(text(X0 + XS * math.pi / 2, Y0 - 16, [("t", "導通")], anchor="middle"))
t.append(text(X0 + XS * 1.5 * math.pi, Y0 - 16, [("t", "截止："), ("v", "i"), ("n", " = 0")], anchor="middle"))
t.append(text(X0 + XS * 1.5 * math.pi, Y0 + YS * 15.56 + 22, [("v", "v"), ("vsub", "s"), ("n", "/"), ("v", "R"), ("t", "（被擋）")], anchor="middle"))
s += ''.join(t) + footer()
write('EE-110-02-3-waveform.svg', s)
