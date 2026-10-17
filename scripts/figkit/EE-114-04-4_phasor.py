import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
# per-phase values (same rounding as the note)
V = 1847.52; IR = (16.24, -7.86); JX = (157.29, 324.76); I = (162.38, -78.64)
W, H = 720, 420; s = header(W, H)
k = 0.3; ox, oy = 40, 200                                   # 0.3 px per volt
vx = ox + k * V
qx, qy = vx + k * IR[0], oy - k * IR[1]
ex, ey = ox + k * (V + IR[0] + JX[0]), oy - k * (IR[1] + JX[1])
s += arrow(ox, oy, vx, oy, color=BLUE)                       # V_phi
s += line(vx, oy, qx, qy).replace('/>', f' stroke="{BLUE}"/>')  # Ia Ra (5 px)
s += arrow(qx, qy, ex, ey, color=BLUE)                       # jXs Ia
s += arrow(ox, oy, ex, ey, color=BLUE)                       # E_f
ki = 1.2
s += arrow(ox, oy, ox + ki * I[0], oy - ki * I[1], color=RED)
phi = math.atan2(-I[1], I[0]); d = math.atan2(ey - oy, ex - ox)
s += f'<path d="M{ox+55} {oy} A55 55 0 0 1 {ox+55*math.cos(phi):.1f} {oy+55*math.sin(phi):.1f}"/>\n'
R = 220
s += f'<path d="M{ox+R} {oy} A{R} {R} 0 0 0 {ox+R*math.cos(d):.1f} {oy+R*math.sin(d):.1f}"/>\n'
s += dot(ox, oy)
# zoom circle at the V_phi tip + leader to inset
s += f'<circle cx="{vx+2:.1f}" cy="{oy+1}" r="14" stroke-dasharray="4 3" stroke-width="1"/>\n'
s += f'<path d="M{vx+2:.1f} {oy+15} L{vx+2:.1f} 250" stroke-dasharray="4 3" stroke-width="1"/>\n'
s += f'<rect x="380" y="250" width="332" height="162" stroke-dasharray="6 4" stroke-width="1"/>\n'
# inset: 10x (3 px per volt)
m = 3.0; px, py = 430, 340
q2x, q2y = px + m * IR[0], py - m * IR[1]
s += arrow(392, py, px, py, color=BLUE)
s += arrow(px, py, q2x, q2y, color=BLUE)
u = (math.cos(phi), math.sin(phi)); w = (math.sin(phi), -math.cos(phi))   # along Ia, +90 deg (svg y down)
L = 100
s += line(q2x, q2y, q2x + L * w[0], q2y + L * w[1]).replace('/>', f' stroke="{BLUE}"/>')
s += f'<path d="M{q2x + L*w[0]:.1f} {q2y + L*w[1]:.1f} L{q2x + (L+22)*w[0]:.1f} {q2y + (L+22)*w[1]:.1f}" stroke="{BLUE}" stroke-dasharray="4 3"/>\n'
c = 10
s += (f'<path d="M{q2x+c*u[0]:.1f} {q2y+c*u[1]:.1f} L{q2x+c*u[0]+c*w[0]:.1f} {q2y+c*u[1]+c*w[1]:.1f} '
      f'L{q2x+c*w[0]:.1f} {q2y+c*w[1]:.1f}" stroke-width="1"/>\n')
s += f'<path d="M{q2x:.1f} {q2y:.1f} L{q2x+40*u[0]:.1f} {q2y+40*u[1]:.1f}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += end_group()
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, 330, oy + 24, [("v", "V"), ("vsub", "ϕ"), ("n", " = 1847.52∠0° V")])
s += text(112, oy + 22, [("v", "φ"), ("n", " = 25.84°")])
s += ctext(RED, 150, 324, [("v", "I"), ("vsub", "a"), ("n", " = 180.42∠−25.84° A")])
s += text(268, oy - 12, [("v", "δ"), ("n", " = 8.91°")])
s += ctext(BLUE, 704, 90, [("v", "E"), ("vsub", "f"), ("n", " = 2045.74∠8.91° V")], anchor="end")
s += ctext(BLUE, 588, oy - 18, [("v", "jX"), ("vsub", "s"), ("n", " "), ("v", "I"), ("vsub", "a"), ("n", " = 360.84∠64.16° V")], anchor="end")
s += text(30, 30, [("t", "電壓依同一比例繪製；"), ("v", "I"), ("vsub", "a"), ("t", " 另用電流比例")])
s += text(704, 272, [("t", "尖端放大 10 倍")], anchor="end")
s += text(412, py - 10, [("v", "V"), ("vsub", "ϕ"), ("t", " 尖端")], anchor="middle")
s += ctext(BLUE, 420, 394, [("v", "I"), ("vsub", "a"), ("v", "R"), ("vsub", "a"), ("n", " = 18.04∠−25.84° V")])
s += ctext(BLUE, 536, 316, [("v", "jX"), ("vsub", "s"), ("n", " "), ("v", "I"), ("vsub", "a"), ("t", "（⊥ "), ("v", "I"), ("vsub", "a"), ("t", "，至 "), ("v", "E"), ("vsub", "f"), ("t", " 尖端）")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-114-04-4-phasor.svg'), 'w').write(s)
print(len(s))
