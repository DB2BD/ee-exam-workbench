"""EE-111-04-3 fig 1: long-shunt cumulative compound generator; I_a = I_L + I_sh (reference directions)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def term(x, y): return f'<circle cx="{x}" cy="{y}" r="4" fill="#fff"/>\n'
W, H = 640, 320; YT, YB = 60, 270; XA, XN, XT = 150, 440, 580
s = header(W, H)
s += f'<circle cx="{XA}" cy="200" r="24"/>\n'
s += line(XA, 176, XA, 150) + resistor(XA, 150, XA, 90, zigs=6, lead=8) + line(XA, 90, XA, YT)   # Ra
s += line(XA, YT, 250, YT) + coil(250, YT, 350, YT, turns=5) + line(350, YT, XT - 4, YT)        # series field
s += line(XN, YT, XN, 90) + resistor(XN, 90, XN, 150, zigs=6, lead=8)                            # Rfc
s += arrow(XN - 22, 140, XN + 22, 100)                                                           # variable mark
s += line(XN, 150, XN, 166) + coil(XN, 166, XN, 230, turns=4) + line(XN, 230, XN, YB)            # Rfw
s += line(XA, 224, XA, YB) + line(XA, YB, XT - 4, YB)
s += term(XT, YT) + term(XT, YB) + dot(XN, YT) + dot(XN, YB)
s += arrow(180, YT - 16, 230, YT - 16, color=RED)          # I_a
s += arrow(490, YT - 16, 540, YT - 16, color=RED)          # I_L
s += arrow(XN + 30, 170, XN + 30, 220, color=RED)          # I_sh
s += end_group()
s += text(XA - 32, 192, [("n", "+")], anchor="middle") + text(XA - 32, 222, [("n", "−")], anchor="middle")
s += text(XA - 44, 206, [("v", "E"), ("vsub", "a")], anchor="end")
s += text(XA + 16, 124, [("v", "R"), ("vsub", "a"), ("n", " = 0.1 Ω")])
s += text(300, YT + 32, [("v", "R"), ("vsub", "sr"), ("n", " = 0.04 Ω")], anchor="middle")
s += text(300, YT + 52, [("t", "串激 "), ("v", "N"), ("vsub", "s")], anchor="middle")
s += text(XN - 26, 124, [("v", "R"), ("vsub", "fc")], anchor="end")
s += text(XN - 16, 196, [("v", "R"), ("vsub", "fw"), ("n", " = 150 Ω")], anchor="end")
s += text(XN - 16, 216, [("t", "並激 "), ("v", "N"), ("vsub", "f"), ("n", " = 1200")], anchor="end")
s += ctext(RED, 205, YT - 26, [("v", "I"), ("vsub", "a")], anchor="middle")
s += ctext(RED, 515, YT - 26, [("v", "I"), ("vsub", "L")], anchor="middle")
s += ctext(RED, XN + 42, 200, [("v", "I"), ("vsub", "sh")])
s += ctext(BLUE, XT, YT + 34, [("n", "+")], anchor="middle")
s += ctext(BLUE, XT, 170, [("v", "V"), ("vsub", "t")], anchor="middle")
s += ctext(BLUE, XT, YB - 18, [("n", "−")], anchor="middle")
s += text(W / 2, 304, [("t", "KCL："), ("v", "I"), ("vsub", "a"), ("n", " = "), ("v", "I"), ("vsub", "L"), ("n", " + "), ("v", "I"), ("vsub", "sh"),
                       ("t", "；KVL："), ("v", "E"), ("vsub", "a"), ("n", " = "), ("v", "V"), ("vsub", "t"), ("n", " + 0.14"), ("v", "I"), ("vsub", "a")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-3-long-shunt.svg'), 'w').write(s)
print(len(s))
