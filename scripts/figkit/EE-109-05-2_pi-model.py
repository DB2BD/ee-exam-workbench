import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap_v(x, y1, y2):
    m = (y1 + y2) / 2
    return line(x, y1, x, m - 4) + line(x - 13, m - 4, x + 13, m - 4) + line(x - 13, m + 4, x + 13, m + 4) + line(x, m + 4, x, y2)
W, H = 720, 320
YT, YB = 80, 220
XS, X1, X2, XR = 150, 250, 490, 580       # sending source, left shunt node, right shunt node, receiving terminal
s = header(W, H)
s += line(XS, YT, XS, 136) + ac_source(XS, 150) + line(XS, 164, XS, YB)
s += line(XS, YT, X1, YT) + line(X1, YT, 300, YT) + coil(300, YT, 440, YT, turns=5) + line(440, YT, XR, YT)
s += line(X1, YT, X1, 125) + cap_v(X1, 125, 175) + line(X1, 175, X1, YB)
s += line(X2, YT, X2, 125) + cap_v(X2, 125, 175) + line(X2, 175, X2, YB)
s += line(XS, YB, XR, YB)
s += dot(X1, YT) + dot(X1, YB) + dot(X2, YT) + dot(X2, YB) + dot(XR, YT) + dot(XR, YB)
s += arrow(XR, YB - 6, XR, YT + 14, color=BLUE)          # V_R: reference -> receiving node (+)
s += end_group()
s += ctext(BLUE, XS - 24, 146, [("v", "V"), ("vsub", "S"), ("sub", ","), ("vsub", "ϕ")], anchor="end")
s += ctext(BLUE, XS - 24, 168, [("n", "199.19∠30° kV")], anchor="end")
s += text(370, YT - 18, [("v", "j"), ("v", "X"), ("n", " = "), ("v", "j"), ("n", "78.047 Ω")], anchor="middle")
s += text(X1 + 18, 146, [("v", "Y"), ("n", "/2")])
s += text(X2 - 18, 146, [("v", "Y"), ("n", "/2")], anchor="end")
s += ctext(BLUE, XR + 12, 146, [("v", "V"), ("vsub", "R"), ("sub", ","), ("vsub", "ϕ")])
s += ctext(BLUE, XR + 12, 168, [("n", "189.23∠0° kV")])
s += text(XS, YB + 24, [("t", "中性點")], anchor="middle")
s += text(370, 270, [("t", "每相 π 模型：實功率只經串聯 "), ("v", "j"), ("v", "X"), ("t", "；兩端 "), ("v", "Y"), ("n", "/2"), ("t", " 為純電容")], anchor="middle")
s += text(370, 300, [("v", "Y"), ("n", "/2 = "), ("v", "j"), ("n", "4.145×10"), ("sub", "")], anchor="middle")
s += footer()
s = s.replace('<tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif">4.145×10</tspan><tspan class="n sub" font-family="KaTeX_Main, \'Times New Roman\', serif" font-size="12" baseline-shift="sub"></tspan>',
              '<tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif">4.145×10</tspan><tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif" font-size="12" baseline-shift="super">−4</tspan><tspan class="n" font-family="KaTeX_Main, \'Times New Roman\', serif"> S</tspan>')
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-109-05-2-pi-model.svg'), 'w').write(s)
print(len(s))
