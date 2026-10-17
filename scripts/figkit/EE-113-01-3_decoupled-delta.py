import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-113-01-3_delta_common.py')
_s = importlib.util.spec_from_file_location('dc', _p); dc = importlib.util.module_from_spec(_s); _s.loader.exec_module(dc)
from svgkit import *
A, B, C, at, anchor = dc.A, dc.B, dc.C, dc.at, dc.anchor
W, H, YLC = 640, 380, 345
s = header(W, H)
s += dc.frame(YLC)
for P, Q, _ in dc.BRANCHES:
    s += dc.branch(P, Q)                                # Z_phi = R + j(ωL − ωM): 1 Ω in series with j1 Ω
    s += dc.tint(dc.head(P, Q, 0.47), dc.RED)
s += dc.tint(arrow(190, A[1], 236, A[1]), dc.RED)
s += end_group()
s += dc.labels_terminals(YLC)
s += dc.tint(text(212, A[1] - 12, [("v", "I"), ("vsub", "a")], anchor="middle"), dc.RED)
ZP = [("v", "Z"), ("vsub", "φ")]
for P, Q, nm in dc.BRANCHES:
    x, y, nx = at(P, Q, sum(dc.T_R) / 2, 22); s += text(round(x), round(y + 5), [("n", "1 Ω")], anchor=anchor(nx))
    x, y, nx = at(P, Q, sum(dc.T_L) / 2, 22); s += text(round(x), round(y + 5), [("v", "j"), ("n", "1 Ω")], anchor=anchor(nx))
    x, y, nx = at(P, Q, 0.47, 18); s += dc.tint(text(round(x), round(y + 5), [("v", "I"), ("vsub", nm)], anchor=anchor(nx)), dc.RED)
cx, cy = dc.CEN
s += text(round(cx), round(cy + 8), ZP + [("n", " = "), ("v", "R"), ("n", " + "), ("v", "jω"), ("n", "("), ("v", "L"), ("n", " − "), ("v", "M"), ("n", ")")], anchor="middle")
s += text(round(cx), round(cy + 30), [("n", "= 1 + "), ("v", "j"), ("n", "1 = √2∠45° Ω")], anchor="middle")
s += text(84, 176, [("t", "無互感等效 Δ")])
s += text(84, 198, [("t", "每邊 ")] + ZP + [("n", " = 1 + "), ("v", "j"), ("n", "1 Ω")])
s += footer()
open(dc.out_path('EE-113-01-3-decoupled-delta.svg'), 'w').write(s)
print(len(s))
