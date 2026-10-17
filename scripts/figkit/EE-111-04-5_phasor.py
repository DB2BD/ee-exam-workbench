"""EE-111-04-5 fig 2: condenser phasors, motor convention; -jXs*Ic is along +real so E_f = V + Xs*Ic."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
kv, ki = 0.25, 0.25
ox, oy = 50, 160
vx = ox + kv * 1327.906; ex = vx + kv * 746.731; iy = oy - ki * 466.707
W, H = 640, 260
s = header(W, H)
s += arrow(ox, oy, vx, oy, color=BLUE)
s += arrow(vx, oy, ex, oy, color=BLUE)
s += arrow(ox, oy, ox, iy, color=RED)
s += arrow(ox, oy + 50, ex, oy + 50, color=BLUE)                     # E_f drawn offset below
s += f'<path d="M{ox} {oy+6} L{ox} {oy+56}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += f'<path d="M{ex} {oy+6} L{ex} {oy+56}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += f'<path d="M{ox+12} {oy} L{ox+12} {oy-12} L{ox} {oy-12}" stroke-width="1"/>\n'   # right angle
s += dot(ox, oy)
s += end_group()
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(RED, ox + 10, iy + 8, [("v", "I"), ("vsub", "c"), ("n", " = "), ("v", "j"), ("n", "466.707 A"), ("t", "（超前 90°）")])
s += ctext(BLUE, (ox + vx) / 2, oy - 10, [("v", "V"), ("vsub", "ϕ"), ("n", " = 1327.906 V")], anchor="middle")
s += ctext(BLUE, (vx + ex) / 2, oy - 10, [("n", "−"), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "c"), ("n", " = 746.731 V")], anchor="middle")
s += ctext(BLUE, (ox + ex) / 2, oy + 76, [("v", "E"), ("vsub", "f"), ("n", " = "), ("v", "V"), ("vsub", "ϕ"), ("n", " − "), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "c"), ("n", " = 2074.637 V")], anchor="middle")
s += text(W - 20, 30, [("t", "電壓、電流各自依比例；"), ("v", "δ"), ("n", " = 0")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-5-phasor.svg'), 'w').write(s)
print(len(s))
