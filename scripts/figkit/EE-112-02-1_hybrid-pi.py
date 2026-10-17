"""EE-112-02-1: high-frequency hybrid-pi model of the common-base stage.

Base = ac ground (bypassed), the 0.5 mA source is an ac open, the three infinite capacitors are shorts.
r_pi and C_pi sit between B (ground) and E; C_mu between B (ground) and C; the dependent source
g_m v_pi points C -> E (reference direction), with v_pi = v_b - v_e = -v_e (+ at the ground side)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YB = 110, 290
XS, XRS2, XRE, XRP, XCP, XGM2, XCM, XRL, XO = 50, 160, 200, 280, 400, 490, 545, 605, 665

W, H = 720, 380
s = header(W, H)
s += vsrc(XS, YT, XS, YB) + resistor(XS, YT, XRS2, YT, zigs=6, lead=20)
s += line(XRS2, YT, XCP, YT) + dot(XRE, YT) + dot(XRP, YT) + dot(XCP, YT)
s += resistor(XRE, YT, XRE, YB, zigs=6, lead=40) + resistor(XRP, YT, XRP, YB, zigs=6, lead=40) + cap(XCP, YT, XCP, YB)
s += dep_isrc(XGM2, YT, XCP, YT)            # g_m v_pi, reference C -> E
s += line(XGM2, YT, XO - 3.5, YT) + dot(XGM2, YT) + dot(XCM, YT) + dot(XRL, YT) + terminal(XO, YT)
s += cap(XCM, YT, XCM, YB) + resistor(XRL, YT, XRL, YB, zigs=6, lead=40)
s += line(XS, YB, XO - 3.5, YB) + terminal(XO, YB) + dot(XRE, YB) + dot(XRP, YB) + dot(XCP, YB) + dot(XCM, YB) + dot(XRL, YB)
s += line(445, YB, 445, YB + 10) + ground(445, YB + 10)
s += end_group()
t = []
t.append(btext(XS - 22, 206, [("v", "v"), ("vsub", "i")], anchor="end"))
t.append(text(105, YT - 16, [("v", "R"), ("vsub", "s"), ("n", " = 50 Ω")], anchor="middle"))
t.append(text(XRE - 4, YT - 12, [("v", "E")], anchor="middle"))
t.append(text(XRE - 12, 196, [("v", "R"), ("vsub", "E")], anchor="end"))
t.append(text(XRE - 12, 216, [("n", "0.5 kΩ")], anchor="end"))
t.append(text(XRP + 12, 196, [("v", "r"), ("vsub", "π")]))
t.append(text(XRP + 12, 216, [("n", "5.050 kΩ")]))
t.append(btext(XRP - 22, YT + 24, [("n", "−")], anchor="middle"))
t.append(btext(XRP - 22, YB - 8, [("n", "+")], anchor="middle"))
t.append(btext(XRP - 22, 250, [("v", "v"), ("vsub", "π")], anchor="middle"))
t.append(text(XCP + 20, 196, [("v", "C"), ("vsub", "π")]))
t.append(text(XCP + 20, 216, [("n", "10 pF")]))
t.append(text(445, YT - 30, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "π")], anchor="middle"))
t.append(text(445, YT + 40, [("v", "g"), ("vsub", "m"), ("n", " = 19.80 mS")], anchor="middle"))
t.append(text(XGM2 + 4, YT - 12, [("v", "C")], anchor="middle"))
t.append(text(XCM - 20, 196, [("v", "C"), ("vsub", "μ")], anchor="end"))
t.append(text(XCM - 20, 216, [("n", "1 pF")], anchor="end"))
t.append(text(XRL + 12, 196, [("v", "R"), ("vsub", "L"), ("n", " ∥ "), ("v", "R"), ("vsub", "B")]))
t.append(polarity(XO + 16, YT, YB, [("v", "v"), ("vsub", "o")]))
t.append(text(XRE, YB + 26, [("v", "B"), ("t", "（基極交流接地）")]))
t.append(text(20, 348, [("v", "v"), ("vsub", "π"), ("n", " = "), ("v", "v"), ("vsub", "b"), ("n", " − "), ("v", "v"), ("vsub", "e"), ("n", " = −"),
                        ("v", "v"), ("vsub", "e"), ("t", "；"), ("v", "C"), ("vsub", "π"), ("t", " 只接射極節點、"), ("v", "C"), ("vsub", "μ"),
                        ("t", " 只接集極節點")]))
t.append(text(20, 372, [("t", "偏壓電流源交流開路、5 V 與三個 ∞ 電容交流接地／短路；"), ("v", "V"), ("vsub", "A"), ("n", " = ∞"), ("t", " 無 "),
                        ("v", "r"), ("vsub", "o")]))
s += ''.join(t) + footer()
write('EE-112-02-1-hybrid-pi.svg', s)
