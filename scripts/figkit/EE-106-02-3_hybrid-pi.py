"""EE-106-02-3: (a) high-frequency hybrid-pi equivalent (bias divider 20k || 20k = R_TH to ac ground, emitter bypassed,
R_C || R_L at the collector, C_mu bridging B-C); (b) after the Miller split, the input node alone:
v_i -> 1 k -> B with R_TH, r_pi, C_pi and C_M to ground."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *


def panel_a(oy):
    YT, YR, YU = oy + 100, oy + 230, oy + 52
    XV, XR1, XR2, XB, XRT, XRP, XCP = 40, 70, 150, 190, 190, 260, 370
    XC, XRC, XRL, XO = 470, 560, 635, 682
    s = line(XV, YT, XR1, YT) + resistor(XR1, YT, XR2, YT, zigs=6, lead=12) + line(XR2, YT, XCP, YT)
    s += vsrc(XV, YT, XV, YR) + dot(XB, YT)
    s += resistor(XRT, YT, XRT, YR, zigs=6, lead=28) + resistor(XRP, YT, XRP, YR, zigs=6, lead=28) + cap(XCP, YT, XCP, YR)
    s += dot(XRP, YT) + dot(XCP, YT)
    # C_mu bridge B -> C on an upper wire
    s += line(XCP, YT, XCP, YU) + cap(XCP, YU, XC, YU) + line(XC, YU, XC, YT) + dot(XC, YT)
    s += dep_isrc(XC, YT, XC, YR) + line(XC, YT, XO - 3.5, YT) + terminal(XO, YT)
    s += resistor(XRC, YT, XRC, YR, zigs=6, lead=28) + resistor(XRL, YT, XRL, YR, zigs=6, lead=28) + dot(XRC, YT) + dot(XRL, YT)
    s += line(XV, YR, XO - 3.5, YR) + terminal(XO, YR)
    for x in (XRT, XRP, XCP, XC, XRC, XRL):
        s += dot(x, YR)
    s += line(420, YR, 420, YR + 8) + ground(420, YR + 8)
    t = []
    t.append(text(8, oy + 22, [("t", "(a) 高頻混合 "), ("v", "π"), ("t", " 等效電路（射極旁路＝交流地）")]))
    t.append(text(XV - 22, oy + 170, [("v", "v"), ("vsub", "i")], anchor="end"))
    t.append(text((XR1 + XR2) / 2, YT - 14, [("v", "R"), ("vsub", "s"), ("n", " = 1 kΩ")], anchor="middle"))
    t.append(text(XB - 6, YT - 12, [("v", "B")], anchor="end"))
    t.append(text(XRT - 12, oy + 160, [("v", "R"), ("vsub", "TH")], anchor="end"))
    t.append(text(XRT - 12, oy + 180, [("n", "10 kΩ")], anchor="end"))
    t.append(text(XRP + 12, oy + 160, [("v", "r"), ("vsub", "π")]))
    t.append(text(XRP + 12, oy + 180, [("n", "2.9942 kΩ")]))
    t.append(text(XCP + 20, oy + 160, [("v", "C"), ("vsub", "π")]))
    t.append(text(XCP + 20, oy + 180, [("n", "25 pF")]))
    t.append(text((XCP + XC) / 2, YU - 18, [("v", "C"), ("vsub", "μ"), ("n", " = 3 pF")], anchor="middle"))
    t.append(text(XC + 8, YT - 12, [("v", "C")]))
    t.append(text(XC + 22, oy + 175, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "π")]))
    t.append(text(XRC + 12, oy + 160, [("v", "R"), ("vsub", "C")]))
    t.append(text(XRC + 12, oy + 180, [("n", "2.5 kΩ")]))
    t.append(text(XRL + 12, oy + 160, [("v", "R"), ("vsub", "L")]))
    t.append(text(XRL + 12, oy + 180, [("n", "5 kΩ")]))
    t.append(polarity(XRP - 22, YT, YR, [("v", "v"), ("vsub", "π")], anchor="end"))
    t.append(polarity(XO + 4, YT + 10, YR - 4, [("v", "v"), ("vsub", "o")]))
    return s, ''.join(t)


def panel_b(oy):
    YT, YR = oy + 80, oy + 200
    XV, XR1, XR2, XB, XRT, XRP, XCP, XCM = 50, 80, 170, 210, 210, 290, 370, 460
    s = f'<rect x="{XCP - 22}" y="{YT + 14}" width="{XCM - XCP + 38}" height="{YR - YT - 28}" fill="{FILL_BLUE}" stroke="none"/>\n'
    s += G_OPEN + line(XV, YT, XR1, YT) + resistor(XR1, YT, XR2, YT, zigs=6, lead=12) + line(XR2, YT, XCM, YT)
    s += vsrc(XV, YT, XV, YR) + dot(XB, YT) + dot(XRP, YT) + dot(XCP, YT)
    s += resistor(XRT, YT, XRT, YR, zigs=6, lead=24) + resistor(XRP, YT, XRP, YR, zigs=6, lead=24)
    s += cap(XCP, YT, XCP, YR) + cap(XCM, YT, XCM, YR)
    s += line(XV, YR, XCM, YR) + line(330, YR, 330, YR + 8) + ground(330, YR + 8)
    for x in (XRT, XRP, XCP):
        s += dot(x, YR)
    s += end_group()
    t = []
    t.append(text(8, oy + 22, [("t", "(b) Miller 分解後的輸入節點")]))
    t.append(text(XV - 22, oy + 145, [("v", "v"), ("vsub", "i")], anchor="end"))
    t.append(text((XR1 + XR2) / 2, YT - 14, [("v", "R"), ("vsub", "s"), ("n", " = 1 kΩ")], anchor="middle"))
    t.append(text(XB - 6, YT - 12, [("v", "B")], anchor="end"))
    t.append(text(XRT - 12, oy + 135, [("v", "R"), ("vsub", "TH")], anchor="end"))
    t.append(text(XRT - 12, oy + 155, [("n", "10 kΩ")], anchor="end"))
    t.append(text(XRP + 12, oy + 145, [("v", "r"), ("vsub", "π")]))
    t.append(text(XCP + 20, oy + 135, [("v", "C"), ("vsub", "π")]))
    t.append(text(XCP + 20, oy + 155, [("n", "25 pF")]))
    t.append(text(XCM + 26, oy + 135, [("v", "C"), ("vsub", "M"), ("n", " = "), ("v", "C"), ("vsub", "μ"), ("n", "(1 − "), ("v", "K"), ("n", ")")]))
    t.append(text(XCM + 26, oy + 155, [("v", "K"), ("n", " = "), ("v", "v"), ("vsub", "c"), ("n", "/"), ("v", "v"), ("vsub", "b")]))
    t.append(btext(8, oy + 236, [("t", "電容看到的電阻 "), ("v", "R"), ("vsub", "in"), ("n", "′ = (1 kΩ ∥ 10 kΩ) ∥ "), ("v", "r"), ("vsub", "π")]))
    return s, ''.join(t)


W, H = 720, 540
s = header(W, H)
a, ta = panel_a(0)
b, tb = panel_b(290)
s += a + end_group() + b + ta + tb + footer()
write('EE-106-02-3-hybrid-pi.svg', s)
