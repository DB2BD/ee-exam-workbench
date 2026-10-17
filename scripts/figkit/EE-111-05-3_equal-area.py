import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Equal-area criterion, fault at generator terminal: Pe = 0 during fault (A1 = rectangle under Pm),
# post-fault curve = pre-fault 2.5 sin(delta).  delta_cr shown as a symbol only (derived later).
W, H = 640, 384
ox, oy = 80, 300
X = lambda deg: ox + deg * 2.7            # 0..180 deg -> 80..566 px
Y = lambda p: oy - p * 96                 # 0..2.6 pu -> 300..50 px
PMAX, PM = 2.5, 1.0
d0 = math.degrees(math.asin(PM / PMAX)); dm = 180 - d0; dcr = 89.375
s = header(W, H)
# A1: rectangle between Pm and the delta axis (Pe = 0 during the fault)
s += f'<path d="M{X(d0):.1f} {oy} L{X(d0):.1f} {Y(PM):.1f} L{X(dcr):.1f} {Y(PM):.1f} L{X(dcr):.1f} {oy} Z" fill="{FILL_RED}" stroke="none"/>\n'
# A2: between the post-fault curve and Pm, dcr..dmax
pts = [(X(d), Y(PMAX * math.sin(math.radians(d)))) for d in [dcr + (dm - dcr) * k / 60 for k in range(61)]]
pts.append((X(dcr), Y(PM)))
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f' Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(ox, oy, X(190), oy) + arrow(ox, oy, ox, 36)
curve = ' L'.join(f'{X(d):.1f} {Y(PMAX * math.sin(math.radians(d))):.1f}' for d in range(0, 181, 2))
s += f'<path d="M{curve}"/>\n'
s += f'<path d="M{ox} {Y(PM):.1f} L{X(182):.1f} {Y(PM):.1f}" stroke="{BLUE}"/>\n'
s += f'<path d="M{ox} {Y(PMAX):.1f} L{X(90):.1f} {Y(PMAX):.1f}" stroke-width="1" stroke-dasharray="4 3"/>\n'
for d in (d0, dcr, dm):
    s += f'<path d="M{X(d):.1f} {oy} L{X(d):.1f} {Y(PM) if d != dcr else Y(PMAX * math.sin(math.radians(d))):.1f}" stroke-width="1" stroke-dasharray="4 3"/>\n'
s += dot(X(d0), Y(PM)) + dot(X(dm), Y(PM))
s += end_group()
s += text(X(190) + 4, oy + 5, [("v", "δ")])
s += text(ox - 8, 30, [("v", "P"), ("n", " (pu)")], anchor="start")
s += text(ox - 8, Y(PMAX) + 5, [("n", "2.5")], anchor="end")
s += text(ox - 8, Y(PM) + 5, [("n", "1.0")], anchor="end", color=BLUE)
s += text(X(118), Y(2.38), [("v", "P"), ("vsub", "e"), ("n", " = 2.5 sin "), ("v", "δ")], anchor="start")
s += text(X(118), Y(2.38) + 20, [("t", "（故障前／清除後）")], anchor="start")
s += text(X(182), Y(PM) - 8, [("v", "P"), ("vsub", "m"), ("n", " = 1.0")], anchor="end", color=BLUE)
s += text(X(56), Y(0.45), [("v", "A"), ("sub", "1")], anchor="middle")
s += text(X(112), Y(1.55), [("v", "A"), ("sub", "2")], anchor="middle")
s += text(X(56), oy - 8, [("t", "故障中 "), ("v", "P"), ("vsub", "e"), ("n", " = 0")], anchor="middle")
s += text(X(d0), oy + 22, [("v", "δ"), ("sub", "0")], anchor="middle")
s += text(X(d0), oy + 42, [("n", "23.5782°")], anchor="middle")
s += text(X(dcr), oy + 22, [("v", "δ"), ("vsub", "cr")], anchor="middle")
s += text(X(dm), oy + 22, [("v", "δ"), ("sub", "max")], anchor="middle")
s += text(X(dm), oy + 42, [("n", "156.4218°")], anchor="middle")
s += text(320, 372, [("t", "臨界情形："), ("v", "A"), ("sub", "1"), ("n", " = "), ("v", "A"), ("sub", "2")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-111-05-3-equal-area.svg')
out.write_text(s)
print(len(s))
