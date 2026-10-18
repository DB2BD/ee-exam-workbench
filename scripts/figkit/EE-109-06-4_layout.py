"""EE-109-06-4 lighting layout plan: 60 m x 30 m plant, 11 x 4 two-lamp fixtures (N = 44).

s_x = 60/11 = 5.45 m, s_y = 30/4 = 7.5 m, wall margins s_x/2 = 2.73 m, s_y/2 = 3.75 m (values as in note 配置方式).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dim_h(x1, x2, y, tick=6):
    return line(x1, y, x2, y) + line(x1, y - tick, x1, y + tick) + line(x2, y - tick, x2, y + tick)
def dim_v(x, y1, y2, tick=6):
    return line(x, y1, x, y2) + line(x - tick, y1, x + tick, y1) + line(x - tick, y2, x + tick, y2)

k = 8.5                                   # px per metre
x0, y0 = 120, 80; Wr, Hr = 60 * k, 30 * k
W, H = 720, 440; s = header(W, H); lab = ''
s += f'<rect x="{x0}" y="{y0}" width="{Wr}" height="{Hr}" stroke-width="2.2"/>\n'
nx, ny = 11, 4
sx, sy = 60 / nx, 30 / ny
for i in range(nx):
    for j in range(ny):
        cx = x0 + (sx / 2 + i * sx) * k; cy = y0 + (sy / 2 + j * sy) * k
        s += f'<rect x="{cx - 8:.1f}" y="{cy - 8:.1f}" width="16" height="16" fill="{FILL_BLUE}" stroke-width="1"/>\n'
        s += f'<circle cx="{cx - 3.5:.1f}" cy="{cy:.1f}" r="2.2" stroke-width="1"/>\n<circle cx="{cx + 3.5:.1f}" cy="{cy:.1f}" r="2.2" stroke-width="1"/>\n'
ax1 = x0; ax2 = x0 + sx / 2 * k; ax3 = ax2 + sx * k
s += f'<g stroke="{BLUE}">' + dim_h(ax1, ax2, y0 - 22) + dim_h(ax2, ax3, y0 - 22) + '</g>\n'
by1 = y0; by2 = y0 + sy / 2 * k; by3 = by2 + sy * k
s += f'<g stroke="{BLUE}">' + dim_v(x0 - 24, by1, by2) + dim_v(x0 - 24, by2, by3) + '</g>\n'
s += dim_h(x0, x0 + Wr, y0 + Hr + 26) + dim_v(x0 + Wr + 24, y0, y0 + Hr)
s += end_group()
lab += ctext(BLUE, (ax1 + ax2) / 2 - 2, y0 - 32, [("n", "2.73 m")], anchor="end")
lab += ctext(BLUE, (ax2 + ax3) / 2 + 6, y0 - 32, [("v", "s"), ("vsub", "x"), ("n", " = 5.45 m")])
lab += ctext(BLUE, x0 - 32, (by1 + by2) / 2 + 5, [("n", "3.75 m")], anchor="end")
lab += ctext(BLUE, x0 - 32, (by2 + by3) / 2 - 4, [("v", "s"), ("vsub", "y"), ("n", " =")], anchor="end")
lab += ctext(BLUE, x0 - 32, (by2 + by3) / 2 + 16, [("n", "7.5 m")], anchor="end")
lab += text(x0 + Wr / 2, y0 + Hr + 48, [("n", "60 m"), ("t", "（每列 11 具）")], anchor="middle")
lab += text(x0 + Wr + 32, y0 + Hr / 2 - 8, [("n", "30 m")]) + text(x0 + Wr + 32, y0 + Hr / 2 + 14, [("t", "（4 列）")])
lab += text(W / 2, y0 + Hr + 80, [("v", "N"), ("n", " = 4 × 11 = 44"), ("t", " 具（每具 2 燈，"), ("v", "F"), ("n", " = 46000 lm"), ("t", "）；牆邊取半間距")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-109-06-4-layout.svg'
out.write_text(s); print(out.name, len(s))
