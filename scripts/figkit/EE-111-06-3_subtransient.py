import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 370; s = header(W, H); y, g, sy = 90, 290, 240
xs = [100, 250, 400, 630]
s += busbar(80, 670, y)
for x in xs:
    s += dot(x, y) + ac_source(x, sy) + line(x, sy + 14, x, g)
# breaker A on generator branch
s += line(100, y, 100, 112) + '<rect x="91" y="112" width="18" height="18" fill="#fff"/>\n' + coil(100, 130, 100, 226)
s += coil(250, y, 250, 226)
s += line(400, y, 400, 120) + dot(400, 120) + coil(400, 120, 400, 226) + coil(630, y, 630, 226)
s += f'<path d="M400 120 L490 120 L490 {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n' + dot(490, g)
s += line(80, g, 670, g)
for x in xs:
    s += arrow(x - 16, 210, x - 16, 140, RED)
s += arrow(502, 170, 502, 250, RED)
s += end_group()
s += text(140, 72, [("n", "3.3 kV "), ("t", "母線")], anchor="start")
s += text(118, 126, [("n", "A")])
s += text(114, 172, [("v", "j"), ("n", "0.20")]) + text(114, 192, [("t", "（"), ("v", "X"), ("vsub", "G"), ("n", "+"), ("v", "X"), ("vsub", "T"), ("t", "）")])
for x in (250, 400, 630):
    s += text(x + 14, 180, [("v", "j"), ("n", "0.625")])
s += text(410, 114, [("v", "F")])
s += ctext(RED, 78, 140, [("v", "I"), ("vsub", "G"), ("n", " = 5")], anchor="end")
for x in (250, 400, 630):
    s += ctext(RED, x - 22, 140, [("v", "I"), ("vsub", "M"), ("n", " = 1.6")], anchor="end")
s += ctext(RED, 514, 220, [("v", "I"), ("vsub", "F"), ("n", "″ = 9.8")])
for x, nm in zip(xs, ["G＋T", "M", "M", "M"]):
    s += text(x, 312, [("t", nm)], anchor="middle")
for x in xs:
    s += text(x + 18, sy + 24, [("n", "1∠0°")])
s += text(370, 340, [("t", "單位 pu；"), ("v", "I"), ("vsub", "F"), ("n", "″ = 5 + 3×1.6 = 9.8"), ("t", "；A 只流過 "), ("v", "I"), ("vsub", "G"), ("n", " = 5")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-111-06-3-subtransient.svg'), 'w').write(s)
print(len(s))
