import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 330; s = header(W, H); y, g = 110, 260
s += line(60, g, 60, 204) + ac_source(60, 190) + line(60, 176, 60, y)
s += coil(60, y, 170, y, turns=4) + line(170, y, 210, y)
s += f'<rect x="210" y="102" width="26" height="16" fill="#fff"/>\n' + line(236, y, 290, y)
s += f'<circle cx="270" cy="{y}" r="7"/>\n'                                    # CT on the HV wire
s += line(270, 117, 270, 176) + '<rect x="252" y="176" width="36" height="20" fill="#fff"/>\n'
s += coil(290, y, 420, y, turns=5) + line(420, y, 520, y) + dot(520, y)
s += f'<path d="M520 {y} L520 {g}" stroke="{RED}" stroke-dasharray="6 4"/>\n' + dot(520, g)
s += line(60, g, 520, g)
s += f'<path d="M355 122 L355 240" stroke="{BLUE}" stroke-width="1" stroke-dasharray="3 4"/>\n'
s += arrow(150, 134, 200, 134, RED) + arrow(440, 134, 506, 134, RED)
s += end_group()
s += text(115, 72, [("v", "X"), ("sub", "src")], anchor="middle") + text(115, 94, [("v", "j"), ("n", "0.0015")], anchor="middle")
s += text(223, 94, [("n", "CB")], anchor="middle") + text(270, 94, [("n", "CT")], anchor="middle")
s += text(270, 192, [("n", "CO")], anchor="middle")
s += text(355, 72, [("v", "X"), ("sub", "T")], anchor="middle") + text(355, 94, [("v", "j"), ("n", "0.057")], anchor="middle")
s += text(520, 94, [("v", "F")], anchor="middle")
s += text(80, 195, [("n", "1 pu")])
s += ctext(BLUE, 340, 232, [("n", "11.4 kV "), ("t", "側")], anchor="end") + ctext(BLUE, 370, 232, [("n", "380 V "), ("t", "側")], anchor="start")
s += ctext(RED, 160, 160, [("v", "I"), ("sub", "F,H"), ("n", " = 649.29 A")], anchor="middle")
s += ctext(RED, 508, 160, [("v", "I"), ("vsub", "F"), ("n", " = 19.48 kA")], anchor="end")
s += text(320, 290, [("v", "S"), ("vsub", "b"), ("n", " = 750 kVA"), ("t", "；故障電流經 CT 時要用高壓側值 "), ("v", "I"), ("sub", "F,H")], anchor="middle")
s += text(320, 314, [("v", "I"), ("sub", "F,H"), ("n", " = "), ("v", "I"), ("vsub", "F"), ("n", " × 380/11 400")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-112-06-4-reactance.svg'), 'w').write(s)
print(len(s))
