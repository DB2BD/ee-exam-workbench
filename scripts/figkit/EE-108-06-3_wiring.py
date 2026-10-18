"""EE-108-06-3 V-V (open-delta) bank, three-line diagram.
Primary 11.4 kV lines A, B, C; T1 H1-A, H2-B; T2 H1-B, H2-C (subtractive polarity, dots at H1/X1).
Secondary: T1 X1 -> X, centre tap -> N (grounded), T1 X2 and T2 X1 -> Y, T2 X2 -> Z.
Terminal voltages as in note step 2 / table.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def vhop(x, y_from, y_to, crossings, r=6):
    """vertical wire from y_from (bottom) up to y_to, hopping (semicircle) over horizontal lines at crossings."""
    d = f'M{x} {y_from} '
    for yc in sorted(crossings, reverse=True):
        d += f'L{x} {yc + r} A{r} {r} 0 0 1 {x} {yc - r} '
    d += f'L{x} {y_to}'
    return f'<path d="{d}"/>\n'
W, H = 720, 500; s = header(W, H); lab = ''
yA, yB, yC = 50, 80, 110
s += line(60, yA, 600, yA) + line(60, yB, 600, yB) + line(60, yC, 600, yC)
yp, ys = 180, 214                   # primary / secondary coil axes
def xfmr(x1, x2):
    out = coil(x2, yp, x1, yp, turns=6, r=10)          # bumps face down (towards core)
    out += coil(x1, ys, x2, ys, turns=6, r=10)         # bumps face up
    out += line(x1 + 6, 194, x2 - 6, 194) + line(x1 + 6, 200, x2 - 6, 200)   # core
    return out
t1a, t1b, t2a, t2b = 160, 280, 420, 540
s += xfmr(t1a, t1b) + xfmr(t2a, t2b)
# primary leads
s += vhop(t1a, yp, yA, [yB, yC]) + dot(t1a, yA)
s += vhop(t1b, yp, yB, [yC]) + dot(t1b, yB)
s += vhop(t2a, yp, yB, [yC]) + dot(t2a, yB)
s += line(t2b, yp, t2b, yC) + dot(t2b, yC)
# secondary leads and output terminals
yo = 330
tx, tn, ty, tz = t1a, (t1a + t1b) / 2, (t1b + t2a) / 2, t2b
s += line(t1a, ys, tx, yo)
s += line(tn, ys, tn, yo) + dot(tn, ys)
s += line(t1b, ys, t1b, 260) + line(t2a, ys, t2a, 260) + line(t1b, 260, t2a, 260) + dot(ty, 260) + line(ty, 260, ty, yo)
s += line(t2b, ys, tz, yo)
for x in (tx, tn, ty, tz):
    s += f'<circle cx="{x}" cy="{yo + 4}" r="4" fill="#fff"/>\n'
s += line(tn, 290, tn - 40, 290) + line(tn - 40, 290, tn - 40, 300) + ground(tn - 40, 300)
s += dot(tn, 290)
# polarity dots H1 / X1
for x in (t1a, t2a):
    s += f'<circle cx="{x + 8}" cy="{yp - 16}" r="3" fill="#000" stroke="none"/>\n<circle cx="{x + 8}" cy="{ys + 16}" r="3" fill="#000" stroke="none"/>\n'
s += end_group()
lab += text(50, yA + 5, [("v", "A")], anchor="end") + text(50, yB + 5, [("v", "B")], anchor="end") + text(50, yC + 5, [("v", "C")], anchor="end")
lab += text(612, yA + 5, [("n", "11.4 kV")]) + text(612, yC + 5, [("t", "三相配電線")])
lab += text((t1a + t1b) / 2, 150, [("v", "T"), ("sub", "1")], anchor="middle") + text((t2a + t2b) / 2, 150, [("v", "T"), ("sub", "2")], anchor="middle")
lab += text(t1a - 8, yp + 4, [("v", "H"), ("sub", "1")], anchor="end") + text(t1b + 8, yp + 4, [("v", "H"), ("sub", "2")])
lab += text(t2a - 8, yp + 4, [("v", "H"), ("sub", "1")], anchor="end") + text(t2b + 8, yp + 4, [("v", "H"), ("sub", "2")])
lab += text(t1a - 8, ys + 18, [("v", "X"), ("sub", "1")], anchor="end") + text(t1b + 8, ys + 18, [("v", "X"), ("sub", "2")])
lab += text(t2a - 8, ys + 18, [("v", "X"), ("sub", "1")], anchor="end") + text(t2b + 8, ys + 18, [("v", "X"), ("sub", "2")])
lab += text(600, 196, [("t", "每台 "), ("n", "11.4 kV /")]) + text(600, 218, [("n", "220–110 V")])
for x, nm in ((tx, "X"), (tn, "N"), (ty, "Y"), (tz, "Z")):
    lab += text(x, yo + 30, [("v", nm)], anchor="middle")
# voltage annotations (between terminals)
yv = 390
lab += ctext(BLUE, (tx + tn) / 2, yv, [("v", "V"), ("vsub", "XN"), ("n", " = 110 V")], anchor="middle")
lab += ctext(BLUE, (tn + ty) / 2 + 30, yv, [("v", "V"), ("vsub", "YN"), ("n", " = 110 V")], anchor="middle")
lab += ctext(BLUE, (ty + tz) / 2 + 30, yv, [("v", "V"), ("vsub", "YZ"), ("n", " = 220 V")], anchor="middle")
lab += ctext(BLUE, W / 2, 420, [("v", "V"), ("vsub", "XY"), ("n", " = "), ("v", "V"), ("vsub", "YZ"), ("n", " = "), ("v", "V"), ("vsub", "ZX"), ("n", " = 220 V"), ("t", "（三相／單相 220 V）")], anchor="middle")
lab += ctext(BLUE, W / 2, 446, [("v", "V"), ("vsub", "ZN"), ("n", " = 190.53 V"), ("t", "（高腳相，不接 110 V 負載）")], anchor="middle")
lab += text(W / 2, 478, [("t", "黑點為同名端（減極性）；"), ("v", "N"), ("t", " 只由 "), ("v", "T"), ("sub", "1"), ("t", " 中點抽頭引出並接地；"), ("v", "X"), ("t", "–"), ("v", "Z"), ("t", " 間開口")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-108-06-3-wiring.svg'
out.write_text(s); print(out.name, len(s))
