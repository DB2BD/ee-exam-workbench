"""EE-105-04-4 fig 2: motor phasors at constant P -- PF 0.8 leading (solid) vs PF 1 (dashed); E_f tip slides along the
horizontal line E_f sin(delta) = const, I_a tip along the vertical line I_a cos(phi) = const. Drawn to scale for
V=1, X_s=1, P=0.8 pu but labelled with symbols only (the stem gives no numbers)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def col(frag, c): return f'<g stroke="{c}">' + frag.replace('fill="#000"', f'fill="{c}"').replace('stroke="#000"', f'stroke="{c}"') + '</g>\n'
def dashed(frag): return frag.replace('<path d=', '<path stroke-dasharray="7 5" d=', 1)
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 380; ox, oy = 70, 130; kv, ki = 220, 100
vx = ox + kv * 1.0
e1 = (ox + kv * 1.6, oy + kv * 0.8)        # E_f1 = 1.6 - j0.8
e2 = (ox + kv * 1.0, oy + kv * 0.8)        # E_f2 = 1.0 - j0.8
i1 = (ox + ki * 0.8, oy - ki * 0.6)        # I_a1 = 1 /+36.87
i2 = (ox + ki * 0.8, oy)                   # I_a2 = 0.8 /0
s = header(W, H)
s += col(arrow(ox, oy, vx, oy), BLUE)
s += col(arrow(vx, oy, *e1), BLUE) + col(arrow(ox, oy, *e1), BLUE)
s += col(dashed(arrow(vx, oy, *e2)), BLUE) + col(dashed(arrow(ox, oy, *e2)), BLUE)
s += col(arrow(ox, oy, *i1), RED)
s += col(arrow(ox, oy - 5, i2[0], oy - 5), RED)
# loci
s += f'<path d="M{e2[0] - 60} {e2[1]} L{e1[0] + 50} {e1[1]}" stroke-dasharray="2 4" stroke-width="1"/>\n'
s += f'<path d="M{i1[0]} {i1[1] - 25} L{i1[0]} {oy + 20}" stroke-dasharray="2 4" stroke-width="1"/>\n'
# angle arcs: phi (above axis), delta1 / delta2 (below axis)
phi = math.atan2(0.6, 0.8)
s += f'<path d="M{ox + 45} {oy} A45 45 0 0 0 {ox + 45 * math.cos(phi):.1f} {oy - 45 * math.sin(phi):.1f}"/>\n'
d1 = math.atan2(0.8, 1.6); d2 = math.atan2(0.8, 1.0)
R1, R2 = 115, 70
s += f'<path d="M{ox + R1} {oy} A{R1} {R1} 0 0 1 {ox + R1 * math.cos(d1):.1f} {oy + R1 * math.sin(d1):.1f}"/>\n'
s += f'<path d="M{ox + R2} {oy} A{R2} {R2} 0 0 1 {ox + R2 * math.cos(d2):.1f} {oy + R2 * math.sin(d2):.1f}"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(20, 26, [("t", "實線：PF 0.8 超前（原狀態）；虛線：PF 1（減小 "), ("v", "I"), ("vsub", "f"), ("t", " 後）")])
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, vx + 10, oy - 8, [("v", "V"), ("vsub", "ϕ"), ("t", "（參考）")])
s += ctext(RED, i1[0] - 12, i1[1] - 6, [("v", "I"), ("vsub", "a"), ("sub", "1")], anchor="end")
s += ctext(RED, i2[0] + 6, oy - 10, [("v", "I"), ("vsub", "a"), ("sub", "2")])
s += text(ox + 50, oy - 12, [("v", "φ")])
s += ctext(BLUE, e1[0] + 8, e1[1] + 22, [("v", "E"), ("vsub", "f"), ("sub", "1")])
s += ctext(BLUE, e2[0] - 6, e2[1] + 22, [("v", "E"), ("vsub", "f"), ("sub", "2")], anchor="end")
s += ctext(BLUE, (vx + e1[0]) / 2 + 12, (oy + e1[1]) / 2 - 4, [("n", "−"), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("sub", "1")])
s += ctext(BLUE, vx - 6, oy + 28, [("n", "−"), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "a"), ("sub", "2")], anchor="end")
s += text(ox + R1 + 6, oy + 34, [("v", "δ"), ("sub", "1")])
s += text(ox + R2 * math.cos(d2 / 2) - 30, oy + R2 * math.sin(d2 / 2) + 30, [("v", "δ"), ("sub", "2")])
s += text(e1[0] + 14, e1[1] - 6, [("v", "E"), ("vsub", "f"), ("n", " sin "), ("v", "δ"), ("t", " 固定")])
s += text(i1[0] + 8, i1[1] - 12, [("v", "I"), ("vsub", "a"), ("n", " cos "), ("v", "φ"), ("t", " 固定")])
s += text(320, 360, [("v", "P"), ("n", " = 3"), ("v", "V"), ("vsub", "ϕ"), ("v", "I"), ("vsub", "a"), ("n", " cos "), ("v", "φ"), ("n", " = 3"), ("v", "V"), ("vsub", "ϕ"), ("v", "E"), ("vsub", "f"), ("n", " sin "), ("v", "δ"), ("n", "/"), ("v", "X"), ("vsub", "s"), ("t", " 不變")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-105-04-4-phasor.svg'), 'w').write(s)
print(len(s))
