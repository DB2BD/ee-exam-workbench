"""EE-105-01-5: band-pass magnitude |V_R/V_S| of the designed series RLC (R = 100 ohm, L = 1 H, C = 1 uF)."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

R, L, C = 100.0, 1.0, 1e-6
W, H = 640, 360
X0, X1, Y0, Y1 = 80, 600, 280, 70          # axes box: w in [850, 1150], |H| in [0, 1]
wx = lambda w: X0 + (w - 850) / 300 * (X1 - X0)
hy = lambda h: Y0 - h * (Y0 - Y1)
Hm = lambda w: R / math.hypot(R, w * L - 1 / (w * C))
w1 = (-R / L + math.sqrt((R / L) ** 2 + 4 / (L * C))) / 2
w2 = w1 + R / L
s = header(W, H)
s += arrow(X0, Y0, X1 + 20, Y0) + arrow(X0, Y0, X0, Y1 - 20)
pts = [(wx(850 + k * 0.5), hy(Hm(850 + k * 0.5))) for k in range(601)]
s += f'<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" stroke="{BLUE}" stroke-width="2"/>\n'
s += dashed(X0, hy(1 / math.sqrt(2)), wx(w2), hy(1 / math.sqrt(2)))
for w in (w1, w2):
    s += dashed(wx(w), hy(1 / math.sqrt(2)), wx(w), Y0)
s += dashed(wx(1000), hy(1), wx(1000), Y0) + dashed(X0, hy(1), wx(1000), hy(1))
yb = Y0 + 34
s += arrow(wx(1000), yb, wx(w2), yb) + arrow(wx(1000), yb, wx(w1), yb)
s += end_group()
s += text(X0 + 8, Y1 - 18, [("n", "|"), ("v", "V"), ("vsub", "R"), ("n", "/"), ("v", "V"), ("vsub", "S"), ("n", "|")])
s += text(X1 + 20, Y0 + 22, [("v", "ω"), ("n", " (rad/s)")], anchor="end")
s += text(X0 - 8, hy(1) + 5, [("n", "1")], anchor="end")
s += text(X0 - 8, hy(1 / math.sqrt(2)) + 5, [("n", "1/√2")], anchor="end")
s += text(wx(w1) - 6, Y0 + 20, [("v", "ω"), ("sub", "1")], anchor="end")
s += text(wx(w2) + 6, Y0 + 20, [("v", "ω"), ("sub", "2")])
s += text(wx(1000), Y0 + 20, [("v", "ω"), ("sub", "0"), ("n", " = 1000")], anchor="middle")
s += text(wx(1000), yb + 26, [("v", "B"), ("n", " = "), ("v", "ω"), ("sub", "2"), ("n", " − "), ("v", "ω"), ("sub", "1"), ("n", " = 100 rad/s")], anchor="middle")
s += text(X1 - 10, Y1 + 10, [("v", "R"), ("n", " = 100 Ω, "), ("v", "L"), ("n", " = 1 H, "), ("v", "C"), ("n", " = 1 μF")], anchor="end")
s += footer()
write('EE-105-01-5-response.svg', s)
