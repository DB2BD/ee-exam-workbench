"""EE-106-06-4 three-phase differential wiring: Y–Δ main transformer, CT1 secondaries in Δ, CT2 in Y, 87 per phase.

Dot convention (checked in the note): main-transformer dots on the left winding ends; both CT sets have their
primary polarity facing the transformer. Main Δ: a non-dot end + b dot end -> 69 kV line A (line A ∝ I_B − I_A).
CT1 Δ uses the same combination: a non-dot + b dot -> 87A (pilot A ∝ I_A − I_B), so pilot currents circulate.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
DOT = "̇"
def pdot(x, y): return f'<circle cx="{x}" cy="{y}" r="2.8" fill="#000" stroke="none"/>\n'
def vhop(x, y1, y2, hops=()):
    """Vertical wire from y1 down to y2 with a small jump arc at each crossing y in hops (not connected)."""
    d = f'M{x} {y1} '
    for h in sorted(hops):
        d += f'L{x} {h - 5} A5 5 0 0 1 {x} {h + 5} '
    return f'<path d="{d}L{x} {y2}"/>\n'

W, H = 720, 640; s = header(W, H); lab = ''
Y = {"A": 80, "B": 130, "C": 180}
# ---- main transformer: primary Y (neutral grounded), secondary Δ ----
for p, y in Y.items():
    s += line(30, y, 280, y) + coil(280, y, 320, y, turns=3, r=5) + line(320, y, 332, y) + coil(380, y, 420, y, turns=3, r=5)
    s += line(420, y, 690, y) + dot(432, y)
    s += pdot(284, y - 9) + pdot(384, y - 9)
    lab += text(26, y + 5, [("n", p)], anchor="end") + text(698, y + 5, [("n", p)])
s += line(332, Y["A"], 332, Y["C"] + 32) + ground(332, Y["C"] + 32) + dot(332, Y["B"])
s += line(344, 62, 344, 198) + line(350, 62, 350, 198)                        # core
s += line(380, Y["B"], 370, Y["B"]) + line(370, Y["B"], 370, Y["A"] + 25) + line(370, Y["A"] + 25, 432, Y["A"] + 25) + line(432, Y["A"] + 25, 432, Y["A"])
s += line(380, Y["C"], 370, Y["C"]) + line(370, Y["C"], 370, Y["B"] + 25) + line(370, Y["B"] + 25, 432, Y["B"] + 25) + line(432, Y["B"] + 25, 432, Y["B"])
s += line(432, Y["C"], 432, Y["C"] + 22) + line(432, Y["C"] + 22, 360, Y["C"] + 22) + line(360, Y["C"] + 22, 360, Y["A"]) + line(360, Y["A"], 380, Y["A"])
# ---- CT1 (Y side), polarity toward transformer (right); secondaries to Δ ----
ct1 = {"A": 210, "B": 160, "C": 110}
yJ, yJC = 262, 288
P1, Q1 = {}, {}
for p, x in ct1.items():
    y = Y[p]; s += coil(x - 12, y + 12, x + 12, y + 12, turns=2, r=5)
    s += pdot(x + 12, y - 7) + pdot(x + 17, y + 20)
    cross = [yy for q, yy in Y.items() if yy > y]
    Q1[p], P1[p] = x - 12, x + 12
    s += vhop(x - 12, y + 12, yJ if p != "C" else yJC, cross) + vhop(x + 12, y + 12, yJ if p != "A" else yJC, cross)
s += line(P1["B"], yJ, Q1["A"], yJ) + dot((P1["B"] + Q1["A"]) // 2 + 1, yJ)         # J_A = Q_a + P_b
s += line(P1["C"], yJ, Q1["B"], yJ) + dot((P1["C"] + Q1["B"]) // 2 + 1, yJ)         # J_B = Q_b + P_c
s += line(Q1["C"], yJC, P1["A"], yJC) + dot(Q1["C"], yJC)                          # J_C = Q_c + P_a
xJA, xJB, xJC = (P1["B"] + Q1["A"]) // 2 + 1, (P1["C"] + Q1["B"]) // 2 + 1, Q1["C"]
R = {"A": 400, "B": 470, "C": 540}
s += vhop(xJA, yJ, R["A"], [yJC]) + vhop(xJB, yJ, R["B"], [yJC]) + line(xJC, yJC, xJC, R["C"])
# ---- CT2 (Δ side), polarity toward transformer (left); secondaries in Y ----
ct2 = {"A": 510, "B": 560, "C": 610}
yN = 262
P2 = {}
for p, x in ct2.items():
    y = Y[p]; s += coil(x - 12, y + 12, x + 12, y + 12, turns=2, r=5)
    s += pdot(x - 12, y - 7) + pdot(x - 17, y + 20)
    cross = [yy for q, yy in Y.items() if yy > y]
    P2[p] = x - 12
    s += vhop(x + 12, y + 12, yN, cross)
    s += vhop(x - 12, y + 12, R[p], cross + ([yN] if x - 12 > ct2["A"] + 12 else []))
s += line(ct2["A"] + 12, yN, 666, yN) + dot(ct2["A"] + 12, yN) + dot(ct2["B"] + 12, yN) + dot(ct2["C"] + 12, yN) + dot(666, yN)
s += line(666, yN, 690, yN) + line(690, yN, 690, yN + 12) + ground(690, yN + 12)
# ---- 87 elements: R1 – (OP to N) – R2 per phase ----
xr = 470
for p, y in R.items():
    xl = {"A": xJA, "B": xJB, "C": xJC}[p]
    s += line(xl, y, 270, y) + coil(270, y, 330, y, turns=3) + line(330, y, 390, y) + coil(390, y, 450, y, turns=3)
    s += line(450, y, P2[p], y) + dot(360, y)
    s += coil(360, y, 360, y + 40, turns=3, r=5) + line(360, y + 40, xr, y + 40) + dot(xr, y + 40)
    lab += text(300, y - 16, [("v", "R"), ("sub", "1")], anchor="middle") + text(420, y - 16, [("v", "R"), ("sub", "2")], anchor="middle")
    lab += text(360, y - 12, [("n", f"87{p}")], anchor="middle") + text(352, y + 28, [("n", "OP")], anchor="end")
s += vhop(xr, R["A"] + 40, 600, [R["B"], R["C"]]) + line(xr, 600, 666, 600) + line(666, 600, 666, yN)
s += arrow(xJA + 20, R["A"], xJA + 56, R["A"], RED) + arrow(P2["A"] - 40, R["A"], P2["A"] - 4, R["A"], RED)
s += end_group()
lab += text(380, 30, [("n", "30 MVA，11.4/69 kV，Y–Δ")], anchor="middle")
lab += text(40, 52, [("n", "11.4 kV"), ("t", "（Y 側）")]) + text(680, 52, [("n", "69 kV"), ("t", "（Δ 側）")], anchor="end")
lab += text(90, 208, [("n", "CT"), ("sub", "1")], anchor="end") + text(232, 306, [("n", "CT"), ("sub", "1"), ("t", " 二次接 Δ")])
lab += text(632, 206, [("n", "CT"), ("sub", "2")]) + text(632, 228, [("t", "二次接 Y")])
lab += text(650, 254, [("n", "N")], anchor="middle")
s += lab
s += ctext(RED, xJA + 38, R["A"] + 22, [("v", "I" + DOT), ("sub", "1"), ("n", "′")], anchor="middle")
s += ctext(RED, P2["A"] - 22, R["A"] - 10, [("v", "I" + DOT), ("sub", "2"), ("n", "′")], anchor="middle")
s += text(360, 628, [("t", "● 為極性端；正常負載或區外故障 "), ("v", "I" + DOT), ("sub", "1"), ("n", "′ = "), ("v", "I" + DOT), ("sub", "2"), ("n", "′"), ("t", "，OP 無電流")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-106-06-4-wiring.svg'), 'w').write(s)
print(len(s))
