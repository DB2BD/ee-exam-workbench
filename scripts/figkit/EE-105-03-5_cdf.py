import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# CDF of EE-105-03-5: ramps x/3 on [0,1), x/2 on [1,2), jump of 1/6 at x = 1.
W, H = 680, 380
ox, oy, ux, uy = 90, 320, 220, 260
X = lambda x: ox + ux * x
Y = lambda y: oy - uy * y
s = header(W, H)
# event interval [1/2, 3/2] on the x-axis
s += f'<rect x="{X(0.5)}" y="{oy - 6}" width="{X(1.5) - X(0.5)}" height="12" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, oy, 650, oy) + arrow(ox, oy + 30, ox, 28)
# F(x)
s += f'<path d="M40 {oy} L{X(0)} {Y(0)} L{X(1)} {Y(1/3)}" stroke-width="2"/>\n'
s += f'<path d="M{X(1)} {Y(0.5)} L{X(2)} {Y(1)} L630 {Y(1)}" stroke-width="2"/>\n'
# guide lines for F(1/2), F(3/2), level 1
s += dashed(X(0.5), oy, X(0.5), Y(1/6)) + dashed(ox, Y(1/6), X(0.5), Y(1/6))
s += dashed(X(1.5), oy, X(1.5), Y(0.75)) + dashed(ox, Y(0.75), X(1.5), Y(0.75))
s += dashed(ox, Y(1), X(2), Y(1)) + dashed(X(2), oy, X(2), Y(1))
s += dashed(X(1), oy, X(1), Y(1/3))
s += end_group()
# jump at x = 1 (blue): open circle at left limit 1/3, solid circle at F(1) = 1/2
s += f'<path d="M{X(1)} {Y(1/3) - 4} L{X(1)} {Y(0.5) + 4}" stroke="{BLUE}" stroke-width="2.5"/>\n'
s += f'<circle cx="{X(1)}" cy="{Y(1/3)}" r="4" fill="#fff" stroke="#000" stroke-width="1.5"/>\n'
s += f'<circle cx="{X(1)}" cy="{Y(0.5)}" r="4" fill="#000" stroke="none"/>\n'
# axis labels
s += text(640, oy + 24, [("v", "x")], anchor="middle")
s += mtext(ox + 10, 40, [("v", "F"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
for v, lab in ((0.5, "1/2"), (1, "1"), (1.5, "3/2"), (2, "2")):
    s += text(X(v), oy + 24, [("n", lab)], anchor="middle")
s += text(ox - 10, Y(1/6) + 5, [("n", "1/6")], anchor="end")
s += text(ox - 10, Y(0.75) + 5, [("n", "3/4")], anchor="end")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
# piece labels
s += text(X(0.42), Y(0.27), [("v", "F"), ("n", " = "), ("v", "x"), ("n", "/3")], anchor="end")
s += text(X(1.66), Y(0.83) + 30, [("v", "F"), ("n", " = "), ("v", "x"), ("n", "/2")])
# left limit and value at x = 1
s += mtext(X(1) + 10, Y(1/3) + 18, [("v", "F"), ("n", "(1"), ("sup", "−"), ("n", ") = 1/3")])
s += text(X(1) - 10, Y(0.5) - 8, [("v", "F"), ("n", "(1) = 1/2")], anchor="end")
s += ctext(X(1) - 10, Y(0.42) + 4, [("t", "跳躍 "), ("v", "P"), ("n", "("), ("v", "X"), ("n", " = 1) = 1/6")], anchor="end")
s += text(X(0.5) + 8, Y(1/6) + 22, [("v", "F"), ("n", "(1/2) = 1/6")])
s += text(X(1.5) - 8, Y(0.75) - 10, [("v", "F"), ("n", "(3/2) = 3/4")], anchor="end")
s += ctext(X(1), oy + 50, [("t", "所求區間 "), ("n", "1/2 ≤ "), ("v", "x"), ("n", " ≤ 3/2"), ("t", "（含跳躍點 "), ("v", "x"), ("n", " = 1"), ("t", "）")], anchor="middle")
s += footer()
write('EE-105-03-5-cdf.svg', s)
