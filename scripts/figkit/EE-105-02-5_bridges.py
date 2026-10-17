"""EE-105-02-5 (2a): half-bridge rectifier (diode leg + capacitor leg) vs full-bridge rectifier (two diode legs)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

YP, YM, YN = 60, 150, 240          # (+) rail, AC mid row, (-) rail
X1, X2, XL = 110, 230, 310         # left leg, right leg, load


def skeleton(ox):
    s = line(ox + X1, YP, ox + XL, YP) + line(ox + X1, YN, ox + XL, YN)
    s += resistor(ox + XL, YP, ox + XL, YN, zigs=6, lead=50)
    s += ac_source(ox + (X1 + X2) / 2, YM) + line(ox + X1, YM, ox + (X1 + X2) / 2 - 14, YM) + line(ox + (X1 + X2) / 2 + 14, YM, ox + X2, YM)
    for x, y in ((X1, YM), (X2, YM), (X1, YP), (X2, YP), (X1, YN), (X2, YN)):
        s += dot(ox + x, y)
    return s


W, H = 720, 344
s = header(W, H)
# (a) half bridge: diode leg on the left, capacitor leg on the right
s += skeleton(0)
s += diode(X1, YM, X1, YP) + diode(X1, YN, X1, YM)
s += cap(X2, YP, X2, YM) + cap(X2, YM, X2, YN)
# (b) full bridge: two diode legs
s += skeleton(360)
s += diode(360 + X1, YM, 360 + X1, YP) + diode(360 + X1, YN, 360 + X1, YM)
s += diode(360 + X2, YM, 360 + X2, YP) + diode(360 + X2, YN, 360 + X2, YM)
s += end_group()
for ox, title in ((0, "(a) 半橋：2 二極體 + 2 電容"), (360, "(b) 全橋：4 二極體")):
    s += text(ox + 6, 24, [("t", title)])
    s += text(ox + X1 - 8, YM + 22, [("t", "AC1")], anchor="end")
    s += text(ox + (X1 + X2) / 2, YM - 22, [("v", "v"), ("vsub", "s")], anchor="middle")
    s += text(ox + (X1 + X2) / 2 - 22, YM - 8, [("n", "+")], anchor="end")
    s += text(ox + XL + 14, YM + 6, [("v", "R"), ("vsub", "L")])
    s += text(ox + XL - 10, YP + 26, [("n", "(+)")], anchor="end")
    s += text(ox + XL - 10, YN - 12, [("n", "(−)")], anchor="end")
s += text(X1 - 18, 110, [("v", "D"), ("sub", "1")], anchor="end")
s += text(X1 - 18, 200, [("v", "D"), ("sub", "2")], anchor="end")
s += text(X2 + 20, 110, [("v", "C"), ("sub", "1")])
s += text(X2 + 20, 200, [("v", "C"), ("sub", "2")])
s += text(X2 + 8, YM + 22, [("v", "M")])
s += text(360 + X1 - 18, 110, [("v", "D"), ("sub", "1")], anchor="end")
s += text(360 + X1 - 18, 200, [("v", "D"), ("sub", "3")], anchor="end")
s += text(360 + X2 + 18, 110, [("v", "D"), ("sub", "2")])
s += text(360 + X2 + 18, 200, [("v", "D"), ("sub", "4")])
s += text(360 + X2 + 8, YM + 22, [("t", "AC2")])
s += text(6, 276, [("t", "正峰值經 "), ("v", "D"), ("sub", "1"), ("t", " 把 "), ("v", "C"), ("sub", "1"), ("t", " 充到 "), ("v", "V"), ("vsub", "m"), ("t", "（對 "), ("v", "M"), ("t", "）")])
s += text(6, 300, [("t", "負峰值經 "), ("v", "D"), ("sub", "2"), ("t", " 把 "), ("v", "C"), ("sub", "2"), ("t", " 充到 "), ("v", "V"), ("vsub", "m"), ("t", "（對 "), ("v", "M"), ("t", "）")])
s += text(6, 324, [("t", "無載 (+)(−) 間 ≈ 2"), ("v", "V"), ("vsub", "m"), ("t", "；每顆 PIV ≈ 2"), ("v", "V"), ("vsub", "m")])
s += text(366, 276, [("t", "正半週 "), ("v", "D"), ("sub", "1"), ("t", "、"), ("v", "D"), ("sub", "4"), ("t", " 導通，負半週 "), ("v", "D"), ("sub", "2"), ("t", "、"), ("v", "D"), ("sub", "3"), ("t", " 導通")])
s += text(366, 300, [("v", "v"), ("vsub", "o"), ("n", " = |"), ("v", "v"), ("vsub", "s"), ("n", "|"), ("t", "，峰值 "), ("v", "V"), ("vsub", "m")])
s += text(366, 324, [("t", "每顆 PIV ≈ "), ("v", "V"), ("vsub", "m"), ("t", "；導通路徑串 2 顆")])
s += footer()
write('EE-105-02-5-bridges.svg', s)
