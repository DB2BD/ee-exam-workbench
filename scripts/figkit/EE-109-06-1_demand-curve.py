import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 344; s = header(W, H)
x0, x1, yb, yt = 70, 630, 260, 50
hx = lambda h: x0 + (x1 - x0) * h / 24
# illustrative hourly demand (kW, arbitrary scale 0..100)
p = [48, 56, 60, 58, 50, 40, 34, 38, 55, 66, 72, 75, 60, 70, 82, 78, 72, 68, 62, 58, 50, 44, 50, 52]
py = lambda v: yb - (yb - yt) * v / 100
pk0, pk1 = 9, 22                                      # peak window (illustrative)
s += f'<rect x="{hx(pk0):.1f}" y="{yt}" width="{hx(pk1) - hx(pk0):.1f}" height="{yb - yt}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(x0, yb, x1 + 20, yb) + arrow(x0, yb, x0, yt - 20)
d = ''
for h, v in enumerate(p):
    d += f'{"M" if h == 0 else "L"}{hx(h):.1f} {py(v):.1f} L{hx(h + 1):.1f} {py(v):.1f} '
s += f'<path d="{d}"/>\n'
on = max(v for h, v in enumerate(p) if pk0 <= h < pk1); off = max(v for h, v in enumerate(p) if not pk0 <= h < pk1)
s += f'<path d="M{x0} {py(on):.1f} L{x1} {py(on):.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += f'<path d="M{x0} {py(off):.1f} L{x1} {py(off):.1f}" stroke-dasharray="2 3"/>\n'
hon = next(h for h, v in enumerate(p) if pk0 <= h < pk1 and v == on); hoff = next(h for h, v in enumerate(p) if not pk0 <= h < pk1 and v == off)
s += dot(hx(hon + 0.5), py(on)) + dot(hx(hoff + 0.5), py(off))
s += end_group()
s += text(x0 - 8, yt - 24, [("v", "P"), ("n", "("), ("v", "t"), ("n", ") kW")], anchor="start")
s += text(x1 + 22, yb + 6, [("v", "t"), ("n", " h")])
for h in (0, 6, 12, 18, 24):
    s += text(hx(h), yb + 22, [("n", str(h))], anchor="middle")
s += ctext(BLUE, hx(15.5), yt + 18, [("t", "尖峰時段")], anchor="middle")
s += text(hx(3), yt + 18, [("t", "離峰")], anchor="middle") + text(hx(23), yt + 18, [("t", "離峰")], anchor="middle")
s += ctext(BLUE, x0 - 6, py(on) + 5, [("v", "D"), ("sub", "經常")], anchor="end")
s += text(x0 - 6, py(off) + 5, [("v", "D"), ("sub", "離峰")], anchor="end")
s += text(350, 306, [("t", "階梯代表 15 分鐘平均需量（示意）；各時段取最大值訂該時段契約容量")], anchor="middle")
s += text(350, 330, [("t", "藍底：尖峰時段（時段範圍依當期台電費率表）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-109-06-1-demand-curve.svg'), 'w').write(s)
print(len(s))
