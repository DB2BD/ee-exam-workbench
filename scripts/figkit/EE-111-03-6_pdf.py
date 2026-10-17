import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 600, 330
ox, oy, ux, uy = 90, 270, 180, 180     # origin and pixels per unit
X = lambda x: ox + ux * x
Y = lambda y: oy - uy * y
s = header(W, H)
s += f'<path d="M{X(0)} {Y(0)} L{X(1)} {Y(1)} L{X(1)} {Y(0)} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += f'<path d="M{X(1)} {Y(0)} L{X(1)} {Y(1)} L{X(2)} {Y(0)} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(40, oy, 560, oy) + arrow(ox, oy + 30, ox, 34)
s += f'<path d="M{X(0)} {Y(0)} L{X(1)} {Y(1)} L{X(2)} {Y(0)}" stroke-width="2"/>\n'
s += dashed(X(1), Y(0), X(1), Y(1), color=BLUE) + dashed(X(0), Y(1), X(1), Y(1))
s += end_group()
s += text(552, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 46, [("v", "p"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(X(0) - 8, oy + 22, [("n", "0")], anchor="end")
for v in (1, 2):
    s += text(X(v), oy + 24, [("n", str(v))], anchor="middle")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
s += text(X(0.38), Y(0.62), [("v", "p"), ("n", "("), ("v", "x"), ("n", ") = "), ("v", "x")], anchor="end")
s += text(X(1.62), Y(0.62), [("v", "p"), ("n", "("), ("v", "x"), ("n", ") = 2 − "), ("v", "x")])
s += ctext(X(0.66), Y(0.18), [("t", "第 1 段")], anchor="middle")
s += ctext(X(0.66), Y(0.18) + 22, [("n", "0 ≤ "), ("v", "x"), ("n", " ≤ 1")], anchor="middle")
s += ctext(X(1.34), Y(0.18), [("t", "第 2 段")], anchor="middle")
s += ctext(X(1.34), Y(0.18) + 22, [("n", "1 &lt; "), ("v", "x"), ("n", " ≤ 2")], anchor="middle")
s += text(X(2) + 10, Y(0.25), [("t", "區域外 "), ("v", "p"), ("n", " = 0")])
s += footer()
write('EE-111-03-6-pdf.svg', s)
