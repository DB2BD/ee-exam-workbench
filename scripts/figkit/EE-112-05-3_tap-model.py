import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Off-nominal tap branch model: bus i -- ideal a:1 (tap at bus i side) -- node V_i/a -- series y -- bus k.
# Reference directions: I_i injected at bus i into the branch, I through y from the tap node to bus k,
# I_k injected at bus k into the branch (= -I).
W, H = 640, 250
YL = 110
XI, XT, XN, XK = 70, 200, 300, 560
s = header(W, H)
s += f'<path d="M{XI} {YL - 45} L{XI} {YL + 45}" stroke-width="5"/>\n'          # bus i
s += f'<path d="M{XK} {YL - 45} L{XK} {YL + 45}" stroke-width="5"/>\n'          # bus k
s += line(XI, YL, XT - 32, YL)
s += f'<circle cx="{XT - 12}" cy="{YL}" r="20"/>\n<circle cx="{XT + 12}" cy="{YL}" r="20"/>\n'   # ideal transformer
s += line(XT + 32, YL, XN, YL) + dot(XN, YL)
s += coil(XN, YL, 470, YL, turns=5) + line(470, YL, XK, YL)
s += arrow(XI + 14, YL - 20, XI + 74, YL - 20, color=RED)
s += arrow(XN + 26, YL - 26, XN + 96, YL - 26, color=RED)
s += arrow(XK - 14, YL - 20, XK - 74, YL - 20, color=RED)
s += end_group()
s += text(XI, YL - 55, [("t", "Bus "), ("v", "i")], anchor="middle")
s += text(XK, YL - 55, [("t", "Bus "), ("v", "k")], anchor="middle")
s += text(XI - 10, YL + 6, [("v", "V"), ("vsub", "i")], anchor="end", color=BLUE)
s += text(XK + 10, YL + 6, [("v", "V"), ("vsub", "k")], anchor="start", color=BLUE)
s += text(XN, YL + 28, [("v", "V"), ("vsub", "i"), ("n", " / "), ("v", "a")], anchor="middle", color=BLUE)
s += text(XI + 44, YL - 28, [("v", "I"), ("vsub", "i")], anchor="middle", color=RED)
s += text(XN + 61, YL - 34, [("v", "I")], anchor="middle", color=RED)
s += text(XK - 44, YL - 28, [("v", "I"), ("vsub", "k")], anchor="middle", color=RED)
s += text(XT, YL + 44, [("v", "a"), ("n", " : 1")], anchor="middle")
s += text(XT, YL + 64, [("t", "理想變壓器")], anchor="middle")
s += text(XT, YL - 32, [("t", "抽頭側")], anchor="middle")
s += text(415, YL + 34, [("v", "y"), ("n", " = 1 / ("), ("v", "jX"), ("n", ")")], anchor="middle")
s += text(W / 2, 222, [("t", "T1："), ("v", "a"), ("n", " = 0.8"), ("t", "，"), ("v", "i"), ("n", " = 1"), ("t", "，"), ("v", "k"), ("n", " = 3"),
                       ("t", "；T2："), ("v", "a"), ("n", " = 1.25"), ("t", "，"), ("v", "i"), ("n", " = 4"), ("t", "，"), ("v", "k"), ("n", " = 2")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-112-05-3-tap-model.svg')
out.write_text(s)
print(len(s))
