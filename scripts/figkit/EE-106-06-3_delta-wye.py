"""EE-106-06-3 three single-phase transformers, Δ (3.3 kV, 3300 V tap) – Y (220 V windings, 380 V lines).

Subtractive polarity: H1 and X1 are the dotted (same-polarity) ends, both on the left of each unit.
Primary Δ: T1 H1-L1 / H2-L2, T2 H1-L2 / H2-L3, T3 H1-L3 / H2-L1 (head-to-tail).
Secondary Y: all X2 to neutral N (grounded), X1 of T1/T2/T3 -> a/b/c. Voltages as in note step 1 and (一).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def pdot(x, y): return f'<circle cx="{x}" cy="{y}" r="3" fill="#000" stroke="none"/>\n'
def vhop(x, y1, y2, hops=()):
    """Vertical wire y1 -> y2 with a small jump arc at each crossing y in hops (no connection)."""
    d = f'M{x} {y1} '; down = y2 > y1
    for h in sorted(hops, reverse=not down):
        a, b = (h - 5, h + 5) if down else (h + 5, h - 5)
        d += f'L{x} {a} A5 5 0 0 {1 if down else 0} {x} {b} '
    return f'<path d="{d}L{x} {y2}"/>\n'

W, H = 720, 510; s = header(W, H); lab = ''
L = {"L1": 50, "L2": 80, "L3": 110}
yP, yS = 200, 236                 # primary / secondary coil axes
yN, Yo = 300, {"a": 340, "b": 370, "c": 400}
cx = {"T1": 180, "T2": 360, "T3": 540}
for n, y in L.items():
    s += line(60, y, 680, y)
    lab += text(52, y + 5, [("n", n)], anchor="end")
for t, x in cx.items():
    s += line(x - 50, yP, x - 40, yP) + coil(x + 40, yP, x - 40, yP, turns=5, r=8) + line(x + 40, yP, x + 50, yP)
    s += line(x - 44, 214, x + 44, 214) + line(x - 44, 219, x + 44, 219)
    s += line(x - 50, yS, x - 40, yS) + coil(x - 40, yS, x + 40, yS, turns=5, r=8) + line(x + 40, yS, x + 50, yS)
    s += pdot(x - 42, yP - 12) + pdot(x - 42, yS + 12)
    lab += text(x, yP - 28, [("n", t)], anchor="middle")
    lab += text(x - 56, yP - 6, [("v", "H"), ("sub", "1")], anchor="end") + text(x + 56, yP - 6, [("v", "H"), ("sub", "2")])
    lab += text(x - 56, yS + 18, [("v", "X"), ("sub", "1")], anchor="end") + text(x + 56, yS + 18, [("v", "X"), ("sub", "2")])
# primary Δ: (H1 line, H2 line) per unit
conn = {"T1": ("L1", "L2"), "T2": ("L2", "L3"), "T3": ("L3", "L1")}
for t, (l1, l2) in conn.items():
    x = cx[t]
    for xx, ln in ((x - 50, l1), (x + 50, l2)):
        hops = [y for y in L.values() if y > L[ln]]
        s += vhop(xx, yP, L[ln], hops) + dot(xx, L[ln])
# secondary Y
s += line(cx["T1"] + 50, yN, 680, yN) + line(680, yN, 680, yN + 4) + ground(680, yN + 4)
for t, o in (("T1", "a"), ("T2", "b"), ("T3", "c")):
    x = cx[t]
    s += line(x + 50, yS, x + 50, yN) + dot(x + 50, yN)
    hops = ([yN] if x - 50 > cx["T1"] + 50 else []) + [y for k, y in Yo.items() if y < Yo[o]]
    s += vhop(x - 50, yS, Yo[o], hops) + dot(x - 50, Yo[o]) + line(x - 50, Yo[o], 640, Yo[o])
    lab += text(650, Yo[o] + 5, [("n", o)])
s += end_group()
lab += text(664, yN - 8, [("n", "N")], anchor="end")
lab += text(690, 30, [("n", "3.3 kV"), ("t", " 三相（一次 Δ）")], anchor="end")
lab += ctext(BLUE, W / 2, 440, [("t", "一次 Δ：每個繞組 "), ("v", "V"), ("vsub", "H"), ("n", " = 3300 V"), ("t", "（3300 V 分接頭）")], anchor="middle")
lab += ctext(BLUE, W / 2, 466, [("t", "二次 Y："), ("v", "V"), ("vsub", "ϕ"), ("n", " = 220 V"), ("t", "（a、b、c 對 N），"), ("v", "V"), ("vsub", "LL"), ("n", " = 381.05 V ≈ 380 V")], anchor="middle")
lab += text(W / 2, 492, [("t", "減極性：黑點為同名端 "), ("v", "H"), ("sub", "1"), ("t", "、"), ("v", "X"), ("sub", "1")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-106-06-3-delta-wye.svg'
out.write_text(s); print(out.name, len(s))
