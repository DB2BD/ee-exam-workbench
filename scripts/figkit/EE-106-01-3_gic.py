"""EE-106-01-3: two-op-amp GIC with node voltages V1..V5, virtual shorts and the op-amp output nodes."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *


def zbox(x1, y, x2, w=44, h=14):
    """Generic impedance: rectangle centred on a horizontal segment."""
    m = (x1 + x2) / 2
    return line(x1, y, m - w / 2, y) + f'<rect x="{m - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}"/>\n' + line(m + w / 2, y, x2, y)


def vzbox(x, y1, y2, w=14, h=44):
    m = (y1 + y2) / 2
    return line(x, y1, x, m - h / 2) + f'<rect x="{x - w / 2:.1f}" y="{m - h / 2:.1f}" width="{w}" height="{h}"/>\n' + line(x, m + h / 2, x, y2)


def tri(xl, xr, yb, ya):
    """Op-amp triangle with a horizontal base (xl..xr at y = yb) and apex at y = ya."""
    return f'<path d="M{xl} {yb} L{xr} {yb} L{(xl + xr) / 2} {ya} Z"/>\n'


def pm(x, y, plus):
    s = line(x - 4, y, x + 4, y)
    return s + (line(x, y - 4, x, y + 4) if plus else '')


W, H = 720, 430
X1, X2, X3, X4, X5, XZ = 120, 240, 360, 480, 600, 670
Y, YG = 230, 330
s = header(W, H)
s += line(50, Y, X1, Y) + isrc(50, YG, 50, Y) + ground(50, YG)
s += zbox(X1, Y, X2) + zbox(X2, Y, X3) + zbox(X3, Y, X4) + zbox(X4, Y, X5)
s += line(X5, Y, XZ, Y) + vzbox(XZ, Y, YG) + ground(XZ, YG)
# op-amp A (top, apex up): + at x=200 (V1), - at x=260 (V3), output -> V4
s += tri(180, 280, 150, 70) + pm(205, 140, True) + pm(255, 140, False)
s += line(205, 150, 205, 180) + line(205, 180, X1, 180) + line(X1, 180, X1, Y)
s += line(255, 150, 255, 180) + line(255, 180, X3, 180) + line(X3, 180, X3, Y)
s += line(230, 70, 230, 40) + line(230, 40, X4, 40) + line(X4, 40, X4, Y)
# op-amp B (bottom, apex down): - at x=450 (V3), + at x=530 (V5), output -> V2
s += tri(430, 550, 300, 380) + pm(458, 310, False) + pm(522, 310, True)
s += line(458, 300, 458, 268) + line(458, 268, X3, 268) + line(X3, 268, X3, Y)
s += line(522, 300, 522, 268) + line(522, 268, X5, 268) + line(X5, 268, X5, Y)
s += line(490, 380, 490, 405) + line(490, 405, X2, 405) + line(X2, 405, X2, Y)
for x in (X1, X2, X3, X4, X5):
    s += dot(x, Y)
s += end_group()
s += ttext(20, 28, [("t", "理想運放虛短：A："), ("v", "V"), ("sub", "1"), ("n", " = "), ("v", "V"), ("sub", "3"),
                    ("t", "；B："), ("v", "V"), ("sub", "3"), ("n", " = "), ("v", "V"), ("sub", "5")], color=BLUE)
s += text(230, 124, [("n", "A")], anchor="middle") + text(490, 345, [("n", "B")], anchor="middle")
for x, k in ((X1, "1"), (X2, "2"), (X3, "3"), (X4, "4"), (X5, "5")):
    s += ttext(x + 6, Y + 26, [("v", "V"), ("sub", k)], color=BLUE)
for xa, xb, k in ((X1, X2, "1"), (X2, X3, "2"), (X3, X4, "3"), (X4, X5, "4")):
    s += text((xa + xb) / 2, Y - 14, [("v", "Z"), ("sub", k)], anchor="middle")
s += text(XZ + 14, 286, [("v", "Z"), ("sub", "5")])
s += ttext(28, 286, [("v", "I"), ("vsub", "s")], anchor="end", color=RED)
s += text(X4 + 8, 60, [("t", "A 輸出")])
s += text(X2 - 8, 398, [("t", "B 輸出")], anchor="end")
s += footer()
write('EE-106-01-3-gic.svg', s)
