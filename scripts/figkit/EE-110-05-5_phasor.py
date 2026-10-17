import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
# per-unit phasors (text values): V_phi = 1∠0°, I_a = 1∠-36.87°, jXsIa = 0.2755 + j0.3673, E_f = 1.2755 + j0.3673
W, H = 600, 330
ox, oy, k = 60, 200, 330                       # px per pu
vx = ox + 1.0 * k
ex, ey = vx + 0.2755 * k, oy - 0.3673 * k
a = math.radians(-36.87); LI = 0.42 * k        # current drawn shortened (未依比例)
ix, iy = ox + LI * math.cos(a), oy - LI * math.sin(a)
s = header(W, H)
s += arrow(ox, oy, vx, oy, color=BLUE)
s += arrow(vx, oy, ex, ey)
s += arrow(ox, oy, ex, ey, color=BLUE)
s += arrow(ox, oy, ix, iy, color=RED)
R = 70
s += f'<path d="M{ox + R} {oy} A{R} {R} 0 0 1 {ox + R * math.cos(a):.1f} {oy - R * math.sin(a):.1f}" stroke-width="1"/>\n'
R2 = 120; b = math.atan2(oy - ey, ex - ox)
s += f'<path d="M{ox + R2} {oy} A{R2} {R2} 0 0 0 {ox + R2 * math.cos(b):.1f} {oy - R2 * math.sin(b):.1f}" stroke-width="1"/>\n'
s += dot(ox, oy)
s += end_group()
mx, my = (vx + ex) / 2, (oy + ey) / 2
s += ctext(BLUE, (ox + vx) / 2 + 30, oy + 24, [("v", "V"), ("vsub", "ϕ"), ("n", " = 1∠0° pu")], anchor="middle")
s += text(mx + 22, my + 2, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a")])
s += text(mx + 22, my + 22, [("n", "= 0.2755 + "), ("v", "j"), ("n", "0.3673")])
s += ctext(BLUE, (ox + ex) / 2 - 10, (oy + ey) / 2 - 16, [("v", "E"), ("vsub", "f"), ("n", " = 1.3273∠16.07° pu")], anchor="middle")
s += ctext(RED, ix + 8, iy + 16, [("v", "I"), ("vsub", "a"), ("n", " = 1∠−36.87° pu")])
s += text(ox + R + 6, oy + 30, [("n", "36.87°")])
s += text(ox + R2 + 6, oy - 10, [("n", "16.07°")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-110-05-5-phasor.svg'), 'w').write(s)
print(len(s))
