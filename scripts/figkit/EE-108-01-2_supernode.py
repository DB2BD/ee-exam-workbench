"""EE-108-01-2: node voltages V1, v, V3, V4, the supernode {V1, v, V3} and the reference directions of i1 and v2."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *


def dep_isrc(x1, y1, x2, y2, h=17):
    """Dependent current source (diamond) with an arrow pointing (x1, y1) -> (x2, y2)."""
    L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - h * ux, cy - h * uy) + line(cx + h * ux, cy + h * uy, x2, y2)
    s += f'<path d="M{cx - h:.1f} {cy:.1f} L{cx:.1f} {cy - h:.1f} L{cx + h:.1f} {cy:.1f} L{cx:.1f} {cy + h:.1f} Z"/>\n'
    return s + arrow(cx - 9 * ux, cy - 9 * uy, cx + 9 * ux, cy + 9 * uy)


W, H = 680, 410
XA, XB, XC, XT = 150, 310, 470, 600
YTOP, YM, YB = 80, 210, 360
s = header(W, H)
s += f'<ellipse cx="{(XA + XC) / 2}" cy="{YM}" rx="{(XC - XA) / 2 + 40}" ry="44" fill="{FILL_BLUE}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += line(XA, YTOP, 260, YTOP) + isrc(360, YTOP, 260, YTOP) + line(360, YTOP, XT, YTOP)
s += line(XA, YTOP, XA, YM) + resistor(XA, YM, XA, YB, zigs=6, lead=50)
s += vsrc(XA, YM, XB, YM)
s += resistor(XB, YM, XB, YB, zigs=6, lead=50)
s += dep_vsrc(XC, YM, XB, YM)
s += resistor(XC, YTOP, XC, YM, zigs=6, lead=36)
s += dep_isrc(XC, YB, XC, YM)
s += resistor(XT, YTOP, XT, YB, zigs=6, lead=100)
s += line(XA, YB, XT, YB)
for x, y in ((XA, YM), (XB, YM), (XC, YM), (XC, YTOP), (XB, YB), (XC, YB)):
    s += dot(x, y)
s += tint_arrow(250, YB + 14, 200, YB + 14)                              # i1 along the bottom wire, to the left
s += end_group()
s += ttext(20, 30, [("t", "超節點（虛線）：6 V 與 4"), ("v", "i"), ("sub", "1"), ("t", " 兩電壓源把 "), ("v", "V"), ("sub", "1"),
                    ("t", "、"), ("v", "v"), ("t", "、"), ("v", "V"), ("sub", "3"), ("t", " 連成一體；底線為參考地")], color=BLUE)
s += text(310, YTOP - 26, [("n", "6 A")], anchor="middle")
s += text((XA + XB) / 2, YM - 28, [("n", "6 V")], anchor="middle")
s += text((XB + XC) / 2, YM - 28, [("n", "4"), ("v", "i"), ("sub", "1")], anchor="middle")
s += ttext(XA + 8, YM + 20, [("v", "V"), ("sub", "1")], color=BLUE)
s += ttext(XC - 10, YM + 20, [("v", "V"), ("sub", "3")], anchor="end", color=BLUE)
s += ttext(XC + 10, YTOP - 10, [("v", "V"), ("sub", "4")], color=BLUE)
s += text(XA + 16, 296, [("n", "1 Ω")])
s += ttext(XA - 16, 262, [("n", "+")], anchor="end", color=BLUE) + ttext(XA - 16, 296, [("v", "v"), ("sub", "1")], anchor="end", color=BLUE)
s += ttext(XA - 16, 336, [("n", "−")], anchor="end", color=BLUE)
s += text(XB + 16, 296, [("n", "4 Ω")])
s += ttext(XB - 16, 262, [("n", "+")], anchor="end", color=BLUE) + ttext(XB - 16, 296, [("v", "v")], anchor="end", color=BLUE)
s += ttext(XB - 16, 336, [("n", "−")], anchor="end", color=BLUE)
s += text(XC - 16, 150, [("n", "1 Ω")], anchor="end")
s += ttext(XC + 16, 112, [("n", "+")], color=BLUE) + ttext(XC + 16, 150, [("v", "v"), ("sub", "2")], color=BLUE)
s += ttext(XC + 16, 184, [("n", "−")], color=BLUE)
s += text(XC + 26, 292, [("n", "(3/2)"), ("v", "v"), ("sub", "2")])
s += text(XT + 16, 226, [("n", "2 Ω")])
s += ttext(225, YB + 38, [("v", "i"), ("sub", "1")], anchor="middle", color=RED)
s += footer()
write('EE-108-01-2-supernode.svg', s)
