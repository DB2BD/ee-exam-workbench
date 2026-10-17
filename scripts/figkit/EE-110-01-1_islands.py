"""EE-110-01-1: as-drawn topology — right half (L2, 2 ohm) joined to the left only through the 2 F capacitor."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB, YC = 680, 330, 120, 280, 66
XS, XR1, XL1, XL2, XR2 = 90, 190, 290, 410, 520
s = header(W, H)
s += f'<rect x="{XL2 - 18}" y="{YT - 18}" width="{XR2 - XL2 + 110}" height="{YB - YT + 34}" fill="{FILL_BLUE}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += isrc(XS, YB, XS, YT)
s += line(XS, YT, XL1, YT) + line(XS, YB, XL1, YB)
s += resistor(XR1, YT, XR1, YB, zigs=6, lead=45)
s += line(XL1, YT, XL1, 150) + coil(XL1, 150, XL1, 250, turns=4) + line(XL1, 250, XL1, YB)
s += line(XL1, YT, XL1, YC) + line(XL1, YC, 330, YC) + cap(330, YC, 370, YC) + line(370, YC, XL2, YC) + line(XL2, YC, XL2, YT)
s += line(XL2, YT, XR2, YT) + line(XL2, YB, XR2, YB)
s += line(XL2, YT, XL2, 150) + coil(XL2, 250, XL2, 150, turns=4) + line(XL2, 250, XL2, YB)
s += resistor(XR2, YT, XR2, YB, zigs=6, lead=45)
for x in (XR1, XL1):
    s += dot(x, YT) + dot(x, YB)
s += dot(XL2, YT)
s += '<circle cx="278" cy="140" r="3.6" fill="#000" stroke="none"/>\n'   # L1 dot: top
s += '<circle cx="424" cy="260" r="3.6" fill="#000" stroke="none"/>\n'   # L2 dot: bottom
s += tint_arrow(XL1 - 18, 180, XL1 - 18, 222)                             # I_a down through L1
s += tint_arrow(XR2 + 18, 180, XR2 + 18, 222)                             # I_b down through 2 ohm
s += tint_arrow(XL2 + 18, 222, XL2 + 18, 180)                             # I_b up through L2
s += end_group()
s += text(20, 28, [("t", "依官方圖：左、右下導線斷開；淡藍區（右半）只經電容一條線與外界相連")])
s += text(XS - 22, 196, [("v", "i"), ("vsub", "s")], anchor="end")
s += text(XS - 22, 218, [("n", "10 cos "), ("v", "t"), ("n", " A")], anchor="end")
s += text(XR1 - 14, 205, [("n", "1 Ω")], anchor="end")
s += ttext(XR1 + 14, 150, [("n", "+")], color=BLUE) + ttext(XR1 + 14, 205, [("v", "v"), ("sub", "1")], color=BLUE)
s += ttext(XR1 + 14, 262, [("n", "−")], color=BLUE)
s += text(XL1 + 16, 205, [("n", "3 H")])
s += text(XL2 - 16, 205, [("n", "1 H")], anchor="end")
s += text(350, 132, [("v", "M"), ("n", " = 1 H")], anchor="middle")
s += text(350, YC - 22, [("n", "2 F")], anchor="middle")
s += ttext(350, YC + 32, [("v", "I"), ("vsub", "C"), ("n", " = 0")], anchor="middle", color=RED)
s += text(XR2 - 14, 205, [("n", "2 Ω")], anchor="end")
s += ttext(XR2 + 48, 150, [("n", "+")], color=BLUE) + ttext(XR2 + 48, 262, [("n", "−")], color=BLUE)
s += ttext(XR2 + 48, 205, [("v", "v"), ("sub", "2")], color=BLUE)
s += ttext(XL1 - 26, 205, [("v", "I"), ("vsub", "a")], anchor="end", color=RED)
s += ttext(XR2 + 26, 182, [("v", "I"), ("vsub", "b")], color=RED)
s += ttext(XL2 + 26, 194, [("v", "I"), ("vsub", "b")], color=RED)
s += footer()
write('EE-110-01-1-islands.svg', s)
