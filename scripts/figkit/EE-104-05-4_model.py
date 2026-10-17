import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 340
YT, YU, YR = 130, 60, 290           # bus row, upper line 1-3, reference
X1, X2, X3 = 220, 340, 460
XS1, XS3 = 60, 620
s = header(W, H)
s += coil(X1, YT, X2, YT, turns=4) + coil(X2, YT, X3, YT, turns=4)                      # 1-2, 2-3
s += line(X1, YT, X1, YU) + coil(X1, YU, X3, YU, turns=5) + line(X3, YU, X3, YT)        # 1-3
s += line(X1, YT, 190, YT) + coil(190, YT, 90, YT, turns=4) + line(90, YT, XS1, YT)     # source impedance j0.4
s += line(X3, YT, 490, YT) + coil(490, YT, 590, YT, turns=4) + line(590, YT, XS3, YT)   # j0.5
for X in (XS1, XS3):
    s += line(X, YT, X, 196) + ac_source(X, 210) + line(X, 224, X, YR)
s += line(XS1, YR, XS3, YR) + line(200, YR, 200, YR + 4) + ground(200, YR + 4)
s += line(X2, YT, X2, 200) + f'<circle cx="{X2}" cy="204" r="4"/>\n'                     # load terminal (open)
s += line(X2, YR, X2, 254) + f'<circle cx="{X2}" cy="250" r="4"/>\n'
for X in (X1, X2, X3): s += dot(X, YT)
s += end_group()
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
for X, n in ((X1, "1"), (X2, "2"), (X3, "3")):
    s += lab(X + (0 if n == "2" else 0), YT + (-14 if n == "2" else 26), [("n", "Bus " + n)]) if n == "2" else ""
s += lab(X1 - 6, YT + 26, [("n", "Bus 1")], "end") + lab(X3 + 6, YT + 26, [("n", "Bus 3")], "start")
s += lab(280, YT + 26, [("v", "j"), ("n", "0.1")]) + lab(400, YT + 26, [("v", "j"), ("n", "0.2")])
s += lab(340, YU - 14, [("v", "j"), ("n", "0.25")])
s += lab(140, YT - 14, [("v", "j"), ("n", "0.4")]) + lab(540, YT - 14, [("v", "j"), ("n", "0.5")])
s += ctext(BLUE, XS1 + 22, 216, [("v", "E"), ("n", " = 1.25∠0°")])
s += ctext(BLUE, XS3 - 22, 216, [("v", "E"), ("n", " = 1.25∠0°")], anchor="end")
s += lab(X2 + 12, 232, [("t", "負載接點")], "start")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-4-model.svg'), 'w').write(s)
print(len(s))
