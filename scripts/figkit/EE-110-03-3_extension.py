import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-110-03-3: f(x) = x - x^2 on (-pi, pi), 2pi-periodic extension (assumed interval).
# Basic period in blue; open circles = one-sided limits pi - pi^2 and -pi - pi^2 at x = (2m+1)pi;
# blue dots = Dirichlet average -pi^2.
W, H = 680, 340
ox, oy, ux, uy = 340, 70, 95, 15      # ux pixels per pi, uy pixels per unit of f
X = lambda k: ox + ux * k             # k = x / pi
Y = lambda v: oy - uy * v
PI = math.pi
f = lambda t: t - t * t               # t = x on the basic period
s = header(W, H)
s += arrow(30, oy, 660, oy) + arrow(ox, Y(-14.2), ox, 30)
for a in (-2, 2):                     # shifted copies (black)
    pts = ' L'.join(f'{X(a + (-1 + j / 60)):.1f} {Y(f(PI * (-1 + j / 60))):.1f}' for j in range(121))
    s += f'<path d="M{pts}" stroke-width="2"/>\n'
s += dashed(X(-1), oy, X(-1), Y(f(-PI)) + 4) + dashed(X(1), oy, X(1), Y(f(-PI)) + 4)
s += end_group()
pts = ' L'.join(f'{X(-1 + j / 60):.1f} {Y(f(PI * (-1 + j / 60))):.1f}' for j in range(121))
s += f'<path d="M{pts}" stroke="{BLUE}" stroke-width="2.5" fill="none"/>\n'
for k in (-1, 1):
    for v in (f(PI), f(-PI)):
        s += f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="4" fill="#fff" stroke="#000" stroke-width="1.5"/>\n'
    s += f'<circle cx="{X(k):.1f}" cy="{Y(-PI * PI):.1f}" r="4.5" fill="{BLUE}" stroke="none"/>\n'
# labels
s += text(656, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 40, [("v", "f"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 8, oy - 8, [("n", "0")], anchor="end")
for k, lab in ((-3, "−3"), (-2, "−2"), (2, "2"), (3, "3")):
    s += text(X(k), oy - 10, [("n", lab), ("v", "π")], anchor="middle")
s += text(X(-1) - 6, oy - 10, [("n", "−"), ("v", "π")], anchor="middle")
s += text(X(1) + 6, oy - 10, [("v", "π")], anchor="middle")
s += mtext(X(-1) - 14, Y(-12.0), [("v", "f"), ("n", " = "), ("v", "x"), ("n", " − "), ("v", "x"), ("sup", "2")], anchor="end", color=BLUE)
# f(pi^-) label left of the jump (the black copy rising from (pi, -pi - pi^2) would cross it on the right)
s += mtext(X(1) - 12, Y(f(PI)) + 5, [("v", "f"), ("n", "("), ("v", "π"), ("sup", "−"), ("n", "\u2009)")], anchor="end")
s += mtext(X(1) - 12, Y(f(PI)) + 23, [("n", "= "), ("v", "π"), ("n", " − "), ("v", "π"), ("sup", "2")], anchor="end")
s += mtext(X(1) - 12, Y(-PI * PI) + 5, [("t", "平均 "), ("n", "−"), ("v", "π"), ("sup", "2")], anchor="end", color=BLUE)
s += mtext(X(1) + 6, Y(f(-PI)) + 26, [("v", "f"), ("n", "("), ("v", "π"), ("sup", "+"), ("n", ") = "), ("v", "f"), ("n", "(−"), ("v", "π"), ("sup", "+"), ("n", ") = −"), ("v", "π"),
                                      ("n", " − "), ("v", "π"), ("sup", "2")])
s += text(ox, 322, [("t", "基本週期 "), ("n", "(−"), ("v", "π"), ("n", ", "), ("v", "π"), ("n", ")"),
                    ("t", "（藍）作 "), ("n", "2"), ("v", "π"), ("t", " 週期延拓；"), ("v", "x"), ("n", " = ±"), ("v", "π"),
                    ("t", " 為跳躍點")], anchor="middle")
s += footer()
write('EE-110-03-3-extension.svg', s)
