import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
# Equal-area criterion with a reactive fault: fault-on curve P2max sin(delta), post-fault = pre-fault Pmax sin(delta).
# delta_cr is a symbol only (derived in the same sub-question after the figure).
W, H = 640, 384
ox, oy = 80, 300
X = lambda deg: ox + deg * 2.7
Y = lambda p: oy - p * 105
PMAX, P2, PM = 2.222942, 0.246994, 0.8
d0 = math.degrees(math.asin(PM / PMAX)); dm = 180 - d0; dcr = 101.0936
sinp = lambda pm, d: pm * math.sin(math.radians(d))
s = header(W, H)
ds = [d0 + (dcr - d0) * k / 60 for k in range(61)]
pts = [(X(d), Y(PM)) for d in ds] + [(X(d), Y(sinp(P2, d))) for d in reversed(ds)]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f' Z" fill="{FILL_RED}" stroke="none"/>\n'
ds = [dcr + (dm - dcr) * k / 60 for k in range(61)]
pts = [(X(d), Y(sinp(PMAX, d))) for d in ds] + [(X(dcr), Y(PM))]
s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f' Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(ox, oy, X(190), oy) + arrow(ox, oy, ox, 36)
for pm, dash in ((PMAX, ''), (P2, ' stroke-dasharray="7 4"')):
    c = ' L'.join(f'{X(d):.1f} {Y(sinp(pm, d)):.1f}' for d in range(0, 181, 2))
    s += f'<path d="M{c}"{dash}/>\n'
s += f'<path d="M{ox} {Y(PM):.1f} L{X(182):.1f} {Y(PM):.1f}" stroke="{BLUE}"/>\n'
for d, top in ((d0, Y(PM)), (dcr, Y(sinp(PMAX, dcr))), (dm, Y(PM))):
    s += f'<path d="M{X(d):.1f} {oy} L{X(d):.1f} {top:.1f}" stroke-width="1" stroke-dasharray="4 3"/>\n'
s += dot(X(d0), Y(PM)) + dot(X(dm), Y(PM))
s += end_group()
s += text(X(190) + 4, oy + 5, [("v", "δ")])
s += text(ox - 8, 30, [("v", "P"), ("n", " (pu)")], anchor="start")
s += text(ox - 8, Y(PM) + 5, [("n", "0.8")], anchor="end", color=BLUE)
s += text(X(182), Y(PM) - 8, [("v", "P"), ("vsub", "m"), ("n", " = 0.8")], anchor="end", color=BLUE)
s += text(X(112), Y(2.2), [("v", "P"), ("sub", "max"), ("n", " sin "), ("v", "δ"), ("t", "（故障前／復閉後）")], anchor="start")
s += text(X(108), Y(0.36), [("v", "P"), ("sub", "2max"), ("n", " sin "), ("v", "δ"), ("t", "（故障中）")], anchor="start")
s += text(X(62), Y(0.5), [("v", "A"), ("sub", "1")], anchor="middle")
s += text(X(118), Y(1.45), [("v", "A"), ("sub", "2")], anchor="middle")
s += text(X(d0), oy + 22, [("v", "δ"), ("sub", "0")], anchor="middle")
s += text(X(d0), oy + 42, [("n", "21.0930°")], anchor="middle")
s += text(X(dcr), oy + 22, [("v", "δ"), ("vsub", "cr")], anchor="middle")
s += text(X(dm), oy + 22, [("v", "δ"), ("sub", "max")], anchor="middle")
s += text(X(dm), oy + 42, [("n", "158.9070°")], anchor="middle")
s += text(320, 372, [("t", "臨界情形："), ("v", "A"), ("sub", "1"), ("n", " = "), ("v", "A"), ("sub", "2")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-112-05-4-equal-area.svg')
out.write_text(s)
print(len(s))
