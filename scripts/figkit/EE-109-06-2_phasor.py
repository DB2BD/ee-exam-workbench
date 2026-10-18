"""EE-109-06-2 per-phase phasor diagram (not to scale): V_r reference, I lagging by phi = 25.84 deg,
IR parallel to I, jIX leading I by 90 deg; the projection on V_r is I(R cos phi + X sin phi).
"""
import sys, math, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
DOT = "̇"  # combining dot above -> phasor
W, H = 680, 372; s = header(W, H)
ox, oy = 50, 200; th = math.acos(0.9)
vr = (440, oy)
c, sn = math.cos(th), math.sin(th)
irl = (vr[0] + 110 * c, vr[1] + 110 * sn)                 # IR parallel to I (lagging -> drawn downward)
vs = (irl[0] + 120 * sn, irl[1] - 120 * c)                 # jIX leads I by 90 deg (drawn longer, X = 2R)
ie = (ox + 170 * c, oy + 170 * sn)
s += arrow(ox, oy, *vr, BLUE) + arrow(ox, oy, *vs, BLUE)
s += arrow(*vr, *irl) + arrow(*irl, *vs)
s += arrow(ox, oy, *ie, RED)
s += f'<path d="M{ox + 70} {oy} A70 70 0 0 1 {ox + 70 * c:.1f} {oy + 70 * sn:.1f}" stroke-width="1"/>\n'
for x, y0 in ((vr[0], oy - 4), (vs[0], vs[1] - 4)):
    s += f'<path d="M{x:.1f} {y0:.1f} L{x:.1f} 104" stroke-width="1" stroke-dasharray="4 3"/>\n'
s += arrow(vr[0] + 8, 112, vs[0] - 0.5, 112) + arrow(vs[0] - 8, 112, vr[0] + 0.5, 112)
s += dot(ox, oy) + end_group()
s += ctext(BLUE, 300, oy + 24, [("v", "V" + DOT), ("vsub", "r")], anchor="middle")
s += ctext(BLUE, 320, 158, [("v", "V" + DOT), ("vsub", "s")], anchor="middle")
s += ctext(RED, ie[0] - 6, ie[1] + 24, [("v", "I" + DOT)], anchor="middle")
s += text(ox + 82, oy + 26, [("v", "ϕ")])
s += text((vr[0] + irl[0]) / 2 - 16, (vr[1] + irl[1]) / 2 + 30, [("v", "I" + DOT + "R")], anchor="middle")
s += text(irl[0] + 52, irl[1] - 20, [("v", "jI" + DOT + "X")], anchor="start")
s += text((vr[0] + vs[0]) / 2, 94, [("v", "I"), ("n", "("), ("v", "R"), ("n", " cos "), ("v", "ϕ"), ("n", " + "), ("v", "X"), ("n", " sin "), ("v", "ϕ"), ("n", ")")], anchor="middle")
s += text(340, 336, [("n", "cos "), ("v", "ϕ"), ("n", " = 0.9"), ("t", "（落後），"), ("v", "ϕ"), ("n", " = 25.84°"), ("t", "；相量長度放大示意，未依比例")], anchor="middle")
s += text(340, 360, [("t", "線間壓降 "), ("n", "Δ"), ("v", "V"), ("n", " = √3 "), ("v", "I"), ("vsub", "L"), ("n", "("), ("v", "R"), ("n", " cos "), ("v", "ϕ"), ("n", " + "), ("v", "X"), ("n", " sin "), ("v", "ϕ"), ("n", ")")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-109-06-2-phasor.svg'
out.write_text(s); print(out.name, len(s))
