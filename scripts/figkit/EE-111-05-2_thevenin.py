import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 280
YT, YB = 70, 210
s = header(W, H)
# left panel: Thevenin equivalent seen from bus 5, short-circuited
XS, X5 = 60, 260
s += line(XS, YT, XS, 126) + ac_source(XS, 140) + line(XS, 154, XS, YB)
s += line(XS, YT, 100, YT) + coil(100, YT, 210, YT, turns=5) + line(210, YT, X5, YT)
s += line(X5, YT, X5, YB)                     # bolted fault (Zf = 0)
s += line(XS, YB, X5, YB) + dot(X5, YT) + dot(X5, YB)
s += line(160, YB, 160, YB + 10) + ground(160, YB + 10)
s += arrow(X5 + 18, 110, X5 + 18, 165, color=RED)
# right panel: line 2-1
X2, X1, YL = 400, 620, 130
s += busbar(X2, X2, YL)
s += f'<path d="M{X2} {YL - 40} L{X2} {YL + 40}" stroke-width="5"/>\n'
s += f'<path d="M{X1} {YL - 40} L{X1} {YL + 40}" stroke-width="5"/>\n'
s += line(X2, YL, 460, YL) + coil(460, YL, 560, YL, turns=5) + line(560, YL, X1, YL)
s += arrow(470, YL + 26, 550, YL + 26, color=RED)
s += end_group()
s += text(155, YT - 14, [("v", "Z"), ("sub", "55"), ("n", " = "), ("v", "j"), ("n", "0.1301")], anchor="middle")
s += ctext(BLUE, XS + 22, 145, [("n", "1∠0°")])
s += text(X5, YT - 14, [("n", "Bus 5")], anchor="middle")
s += ctext(RED, X5 + 28, 144, [("v", "I"), ("vsub", "f")])
s += text(X5 - 8, 145, [("v", "Z"), ("vsub", "f"), ("n", " = 0")], anchor="end")
s += text(160, YB + 50, [("t", "（a）Bus 5 看入的戴維寧等效")], anchor="middle")
s += text(X2, YL - 50, [("n", "Bus 2")], anchor="middle")
s += text(X1, YL - 50, [("n", "Bus 1")], anchor="middle")
s += text(510, YL - 14, [("v", "j"), ("n", "0.168")], anchor="middle")
s += ctext(RED, 510, YL + 50, [("v", "I"), ("sub", "2→1")], anchor="middle")
s += ctext(BLUE, X2 - 10, YL + 62, [("v", "V"), ("sub", "2")], anchor="middle")
s += ctext(BLUE, X1 + 10, YL + 62, [("v", "V"), ("sub", "1")], anchor="middle")
s += text(510, YB + 50, [("t", "（b）線路 1–2 與電流參考方向")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-111-05-2-thevenin.svg'), 'w').write(s)
print(len(s))
