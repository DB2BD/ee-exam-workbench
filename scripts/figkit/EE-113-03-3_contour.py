import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 620, 420
ox, oy = 310, 290          # origin z = 0
r1, R = 80, 220            # |z| = 1 circle and contour radius R (schematic)
s = header(W, H)
# axes
s += arrow(40, oy, 590, oy) + arrow(ox, 372, ox, 36)
# |z| = 1 (dashed)
s += f'<circle cx="{ox}" cy="{oy}" r="{r1}" stroke-dasharray="5 4"/>\n'
# contour: segment [-R, R] + upper semicircle C_R, counter-clockwise (blue)
s += f'<path d="M{ox - R} {oy} L{ox + R} {oy} A{R} {R} 0 0 0 {ox - R} {oy}" stroke="{BLUE}" stroke-width="2"/>\n'
s += arrow(ox + 90, oy, ox + 130, oy, color=BLUE)
s += arrow(ox + 20, oy - R, ox - 20, oy - R, color=BLUE)
s += arrow(ox - R * math.cos(math.radians(30)) + 0.0, oy - R * math.sin(math.radians(30)),
           ox - R * math.cos(math.radians(24)), oy - R * math.sin(math.radians(24)), color=BLUE)
# poles (x marks): upper half plane blue, lower half plane black
def cross(x, y, c):
    return f'<path d="M{x - 6:.1f} {y - 6:.1f} L{x + 6:.1f} {y + 6:.1f} M{x - 6:.1f} {y + 6:.1f} L{x + 6:.1f} {y - 6:.1f}" stroke="{c}" stroke-width="2"/>\n'
pts = {k: (ox + r1 * math.cos(math.radians(a)), oy - r1 * math.sin(math.radians(a))) for k, a in ((1, 45), (2, 135), (3, 225), (4, 315))}
for k, (x, y) in pts.items():
    s += cross(x, y, BLUE if k <= 2 else "#000")
s += end_group()
# labels
s += text(592, oy + 22, [("n", "Re "), ("v", "z")], anchor="end")
s += text(ox + 10, 46, [("n", "Im "), ("v", "z")])
s += text(ox - R, oy + 22, [("n", "−"), ("v", "R")], anchor="middle")
s += text(ox + R, oy + 22, [("v", "R")], anchor="middle")
s += text(ox - 8, oy + 20, [("n", "0")], anchor="end")
s += ctext(ox + R * 0.74 + 8, oy - R * 0.74 - 4, [("v", "C"), ("vsub", "R")])
s += ctext(ox + 150, oy - 14, [("t", "實軸段 "), ("n", "−"), ("v", "R"), ("n", " → "), ("v", "R")], anchor="middle")
x1, y1 = pts[1]; x2, y2 = pts[2]; x3, y3 = pts[3]; x4, y4 = pts[4]
s += text_sup(x1 + 10, y1 - 10, [("v", "z"), ("sub", "1"), ("n", " = "), ("v", "e")], [("v", "i"), ("v", "π"), ("n", "/4")], color=BLUE)
s += text_sup(x2 - 10, y2 - 10, [("v", "z"), ("sub", "2"), ("n", " = "), ("v", "e")], [("v", "i"), ("n", "3"), ("v", "π"), ("n", "/4")], anchor="end", color=BLUE)
s += text_sup(x3 - 10, y3 + 22, [("v", "z"), ("sub", "3"), ("n", " = "), ("v", "e")], [("v", "i"), ("n", "5"), ("v", "π"), ("n", "/4")], anchor="end")
s += text_sup(x4 + 10, y4 + 22, [("v", "z"), ("sub", "4"), ("n", " = "), ("v", "e")], [("v", "i"), ("n", "7"), ("v", "π"), ("n", "/4")])
s += text(ox - r1 - 6, oy + 32, [("n", "|"), ("v", "z"), ("n", "| = 1")], anchor="end")
s += text(ox, 404, [("t", "下半平面的 "), ("v", "z"), ("sub", "3"), ("t", "、"), ("v", "z"), ("sub", "4"), ("t", " 不在圍道內，不計留數")], anchor="middle")
s += footer()
write('EE-113-03-3-contour.svg', s)
