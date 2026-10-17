import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def col(frag, c): return f'<g stroke="{c}">' + frag.replace('fill="#000"', f'fill="{c}"') + '</g>\n'
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 360; s = header(W, H); y, g = 100, 280
# grid source + Xs + XT1
s += line(50, g, 50, 214) + ac_source(50, 200) + line(50, 186, 50, y)
s += coil(50, y, 150, y, turns=4) + coil(150, y, 250, y, turns=4) + line(250, y, 290, y)
# synchronous motor branch
s += dot(290, y) + coil(290, y, 290, 186, turns=4) + ac_source(290, 200) + line(290, 214, 290, g)
# T2, CB, F
s += line(290, y, 320, y) + coil(320, y, 430, y, turns=4) + line(430, y, 460, y)
s += f'<rect x="460" y="92" width="26" height="16" fill="#fff"/>\n' + line(486, y, 530, y) + dot(530, y)
# induction motor branch
s += line(530, y, 630, y) + coil(630, y, 630, 186, turns=4) + ac_source(630, 200) + line(630, 214, 630, g)
s += line(50, g, 630, g)
# fault link and currents (red)
s += f'<path d="M530 {y} L530 {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n' + dot(530, g)
s += arrow(440, 124, 512, 124, RED) + arrow(612, 124, 548, 124, RED) + arrow(546, 180, 546, 236, RED)
s += end_group()
s += text(100, 62, [("t", "電網 "), ("v", "X"), ("sub", "s")], anchor="middle") + text(100, 84, [("v", "j"), ("n", "0.012")], anchor="middle")
s += text(200, 62, [("v", "X"), ("sub", "T1")], anchor="middle") + text(200, 84, [("v", "j"), ("n", "0.05")], anchor="middle")
s += text(290, 62, [("n", "6.6 kV "), ("t", "母線")], anchor="middle")
s += text(302, 140, [("v", "X"), ("sub", "SM"), ("n", "″ = "), ("v", "j"), ("n", "0.41")])
s += text(375, 62, [("v", "X"), ("sub", "T2")], anchor="middle") + text(375, 84, [("v", "j"), ("n", "0.14")], anchor="middle")
s += text(473, 84, [("n", "CB")], anchor="middle") + text(530, 84, [("v", "F")], anchor="middle")
s += text(642, 140, [("v", "X"), ("sub", "IM"), ("n", "″")]) + text(642, 160, [("v", "j"), ("n", "1.50")])
s += text(70, 205, [("n", "1∠0°")]) + text(310, 205, [("n", "SM")]) + text(650, 205, [("n", "IM")])
s += ctext(RED, 476, 150, [("v", "I"), ("sub", "CB"), ("n", " = 18.61 kA")], anchor="middle")
s += ctext(RED, 582, 112, [("v", "I"), ("sub", "IM")], anchor="middle")
s += ctext(RED, 556, 262, [("v", "I"), ("vsub", "F"), ("n", " = 21.02 kA")])
s += text(340, 312, [("t", "參考點：各內電勢 "), ("n", "1∠0°"), ("t", "（電網、SM、IM）接於此；"), ("v", "S"), ("vsub", "b"), ("n", " = 3 MVA")], anchor="middle")
s += text(340, 336, [("t", "CB 只流過上游（電網＋SM 經 T2）電流；IM 倒灌直接進 F")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-113-06-4-reactance.svg'), 'w').write(s)
print(len(s))
