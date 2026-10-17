import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 620, 360
ox, oy, u = 80, 300, 76          # origin and pixels per unit
X = lambda x: ox + u * x
Y = lambda y: oy - u * y
s = header(W, H)
# event region X > Y inside the 5 x 3 rectangle: (0,0)-(5,0)-(5,3)-(3,3)
s += f'<path d="M{X(0)} {Y(0)} L{X(5)} {Y(0)} L{X(5)} {Y(3)} L{X(3)} {Y(3)} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
# support rectangle
s += f'<path d="M{X(0)} {Y(0)} L{X(5)} {Y(0)} L{X(5)} {Y(3)} L{X(0)} {Y(3)} Z"/>\n'
# axes
s += arrow(40, oy, 560, oy) + arrow(ox, oy + 30, ox, 30)
# boundary y = x (dashed), extended a little beyond the rectangle
s += dashed(X(0), Y(0), X(3.45), Y(3.45))
# horizontal strip at fixed y = 1.3: x from y to 5
yy = 1.3
s += dashed(X(0), Y(yy), X(yy), Y(yy))
s += line(X(3), oy, X(3), oy - 6) + line(X(5), oy, X(5), oy - 6)
s += end_group()
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">' + arrow(X(yy) + 4, Y(yy), X(5) - 4, Y(yy), color=BLUE) + '</g>\n'
s += f'<circle cx="{X(yy)}" cy="{Y(yy)}" r="3" fill="{BLUE}" stroke="none"/>\n'
# labels
s += text(552, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 42, [("v", "y")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
for v in (3, 5):
    s += text(X(v), oy + 24, [("n", str(v))], anchor="middle")
s += text(ox - 10, Y(3) + 5, [("n", "3")], anchor="end")
s += text(ox - 10, Y(yy) + 5, [("v", "y")], anchor="end")
s += text(X(3.45) + 6, Y(3.45) + 4, [("v", "y"), ("n", " = "), ("v", "x")])
s += text(X(0.95), Y(2.25), [("v", "x"), ("n", " ≤ "), ("v", "y")], anchor="middle")
s += text(X(4.1), Y(2.35), [("v", "x"), ("n", " &gt; "), ("v", "y")], anchor="middle")
# density holds on the whole support rectangle -> label outside, to the right
s += text(X(5) + 12, Y(1.9), [("t", "整個矩形：")])
s += text(X(5) + 12, Y(1.9) + 24, [("v", "f"), ("vsub", "X"), ("sub", ","), ("vsub", "Y"), ("n", " = 1/15")])
# intersection of y = x with the top edge y = 3
s += f'<circle cx="{X(3)}" cy="{Y(3)}" r="3" fill="#000" stroke="none"/>\n'
s += text(X(3) - 8, Y(3) - 10, [("n", "(3, 3)")], anchor="end")
s += ctext(X(3.15), Y(yy) - 10, [("t", "固定 "), ("v", "y"), ("t", "："), ("v", "x"), ("t", " 由 "), ("v", "y"), ("t", " 積到 "), ("n", "5")], anchor="middle")
s += footer()
write('EE-109-03-3-region.svg', s)
