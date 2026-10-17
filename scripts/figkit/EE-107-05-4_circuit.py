import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap_h(x1, x2, y, gap=8, w=26):
    m = (x1 + x2) / 2
    return (line(x1, y, m - gap / 2, y) + line(m - gap / 2, y - w / 2, m - gap / 2, y + w / 2)
            + line(m + gap / 2, y - w / 2, m + gap / 2, y + w / 2) + line(m + gap / 2, y, x2, y))
def dashed(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke-dasharray="6 4"/>\n'
# Y source (neutral n, grounded) feeding a Y load (neutral N) through ideal lines a, b, c.
# Reference directions: line currents source -> load; I_n from N back to n (I_n = I_a + I_b + I_c).
W, H = 680, 400
XN, XS, XZ1, XZ2, XLN = 80, 150, 450, 540, 590
YA, YB, YC, YW = 80, 160, 240, 310
s = header(W, H)
s += line(XN, YA, XN, YW)                                   # source neutral bus n
for y in (YA, YB, YC):
    s += line(XN, y, XS - 16, y) + ac_source(XS, y, 16) + line(XS + 16, y, XZ1, y)
    s += line(XS + 20, y - 12, XS + 26, y - 12) + line(XS + 23, y - 15, XS + 23, y - 9)   # + mark on the line side
    s += dot(XN, y)
s += resistor(XZ1, YA, XZ2, YA) + line(XZ2, YA, XLN, YA)       # Z_a = 10
s += cap_h(XZ1, XZ2, YB) + line(XZ2, YB, XLN, YB)              # Z_b = -j10
s += coil(XZ1, YC, XZ2, YC, turns=4) + line(XZ2, YC, XLN, YC)  # Z_c = j10
s += line(XLN, YA, XLN, YC) + dot(XLN, YB) + dot(XLN, YC) + dot(XLN, YA)
s += dashed(XLN, YC, XLN, YW) + dashed(XLN, YW, XN, YW)        # neutral wire, only in (一)
s += dot(XN, YW) + line(XN, YW, XN, YW + 12) + ground(XN, YW + 12)
for y in (YA, YB, YC):
    s += arrow(300, y - 12, 350, y - 12, color=RED)
s += arrow(250, YW - 12, 200, YW - 12, color=RED)
s += end_group()
s += text(XN - 10, YA + 5, [("v", "n")], anchor="end")
s += text(XLN + 12, YB + 5, [("v", "N")])
for y, nm, val in ((YA, "a", "220∠0°"), (YB, "b", "220∠−120°"), (YC, "c", "220∠120°")):
    s += ctext(BLUE, XS + 4, y - 24, [("v", "V"), ("vsub", nm), ("n", " = " + val + " V")], anchor="middle")
    s += ctext(RED, 325, y - 24, [("v", "I"), ("vsub", nm)], anchor="middle")
s += text(495, YA - 16, [("v", "Z"), ("vsub", "a"), ("n", " = 10 Ω")], anchor="middle")
s += text(495, YB - 20, [("v", "Z"), ("vsub", "b"), ("n", " = −"), ("v", "j"), ("n", "10 Ω")], anchor="middle")
s += text(495, YC - 16, [("v", "Z"), ("vsub", "c"), ("n", " = "), ("v", "j"), ("n", "10 Ω")], anchor="middle")
s += ctext(RED, 225, YW - 22, [("v", "I"), ("vsub", "n")], anchor="middle")
s += text(470, YW + 24, [("t", "中性線：（一）接上；（二）拆除")], anchor="middle")
s += ctext(BLUE, XLN - 14, YW - 8, [("n", "+")], anchor="middle")
s += ctext(BLUE, XN + 14, YW - 8, [("n", "−")], anchor="middle")
s += ctext(BLUE, 400, YW - 12, [("v", "V"), ("vsub", "N"), ("t", "（"), ("v", "N"), ("t", " 對 "), ("v", "n"), ("t", "）")], anchor="middle")
s += text(340, 386, [("t", "（二）的線電流記 "), ("v", "I"), ("vsub", "a"), ("n", "′"), ("t", "、"), ("v", "I"), ("vsub", "b"), ("n", "′"), ("t", "、"), ("v", "I"), ("vsub", "c"), ("n", "′"), ("t", "，參考方向相同")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-107-05-4-circuit.svg'), 'w').write(s)
print(len(s))
