import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-112-03-2: adopted reading f(x) = 2|x| on [-2, 2), period 4 (triangle wave).
# Basic interval in blue with light-blue area; periodic copies in black.
W, H = 680, 300
ox, oy, ux, uy = 340, 220, 48, 36     # ux px per unit x, uy px per unit f
X = lambda x: ox + ux * x
Y = lambda v: oy - uy * v
s = header(W, H)
# light-blue area under the basic interval
s += f'<path d="M{X(-2):.1f} {oy} L{X(-2):.1f} {Y(4):.1f} L{X(0):.1f} {oy} L{X(2):.1f} {Y(4):.1f} L{X(2):.1f} {oy} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, oy, 660, oy) + arrow(ox, oy + 30, ox, 40)
s += dashed(X(-6.4), Y(4), X(6.4), Y(4))
# periodic copies (black): f(x) = 2|x - 4k|
s += f'<path d="M{X(-6.4):.1f} {Y(3.2):.1f} L{X(-6):.1f} {Y(4):.1f} L{X(-4):.1f} {Y(0):.1f} L{X(-2):.1f} {Y(4):.1f}" stroke-width="2"/>\n'
s += f'<path d="M{X(2):.1f} {Y(4):.1f} L{X(4):.1f} {Y(0):.1f} L{X(6):.1f} {Y(4):.1f} L{X(6.4):.1f} {Y(3.2):.1f}" stroke-width="2"/>\n'
for k in (-6, -4, -2, 2, 4, 6):
    s += line(X(k), oy - 4, X(k), oy + 4)
s += end_group()
# basic interval (blue)
s += f'<path d="M{X(-2):.1f} {Y(4):.1f} L{X(0):.1f} {oy} L{X(2):.1f} {Y(4):.1f}" stroke="{BLUE}" stroke-width="2.5" fill="none"/>\n'
# labels
s += text(656, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 50, [("v", "f"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 8, Y(4) - 6, [("n", "4")], anchor="end")
s += text(ox - 8, oy + 20, [("n", "0")], anchor="end")
for k in (-6, -4, -2, 2, 4, 6):
    s += text(X(k), oy + 22, [("n", str(k).replace("-", "−"))], anchor="middle")
s += ctext(X(1.55), Y(3.3), [("v", "f"), ("n", " = 2"), ("v", "x")], anchor="end")
s += ctext(X(-1.55), Y(3.3), [("v", "f"), ("n", " = −2"), ("v", "x")])
s += text(ox, 284, [("t", "基本區間 "), ("n", "[−2, 2)"), ("t", "：偶函數 "), ("v", "f"), ("n", " = 2|"), ("v", "x"), ("n", "|"),
                    ("t", "，週期 "), ("n", "4"), ("t", "（"), ("v", "L"), ("n", " = 2"), ("t", "）")], anchor="middle")
s += footer()
write('EE-112-03-2-triangle.svg', s)
