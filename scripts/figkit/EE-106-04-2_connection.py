"""EE-106-04-2 fig 1: 2400/240 V two-winding transformer reconnected as a 2400 V -> 2640 V step-up
autotransformer.  The 2400 V winding is the common winding (source across it); the 240 V winding is
the series winding, connected aiding on top of it; the load sits across both (2640 V).
Reference directions: I_in from the source into the tap, I_out from the tap up through the series
winding to the load, I_c down through the common winding (KCL at the tap: I_in = I_out + I_c)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import terminal, ttext

W, H = 700, 360
XS, XW, XO = 200, 360, 560           # source, winding stack, load terminals
YT, YM, YB = 60, 160, 280            # top (series winding top), tap, bottom (common line)
s = header(W, H)
# winding stack: series winding YT..YM, common winding YM..YB
s += line(XW, YT, XW, 76) + coil(XW, 76, XW, 144, turns=4, r=8.5) + line(XW, 144, XW, YM)
s += line(XW, YM, XW, 178) + coil(XW, 178, XW, 262, turns=5, r=8.4) + line(XW, 262, XW, YB)
s += line(XW + 26, 70, XW + 26, 270) + line(XW + 32, 70, XW + 32, 270)       # iron core
s += dot(XW - 14, 80) + dot(XW - 14, 182)                                      # polarity dots (top ends)
# source across the common winding
s += ac_source(XS, 220, r=22)
s += line(XS, 198, XS, YM) + line(XS, YM, XW, YM) + dot(XW, YM)
s += line(XS, 242, XS, YB) + line(XS, YB, XO, YB) + dot(XW, YB)
# load across both windings
s += line(XW, YT, XO, YT)
s += terminal(XO, YT) + terminal(XO, YB)
s += resistor(XO + 40, YT + 40, XO + 40, YB - 40) + line(XO, YT, XO + 40, YT) + line(XO + 40, YT, XO + 40, YT + 40)
s += line(XO, YB, XO + 40, YB) + line(XO + 40, YB, XO + 40, YB - 40)
# current reference arrows
s += arrow(245, YM - 14, 315, YM - 14, color=RED)
s += arrow(430, YT - 14, 500, YT - 14, color=RED)
s += arrow(XW - 40, 196, XW - 40, 244, color=RED)
s += end_group()
s += ttext(280, YM - 24, [("v", "I"), ("vsub", "in")], anchor="middle", color=RED)
s += ttext(465, YT - 24, [("v", "I"), ("vsub", "out")], anchor="middle", color=RED)
s += ttext(XW - 48, 226, [("v", "I"), ("vsub", "c")], anchor="end", color=RED)
s += text(XW + 44, 104, [("t", "串聯繞組")])
s += ttext(XW + 44, 126, [("v", "V"), ("vsub", "se"), ("n", " = 240 V")], color=BLUE)
s += text(XW + 44, 214, [("t", "公共繞組")])
s += ttext(XW + 44, 236, [("v", "V"), ("vsub", "c"), ("n", " = 2400 V")], color=BLUE)
s += text(XS - 30, 206, [("n", "+")], anchor="end") + text(XS - 30, 248, [("n", "−")], anchor="end")
s += ttext(XS - 30, 228, [("v", "V"), ("vsub", "in"), ("n", " = 2400 V")], anchor="end", color=BLUE)
s += text(XO + 56, YT + 34, [("n", "+")]) + text(XO + 56, YB - 24, [("n", "−")])
s += ttext(XO + 56, 160, [("v", "V"), ("vsub", "out")], color=BLUE)
s += ttext(XO + 56, 182, [("n", "= 2640 V")], color=BLUE)
s += text(XO + 56, 204, [("t", "負載")])
s += text(350, 322, [("t", "兩繞組打點端同在上方（加極性串接）："), ("n", "2400 + 240 = 2640 V")], anchor="middle")
s += text(350, 346, [("t", "電源跨公共繞組，負載跨兩繞組（升壓）")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-106-04-2-connection.svg'
out.write_text(s)
print(out.name, len(s))
