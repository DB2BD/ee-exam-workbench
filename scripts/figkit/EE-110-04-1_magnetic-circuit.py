"""EE-110-04-1 fig 1: (left) winding sense read from the crop, front side = out of the page:
N1 front strokes carry I to the right -> flux up the left leg; N2 front strokes carry I to the left ->
flux down the right leg; both drive the same clockwise flux Phi along the mean path l_c.
(right) magnetic equivalent circuit: N1 I and N2 I aiding in series with R_c."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 700, 340
s = header(W, H)
# --- left panel: core ---
s += '<rect x="40" y="50" width="250" height="220"/>\n<rect x="95" y="105" width="140" height="110"/>\n'
s += '<rect x="67.5" y="77.5" width="195" height="165" stroke-dasharray="5 4" stroke-width="1"/>\n'
for y in (130, 152, 174, 196):
    s += line(34, y, 101, y) + line(229, y, 296, y)
    s += arrow(46, y - 6, 74, y - 6, color=RED) + arrow(284, y - 6, 256, y - 6, color=RED)
s += arrow(145, 77.5, 185, 77.5) + arrow(185, 242.5, 145, 242.5)
s += arrow(67.5, 112, 67.5, 92) + arrow(262.5, 92, 262.5, 112)
# --- right panel: magnetic equivalent circuit ---
XL, XR, YT, YB = 430, 620, 90, 240
s += vsrc(XL, YT, XL, YB, r=22)                      # + at top
s += vsrc(XR, YB, XR, YT, r=22)                      # + at bottom: pushes Phi downward on the right
s += line(XL, YT, 490, YT) + resistor(480, YT, 570, YT) + line(570, YT, XR, YT)
s += line(XL, YB, XR, YB)
s += arrow(495, YT - 18, 555, YT - 18)
s += end_group()
s += text(118, 160, [("v", "N"), ("sub", "1")]) + text(212, 160, [("v", "N"), ("sub", "2")], anchor="end")
s += text(165, 70, [("n", "Φ")], anchor="middle")
s += text(298, 72, [("v", "l"), ("vsub", "c"), ("t", "（虛線）")])
s += ttext(165, 296, [("t", "前側電流："), ("v", "N"), ("sub", "1"), ("t", " 向右、"), ("v", "N"), ("sub", "2"), ("t", " 向左")], anchor="middle", color=RED)
s += text(165, 322, [("t", "左柱磁通向上、右柱向下 → 同為順時針")], anchor="middle")
s += ttext(XL - 30, 172, [("v", "N"), ("sub", "1"), ("v", "I")], anchor="end", color=BLUE)
s += ttext(XR + 30, 172, [("v", "N"), ("sub", "2"), ("v", "I")], color=BLUE)
s += text(525, YT - 26, [("n", "Φ")], anchor="middle")
s += text(525, YT + 34, [("v", "ℛ"), ("vsub", "c")], anchor="middle")
s += text(525, YB + 50, [("t", "兩磁動勢同向（和動串聯）")], anchor="middle")
s += text(525, YB + 76, [("v", "ℱ"), ("n", " = ("), ("v", "N"), ("sub", "1"), ("n", " + "), ("v", "N"), ("sub", "2"), ("n", ")"), ("v", "I")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-110-04-1-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
