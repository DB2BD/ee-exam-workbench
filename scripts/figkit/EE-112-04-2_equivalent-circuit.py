"""EE-112-04-2 fig 1: approximate equivalent circuit referred to the 13.8 kV side."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def term(x, y): return f'<circle cx="{x}" cy="{y}" r="4" fill="#fff"/>\n'
W, H = 720, 280; YT, YB = 70, 220; XL, XC, XM, XR = 70, 170, 290, 640
s = header(W, H)
s += line(XL + 4, YT, 400, YT) + line(XL + 4, YB, XR - 4, YB)
s += term(XL, YT) + term(XL, YB) + term(XR, YT) + term(XR, YB)
s += resistor(XC, YT, XC, YB, zigs=8, lead=40)                 # Rc
s += line(XM, YT, XM, 112) + coil(XM, 112, XM, 178, turns=5) + line(XM, 178, XM, YB)   # Xm
s += dot(XC, YT) + dot(XC, YB) + dot(XM, YT) + dot(XM, YB)
s += resistor(400, YT, 470, YT)                                # Req
s += line(470, YT, 500, YT) + coil(500, YT, 580, YT, turns=5)  # Xeq
s += line(580, YT, XR - 4, YT)
s += arrow(592, YT - 16, 630, YT - 16, color=RED)
s += end_group()
s += ctext(BLUE, XL - 14, YT + 30, [("n", "+")], anchor="middle")
s += ctext(BLUE, XL - 14, 150, [("v", "V"), ("sub", "1"), ("n", "′")], anchor="middle")
s += ctext(BLUE, XL - 14, YB - 18, [("n", "−")], anchor="middle")
s += text(XC + 14, 140, [("v", "R"), ("vsub", "c")])
s += text(XC + 14, 160, [("n", "2097.36 Ω")])
s += text(XM + 16, 140, [("v", "jX"), ("vsub", "m")])
s += text(XM + 16, 160, [("v", "j"), ("n", "688.35 Ω")])
s += text(435, YT - 20, [("v", "R"), ("vsub", "eq"), ("n", " = 0.38088 Ω")], anchor="middle")
s += text(540, YT + 34, [("v", "jX"), ("vsub", "eq"), ("n", " = "), ("v", "j"), ("n", "1.9044 Ω")], anchor="middle")
s += ctext(RED, 611, YT - 26, [("v", "I")], anchor="middle")
s += ctext(BLUE, XR + 14, YT + 30, [("n", "+")], anchor="middle")
s += ctext(BLUE, XR + 14, 150, [("v", "V"), ("sub", "2")], anchor="middle")
s += ctext(BLUE, XR + 14, YB - 18, [("n", "−")], anchor="middle")
s += text(XR + 14, YB + 26, [("t", "負載")], anchor="middle")
s += text(230, YB + 26, [("t", "激磁支路（開路試驗）")], anchor="middle")
s += text(490, YB + 26, [("t", "串聯支路（標么值 × "), ("v", "Z"), ("vsub", "b"), ("t", "）")], anchor="middle")
s += text(360, YB + 52, [("t", "全部參數參照低壓側 13.8 kV")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-112-04-2-equivalent-circuit.svg'), 'w').write(s)
print(len(s))
