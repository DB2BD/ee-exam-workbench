"""EE-113-02-2: T-model small-signal equivalent of the common-base stage.

+5 V is ac ground, the 0.5 mA bias source is an ac open, C1 and C2 are shorts, the base is grounded.
Reference directions: i_e flows B -> r_e -> E and out of the emitter terminal toward R_sig;
alpha*i_e flows C -> B inside the dependent source; v_o is the collector node voltage."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YM, YB = 120, 250, 330
XS, XE, XBN, XC, XRC, XRL, XO = 60, 240, 320, 400, 480, 560, 640

W, H = 700, 430
s = header(W, H)
s += vsrc(XS, YT, XS, YB) + resistor(XS, YT, XE, YT, zigs=6, lead=50) + dot(XE, YT)
s += resistor(XE, YT, XE, YM, zigs=5, lead=30) + line(XE, YM, XC, YM) + dot(XBN, YM)
s += dep_isrc(XC, YT, XC, YM)                       # alpha i_e, C -> B
s += line(XC, YT, XO - 3.5, YT) + dot(XC, YT) + dot(XRC, YT) + dot(XRL, YT) + terminal(XO, YT)
s += resistor(XRC, YT, XRC, YB, zigs=6, lead=50) + resistor(XRL, YT, XRL, YB, zigs=6, lead=50)
s += line(XBN, YM, XBN, YB) + line(XS, YB, XO - 3.5, YB) + terminal(XO, YB) + dot(XBN, YB) + dot(XRC, YB) + dot(XRL, YB)
s += line(XBN, YB, XBN, YB + 10) + ground(XBN, YB + 10)
# i_e reference: up through r_e (B -> E) and out of E toward R_sig
s += red_arrow(XE - 22, 224, XE - 22, 150)
# R_in: looking into the emitter
s += arrow(XE - 46, YT - 30, XE - 10, YT - 30)
s += end_group()
t = []
t.append(btext(XS - 22, 230, [("v", "v"), ("vsub", "sig")], anchor="end"))
t.append(text(115, YT - 18, [("v", "R"), ("vsub", "sig"), ("n", " = 75 Ω")], anchor="middle"))
t.append(text(XE + 4, YT - 8, [("v", "E")]))
t.append(text(XE - 52, YT - 25, [("v", "R"), ("vsub", "in")], anchor="end"))
t.append(text(XE + 12, 192, [("v", "r"), ("vsub", "e"), ("n", " = 50 Ω")]))
t.append(ctext(XE - 30, 196, [("v", "i"), ("vsub", "e")], anchor="end"))
t.append(text(XBN + 8, YM + 22, [("v", "B"), ("t", "（基極）")]))
t.append(text(XC + 26, 190, [("v", "α"), ("v", "i"), ("vsub", "e")]))
t.append(text(XC - 6, YT - 8, [("v", "C")], anchor="end"))
t.append(text(XRC + 12, 236, [("v", "R"), ("vsub", "C")]))
t.append(text(XRC + 12, 256, [("n", "12 kΩ")]))
t.append(text(XRL + 12, 236, [("v", "R"), ("vsub", "L")]))
t.append(text(XRL + 12, 256, [("n", "12 kΩ")]))
t.append(polarity(XO + 16, YT, YB, [("v", "v"), ("vsub", "o")]))
t.append(text(20, 390, [("t", "基極接地；+5 V 交流接地；0.5 mA 偏壓電流源交流開路（不畫）；"), ("v", "C"), ("sub", "1"), ("t", "、"),
                        ("v", "C"), ("sub", "2"), ("t", " 短路")]))
t.append(text(20, 414, [("t", "紅色為參考方向："), ("v", "i"), ("vsub", "e"), ("t", " 由 "), ("v", "B"), ("t", " 經 "), ("v", "r"), ("vsub", "e"),
                        ("t", " 流向 "), ("v", "E"), ("t", " 並流出射極端子")]))
s += ''.join(t) + footer()
write('EE-113-02-2-t-model.svg', s)
