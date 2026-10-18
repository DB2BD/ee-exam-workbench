import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Fault-on positive-sequence reactance network: E' -- j0.40 -- bus 1 -- j0.10 -- V; bus 1 -- Z_f = j0.01 -- reference.
W, H = 640, 300
YT, YB = 70, 240
XE, X1, XV = 70, 300, 570
s = header(W, H)
s += line(XE, YT, XE, 141) + ac_source(XE, 155) + line(XE, 169, XE, YB)
s += coil(XE, YT, X1, YT, turns=5)
s += coil(X1, YT, XV, YT, turns=5)
s += line(XV, YT, XV, 141) + ac_source(XV, 155) + line(XV, 169, XV, YB)
s += f'<path d="M{X1} {YT} L{X1} 115" stroke="{RED}"/>\n'
s += f'<g stroke="{RED}">' + coil(X1, 115, X1, 185, turns=3) + '</g>\n'
s += f'<path d="M{X1} 185 L{X1} {YB}" stroke="{RED}"/>\n'
s += line(XE, YB, XV, YB) + dot(X1, YT) + dot(X1, YB)
s += line(X1, YB, X1, YB + 8) + ground(X1, YB + 8)
s += end_group()
s += text((XE + X1) / 2, YT - 16, [("v", "j"), ("n", "0.40")], anchor="middle")
s += text((XE + X1) / 2, YT + 30, [("t", "（"), ("v", "X"), ("vsub", "d"), ("n", "′ + "), ("v", "X"), ("vsub", "t"), ("t", "）")], anchor="middle")
s += text((X1 + XV) / 2, YT - 16, [("v", "j"), ("n", "0.10")], anchor="middle")
s += text((X1 + XV) / 2, YT + 30, [("t", "（"), ("v", "X"), ("vsub", "L"), ("sub", "1"), ("n", " ∥ "), ("v", "X"), ("vsub", "L"), ("sub", "2"), ("t", "）")], anchor="middle")
s += text(X1 - 8, YT - 10, [("n", "1 (F)")], anchor="end")
s += text(X1 + 24, 156, [("v", "Z"), ("vsub", "f"), ("n", " = "), ("v", "j"), ("n", "0.01")], color=RED)
s += text(X1 + 24, 176, [("t", "三相故障")], color=RED)
s += text(XE + 20, 160, [("v", "E"), ("n", "′∠"), ("v", "δ")], color=BLUE)
s += text(XV - 20, 160, [("v", "V"), ("n", " = 1∠0°")], anchor="end", color=BLUE)
s += text(W / 2, 290, [("t", "故障期間（標么值，共同基準）")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-112-05-4-fault-network.svg')
out.write_text(s)
print(len(s))
