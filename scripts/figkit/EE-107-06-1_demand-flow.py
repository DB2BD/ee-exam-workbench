import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 320; s = header(W, H); labels = ''
users = "ABCD"; xs = [12, 132, 252, 372]; bw, bh = 114, 34
rows = [  # y_box, sub, values, sum label, arrow label, final
    (30, "max", ["42.50", "26.40", "79.20", "43.20"], [("n", "Σ"), ("v", "P"), ("vsub", "max,i"), ("n", " = 191.30 kW")],
     [("n", "÷ "), ("v", "F"), ("vsub", "d"), ("n", " = 1.5")], [("v", "P"), ("vsub", "max"), ("n", " = 127.53 kW")]),
    (170, "avg", ["19.125", "10.56", "39.60", "15.12"], [("n", "Σ"), ("v", "P"), ("vsub", "avg,i"), ("n", " = 84.405 kW")],
     [("t", "直接相加")], [("v", "P"), ("vsub", "avg"), ("n", " = 84.405 kW")]),
]
for yb, sub, vals, sl, al, fin in rows:
    yb2 = yb + bh + 30
    for x, u, v in zip(xs, users, vals):
        s += f'<rect x="{x}" y="{yb}" width="{bw}" height="{bh}"/>\n' + line(x + bw / 2, yb + bh, x + bw / 2, yb2)
        labels += text(x + bw / 2, yb + 23, [("v", "P"), ("vsub", f"{sub},{u}"), ("n", f" = {v}")], anchor="middle")
    s += line(xs[0] + bw / 2, yb2, 488, yb2) + arrow(488, yb2, 560, yb2, BLUE)
    s += f'<rect x="565" y="{yb2 - 20}" width="145" height="40" stroke="{BLUE}"/>\n'
    labels += text(245, yb2 + 22, sl, anchor="middle") + ctext(BLUE, 520, yb2 - 10, al, anchor="middle")
    labels += ctext(BLUE, 637, yb2 + 6, fin, anchor="middle")
s += end_group() + labels
s += text(360, 300, [("v", "LF"), ("n", " = "), ("v", "P"), ("vsub", "avg"), ("n", " / "), ("v", "P"), ("vsub", "max"), ("n", " = 84.405 / 127.53 = 0.6618"), ("t", "；"), ("v", "E"), ("n", " = 84.405 × 24 = 2025.72 kWh")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-107-06-1-demand-flow.svg'), 'w').write(s)
print(len(s))
