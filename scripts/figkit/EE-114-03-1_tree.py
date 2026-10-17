import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 680, 420
root = (40, 200)
xa, xs = 230, 450
rows = [(1, 75, "0.70", "0.01", "0.007"), (2, 200, "0.20", "0.02", "0.004"), (3, 325, "0.10", "0.05", "0.005")]
s = header(W, H)
for i, y, *_ in rows:
    s += line(root[0], root[1], xa, y)                      # partition branch
    s += f'<path d="M{xa + 40} {y} L{xs} {y - 32}" stroke="{BLUE}"/>\n'   # spam branch
    s += line(xa + 40, y, xs, y + 32)                       # non-spam branch
s += end_group()
s += dot(*root)
for i, y, pa, ps, prod in rows:
    s += dot(xa, y) + dot(xa + 40, y)
    s += text(xa + 20, y + 5, [("v", "A"), ("sub", str(i))], anchor="middle")
    s += dot(xs, y - 32) + dot(xs, y + 32)
    s += ctext(xs + 10, y - 27, [("v", "S")])
    s += text_sup(xs + 10, y + 37, [("v", "S")], [("v", "c")])
    # P(S|A_i) label above the spam branch
    s += ctext(xa + 128, y - 34, [("v", "P"), ("n", "("), ("v", "S"), ("n", " | "), ("v", "A"), ("sub", str(i)), ("n", ") = " + ps)], anchor="middle")
    # product along the spam path
    s += ctext(xs + 34, y - 27, [("n", "→ "), ("v", "P"), ("n", "("), ("v", "S"), ("n", " ∩ "), ("v", "A"), ("sub", str(i)), ("n", ") = " + prod)])
# partition labels P(A_i)
s += text(140, 118, [("v", "P"), ("n", "("), ("v", "A"), ("sub", "1"), ("n", ") = 0.70")], anchor="end")
s += text(135, 192, [("v", "P"), ("n", "("), ("v", "A"), ("sub", "2"), ("n", ") = 0.20")], anchor="middle")
s += text(140, 296, [("v", "P"), ("n", "("), ("v", "A"), ("sub", "3"), ("n", ") = 0.10")], anchor="end")
s += ctext(W / 2, 395, [("v", "P"), ("n", "("), ("v", "S"), ("n", ") = 0.007 + 0.004 + 0.005 = 0.016"), ("t", "（三條藍色路徑相加）")], anchor="middle")
s += footer()
write('EE-114-03-1-tree.svg', s)
