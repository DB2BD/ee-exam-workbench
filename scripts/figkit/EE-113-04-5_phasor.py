import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 420; ox, oy = 150, 200; k = 6.0          # 6 px per ampere
def tip(mag, deg): r = math.radians(deg); return ox + k * mag * math.cos(r), oy - k * mag * math.sin(r)
s = header(W, H)
s += arrow(ox, oy, 560, oy, color=BLUE)
m = tip(33.71, -60.55); a0 = tip(27.74, -33.69); ac = tip(29.03, 29.45)
s += arrow(ox, oy, *m, color=RED) + arrow(ox, oy, *ac, color=RED)
s += f'<path d="M{ox} {oy} L{a0[0]:.1f} {a0[1]:.1f}" stroke="{RED}" stroke-dasharray="6 4"/>\n'
s += arrow(a0[0] - 0.01 * (a0[0] - ox), a0[1] - 0.01 * (a0[1] - oy), *a0, color=RED)
def arc(r, d1, d2):
    p1 = (ox + r * math.cos(math.radians(d1)), oy - r * math.sin(math.radians(d1)))
    p2 = (ox + r * math.cos(math.radians(d2)), oy - r * math.sin(math.radians(d2)))
    return f'<path d="M{p1[0]:.1f} {p1[1]:.1f} A{r} {r} 0 0 0 {p2[0]:.1f} {p2[1]:.1f}" stroke-width="1.2"/>\n'
s += arc(48, -60.55, 0) + arc(110, -60.55, -33.69)
# right-angle mark between I_m and I_aC
u = (math.cos(math.radians(-60.55)), -math.sin(math.radians(-60.55))); w = (math.cos(math.radians(29.45)), -math.sin(math.radians(29.45)))
c = 14
s += f'<path d="M{ox+c*u[0]:.1f} {oy+c*u[1]:.1f} L{ox+c*u[0]+c*w[0]:.1f} {oy+c*u[1]+c*w[1]:.1f} L{ox+c*w[0]:.1f} {oy+c*w[1]:.1f}" stroke-width="1"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(ox - 8, oy + 6, [("v", "O")], anchor="end")
s += ctext(BLUE, 560, oy - 10, [("v", "V"), ("n", " = 240∠0° V")], anchor="end")
s += ctext(RED, m[0] + 8, m[1] + 18, [("v", "I"), ("vsub", "m"), ("n", " = 33.71∠−60.55° A")])
s += ctext(RED, a0[0] + 8, a0[1] + 4, [("v", "I"), ("vsub", "a"), ("sub", "0"), ("n", " = 27.74∠−33.69° A"), ("t", "（無電容）")])
s += ctext(RED, ac[0] + 8, ac[1] - 4, [("v", "I"), ("vsub", "aC"), ("n", " = 29.03∠29.45° A"), ("t", "（有電容）")])
s += text(ox + 54, oy + 26, [("n", "60.55°")])
s += text(ox + 112, oy + 52, [("v", "α"), ("sub", "0"), ("n", " = 26.86°")])
s += text(ox + 58, oy - 10, [("v", "α"), ("vsub", "C"), ("n", " = 90°")])
s += text(30, 30, [("t", "比例：電流 1 A = 6 px（"), ("v", "V"), ("t", " 只標方向）")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-113-04-5-phasor.svg'), 'w').write(s)
print(len(s))
