import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 360; s = header(W, H); lab = ''
xt, xe, ytop, yg = 150, 440, 70, 262
s += coil(xt, 80, xt, 160, turns=5) + line(xt, ytop, xt, 80) + line(xt, 160, xt, 180)
s += resistor(xt, 180, xt, 240) + line(xt, 240, xt, 250) + ground(xt, 250)
s += line(xt, ytop, xe, ytop) + line(xe, ytop, xe, 130) + dot(xe, 130)
s += '<rect x="380" y="100" width="120" height="90"/>\n'
s += f'<path d="M{xe} 132 L{xe - 8} 150 L{xe + 6} 158 L{xe} 188" stroke="{RED}"/>\n'
s += line(xe, 190, xe, 200) + resistor(xe, 200, xe, 240) + line(xe, 240, xe, 250) + ground(xe, 250)
s += f'<path d="M{xt} {yg + 16} L{xe} {yg + 16}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s += arrow(250, ytop - 12, 320, ytop - 12, RED) + arrow(xe - 16, 204, xe - 16, 238, RED) + arrow(340, yg + 30, 260, yg + 30, RED)
# person touching the frame
s += '<circle cx="570" cy="112" r="10"/>\n' + line(570, 122, 570, 190) + line(570, 142, 500, 142)
s += line(570, 190, 556, 248) + line(570, 190, 584, 248) + line(540, 250, 610, 250)
s += end_group()
lab += text(xt - 14, 125, [("t", "變壓器二次")], anchor="end") + text(xt + 14, 215, [("v", "R"), ("vsub", "n")])
lab += text(440, 92, [("t", "設備外殼")], anchor="middle") + ctext(RED, 372, 160, [("t", "絕緣破壞")], anchor="end")
lab += text(xe - 24, 225, [("v", "R"), ("vsub", "g")], anchor="end")
lab += ctext(BLUE, xe + 14, 210, [("n", "+")]) + ctext(BLUE, xe + 14, 246, [("n", "−")])
lab += ctext(BLUE, xe + 28, 232, [("v", "V"), ("n", " = "), ("v", "I"), ("vsub", "g"), ("v", "R"), ("vsub", "g")])
lab += ctext(RED, 285, ytop - 20, [("v", "I"), ("vsub", "g")], anchor="middle") + ctext(RED, 300, yg + 52, [("v", "I"), ("vsub", "g"), ("t", "（經大地回中性點）")], anchor="middle")
lab += text(570, 280, [("t", "人體接觸外殼")], anchor="middle")
lab += text(320, 340, [("t", "降低 "), ("v", "R"), ("vsub", "g"), ("t", " 限制接觸電壓；迴路阻抗低則 "), ("v", "I"), ("vsub", "g"), ("t", " 大、保護快速動作")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-106-06-1-grounding.svg'), 'w').write(s)
print(len(s))
