"""EE-105-02-5 (2b): half-controlled bridge (2 SCR + 2 diodes) vs fully-controlled bridge (4 SCR), R-L load with continuous current."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

YP, YM, YN = 60, 150, 240
X1, X2, XL = 110, 230, 340


def scr(xa, ya, xk, yk, size=10, gate_left=True):
    """Thyristor: diode symbol plus a gate lead leaving the cathode bar diagonally."""
    s = diode(xa, ya, xk, yk, size)
    # vertical devices only (anode below, cathode above): bar at y = mid - size
    m = (ya + yk) / 2
    yb = m - size if yk < ya else m + size
    sx = -1 if gate_left else 1
    gx, gy = xk + sx * size, yb
    return s + line(gx, gy, gx + sx * 12, gy + (12 if yk < ya else -12))


def skeleton(ox):
    s = line(ox + X1, YP, ox + XL, YP) + line(ox + X1, YN, ox + XL, YN)
    s += resistor(ox + XL, YP, ox + XL, 150, zigs=6, lead=14) + coil(ox + XL, 150, ox + XL, YN, turns=4)
    s += ac_source(ox + (X1 + X2) / 2, YM) + line(ox + X1, YM, ox + (X1 + X2) / 2 - 14, YM) + line(ox + (X1 + X2) / 2 + 14, YM, ox + X2, YM)
    for x, y in ((X1, YM), (X2, YM), (X1, YP), (X2, YP), (X1, YN), (X2, YN)):
        s += dot(ox + x, y)
    return s


W, H = 720, 344
s = header(W, H)
s += skeleton(0)
s += scr(X1, YM, X1, YP) + scr(X2, YM, X2, YP, gate_left=False)
s += diode(X1, YN, X1, YM) + diode(X2, YN, X2, YM)
s += skeleton(345)
s += scr(345 + X1, YM, 345 + X1, YP) + scr(345 + X2, YM, 345 + X2, YP, gate_left=False)
s += scr(345 + X1, YN, 345 + X1, YM) + scr(345 + X2, YN, 345 + X2, YM, gate_left=False)
s += end_group()
for ox, title in ((0, "(a) 半控橋：2 SCR + 2 二極體"), (345, "(b) 全控橋：4 SCR")):
    s += text(ox + 6, 24, [("t", title)])
    s += text(ox + X1 - 8, YM + 24, [("t", "AC1")], anchor="end")
    s += text(ox + X2 + 8, YM + 24, [("t", "AC2")])
    s += text(ox + (X1 + X2) / 2, YM - 22, [("v", "v"), ("vsub", "s")], anchor="middle")
    s += text(ox + XL + 12, 108, [("v", "R")])
    s += text(ox + XL + 12, 200, [("v", "L")])
    s += text(ox + XL - 22, YP + 26, [("n", "(+)")], anchor="end")
    s += text(ox + XL - 22, YN - 12, [("n", "(−)")], anchor="end")
s += text(X1 - 34, 112, [("t", "SCR1")], anchor="end")
s += text(X2 + 34, 112, [("t", "SCR2")])
s += text(X1 - 18, 204, [("v", "D"), ("sub", "3")], anchor="end")
s += text(X2 + 18, 204, [("v", "D"), ("sub", "4")])
s += text(345 + X1 - 34, 112, [("t", "SCR1")], anchor="end")
s += text(345 + X2 + 34, 112, [("t", "SCR2")])
s += text(345 + X1 - 34, 214, [("t", "SCR3")], anchor="end")
s += text(345 + X2 + 34, 214, [("t", "SCR4")])
s += ctext(6, 284, [("v", "V"), ("sub", "DC"), ("n", " = ("), ("v", "V"), ("vsub", "m"), ("n", "/π)(1 + cos "), ("v", "α"), ("n", ")")], color=BLUE)
s += text(6, 310, [("t", "不為負；"), ("v", "D"), ("sub", "3"), ("t", "、"), ("v", "D"), ("sub", "4"), ("t", " 提供自然續流")])
s += ctext(351, 284, [("v", "V"), ("sub", "DC"), ("n", " = (2"), ("v", "V"), ("vsub", "m"), ("n", "/π) cos "), ("v", "α")], color=BLUE)
s += text(351, 310, [("v", "α"), ("n", " &gt; 90°"), ("t", " 時為負（逆變），無續流路徑")])
s += footer()
write('EE-105-02-5-controlled.svg', s)
