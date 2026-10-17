"""EE-105-02-3: transfer characteristic v_O(v_S) of the limiter: slope -4 between the knees,
slope -(R_F || R_3)/R_1 = -(R_F || R_5)/R_1 = -0.06557 outside; knees and the v_S = 5 V point marked."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

R1, RF, R3, R5 = 15.0, 60.0, 1.0, 1.0
k = -(RF * R3 / (RF + R3)) / R1                       # -0.06557
vs_min, vo_max = -0.96, 3.84
vs_max, vo_min = 1.15625, -4.625


def vo(vs):
    if vs <= vs_min:
        return vo_max + k * (vs - vs_min)
    if vs >= vs_max:
        return vo_min + k * (vs - vs_max)
    return -4 * vs


X0, Y0, SX, SY = 250, 160, 52, 24                       # origin and px per volt
P = lambda vs, v: (X0 + SX * vs, Y0 - SY * v)
W, H = 720, 320
s = header(W, H)
s += arrow(X0 - SX * 3.3, Y0, X0 + SX * 8.2, Y0) + arrow(X0, Y0 + SY * 6.2, X0, Y0 - SY * 5.6)
for vs, v in ((vs_min, vo_max), (vs_max, vo_min), (5.0, vo(5.0))):
    x, y = P(vs, v)
    s += dashed(x, y, x, Y0) + dashed(x, y, X0, y)
s += poly([P(-3.2 + 0.05 * i, vo(-3.2 + 0.05 * i)) for i in range(229)], w=2.4, color=BLUE)
for vs, v in ((vs_min, vo_max), (vs_max, vo_min), (5.0, vo(5.0))):
    s += dot(*P(vs, v))
s += end_group()
s += text(X0 + SX * 8.2, Y0 + 22, [("v", "v"), ("vsub", "S"), ("n", " (V)")], anchor="end")
s += text(X0 + 8, Y0 - SY * 5.6 + 6, [("v", "v"), ("vsub", "O"), ("n", " (V)")])
x, y = P(vs_min, vo_max)
s += text(x - 6, y - 10, [("v", "v"), ("vsub", "O"), ("sub", "(max)"), ("n", " = 3.84 V")], anchor="end")
s += text(x, Y0 + 20, [("v", "v"), ("vsub", "S"), ("sub", "(min)"), ("n", " = −0.96 V")], anchor="end")
x, y = P(vs_max, vo_min)
s += text(X0 - 8, y + 5, [("v", "v"), ("vsub", "O"), ("sub", "(min)"), ("n", " = −4.63 V")], anchor="end")
s += text(x + 4, Y0 - 10, [("v", "v"), ("vsub", "S"), ("sub", "(max)"), ("n", " = 1.16 V")])
x, y = P(5.0, vo(5.0))
s += text(x, y + 28, [("v", "v"), ("vsub", "S"), ("n", " = 5 V："), ("v", "v"), ("vsub", "O"), ("n", " = −4.88 V")], anchor="middle")
s += text(X0 + 40, Y0 - 76, [("t", "斜率 −"), ("v", "R"), ("vsub", "F"), ("n", "/"), ("v", "R"), ("sub", "1"), ("n", " = −4")])
s += text(708, Y0 + 62, [("t", "斜率 −("), ("v", "R"), ("vsub", "F"), ("n", "∥"), ("v", "R"), ("sub", "3"), ("n", ")/"), ("v", "R"), ("sub", "1")], anchor="end")
s += text(708, Y0 + 84, [("n", "= −0.06557（"), ("v", "D"), ("sub", "1"), ("t", " 導通段）")], anchor="end")
s += text(16, Y0 - SY * 3.84 + 30, [("t", "（"), ("v", "D"), ("sub", "2"), ("t", " 導通段）")])
s += text(16, Y0 - SY * 3.84 + 52, [("t", "斜率 −("), ("v", "R"), ("vsub", "F"), ("n", "∥"), ("v", "R"), ("sub", "5"), ("n", ")/"), ("v", "R"), ("sub", "1")])
s += text(X0 + 40, Y0 - 54, [("t", "（"), ("v", "D"), ("sub", "1"), ("t", "、"), ("v", "D"), ("sub", "2"), ("t", " 皆截止）")])
s += footer()
write('EE-105-02-3-transfer.svg', s)
