import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-108-03-5: C1 = |z - 1| = 1, C2 = |z + 1| = 1 (both counter-clockwise); poles of 1/(z^2 - 1) at z = 1, -1.
W, H = 620, 380
ox, oy, u = 310, 180, 110          # origin z = 0, pixels per unit
X = lambda x: ox + u * x
Y = lambda y: oy - u * y
s = header(W, H)
# interiors (light blue), then axes
for c in (1, -1):
    s += f'<circle cx="{X(c)}" cy="{oy}" r="{u}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(40, oy, 590, oy) + arrow(ox, 330, ox, 40)
# contours (blue) with counter-clockwise arrows at the top (moving left) and bottom (moving right)
for c in (1, -1):
    s += f'<circle cx="{X(c)}" cy="{oy}" r="{u}" stroke="{BLUE}" stroke-width="2"/>\n'
    s += arrow(X(c) + 8, Y(1), X(c) - 8, Y(1), color=BLUE)
    s += arrow(X(c) - 8, Y(-1), X(c) + 8, Y(-1), color=BLUE)
# poles (x marks)
def cross(x, y):
    return f'<path d="M{x - 7:.1f} {y - 7:.1f} L{x + 7:.1f} {y + 7:.1f} M{x - 7:.1f} {y + 7:.1f} L{x + 7:.1f} {y - 7:.1f}" stroke-width="2"/>\n'
s += cross(X(1), oy) + cross(X(-1), oy)
s += end_group()
# labels
s += text(588, oy + 24, [("n", "Re "), ("v", "z")], anchor="end")
s += text(ox + 10, 50, [("n", "Im "), ("v", "z")])
s += text(ox - 6, oy + 22, [("n", "0")], anchor="end")
s += text(X(2) + 6, oy + 22, [("n", "2")])
s += text(X(-2) - 6, oy + 22, [("n", "−2")], anchor="end")
s += text(X(1), oy + 28, [("v", "z"), ("n", " = 1")], anchor="middle")
s += text(X(-1), oy + 28, [("v", "z"), ("n", " = −1")], anchor="middle")
s += ctext(X(1) + u * 0.78, Y(0.78) - 6, [("v", "C"), ("sub", "1"), ("n", ": |"), ("v", "z"), ("n", " − 1| = 1")])
s += ctext(X(-1) - u * 0.78, Y(0.78) - 6, [("v", "C"), ("sub", "2"), ("n", ": |"), ("v", "z"), ("n", " + 1| = 1")], anchor="end")
s += text(ox, 362, [("t", "兩極點相距 2 ＞ 半徑 1：每個圓只圍住自己圓心的極點（皆取逆時針）")], anchor="middle")
s += footer()
write('EE-108-03-5-contours.svg', s)
