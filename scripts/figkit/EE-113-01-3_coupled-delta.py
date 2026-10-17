import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-113-01-3_delta_common.py')
_s = importlib.util.spec_from_file_location('dc', _p); dc = importlib.util.module_from_spec(_s); _s.loader.exec_module(dc)
from svgkit import *
A, B, C, at, anchor = dc.A, dc.B, dc.C, dc.at, dc.anchor
W, H, YLC = 640, 400, 360
s = header(W, H)
s += dc.frame(YLC)
for P, Q, _ in dc.BRANCHES:
    s += dc.branch(P, Q)
    s += dc.tint(dc.head(P, Q, 0.47), dc.RED)
    # dotted terminal: coil end adjacent to the resistor, marked on the inner side
    x, y, _n = at(P, Q, dc.T_L[0] + 0.035, -13)
    s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="#000" stroke="none"/>\n'
s += dc.tint(arrow(190, A[1], 236, A[1]), dc.RED)                      # line current I_a
s += end_group()
s += dc.labels_terminals(YLC)
s += dc.tint(text(64, A[1] + 26, [("n", "+")], anchor="middle"), dc.BLUE)
s += dc.tint(text(64, B[1] - 14, [("n", "−")], anchor="middle"), dc.BLUE)
s += dc.tint(text(84, 176, [("v", "V"), ("vsub", "ab"), ("n", " = 110√2∠25° V")]), dc.BLUE)
s += text(84, 198, [("t", "（正相序，"), ("v", "ω"), ("n", " = 1 rad/s"), ("t", "）")])
s += dc.tint(text(212, A[1] - 12, [("v", "I"), ("vsub", "a")], anchor="middle"), dc.RED)
for P, Q, nm in dc.BRANCHES:
    x, y, nx = at(P, Q, sum(dc.T_R) / 2, 22); s += text(round(x), round(y + 5), [("v", "R"), ("n", " = 1 Ω")], anchor=anchor(nx))
    x, y, nx = at(P, Q, sum(dc.T_L) / 2, 22); s += text(round(x), round(y + 5), [("v", "L"), ("n", " = 2 H")], anchor=anchor(nx))
    x, y, nx = at(P, Q, 0.47, 18); s += dc.tint(text(round(x), round(y + 5), [("v", "I"), ("vsub", nm)], anchor=anchor(nx)), dc.RED)
cx, cy = dc.CEN
s += text(round(cx), round(cy + 8), [("t", "每對 "), ("v", "M"), ("n", " = 1 H")], anchor="middle")
s += text(round(cx), round(cy + 30), [("n", "● "), ("t", "同名端")], anchor="middle")
s += footer()
open(dc.out_path('EE-113-01-3-coupled-delta.svg'), 'w').write(s)
print(len(s))
