import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 320
ox, oy, k = 60, 205, 0.085                       # px per volt
vx = ox + 3810.51 * k
ex, ey = vx + 1049.73 * k, oy - 1399.64 * k
a = math.radians(-36.87); LI = 130
ix, iy = ox + LI * math.cos(a), oy - LI * math.sin(a)
s = header(W, H)
s += arrow(ox, oy, vx, oy, color=BLUE)
s += arrow(vx, oy, ex, ey)
s += arrow(ox, oy, ex, ey, color=BLUE)
s += arrow(ox, oy, ix, iy, color=RED)
R = 70
s += f'<path d="M{ox + R} {oy} A{R} {R} 0 0 1 {ox + R * math.cos(a):.1f} {oy - R * math.sin(a):.1f}" stroke-width="1"/>\n'
R2 = 110; b = math.atan2(oy - ey, ex - ox)
s += f'<path d="M{ox + R2} {oy} A{R2} {R2} 0 0 0 {ox + R2 * math.cos(b):.1f} {oy - R2 * math.sin(b):.1f}" stroke-width="1"/>\n'
s += dot(ox, oy)
s += end_group()
s += ctext(BLUE, (ox + vx) / 2 + 40, oy + 22, [("v", "V"), ("vsub", "φ"), ("n", " = 3810.51∠0° V")], anchor="middle")
s += text(ex + 10, (oy + ey) / 2 + 10, [("v", "j"), ("v", "X"), ("vsub", "s"), ("v", "I"), ("vsub", "a")])
s += ctext(BLUE, (ox + ex) / 2 - 20, (oy + ey) / 2 - 14, [("v", "E"), ("vsub", "f"), ("n", " = 5057.76∠16.07° V")], anchor="middle")
s += ctext(RED, ix + 8, iy + 14, [("v", "I"), ("vsub", "a"), ("n", " = 218.69∠−36.87° A")])
s += text(ox + R + 6, oy + 26, [("n", "36.87°")])
s += text(ox + R2 + 6, oy - 12, [("n", "16.07°")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-110-05-5-phasor.svg'), 'w').write(s)
print(len(s))
