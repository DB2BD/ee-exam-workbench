"""EE-114-06-1 secondary line-voltage phasors (part (一)), drawn head to tail:
V_ab = 220∠0°, V_bc = 220∠-120°, V_ca = -(V_ab + V_bc) = 220∠120° closes the triangle (KVL a->b->c->a).
"""
import sys, math, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 560, 370; s = header(W, H)
L = 240; ox, oy = 150, 60
p0 = (ox, oy)
p1 = (ox + L, oy)                                   # tip of V_ab (0 deg)
p2 = (p1[0] - L * 0.5, p1[1] + L * math.sqrt(3) / 2)   # tip of V_bc (-120 deg; SVG y down)
s += arrow(*p0, *p1, BLUE) + arrow(*p1, *p2, BLUE)
# V_ca dashed shaft (obtained, not a winding) + head
ang = math.atan2(p0[1] - p2[1], p0[0] - p2[0])
s += f'<path d="M{p2[0]:.1f} {p2[1]:.1f} L{p0[0] - 9 * math.cos(ang):.1f} {p0[1] - 9 * math.sin(ang):.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += arrow(p0[0] - 12 * math.cos(ang), p0[1] - 12 * math.sin(ang), *p0, BLUE)
s += end_group()
s += ctext(BLUE, (p0[0] + p1[0]) / 2, oy - 12, [("v", "V"), ("vsub", "ab"), ("n", " = 220∠0° V")], anchor="middle")
s += ctext(BLUE, (p1[0] + p2[0]) / 2 + 14, (p1[1] + p2[1]) / 2 + 4, [("v", "V"), ("vsub", "bc"), ("n", " = 220∠−120° V")])
s += ctext(BLUE, (p0[0] + p2[0]) / 2 - 14, (p0[1] + p2[1]) / 2 + 4, [("v", "V"), ("vsub", "ca"), ("n", " = 220∠120° V")], anchor="end")
s += text(W / 2, 330, [("t", "實線：兩台繞組提供；虛線："), ("v", "V"), ("vsub", "ca"), ("n", " = −("), ("v", "V"), ("vsub", "ab"), ("n", " + "), ("v", "V"), ("vsub", "bc"), ("n", ")"), ("t", " 由 KVL 補出")], anchor="middle")
s += text(W / 2, 356, [("t", "三相量首尾相接成閉合正三角形（大小相等、互差 "), ("n", "120°"), ("t", "）")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-114-06-1-phasor.svg'
out.write_text(s); print(out.name, len(s))
