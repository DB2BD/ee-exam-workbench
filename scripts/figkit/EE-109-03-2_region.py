import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 600, 370
ox, oy, ux, uy = 100, 320, 120, 62      # origin and pixels per unit
X = lambda x: ox + ux * x
Y = lambda y: oy - uy * y
pts = [(X(k / 40), Y((k / 40) ** 2)) for k in range(0, 83)]   # x from 0 to 2.05
para = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts)
region = ('M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts[:81]) + f' L{X(0)} {Y(4)} Z')
s = header(W, H)
s += f'<path d="{region}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(50, oy, 470, oy) + arrow(ox, oy + 30, ox, 30)
s += f'<path d="{para}"/>\n'
s += line(X(0), Y(4), X(2.5), Y(4))
s += dot(X(2), Y(4))
s += dashed(X(2), Y(4), X(2), Y(0))
yy = 2.2
s += end_group()
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">' + arrow(X(0) + 2, Y(yy), X(math.sqrt(yy)) - 3, Y(yy), color=BLUE) + '</g>\n'
s += f'<circle cx="{X(math.sqrt(yy)):.1f}" cy="{Y(yy):.1f}" r="3" fill="{BLUE}" stroke="none"/>\n'
# labels
s += text(462, oy + 24, [("v", "x")], anchor="middle")
s += text(ox + 10, 42, [("v", "y")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
s += text(X(2), oy + 24, [("n", "2")], anchor="middle")
s += text(ox - 10, Y(4) + 5, [("n", "4")], anchor="end")
s += text(ox - 10, Y(yy) + 5, [("v", "y")], anchor="end")
s += mtext(X(1.42), Y(1.3), [("v", "y"), ("n", " = "), ("v", "x"), ("sup", "2")])
s += text(X(2.5) + 8, Y(4) + 5, [("v", "y"), ("n", " = 4")])
s += text(X(2) + 8, Y(4) + 22, [("n", "(2, 4)")])
s += text(X(0.42), Y(3.2), [("v", "R")], anchor="middle")
s += ctext(X(math.sqrt(yy)) + 10, Y(yy) + 5, [("v", "x"), ("n", " = √"), ("v", "y")])
s += ctext(X(0.75), Y(yy) + 26, [("t", "固定 "), ("v", "y"), ("t", "：先積 "), ("v", "x")], anchor="middle")
s += footer()
write('EE-109-03-2-region.svg', s)
