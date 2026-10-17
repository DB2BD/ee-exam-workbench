import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# Probability tree for (二): first ball colour (partition) -> second ball red or not.
W, H = 680, 440
root = (50, 220)
x1, x2 = 230, 470                    # first-draw nodes, second-draw nodes
rows = [("B", "黑", 100, "2/9", "3/8"), ("R", "紅", 220, "3/9", "2/8"), ("W", "白", 340, "4/9", "3/8")]
s = header(W, H)
for c, _, y, *_ in rows:
    s += line(root[0], root[1], x1, y)                                   # first draw
    s += f'<path d="M{x1 + 62} {y} L{x2} {y - 36}" stroke="{BLUE}"/>\n'   # second red
    s += line(x1 + 62, y, x2, y + 36)                                    # second not red
s += end_group()
s += dot(*root)
s += text(root[0] - 6, root[1] + 24, [("t", "9 球")], anchor="middle")
for c, name, y, p1, p2 in rows:
    s += dot(x1, y) + dot(x1 + 62, y)
    s += text(x1 + 31, y + 5, [("v", c), ("sub", "1")], anchor="middle")
    s += dot(x2, y - 36) + dot(x2, y + 36)
    s += ctext(x2 + 10, y - 31, [("v", "R"), ("sub", "2")])
    s += text_sup(x2 + 10, y + 41, [("v", "R"), ("sub", "2")], [("v", "c")], tail=[("t", "（非紅）")])
    s += ctext(x1 + 170, y - 46, [("v", "P"), ("n", "("), ("v", "R"), ("sub", "2"), ("n", " | "), ("v", c), ("sub", "1"),
                                   ("n", ") = " + p2)], anchor="middle")
# first-draw probabilities on the partition branches
s += text(128, 140, [("v", "P"), ("n", "("), ("v", "B"), ("sub", "1"), ("n", ") = 2/9")], anchor="end")
s += text(140, 210, [("v", "P"), ("n", "("), ("v", "R"), ("sub", "1"), ("n", ") = 3/9")], anchor="middle")
s += text(128, 316, [("v", "P"), ("n", "("), ("v", "W"), ("sub", "1"), ("n", ") = 4/9")], anchor="end")
s += text(x1 - 50, 26, [("t", "第一顆")], anchor="middle")
s += text(x2 - 40, 26, [("t", "第二顆（剩 8 球）")], anchor="middle")
s += ctext(W / 2, 420, [("t", "藍色三條路徑＝第二顆為紅球，各路徑機率相乘後相加")], anchor="middle")
s += footer()
write('EE-105-03-6-tree.svg', s)
