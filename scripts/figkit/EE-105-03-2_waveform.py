import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-105-03-2: f(t) = |sin wt| over three periods; period T = pi/w; first period (where f = sin wt) shaded.
W, H = 680, 330
ox, oy, ux, uy = 70, 250, 180, 150   # ux pixels per period T, uy pixels per unit of f
X = lambda k: ox + ux * k             # k = t / T
Y = lambda v: oy - uy * v
s = header(W, H)
# shaded one-period integral region 0 <= t <= T
pts = ' L'.join(f'{X(k / 60):.1f} {Y(math.sin(math.pi * k / 60)):.1f}' for k in range(61))
s += f'<path d="M{X(0)} {oy} L{pts} L{X(1)} {oy} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, oy, 650, oy) + arrow(ox, oy + 30, ox, 30)
# curve |sin wt| on 0 <= t <= 3T
pts = ' L'.join(f'{X(k / 60):.1f} {Y(abs(math.sin(math.pi * k / 60))):.1f}' for k in range(181))
s += f'<path d="M{pts}" stroke-width="2"/>\n'
# period guide lines and level 1
for k in (1, 2, 3):
    s += dashed(X(k), oy, X(k), Y(1.0) - 10)
s += dashed(ox, Y(1), X(0.5), Y(1))
s += end_group()
# period dimension line between 0 and T (blue)
yd = Y(1) - 26
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">\n'
s += arrow(X(0.5), yd, X(0) + 2, yd, BLUE) + arrow(X(0.5), yd, X(1) - 2, yd, BLUE)
s += '</g>\n'
s += ctext(X(0.5), yd - 10, [("t", "週期 "), ("v", "T"), ("n", " = "), ("v", "π"), ("n", "/"), ("v", "ω")], anchor="middle")
# axis labels and ticks
s += text(648, oy + 26, [("v", "t")], anchor="middle")
s += text(ox + 10, 40, [("v", "f"), ("n", "("), ("v", "t"), ("n", ") = |sin "), ("v", "ωt"), ("n", "|")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
s += text(X(1), oy + 24, [("v", "T"), ("n", " = "), ("v", "π"), ("n", "/"), ("v", "ω")], anchor="middle")
s += text(X(2), oy + 24, [("n", "2"), ("v", "T")], anchor="middle")
s += text(X(3), oy + 24, [("n", "3"), ("v", "T")], anchor="middle")
# what the shaded region is
s += ctext(X(0.5), Y(0.32), [("v", "f"), ("n", " = sin "), ("v", "ωt")], anchor="middle")
s += ctext(X(0.5), oy + 56, [("t", "一個週期的積分只取 "), ("n", "0 ≤ "), ("v", "t"), ("n", " ≤ "), ("v", "T"),
                             ("t", "（此段 "), ("n", "sin "), ("v", "ωt"), ("n", " ≥ 0"), ("t", "，絕對值不起作用）")], anchor="start")
s += footer()
write('EE-105-03-2-waveform.svg', s)
