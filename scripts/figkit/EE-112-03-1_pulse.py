import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-112-03-1: g(t) = u(t-5) - u(t-20): unit pulse on 5 <= t < 20 as the difference of two delayed steps.
W, H = 640, 300
ox, oy, ux, uy = 60, 220, 20, 130
X = lambda t: ox + ux * t
Y = lambda v: oy - uy * v
s = header(W, H)
s += f'<rect x="{X(5)}" y="{Y(1)}" width="{X(20) - X(5)}" height="{uy}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, oy, 610, oy) + arrow(ox, oy + 30, ox, 30)
# g(t)
s += f'<path d="M{ox} {oy} L{X(5)} {oy} L{X(5)} {Y(1)} L{X(20)} {Y(1)} L{X(20)} {oy} L{X(27)} {oy}" stroke-width="2.5"/>\n'
s += dashed(ox, Y(1), X(5), Y(1))
s += end_group()
# step markers: +u(t-5) switches on (up), -u(t-20) switches off (down)
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">\n'
s += arrow(X(5) - 22, oy - 8, X(5) - 22, Y(1) + 8, BLUE)
s += arrow(X(20) + 22, Y(1) + 8, X(20) + 22, oy - 8, BLUE)
s += '</g>\n'
s += ctext(X(5) - 30, Y(0.5) + 5, [("n", "+"), ("v", "u"), ("n", "("), ("v", "t"), ("n", " − 5)")], anchor="end")
s += ctext(X(20) + 30, Y(0.5) + 5, [("n", "−"), ("v", "u"), ("n", "("), ("v", "t"), ("n", " − 20)")], anchor="start")
# labels
s += text(608, oy + 26, [("v", "t")], anchor="middle")
s += text(ox + 10, 40, [("v", "g"), ("n", "("), ("v", "t"), ("n", ") = "), ("v", "u"), ("n", "("), ("v", "t"),
                        ("n", " − 5) − "), ("v", "u"), ("n", "("), ("v", "t"), ("n", " − 20)")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
s += text(X(5), oy + 24, [("n", "5")], anchor="middle")
s += text(X(20), oy + 24, [("n", "20")], anchor="middle")
s += text(X(12.5), Y(1) - 10, [("v", "g"), ("n", " = 1"), ("t", "（"), ("n", "5 ≤ "), ("v", "t"), ("n", " &lt; 20"), ("t", "）")], anchor="middle")
s += mtext(X(12.5), oy + 56, [("t", "兩個延遲單位步階相減，轉換後各帶延遲因子 "), ("v", "e"), ("sup", "−5"), ("vsup", "s"),
                              ("t", "、"), ("v", "e"), ("sup", "−20"), ("vsup", "s")], anchor="middle")
s += footer()
write('EE-112-03-1-pulse.svg', s)
