import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-111-03-3: contour |z| = 2.5 (counter-clockwise); pole z = 1 inside, pole z = -3 outside.
W, H = 620, 400
ox, oy = 360, 185          # origin z = 0
u = 60                     # px per unit
R = 2.5 * u
s = header(W, H)
s += f'<circle cx="{ox}" cy="{oy}" r="{R}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(80, oy, 590, oy) + arrow(ox, 348, ox, 18)
s += f'<circle cx="{ox}" cy="{oy}" r="{R}" stroke="{BLUE}" stroke-width="2"/>\n'
for a in (60, 240):
    t1, t2 = math.radians(a - 6), math.radians(a + 6)
    s += arrow(ox + R * math.cos(t1), oy - R * math.sin(t1), ox + R * math.cos(t2), oy - R * math.sin(t2), color=BLUE)
# ticks at Re = -3, -2.5, 1, 2.5
for k in (-3, -2.5, 1, 2.5):
    s += line(ox + k * u, oy - 5, ox + k * u, oy + 5)
s += end_group()
def cross(x, y, c):
    return f'<path d="M{x - 7:.1f} {y - 7:.1f} L{x + 7:.1f} {y + 7:.1f} M{x - 7:.1f} {y + 7:.1f} L{x + 7:.1f} {y - 7:.1f}" stroke="{c}" stroke-width="2.2" fill="none"/>\n'
s += cross(ox + u, oy, BLUE) + cross(ox - 3 * u, oy, "#000")
# labels
s += text(592, oy + 24, [("n", "Re "), ("v", "z")], anchor="end")
s += text(ox + 10, 30, [("n", "Im "), ("v", "z")])
s += text(ox - 8, oy + 20, [("n", "0")], anchor="end")
s += ctext(ox + u, oy - 14, [("v", "z"), ("n", " = 1")], anchor="middle")
s += text(ox + 2.5 * u + 6, oy + 22, [("n", "2.5")])
s += text(ox - 2.5 * u + 6, oy + 22, [("n", "−2.5")])
s += text(ox - 3 * u, oy - 14, [("v", "z"), ("n", " = −3")], anchor="middle")
s += ctext(ox + R * math.cos(math.radians(38)) + 8, oy - R * math.sin(math.radians(38)) - 6,
           [("v", "C"), ("n", " : |"), ("v", "z"), ("n", "| = 2.5")])
s += text(W / 2, 384, [("n", "|1| = 1 &lt; 2.5"), ("t", "（圓內）；"), ("n", "|−3| = 3 &gt; 2.5"), ("t", "（圓外）")], anchor="middle")
s += footer()
write('EE-111-03-3-contour.svg', s)
