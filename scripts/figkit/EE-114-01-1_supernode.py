"""EE-114-01-1: circuit with the supernode boundary (v1, v2, v3 joined by the two voltage sources)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YN, YTOP, YB = 640, 380, 170, 70, 320
X1, X2, X3 = 150, 330, 510
s = header(W, H)
s += (f'<ellipse cx="{X2}" cy="122" rx="250" ry="90" fill="{FILL_BLUE}" stroke="{BLUE}" '
      f'stroke-dasharray="6 4"/>\n')
s += line(X1, YN, X1, YTOP) + line(X1, YTOP, 270, YTOP) + resistor(270, YTOP, 390, YTOP) + line(390, YTOP, X3, YTOP) + line(X3, YTOP, X3, YN)
s += vsrc(X1, YN, X2, YN)                  # 25 V: + at v1, - at v2
s += dep_vsrc(X3, YN, X2, YN)              # 5I: + at v3, - at v2
for x in (X1, X2, X3):
    s += resistor(x, YN, x, YB, zigs=6, lead=45) + dot(x, YN)
s += line(X1, YB, X3, YB) + dot(X2, YB) + line(X2, YB, X2, YB + 12) + ground(X2, YB + 12)
for x in (X1, X2, X3):
    s += tint_arrow(x - 16, 228, x - 16, 266)
s += end_group()
s += ttext(20, 28, [("t", "超節點（虛線內）：兩個電壓源把 "), ("v", "v"), ("sub", "1"), ("n", ", "), ("v", "v"), ("sub", "2"),
                    ("n", ", "), ("v", "v"), ("sub", "3"), ("t", " 連成一體；6 Ω 為內部支路")], color=BLUE)
s += text(X1 + 10, YN - 10, [("v", "v"), ("sub", "1")])
s += text(X2 + 10, YN + 24, [("v", "v"), ("sub", "2")])
s += text(X3 - 10, YN - 10, [("v", "v"), ("sub", "3")], anchor="end")
s += text(X2, YTOP - 14, [("n", "6 Ω")], anchor="middle")
s += text(240, YN - 24, [("n", "25 V")], anchor="middle")
s += text(420, YN - 26, [("n", "5"), ("v", "I")], anchor="middle")
for x, r in ((X1, "2 Ω"), (X2, "4 Ω"), (X3, "3 Ω")):
    s += text(x + 18, 252, [("n", r)])
s += ttext(X1 - 24, 252, [("v", "I"), ("n", " = "), ("v", "v"), ("sub", "1"), ("n", "/2")], anchor="end", color=RED)
s += ttext(X2 - 24, 252, [("v", "v"), ("sub", "2"), ("n", "/4")], anchor="end", color=RED)
s += ttext(X3 - 24, 252, [("v", "v"), ("sub", "3"), ("n", "/3")], anchor="end", color=RED)
s += footer()
write('EE-114-01-1-supernode.svg', s)
