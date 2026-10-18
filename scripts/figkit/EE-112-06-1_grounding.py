"""EE-112-06-1 system grounding vs equipment grounding (TN-S style, low-resistance grounded neutral).

Left: transformer secondary Y; neutral point N -> R_N -> main grounding bus G -> system electrode.
Right: motor frame -> PE (equipment grounding conductor) -> G; local equipment electrode on the PE.
N and PE meet only at G (source end). Red: ground-fault current I_g for an L3-to-frame fault
(L3 -> frame -> PE -> G -> R_N -> N -> winding), symbol only.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 420; s = header(W, H); lab = ''
ys = {"L1": 90, "L2": 130, "L3": 170}
xst, xc, xf0, xf1, yf0, yf1 = 90, 150, 500, 620, 66, 196
# Y secondary: three windings, left ends tied (star point), neutral drops to node N
for name, y in ys.items():
    s += line(xst, y, xst + 8, y) + coil(xst + 8, y, xc, y, turns=3, r=5) + line(xc, y, xf0, y)
    s += line(xf0, y, 549, y)
    lab += text(xc + 26, y - 8, [("n", name)])
s += line(xst, ys["L1"], xst, 222) + dot(xst, ys["L1"]) + dot(xst, ys["L2"]) + dot(xst, ys["L3"]) + dot(xst, 222)
# neutral conductor to single-phase loads (terminal)
s += line(xst, 222, 440, 222) + '<circle cx="444" cy="222" r="4" fill="#fff"/>\n'
# system grounding: N -> R_N -> grounding bus G -> electrode
s += resistor(xst, 232, xst, 282) + line(xst, 222, xst, 232) + line(xst, 282, xst, 310) + dot(xst, 310)
s += line(xst, 310, xst, 330) + ground(xst, 330)
# motor frame and motor
s += f'<rect x="{xf0}" y="{yf0}" width="{xf1 - xf0}" height="{yf1 - yf0}" stroke-width="2.2"/>\n'
s += '<circle cx="575" cy="130" r="26"/>\n'
s += line(549, 90, 556, 112) + line(549, 170, 556, 148)
# PE: frame -> G, plus a local equipment electrode
s += line(560, yf1, 560, 310) + dot(560, yf1) + dot(560, 310) + line(xst, 310, 650, 310)
s += line(650, 310, 650, 330) + ground(650, 330)
# insulation breakdown L3 -> frame (red zigzag)
s += f'<path d="M520 170 L527 178 L517 184 L524 {yf1}" stroke="{RED}" stroke-width="1.8"/>\n'
# fault-current arrows (reference path of I_g)
s += arrow(250, 158, 320, 158, RED) + arrow(574, 222, 574, 278, RED) + arrow(420, 324, 340, 324, RED)
s += arrow(xst - 14, 276, xst - 14, 240, RED)
# category boxes (blue, dashed)
s += f'<path d="M40 216 L210 216 L210 352 L40 352 Z" stroke="{BLUE}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s += f'<path d="M480 48 L680 48 L680 352 L480 352 Z" stroke="{BLUE}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s += end_group()
lab += text(xst - 10, 60, [("t", "變壓器二次 Y 接")])
lab += text(xst - 10, 226, [("n", "N")], anchor="end")
lab += text(300, 214, [("n", "N"), ("t", " 中性線（至單相負載）")], anchor="middle")
lab += text(xst + 14, 263, [("v", "R"), ("vsub", "N")])
lab += text(xst + 12, 302, [("v", "G")])
lab += text(118, 345, [("t", "系統接地極")], anchor="start")
lab += ctext(BLUE, 125, 210, [("t", "系統接地")], anchor="middle").replace('y="210"', 'y="240"').replace('x="125"', 'x="150"')
lab += text(575, 136, [("n", "M")], anchor="middle")
lab += text(560, 214, [("t", "外殼")], anchor="end").replace('x="560"', 'x="552"')
lab += text(330, 302, [("n", "PE"), ("t", "（設備接地導線）")], anchor="middle")
lab += text(610, 345, [("t", "設備接地極")], anchor="end")
lab += ctext(BLUE, 580, 42, [("t", "設備接地")], anchor="middle")
lab += ctext(RED, 494, 190, [("t", "碰殼")], anchor="end")
lab += ctext(RED, 285, 150, [("v", "I"), ("vsub", "g")], anchor="middle") + ctext(RED, 590, 256, [("v", "I"), ("vsub", "g")])
lab += ctext(RED, 380, 344, [("v", "I"), ("vsub", "g")], anchor="middle") + ctext(RED, xst - 20, 262, [("v", "I"), ("vsub", "g")], anchor="end")
lab += text(W / 2, 400, [("n", "N"), ("t", " 與 "), ("n", "PE"), ("t", " 只在電源端接地母排 "), ("v", "G"), ("t", " 單點相連；碰殼電流沿紅箭頭回到中性點")], anchor="middle")
s += lab + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-112-06-1-grounding.svg'), 'w').write(s)
print(len(s))
