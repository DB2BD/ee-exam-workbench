"""EE-108-02-3: A circuit of the series-series feedback amplifier (feedback network R_S, z-parameter loading).
Input loop: v_i across the gate-source port, input copy of R_S (z11) carries the gate current = 0 -> v_gs = v_i.
Output loop: g_m v_gs (drain -> source) || r_o, in series with R_L (drain to ground) and the output copy of
R_S (z22); i_o enters the drain from R_L (reference direction of the stem), v_o = -i_o R_L, v_f = R_S i_o."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

W, H = 700, 370
s = header(W, H)
# ---- input loop ----
XV, XG, YT, YS, YB = 70, 200, 90, 200, 300
s += vsrc(XV, YT, XV, YB) + line(XV, YT, XG - 3.5, YT) + terminal(XG, YT)
s += line(XV, YB, XG, YB)
s += terminal(XG, YS) + resistor(XG, YS + 3.5, XG, YB, zigs=6, lead=16) + dot(XG, YB)
# ---- output loop ----
XI, XO, XL = 420, 520, 630
YD, YSo = 90, 200
s += dep_isrc(XI, YD, XI, YSo) + resistor(XO, YD, XO, YSo, zigs=6, lead=20)
s += line(XI, YD, XL, YD) + line(XI, YSo, XO, YSo) + dot(470, YD) + dot(XO, YD) + dot(470, YSo)
s += resistor(470, YSo, 470, YB, zigs=6, lead=16)
s += resistor(XL, YD, XL, YB, zigs=8, lead=50) + line(470, YB, XL, YB)
s += line(560, YB, 560, YB + 8) + ground(560, YB + 8)
s += line(135, YB, 135, YB + 8) + ground(135, YB + 8)
s += red_arrow(600, YD - 14, 560, YD - 14)                 # i_o enters the drain node from R_L
s += red_arrow(XL - 18, 230, XL - 18, 180)                 # i_o upward through R_L
s += end_group()
t = []
t.append(text(14, 26, [("t", "(a) 輸入迴路：閘極不取電流")]))
t.append(text(370, 26, [("t", "(b) 輸出迴路：取樣電流 "), ("v", "i"), ("vsub", "o")]))
t.append(text(XV - 22, (YT + YB) / 2 + 5, [("v", "v"), ("vsub", "i")], anchor="end"))
t.append(text(XG + 10, YT + 5, [("t", "閘極 "), ("v", "G")]))
t.append(text(XG + 10, YS + 5, [("t", "源極 "), ("v", "S")]))
t.append(btext(XG - 12, YT + 22, [("n", "+")], anchor="middle"))
t.append(btext(XG - 12, YS - 6, [("n", "−")], anchor="middle"))
t.append(btext(XG - 14, (YT + YS) / 2 + 5, [("v", "v"), ("vsub", "gs")], anchor="end"))
t.append(text(XG + 14, 258, [("v", "R"), ("vsub", "S")]))
t.append(text(XG + 14, 280, [("t", "（電流 0）")]))
t.append(text(XI - 24, (YD + YSo) / 2 + 5, [("v", "g"), ("vsub", "m"), ("v", "v"), ("vsub", "gs")], anchor="end"))
t.append(text(XO + 12, (YD + YSo) / 2 + 5, [("v", "r"), ("vsub", "o")]))
t.append(text(470, YD - 22, [("v", "D")], anchor="middle"))
t.append(text(486, YSo + 20, [("v", "S")]))
t.append(text(486, 262, [("v", "R"), ("vsub", "S")]))
t.append(ctext(580, YD - 22, [("v", "i"), ("vsub", "o")], anchor="middle"))
t.append(ctext(XL - 24, 210, [("v", "i"), ("vsub", "o")], anchor="end"))
t.append(text(XL + 12, 200, [("v", "R"), ("vsub", "L")]))
t.append(polarity(XL + 40, YD, YB, [("v", "v"), ("vsub", "o")], color=BLUE))
t.append(polarity(430, YSo, YB, [("v", "v"), ("vsub", "f")], color=BLUE, anchor="end"))
t.append(text(14, 350, [("v", "v"), ("vsub", "gs"), ("n", " = "), ("v", "v"), ("vsub", "i"), ("t", "；"),
                        ("v", "v"), ("vsub", "f"), ("n", " = "), ("v", "R"), ("vsub", "S"), ("v", "i"), ("vsub", "o"),
                        ("t", "（回授網路 "), ("v", "β"), ("n", " = "), ("v", "R"), ("vsub", "S"), ("t", "）；"),
                        ("v", "v"), ("vsub", "o"), ("n", " = −"), ("v", "i"), ("vsub", "o"), ("v", "R"), ("vsub", "L")]))
s += ''.join(t) + footer()
write('EE-108-02-3-a-circuit.svg', s)
