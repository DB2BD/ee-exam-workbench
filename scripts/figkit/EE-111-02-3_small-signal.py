"""EE-111-02-3: small-signal model with source degeneration (lambda = 0, coupling capacitor short,
V_DD = ac ground).  Reference i_d = g_m v_gs flows D -> S in the dependent source; it comes from
the ac-ground rail down through R_D (v_o = -i_d R_D) and leaves S down through R_S (v_s = i_d R_S)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YD, YS, YB = 50, 150, 270, 360     # ac-ground rail (V_DD), drain row, source row, ground row
XI, XR12, XG, XM, XO = 70, 180, 250, 400, 560

W, H = 640, 430
s = header(W, H)
# gate side: v_in drives G directly; R_1 || R_2 to ground
s += terminal(XI, YD) + vsrc(XI, YD + 3.5, XI, YB) + line(XI + 3.5, YD, XG - 3.5, YD) + dot(XR12, YD) + terminal(XG, YD)
s += resistor(XR12, YD, XR12, YB, zigs=6, lead=50)
# drain-source branch
s += line(XM - 60, YT, XM + 60, YT) + resistor(XM, YT, XM, YD, zigs=6, lead=14) + dot(XM, YD)
s += dep_isrc(XM, YD, XM, YS) + dot(XM, YS) + resistor(XM, YS, XM, YB, zigs=5, lead=14)
s += line(XM, YD, XO - 3.5, YD) + terminal(XO, YD)
s += line(XI, YB, XO - 3.5, YB) + terminal(XO, YB) + line(300, YB, 300, YB + 10) + ground(300, YB + 10)
s += line(XM + 60, YT, XM + 60, YT - 0)
# currents (reference directions)
s += red_arrow(XM - 24, 66, XM - 24, 116)        # i_d down through R_D into D
s += red_arrow(XM - 24, 290, XM - 24, 336)       # i_d down through R_S
s += end_group()
t = []
t.append(text(XM - 64, YT + 6, [("v", "V"), ("vsub", "DD"), ("t", "（交流接地）")], anchor="end"))
t.append(text(XI - 22, 262, [("v", "v"), ("vsub", "in")], anchor="end"))
t.append(text(XG, YD - 14, [("v", "G")], anchor="middle"))
t.append(btext(XG + 12, YD + 6, [("v", "v"), ("vsub", "g"), ("n", " = "), ("v", "v"), ("vsub", "in")]))
t.append(text(XR12 + 12, 262, [("v", "R"), ("sub", "1"), ("n", " ∥ "), ("v", "R"), ("sub", "2")]))
t.append(text(XM + 14, 100, [("v", "R"), ("vsub", "D"), ("n", " = 200 Ω")]))
t.append(ctext(XM - 32, 98, [("v", "i"), ("vsub", "d")], anchor="end"))
t.append(text(XM - 10, YD + 22, [("v", "D")], anchor="end"))
t.append(text(XM + 26, 206, [("v", "i"), ("vsub", "d"), ("n", " = "), ("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "gs")]))
t.append(text(XM - 10, YS - 8, [("v", "S")], anchor="end"))
t.append(btext(XM + 12, YS - 8, [("v", "v"), ("vsub", "s")]))
t.append(text(XM + 14, 322, [("v", "R"), ("vsub", "S"), ("n", " = 30 Ω")]))
t.append(ctext(XM - 32, 320, [("v", "i"), ("vsub", "d")], anchor="end"))
t.append(polarity(XO + 16, YD, YB, [("v", "v"), ("vsub", "o")]))
t.append(text(20, 404, [("v", "v"), ("vsub", "gs"), ("n", " = "), ("v", "v"), ("vsub", "g"), ("n", " − "), ("v", "v"), ("vsub", "s"),
                        ("t", "；閘極不取電流，"), ("v", "R"), ("sub", "1"), ("n", " ∥ "), ("v", "R"), ("sub", "2"), ("t", " 不影響 "),
                        ("v", "v"), ("vsub", "g")]))
s += ''.join(t) + footer()
write('EE-111-02-3-small-signal.svg', s)
