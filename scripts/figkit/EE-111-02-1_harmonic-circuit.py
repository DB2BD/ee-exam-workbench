"""EE-111-02-1: (a) full-wave output v_o = |Vm sin| with its average V_o; (b) n-th harmonic equivalent circuit."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 720, 300
s = header(W, H)
# (a) waveform
X0, Y0, XS, YS = 112, 235, 240 / (2 * math.pi), 1.5   # 100 V -> 150 px
s += arrow(X0, Y0, X0 + 262, Y0) + arrow(X0, Y0 + 10, X0, 50)
pts = [(X0 + XS * t, Y0 - YS * 100 * abs(math.sin(t))) for t in [k * 2 * math.pi / 200 for k in range(201)]]
s += poly(pts, w=2.2, color=BLUE)
yvo = Y0 - YS * 63.66
s += dashed(X0, yvo, X0 + 245, yvo)
s += dashed(X0, Y0 - 150, X0 + XS * 1.5 * math.pi, Y0 - 150)
for k, lab in ((1, "π"), (2, "2π")):
    s += line(X0 + XS * math.pi * k, Y0, X0 + XS * math.pi * k, Y0 + 5)
s += end_group()
t = []
t.append(text(6, 22, [("t", "(a) 輸出電壓 "), ("v", "v"), ("vsub", "o"), ("n", " = |"), ("v", "V"), ("vsub", "m"), ("n", " sin "), ("v", "ωt"), ("n", "|")]))
t.append(text(X0 + XS * math.pi, Y0 + 22, [("v", "π")], anchor="middle"))
t.append(text(X0 + XS * 2 * math.pi, Y0 + 22, [("n", "2"), ("v", "π")], anchor="middle"))
t.append(text(X0 + 266, Y0 + 5, [("v", "ωt")]))
t.append(text(X0 - 6, Y0 - 145, [("v", "V"), ("vsub", "m"), ("n", " = 100 V")], anchor="end"))
t.append(text(X0 - 6, yvo + 5, [("v", "V"), ("vsub", "o"), ("n", " = 63.66 V")], anchor="end"))
# (b) n-th harmonic circuit
L0, R0, T0, B0 = 450, 630, 80, 240
s += G_OPEN
s += line(L0, T0, L0, 140) + ac_source(L0, 160, r=18) + line(L0, 178, L0, B0)
s += line(L0, T0, R0, T0) + line(L0, B0, R0, B0)
s += resistor(R0, T0, R0, 155, zigs=6, lead=10) + coil(R0, 165, R0, B0, turns=4) + line(R0, 155, R0, 165)
s += red_arrow(500, T0 - 12, 580, T0 - 12)
s += end_group()
t.append(text(400, 22, [("t", "(b) 第 "), ("v", "n"), ("t", " 次諧波等效電路")]))
t.append(text(L0 - 26, 165, [("v", "V"), ("vsub", "n")], anchor="end"))
t.append(text(L0 - 26, 185, [("t", "頻率 "), ("v", "nω")], anchor="end"))
t.append(ctext(540, T0 - 30, [("v", "I"), ("vsub", "n"), ("n", " = "), ("v", "V"), ("vsub", "n"), ("n", "/|"), ("v", "Z"), ("vsub", "n"), ("n", "|")], anchor="middle"))
t.append(text(R0 + 14, 122, [("v", "R"), ("n", " = 10 Ω")]))
t.append(text(R0 + 14, 207, [("v", "j"), ("v", "nωL")]))
t.append(text(540, 272, [("v", "Z"), ("vsub", "n"), ("n", " = "), ("v", "R"), ("n", " + "), ("v", "jnωL")], anchor="middle"))
s += ''.join(t) + footer()
write('EE-111-02-1-harmonic-circuit.svg', s)
