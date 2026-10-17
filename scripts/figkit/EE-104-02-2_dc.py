"""EE-104-02-2: dc bias circuit (all capacitors open, so R_s, V_s and R_L are cut off).

I_CC enters the collector node and splits into I_C (into the collector) and I_B (through R_B to the base);
the emitter carries I_E = I_C + I_B = I_CC through R_E."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

BX, BY = 340, 200                       # base bar centre
XRB = 220
W, H = 600, 420
s = header(W, H)
sym, (xc, yc), (xe, ye) = npn(BX, BY, lead=24)
s += sym
YCN = 120                                # collector node row
s += terminal(xc, 30) + isrc(xc, 33.5, xc, YCN) + line(xc, YCN, xc, yc) + dot(xc, YCN)
s += line(XRB, YCN, xc, YCN) + resistor(XRB, YCN, XRB, BY, zigs=6, lead=10) + line(XRB, BY, BX, BY) + dot(XRB, BY)
s += resistor(xe, ye, xe, ye + 80, zigs=6, lead=10) + line(xe, ye + 80, xe, ye + 100) + ground(xe, ye + 100)
# currents
s += red_arrow(xc + 26, 50, xc + 26, 96)            # I_CC
s += red_arrow(xc + 14, 132, xc + 14, 166)          # I_C
s += red_arrow(XRB - 22, 136, XRB - 22, 178)        # I_B (C -> B through R_B)
s += red_arrow(xe + 26, ye + 14, xe + 26, ye + 62)  # I_E
s += end_group()
t = []
t.append(text(xc + 12, 26, [("n", "+5 V")]))
t.append(ctext(xc + 36, 80, [("v", "I"), ("vsub", "CC"), ("n", " = 0.5 mA")]))
t.append(ctext(xc + 24, 156, [("v", "I"), ("vsub", "C"), ("n", " = "), ("v", "β"), ("v", "I"), ("vsub", "B")]))
t.append(ctext(XRB - 30, 164, [("v", "I"), ("vsub", "B")], anchor="end"))
t.append(text(XRB + 14, 152, [("v", "R"), ("vsub", "B")]))
t.append(text(XRB + 14, 172, [("n", "100 kΩ")]))
t.append(ctext(xe + 36, ye + 44, [("v", "I"), ("vsub", "E"), ("n", " = "), ("v", "I"), ("vsub", "C"), ("n", " + "), ("v", "I"), ("vsub", "B")]))
t.append(text(xe - 14, ye + 36, [("v", "R"), ("vsub", "E")], anchor="end"))
t.append(text(xe - 14, ye + 56, [("n", "1 kΩ")], anchor="end"))
t.append(btext(xc - 8, YCN - 10, [("v", "V"), ("vsub", "C")], anchor="end"))
t.append(btext(XRB - 10, BY + 22, [("v", "V"), ("vsub", "B")], anchor="end"))
t.append(btext(xe + 10, ye + 4, [("v", "V"), ("vsub", "E")]))
t.append(text(BX - 6, BY + 34, [("t", "主動區")], anchor="end"))
t.append(text(20, 400, [("t", "直流時 "), ("v", "C"), ("vsub", "B"), ("t", "、"), ("v", "C"), ("vsub", "C"), ("sub", "1"), ("t", "、"),
                        ("v", "C"), ("vsub", "C"), ("sub", "2"), ("t", " 開路："), ("v", "R"), ("vsub", "s"), ("t", "、"), ("v", "V"), ("vsub", "s"),
                        ("t", "、"), ("v", "R"), ("vsub", "L"), ("t", " 不影響偏壓")]))
s += ''.join(t) + footer()
write('EE-104-02-2-dc.svg', s)
