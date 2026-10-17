import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# Path C lies in the plane y = 1: draw its projection on the x-z plane, start -> end.
W, H = 720, 370
ox, oy, u = 420, 300, 66             # origin (x = 0, z = 0) and pixels per unit
X = lambda x: ox + u * x
Z = lambda z: oy - u * z
s = header(W, H)
s += arrow(180, oy, 600, oy) + arrow(ox, oy + 26, ox, 26)
for v in (-2, -1, 1):
    s += line(X(v), oy - 5, X(v), oy + 5)
for v in (1, 2, 3):
    s += line(ox - 5, Z(v), ox + 5, Z(v))
# component legs of P1 - P0: dx = -3 along x, then dz = +2 along z
s += dashed(X(1), Z(1), X(-2), Z(1)) + dashed(X(-2), Z(1), X(-2), Z(3))
s += end_group()
s += f'<g fill="none" stroke="{BLUE}" stroke-width="2">' + arrow(X(1), Z(1), X(-2) + 7, Z(3) + 4.7, color=BLUE) + '</g>\n'
s += dot(X(1), Z(1)) + dot(X(-2), Z(3))
s += text(608, oy + 6, [("v", "x")])
s += text(ox + 10, 34, [("v", "z")])
s += text(ox + 8, oy + 22, [("n", "0")])
for v in (-2, -1, 1):
    s += text(X(v), oy + 22, [("n", str(v).replace("-", "−"))], anchor="middle")
for v in (2, 3):
    s += text(ox - 10, Z(v) + 5, [("n", str(v))], anchor="end")
s += text(ox - 8, Z(1) - 6, [("n", "1")], anchor="end")
s += text(X(1) + 12, Z(1) + 22, [("t", "起點 "), ("n", "(1, 1, 1)"), ("t", "，"), ("v", "u"), ("n", " = 0")])
s += text(X(-2) - 10, Z(3) - 10, [("t", "終點 "), ("n", "(−2, 1, 3)"), ("t", "，"), ("v", "u"), ("n", " = 1")], anchor="middle")
s += text(X(-1), Z(1) + 22, [("n", "Δ"), ("v", "x"), ("n", " = −3")], anchor="middle")
s += text(X(-2) - 10, Z(2) + 5, [("n", "Δ"), ("v", "z"), ("n", " = 2")], anchor="end")
s += ctext(X(-0.9), Z(1.85), [("t", "路徑 "), ("v", "C")], anchor="middle")
s += text(W / 2, 356, [("t", "整段在平面 "), ("v", "y"), ("n", " = 1"), ("t", " 上（"), ("v", "dy"), ("n", " = 0"), ("t", "），畫在 "), ("v", "xz"), ("t", " 平面")], anchor="middle")
s += footer()
write('EE-104-03-5-segment.svg', s)
