import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
# Percentage-differential characteristic: operate quantity |I1 - I2| vs restraint (|I1| + |I2|)/2,
# trip region above the slope-K line (plus a minimum pickup). Symbolic only: the exam gives no settings.
W, H = 560, 380
ox, oy, xm, ym = 90, 320, 520, 40
pick = 40                                   # minimum pickup height (px)
s = header(W, H)
# slope line through origin, floor at the pickup level
xk = ox + pick / 0.45
s += (f'<path d="M{ox} {oy - pick} L{xk:.1f} {oy - pick} L{xm} {oy - 0.45 * (xm - ox):.1f} L{xm} {ym} L{ox} {ym} Z" '
      f'fill="{FILL_RED}" stroke="none"/>\n')
s += arrow(ox, oy, xm + 10, oy) + arrow(ox, oy, ox, ym - 10)
s += f'<path d="M{ox} {oy} L{xk:.1f} {oy - pick}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{ox} {oy - pick} L{xk:.1f} {oy - pick} L{xm} {oy - 0.45 * (xm - ox):.1f}" stroke-width="2.2"/>\n'
s += end_group()
s += text(xm + 6, oy + 28, [("t", "抑制量 "), ("n", "("), ("n", "|"), ("v", "I"), ("sub", "1"), ("n", "| + |"), ("v", "I"), ("sub", "2"), ("n", "|)/2")], anchor="end")
s += text(ox - 8, ym - 16, [("t", "動作量 "), ("n", "|"), ("v", "I"), ("sub", "1"), ("n", " − "), ("v", "I"), ("sub", "2"), ("n", "|")], anchor="start")
s += text(200, 110, [("t", "跳脫區（區內故障）")], anchor="middle")
s += text(400, 290, [("t", "不動作區（正常、區外故障）")], anchor="middle")
s += text(400, 150, [("t", "斜率 "), ("v", "K")], anchor="middle")
s += text(ox + 4, oy - pick - 8, [("t", "最小動作電流")])
s += text(ox - 8, oy + 18, [("n", "0")], anchor="end")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-4-characteristic.svg'), 'w').write(s)
print(len(s))
