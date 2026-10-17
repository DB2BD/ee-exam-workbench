"""EE-106-04-5 fig 3: phasor diagram, PF 0.8 leading; |E_f| ends up slightly below V_phi."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def col(frag, c): return f'<g stroke="{c}">' + frag.replace('fill="#000"', f'fill="{c}"') + '</g>\n'
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
V = 120.0889; ER, EI = 38.1496, 113.4160; I = 24.9815; phi = math.radians(36.87)
W, H = 600, 380; k = 2.2; ox, oy = 200, 330
vx = ox + k * V; ex, ey = ox + k * ER, oy - k * EI
s = header(W, H)
s += col(arrow(ox, oy, vx, oy), BLUE) + col(arrow(ox, oy, ex, ey), BLUE) + col(arrow(vx, oy, ex, ey), BLUE)
ki = 5.0
s += col(arrow(ox, oy, ox + ki * I * math.cos(phi), oy - ki * I * math.sin(phi)), RED)
s += f'<path d="M{ox + 40} {oy} A40 40 0 0 0 {ox + 40 * math.cos(phi):.1f} {oy - 40 * math.sin(phi):.1f}"/>\n'
d = math.atan2(EI, ER); R = 120
s += f'<path d="M{ox + R} {oy} A{R} {R} 0 0 0 {ox + R * math.cos(d):.1f} {oy - R * math.sin(d):.1f}"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(20, 24, [("t", "電壓 1 V = 2.2 px；"), ("v", "I"), ("vsub", "a"), ("t", " 另用電流比例")])
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, ox + 200, oy + 26, [("v", "V"), ("vsub", "ϕ"), ("n", " = 120.0889∠0° V")], anchor="middle")
s += ctext(BLUE, ex + 12, ey + 6, [("v", "E"), ("vsub", "f"), ("n", " = 119.6603∠71.41° V")])
s += ctext(BLUE, (vx + ex) / 2 + 12, (oy + ey) / 2 - 2, [("v", "I"), ("vsub", "a"), ("v", "Z"), ("vsub", "s")])
s += text(ox + 150 * math.cos(math.radians(58)), oy - 150 * math.sin(math.radians(58)), [("v", "δ"), ("n", " = 71.41°")])
s += text(ox + 46, oy - 8, [("n", "36.87°")])
s += ctext(RED, ox + ki * I * math.cos(phi) + 6, oy - ki * I * math.sin(phi) - 2, [("v", "I"), ("vsub", "a")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-106-04-5-phasor-lead.svg'), 'w').write(s)
print(len(s))
