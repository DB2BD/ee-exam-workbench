"""EE-112-04-5 fig 1: shunt motor, KCL split I_L = I_f + I_a (reference directions as in the note)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 640, 300; YT, YB = 80, 260; XA, XN, XT = 150, 380, 540
s = header(W, H)
s += f'<circle cx="{XA}" cy="170" r="26"/>\n'                 # armature
s += line(XA, 144, XA, YT) + line(XA, YT, 200, YT)
s += resistor(200, YT, 280, YT)                                # Ra
s += line(280, YT, XT - 4, YT)
s += f'<circle cx="{XT}" cy="{YT}" r="4" fill="#fff"/>\n'
s += line(XN, YT, XN, 100) + resistor(XN, 100, XN, 160)       # Rf
s += line(XN, 160, XN, 172) + coil(XN, 172, XN, 236, turns=4)  # Lf
s += line(XN, 236, XN, YB)
s += line(XA, 196, XA, YB) + line(XA, YB, XT - 4, YB)
s += f'<circle cx="{XT}" cy="{YB}" r="4" fill="#fff"/>\n'
s += dot(XN, YT) + dot(XN, YB)
s += arrow(510, YT - 16, 450, YT - 16, color=RED)              # I_L into node
s += arrow(340, YT - 16, 290, YT - 16, color=RED)              # I_a toward armature
s += arrow(XN + 26, 150, XN + 26, 200, color=RED)              # I_f down the field branch
s += end_group()
s += text(XA - 34, 160, [("n", "+")], anchor="middle")
s += text(XA - 34, 196, [("n", "−")], anchor="middle")
s += text(XA - 46, 176, [("v", "E"), ("vsub", "A")], anchor="end")
s += text(240, YT + 30, [("v", "R"), ("vsub", "a"), ("n", " = 0.12 Ω")], anchor="middle")
s += text(XN - 16, 136, [("v", "R"), ("vsub", "f"), ("n", " = 50 Ω")], anchor="end")
s += text(XN - 16, 210, [("v", "L"), ("vsub", "f")], anchor="end")
s += ctext(RED, 480, YT - 28, [("v", "I"), ("vsub", "L"), ("n", " = 150 A")], anchor="middle")
s += ctext(RED, 315, YT - 28, [("v", "I"), ("vsub", "a"), ("n", " = 145 A")], anchor="middle")
s += ctext(RED, XN + 40, 180, [("v", "I"), ("vsub", "f"), ("n", " = 5 A")])
s += ctext(BLUE, XT, YT + 32, [("n", "+")], anchor="middle")
s += ctext(BLUE, XT, 176, [("v", "V"), ("vsub", "t"), ("n", " = 250 V")], anchor="middle")
s += ctext(BLUE, XT, YB - 18, [("n", "−")], anchor="middle")
s += text(320, 292, [("t", "節點 KCL："), ("v", "I"), ("vsub", "L"), ("n", " = "), ("v", "I"), ("vsub", "f"), ("n", " + "), ("v", "I"), ("vsub", "a")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-112-04-5-shunt-circuit.svg'), 'w').write(s)
print(len(s))
