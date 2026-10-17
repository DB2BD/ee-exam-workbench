import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 680, 440
root = (40, 200)
xa, xs = 230, 450
rows = [("A", "甲", 75, "50/163", "0.75"), ("B", "乙", 200, "53/163", "0.72"), ("C", "丙", 325, "60/163", "0.70")]
s = header(W, H)
for ev, who, y, *_ in rows:
    s += line(root[0], root[1], xa, y)                                     # whose bullet
    s += f'<path d="M{xa} {y} L{xs} {y - 32}" stroke="{BLUE}"/>\n'     # hit branch
    s += line(xa, y, xs, y + 32)                                      # miss branch
s += end_group()
s += dot(*root)
for ev, who, y, pw, ph in rows:
    s += dot(xa, y)
    s += text(xa, y + 26, [("v", ev), ("t", "（" + who + "）")], anchor="middle")
    s += dot(xs, y - 32) + dot(xs, y + 32)
    s += ctext(xs + 10, y - 27, [("v", "H")])
    s += text_sup(xs + 10, y + 37, [("v", "H")], [("v", "c")])
    s += ctext(xa + 112, y - 34, [("v", "p"), ("vsub", ev), ("n", " = " + ph)], anchor="middle")
    s += ctext(xs + 36, y - 27, [("n", "→ "), ("v", "P"), ("n", "("), ("v", "H"), ("n", " ∩ "), ("v", ev), ("n", ") = "), ("v", "n"), ("vsub", ev), ("n", " "), ("v", "p"), ("vsub", ev), ("n", " / "), ("v", "N")])
s += text(140, 118, [("v", "P"), ("n", "("), ("v", "A"), ("n", ") = 50/163")], anchor="end")
s += text(135, 192, [("v", "P"), ("n", "("), ("v", "B"), ("n", ") = 53/163")], anchor="middle")
s += text(140, 296, [("v", "P"), ("n", "("), ("v", "C"), ("n", ") = 60/163")], anchor="end")
s += ctext(W / 2, 392, [("t", "（一）"), ("v", "P"), ("n", "("), ("v", "H"), ("n", ") = "), ("t", "三條藍色路徑相加")], anchor="middle")
s += ctext(W / 2, 420, [("t", "（二）"), ("v", "P"), ("n", "("), ("v", "B"), ("n", " | "), ("v", "H"), ("n", ") = "), ("v", "P"), ("n", "("), ("v", "H"), ("n", " ∩ "), ("v", "B"), ("n", ") / "), ("v", "P"), ("n", "("), ("v", "H"), ("n", ")")], anchor="middle")
s += footer()
write('EE-112-03-3-tree.svg', s)
