"""EE-108-02-2: three +-90 V triangular phase voltages and the five-diode rectifier output V_L with its notch."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *


def tri(t):
    t %= 360
    return t if t <= 90 else (180 - t if t <= 270 else t - 360)


W, H = 720, 520
X0, XS = 110, 1.5            # 360 deg -> 540 px
YP, PS = 130, 0.8            # phase panel zero line, px per V
YL, LS = 440, 1.2            # V_L panel zero line, px per V
X = lambda th: X0 + XS * th
s = header(W, H)
s += arrow(X0, YP, X(360) + 30, YP) + arrow(X0, YP + 82, X0, 30)
s += arrow(X0, YL, X(360) + 30, YL) + arrow(X0, YL + 8, X0, 282)
styles = (("a", 0, None, ''), ("b", 120, None, ' stroke-dasharray="7 4"'), ("c", 240, BLUE, ''))
for name, sh, col, dash in styles:
    pts = [(X(th), YP - PS * tri(th - sh)) for th in range(0, 361, 30)]
    c = f' stroke="{col}"' if col else ''
    s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" stroke-width="1.8"{c}{dash}/>\n'
# V_L
vl = [(X(th), YL - LS * (max(tri(th), tri(th - 240)) - min(tri(th), tri(th - 120), tri(th - 240)))) for th in range(0, 361, 30)]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in vl) + f' L{X(360):.1f} {YL} L{X0} {YL} Z" fill="{FILL_RED}" stroke="none"/>\n'
s += poly(vl, w=2.2, color=RED)
s += dashed(X0, YL - LS * 100, X(360), YL - LS * 100)
for th in (30, 90, 150, 210, 270, 330):
    s += dashed(X(th), 30, X(th), YL + 6)
s += end_group()
t = []
t.append(text(X0 - 8, YP - PS * 90 + 5, [("n", "90 V")], anchor="end"))
t.append(text(X0 - 8, YP + PS * 90 + 5, [("n", "−90 V")], anchor="end"))
t.append(text(X0 - 8, YP + 5, [("v", "V"), ("vsub", "an")], anchor="end"))
t.append(text(X0 - 8, YP + PS * 60 + 5, [("v", "V"), ("vsub", "bn")], anchor="end"))
t.append(text(X0 - 8, YP - PS * 60 + 5, [("v", "V"), ("vsub", "cn")], anchor="end").replace('fill="#000"', f'fill="{BLUE}"', 1))
t.append(text(X(360) + 30, YP + 20, [("v", "θ")]))
t.append(text(X0 - 8, YL - LS * 120 + 5, [("v", "V"), ("vsub", "L"), ("n", " = 120 V")], anchor="end"))
t.append(text(X0 - 8, YL - LS * 100 + 12, [("v", "V"), ("vsub", "dc"), ("n", " = 100 V")], anchor="end"))
t.append(text(X(210), YL + 22, [("n", "210°")], anchor="middle"))
t.append(text(X(168), YL - 40, [("n", "420 − 2"), ("v", "θ")], anchor="end"))
t.append(text(X(252), YL - 40, [("n", "2"), ("v", "θ"), ("n", " − 420")], anchor="start"))
for th in (30, 90, 150, 270, 330, 360):
    t.append(text(X(th), YL + 22, [("n", f"{th}°")], anchor="middle"))
pairs = ((15, "2", "4"), (60, "1", "4"), (120, "1", "5"), (180, "1", "5"), (240, "2", "3"), (300, "2", "3"), (345, "2", "4"))
for th, top, bot in pairs:
    t.append(text(X(th), 248, [("v", "D"), ("sub", top)], anchor="middle"))
    t.append(text(X(th), 268, [("v", "D"), ("sub", bot)], anchor="middle"))
t.append(text(X0 - 8, 248, [("t", "上臂")], anchor="end"))
t.append(text(X0 - 8, 268, [("t", "下臂")], anchor="end"))
s += ''.join(t) + footer()
write('EE-108-02-2-waveforms.svg', s)
