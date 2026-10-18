"""EE-105-02-2: finite-gain op-amp model: v_S - R_1 - node v_n - R_F - output; op-amp input draws no current,
v_p = 0 (no current in R_x), output = controlled voltage source A_o(v_p - v_n) = -A_o v_n to ground.
Reference currents i_s (through R_1) and i_f (through R_F) both left -> right, as in the official figure."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 640, 320
YT, YB, YU = 150, 265, 85
XS, XA, XB, XN, XO, XT = 50, 90, 190, 240, 450, 560
s = header(W, H)
s += vsrc(XS, YT, XS, YB) + line(XS, YT, XA, YT) + resistor(XA, YT, XB, YT, zigs=6, lead=14) + line(XB, YT, XN, YT)
s += line(XN, YT, XN, YU) + line(XN, YU, 300, YU) + resistor(300, YU, 400, YU, zigs=6, lead=14) + line(400, YU, XO, YU) + line(XO, YU, XO, YT)
cy = (YT + YB) / 2
s += line(XO, YT, XO, cy - 22) + line(XO, cy + 22, XO, YB)
s += f'<path d="M{XO - 22} {cy} L{XO} {cy - 22} L{XO + 22} {cy} L{XO} {cy + 22} Z"/>\n'
s += line(XO - 4, cy - 9, XO + 4, cy - 9) + line(XO, cy - 13, XO, cy - 5) + line(XO - 4, cy + 9, XO + 4, cy + 9)
s += line(XO, YT, XT - 3.5, YT) + terminal(XT, YT) + line(XS, YB, XT - 3.5, YB) + terminal(XT, YB)
s += dot(XN, YT) + dot(XO, YT) + dot(XO, YB) + line(300, YB, 300, YB + 8) + ground(300, YB + 8)
s += red_arrow(XA + 10, YT - 22, XA + 50, YT - 22) + red_arrow(310, YU - 20, 350, YU - 20)
s += end_group()
t = []
t.append(text(10, 24, [("t", "運算放大器以受控電壓源表示（輸入不取電流，"), ("v", "v"), ("vsub", "p"), ("n", " = 0"), ("t", "）")]))
t.append(text(XS - 22, cy + 5, [("v", "v"), ("vsub", "S")], anchor="end"))
t.append(text((XA + XB) / 2, YT + 26, [("v", "R"), ("sub", "1"), ("n", " = 10 kΩ")], anchor="middle"))
t.append(ctext(XA + 20, YT - 30, [("v", "i"), ("vsub", "s")], anchor="middle"))
t.append(text(350, YU + 28, [("v", "R"), ("vsub", "F"), ("n", " = 800 kΩ")], anchor="middle"))
t.append(ctext(330, YU - 28, [("v", "i"), ("vsub", "f")], anchor="middle"))
t.append(polarity(XN + 18, YT + 6, YB - 4, [("v", "v"), ("vsub", "n")]))
t.append(text(XO - 34, cy - 2, [("n", "−"), ("v", "A"), ("vsub", "o"), ("v", "v"), ("vsub", "n")], anchor="end"))
t.append(text(XO - 34, cy + 20, [("v", "A"), ("vsub", "o"), ("n", " = 2×10⁵")], anchor="end"))
t.append(polarity(XT + 2, YT + 10, YB - 4, [("v", "v"), ("vsub", "O")]))
t.append(text(10, 308, [("t", "反相端 KCL："), ("v", "i"), ("vsub", "s"), ("n", " = "), ("v", "i"), ("vsub", "f")]))
s += ''.join(t) + footer()
write('EE-105-02-2-model.svg', s)
