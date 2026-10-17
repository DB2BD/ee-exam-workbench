import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dashed(x1, y1, x2, y2, color="#000"):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="5 4"/>\n'
# Salient-pole two-reaction phasor diagram at unity pf (per unit, drawn to scale):
# V = 1.05∠0°, I = 0.95238∠0°, q axis along E at δ = 25°;
# E = V + jXq Iq + jXd Id, with jXq Iq ⟂ q axis and jXd Id ∥ q axis.
d = math.radians(25)
V, E, I = 1.05, 1.4, 1 / 1.05
Iq, Id = I * math.cos(d), I * math.sin(d)
XqIq = V * math.sin(d); XdId = E - V * math.cos(d)
W, H = 620, 330
ox, oy, k = 60, 250, 250
P = lambda re, im: (ox + re * k, oy - im * k)
vt = P(V, 0)
m = P(V + XqIq * math.cos(d + math.pi / 2), XqIq * math.sin(d + math.pi / 2))
et = P(E * math.cos(d), E * math.sin(d))
iq = P(Iq * math.cos(d), Iq * math.sin(d))
it = P(I, 0)
s = header(W, H)
ofx, ofy = 10 * math.sin(d), 10 * math.cos(d)        # current phasors drawn shifted (rigidly) off the voltage lines
sh = lambda p: (p[0] + ofx, p[1] + ofy)
o2, iq2, it2 = sh((ox, oy)), sh(iq), sh(it)
nx, ny = -8 * math.sin(d), -8 * math.cos(d)          # jXd Id drawn parallel to (just above) the q axis
s += dashed(ox, oy, *P(1.75 * math.cos(d), 1.75 * math.sin(d)))                       # q axis
s += arrow(ox, oy, *vt, color=BLUE)
s += arrow(ox, oy, *et, color=BLUE)
s += arrow(*o2, *it2, color=RED)
s += arrow(*o2, *iq2, color=RED).replace('<path d="M', '<path stroke-dasharray="6 3" d="M', 1)
s += arrow(*iq2, *it2, color=RED).replace('<path d="M', '<path stroke-dasharray="6 3" d="M', 1)
s += arrow(*vt, *m)
s += arrow(m[0] + nx, m[1] + ny, et[0] + nx, et[1] + ny)
s += (f'<path d="M{ox + 90:.1f} {oy:.1f} A90 90 0 0 0 {ox + 90 * math.cos(d):.1f} {oy - 90 * math.sin(d):.1f}" stroke-width="1"/>\n')
s += dot(ox, oy) + dot(*m)
s += end_group()
s += text(*P(1.75 * math.cos(d) + 0.02, 1.75 * math.sin(d) - 0.02), [("v", "q"), ("t", " 軸")])
s += ctext(BLUE, vt[0] + 8, oy - 8, [("v", "V"), ("n", " = 1.05∠0°")])
s += ctext(BLUE, et[0] - 6, et[1] - 16, [("v", "E"), ("n", " = 1.4∠25°")], anchor="end")
s += ctext(RED, it2[0] - 40, oy + 34, [("v", "I"), ("t", "（與 "), ("v", "V"), ("t", " 同相）")], anchor="end")
qa = P(0.7 * Iq * math.cos(d), 0.7 * Iq * math.sin(d))
s += ctext(RED, qa[0] + 12, qa[1] + 22, [("v", "I"), ("vsub", "q")])
s += ctext(RED, (iq2[0] + it2[0]) / 2 - 10, (iq2[1] + it2[1]) / 2 + 4, [("v", "I"), ("vsub", "d")], anchor="end")
s += text((vt[0] + m[0]) / 2 + 12, (vt[1] + m[1]) / 2 + 6, [("v", "jX"), ("vsub", "q"), ("v", "I"), ("vsub", "q")])
s += text((m[0] + et[0]) / 2 - 10, (m[1] + et[1]) / 2 - 14, [("v", "jX"), ("vsub", "d"), ("v", "I"), ("vsub", "d")], anchor="end")
s += text(ox + 98, oy - 6, [("v", "δ")])
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += text(310, 322, [("t", "功因 1：電流與 "), ("v", "V"), ("t", " 同相，與 "), ("v", "q"), ("t", " 軸夾角 = "), ("v", "δ"), ("n", " = 25°")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-110-05-1-phasor.svg'), 'w').write(s)
print(len(s))
