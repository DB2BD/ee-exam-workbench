"""EE-108-04-5 fig 3: surface-mounted PM synchronous motor cross-section (12 slots, 4 poles)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 420; CX, CY = 200, 205
RO, RB, RT, RM, RR, RSH = 150, 128, 100, 92, 80, 14     # outer, slot bottom, bore, magnet, rotor core, shaft
WT = 30                                                    # tooth width
P = lambda r, a: (CX + r * math.cos(math.radians(a)), CY - r * math.sin(math.radians(a)))
def G(u, v, th):
    t = math.radians(th)
    return (CX + u * math.cos(t) - v * math.sin(t), CY - (u * math.sin(t) + v * math.cos(t)))
def teeth(n, th0, r_tip, r_base, w):
    ub = math.sqrt(r_base ** 2 - (w / 2) ** 2); ut = math.sqrt(r_tip ** 2 - (w / 2) ** 2); d = ''
    for k in range(n):
        th = th0 + 360 / n * k
        a, b, c, e = G(ub, -w / 2, th), G(ut, -w / 2, th), G(ut, w / 2, th), G(ub, w / 2, th)
        nxt = G(ub, -w / 2, th + 360 / n)
        d += (f'M{a[0]:.1f} {a[1]:.1f} ' if k == 0 else f'L{a[0]:.1f} {a[1]:.1f} ')
        d += f'L{b[0]:.1f} {b[1]:.1f} A{r_tip} {r_tip} 0 0 0 {c[0]:.1f} {c[1]:.1f} L{e[0]:.1f} {e[1]:.1f} A{r_base} {r_base} 0 0 0 {nxt[0]:.1f} {nxt[1]:.1f} '
    return d + 'Z'
s = header(W, H)
s += f'<path d="M{CX + RO} {CY} A{RO} {RO} 0 1 0 {CX - RO} {CY} A{RO} {RO} 0 1 0 {CX + RO} {CY} Z {teeth(12, 90, RT, RB, WT)}" fill-rule="evenodd"/>\n'
for k in range(4):                                         # surface magnets, 80 deg each
    a1, a2 = 45 + 90 * k + 5, 45 + 90 * k + 85
    p1, p2, p3, p4 = P(RR, a1), P(RR, a2), P(RM, a2), P(RM, a1)
    s += (f'<path d="M{p1[0]:.1f} {p1[1]:.1f} A{RR} {RR} 0 0 0 {p2[0]:.1f} {p2[1]:.1f} L{p3[0]:.1f} {p3[1]:.1f} '
          f'A{RM} {RM} 0 0 1 {p4[0]:.1f} {p4[1]:.1f} Z" fill="{FILL_BLUE}"/>\n')
s += f'<circle cx="{CX}" cy="{CY}" r="{RR}"/>\n<circle cx="{CX}" cy="{CY}" r="{RSH}"/>\n'
s += line(*P(140, 40), 400, 92)                            # stator core
s += line(*P(122, 8), 400, 150)                            # winding (slot at 15 deg)
s += line(*P(96, -8), 400, 214)                            # air gap
s += line(*P(86, -25), 400, 270)                           # magnet
s += line(*P(60, -45), 400, 334)                           # rotor core
s += end_group()
for k, lab in enumerate(("A", "C′", "B", "A′", "C", "B′") * 2):
    x, y = P(116, 105 + 30 * k)
    s += ctext(RED, x, y + 6, [("t", lab)], anchor="middle")
for k, lab in enumerate(("N", "S", "N", "S")):
    x, y = P(66, 90 + 90 * k)
    s += text(x, y + 6, [("t", lab)], anchor="middle")
X = 406
s += text(X, 88, [("t", "定子：疊片鐵心（12 槽）")])
s += ctext(RED, X, 146, [("t", "三相分布繞組，嵌於定子槽內")])
s += text(X, 166, [("t", "（每極每相 1 槽，相序 A–C′–B–A′…）")])
s += text(X, 210, [("t", "氣隙：均勻（磁鐵外徑為圓）")])
s += text(X, 266, [("t", "永磁體：黏貼在轉子表面，")])
s += text(X, 286, [("t", "N、S 交替（4 極）")])
s += text(X, 330, [("t", "轉子鐵心：無繞組，")])
s += text(X, 350, [("t", "無電刷、無滑環")])
s += text(W / 2, H - 12, [("t", "表面黏著式永磁同步電動機剖面（"), ("v", "L"), ("vsub", "d"), ("n", " ≈ "), ("v", "L"), ("vsub", "q"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-108-04-5-spmsm.svg'), 'w').write(s)
print(len(s))
