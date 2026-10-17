import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def box(x, y, w=150, h=44): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
W, H = 700, 330; s = header(W, H)
dev = [(1, "228"), (2, "127.50"), (3, "200"), (4, "122.50")]
ys = [30, 92, 178, 240]
for (i, p), y in zip(dev, ys):
    s += box(30, y)
s += box(290, 61) + box(290, 209) + box(530, 135, w=150)
# connectors device -> transformer
for y, ty in ((ys[0], 83), (ys[1], 83), (ys[2], 231), (ys[3], 231)):
    s += line(180, y + 22, 230, y + 22) + line(230, y + 22, 230, ty)
s += arrow(230, 83, 288, 83) + arrow(230, 231, 288, 231)
s += line(440, 83, 480, 83) + line(440, 231, 480, 231) + line(480, 83, 480, 231) + arrow(480, 157, 528, 157)
s += end_group()
for (i, p), y in zip(dev, ys):
    s += text(105, y + 28, [("t", f"設備 {i}："), ("n", f"{p} kW")], anchor="middle")
s += text(365, 89, [("t", "A："), ("n", "296.25 kW")], anchor="middle")
s += text(365, 237, [("t", "B："), ("n", "230.36 kW")], anchor="middle")
s += ctext(RED, 605, 163, [("t", "主："), ("n", "457.92 kW")], anchor="middle")
s += ctext(BLUE, 259, 55, [("n", "÷ 1.2")], anchor="middle")
s += ctext(BLUE, 259, 203, [("n", "÷ 1.4")], anchor="middle")
s += ctext(BLUE, 505, 127, [("n", "÷ 1.15")], anchor="middle")
s += text(350, 318, [("t", "尖峰需量逐層相加後除以該層參差因數；平均功率與電能不除參差因數")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-112-06-2-demand-tree.svg'), 'w').write(s)
print(len(s))
