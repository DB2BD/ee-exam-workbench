import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# Contour |z| = 2 (counter-clockwise) and the single pole z0 = 1 - i inside it.
W, H = 560, 400
ox, oy = 250, 190          # origin z = 0
u = 70                     # px per unit
R = 2 * u
s = header(W, H)
# interior of gamma (light blue fill), then the contour itself (blue)
s += f'<circle cx="{ox}" cy="{oy}" r="{R}" fill="{FILL_BLUE}" stroke="none"/>\n'
# axes
s += arrow(40, oy, 470, oy) + arrow(ox, 372, ox, 22)
s += f'<circle cx="{ox}" cy="{oy}" r="{R}" stroke="{BLUE}" stroke-width="2"/>\n'
# counter-clockwise direction arrows on gamma (at 60 deg and 240 deg)
for a in (60, 240):
    t1, t2 = math.radians(a - 6), math.radians(a + 6)
    s += arrow(ox + R * math.cos(t1), oy - R * math.sin(t1), ox + R * math.cos(t2), oy - R * math.sin(t2), color=BLUE)
# ticks at Re = 1, 2 and Im = -1
for k in (1, 2):
    s += line(ox + k * u, oy - 5, ox + k * u, oy + 5)
s += line(ox - 5, oy + u, ox + 5, oy + u)
# pole z0 = 1 - i (x mark) and its distance from the origin (dashed)
px, py = ox + u, oy + u
s += dashed(ox, oy, px, py)
s += dashed(px, oy, px, py) + dashed(ox, py, px, py)
s += line(px + 9, py + 4, 398, 276)
s += f'<path d="M{px - 7} {py - 7} L{px + 7} {py + 7} M{px - 7} {py + 7} L{px + 7} {py - 7}" stroke-width="2.2"/>\n'
s += end_group()
# labels
s += text(472, oy + 24, [("n", "Re "), ("v", "z")], anchor="end")
s += text(ox + 10, 34, [("n", "Im "), ("v", "z")])
s += text(ox - 8, oy - 8, [("n", "0")], anchor="end")
s += text(ox + u, oy - 10, [("n", "1")], anchor="middle")
s += text(ox + R + 8, oy - 10, [("n", "2")])
s += text(ox - 10, oy + u + 5, [("n", "−1")], anchor="end")
s += text(404, 282, [("v", "z"), ("sub", "0"), ("n", " = 1 − "), ("v", "i")])
s += text(404, 306, [("n", "|"), ("v", "z"), ("sub", "0"), ("n", "| = √2 ≈ 1.414")])
s += ctext(ox + R * math.cos(math.radians(40)) + 8, oy - R * math.sin(math.radians(40)) - 6,
           [("v", "γ"), ("n", " : |"), ("v", "z"), ("n", "| = 2")])
s += text(W / 2, 390, [("v", "z"), ("sub", "0"), ("t", " 在圓內（"), ("n", "√2 &lt; 2"), ("t", "），逆時針一圈")], anchor="middle")
s += footer()
write('EE-105-03-4-contour.svg', s)
