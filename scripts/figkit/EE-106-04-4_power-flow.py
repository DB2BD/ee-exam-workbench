"""EE-106-04-4 fig 1: induction-motor power flow P_in -> P_ag -> P_conv -> P_out with the given losses
taken off at each stage (only given loss values are numbered; stage powers are symbols)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

W, H = 700, 250; Y = 96
XS = [40, 250, 440, 660]            # P_in, P_ag, P_conv, P_out
XL = [145, 345, 550]                # loss take-off points
s = header(W, H)
s += arrow(XS[0], Y, XS[3], Y, color=BLUE)
for x in XS[1:3]:
    s += f'<path d="M{x} {Y - 12} L{x} {Y + 12}" stroke="{BLUE}" stroke-width="2"/>\n'
for x in XL:
    s += arrow(x, Y, x, 156)
s += end_group()
s += text(XS[0], Y - 40, [("t", "電源輸入")])
s += text(XS[0], Y - 16, [("v", "P"), ("vsub", "in")])
s += text(XS[1], Y - 40, [("t", "氣隙功率")], anchor="middle")
s += text(XS[1], Y - 16, [("v", "P"), ("vsub", "ag")], anchor="middle")
s += text(XS[2], Y - 40, [("t", "電磁轉換功率")], anchor="middle")
s += text(XS[2], Y - 16, [("v", "P"), ("vsub", "conv")], anchor="middle")
s += text(XS[3], Y - 40, [("t", "軸輸出")], anchor="end")
s += text(XS[3], Y - 16, [("v", "P"), ("vsub", "out")], anchor="end")
s += text(XL[0], 178, [("t", "定子銅損 "), ("v", "P"), ("vsub", "cu"), ("sub", "1"), ("n", " = 850 W")], anchor="middle")
s += text(XL[0], 202, [("t", "鐵損 "), ("v", "P"), ("vsub", "core"), ("n", " = 450 W")], anchor="middle")
s += text(XL[1], 178, [("t", "轉子銅損")], anchor="middle")
s += text(XL[1], 202, [("v", "P"), ("vsub", "cu"), ("sub", "2"), ("n", " = 1050 W")], anchor="middle")
s += text(XL[2] + 10, 178, [("t", "旋轉損")], anchor="middle")
s += text(XL[2] + 10, 202, [("v", "P"), ("vsub", "rot"), ("n", " = 500 W")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-106-04-4-power-flow.svg'
out.write_text(s)
print(out.name, len(s))
