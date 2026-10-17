import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 340; s = header(W, H)
X0, Y0 = 90, 270
X = lambda h: X0 + h * 20.5
Y = lambda kw: Y0 - kw * 0.17
dem = [250, 450, 1175, 1025, 600, 250]
# energy area under the demand steps (light blue)
pts = [(X(0), Y0)]
for k, d in enumerate(dem):
    pts += [(X(4 * k), Y(d)), (X(4 * k + 4), Y(d))]
pts += [(X(24), Y0)]
s += '<path d="M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + f' Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += '<path d="M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts[1:-1]) + '" stroke-width="2"/>\n'
for k in range(1, 6):
    s += f'<path d="M{X(4*k):.1f} {Y0} L{X(4*k):.1f} {Y(min(dem[k-1], dem[k])):.1f}" stroke-width="1"/>\n'
s += arrow(X0, Y0, X(25.2), Y0) + arrow(X0, Y0, X0, 40)
for h in range(0, 25, 4):
    s += line(X(h), Y0, X(h), Y0 + 4)
for kw in (250, 625, 1175):
    s += line(X0 - 4, Y(kw), X0, Y(kw))
s += f'<path d="M{X0} {Y(625):.1f} L{X(24):.1f} {Y(625):.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += f'<path d="M{X0} {Y(1175):.1f} L{X(8):.1f} {Y(1175):.1f}" stroke="{RED}" stroke-width="1" stroke-dasharray="3 3"/>\n'
s += end_group()
for h in range(0, 25, 4):
    s += text(X(h), Y0 + 22, [("n", str(h))], anchor="middle")
s += text(X(25.2), Y0 - 10, [("v", "t"), ("n", " (h)")], anchor="end")
s += text(X0 - 8, Y(250) + 5, [("n", "250")], anchor="end") + ctext(BLUE, X0 - 8, Y(625) + 5, [("n", "625")], anchor="end")
s += ctext(RED, X0 - 8, Y(1175) + 5, [("n", "1175")], anchor="end")
s += text(X0 + 6, 38, [("v", "P"), ("n", " (kW)")])
for k, d in enumerate(dem):
    s += text(X(4 * k + 2), Y(d) + (22 if d == 600 else -8), [("n", str(d))], anchor="middle") if d != 1175 else ''
s += ctext(RED, X(10), Y(1175) - 14, [("v", "P"), ("sub", "max"), ("n", " = 1175")], anchor="middle")
s += ctext(BLUE, X(22.3), Y(625) - 8, [("v", "P"), ("sub", "avg"), ("n", " = 625")], anchor="middle")
s += text(320, 324, [("t", "區間需量 = 相鄰累積讀值差 ÷ 4 h；淡藍面積 = 全日電能 "), ("n", "15000 kWh")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-113-06-1-demand.svg'), 'w').write(s)
print(len(s))
