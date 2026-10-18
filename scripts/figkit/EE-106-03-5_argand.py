import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# Argand plane: z = 1 - sqrt(3) i, modulus r = 2, argument theta = -pi/3 (fourth quadrant).
W, H = 560, 420
ox, oy = 180, 130          # origin z = 0
u = 130                    # px per unit
zx, zy = ox + 1 * u, oy + math.sqrt(3) * u
s = header(W, H)
# axes
s += arrow(40, oy, 520, oy) + arrow(ox, 400, ox, 20)
# projections of z onto the axes (dashed)
s += dashed(zx, oy, zx, zy) + dashed(ox, zy, zx, zy)
# ticks Re = 1, Im = -sqrt(3)
s += line(zx, oy - 5, zx, oy + 5)
s += line(ox - 5, zy, ox + 5, zy)
# vector 0 -> z (blue)
s += arrow(ox, oy, zx, zy, color=BLUE)
s += dot(zx, zy)
# angle arc from +Re axis clockwise to the vector (theta negative)
R = 46
ex, ey = ox + R * math.cos(math.radians(60)), oy + R * math.sin(math.radians(60))
s += f'<path d="M{ox + R} {oy} A{R} {R} 0 0 1 {ex:.1f} {ey:.1f}" stroke="{BLUE}"/>\n'
a1, a2 = math.radians(52), math.radians(60)
s += arrow(ox + R * math.cos(a1), oy + R * math.sin(a1), ex, ey, color=BLUE)
s += end_group()
# labels
s += text(522, oy + 24, [("n", "Re "), ("v", "z")], anchor="end")
s += text(ox + 10, 32, [("n", "Im "), ("v", "z")])
s += text(ox - 8, oy - 8, [("n", "0")], anchor="end")
s += text(zx, oy - 10, [("n", "1")], anchor="middle")
s += text(ox - 10, zy + 5, [("n", "−√3")], anchor="end")
s += text(zx + 12, zy + 6, [("v", "z"), ("n", " = 1 − √3 "), ("v", "i")])
mx, my = (ox + zx) / 2 + 12 * math.sin(math.radians(60)), (oy + zy) / 2 - 12 * math.cos(math.radians(60))
s += text(mx, my, [("v", "r"), ("n", " = |"), ("v", "z"), ("n", "| = 2")], anchor="middle").replace(
    '<text ', f'<text transform="rotate(60 {mx:.1f} {my:.1f})" ', 1)
s += ctext(ox + 56, oy + 30, [("v", "θ"), ("n", " = −π/3")])
s += text(zx + 90, oy + 110, [("t", "第四象限")])
s += footer()
write('EE-106-03-5-argand.svg', s)
