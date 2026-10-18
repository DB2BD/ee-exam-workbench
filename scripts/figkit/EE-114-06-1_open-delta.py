"""EE-114-06-1 open-delta (V-V) three-line diagram, part (一).
Primary 3300 V lines A, B, C: T1 H1-A, H2-B; T2 H1-B, H2-C (subtractive polarity, dots at H1/X1).
Secondary 220 V: T1 X1 -> a; T1 X2 and T2 X1 -> b; T2 X2 -> c.  Faulty T3 (C-A / c-a) removed: dashed box.
Line currents I_a, I_b, I_c drawn with reference direction towards the load (used in part (二) KCL).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def vhop(x, y_from, y_to, crossings, r=6):
    d = f'M{x} {y_from} '
    for yc in sorted(crossings, reverse=True):
        d += f'L{x} {yc + r} A{r} {r} 0 0 1 {x} {yc - r} '
    d += f'L{x} {y_to}'
    return f'<path d="{d}"/>\n'
W, H = 720, 470; s = header(W, H); lab = ''
yA, yB, yC = 50, 80, 110
s += line(60, yA, 470, yA) + line(60, yB, 470, yB) + line(60, yC, 470, yC)
yp, ys = 180, 214
def xfmr(x1, x2):
    out = coil(x2, yp, x1, yp, turns=6, r=10)
    out += coil(x1, ys, x2, ys, turns=6, r=10)
    out += line(x1 + 6, 194, x2 - 6, 194) + line(x1 + 6, 200, x2 - 6, 200)
    return out
t1a, t1b, t2a, t2b = 110, 230, 330, 450
s += xfmr(t1a, t1b) + xfmr(t2a, t2b)
s += vhop(t1a, yp, yA, [yB, yC]) + dot(t1a, yA)
s += vhop(t1b, yp, yB, [yC]) + dot(t1b, yB)
s += vhop(t2a, yp, yB, [yC]) + dot(t2a, yB)
s += line(t2b, yp, t2b, yC) + dot(t2b, yC)
yo = 320
xa, xb, xc = t1a, (t1b + t2a) / 2, t2b
s += line(t1a, ys, xa, yo)
s += line(t1b, ys, t1b, 260) + line(t2a, ys, t2a, 260) + line(t1b, 260, t2a, 260) + dot(xb, 260) + line(xb, 260, xb, yo)
s += line(t2b, ys, xc, yo)
for x in (xa, xb, xc):
    s += f'<circle cx="{x}" cy="{yo + 4}" r="4" fill="#fff"/>\n'
for x in (t1a, t2a):
    s += f'<circle cx="{x + 8}" cy="{yp - 16}" r="3" fill="#000" stroke="none"/>\n<circle cx="{x + 8}" cy="{ys + 16}" r="3" fill="#000" stroke="none"/>\n'
# removed T3 (dashed box)
s += '<rect x="510" y="150" width="170" height="100" stroke-dasharray="6 4" stroke-width="1"/>\n'
# line current reference arrows (towards the load)
for x in (xa, xb, xc):
    s += arrow(x + 14, 272, x + 14, 304, RED)
s += end_group()
lab += text(50, yA + 5, [("v", "A")], anchor="end") + text(50, yB + 5, [("v", "B")], anchor="end") + text(50, yC + 5, [("v", "C")], anchor="end")
lab += text(482, yA + 5, [("t", "一次 "), ("n", "3300 V")]) + text(482, yC + 5, [("t", "三相電源")])
lab += text((t1a + t1b) / 2, 150, [("v", "T"), ("sub", "1")], anchor="middle") + text((t2a + t2b) / 2, 150, [("v", "T"), ("sub", "2")], anchor="middle")
for xl, xr in ((t1a, t1b), (t2a, t2b)):
    lab += text(xl - 8, yp + 4, [("v", "H"), ("sub", "1")], anchor="end") + text(xr + 8, yp + 4, [("v", "H"), ("sub", "2")])
    lab += text(xl - 8, ys + 18, [("v", "X"), ("sub", "1")], anchor="end") + text(xr + 8, ys + 18, [("v", "X"), ("sub", "2")])
lab += text(595, 180, [("v", "T"), ("sub", "3"), ("t", " 故障拆除")], anchor="middle")
lab += text(595, 204, [("t", "一次 "), ("v", "CA"), ("t", "、二次 "), ("v", "ca")], anchor="middle")
lab += text(595, 228, [("t", "兩邊皆開路")], anchor="middle")
for x, nm, cur in ((xa, "a", "a"), (xb, "b", "b"), (xc, "c", "c")):
    lab += text(x, yo + 30, [("v", nm)], anchor="middle")
    lab += ctext(RED, x + 22, 296, [("v", "I"), ("vsub", cur)])
lab += ctext(BLUE, (xa + xb) / 2, yo + 30, [("n", "|"), ("v", "V"), ("vsub", "ab"), ("n", "| = 220 V")], anchor="middle")
lab += ctext(BLUE, (xb + xc) / 2, yo + 30, [("n", "|"), ("v", "V"), ("vsub", "bc"), ("n", "| = 220 V")], anchor="middle")
lab += ctext(BLUE, W / 2, 388, [("v", "V"), ("vsub", "ca"), ("t", " 由 "), ("v", "a"), ("t", "、"), ("v", "c"), ("t", " 兩端點的電位差給出（"), ("v", "a"), ("t", "–"), ("v", "c"), ("t", " 間不接任何繞組或導線）")], anchor="middle")
lab += text(W / 2, 420, [("t", "每台 "), ("n", "50 kVA，3300/220 V"), ("t", "；黑點為同名端（減極性），"), ("v", "T"), ("sub", "1"), ("t", "、"), ("v", "T"), ("sub", "2"), ("t", " 首尾相接於 "), ("v", "b")], anchor="middle")
lab += text(W / 2, 446, [("v", "I"), ("vsub", "a"), ("t", "、"), ("v", "I"), ("vsub", "b"), ("t", "、"), ("v", "I"), ("vsub", "c"), ("t", "：線電流參考方向（流向負載）")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-114-06-1-open-delta.svg'
out.write_text(s); print(out.name, len(s))
