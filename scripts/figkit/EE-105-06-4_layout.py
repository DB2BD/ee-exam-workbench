"""EE-105-06-4 lighting layout plan: 30 m x 20 m room, 20 x 11 fixtures (N_actual = 220).

s_x = 30/20 = 1.50 m, s_y = 20/11 = 1.818 m, wall margins s_x/2 = 0.75 m, s_y/2 = 0.909 m (values as in note (二)).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dim_h(x1, x2, y, tick=6):
    return line(x1, y, x2, y) + line(x1, y - tick, x1, y + tick) + line(x2, y - tick, x2, y + tick)
def dim_v(x, y1, y2, tick=6):
    return line(x, y1, x, y2) + line(x - tick, y1, x + tick, y1) + line(x - tick, y2, x + tick, y2)

k = 16                                   # px per metre
x0, y0 = 140, 80; Wr, Hr = 30 * k, 20 * k
W, H = 720, 520; s = header(W, H); lab = ''
s += f'<rect x="{x0}" y="{y0}" width="{Wr}" height="{Hr}" stroke-width="2.2"/>\n'
sx, sy = 30 / 20, 20 / 11
fix = ''
for i in range(20):
    for j in range(11):
        cx = x0 + (sx / 2 + i * sx) * k; cy = y0 + (sy / 2 + j * sy) * k
        fix += f'<rect x="{cx - 9:.1f}" y="{cy - 3:.1f}" width="18" height="6" fill="{FILL_BLUE}" stroke-width="1"/>\n'
s += fix
# dimension lines (blue): top = margin + one spacing, left = margin + one spacing; totals bottom/right
ax1 = x0; ax2 = x0 + sx / 2 * k; ax3 = ax2 + sx * k
s += f'<g stroke="{BLUE}">' + dim_h(ax1, ax2, y0 - 22) + dim_h(ax2, ax3, y0 - 22) + '</g>\n'
by1 = y0; by2 = y0 + sy / 2 * k; by3 = by2 + sy * k
s += f'<g stroke="{BLUE}">' + dim_v(x0 - 24, by1, by2) + dim_v(x0 - 24, by2, by3) + '</g>\n'
s += dim_h(x0, x0 + Wr, y0 + Hr + 26) + dim_v(x0 + Wr + 24, y0, y0 + Hr)
s += end_group()
lab += ctext(BLUE, (ax1 + ax2) / 2, y0 - 32, [("n", "0.75 m")], anchor="end")
lab += ctext(BLUE, (ax2 + ax3) / 2 + 8, y0 - 32, [("v", "s"), ("vsub", "x"), ("n", " = 1.50 m")])
lab += ctext(BLUE, x0 - 32, (by1 + by2) / 2 + 5, [("n", "0.909 m")], anchor="end")
lab += ctext(BLUE, x0 - 32, (by2 + by3) / 2 + 5, [("v", "s"), ("vsub", "y"), ("n", " = 1.818 m")], anchor="end")
lab += text(x0 + Wr / 2, y0 + Hr + 48, [("n", "30 m"), ("t", "（每排 20 具）")], anchor="middle")
lab += text(x0 + Wr + 34, y0 + Hr / 2 - 8, [("n", "20 m")]) + text(x0 + Wr + 34, y0 + Hr / 2 + 14, [("t", "（11 排）")])
lab += text(W / 2, y0 + Hr + 80, [("v", "N"), ("vsub", "actual"), ("n", " = 20 × 11 = 220"), ("t", " 具，每具 "), ("n", "Φ"), ("vsub", "f"), ("n", " = 9000 lm")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-105-06-4-layout.svg'
out.write_text(s); print(out.name, len(s))
