"""EE-111-04-5 fig 1: plant power triangle and the condenser's reactive compensation."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
k = 0.1                                 # px per kW / kvar
ox, oy = 60, 250
px, qy = ox + k * 3000, oy - k * 1859.23
W, H = 640, 320
s = header(W, H)
s += arrow(ox, oy, px, oy)                       # P
s += arrow(px, oy, px, qy)                       # Q (lagging, drawn up)
s += arrow(ox, oy, px, qy)                       # S before
s += arrow(px + 40, qy, px + 40, oy, color=BLUE) # Qc supplied by the condenser
s += f'<path d="M{px} {qy} L{px+40} {qy}" stroke-dasharray="3 3" stroke-width="1"/>\n'
phi = math.atan2(1859.23, 3000); r = 70
s += f'<path d="M{ox+r} {oy} A{r} {r} 0 0 0 {ox+r*math.cos(phi):.1f} {oy-r*math.sin(phi):.1f}"/>\n'
s += end_group()
s += text((ox + px) / 2, oy + 26, [("v", "P"), ("n", " = 3000 kW")], anchor="middle")
s += text(px - 10, (oy + qy) / 2, [("v", "Q"), ("n", " = 1859.23 kvar")], anchor="end")
s += text(ox + 160, qy + 60, [("v", "S"), ("n", " = 3529.41 kVA")], anchor="end")
s += text(ox + 80, oy - 10, [("v", "φ"), ("n", " = 31.79°")])
s += ctext(BLUE, px + 52, (oy + qy) / 2 - 10, [("v", "Q"), ("vsub", "c"), ("n", " = 1859.23 kvar")])
s += ctext(BLUE, px + 52, (oy + qy) / 2 + 12, [("t", "由同步電容器供給")])
s += text(W / 2, 308, [("t", "補償後：電纜只送 "), ("v", "P"), ("n", " = 3000 kW"), ("t", "，PF = 1.0")], anchor="middle")
s += text(30, 30, [("t", "補償前工廠負載（PF 0.85 落後）")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-5-power-triangle.svg'), 'w').write(s)
print(len(s))
