"""EE-111-06-5 low-resistance grounding: 33 kV Y secondary, neutral through R = 18 Ω, phase-a-to-ground fault.

I_R is drawn in its actual (and reference) direction: fault -> earth -> R -> neutral; V_R is taken with + at the
ground end of R so that I_R enters the + terminal (|V_R| = phase voltage when transformer/system impedance is neglected).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 380; s = header(W, H); lab = ''
xs = {"a": 120, "b": 170, "c": 220}; ytop = {"a": 60, "b": 84, "c": 108}
xn, yn, xf, ye = 170, 190, 470, 300
for p, x in xs.items():
    s += coil(x, 130, x, 180, turns=4, r=6) + line(x, 180, x, yn) + line(x, 130, x, ytop[p]) + line(x, ytop[p], 590, ytop[p])
    lab += text(600, ytop[p] + 5, [("v", p)])
s += line(xs["a"], yn, xs["c"], yn) + dot(xn, yn)
s += line(xn, yn, xn, 214) + resistor(xn, 214, xn, 274) + line(xn, 274, xn, ye) + ground(xn, ye)
# fault on phase a
s += dot(xf, ytop["a"]) + f'<path d="M{xf} {ytop["a"]} L{xf} 150 L{xf - 10} 168 L{xf + 10} 184 L{xf} 202 L{xf} {ye}" stroke="{RED}"/>\n' + ground(xf, ye)
s += f'<path d="M{xf} {ye + 20} L{xn} {ye + 20}" stroke-width="1" stroke-dasharray="5 4"/>\n'
s += arrow(300, ytop["a"] - 12, 380, ytop["a"] - 12, RED) + arrow(380, ye + 34, 260, ye + 34, RED) + arrow(xn - 22, 266, xn - 22, 222, RED)
s += end_group()
lab += text(xs["b"], 30, [("t", "主變二次側 Y（33 kV）")], anchor="middle")
lab += text(xn + 18, 240, [("v", "R"), ("n", " = 18 Ω")])
lab += text(xs["c"] + 10, yn + 5, [("t", "中性點")])
lab += ctext(BLUE, xn + 14, 216, [("n", "−")]) + ctext(BLUE, xn + 14, 288, [("n", "+")]) + ctext(BLUE, xn + 18, 264, [("v", "V"), ("vsub", "R")])
lab += ctext(RED, xn - 30, 250, [("v", "I"), ("vsub", "R")], anchor="end")
lab += ctext(RED, 340, ytop["a"] - 20, [("v", "I"), ("vsub", "R")], anchor="middle")
lab += ctext(RED, xf + 16, 176, [("t", "a 相接地故障")])
lab += text(320, ye + 56, [("t", "經大地回中性點")], anchor="middle")
s += lab
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-111-06-5-neutral-resistor.svg'), 'w').write(s)
print(len(s))
