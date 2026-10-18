"""EE-107-06-3 three-phase differential wiring: 11.4 kV Y (left, neutral grounded) – 69 kV Δ (right), 40 MVA.

Main Δ as in the official figure: winding a has its dot (line end) on A′ and its other end on B′; b: B′/C′; c: C′/A′.
So line A′ = a dot + c non-dot and I_A′ ∝ I_A − I_C (lags I_A by 30°: LV leads HV by 30°).
CT1 (3000/5, 11.4 kV) secondaries in Δ with the same combination: J_A = P_a + Q_c -> 87A (∝ i_a − i_c).
CT2 (400/5, 69 kV) secondaries in Y. Both CT sets have their primary polarity facing the transformer, so for
through current I_H,r leaves CT2 polarity into R2 and I_L,r returns through R1 into the CT1 Δ junction (both leftward).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def pdot(x, y): return f'<circle cx="{x}" cy="{y}" r="2.8" fill="#000" stroke="none"/>\n'
def vhop(x, y1, y2, hops=()):
    """Vertical wire from y1 down to y2 with a small jump arc at each crossing y in hops (not connected)."""
    d = f'M{x} {y1} '
    for h in sorted(hops):
        d += f'L{x} {h - 5} A5 5 0 0 1 {x} {h + 5} '
    return f'<path d="{d}L{x} {y2}"/>\n'

W, H = 720, 640; s = header(W, H); lab = ''
Y = {"A": 80, "B": 130, "C": 180}
# ---- main transformer: 11.4 kV Y (neutral grounded) | 69 kV Δ ----
for p, y in Y.items():
    s += line(30, y, 280, y) + coil(280, y, 320, y, turns=3, r=5) + line(320, y, 332, y) + coil(380, y, 420, y, turns=3, r=5)
    s += line(420, y, 690, y)
    s += pdot(284, y - 9) + pdot(416, y - 9)                 # dots at the line ends of both windings
    lab += text(26, y + 5, [("n", p)], anchor="end") + text(698, y + 5, [("n", p + "′")])
s += line(332, Y["A"], 332, Y["C"] + 32) + ground(332, Y["C"] + 32) + dot(332, Y["B"])
s += line(344, 62, 344, 198) + line(350, 62, 350, 198)                        # core
# a: non-dot end -> B′ ; b: non-dot end -> C′ (junctions at x = 432)
for p, q in (("A", "B"), ("B", "C")):
    y = Y[p]
    s += line(380, y, 370, y) + line(370, y, 370, y + 25) + line(370, y + 25, 432, y + 25) + line(432, y + 25, 432, Y[q]) + dot(432, Y[q])
# c: non-dot end -> A′ (vertical at x = 446 hops over lines B′, C′)
s += line(380, Y["C"], 362, Y["C"]) + line(362, Y["C"], 362, Y["C"] + 22) + line(362, Y["C"] + 22, 446, Y["C"] + 22)
s += vhop(446, Y["C"] + 22, Y["A"], []).replace(f'M446 {Y["C"] + 22} L446 {Y["A"]}', f'M446 {Y["C"] + 22} L446 {Y["C"] + 5} A5 5 0 0 0 446 {Y["C"] - 5} L446 {Y["B"] + 5} A5 5 0 0 0 446 {Y["B"] - 5} L446 {Y["A"]}')
s += dot(446, Y["A"])
# ---- CT1 (11.4 kV), primary polarity toward the transformer (right); secondaries in Δ ----
ct1 = {"A": 210, "B": 160, "C": 110}
yJ, yJA = 262, 288
P1, Q1 = {}, {}
for p, x in ct1.items():
    y = Y[p]; s += coil(x - 12, y + 12, x + 12, y + 12, turns=2, r=5)
    s += pdot(x + 12, y - 7) + pdot(x + 17, y + 20)
    cross = [yy for q, yy in Y.items() if yy > y]
    Q1[p], P1[p] = x - 12, x + 12
    s += vhop(x - 12, y + 12, yJA if p == "C" else yJ, cross) + vhop(x + 12, y + 12, yJA if p == "A" else yJ, cross)
xJB, xJC, xJA = (P1["B"] + Q1["A"]) // 2 + 1, (P1["C"] + Q1["B"]) // 2 + 1, P1["A"]
s += line(P1["B"], yJ, Q1["A"], yJ) + dot(xJB, yJ)          # J_B = P_b + Q_a  (i_b − i_a)
s += line(P1["C"], yJ, Q1["B"], yJ) + dot(xJC, yJ)          # J_C = P_c + Q_b  (i_c − i_b)
s += line(Q1["C"], yJA, P1["A"], yJA) + dot(xJA, yJA)       # J_A = P_a + Q_c  (i_a − i_c)
R = {"A": 400, "B": 470, "C": 540}
s += line(xJA, yJA, xJA, R["A"]) + vhop(xJB, yJ, R["B"], [yJA]) + vhop(xJC, yJ, R["C"], [yJA])
# ---- CT2 (69 kV), primary polarity toward the transformer (left); secondaries in Y ----
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
s += arrow(264, R["A"], 232, R["A"], RED) + arrow(P2["A"] - 4, R["A"], P2["A"] - 40, R["A"], RED)
s += end_group()
lab += text(380, 30, [("n", "40 MVA，11.4 kV Y / 69 kV Δ")], anchor="middle")
lab += text(40, 52, [("n", "11.4 kV"), ("t", "（Y 側）")]) + text(680, 52, [("n", "69 kV"), ("t", "（Δ 側）")], anchor="end")
lab += text(90, 208, [("n", "CT"), ("sub", "1")], anchor="end") + text(90, 228, [("n", "3000/5")], anchor="end")
lab += text(232, 312, [("n", "CT"), ("sub", "1"), ("t", " 二次接 Δ")])
lab += text(632, 206, [("n", "CT"), ("sub", "2"), ("n", " 400/5")]) + text(632, 228, [("t", "二次接 Y")])
lab += text(650, 254, [("n", "N")], anchor="middle")
lab += text(xJA + 6, 340, [("v", "i"), ("vsub", "a"), ("n", " − "), ("v", "i"), ("vsub", "c")])
s += lab
s += ctext(RED, 248, R["A"] + 24, [("v", "I"), ("vsub", "L,r")], anchor="middle")
s += ctext(RED, P2["A"] - 22, R["A"] - 10, [("v", "I"), ("vsub", "H,r")], anchor="middle")
s += text(360, 628, [("t", "● 為極性端；兩側 CT 一次極性端朝向變壓器，正常時電流經 "), ("v", "R"), ("sub", "2"), ("t", "→"), ("v", "R"), ("sub", "1"), ("t", " 環流，OP 只流兩者之差")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/06_工業配電/figures/EE-107-06-3-wiring.svg'), 'w').write(s)
print(len(s))
