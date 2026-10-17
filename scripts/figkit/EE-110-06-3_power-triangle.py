import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 620, 400; s = header(W, H)
X0, Y0, k = 70, 320, 0.25
X = lambda p: X0 + p * k
Y = lambda q: Y0 - q * k
P, Q, Qa = 950, 600 + math.sqrt(17500), math.sqrt(97500)
# rating circle 1000 kVA
s += f'<path d="M{X(1000):.1f} {Y0} A{1000*k:.1f} {1000*k:.1f} 0 0 0 {X0} {Y(1000):.1f}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += arrow(X0, Y0, X(1250), Y0) + arrow(X0, Y0, X0, 40)
s += f'<path d="M{X(800):.1f} {Y0} L{X(800):.1f} {Y(1000):.1f}" stroke-width="1" stroke-dasharray="3 3"/>\n'
s += line(X0, Y0, X(P), Y(Q)) + line(X(P), Y0, X(P), Y(Q))
s += f'<path d="M{X0} {Y0} L{X(P):.1f} {Y(Qa):.1f}" stroke="{BLUE}"/>\n'
s += arrow(X(P) + 10, Y(Q), X(P) + 10, Y(Qa), RED)
s += dot(X(P), Y(Q)) + dot(X(P), Y(Qa)) + dot(X(P), Y0)
s += end_group()
s += text(X(1250), Y0 + 24, [("v", "P"), ("n", " (kW)")], anchor="end")
s += text(X0 + 8, 46, [("v", "Q"), ("n", " (kvar)")])
s += text(X(P), Y0 + 24, [("n", "950")], anchor="middle") + text(X(800) - 4, Y0 + 24, [("n", "800")], anchor="end")
s += text(X(800) - 6, Y(1000) + 4, [("t", "原動機 "), ("n", "800 kW")], anchor="end")
s += text(X(P) + 20, Y(Q) + 5, [("v", "Q"), ("n", " = 600 + 132.3 = 732.3")])
s += ctext(RED, X(P) + 20, (Y(Q) + Y(Qa)) / 2 + 5, [("v", "Q"), ("vsub", "c"), ("n", " = 420.04 kvar")])
s += ctext(BLUE, X(P) + 20, Y(Qa) + 5, [("v", "Q"), ("vsub", "allow"), ("n", " = √97500 = 312.2")])
s += ctext(BLUE, X(1000) + 14, Y(120), [("n", "|"), ("v", "S"), ("n", "| = 1000 kVA "), ("t", "額定圓")])
s += text(310, 388, [("t", "電容只把工作點垂直下移（"), ("v", "P"), ("t", " 不變），移到 1000 kVA 額定圓上為止")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-110-06-3-power-triangle.svg'), 'w').write(s)
print(len(s))
