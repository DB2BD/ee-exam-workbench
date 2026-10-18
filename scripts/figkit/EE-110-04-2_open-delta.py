"""EE-110-04-2 fig 2: two 380/220 V autotransformers in V (open-delta) for 3-phase 380 V -> 220 V.
Unit 1 across A-B, unit 2 across C-B, common ends on line B; taps give a and c, b = B.
Each unit: series winding (160 V) dotted at the line end (A or C), common winding (220 V) dotted at
the tap end (a or c) -- the same additive connection as fig 1."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import terminal, ttext

W, H = 680, 420
XL, XW, XR = 70, 300, 560            # HV terminals, winding column, LV terminals
YA, Ya, YB, Yc, YC = 60, 130, 200, 270, 340
s = header(W, H)
# unit 1: A -> series -> a -> common -> B
s += line(XL, YA, XW, YA) + line(XW, YA, XW, 72) + coil(XW, 72, XW, 118, turns=3, r=7.5) + line(XW, 118, XW, Ya)
s += line(XW, Ya, XW, 142) + coil(XW, 142, XW, 188, turns=3, r=7.5) + line(XW, 188, XW, YB)
# unit 2: C -> series -> c -> common -> B (drawn upward)
s += line(XL, YC, XW, YC) + line(XW, YC, XW, 328) + coil(XW, 328, XW, 282, turns=3, r=7.5) + line(XW, 282, XW, Yc)
s += line(XW, Yc, XW, 258) + coil(XW, 258, XW, 212, turns=3, r=7.5) + line(XW, 212, XW, YB)
# cores (one per unit)
s += line(XW - 28, 66, XW - 28, 194) + line(XW - 22, 66, XW - 22, 194)
s += line(XW - 28, 206, XW - 28, 334) + line(XW - 22, 206, XW - 22, 334)
# polarity dots: series at line end, common at tap end
s += dot(XW + 14, 76) + dot(XW + 14, 146)
s += dot(XW + 14, 324) + dot(XW + 14, 254)
# B line straight through, taps out
s += line(XL, YB, XR, YB) + dot(XW, YB)
s += line(XW, Ya, XR, Ya) + dot(XW, Ya) + line(XW, Yc, XR, Yc) + dot(XW, Yc)
for y in (YA, YB, YC):
    s += terminal(XL, y)
for y in (Ya, YB, Yc):
    s += terminal(XR, y)
# 3-phase load box
s += line(XR, Ya, XR + 30, Ya) + line(XR, YB, XR + 30, YB) + line(XR, Yc, XR + 30, Yc)
s += f'<rect x="{XR + 30}" y="{Ya - 20}" width="56" height="{Yc - Ya + 40}"/>\n'
s += end_group()
for y, n in ((YA, "A"), (YB, "B"), (YC, "C")):
    s += text(XL - 12, y + 6, [("v", n)], anchor="end")
for y, n in ((Ya, "a"), (YB, "b"), (Yc, "c")):
    s += text(XR - 4, y - 10, [("v", n)], anchor="end")
s += text(XR + 58, YB - 6, [("t", "三相")], anchor="middle")
s += text(XR + 58, YB + 16, [("t", "負載")], anchor="middle")
s += ttext(XW + 26, 100, [("v", "V"), ("vsub", "se"), ("n", " = 160 V")], color=BLUE) + text(XW + 136, 100, [("t", "串聯")])
s += ttext(XW + 26, 170, [("v", "V"), ("vsub", "c"), ("n", " = 220 V")], color=BLUE) + text(XW + 136, 170, [("t", "公共")])
s += ttext(XW + 26, 240, [("v", "V"), ("vsub", "c"), ("n", " = 220 V")], color=BLUE) + text(XW + 136, 240, [("t", "公共")])
s += ttext(XW + 26, 310, [("v", "V"), ("vsub", "se"), ("n", " = 160 V")], color=BLUE) + text(XW + 136, 310, [("t", "串聯")])
s += text(XW - 40, 134, [("t", "第 1 台")], anchor="end")
s += text(XW - 40, 274, [("t", "第 2 台")], anchor="end")
# line-to-line voltages between the HV terminals: + at A (C), - at B
s += ttext(XL + 30, YA + 26, [("n", "+")], color=BLUE) + ttext(XL + 30, YB - 10, [("n", "−")], color=BLUE)
s += ttext(XL + 30, 136, [("v", "V"), ("vsub", "AB"), ("n", " = 380 V")], color=BLUE)
s += ttext(XL + 30, YC - 12, [("n", "+")], color=BLUE) + ttext(XL + 30, YB + 26, [("n", "−")], color=BLUE)
s += ttext(XL + 30, 276, [("v", "V"), ("vsub", "CB"), ("n", " = 380 V")], color=BLUE)
s += text(340, 382, [("t", "兩台各跨 "), ("v", "A"), ("t", "–"), ("v", "B"), ("t", "、"), ("v", "C"), ("t", "–"), ("v", "B"), ("t", "，公共端共接 "), ("v", "B"), ("t", " 線（"), ("v", "b"), ("n", " = "), ("v", "B"), ("t", "）")], anchor="middle")
s += ttext(340, 408, [("v", "V"), ("vsub", "ab"), ("n", " = "), ("v", "V"), ("vsub", "cb"), ("n", " = "), ("v", "V"), ("vsub", "ac"), ("n", " = 220 V")], anchor="middle", color=BLUE)
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-110-04-2-open-delta.svg'
out.write_text(s)
print(out.name, len(s))
