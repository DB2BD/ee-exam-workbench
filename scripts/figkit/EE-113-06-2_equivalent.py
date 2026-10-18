"""EE-113-06-2 equivalent circuit (step 1): V_s = 220 V -> round-trip line R_l + jX_l -> load bus V_L;
load Z = 1.68 + j1.26 ohm in parallel with the correcting capacitor C.  Reference directions:
I from source to bus, I_Z and I_C from bus down to the return line (I = I_Z + I_C).
V_s and V_L marked by +/- at their two nodes (upper wire / return line).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def cap(x, y1, y2, gap=10, w=28):
    m = (y1 + y2) / 2
    return (line(x, y1, x, m - gap / 2) + line(x - w / 2, m - gap / 2, x + w / 2, m - gap / 2)
            + line(x - w / 2, m + gap / 2, x + w / 2, m + gap / 2) + line(x, m + gap / 2, x, y2))
W, H = 680, 330; s = header(W, H); lab = ''
yT, yB = 70, 250
xs, xr1, xr2, xx2, xbus, xz, xc = 110, 170, 260, 350, 400, 540, 620
# source
s += line(xs, yT, xs, 140) + ac_source(xs, 160, 20) + line(xs, 180, xs, yB)
# top wire: R_l then X_l
s += line(xs, yT, xr1, yT) + resistor(xr1, yT, xr2, yT) + coil(xr2, yT, xx2, yT, turns=4, r=8) + line(xx2, yT, xc, yT)
s += line(xs, yB, xc, yB)
# load Z (R + jX) and capacitor
s += resistor(xz, yT, xz, 160, zigs=5) + coil(xz, 160, xz, yB, turns=3, r=7)
s += cap(xc, yT, yB)
for x in (xbus, xz):
    s += dot(x, yT) + dot(x, yB)
# current arrows (reference directions)
s += arrow(180, yT - 22, 250, yT - 22, RED)
s += arrow(xz + 20, 100, xz + 20, 140, RED) + arrow(xc + 22, 120, xc + 22, 160, RED)
# voltages by polarity marks (+ at the upper node, - at the return line)
s += end_group()
lab += ctext(BLUE, xs - 30, 166, [("v", "V"), ("vsub", "s")], anchor="end") + ctext(BLUE, xs - 30, 188, [("n", "220 V")], anchor="end")
lab += ctext(BLUE, xs - 14, 128, [("n", "+")], anchor="middle") + ctext(BLUE, xs - 14, 204, [("n", "−")], anchor="middle")
lab += ctext(BLUE, xbus, yT + 26, [("n", "+")], anchor="middle") + ctext(BLUE, xbus, yB - 12, [("n", "−")], anchor="middle")
lab += ctext(BLUE, xbus, 166, [("v", "V"), ("vsub", "L")], anchor="middle")
lab += ctext(RED, 215, yT - 30, [("v", "I")], anchor="middle")
lab += ctext(RED, xz + 30, 126, [("v", "I"), ("vsub", "Z")]) + ctext(RED, xc + 32, 146, [("v", "I"), ("vsub", "C")])
lab += text((xr1 + xr2) / 2, yT + 30, [("v", "R"), ("vsub", "ℓ")], anchor="middle")
lab += text((xr1 + xr2) / 2, yT + 50, [("n", "0.12558 Ω")], anchor="middle")
lab += text((xr2 + xx2) / 2, yT + 30, [("v", "X"), ("vsub", "ℓ")], anchor="middle")
lab += text((xr2 + xx2) / 2, yT + 50, [("n", "0.028158 Ω")], anchor="middle")
lab += text(xz - 14, 120, [("v", "R"), ("n", " = 1.68 Ω")], anchor="end")
lab += text(xz - 14, 210, [("v", "X"), ("n", " = 1.26 Ω")], anchor="end")
lab += text(xc + 22, 205, [("v", "C")])
lab += text(xbus, yT - 12, [("t", "負載母線")], anchor="middle")
lab += text(W / 2, 290, [("v", "Z"), ("vsub", "ℓ"), ("n", " = "), ("v", "R"), ("vsub", "ℓ"), ("n", " + "), ("v", "jX"), ("vsub", "ℓ"), ("t", "：去線＋回線共 "), ("n", "2 × 0.13 km"), ("t", "（集中畫在上方導線）")], anchor="middle")
lab += text(W / 2, 314, [("t", "負載 "), ("v", "Z"), ("n", " = 1.68 + "), ("v", "j"), ("n", "1.26 Ω"), ("t", "；"), ("v", "I"), ("n", " = "), ("v", "I"), ("vsub", "Z"), ("n", " + "), ("v", "I"), ("vsub", "C")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-113-06-2-equivalent.svg'
out.write_text(s); print(out.name, len(s))
