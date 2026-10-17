import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def box(x, y, w, h=52): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
W, H = 700, 300; s = header(W, H)
rows = [(30, "裝置 1–3", "8.10 + 24.90 + 16.25 = 49.25", "1.35", "A", "36.48"),
        (110, "裝置 4–6", "31.50 + 24.00 + 15.00 = 70.50", "1.56", "B", "45.19"),
        (190, "裝置 7–8", "11.20 + 16.25 = 27.45", "1.6", "C", "17.16")]
for y, *_ in rows:
    s += box(20, y, 260) + box(370, y, 120) + arrow(280, y + 26, 368, y + 26) + line(490, y + 26, 530, y + 26)
s += line(530, 56, 530, 216) + arrow(530, 136, 568, 136) + box(570, 110, 115)
s += end_group()
for y, dev, sm, fd, g, val in rows:
    s += text(150, y + 20, [("t", dev), ("t", "　"), ("v", "S"), ("v", "f"), ("vsub", "D")], anchor="middle")
    s += text(150, y + 44, [("n", sm)], anchor="middle")
    s += ctext(BLUE, 324, y + 14, [("n", f"÷ {fd}")], anchor="middle")
    s += text(430, y + 32, [("t", f"{g}："), ("n", val)], anchor="middle")
s += ctext(BLUE, 552, 104, [("n", "÷ 1.25")], anchor="middle")
s += ctext(RED, 627, 132, [("t", "主")], anchor="middle") + ctext(RED, 627, 152, [("n", "79.06")], anchor="middle")
s += text(350, 280, [("t", "單位 kVA：各裝置最大需量 "), ("v", "S"), ("v", "f"), ("vsub", "D"), ("t", " 相加 ÷ 設備間參差因數，再相加 ÷ 變壓器間參差因數")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-110-06-2-demand-tree.svg'), 'w').write(s)
print(len(s))
