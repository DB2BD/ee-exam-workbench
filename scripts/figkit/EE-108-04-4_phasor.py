"""EE-108-04-4 fig 2: unity-PF motor phasors, V_phi = E_f + jXs I_a."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
kv, ki = 0.36, 0.40                     # px per volt, px per ampere
ox, oy = 50, 90
W, H = 680, 400
V, E = (1327.91, 0.0), (1327.91, -734.24)
P = lambda x, y, k: (ox + k * x, oy - k * y)
s = header(W, H)
v = P(*V, kv); e = P(*E, kv); i = P(376.53, 0, ki)
s += f'<path d="M{ox - 10} {oy} L{v[0] + 30:.1f} {oy}" stroke-width="0.8"/>\n'
s += arrow(ox, oy, *v, color=BLUE) + arrow(ox, oy, *e, color=BLUE) + arrow(*e, *v, color=BLUE)
s += f'<path d="M{ox} {oy + 4} L{i[0]:.1f} {oy + 4}" stroke="{RED}" stroke-width="2.5"/>\n'
s += arrow(i[0] - 10, oy + 4, i[0], oy + 4, color=RED) + dot(ox, oy)
d = math.atan2(-E[1], E[0]); r = 230
s += f'<path d="M{ox + r} {oy} A{r} {r} 0 0 1 {ox + r * math.cos(d):.1f} {oy + r * math.sin(d):.1f}"/>\n'
s += f'<path d="M{v[0] - 14:.1f} {oy} L{v[0] - 14:.1f} {oy + 14} L{v[0]:.1f} {oy + 14}" stroke-width="1"/>\n'   # right angle
s += end_group()
s += text(ox - 6, oy - 8, [("v", "O")], anchor="end")
s += ctext(BLUE, v[0] - 10, oy - 14, [("v", "V"), ("vsub", "ϕ"), ("n", " = 1327.91∠0° V")], anchor="end")
s += ctext(RED, ox + 10, oy - 14, [("v", "I"), ("vsub", "a"), ("n", " = 376.53∠0° A")])
s += ctext(BLUE, v[0] + 10, (oy + e[1]) / 2 - 6, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a")])
s += ctext(BLUE, v[0] + 10, (oy + e[1]) / 2 + 16, [("n", "= 734.24∠90° V")])
s += ctext(BLUE, (ox + e[0]) / 2 - 50, (oy + e[1]) / 2 + 40, [("v", "E"), ("vsub", "f"), ("n", " = 1517.38∠−28.94° V")], anchor="middle")
s += text(ox + r + 8, oy + 60, [("v", "δ"), ("n", " = −28.94°")])
s += text(W / 2, H - 16, [("t", "電動機："), ("v", "V"), ("vsub", "ϕ"), ("n", " = "), ("v", "E"), ("vsub", "f"), ("n", " + "), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("t", "；PF = 1，"), ("v", "I"), ("vsub", "a"), ("t", " 與 "), ("v", "V"), ("vsub", "ϕ"), ("t", " 同相（電流另用比例）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-108-04-4-phasor.svg'), 'w').write(s)
print(len(s))
