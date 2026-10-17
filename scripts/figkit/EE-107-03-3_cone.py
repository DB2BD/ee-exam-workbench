import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 680, 380
ox, oy, u = 210, 320, 70          # apex (origin) and pixels per unit, xz-section
X = lambda x: ox + u * x
Y = lambda z: oy - u * z
ry = 28                            # half-height of the cap ellipse (perspective)
s = header(W, H)
# solid cone V: side triangle + front half of the cap ellipse, light-blue fill
s += (f'<path d="M{X(-2)} {Y(2)} L{X(0)} {Y(0)} L{X(2)} {Y(2)} '
      f'A{u * 2} {ry} 0 0 1 {X(-2)} {Y(2)} Z" fill="{FILL_BLUE}" stroke="none"/>\n')
# lateral surface S (silhouette lines) and cap D (full ellipse)
s += line(X(-2), Y(2), X(0), Y(0)) + line(X(0), Y(0), X(2), Y(2))
s += f'<ellipse cx="{X(0)}" cy="{Y(2)}" rx="{u * 2}" ry="{ry}"/>\n'
# axes
s += arrow(X(-2.6), oy, X(2.7), oy) + arrow(ox, oy + 18, ox, 58)
s += dot(ox, oy)
# radius 2 at the rim
s += dashed(X(2), Y(2), X(2), oy)
# outward normals: lateral (away from axis, downward) and cap (+k)
L = 30
for xs, sx in ((0.75, 1), (-0.75, -1)):
    x0, y0 = X(xs), Y(abs(xs))
    s += arrow(x0, y0, x0 + sx * L / math.sqrt(2), y0 + L / math.sqrt(2))
s += arrow(X(0.95), Y(2), X(0.95), Y(2) - 48)
# integration strip at fixed r: z from r to 2
rr = 1.4
s += dashed(X(rr), Y(rr), X(rr), oy)
s += end_group()
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">' + arrow(X(rr), Y(rr) - 3, X(rr), Y(2) + 3, color=BLUE) + '</g>\n'
s += f'<circle cx="{X(rr)}" cy="{Y(rr)}" r="3" fill="{BLUE}" stroke="none"/>\n'
# labels on the drawing
s += text(X(2.7) + 2, oy + 22, [("v", "x")], anchor="end")
s += text(ox + 10, 70, [("v", "z")])
s += text(ox - 8, oy + 20, [("n", "O")], anchor="end")
s += text(X(2), oy + 22, [("n", "2")], anchor="middle")
s += text(X(rr), oy + 22, [("v", "r")], anchor="middle")
s += text(X(1.0) + 8, Y(2) - 36, [("v", "n̂"), ("n", " = "), ("v", "k̂")])
s += text(X(0.75) + 26, Y(0.75) + 36, [("v", "n̂")])
s += text(X(-0.75) - 26, Y(0.75) + 36, [("v", "n̂")], anchor="end")
s += text(X(-1.35) - 10, Y(1.35) + 4, [("v", "S")], anchor="end")
s += text(X(-1.2), Y(2) - ry - 6, [("v", "D")], anchor="middle")
s += ctext(X(-0.4), Y(1.0), [("v", "V")], anchor="middle")
# side notes
P = 430
s += mtext(P, 100, [("v", "S"), ("n", "： "), ("v", "x"), ("sup", "2"), ("n", " + "), ("v", "y"), ("sup", "2"), ("n", " = "), ("v", "z"), ("sup", "2"), ("n", "，0 ≤ "), ("v", "z"), ("n", " ≤ 2")])
s += text(P, 126, [("t", "側面，柱座標 "), ("v", "r"), ("n", " = "), ("v", "z")])
s += text(P, 164, [("v", "D"), ("n", "： "), ("v", "z"), ("n", " = 2，"), ("v", "r"), ("n", " ≤ 2"), ("t", "（補的頂蓋）")])
s += ctext(P, 202, [("v", "V"), ("n", "： "), ("v", "r"), ("n", " ≤ "), ("v", "z"), ("n", " ≤ 2"), ("t", "（實心圓錐）")])
s += text(P, 244, [("t", "側面外法向：離軸且朝下")])
s += text(P, 270, [("t", "頂蓋外法向："), ("v", "n̂"), ("n", " = "), ("v", "k̂")])
s += ctext(P, 312, [("t", "藍線：固定 "), ("v", "r"), ("t", "，"), ("v", "z"), ("t", " 由 "), ("v", "r"), ("t", " 積到 "), ("n", "2")])
s += text(P, 350, [("t", "圖為 "), ("v", "xz"), ("t", " 截面（"), ("v", "θ"), ("n", " = 0 時 "), ("v", "x"), ("n", " = "), ("v", "r"), ("t", "）")])
s += footer()
write('EE-107-03-3-cone.svg', s)
