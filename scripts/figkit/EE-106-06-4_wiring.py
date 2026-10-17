import sys, math, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
DOT = "̇"
W, H = 720, 520; s = header(W, H); lab = ''
ph = {"A": 70, "B": 100, "C": 130}
cx1, cx2, r = 335, 385, 42; cy = 100
def xin(xc, y, side):  # where a phase line meets a transformer circle
    d = math.sqrt(r * r - (y - cy) ** 2); return xc - d if side < 0 else xc + d
for p, y in ph.items():
    s += line(40, y, xin(cx1, y, -1), y) + line(xin(cx2, y, 1), y, 680, y)
    lab += text(30, y + 5, [("n", p)], anchor="end") + text(690, y + 5, [("n", p)])
s += f'<circle cx="{cx1}" cy="{cy}" r="{r}"/>\n<circle cx="{cx2}" cy="{cy}" r="{r}"/>\n'
s += line(318, 96, 318, 112) + line(318, 96, 308, 86) + line(318, 96, 328, 86)          # Y glyph
s += f'<path d="M402 86 L412 108 L392 108 Z"/>\n'                                    # delta glyph
lab += text(360, 30, [("n", "30 MVA，11.4/69 kV，Y–Δ")], anchor="middle")
lab += text(60, 52, [("n", "11.4 kV（Y 側）")]) + text(660, 52, [("n", "69 kV（Δ 側）")], anchor="end")
rows = {"A": 290, "B": 360, "C": 430}
ct1 = {"A": 200, "B": 170, "C": 140}; ct2 = {"A": 520, "B": 550, "C": 580}
yb1, yb2 = 175, 220
for side, ct, bx in ((1, ct1, 125), (2, ct2, 505)):
    s += f'<rect x="{bx}" y="{yb1}" width="90" height="{yb2 - yb1}"/>\n'
    for p, x in ct.items():
        y = ph[p]
        s += f'<circle cx="{x}" cy="{y}" r="8"/>\n' + line(x, y + 8, x, yb1) + line(x, yb2, x, rows[p])
        pd = x + 11 if side == 1 else x - 11
        s += f'<circle cx="{pd}" cy="{y - 11}" r="2.6" fill="#000" stroke="none"/>\n'
s += f'<path d="M158 210 L182 210 L170 188 Z"/>\n'                                    # CT1 delta glyph
s += line(550, 198, 550, 212) + line(550, 198, 540, 186) + line(550, 198, 560, 186)    # CT2 Y glyph
lab += text(118, 202, [("t", "二次 Δ")], anchor="end") + text(498, 202, [("t", "二次 Y")], anchor="end")
lab += text(118, 160, [("n", "CT"), ("sub", "1")], anchor="end") + text(600, 160, [("n", "CT"), ("sub", "2")])
# neutral of CT2 Y, grounded, and OP return
s += line(595, 198, 650, 198) + dot(650, 198) + line(650, 198, 676, 198) + line(676, 198, 676, 210) + ground(676, 210)
lab += text(650, 188, [("n", "N")], anchor="middle")
xr = 470
for p, y in rows.items():
    xl, xrgt = ct1[p], ct2[p]
    s += line(xl, y, 270, y) + coil(270, y, 330, y, turns=3) + line(330, y, 390, y) + coil(390, y, 450, y, turns=3) + line(450, y, xrgt, y)
    s += dot(xl, y) * 0 + dot(360, y) + coil(360, y, 360, y + 44, turns=3, r=5) + line(360, y + 44, xr, y + 44) + dot(xr, y + 44)
    lab += text(300, y - 12, [("v", "R"), ("sub", "1")], anchor="middle") + text(420, y - 12, [("v", "R"), ("sub", "2")], anchor="middle")
    lab += text(360, y - 12, [("n", f"87{p}")], anchor="middle") + text(352, y + 28, [("n", "OP")], anchor="end")
s += line(xr, rows["A"] + 44, xr, rows["C"] + 44) + line(xr, rows["C"] + 44, xr, 490) + line(xr, 490, 650, 490) + line(650, 490, 650, 198)
ya = rows["A"]
s += arrow(222, ya, 258, ya, RED) + arrow(462, ya, 498, ya, RED)
s += end_group() + lab
s += ctext(RED, 240, ya + 22, [("v", "I" + DOT), ("n", "′"), ("sub", "1")], anchor="middle")
s += ctext(RED, 480, ya - 10, [("v", "I" + DOT), ("n", "′"), ("sub", "2")], anchor="middle")
s += text(360, 512, [("t", "● 為 CT 極性端；正常負載或區外故障 "), ("v", "I" + DOT), ("n", "′"), ("sub", "1"), ("n", " = "), ("v", "I" + DOT), ("n", "′"), ("sub", "2"), ("t", "，OP 無電流")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-106-06-4-wiring.svg'), 'w').write(s)
print(len(s))
