"""EE-110-04-3 fig 2: rated-point phasors, V_phi = E_a + jXs I_a (motor), PF 0.8 lagging."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
kv, ki = 1.6, 6.0                       # px per volt, px per ampere
ox, oy = 60, 60
W, H = 640, 340
V = (219.3931, 0.0); E = (120.2560, -132.1832); I = (22.7902, -17.0926)
P = lambda x, y, k: (ox + k * x, oy - k * y)
s = header(W, H)
s += f'<path d="M{ox - 10} {oy} L{ox + 400} {oy}" stroke-width="0.8"/>\n'
v = P(*V, kv); e = P(*E, kv); i = P(*I, ki)
s += arrow(ox, oy, *v, color=BLUE) + arrow(ox, oy, *e, color=BLUE) + arrow(*e, *v, color=BLUE)
s += arrow(ox, oy, *i, color=RED) + dot(ox, oy)
d = math.atan2(-E[1], E[0]); r = 150
s += f'<path d="M{ox + r} {oy} A{r} {r} 0 0 1 {ox + r * math.cos(d):.1f} {oy + r * math.sin(d):.1f}"/>\n'
ph = math.atan2(-I[1], I[0]); r2 = 70
s += f'<path d="M{ox + r2} {oy} A{r2} {r2} 0 0 1 {ox + r2 * math.cos(ph):.1f} {oy + r2 * math.sin(ph):.1f}"/>\n'
s += end_group()
s += text(ox - 6, oy - 8, [("v", "O")], anchor="end")
s += ctext(BLUE, v[0], oy - 12, [("v", "V"), ("vsub", "ϕ"), ("n", " = 219.39∠0° V")], anchor="middle")
s += ctext(BLUE, e[0] - 14, e[1] + 28, [("v", "E"), ("vsub", "a"), ("n", " = 178.70∠−47.71° V")], anchor="middle")
mx, my = (e[0] + v[0]) / 2, (e[1] + v[1]) / 2
s += ctext(BLUE, mx + 18, my + 10, [("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("n", " = 165.23∠53.13° V")])
s += ctext(RED, i[0] + 8, i[1] + 4, [("v", "I"), ("vsub", "a"), ("n", " = 28.49")])
s += ctext(RED, i[0] + 8, i[1] + 24, [("n", "∠−36.87° A")])
s += text(ox + r2 + 4, oy + 22, [("n", "36.87°")])
s += text(ox + 152, oy + 58, [("v", "δ"), ("n", " = −47.71°")])
s += text(W / 2, H - 14, [("t", "電動機："), ("v", "V"), ("vsub", "ϕ"), ("n", " = "), ("v", "E"), ("vsub", "a"), ("n", " + "), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("t", "（電壓、電流各自依比例）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-110-04-3-phasor.svg'), 'w').write(s)
print(len(s))
