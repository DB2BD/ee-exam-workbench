"""EE-106-01-2: node names, chosen state-variable references (v_C polarities, i_L directions) and the right-hand supernode."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 560
XL, XM, XR = 110, 340, 570
YT, YM, YB = 100, 290, 480
O = (XM, YM)


def name(x, y, letter, idx, anchor="start", color="#000"):
    return ttext(x, y, [("v", letter), ("sub", idx)], anchor=anchor, color=color)


s = header(W, H)
s += (f'<rect x="{XR - 16}" y="{YT - 26}" width="92" height="{YB - YT + 52}" '
      f'fill="{FILL_BLUE}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n')
s += resistor(XL, YT, XM, YT, lead=80) + resistor(XM, YT, XR, YT, lead=80)
s += resistor(XL, YB, XM, YB, lead=80) + resistor(XM, YB, XR, YB, lead=80)
s += coil(XL, YT, XL, YM) + cap(XR, YT, XR, YM)
s += vsrc(XL, YM, XL, YB) + vsrc(XR, YM, XR, YB)
s += coil(XL, YM, XM, YM) + coil(XM, YM, XR, YM)
s += cap(XM, YT, XM, YM) + cap(XM, YM, XM, YB)
for corner in ((XL, YT), (XR, YT), (XL, YB), (XR, YB)):
    s += resistor(*corner, *O, lead=100)
for p in ((XL, YT), (XM, YT), (XR, YT), (XL, YM), O, (XR, YM), (XL, YB), (XM, YB), (XR, YB)):
    s += dot(*p)
s += tint_arrow(XL + 18, 170, XL + 18, 214)            # i_L1: TL -> ML
s += tint_arrow(200, YM - 16, 250, YM - 16)            # i_L2: ML -> O
s += tint_arrow(430, YM - 16, 480, YM - 16)            # i_L3: O -> MR
s += end_group()
s += text(20, 34, [("t", "中心節點 "), ("v", "O"), ("t", " 為參考；電容極性與電感電流方向為自訂參考方向；虛線框為超節點")])
# element names
s += name(225, YT - 16, "R", "1", "middle") + name(455, YT - 16, "R", "2", "middle")
s += name(225, YB + 30, "R", "3", "middle") + name(455, YB + 30, "R", "4", "middle")
s += name(198, 222, "R", "5", "end") + name(482, 222, "R", "6")
s += name(198, 372, "R", "7", "end") + name(482, 372, "R", "8")
s += name(XL - 22, 200, "L", "1", "end")
s += name(225, YM + 30, "L", "2", "middle") + name(455, YM + 30, "L", "3", "middle")
s += name(XM + 22, 200, "C", "1") + name(XR - 24, 200, "C", "2", "end") + name(XM + 22, 400, "C", "3")
s += text(XL - 24, 390, [("v", "V"), ("vsub", "s"), ("sub", "1")], anchor="end")
s += text(XR + 24, 390, [("v", "V"), ("vsub", "s"), ("sub", "2")])
# node names
s += text(XL - 10, YT - 8, [("v", "TL")], anchor="end")
s += text(XM, YT - 36, [("v", "TM")], anchor="middle")
s += text(XR + 10, YT - 8, [("v", "TR")])
s += text(XL - 10, YM + 6, [("v", "ML")], anchor="end")
s += text(XM + 9, YM - 14, [("v", "O")])
s += text(XR + 10, YM + 22, [("v", "MR")])
s += text(XL - 10, YB + 18, [("v", "BL")], anchor="end")
s += text(XM, YB + 52, [("v", "BM")], anchor="middle")
s += text(XR + 10, YB + 18, [("v", "BR")])
# state-variable references
s += ttext(XM - 14, 160, [("n", "+")], anchor="end", color=BLUE)
s += ttext(XM - 14, 202, [("v", "v"), ("vsub", "C"), ("sub", "1")], anchor="end", color=BLUE)
s += ttext(XM - 14, 250, [("n", "−")], anchor="end", color=BLUE)
s += ttext(XR + 20, 160, [("n", "+")], color=BLUE)
s += ttext(XR + 20, 202, [("v", "v"), ("vsub", "C"), ("sub", "2")], color=BLUE)
s += ttext(XR + 20, 250, [("n", "−")], color=BLUE)
s += ttext(XM - 14, 350, [("n", "+")], anchor="end", color=BLUE)
s += ttext(XM - 14, 392, [("v", "v"), ("vsub", "C"), ("sub", "3")], anchor="end", color=BLUE)
s += ttext(XM - 14, 440, [("n", "−")], anchor="end", color=BLUE)
s += ttext(XL + 30, 164, [("v", "i"), ("vsub", "L"), ("sub", "1")], color=RED)
s += ttext(225, YM - 26, [("v", "i"), ("vsub", "L"), ("sub", "2")], anchor="middle", color=RED)
s += ttext(455, YM - 26, [("v", "i"), ("vsub", "L"), ("sub", "3")], anchor="middle", color=RED)
s += footer()
write('EE-106-01-2-nodes.svg', s)
