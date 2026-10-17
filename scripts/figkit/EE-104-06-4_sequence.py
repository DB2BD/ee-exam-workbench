import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 330; s = header(W, H); y, g = 100, 230
# (a) three-phase fault: positive-sequence network only
xa, xf = 50, 220
s += line(xa, g, xa, 179) + ac_source(xa, 165) + line(xa, 151, xa, y)
s += line(xa, y, 90, y) + coil(90, y, 170, y) + line(170, y, xf, y) + dot(xf, y)
s += f'<path d="M{xf} {y} L{xf} {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n' + line(xa, g, xf, g) + dot(xf, g)
s += arrow(180, y - 10, 212, y - 10, RED)
# (b) single line-to-ground fault: 1, 2, 0 networks in series
xb, xr = 330, 650
s += line(xb, g, xb, 179) + ac_source(xb, 165) + line(xb, 151, xb, y)
s += line(xb, y, 370, y) + coil(370, y, 450, y) + line(450, y, 490, y) + coil(490, y, 570, y) + line(570, y, xr, y)
s += line(xr, y, xr, g) + line(xr, g, 570, g) + coil(570, g, 490, g) + line(490, g, xb, g)
s += arrow(590, y - 10, 630, y - 10, RED)
s += end_group()
s += text(130, 76, [("v", "jX"), ("sub", "1")], anchor="middle") + text(130, 130, [("v", "j"), ("n", "1.1604 Ω")], anchor="middle")
s += text(xa + 22, 170, [("v", "V"), ("vsub", "ϕ")])
s += ctext(RED, 216, 72, [("v", "I"), ("sub", "3"), ("vsub", "ϕ")], anchor="end")
s += text(410, 76, [("v", "jX"), ("sub", "1")], anchor="middle") + text(410, 130, [("v", "j"), ("n", "1.1604 Ω")], anchor="middle")
s += text(530, 76, [("v", "jX"), ("sub", "2")], anchor="middle") + text(530, 130, [("v", "j"), ("n", "1.1604 Ω")], anchor="middle")
s += text(530, 212, [("v", "jX"), ("sub", "0")], anchor="middle") + text(530, 262, [("v", "j"), ("n", "0.9973 Ω")], anchor="middle")
s += text(xb + 22, 170, [("v", "V"), ("vsub", "ϕ"), ("n", " = 13.164 kV")])
s += ctext(RED, 690, 72, [("v", "I"), ("vsub", "a"), ("sub", "0"), ("n", " = 3.9673 kA")], anchor="end")
s += text(135, 296, [("t", "(a) 三相短路：只有正序")], anchor="middle")
s += text(490, 296, [("t", "(b) 單相接地：三序串聯，"), ("v", "I"), ("vsub", "f"), ("n", " = 3"), ("v", "I"), ("vsub", "a"), ("sub", "0")], anchor="middle")
s += text(350, 322, [("v", "S"), ("sub", "3"), ("vsub", "ϕ"), ("n", " = "), ("v", "V"), ("vsub", "LL"), ("n", "²/"), ("v", "X"), ("sub", "1"), ("t", "；"), ("v", "S"), ("sub", "1"), ("vsub", "ϕ"), ("n", " = 3"), ("v", "V"), ("vsub", "LL"), ("n", "²/("), ("v", "X"), ("sub", "1"), ("n", " + "), ("v", "X"), ("sub", "2"), ("n", " + "), ("v", "X"), ("sub", "0"), ("n", ")")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-104-06-4-sequence.svg'), 'w').write(s)
print(len(s))
