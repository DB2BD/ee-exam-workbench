import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def xfmr(cx, cy, r=14):
    return f'<circle cx="{cx - 8}" cy="{cy}" r="{r}"/>\n<circle cx="{cx + 8}" cy="{cy}" r="{r}"/>\n'
W, H = 640, 300
XB = 460                       # system bus
s = header(W, H)
for Y in (90, 210):
    s += ac_source(80, Y, r=18) + line(98, Y, 208, Y) + xfmr(230, Y) + line(252, Y, XB, Y)
s += f'<path d="M{XB} 50 L{XB} 250" stroke-width="5"/>\n'
s += f'<path d="M{XB} 150 L540 150 L540 178" stroke="{RED}"/>\n' + ground(540, 178)
s += end_group()
for Y, n in ((90, "1"), (210, "2")):
    s += text(80, Y - 28, [("v", "G"), ("sub", n)], anchor="middle")
    s += text(230, Y - 24, [("v", "T"), ("sub", n)], anchor="middle")
s += text(80, 128, [("n", "550 MVA, 20 kV")], anchor="middle")
s += text(80, 150, [("v", "X"), ("vsub", "d"), ("n", "″ = 0.25")], anchor="middle")
s += text(230, 128, [("n", "550 MVA, 20/345 kV")], anchor="middle")
s += text(230, 150, [("v", "X"), ("vsub", "T"), ("n", " = 0.15")], anchor="middle")
s += text(XB, 38, [("n", "345 kV "), ("t", "系統匯流排")], anchor="middle")
s += ctext(RED, 630, 138, [("v", "F"), ("t", "（三相短路）")], anchor="end")
s += text(360, 80, [("v", "P"), ("vsub", "i"), ("n", " = 440 MW")], anchor="middle")
s += text(360, 200, [("v", "P"), ("vsub", "i"), ("n", " = 440 MW")], anchor="middle")
s += text(320, 286, [("t", "兩部相同機組各經升壓變壓器並聯至系統匯流排")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-3-one-line.svg'), 'w').write(s)
print(len(s))
