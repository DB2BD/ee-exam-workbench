"""EE-114-02-2: open-circuit time constant for C_a (v_s = 0, C_L open).

R_s || R_a = R' from the v_a node to ground; a test source I_x replaces C_a, pushing current into the
v_o node and drawing it from the v_a node (V_x = v_o - v_a, + at v_o); G_m v_a flows from the v_o node
down to ground; R_L from the v_o node to ground."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YB = 110, 290
XA, XGM, XRL = 150, 420, 540

W, H = 680, 400
s = header(W, H)
s += resistor(XA, YT, XA, YB, zigs=6, lead=40) + dot(XA, YT)
s += isrc(XA, YT, XGM, YT)                          # I_x : v_a -> v_o
s += dot(XGM, YT) + dep_isrc(XGM, YT, XGM, YB)      # G_m v_a : down
s += line(XGM, YT, XRL, YT) + dot(XRL, YT) + resistor(XRL, YT, XRL, YB, zigs=6, lead=40)
s += line(XA, YB, XRL, YB) + dot(XGM, YB) + line(340, YB, 340, YB + 10) + ground(340, YB + 10)
s += red_arrow(240, YT - 26, 330, YT - 26)          # I_x reference
s += red_arrow(XRL + 26, 160, XRL + 26, 220)        # current down R_L
s += end_group()
t = []
t.append(text(XA - 12, 196, [("v", "R"), ("n", "′ = "), ("v", "R"), ("vsub", "s"), ("n", " ∥ "), ("v", "R"), ("vsub", "a")], anchor="end"))
t.append(text(XA - 12, 218, [("n", "= 2.50 kΩ")], anchor="end"))
t.append(btext(XA - 6, YT - 12, [("v", "v"), ("vsub", "a")], anchor="end"))
t.append(btext(XGM + 6, YT - 12, [("v", "v"), ("vsub", "o")]))
t.append(ctext(285, YT - 34, [("v", "I"), ("vsub", "x")], anchor="middle"))
t.append(text(285, YT + 40, [("t", "測試源取代 "), ("v", "C"), ("vsub", "a")], anchor="middle"))
t.append(btext(XA + 30, YT + 22, [("n", "−")], anchor="middle"))
t.append(btext(XGM - 30, YT + 22, [("n", "+")], anchor="middle"))
t.append(btext(285, YT + 64, [("v", "V"), ("vsub", "x"), ("n", " = "), ("v", "v"), ("vsub", "o"), ("n", " − "), ("v", "v"), ("vsub", "a")], anchor="middle"))
t.append(text(XGM - 26, 196, [("v", "G"), ("vsub", "m"), ("v", "v"), ("vsub", "a")], anchor="end"))
t.append(text(XGM - 26, 218, [("v", "G"), ("vsub", "m"), ("n", " = 15 mA/V")], anchor="end"))
t.append(text(XRL + 12, 252, [("v", "R"), ("vsub", "L"), ("n", " = 1 kΩ")]))
t.append(ctext(XRL + 34, 196, [("v", "v"), ("vsub", "o"), ("n", "/"), ("v", "R"), ("vsub", "L")]))
t.append(text(20, 348, [("v", "v"), ("vsub", "s"), ("n", " = 0"), ("t", "（短路）；"), ("v", "C"), ("vsub", "L"), ("t", " 開路（不畫）；"),
                        ("v", "v"), ("vsub", "a"), ("t", " 節點："), ("v", "v"), ("vsub", "a"), ("n", " = −"), ("v", "I"), ("vsub", "x"),
                        ("v", "R"), ("n", "′")]))
t.append(text(20, 372, [("v", "v"), ("vsub", "o"), ("t", " 節點 KCL："), ("v", "I"), ("vsub", "x"), ("n", " = "), ("v", "G"), ("vsub", "m"),
                        ("v", "v"), ("vsub", "a"), ("n", " + "), ("v", "v"), ("vsub", "o"), ("n", "/"), ("v", "R"), ("vsub", "L")]))
s += ''.join(t) + footer()
write('EE-114-02-2-octc-ca.svg', s)
