import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Per-phase line with a series capacitor: V_S∠δ — jX_L — (−jX_C) — V_R∠0°, lossless short-line model.
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap_h(x1, x2, y, gap=10, w=28):
    m = (x1 + x2) / 2
    return (line(x1, y, m - gap / 2, y) + line(m - gap / 2, y - w / 2, m - gap / 2, y + w / 2)
            + line(m + gap / 2, y - w / 2, m + gap / 2, y + w / 2) + line(m + gap / 2, y, x2, y))
W, H = 640, 290
YT, YB = 80, 210
XS, XR = 90, 550
s = header(W, H)
s += line(XS, YT, XS, 131) + ac_source(XS, 145) + line(XS, 159, XS, YB)
s += line(XR, YT, XR, 131) + ac_source(XR, 145) + line(XR, 159, XR, YB)
s += line(XS, YT, 160, YT) + coil(160, YT, 290, YT, turns=5) + line(290, YT, 350, YT)
s += cap_h(350, 420, YT) + line(420, YT, XR, YT)
s += line(XS, YB, XR, YB)
s += dot(XS, YT) + dot(XR, YT) + dot(XS, YB) + dot(XR, YB)
s += arrow(440, YT - 14, 500, YT - 14, color=RED)
s += end_group()
s += text(225, YT - 20, [("v", "j"), ("v", "X"), ("vsub", "L")], anchor="middle")
s += text(385, YT - 26, [("n", "−"), ("v", "j"), ("v", "X"), ("vsub", "C")], anchor="middle")
s += ctext(RED, 470, YT - 24, [("v", "I")], anchor="middle")
s += ctext(BLUE, XS + 24, 150, [("v", "V"), ("vsub", "S"), ("n", "∠"), ("v", "δ")])
s += ctext(BLUE, XR - 24, 150, [("v", "V"), ("vsub", "R"), ("n", "∠0°")], anchor="end")
s += text(225, YT + 30, [("t", "線路")], anchor="middle")
s += text(385, YT + 30, [("t", "串聯電容器")], anchor="middle")
s += text(W / 2, YB + 30, [("t", "中性點")], anchor="middle")
s += text(W / 2, YB + 62, [("t", "串聯總電抗 "), ("v", "X"), ("vsub", "eq"), ("n", " = "), ("v", "X"), ("vsub", "L"), ("n", " − "), ("v", "X"), ("vsub", "C"), ("n", " = (1 − "), ("v", "k"), ("n", ")"), ("v", "X"), ("vsub", "L")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-111-05-1-circuit.svg'), 'w').write(s)
print(len(s))
