"""EE-108-02-4: the GIC unfolded as a chain X -R- P -2R- N -R- Y -C- Z -R- ground.
Op amp A: + at X, - at N, output Y; op amp B: + at Z, - at N, output P.  Virtual shorts V_N = V_X, V_Z = V_X.
Reference currents: I_in (X -> P), I_N (Y -> N -> P through R and 2R), I_Z (Y -> Z -> ground)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 700, 300
Y0 = 140
XX, XP, XN, XY, XZ = 60, 190, 330, 470, 600
YG = 250
s = header(W, H)
s += terminal(XX, Y0) + resistor(XX + 3.5, Y0, XP, Y0, zigs=6, lead=22)
s += resistor(XP, Y0, XN, Y0, zigs=6, lead=22) + resistor(XN, Y0, XY, Y0, zigs=6, lead=22)
s += cap(XY, Y0, XZ, Y0) + resistor(XZ, Y0, XZ, YG, zigs=6, lead=24) + ground(XZ, YG)
for x in (XP, XN, XY, XZ):
    s += dot(x, Y0)
s += red_arrow(100, Y0 - 22, 150, Y0 - 22)                  # I_in  X -> P
s += red_arrow(420, Y0 - 22, 380, Y0 - 22)                  # I_N   Y -> N
s += red_arrow(280, Y0 - 22, 240, Y0 - 22)                  # I_N   N -> P
s += red_arrow(515, Y0 - 22, 555, Y0 - 22)                  # I_Z   Y -> Z
s += red_arrow(XZ + 22, 175, XZ + 22, 215)                  # I_Z   Z -> ground
s += end_group()
t = []
t.append(text(10, 24, [("t", "GIC 展開成一條鏈（運放輸入不取電流；虛短 "), ("v", "V"), ("vsub", "N"), ("n", " = "), ("v", "V"), ("vsub", "X"),
                       ("t", "、"), ("v", "V"), ("vsub", "Z"), ("n", " = "), ("v", "V"), ("vsub", "N"), ("t", "）")]))
for x, name, role in ((XX, "X", "A 的 +"), (XP, "P", "B 輸出"), (XN, "N", "A、B 的 −"), (XY, "Y", "A 輸出"), (XZ, "Z", "B 的 +")):
    t.append(text(x + 14, Y0 - 6, [("v", name)]) if name == "Z" else text(x, Y0 + 30, [("v", name)], anchor="middle"))
    t.append(text(x, 70, [("t", role)], anchor="middle"))
t.append(text((XX + XP) / 2, Y0 + 30, [("v", "R")], anchor="middle"))
t.append(text((XP + XN) / 2, Y0 + 30, [("n", "2"), ("v", "R")], anchor="middle"))
t.append(text((XN + XY) / 2, Y0 + 30, [("v", "R")], anchor="middle"))
t.append(text((XY + XZ) / 2, Y0 + 32, [("v", "C")], anchor="middle"))
t.append(text(XZ - 14, 200, [("v", "R")], anchor="end"))
t.append(ctext(125, Y0 - 30, [("v", "I"), ("vsub", "in")], anchor="middle"))
t.append(ctext(400, Y0 - 30, [("v", "I"), ("vsub", "N")], anchor="middle"))
t.append(ctext(260, Y0 - 30, [("v", "I"), ("vsub", "N")], anchor="middle"))
t.append(ctext(535, Y0 - 30, [("v", "I"), ("vsub", "Z")], anchor="middle"))
t.append(ctext(XZ + 30, 200, [("v", "I"), ("vsub", "Z")]))
t.append(btext(XN, Y0 + 54, [("v", "V"), ("vsub", "N"), ("n", " = "), ("v", "V"), ("vsub", "X")], anchor="middle"))
t.append(btext(XZ - 40, Y0 + 54, [("v", "V"), ("vsub", "Z"), ("n", " = "), ("v", "V"), ("vsub", "X")], anchor="end"))
t.append(text(10, 286, [("t", "鏈上各電阻／電容的電流以紅色參考方向表示；"), ("v", "P"), ("t", "、"), ("v", "Y"), ("t", " 由運放輸出驅動，不寫 KCL")]))
s += ''.join(t) + footer()
write('EE-108-02-4-gic-chain.svg', s)
