import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 520, 340
ox, oy = 180, 280
LV, LI = 230, 170
s = header(W, H)
s += f'<path d="M{ox - 30} {oy} L{ox + 280} {oy}" stroke-dasharray="5 4" stroke-width="1"/>\n'   # 0° reference
s += arrow(ox, oy, ox, oy - LV, color=BLUE)                                                   # V at 90°
a = math.radians(60)
ix, iy = ox + LI * math.cos(a), oy - LI * math.sin(a)
s += arrow(ox, oy, ix, iy, color=RED)                                                         # I at 60°
R = 70                                                                                        # arc 60°→90° (θ = 30°)
s += f'<path d="M{ox + R * math.cos(a):.1f} {oy - R * math.sin(a):.1f} A{R} {R} 0 0 0 {ox} {oy - R}"/>\n'
R2 = 44                                                                                       # arc 0°→60° (current angle)
s += f'<path d="M{ox + R2} {oy} A{R2} {R2} 0 0 0 {ox + R2 * math.cos(a):.1f} {oy - R2 * math.sin(a):.1f}" stroke-width="1"/>\n'
s += dot(ox, oy)
s += line(ox + 17, oy - 68, ox - 26, oy - 106)                                                # leader to θ label
s += end_group()
s += ctext(BLUE, ox - 12, oy - LV + 10, [("v", "V"), ("n", " = 100∠"), ("v", "α"), ("n", " = 100∠90° V")], anchor="end")
s += ctext(RED, ix + 10, iy + 4, [("v", "I"), ("n", " = 10∠60° A")])
s += text(ox - 30, oy - 112, [("v", "θ"), ("n", " = "), ("v", "α"), ("n", " − 60° = 30°")], anchor="end")
s += text(ox + R2 + 8, oy - 12, [("n", "60°")])
s += text(ox + 286, oy + 5, [("n", "0°")])
s += text(ox - 8, oy + 20, [("v", "O")], anchor="end")
s += text(260, 330, [("t", "電流落後電壓 30°（"), ("v", "Q"), ("n", " > 0"), ("t", "，電感性）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-114-05-1-phasor.svg'), 'w').write(s)
print(len(s))
