import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# Support 0 < x < 1, 0 < y < 1 and the two integration directions for the marginals.
W, H = 600, 400
ox, oy, u = 110, 320, 250
X = lambda x: ox + u * x
Y = lambda y: oy - u * y
s = header(W, H)
s += f'<rect x="{X(0)}" y="{Y(1)}" width="{u}" height="{u}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += f'<rect x="{X(0)}" y="{Y(1)}" width="{u}" height="{u}"/>\n'
s += arrow(40, oy, 450, oy) + arrow(ox, oy + 30, ox, 34)
s += end_group()
# fixed x: integrate y from 0 to 1 (vertical); fixed y: integrate x from 0 to 1 (horizontal)
xs, ys = 0.7, 0.35
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">' + arrow(X(xs), Y(0) - 4, X(xs), Y(1) + 4, color=BLUE) + '</g>\n'
s += f'<g fill="none" stroke="#000" stroke-width="1.5">' + arrow(X(0) + 4, Y(ys), X(1) - 4, Y(ys)) + '</g>\n'
s += text(440, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 46, [("v", "y")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
s += text(X(1), oy + 24, [("n", "1")], anchor="middle")
s += text(X(xs), oy + 24, [("v", "x")], anchor="middle")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
s += text(ox - 10, Y(ys) + 5, [("v", "y")], anchor="end")
s += mtext(X(0.04), Y(0.86), [("v", "f"), ("vsub", "X"), ("sub", ","), ("vsub", "Y"), ("n", " = "), ("v", "x"), ("n", "("), ("v", "y"), ("n", " + 3/2)")])
s += ctext(X(1) + 14, Y(0.62), [("t", "固定 "), ("v", "x"), ("t", "，"), ("v", "y"), ("t", "："), ("n", "0 → 1")])
s += ctext(X(1) + 14, Y(0.62) + 22, [("t", "→ "), ("v", "f"), ("vsub", "X"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(X(1) + 14, Y(ys) + 5, [("t", "固定 "), ("v", "y"), ("t", "，"), ("v", "x"), ("t", "："), ("n", "0 → 1")])
s += text(X(1) + 14, Y(ys) + 27, [("t", "→ "), ("v", "f"), ("vsub", "Y"), ("n", "("), ("v", "y"), ("n", ")")])
s += text(W / 2, 384, [("t", "正方形外 "), ("v", "f"), ("vsub", "X"), ("sub", ","), ("vsub", "Y"), ("n", " = 0"), ("t", "；上下限皆為常數 "), ("n", "0 → 1")], anchor="middle")
s += footer()
write('EE-104-03-4-support.svg', s)
