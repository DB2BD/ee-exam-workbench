import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Governor droop line f = 60 - R*f0*P_M (no-load at 60 Hz), slope R*f0 = 3 Hz/pu.
W, H = 600, 360
ox, oy = 90, 300
X = lambda p: ox + p * 400                 # 0..1.1 pu
Y = lambda f: oy - (f - 56.5) * 62         # 56.5..60.6 Hz
dash = lambda x1, y1, x2, y2, c="#000": f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{c}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s = header(W, H)
s += arrow(ox, oy, X(1.15), oy) + arrow(ox, oy, ox, 34)
s += line(X(0), Y(60), X(1), Y(57))
s += dash(ox, Y(59), X(1 / 3), Y(59), BLUE) + dash(X(1 / 3), Y(59), X(1 / 3), oy, BLUE)
s += dash(ox, Y(57), X(1), Y(57)) + dash(X(1), Y(57), X(1), oy)
s += dot(X(0), Y(60)) + dot(X(1), Y(57))
s += f'<circle cx="{X(1 / 3):.1f}" cy="{Y(59):.1f}" r="3.2" fill="{BLUE}" stroke="none"/>\n'
s += end_group()
s += text(ox - 8, 30, [("v", "f"), ("n", " (Hz)")], anchor="start")
s += text(X(1.15), oy + 40, [("v", "P"), ("vsub", "M"), ("n", " (pu)")], anchor="end")
s += text(ox - 8, Y(60) + 5, [("n", "60")], anchor="end")
s += text(ox - 8, Y(59) + 5, [("n", "59")], anchor="end", color=BLUE)
s += text(ox - 8, Y(57) + 5, [("n", "57")], anchor="end")
s += text(ox, oy + 22, [("n", "0")], anchor="middle")
s += text(X(1 / 3), oy + 22, [("n", "1/3")], anchor="middle", color=BLUE)
s += text(X(1), oy + 22, [("n", "1")], anchor="middle")
s += text(X(0.45), Y(59.55), [("t", "斜率 −"), ("v", "R"), ("v", "f"), ("sub", "0"), ("n", " = −3 Hz/pu")], anchor="start")
s += text(X(1 / 3) + 10, Y(59) - 10, [("n", "Δ"), ("v", "f"), ("n", " = −1 Hz，Δ"), ("v", "P"), ("vsub", "M"), ("n", " = 1/3 pu")], anchor="start", color=BLUE)
s += text(X(0.5), Y(57) - 10, [("t", "無載 → 滿載：60 → 57 Hz")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-113-05-4-droop.svg')
out.write_text(s)
print(len(s))
