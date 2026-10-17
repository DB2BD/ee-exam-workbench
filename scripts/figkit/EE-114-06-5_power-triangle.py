import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 364; s = header(W, H); base = 270; k = 0.75
cases = [  # x0, P, Q_old, Q_new, Q_allow, n, title
    (40, 200, 123.95, 23.95, 65.74, 2, [("t", "8–17 時以外")]),
    (350, 300, 225.97, 75.97, 98.61, 3, [("t", "8–17 時")]),
]
labels = ''
for x0, P, Qo, Qn, Qa, n, title in cases:
    xe = x0 + P * k; yo = base - Qo * k; yn = base - Qn * k
    s += line(x0, base, xe, base) + line(xe, base, xe, yo) + line(x0, base, xe, yo)
    s += f'<path d="M{x0} {base} L{xe:.1f} {yn:.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
    ya = base - Qa * k
    s += f'<path d="M{x0} {base} L{xe:.1f} {ya:.1f}" stroke-width="1" stroke-dasharray="2 3"/>\n' + line(xe - 6, ya, xe, ya)
    s += arrow(xe + 8, yo, xe + 8, yn, BLUE) + dot(xe, yn) + dot(xe, yo)
    labels += text((x0 + xe) / 2, base + 22, [("v", "P"), ("n", f" = {P} kW")], anchor="middle")
    labels += text(xe + 16, yo + 6, [("v", "Q"), ("vsub", "old"), ("n", f" = {Qo:.2f}")])
    labels += ctext(BLUE, xe + 16, (yo + yn) / 2 + 2, [("n", f"−{50 * n} kvar")])
    labels += ctext(BLUE, xe + 16, (yo + yn) / 2 + 22, [("t", f"（{n} 組）")])
    labels += text(xe + 16, yn + 6, [("v", "Q"), ("n", f"′ = {Qn:.2f}")])
    labels += text((x0 + xe) / 2, 46, title, anchor="middle")
s += end_group() + labels
s += text(350, 350, [("t", "點線：PF = 0.95 邊界（"), ("v", "Q"), ("vsub", "allow"), ("n", " = 65.74、98.61 kvar"), ("t", "），"), ("v", "Q"), ("n", "′"), ("t", " 須在其下方")], anchor="middle")
s += text(350, 322, [("t", "黑：原負載功率三角形；藍虛線：投入電容器後。電容器只減 "), ("v", "Q"), ("t", "（kvar）、不改變 "), ("v", "P"), ("t", "（kW）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-114-06-5-power-triangle.svg'), 'w').write(s)
print(len(s))
