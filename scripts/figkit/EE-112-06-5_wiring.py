"""EE-112-06-5 receiving-panel wiring: PT on the source side of CB, CT x3 on the load side.

PT secondary (V-V, 110 V, wire b grounded): three-wire bus a/b/c; VS->V, 27 and the kW voltage coils
tap all three wires in parallel. CT secondary (Y, common n grounded once): wires a/b/c run in series
through AS (with ammeter A), 50/51 per phase and the kW current coils (a, c), join at the star point
and return through 51N (residual I_a+I_b+I_c) to n. Trip circuit: 50/51, 51N, 27 contacts in parallel
-> 52a -> TC. Red = residual current reference direction (star point -> 51N -> n), symbol only.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def box(x1, y1, x2, y2): return f'<rect x="{x1}" y="{y1}" width="{x2 - x1}" height="{y2 - y1}" fill="#fff"/>\n'
def term(x, y): return f'<circle cx="{x}" cy="{y}" r="3" fill="#fff"/>\n'
def no_contact(x1, y, x2): return line(x1, y, x1 + 14, y) + line(x2 - 14, y, x2, y) + line(x1 + 14, y, x2 - 18, y - 12)
W, H = 720, 650; s = header(W, H); lab = ''
yl = 60
# ---- one-line: bus, PT tap, CB, CT, load ----
s += f'<path d="M40 {yl - 26} L40 {yl + 26}" stroke-width="5"/>\n' + line(40, yl, 300, yl) + box(300, yl - 13, 360, yl + 13)
s += line(360, yl, 680, yl) + arrow(640, yl, 690, yl)
s += dot(150, yl) + line(150, yl, 150, 76) + box(144, 76, 156, 96) + line(150, 96, 150, 104)
s += '<circle cx="150" cy="114" r="10"/>\n<circle cx="150" cy="128" r="10"/>\n'
s += f'<path d="M150 138 L150 150" stroke-width="1" stroke-dasharray="3 3"/>\n'
s += coil(478, yl + 10, 502, yl + 10, turns=2, r=5) + f'<path d="M490 {yl + 16} L490 100" stroke-width="1" stroke-dasharray="3 3"/>\n'
lab += text(330, yl + 6, [("n", "CB")], anchor="middle") + text(166, 92, [("n", "PF")])
lab += text(168, 126, [("n", "PT")]) + text(510, yl + 30, [("n", "CT ×3")]) + text(690, yl - 12, [("t", "負載")], anchor="end")
lab += text(40, 24, [("t", "母線")], anchor="middle")
# ---- PT secondary: terminals c, b, a (x = 110, 150, 190), fuses, 3-wire bus ----
PT = {"c": (110, 260), "b": (150, 235), "a": (190, 210)}
for ph, (x, yb) in PT.items():
    s += term(x, 160) + line(x, 163, x, 168) + box(x - 5, 168, x + 5, 186) + line(x, 186, x, yb) + line(x, yb, 378, yb)
    lab += text(x - 7, 165, [("n", ph)], anchor="end")
s += line(378, 235, 392, 235) + line(392, 235, 392, 276) + ground(392, 276) + dot(378, 235)
lab += text(96, 182, [("t", "熔絲")], anchor="end")
for x0, name in ((210, "VS"), (275, "27"), (340, "kW")):
    for k, ph in enumerate("abc"):
        xx = x0 + 10 + 15 * k; yb = PT[ph][1]
        s += dot(xx, yb) + line(xx, yb, xx, 300)
    s += box(x0, 300, x0 + 50, 330)
    lab += text(x0 + 25, 321, [("n", name)], anchor="middle")
s += line(228, 330, 228, 356) + line(242, 330, 242, 356) + '<circle cx="235" cy="370" r="14"/>\n'
lab += text(235, 376, [("n", "V")], anchor="middle") + text(365, 350, [("t", "電壓線圈")], anchor="middle")
lab += ctext(BLUE, 250, 290, [("t", "PT 二次 110 V：全部並聯")], anchor="middle").replace('y="290"', 'y="400"')
# ---- CT secondary: terminals a, b, c (x = 430, 490, 550) and n (650) ----
CT = {"a": 430, "b": 490, "c": 550}; xn = 650
for ph, x in CT.items():
    s += term(x, 110) + line(x, 113, x, 310)
    lab += text(x - 8, 106, [("n", ph)], anchor="end")
s += term(xn, 110) + line(xn, 113, xn, 420) + dot(xn, 420) + line(xn, 420, xn, 432) + ground(xn, 432)
lab += text(xn + 8, 106, [("n", "n")])
s += box(415, 132, 565, 162) + line(565, 142, 588, 142) + line(565, 152, 588, 152) + '<circle cx="602" cy="147" r="14"/>\n'
lab += text(490, 153, [("n", "AS")], anchor="middle") + text(602, 153, [("n", "A")], anchor="middle")
for ph, x in CT.items():
    s += box(x - 24, 186, x + 24, 216)
    lab += text(x, 207, [("n", "50/51")], anchor="middle")
for ph in ("a", "c"):
    x = CT[ph]; s += box(x - 20, 240, x + 20, 270)
    lab += text(x, 261, [("n", "kW")], anchor="middle")
s += line(430, 310, 550, 310) + dot(430, 310) + dot(490, 310) + dot(550, 310)
s += line(490, 310, 490, 340) + box(466, 340, 514, 370) + line(490, 370, 490, 420) + line(490, 420, xn, 420)
lab += text(490, 361, [("n", "51N")], anchor="middle") + text(575, 261, [("t", "電流線圈")])
s += arrow(474, 378, 474, 412, RED)
lab += ctext(RED, 466, 400, [("v", "I"), ("vsub", "a"), ("n", "+"), ("v", "I"), ("vsub", "b"), ("n", "+"), ("v", "I"), ("vsub", "c")], anchor="end")
lab += ctext(BLUE, 560, 455, [("t", "CT 二次 5 A：全部串聯、"), ("n", "n"), ("t", " 單點接地")], anchor="middle")
# ---- trip circuit ----
yt = 540
s += line(60, yt, 120, yt) + line(120, yt - 40, 120, yt + 40) + line(320, yt - 40, 320, yt + 40)
for k, name in enumerate(("50/51", "51N", "27")):
    y = yt - 40 + 40 * k
    s += line(120, y, 180, y) + no_contact(180, y, 250) + line(250, y, 320, y) + dot(120, y) + dot(320, y)
    lab += text(258, y - 6, [("n", name)])
s += line(320, yt, 360, yt) + no_contact(360, yt, 430) + line(430, yt, 470, yt) + box(470, yt - 15, 530, yt + 15) + line(530, yt, 600, yt)
lab += text(52, yt + 6, [("n", "+")], anchor="end") + text(610, yt + 6, [("n", "−")]) + text(395, yt - 18, [("n", "52a")], anchor="middle")
lab += text(500, yt + 6, [("n", "TC")], anchor="middle") + text(500, yt + 36, [("t", "CB 跳脫線圈")], anchor="middle")
lab += text(220, yt + 66, [("t", "保護電驛接點並聯")], anchor="middle")
s += end_group()
lab += text(W / 2, 636, [("t", "PT 在 CB 電源側、CT 在負載側；51N 接三相 CT 星形點的殘流路徑")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-112-06-5-wiring.svg'), 'w').write(s)
print(len(s))
