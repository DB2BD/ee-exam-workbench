"""EE-105-04-3 fig 1: per-phase equivalent circuit of the wound-rotor induction motor referred to the stator,
external rotor resistance R_ext' in series with R_2' (both divided by s); R_c neglected.
Dashed line a-b: everything to the left is replaced by the Thevenin equivalent V_th, R_th + jX_th."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext

W, H = 700, 340; YT, YB = 80, 240; XS, XA, XR = 70, 330, 640
s = header(W, H)
s += line(XS, YT, XS, 140) + ac_source(XS, 160, r=20) + line(XS, 180, XS, YB)
s += line(XS, YT, 100, YT) + resistor(100, YT, 165, YT) + line(165, YT, 190, YT)
s += coil(190, YT, 270, YT, turns=4) + line(270, YT, XA, YT)
s += line(XA, YT, XA, 120) + coil(XA, 120, XA, 200, turns=4).replace('rotate(90.00)', 'rotate(90.00) scale(1 -1)') + line(XA, 200, XA, YB)
s += line(XA, YT, 400, YT) + coil(400, YT, 480, YT, turns=4) + line(480, YT, 510, YT)
s += resistor(510, YT, 590, YT) + line(590, YT, XR, YT)
s += line(XR, YT, XR, 120) + resistor(XR, 120, XR, 200) + line(XR, 200, XR, YB)
s += line(XS, YB, XR, YB)
s += dot(XA, YT) + dot(XA, YB)
s += f'<path d="M365 46 L365 {YB + 16}" stroke-dasharray="5 4" stroke-width="1"/>\n'
s += arrow(108, YT - 16, 158, YT - 16, color=RED)
s += arrow(408, YT + 24, 470, YT + 24, color=RED)
s += end_group()
s += text(XS - 28, 152, [("n", "+")], anchor="middle") + text(XS - 28, 182, [("n", "−")], anchor="middle")
s += ttext(XS + 28, 166, [("v", "V"), ("sub", "1")], color=BLUE)
s += text(132, YT + 28, [("v", "R"), ("sub", "1")], anchor="middle")
s += text(230, 54, [("v", "jX"), ("sub", "1")], anchor="middle")
s += ttext(132, YT - 24, [("v", "I"), ("sub", "1")], anchor="middle", color=RED)
s += text(XA - 22, 166, [("v", "jX"), ("vsub", "m")], anchor="end")
s += text(440, 54, [("v", "jX"), ("sub", "2"), ("n", "′")], anchor="middle")
s += text(550, 54, [("v", "R"), ("sub", "2"), ("n", "′/"), ("v", "s")], anchor="middle")
s += text(XR + 12, 156, [("v", "R"), ("vsub", "ext"), ("n", "′/"), ("v", "s")])
s += ttext(440, YT + 48, [("v", "I"), ("sub", "2"), ("n", "′")], anchor="middle", color=RED)
s += text(XA - 8, YT - 8, [("v", "a")], anchor="end") + text(XA - 8, YB + 20, [("v", "b")], anchor="end")
s += text(200, YB + 50, [("t", "左側化為戴維寧等效 "), ("v", "V"), ("vsub", "th"), ("t", "、"), ("v", "R"), ("vsub", "th"), ("n", " + "), ("v", "jX"), ("vsub", "th")], anchor="middle")
s += text(520, YB + 50, [("t", "轉子（換算至定子側）")], anchor="middle")
s += text(520, YB + 74, [("t", "外接電阻經滑環串入")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-105-04-3-equivalent-circuit.svg'
out.write_text(s)
print(out.name, len(s))
