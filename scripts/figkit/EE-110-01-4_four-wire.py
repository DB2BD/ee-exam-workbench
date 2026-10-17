"""EE-110-01-4: Y-Y four-wire connection; each unbalanced phase impedance sits on its own phase voltage."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 360
XT = 70
YA, YBL, YC, YN = 80, 115, 150, 320
BT, BB = 190, 260                                   # impedance box top/bottom
cols = [("c", YC, 260, "6∠20° Ω"), ("b", YBL, 430, "4∠−50° Ω"), ("a", YA, 600, "8∠30° Ω")]
s = header(W, H)
for ph, y, x, _ in cols:
    s += line(XT, y, x, y) + line(x, y, x, BT)
    s += f'<rect x="{x - 15}" y="{BT}" width="30" height="{BB - BT}"/>\n'
    s += line(x, BB, x, YN) + dot(x, YN)
    s += tint_arrow(x - 12, BT - 34, x - 12, BT - 8)
s += line(XT, YN, 600, YN)
for y in (YA, YBL, YC, YN):
    s += terminal(XT, y)
s += end_group()
s += text(20, 30, [("t", "正相序，"), ("v", "V"), ("vsub", "ab"), ("n", " = 208∠0° V"), ("t", "（有效值）；中性線連接電源與負載中性點")])
for ph, y, x, z in cols:
    s += text(XT - 10, y + 5, [("v", ph)], anchor="end")
    s += ttext(x - 20, BT - 14, [("v", "I"), ("vsub", ph)], anchor="end", color=RED)
    s += ttext(x - 22, BT + 14, [("n", "+")], anchor="end", color=BLUE)
    s += ttext(x - 22, BB, [("n", "−")], anchor="end", color=BLUE)
    s += ttext(x - 22, (BT + BB) // 2 + 6, [("v", "V"), ("vsub", ph + "n")], anchor="end", color=BLUE)
    s += text(x + 22, (BT + BB) // 2 - 4, [("v", "Z"), ("vsub", ph + "n")])
    s += text(x + 22, (BT + BB) // 2 + 18, [("n", z)])
s += text(XT - 10, YN + 5, [("v", "n")], anchor="end")
s += text(330, YN + 26, [("t", "中性線（負載中性點 = 電源中性點 "), ("v", "n"), ("t", "）")], anchor="middle")
s += footer()
write('EE-110-01-4-four-wire.svg', s)
