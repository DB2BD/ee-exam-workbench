import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 360
YS = [70, 145, 220]                 # branch rows T_R1, T_R2, T_R3
YR = 300                            # reference line
XL, XR = 160, 420                   # left node (161 kV side), right node (69 kV side)
XS, XLD = 50, 580                   # source, load
s = header(W, H)
s += line(XL, YS[0], XL, YS[2]) + line(XR, YS[0], XR, YS[2])
for y in YS:
    s += line(XL, y, 185, y) + resistor(185, y, 255, y) + coil(265, y, 345, y, turns=4) + line(255, y, 265, y) + line(345, y, XR, y)
    s += dot(XL, y) + dot(XR, y)
YM = YS[1]
s += line(XS, YM, XL, YM)
s += line(XS, YM, XS, 211) + ac_source(XS, 225) + line(XS, 239, XS, YR)
s += line(XR, YM, XLD, YM) + line(XLD, YM, XLD, 200)
s += f'<rect x="{XLD - 14}" y="200" width="28" height="56"/>\n' + line(XLD, 256, XLD, YR)
s += line(XS, YR, XLD, YR)
s += dot(XS, YM) + dot(XLD, YM)
# voltages: reference line -> node (blue)
s += arrow(100, YR - 6, 100, YM + 10, color=BLUE)
s += arrow(450, YR - 6, 450, YM + 10, color=BLUE)
# currents (red)
for y in YS:
    s += arrow(366, y, 406, y, color=RED)
s += arrow(474, YM, 536, YM, color=RED)
s += end_group()
for k, (y, z) in enumerate(zip(YS, ["0.005 + ", "0.006 + ", "0.007 + "]), start=1):
    xs = ["0.10", "0.12", "0.14"][k - 1]
    s += text(265, y - 14, [("v", "z"), ("sub", str(k)), ("n", " = " + z), ("v", "j"), ("n", xs)], anchor="middle")
    s += ctext(RED, 386, y - 10, [("v", "I"), ("sub", str(k))], anchor="middle")
s += ctext(RED, 505, YM - 10, [("v", "I"), ("vsub", "L")], anchor="middle")
s += ctext(BLUE, 108, 230, [("v", "E")])
s += text(20, YS[0] - 12, [("t", "161 kV 側")])
s += ctext(BLUE, 458, 230, [("v", "V"), ("vsub", "L"), ("n", " = 1∠0°")])
s += text(700, YS[0] - 12, [("t", "69 kV 側")], anchor="end")
s += text(604, 225, [("v", "S"), ("vsub", "L"), ("n", " =")])
s += text(604, 247, [("n", "1.60 + "), ("v", "j"), ("n", "1.20")])
s += text(360, 340, [("t", "標么值，基準 200 MVA；忽略激磁支路，每台只剩串聯阻抗")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-2-parallel.svg'), 'w').write(s)
print(len(s))
