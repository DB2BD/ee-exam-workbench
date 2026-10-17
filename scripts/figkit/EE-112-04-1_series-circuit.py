"""EE-112-04-1 fig 2: electric circuit, 60 ohm in series with the inductor (L = 36.56 mH, X_L = 13.783 ohm)
across 220 V, 60 Hz; i is the reference current from terminal a through the resistor into the winding."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext

W, H = 560, 260; XS, XL, YT, YB = 110, 400, 60, 200
s = header(W, H)
s += ac_source(XS, 130, r=22)
s += line(XS, 108, XS, YT) + line(XS, YT, 180, YT) + resistor(180, YT, 290, YT) + line(290, YT, XL, YT)
s += line(XL, YT, XL, 95) + coil(XL, 95, XL, 165, turns=4) + line(XL, 165, XL, YB)
s += line(XL, YB, XS, YB) + line(XS, YB, XS, 152)
s += arrow(310, YT - 16, 370, YT - 16, color=RED)
s += end_group()
s += text(XS - 14, 106, [("n", "+")], anchor="end") + text(XS - 14, 166, [("n", "−")], anchor="end")
s += ttext(XS - 30, 128, [("v", "V"), ("n", " = 220 V")], anchor="end", color=BLUE)
s += ttext(XS - 30, 150, [("n", "60 Hz")], anchor="end", color=BLUE)
s += text(235, YT - 18, [("v", "R"), ("n", " = 60 Ω")], anchor="middle")
s += ttext(340, YT - 26, [("v", "i")], anchor="middle", color=RED)
s += text(XL + 18, 118, [("v", "L"), ("n", " = 36.56 mH")])
s += text(XL + 18, 144, [("v", "X"), ("vsub", "L"), ("n", " = 13.783 Ω")])
s += text(280, 240, [("v", "Z"), ("n", " = 60 + "), ("v", "j"), ("n", "13.783 Ω")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-112-04-1-series-circuit.svg'
out.write_text(s)
print(out.name, len(s))
