"""EE-111-04-4 fig 2: rated-load phasor diagram, PF 0.85 lagging (voltages to one scale)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
V = 6350.853; JX = (3110.504, 5019.012); I = (1115.336, -691.223)
kv, ki = 0.05, 0.1
ox, oy = 50, 290
W, H = 640, 400
s = header(W, H)
vx = ox + kv * V; ex, ey = vx + kv * JX[0], oy - kv * JX[1]
s += f'<path d="M{ox-10} {oy} L{W-20} {oy}" stroke-width="0.8"/>\n'
s += arrow(ox, oy, vx, oy, color=BLUE)
s += arrow(vx, oy, ex, ey, color=BLUE)
s += arrow(ox, oy, ex, ey, color=BLUE)
ix, iy = ox + ki * I[0], oy - ki * I[1]
s += arrow(ox, oy, ix, iy, color=RED)
th = math.atan2(691.223, 1115.336); d = math.atan2(5019.012, 9461.357)
r = 60; s += f'<path d="M{ox+r} {oy} A{r} {r} 0 0 1 {ox+r*math.cos(th):.1f} {oy+r*math.sin(th):.1f}"/>\n'
r = 150; s += f'<path d="M{ox+r} {oy} A{r} {r} 0 0 0 {ox+r*math.cos(d):.1f} {oy-r*math.sin(d):.1f}"/>\n'
# right-angle mark between I_a direction and jXsIa at the V tip
u = (math.cos(th), math.sin(th)); w = (math.sin(th), -math.cos(th)); c = 10
s += (f'<path d="M{vx+c*u[0]:.1f} {oy+c*u[1]:.1f} L{vx+c*u[0]+c*w[0]:.1f} {oy+c*u[1]+c*w[1]:.1f} '
      f'L{vx+c*w[0]:.1f} {oy+c*w[1]:.1f}" stroke-width="1"/>\n')
s += f'<path d="M{vx:.1f} {oy} L{vx+45*u[0]:.1f} {oy+45*u[1]:.1f}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, (ox + vx) / 2 + 80, oy - 10, [("v", "V"), ("vsub", "ϕ"), ("n", " = 6350.853∠0° V")], anchor="middle")
s += ctext(RED, ix + 8, iy + 18, [("v", "I"), ("vsub", "a"), ("n", " = 1312.160∠−31.79° A")])
s += text(ox + 66, oy + 26, [("v", "θ"), ("n", " = 31.79°")])
s += text(ox + 156, oy - 34, [("v", "δ"), ("n", " = 27.94°")])
s += ctext(BLUE, ex - 40, ey - 12, [("v", "E"), ("n", " = 10 710.171∠27.94° V")], anchor="middle")
s += ctext(BLUE, (vx + ex) / 2 + 14, (oy + ey) / 2 + 4, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a")])
s += ctext(BLUE, (vx + ex) / 2 + 14, (oy + ey) / 2 + 24, [("n", "= 5904.720∠58.21° V")])
s += text(W - 20, H - 14, [("t", "電壓同一比例；"), ("v", "I"), ("vsub", "a"), ("t", " 另用電流比例")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-4-phasor.svg'), 'w').write(s)
print(len(s))
