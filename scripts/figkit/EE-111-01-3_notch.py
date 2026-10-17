"""EE-111-01-3: |H(jw)| band-stop response, pass-band gain 0.40, half-power level 0.2828, w1, w0, w2."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 330
X0, X1, Y0, Y1 = 80, 600, 270, 60          # plot box: x range, y (bottom = 0, top = 0.45)
WMIN, WMAX, GMAX = 11000, 21000, 0.52
w0s, a = 2.5e8, 2400.0
w1, w0, w2 = 14656.86, math.sqrt(w0s), 17056.86
px = lambda w: X0 + (w - WMIN) / (WMAX - WMIN) * (X1 - X0)
py = lambda g: Y0 - g / GMAX * (Y0 - Y1)
gain = lambda w: 0.4 * abs(w0s - w * w) / math.hypot(w0s - w * w, a * w)

s = header(W, H)
s += arrow(X0, Y0, X1 + 20, Y0) + arrow(X0, Y0, X0, Y1 - 20)
pts = [(px(w), py(gain(w))) for w in [WMIN + k * (WMAX - WMIN) / 600 for k in range(601)]]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + '" stroke-width="2"/>\n'
s += dashed(X0, py(0.4), X1, py(0.4))
s += f'<path d="M{X0} {py(0.4 / math.sqrt(2)):.1f} L{X1} {py(0.4 / math.sqrt(2)):.1f}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="4 3"/>\n'
yb = py(0.4) - 22
for w in (w1, w2):
    s += f'<path d="M{px(w):.1f} {yb:.1f} L{px(w):.1f} {Y0}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="4 3"/>\n'
    s += f'<circle cx="{px(w):.1f}" cy="{py(0.4 / math.sqrt(2)):.1f}" r="3.2" fill="{BLUE}" stroke="none"/>\n'
s += dashed(px(w0), Y0, px(w0), py(0.4))
s += f'<g stroke="{BLUE}">' + arrow(px(w0), yb, px(w2), yb, BLUE) + arrow(px(w0), yb, px(w1), yb, BLUE) + '</g>\n'
s += end_group()
s += text(X0 - 8, Y1 - 24, [("n", "|"), ("v", "H"), ("n", "("), ("v", "jω"), ("n", ")|")], anchor="start")
s += text(X1 + 14, Y0 + 22, [("v", "ω")], anchor="middle")
s += text(X0 - 8, py(0.4) + 5, [("n", "0.40")], anchor="end")
s += ttext(X0 - 8, py(0.4 / math.sqrt(2)) + 5, [("n", "0.2828")], anchor="end", color=BLUE)
s += text(X0 - 8, Y0 + 5, [("n", "0")], anchor="end")
s += ttext(px(w1) - 6, Y0 + 22, [("v", "ω"), ("sub", "1"), ("n", " = 14656.86")], anchor="end", color=BLUE)
s += ttext(px(w2) + 6, Y0 + 22, [("v", "ω"), ("sub", "2"), ("n", " = 17056.86")], anchor="start", color=BLUE)
s += text(px(w0), Y0 + 44, [("v", "ω"), ("sub", "0"), ("n", " = 15811.39 rad/s")], anchor="middle")
s += ttext(px(w0), yb - 10, [("n", "BW = "), ("v", "α"), ("n", " = 2400 rad/s")], anchor="middle", color=BLUE)
s += ttext(X1 - 4, py(0.4 / math.sqrt(2)) - 8, [("n", "0.40/√2")], anchor="end", color=BLUE)
s += text(X0 + 10, py(0.4) - 8, [("t", "通帶增益 "), ("v", "R"), ("n", "/("), ("v", "R"), ("vsub", "o"), ("n", " + "), ("v", "R"), ("n", ")")], anchor="start")
s += footer()
write('EE-111-01-3-notch.svg', s)
