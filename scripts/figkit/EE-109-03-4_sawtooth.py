import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-109-03-4: f(x) = x/pi on (-pi, pi), period 2pi (sawtooth). Basic period highlighted in blue;
# open circles = one-sided limits at the jumps x = (2m+1)pi; blue dots = Dirichlet average 0.
W, H = 680, 320
ox, oy, ux, uy = 340, 165, 95, 85     # ux pixels per pi, uy pixels per unit of f
X = lambda k: ox + ux * k             # k = x / pi
Y = lambda v: oy - uy * v
s = header(W, H)
s += arrow(30, oy, 660, oy) + arrow(ox, oy + 110, ox, 40)
# level lines f = +1 / -1
s += dashed(X(-3), Y(1), X(3), Y(1)) + dashed(X(-3), Y(-1), X(3), Y(-1))
# periodic copies (black) on (-3pi,-pi) and (pi,3pi)
for a in (-3, 1):
    s += f'<path d="M{X(a):.1f} {Y(-1):.1f} L{X(a + 2):.1f} {Y(1):.1f}" stroke-width="2"/>\n'
s += end_group()
# basic period (-pi, pi) in blue
s += f'<path d="M{X(-1):.1f} {Y(-1):.1f} L{X(1):.1f} {Y(1):.1f}" stroke="{BLUE}" stroke-width="2.5" fill="none"/>\n'
# one-sided limits (open circles) and averages (blue dots) at jumps
for k in (-3, -1, 1, 3):
    if k > -3:
        s += f'<circle cx="{X(k):.1f}" cy="{Y(1):.1f}" r="4" fill="#fff" stroke="#000" stroke-width="1.5"/>\n'
    if k < 3:
        s += f'<circle cx="{X(k):.1f}" cy="{Y(-1):.1f}" r="4" fill="#fff" stroke="#000" stroke-width="1.5"/>\n'
    if k in (-1, 1):
        s += f'<circle cx="{X(k):.1f}" cy="{oy}" r="4.5" fill="{BLUE}" stroke="none"/>\n'
# axis labels and ticks
s += text(656, oy + 26, [("v", "x")], anchor="middle")
s += text(ox + 10, 50, [("v", "f"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 10, Y(1) - 6, [("n", "1")], anchor="end")
s += text(ox - 10, Y(-1) + 18, [("n", "−1")], anchor="end")
for k, lab in ((-3, "−3"), (-2, "−2"), (2, "2"), (3, "3")):
    s += text(X(k), oy + 22, [("n", lab), ("v", "π")], anchor="middle")
s += text(X(-1), oy + 22, [("n", "−"), ("v", "π")], anchor="middle")
s += text(X(1) - 4, oy + 22, [("v", "π")], anchor="end")
s += ctext(405, Y(0.25), [("v", "f"), ("n", " = "), ("v", "x"), ("n", "/"), ("v", "π")])
s += ctext(X(-1) - 14, oy + 54, [("t", "跳躍點平均 "), ("n", "0")], anchor="end")
s += text(ox, 302, [("t", "基本週期 "), ("n", "(−"), ("v", "π"), ("n", ", "), ("v", "π"), ("n", ")"),
                    ("t", " 上為奇函數；空心圈為跳躍兩側極限 "), ("n", "±1")], anchor="middle")
s += footer()
write('EE-109-03-4-sawtooth.svg', s)
