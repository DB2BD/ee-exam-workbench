"""EE-108-06-2 per-unit reactance diagram on S_b = 30 MVA (part 一).

E = 1∠0° – jX_S – (measuring point, 69 kV) – jX_L – jX_T1 – (11.4 kV bus) – [jX_R, part 三, dashed] – jX_T2 – jX_F – return.
Values equal the note; X_R is drawn as a symbol only (its value is derived in part 三).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 330; s = header(W, H); lab = ''
yt, yb, xs, xf = 110, 262, 46, 616
s += line(xs, yb, xs, 200) + ac_source(xs, 186) + line(xs, 172, xs, yt)
s += line(xs, yt, 76, yt) + coil(76, yt, 136, yt, turns=3) + line(136, yt, 196, yt)                 # X_S
s += coil(196, yt, 256, yt, turns=3) + line(256, yt, 276, yt) + coil(276, yt, 336, yt, turns=3)     # X_L, X_T1
s += line(336, yt, 386, yt)
s += f'<path d="M386 {yt} L406 {yt}" stroke-dasharray="4 3"/>\n'
s += f'<path transform="translate(406 {yt})" d="M0 0 A6 6 0 0 1 12 0 A6 6 0 0 1 24 0 A6 6 0 0 1 36 0 L36 0" stroke-dasharray="4 3"/>\n'
s += f'<path d="M442 {yt} L462 {yt}" stroke-dasharray="4 3"/>\n'
s += line(462, yt, 476, yt) + coil(476, yt, 536, yt, turns=3) + line(536, yt, xf, yt)              # X_T2
s += line(xf, yt, xf, 160) + coil(xf, 160, xf, 220, turns=3) + line(xf, 220, xf, yb)                # X_F
s += line(xs, yb, xf, yb)
# measuring point (×) and 11.4 kV bus node
s += dot(166, yt) + line(160, yt - 6, 172, yt + 6) + line(160, yt + 6, 172, yt - 6) + dot(361, yt)
s += f'<path d="M166 {yt} L166 {yb}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="3 3"/>\n' + dot(166, yb)
s += end_group()
for x, name, val in ((106, "S", "0.012"), (226, "L", "0.002552"), (306, "T1", "0.07"), (506, "T2", "0.12")):
    sub = [("vsub", "S")] if name in ("S", "L") else [("vsub", "T"), ("sub", name[1])]
    if name == "L":
        sub = [("vsub", "L")]
    lab += text(x, yt - 22, [("v", "jX")] + sub, anchor="middle") + text(x, yt + 30, [("v", "j"), ("n", val)], anchor="middle")
lab += text(424, yt - 22, [("v", "jX"), ("vsub", "R")], anchor="middle") + text(424, yt + 30, [("t", "（三）加裝")], anchor="middle")
lab += text(xf + 14, 186, [("v", "jX"), ("vsub", "F")]) + text(xf + 14, 208, [("v", "j"), ("n", "0.192")])
lab += text(xs + 22, 182, [("v", "E")]) + text(xs + 22, 204, [("n", "1∠0°")])
lab += text(166, 50, [("t", "測定點")], anchor="middle") + text(166, 70, [("n", "69 kV")], anchor="middle")
lab += text(361, 50, [("t", "11.4 kV 母線")], anchor="middle")
lab += ctext(BLUE, 176, 196, [("v", "V"), ("vsub", "M")])
lab += text(W / 2, 306, [("v", "S"), ("vsub", "b"), ("n", " = 30 MVA"), ("t", "；各值為標么電抗，忽略電阻；"), ("v", "V"), ("vsub", "M"), ("t", " 取測定點對回路線")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-108-06-2-reactance.svg'), 'w').write(s)
print(len(s))
