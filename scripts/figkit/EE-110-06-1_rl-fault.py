import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 600, 300; s = header(W, H); t, b = 80, 230; xs, xf, xl = 90, 420, 530
# source branch
s += line(xs, t, xs, 141) + ac_source(xs, 155) + line(xs, 169, xs, b)
# top wire: R then X
s += line(xs, t, 150, t) + resistor(150, t, 240, t) + line(240, t, 280, t)
s += coil(280, t, 360, t, turns=4) + line(360, t, xl, t) + dot(xf, t)
# closed switch (fault) branch
s += line(xf, t, xf, 140) + dot(xf, 140) + line(xf, 140, xf, 170) + dot(xf, 170) + line(xf, 170, xf, b)
# load branch (shorted)
s += line(xl, t, xl, 128) + f'<rect x="{xl - 11}" y="128" width="22" height="54" fill="#fff"/>\n' + line(xl, 182, xl, b)
s += line(xs, b, xl, b) + dot(xf, b) + line(xf, b, xf, b + 14) + ground(xf, b + 14)
# current arrows
s += arrow(102, t - 14, 142, t - 14, RED) + arrow(xf + 14, 100, xf + 14, 200, RED)
s += end_group()
s += ctext(RED, 122, t - 22, [("v", "i"), ("n", "("), ("v", "t"), ("n", ")")], anchor="middle")
s += ctext(RED, xf + 22, 156, [("v", "i"), ("n", "("), ("v", "t"), ("n", ")")])
s += text(195, t + 30, [("v", "R")], anchor="middle")
s += text(320, t + 30, [("v", "X"), ("n", " = "), ("v", "ωL")], anchor="middle")
s += text(xs - 8, 128, [("n", "+")], anchor="end") + text(xs - 8, 192, [("n", "−")], anchor="end")
s += ctext(BLUE, xs - 22, 160, [("v", "v"), ("n", "("), ("v", "t"), ("n", ")")], anchor="end")
s += ctext(BLUE, xs + 22, 270, [("v", "v"), ("n", "("), ("v", "t"), ("n", ") = "), ("v", "V"), ("vsub", "m"), ("n", " sin("), ("v", "ωt"), ("n", " + "), ("v", "α"), ("n", ")")])
s += text(xf - 26, 160, [("n", "S.W."), ("t", " 閉合")], anchor="end")
s += text(xl + 20, 150, [("t", "負載")]) + text(xl + 20, 172, [("t", "被短路")])
s += text(xf, t - 14, [("t", "故障點")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-110-06-1-rl-fault.svg'), 'w').write(s)
print(len(s))
