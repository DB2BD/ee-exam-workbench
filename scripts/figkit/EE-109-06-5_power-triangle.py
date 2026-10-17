import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 356; s = header(W, H); base = 268; k = 0.28
cases = [  # x0, P, Q_old, Q_new, names, title
    (20, 914.52, 685.89, 442.92, ("1", "target"), [("t", "滿載（200 A）")]),
    (470, 342.95, 457.26, 214.29, ("2", "2′"), [("t", "輕載（100 A）")]),
]
labels = ''
for x0, P, Qo, Qn, (a, bname), title in cases:
    xe = x0 + P * k; yo = base - Qo * k; yn = base - Qn * k
    s += line(x0, base, xe, base) + line(xe, base, xe, yo) + line(x0, base, xe, yo)
    s += f'<path d="M{x0} {base} L{xe:.1f} {yn:.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
    s += arrow(xe + 8, yo, xe + 8, yn, BLUE) + dot(xe, yn) + dot(xe, yo)
    labels += text((x0 + xe) / 2, base + 24, [("v", "P"), ("sub", a), ("n", f" = {P:.2f} kW")], anchor="middle")
    labels += text(xe + 16, yo + 6, [("v", "Q"), ("sub", a), ("n", f" = {Qo:.2f} kvar")])
    labels += ctext(BLUE, xe + 16, (yo + yn) / 2 + 6, [("v", "Q"), ("vsub", "c"), ("n", " = 242.97 kvar")])
    if bname == "target":
        labels += text(xe + 16, yn + 6, [("v", "Q"), ("sub", "target"), ("n", f" = {Qn:.2f} kvar")])
    else:
        labels += text(xe + 16, yn + 6, [("v", "Q"), ("sub", "2"), ("n", f"′ = {Qn:.2f} kvar")])
    labels += text(x0, 40, title, anchor="start")
s += end_group() + labels
s += text(148, base + 48, [("n", "PF 0.8 → 0.9")], anchor="middle")
s += text(518, base + 48, [("n", "PF 0.6 → "), ("n", "PF"), ("sub", "2"), ("n", "′ = 0.8481")], anchor="middle")
s += text(360, 346, [("t", "黑：原負載功率三角形；藍虛線：並聯電容器後（只減 "), ("v", "Q"), ("t", "、不改 "), ("v", "P"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-109-06-5-power-triangle.svg'), 'w').write(s)
print(len(s))
