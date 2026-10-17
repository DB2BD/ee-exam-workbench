"""EE-107-01-3: circuit after the Delta(a, b, c) -> Y(n) conversion; two parallel n-d paths, I0, I4, I5, V_n, V1, V2."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 470
XS, XN, XL, XR = 80, 360, 250, 470
YA, YN, YBC, YD = 70, 150, 230, 340


def zbox(x, y1, y2, w=22):
    """Generic (complex) impedance drawn as a box on a vertical wire."""
    m, h = (y1 + y2) / 2, 22
    return line(x, y1, x, m - h) + f'<rect x="{x - w / 2}" y="{m - h}" width="{w}" height="{2 * h}"/>\n' + line(x, m + h, x, y2)


s = header(W, H)
s += f'<rect x="{XL - 40}" y="{YA + 22}" width="{XR - XL + 80}" height="{YBC - YA - 6}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += vsrc(XS, YA, XS, YD, r=18) + line(XS, YA, XN, YA) + line(XS, YD, XR, YD)
s += zbox(XN, YA, YN)
s += line(XL, YN, XR, YN)
s += zbox(XL, YN, YBC) + zbox(XR, YN, YBC)
s += resistor(XL, YBC, XL, 280, zigs=4, lead=8) + coil(XL, 280, XL, YD)
s += line(XR, YBC, XR, 270) + cap(XR, 270, XR, 300) + line(XR, 300, XR, YD)
for p in ((XN, YA), (XN, YN), (XL, YBC), (XR, YBC), (XL, YD), (XR, YD)):
    s += dot(*p)
s += tint_arrow(170, YA - 16, 240, YA - 16)          # I0
s += tint_arrow(XL - 20, 258, XL - 20, 300)          # I4 down n-b-d
s += tint_arrow(XR + 20, 258, XR + 20, 300)          # I5 down n-c-d
s += end_group()
s += text(XN, YA - 12, [("v", "a")], anchor="middle")
s += text(XN + 10, YN - 8, [("v", "n")])
s += text(XL + 14, YBC + 18, [("v", "b")]) + text(XR - 14, YBC + 18, [("v", "c")], anchor="end")
s += text(XR, YD + 24, [("v", "d")], anchor="middle")
s += text(XS + 26, 210, [("n", "120∠0° V")])
s += text(XN + 18, 116, [("v", "Z"), ("vsub", "an")])
s += text(XL + 18, 196, [("v", "Z"), ("vsub", "bn")])
s += text(XR - 18, 196, [("v", "Z"), ("vsub", "cn")], anchor="end")
s += text(XL + 16, 284, [("n", "20 + "), ("v", "j"), ("n", "60 Ω")])
s += text(XR - 26, 290, [("n", "−"), ("v", "j"), ("n", "20 Ω")], anchor="end")
s += text(XR + 50, 112, [("t", "Δ→Y 後的等效 Y")])
s += ttext(205, YA - 24, [("v", "I"), ("sub", "0")], anchor="middle", color=RED)
s += ttext(XL - 26, 284, [("v", "I"), ("sub", "4")], anchor="end", color=RED)
s += ttext(XR + 28, 284, [("v", "I"), ("sub", "5")], color=RED)
s += ttext(XN - 10, YN - 8, [("v", "V"), ("vsub", "n")], anchor="end", color=BLUE)
s += ttext(XL - 80, YBC + 22, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XL - 80, 290, [("v", "V"), ("sub", "1")], anchor="middle", color=BLUE)
s += ttext(XL - 80, YD - 8, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XR + 70, YBC + 22, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XR + 70, 290, [("v", "V"), ("sub", "2")], anchor="middle", color=BLUE)
s += ttext(XR + 70, YD - 8, [("n", "−")], anchor="middle", color=BLUE)
y0 = 400
s += text(30, y0, [("v", "Z"), ("vsub", "an"), ("n", " = 0.206536 − "), ("v", "j"), ("n", "3.44904 Ω")])
s += text(370, y0, [("v", "Z"), ("vsub", "bn"), ("n", " = 0.0119385 − "), ("v", "j"), ("n", "0.546187 Ω")])
s += text(30, y0 + 28, [("v", "Z"), ("vsub", "cn"), ("n", " = 8.62259 + "), ("v", "j"), ("n", "0.516341 Ω")])
s += text(370, y0 + 28, [("t", "（"), ("v", "d"), ("t", " 為參考點，"), ("v", "V"), ("vsub", "n"), ("t", " 為 "), ("v", "n"), ("t", " 對 "), ("v", "d"), ("t", " 電壓）")])
s += footer()
write('EE-107-01-3-wye.svg', s)
