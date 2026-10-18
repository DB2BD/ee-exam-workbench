"""EE-114-06-2 per-unit reactance diagram on S_b = 25 MVA (resistance neglected).

E = 1∠0° — X_s — X_L — X_MTr — main-transformer secondary bus — X_FTr — X_F — electrode.
Electrode short: path closed to the return line with the whole X_F = 0.4 retained (conditional main model);
arc broken: path open, I = 0. I_sc reference direction: source -> furnace. V_2 = bus node to return line.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 320; s = header(W, H); lab = ''
yt, yb, xs, xbus, xe = 90, 240, 50, 380, 600
# source
s += line(xs, yb, xs, 179) + ac_source(xs, 165) + line(xs, 151, xs, yt)
# upstream reactances
segs = [(100, 150, "s", "0.0125"), (190, 240, "L", "0.01"), (280, 330, "MTr", "0.06"),
        (420, 470, "FTr", "0.05"), (520, 570, "F", "0.4")]
x = xs
for a, b, name, val in segs:
    s += line(x, yt, a, yt) + coil(a, yt, b, yt, turns=4, r=6)
    lab += text((a + b) / 2, yt - 36, [("v", "X"), ("vsub", name)], anchor="middle")
    lab += text((a + b) / 2, yt - 16, [("n", val)], anchor="middle")
    x = b
s += line(x, yt, xe, yt)
s += f'<path d="M{xbus} {yt - 22} L{xbus} {yt + 22}" stroke-width="5"/>\n' + dot(xbus, yt)
# electrode: switch from top wire down to the return line (drawn closed = electrode short)
s += line(xe, yt, xe, 140) + f'<circle cx="{xe}" cy="143" r="3" fill="#fff"/>\n' + f'<circle cx="{xe}" cy="187" r="3" fill="#fff"/>\n'
s += line(xe - 3, 146, xe - 3, 184) + line(xe, 190, xe, yb)
# return line
s += line(xs, yb, xe, yb) + dot(xbus, yb)
# brackets for X_u and X_d
for a, b in ((100, 330), (420, 570)):
    s += f'<path d="M{a} {yt + 14} L{a} {yt + 20} L{b} {yt + 20} L{b} {yt + 14}" stroke-width="1"/>\n'
# current reference arrow (red)
s += arrow(60, yt + 14, 92, yt + 14, RED)
s += end_group()
lab += text(215, yt + 40, [("v", "X"), ("vsub", "u"), ("n", " = 0.0825")], anchor="middle")
lab += text(495, yt + 40, [("v", "X"), ("vsub", "d"), ("n", " = 0.45")], anchor="middle")
lab += text(xbus, yt - 62, [("t", "二次側母線")], anchor="middle")
lab += text(xs + 22, 160, [("v", "E")]) + text(xs + 22, 182, [("n", "1∠0°")])
lab += text(xe - 10, 170, [("t", "電極")], anchor="end")
lab += text(xe + 10, 150, [("t", "短路：閉合")]) + text(xe + 10, 172, [("t", "斷弧：開路")])
lab += ctext(BLUE, xbus + 10, 140, [("n", "+")]) + ctext(BLUE, xbus + 10, yb - 8, [("n", "−")])
lab += ctext(BLUE, xbus + 10, 190, [("v", "V"), ("sub", "2")])
lab += ctext(RED, 76, yt + 36, [("v", "I"), ("vsub", "sc")], anchor="middle")
lab += text(W / 2, 290, [("t", "標么電抗（"), ("v", "S"), ("vsub", "b"), ("n", " = 25 MVA"), ("t", "，電阻忽略）；"), ("v", "V"), ("sub", "2"), ("t", " 取母線對回路線")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-114-06-2-reactance.svg'), 'w').write(s)
print(len(s))
