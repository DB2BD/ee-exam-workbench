"""EE-104-04-5 fig 2: phasors with each case's terminal voltage as reference. Left: case 2 (0.8 lag) to scale.
Right: tip region magnified -- both cases end on the same |E_f| arc."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def col(frag, c): return f'<g stroke="{c}">' + frag.replace('fill="#000"', f'fill="{c}"').replace('stroke="#000"', f'stroke="{c}"') + '</g>\n'
def dashed(frag): return frag.replace('<path d=', '<path stroke-dasharray="6 4" d=', 1)
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
Ef = 219.6221; V2 = 213.6246; I2 = 9.7640; V1 = 219.3931; I1 = 10.0277
phi = math.radians(36.87); dre, dim = I2 * 0.6, I2 * 0.8          # jX_s I' = 5.8584 + j7.8112
W, H = 720, 380; s = header(W, H)
# ---- left panel (to scale, 1.5 px per V; current 9 px per A)
k = 1.5; ox, oy = 30, 170
vx = ox + k * V2; ex, ey = ox + k * (V2 + dre), oy - k * dim
s += col(arrow(ox, oy, vx, oy), BLUE) + col(arrow(ox, oy, ex, ey), BLUE)
ki = 9.0
s += col(arrow(ox, oy, ox + ki * I2 * math.cos(phi), oy + ki * I2 * math.sin(phi)), RED)
s += f'<path d="M{ox + 45} {oy} A45 45 0 0 1 {ox + 45 * math.cos(phi):.1f} {oy + 45 * math.sin(phi):.1f}"/>\n'
s += dot(ox, oy)
s += f'<circle cx="{vx + 4:.1f}" cy="{oy - 6}" r="16" stroke-dasharray="4 4" stroke-width="1"/>\n'
s += f'<path d="M{vx + 20:.1f} {oy - 6} L400 200" stroke-dasharray="4 4" stroke-width="1"/>\n'
# ---- right panel: magnified tip region, 20 px per V, x from 211 V
x0, m, by = 420, 16.0, 340
X = lambda v: x0 + (v - 206) * m
Y = lambda v: by - v * m
s += f'<rect x="400" y="40" width="312" height="330" stroke-dasharray="6 4" stroke-width="1"/>\n'
s += col(arrow(X(206), by, X(V2), by), BLUE)                               # V_phi' tip
s += col(arrow(X(V2), by, X(V2 + dre), Y(dim)), BLUE)                      # jX_s I'
s += col(arrow(X(V2 + dre) - 150, Y(dim) + 150 * dim / (V2 + dre), X(V2 + dre), Y(dim)), BLUE)   # E_f (case 2)
s += col(dashed(arrow(X(V2), by, X(V1), by)), BLUE)                        # case 1 V_phi extends to 219.3931
s += col(dashed(arrow(X(V1), by, X(V1), Y(I1))), BLUE)                     # case 1 jX_s I_a (vertical)
arc = ' L'.join(f'{X(Ef * math.cos(t)):.1f} {Y(Ef * math.sin(t)):.1f}' for t in [i * 0.0006 for i in range(0, 56)])
s += f'<path d="M{arc}" stroke-dasharray="2 4" stroke-width="1"/>\n'
s += f'<path d="M{X(V2) + 26} {by} A26 26 0 0 0 {X(V2) + 26 * 0.6:.1f} {by - 26 * 0.8:.1f}"/>\n'
s += end_group()
s += text(20, 26, [("t", "左：情況 2 依比例（1 V = 1.5 px）；右：尖端放大（1 V = 16 px）")])
s += text(ox - 6, oy + 22, [("v", "O")], anchor="middle")
s += ctext(BLUE, 260, oy + 24, [("v", "V"), ("vsub", "ϕ"), ("n", "′"), ("t", "（參考）")], anchor="middle")
s += ctext(BLUE, 150, oy - 30, [("v", "E"), ("vsub", "f"), ("t", "（與情況 1 同大小）")], anchor="middle")
s += ctext(RED, ox + 80, oy + 72, [("v", "I"), ("vsub", "a"), ("n", "′ = 9.7640∠−36.87° A")])
s += text(ox + 50, oy + 26, [("v", "θ"), ("n", " = 36.87°")])
s += ctext(BLUE, 425, by - 30, [("v", "V"), ("vsub", "ϕ"), ("n", "′ = 213.6246 V")])
s += ctext(BLUE, 425, 262, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("n", "′ =")])
s += ctext(BLUE, 425, 282, [("n", "9.7640∠53.13° V")])
s += ctext(BLUE, 425, 204, [("v", "E"), ("vsub", "f"), ("t", "（情況 2）")])
s += text(X(V2) + 30, by - 8, [("n", "53.13°")])
s += ctext(BLUE, 412, 70, [("t", "虛線：情況 1（電阻負載）")])
s += ctext(BLUE, 412, 92, [("v", "V"), ("vsub", "ϕ"), ("n", " = 219.3931 V")])
s += ctext(BLUE, 412, 114, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("n", " = "), ("v", "j"), ("n", "10.0277 V")])
s += text(412, 142, [("t", "點線：半徑 "), ("n", "|"), ("v", "E"), ("vsub", "f"), ("n", "| = 219.6221 V")])
s += text(412, 162, [("t", "的圓弧（兩種情況尖端皆在其上）")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-104-04-5-phasor.svg'), 'w').write(s)
print(len(s))
