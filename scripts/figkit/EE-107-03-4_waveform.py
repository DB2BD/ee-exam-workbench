import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

# EE-107-03-4: f(x) = 0 on (-pi, 0), sin x on [0, pi), period 2pi (half-wave rectified sine).
# Shaded: the only part of one period (-pi, pi) where the integrand is non-zero.
W, H = 680, 330
ox, oy, ux, uy = 340, 230, 95, 130   # ux pixels per pi, uy pixels per unit of f
X = lambda k: ox + ux * k            # k = x / pi
Y = lambda v: oy - uy * v
f = lambda k: max(0.0, math.sin(math.pi * k)) if (k % 2) < 1 else 0.0
s = header(W, H)
# shaded region 0 <= x <= pi
pts = ' L'.join(f'{X(k / 60):.1f} {Y(math.sin(math.pi * k / 60)):.1f}' for k in range(61))
s += f'<path d="M{X(0)} {oy} L{pts} L{X(1)} {oy} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, oy, 660, oy) + arrow(ox, oy + 30, ox, 40)
# curve over -3pi .. 3pi
pts = ' L'.join(f'{X(-3 + k / 60):.1f} {Y(f(-3 + k / 60)):.1f}' for k in range(361))
s += f'<path d="M{pts}" stroke-width="2"/>\n'
# one-period window (-pi, pi) and level 1
for k in (-1, 1):
    s += dashed(X(k), oy, X(k), Y(1.0) - 12)
s += dashed(ox, Y(1), X(0.5), Y(1))
s += end_group()
# period dimension line between -pi and pi (blue)
yd = Y(1) - 26
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">\n'
s += arrow(X(0), yd, X(-1) + 2, yd, BLUE) + arrow(X(0), yd, X(1) - 2, yd, BLUE)
s += '</g>\n'
s += ctext(X(-0.5), yd - 10, [("t", "一個週期 "), ("n", "2"), ("v", "π")], anchor="middle")
# axis labels and ticks
s += text(656, oy + 26, [("v", "x")], anchor="middle")
s += text(ox + 10, 52, [("v", "f"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(ox - 8, oy + 22, [("n", "0")], anchor="end")
s += text(ox - 10, Y(1) + 5, [("n", "1")], anchor="end")
for k, lab in ((-3, "−3"), (-2, "−2"), (-1, "−"), (1, ""), (2, "2"), (3, "3")):
    s += text(X(k), oy + 24, [("n", lab), ("v", "π")], anchor="middle")
s += ctext(X(0.5), Y(0.3), [("v", "f"), ("n", " = sin "), ("v", "x")], anchor="middle")
s += text(X(-0.5), oy - 12, [("v", "f"), ("n", " = 0")], anchor="middle")
s += ctext(X(0), oy + 62, [("t", "係數積分只剩 "), ("n", "0 ≤ "), ("v", "x"), ("n", " ≤ "), ("v", "π"),
                            ("t", "（"), ("n", "−"), ("v", "π"), ("n", " &lt; "), ("v", "x"), ("n", " &lt; 0"), ("t", " 上 "),
                            ("v", "f"), ("n", " = 0"), ("t", "）")], anchor="middle")
s += footer()
write('EE-107-03-4-waveform.svg', s)
