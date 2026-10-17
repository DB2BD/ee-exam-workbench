import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 560, 346; s = header(W, H); base = 260; k = 0.22; x0 = 60
P, Q1, Q2 = 780, 911.92, 256.37
xe = x0 + P * k; yo = base - Q1 * k; yn = base - Q2 * k
s += line(x0, base, xe, base) + line(xe, base, xe, yo) + line(x0, base, xe, yo)
s += f'<path d="M{x0} {base} L{xe:.1f} {yn:.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += arrow(xe + 8, yo, xe + 8, yn, BLUE) + dot(xe, yn) + dot(xe, yo)
s += end_group()
s += text((x0 + xe) / 2, base + 22, [("v", "P"), ("n", " = 780 kW")], anchor="middle")
s += text(xe + 16, yo + 6, [("v", "Q"), ("sub", "1"), ("n", " = 911.92 kvar")])
s += ctext(BLUE, xe + 16, (yo + yn) / 2 + 6, [("v", "Q"), ("vsub", "c"), ("n", " = 655.55 kvar")])
s += text(xe + 16, yn + 6, [("v", "Q"), ("sub", "2"), ("n", " = 256.37 kvar")])
s += text(x0 + 46, base - 8, [("v", "ϕ"), ("sub", "2")]) + text(x0 + 30, base - 30, [("v", "ϕ"), ("sub", "1")])
s += text(280, 310, [("n", "cos "), ("v", "ϕ"), ("sub", "1"), ("n", " = 0.65 → cos "), ("v", "ϕ"), ("sub", "2"), ("n", " = 0.95"), ("t", "（落後）")], anchor="middle")
s += text(280, 334, [("t", "黑：原負載；藍虛線：並聯電容器後")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-107-06-5-power-triangle.svg'), 'w').write(s)
print(len(s))
