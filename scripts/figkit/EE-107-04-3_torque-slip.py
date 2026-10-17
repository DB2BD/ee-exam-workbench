"""EE-107-04-3 fig 2: T_ind(s) from the Thevenin circuit; stable region 0 < s < s_max, points s = 0.05 and s_max."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
ws = 60 * math.pi
T = lambda s: 3 * 210 ** 2 * (0.8 / s) / ((0.2 + 0.8 / s) ** 2 + 8.0 ** 2) / ws
W, H = 640, 360; X0, Y0 = 80, 300; KX, KY = 1000.0, 5.0
P = lambda s, t: (X0 + KX * s, Y0 - KY * t)
s = header(W, H)
sm = 0.8 / math.hypot(0.2, 8.0)
s += f'<rect x="{X0}" y="70" width="{KX * sm:.1f}" height="{Y0 - 70}" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(X0, Y0, X0 + KX * 0.53, Y0) + arrow(X0, Y0, X0, 50)
s += f'<path d="M{X0 + KX * 0.5:.1f} {Y0} L{X0 + KX * 0.5:.1f} {Y0 - 6}"/>\n'
pts = [P(k / 1000, T(k / 1000)) for k in range(1, 501)]
pts = [(X0, Y0)] + pts
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + '"/>\n'
xm, ym = P(sm, T(sm)); x5, y5 = P(0.05, T(0.05)); s += f'<path d="M{xm:.1f} {ym:.1f} L{xm:.1f} {Y0}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += f'<path d="M{xm:.1f} {ym:.1f} L{X0} {ym:.1f}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += f'<path d="M{x5:.1f} {y5:.1f} L{x5:.1f} {Y0}" stroke-dasharray="3 3" stroke-width="1"/>\n'
s += dot(xm, ym) + dot(x5, y5)
s += line(x5 + 3, y5 + 3, 194, y5 + 44)
s += end_group()
s += text(X0 + KX * 0.53, Y0 + 24, [("v", "s")], anchor="middle")
s += text(X0 + 10, 40, [("v", "T"), ("vsub", "ind"), ("n", " (N·m)")])
s += text(X0, Y0 + 22, [("n", "0")], anchor="middle")
s += text(x5, Y0 + 22, [("n", "0.05")], anchor="middle")
s += text(xm + 8, Y0 + 22, [("v", "s"), ("vsub", "max"), ("n", " ≈ 0.10")])
s += text(X0 + KX * 0.5, Y0 + 22, [("n", "0.5")], anchor="middle")
s += text(X0 + KX * 0.5, Y0 + 44, [("t", "（橫軸只畫到 "), ("v", "s"), ("n", " = 0.5"), ("t", "）")], anchor="end")
s += text(xm + 10, ym - 8, [("v", "T"), ("vsub", "max"), ("n", " = 42.78 N·m")])
s += text(196, y5 + 50, [("v", "T"), ("vsub", "ind"), ("n", " = 34.40 N·m")])
s += text(X0 - 8, ym + 5, [("n", "42.78")], anchor="end")
s += text(X0 + 52, 266, [("t", "穩定")]) + text(X0 + 52, 284, [("t", "運轉區")])
s += text(330, 100, [("v", "s"), ("n", " > "), ("v", "s"), ("vsub", "max"), ("t", "：負載稍增即減速到停")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-107-04-3-torque-slip.svg'), 'w').write(s)
print(len(s))
