"""EE-106-04-5 fig 2: phasor diagram, PF 0.8 lagging (voltages to one scale, I_a on its own scale)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def col(frag, c): return f'<g stroke="{c}">' + frag.replace('fill="#000"', f'fill="{c}"') + '</g>\n'
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
V = 120.0889; ER, EI = 206.0253, 110.4182; I = 24.9815; phi = math.radians(36.87)
W, H = 600, 360; k = 2.0; ox, oy = 60, 270
vx = ox + k * V; ex, ey = ox + k * ER, oy - k * EI
s = header(W, H)
s += col(arrow(ox, oy, vx, oy), BLUE) + col(arrow(ox, oy, ex, ey), BLUE) + col(arrow(vx, oy, ex, ey), BLUE)
ki = 5.0
s += col(arrow(ox, oy, ox + ki * I * math.cos(phi), oy + ki * I * math.sin(phi)), RED)
s += f'<path d="M{ox + 60} {oy} A60 60 0 0 1 {ox + 60 * math.cos(phi):.1f} {oy + 60 * math.sin(phi):.1f}"/>\n'
d = math.atan2(EI, ER); R = 120
s += f'<path d="M{ox + R} {oy} A{R} {R} 0 0 0 {ox + R * math.cos(d):.1f} {oy - R * math.sin(d):.1f}"/>\n'
s += f'<path d="M{vx:.1f} {oy} L{ex:.1f} {oy}" stroke-dasharray="5 4" stroke-width="1"/>\n'
s += f'<path d="M{ex:.1f} {oy} L{ex:.1f} {ey:.1f}" stroke-dasharray="5 4" stroke-width="1"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(20, 30, [("t", "電壓 1 V = 2 px；"), ("v", "I"), ("vsub", "a"), ("t", " 另用電流比例")])
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, vx - 6, oy + 24, [("v", "V"), ("vsub", "ϕ"), ("n", " = 120.0889∠0° V")], anchor="end")
s += ctext(BLUE, 210, 100, [("v", "E"), ("vsub", "f"), ("n", " = 233.7490∠28.19° V")], anchor="middle")
s += text(ox + R + 6, oy - 40, [("v", "δ"), ("n", " = 28.19°")])
s += text(ox + 64, oy + 36, [("n", "36.87°")])
s += ctext(RED, ox + 100, oy + 84, [("v", "I"), ("vsub", "a"), ("n", " = 24.9815∠−36.87° A")])
s += ctext(BLUE, (vx + ex) / 2 - 14, (oy + ey) / 2, [("v", "I"), ("vsub", "a"), ("v", "Z"), ("vsub", "s")], anchor="end")
s += text((vx + ex) / 2, oy + 24, [("n", "85.9364")], anchor="middle")
s += text(ex + 8, (oy + ey) / 2, [("n", "110.4182")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-106-04-5-phasor-lag.svg'), 'w').write(s)
print(len(s))
