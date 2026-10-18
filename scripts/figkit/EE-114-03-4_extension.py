import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-114-03-4: f(x) = 0 on (-pi, 0], x on (0, pi], period 2pi.
# Basic period (-pi, pi] in blue (stated in the Markdown caption); filled dots = f((2m+1)pi) = pi at -3pi, -pi, pi, 3pi (defined values), open circles = right limits 0,
# blue dots = Dirichlet average pi/2 at the jumps x = (2m+1)pi.
W, H = 680, 265
ox, oy, ux, uy = 340, 200, 95, 45     # ux pixels per pi, uy pixels per unit of f
X = lambda k: ox + ux * k             # k = x / pi
Y = lambda v: oy - uy * v
PI = math.pi
s = header(W, H)
s += arrow(30, oy, 660, oy) + arrow(ox, oy + 20, ox, 30)
# periodic copies (black): ramps on (-2pi,-pi] and (2pi,3pi], zero pieces on (-3pi,-2pi] and (pi,2pi]
for a in (-2, 2):
    s += f'<path d="M{X(a):.1f} {Y(0):.1f} L{X(a + 1):.1f} {Y(PI):.1f}" stroke-width="2"/>\n'
for a in (-3, 1):
    s += f'<path d="M{X(a):.1f} {Y(0):.1f} L{X(a + 1):.1f} {Y(0):.1f}" stroke-width="2.5"/>\n'
# guide lines for the levels pi and pi/2
s += dashed(ox, Y(PI), X(1), Y(PI)) + dashed(ox, Y(PI / 2), X(1), Y(PI / 2))
s += dashed(X(1), oy, X(1), Y(PI)) + dashed(X(-1), oy, X(-1), Y(PI))
s += end_group()
# basic period (-pi, pi] in blue
s += f'<path d="M{X(-1):.1f} {Y(0):.1f} L{X(0):.1f} {Y(0):.1f} L{X(1):.1f} {Y(PI):.1f}" stroke="{BLUE}" stroke-width="2.5" fill="none"/>\n'
# jump markers
for k in (-3, -1, 1, 3):
    s += f'<circle cx="{X(k):.1f}" cy="{Y(PI):.1f}" r="4" fill="#000" stroke="none"/>\n'
for k in (-3, -1, 1):
    s += f'<circle cx="{X(k):.1f}" cy="{Y(0):.1f}" r="4" fill="#fff" stroke="#000" stroke-width="1.5"/>\n'
for k in (-1, 1):
    s += f'<circle cx="{X(k):.1f}" cy="{Y(PI / 2):.1f}" r="4.5" fill="{BLUE}" stroke="none"/>\n'
# axes, ticks
s += text(656, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 42, [("v", "f"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 8, oy + 20, [("n", "0")], anchor="end")
s += text(ox - 8, Y(PI) + 5, [("v", "π")], anchor="end")
s += text(ox - 8, Y(PI / 2) + 5, [("v", "π"), ("n", "/2")], anchor="end")
for k, lab in ((-3, "−3"), (-2, "−2"), (2, "2"), (3, "3")):
    s += text(X(k), oy + 22, [("n", lab), ("v", "π")], anchor="middle")
s += text(X(-1), oy + 22, [("n", "−"), ("v", "π")], anchor="middle")
s += text(X(1), oy + 22, [("v", "π")], anchor="middle")
# piece labels on the basic period
s += ctext(X(-0.5), oy - 10, [("v", "f"), ("n", " = 0")], anchor="middle")
s += ctext(X(0.62), oy - 36, [("v", "f"), ("n", " = "), ("v", "x")])
# jump labels at x = pi (right side is free: the copy there lies on the axis)
s += text(X(1) + 10, Y(PI) + 5, [("v", "f"), ("n", "("), ("v", "π"), ("n", ") = "), ("v", "π")])
s += ctext(X(1) + 10, Y(PI / 2) + 5, [("t", "平均 "), ("v", "π"), ("n", "/2")])
s += mtext(X(1) + 8, oy + 48, [("v", "f"), ("n", "("), ("v", "π"), ("sup", "+"), ("n", ") = "), ("v", "f"), ("n", "(−"), ("v", "π"),
                               ("sup", "+"), ("n", ") = 0")])
s += footer()
write('EE-114-03-4-extension.svg', s)
