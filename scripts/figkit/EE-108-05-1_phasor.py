import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
# per-unit phasors from the note: V = 1∠0°, I = 0.72 − j0.34871, jXdI = 0.60121 + j1.24135,
# Ei = 1.60121 + j1.24135 (2.0260∠37.78°), Ei' = 2.0903 + j1.2414 (2.4312∠30.70°)
W, H = 640, 440
ox, oy, k = 60, 330, 205
P = lambda re, im: (ox + re * k, oy - im * k)
vx, vy = P(1, 0); ix, iy = P(0.72, -0.34871); ex, ey = P(1.60121, 1.24135); fx, fy = P(2.0903, 1.2414)
s = header(W, H)
s += f'<path d="M{ox + 40} {ey:.1f} L{fx + 60:.1f} {ey:.1f}" stroke-width="1" stroke-dasharray="5 4"/>\n'   # constant-P locus
s += arrow(ox, oy, vx, vy, color=BLUE)
s += arrow(ox, oy, ix, iy, color=RED)
s += arrow(vx, vy, ex, ey)
s += arrow(ox, oy, ex, ey, color=BLUE)
s += arrow(ox, oy, fx, fy, color=BLUE).replace('<path d="M', '<path stroke-dasharray="7 4" d="M', 1)
def arc(R, a1, a2, sweep):
    return (f'<path d="M{ox + R * math.cos(a1):.1f} {oy - R * math.sin(a1):.1f} A{R} {R} 0 0 {sweep} '
            f'{ox + R * math.cos(a2):.1f} {oy - R * math.sin(a2):.1f}" stroke-width="1"/>\n')
s += arc(70, 0, math.radians(-25.84), 1)
s += arc(105, 0, math.radians(37.78), 0)
s += arc(160, 0, math.radians(30.70), 0)
s += dot(ox, oy)
s += end_group()
s += ctext(BLUE, vx - 5, oy + 26, [("v", "V"), ("n", " = 1∠0° pu")], anchor="middle")
s += ctext(RED, ix + 8, iy + 18, [("v", "I"), ("n", " = 0.8∠−25.84° pu")])
mx, my = (vx + ex) / 2, (vy + ey) / 2
s += text(mx + 18, my + 4, [("v", "jX"), ("vsub", "d"), ("v", "I")])
s += text(mx + 18, my + 24, [("n", "= 0.60121 + "), ("v", "j"), ("n", "1.24135")])
s += ctext(BLUE, ox + 0.55 * (ex - ox) - 12, oy - 0.55 * (oy - ey) - 6, [("v", "E"), ("vsub", "i"), ("n", " = 2.0260∠37.78°")], anchor="end")
s += ctext(BLUE, fx + 10, fy + 24, [("v", "E"), ("vsub", "i"), ("n", "′ = 2.4312∠30.70°")], anchor="start")
s += text(fx + 60, ey - 12, anchor="end", parts=[("v", "P"), ("v", "X"), ("vsub", "d"), ("n", "/"), ("v", "V"), ("n", " = 1.24135（"), ("v", "P"), ("t", " 不變）")])
s += text(ox + 92, oy + 22, [("v", "ϕ")])
s += text(ox + 108, oy - 46, [("v", "δ")])
s += text(ox + 163, oy - 22, [("v", "δ"), ("n", "′")])
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-1-phasor.svg'), 'w').write(s)
print(len(s))
