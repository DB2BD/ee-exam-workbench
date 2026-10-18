"""EE-112-01-1: bridge after the T-L-R delta is replaced by its wye (centre node N); I_s as a symbol only."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 620, 400
XS, YT, YB = 80, 60, 335
T, N, L, R, B = (330, YT), (330, 150), (230, 240), (430, 240), (330, YB)
s = header(W, H)
s += vsrc(XS, YT, XS, YB)
s += line(XS, YT, 140, YT) + resistor(140, YT, 240, YT) + line(240, YT, T[0], T[1])
s += resistor(*T, *N, zigs=6, lead=18)
s += resistor(*N, *L, zigs=6, lead=24, amp=4.5) + resistor(*N, *R, zigs=6, lead=24, amp=4.5)
s += resistor(*L, *B, zigs=6, lead=24, amp=4.5) + resistor(*R, *B, zigs=6, lead=24, amp=4.5)
s += line(XS, YB, B[0], B[1])
for P in (T, N, L, R, B):
    s += dot(*P)
s += tint_arrow(250, YT - 14, 290, YT - 14)
s += end_group()
s += ttext(XS + 24, 196, [("v", "V"), ("vsub", "s"), ("n", " = 120 V")], color=BLUE)
s += text(190, YT - 16, [("n", "5 kΩ")], anchor="middle")
s += ttext(270, YT - 24, [("v", "I"), ("vsub", "s")], anchor="middle", color=RED)
s += text(T[0], T[1] - 12, [("v", "T")], anchor="middle")
s += text(N[0] + 12, N[1] - 2, [("v", "N")])
s += text(L[0] - 12, L[1] + 5, [("v", "L")], anchor="end")
s += text(R[0] + 12, R[1] + 5, [("v", "R")])
s += text(B[0] + 14, B[1] + 20, [("v", "B")])
s += text(T[0] + 16, 110, [("v", "R"), ("vsub", "T"), ("n", " = 3 kΩ")])
s += text(262, 186, [("v", "R"), ("vsub", "L"), ("n", " = 2 kΩ")], anchor="end")
s += text(398, 186, [("v", "R"), ("vsub", "R"), ("n", " = 6 kΩ")])
s += text(268, 300, [("n", "4 kΩ")], anchor="end")
s += text(392, 300, [("n", "6 kΩ")])
s += text(20, 388, [("t", "原 Δ（"), ("v", "T"), ("t", "–"), ("v", "L"), ("t", " 6 kΩ、"), ("v", "T"), ("t", "–"), ("v", "R"), ("t", " 18 kΩ、"),
                    ("v", "L"), ("t", "–"), ("v", "R"), ("t", " 12 kΩ）已換成 Y")])
s += footer()
write('EE-112-01-1-wye.svg', s)
