"""EE-104-01-3: a-phase (per-phase) equivalent of the balanced Y-Y system with two parallel Y loads."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 620, 330
XS, X1, X2 = 180, 350, 500
YT, YB = 80, 280
s = header(W, H)
s += vsrc(XS, YT, XS, YB, r=18)
s += line(XS, YT, X2, YT) + line(XS, YB, X2, YB)
s += line(X1, YT, X1, 120) + resistor(X1, 120, X1, 180, lead=6) + coil(X1, 180, X1, 240) + line(X1, 240, X1, YB)
s += line(X2, YT, X2, 140) + '<rect x="484" y="140" width="32" height="80"/>\n' + line(X2, 220, X2, YB)
for p in ((X1, YT), (X1, YB)):
    s += dot(*p)
s += tint_arrow(240, YT - 16, 290, YT - 16)       # I_a
s += tint_arrow(X1 - 20, 122, X1 - 20, 168)       # I_1
s += tint_arrow(X2 - 30, 142, X2 - 30, 188)       # I_2
s += end_group()
s += text(20, 30, [("v", "a"), ("t", " 相（單相）等效：中性點 "), ("v", "n"), ("t", " 為參考，兩負載並聯於 "), ("v", "V"), ("vsub", "an")])
s += text(XS, YT - 10, [("v", "a")], anchor="middle") + text(XS, YB + 24, [("v", "n")], anchor="middle")
s += ttext(XS - 26, 176, [("v", "V"), ("vsub", "an")], anchor="end", color=BLUE)
s += ttext(XS - 26, 198, [("n", "= 120∠20° V")], anchor="end", color=BLUE)
s += text(X1 + 16, 156, [("n", "8 Ω")]) + text(X1 + 16, 216, [("v", "j"), ("n", "6 Ω")])
s += text(X1 + 16, 262, [("v", "Z"), ("sub", "1")])
s += text(X2 + 26, 176, [("v", "S"), ("sub", "2"), ("vsub", "ϕ")]) + text(X2 + 26, 198, [("n", "= 600∠36° VA")])
s += ttext(265, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle", color=RED)
s += ttext(X1 - 26, 152, [("v", "I"), ("sub", "1")], anchor="end", color=RED)
s += ttext(X2 - 36, 172, [("v", "I"), ("sub", "2")], anchor="end", color=RED)
s += footer()
write('EE-104-01-3-per-phase.svg', s)
