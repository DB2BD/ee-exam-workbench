"""EE-108-04-5 fig 2: dc motor armature reaction (2 poles, brushes on geometric neutral, CCW rotation).
Conductors under N carry current into the page, under S out of the page -> F_a points down (quadrature);
force: left side down, right side up -> CCW; resultant flux tilts down-right, magnetic neutral plane turns CW (against rotation)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 420; CX, CY = 210, 205; RA, RC, RS1, RS2 = 90, 76, 100, 124
P = lambda r, a: (CX + r * math.cos(math.radians(a)), CY - r * math.sin(math.radians(a)))
s = header(W, H)
def pole(ac, sign):
    a1, a2 = ac - 50, ac + 50
    p1, p2, p3, p4 = P(RS1, a1), P(RS1, a2), P(RS2, a2), P(RS2, a1)
    d = (f'M{p1[0]:.1f} {p1[1]:.1f} A{RS1} {RS1} 0 0 0 {p2[0]:.1f} {p2[1]:.1f} L{p3[0]:.1f} {p3[1]:.1f} '
         f'A{RS2} {RS2} 0 0 1 {p4[0]:.1f} {p4[1]:.1f} Z')
    x0 = CX + sign * (RS2 - 6); x1 = CX + sign * (RS2 + 46)
    return f'<path d="{d}"/>\n<path d="M{min(x0, x1):.1f} {CY - 34} L{max(x0, x1):.1f} {CY - 34} L{max(x0, x1):.1f} {CY + 34} L{min(x0, x1):.1f} {CY + 34} Z" fill="#fff"/>\n'
s += pole(180, -1) + pole(0, 1)
s += f'<circle cx="{CX}" cy="{CY}" r="{RA}"/>\n'
for a in list(range(-70, 71, 20)) + list(range(110, 251, 20)):      # conductors
    x, y = P(RC, a)
    s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" stroke="{RED}"/>\n'
    if 90 < a < 270:                                                 # into page (x)
        s += f'<path d="M{x - 4:.1f} {y - 4:.1f} L{x + 4:.1f} {y + 4:.1f} M{x - 4:.1f} {y + 4:.1f} L{x + 4:.1f} {y - 4:.1f}" stroke="{RED}"/>\n'
    else:                                                            # out of page (dot)
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{RED}" stroke="none"/>\n'
for a in (90, 270):                                                  # brushes on geometric neutral
    x, y = P(RA + 7, a)
    s += f'<rect x="{x - 7:.1f}" y="{y - 7:.1f}" width="14" height="14" fill="#fff"/>\n'
s += f'<path d="M{CX} {CY - 150} L{CX} {CY + 150}" stroke-dasharray="6 5" stroke-width="1"/>\n'   # GNP
th = math.radians(20)
s += f'<path d="M{CX + 150 * math.sin(th):.1f} {CY - 150 * math.cos(th):.1f} L{CX - 150 * math.sin(th):.1f} {CY + 150 * math.cos(th):.1f}" stroke="{BLUE}" stroke-dasharray="8 5"/>\n'
s += arrow(CX - 52, CY, CX + 52, CY)                                 # Phi_f
s += arrow(CX, CY - 30, CX, CY + 40)                                 # F_a
s += f'<path d="M{CX - 56 * math.cos(th):.1f} {CY - 56 * math.sin(th):.1f} L{CX + 50 * math.cos(th):.1f} {CY + 50 * math.sin(th):.1f}" stroke-dasharray="4 3"/>\n'
s += arrow(CX + 46 * math.cos(th), CY + 46 * math.sin(th), CX + 58 * math.cos(th), CY + 58 * math.sin(th))
r = 112                                                              # CCW rotation arrow above armature
q1, q2 = P(r, 98), P(r, 116)
s += f'<path d="M{q1[0]:.1f} {q1[1]:.1f} A{r} {r} 0 0 0 {q2[0]:.1f} {q2[1]:.1f}"/>\n'
q3 = P(r, 122)
s += arrow(q2[0], q2[1], q3[0], q3[1])
s += end_group()
s += text(CX - RS2 - 20, CY + 6, [("t", "N")], anchor="middle")
s += text(CX + RS2 + 20, CY + 6, [("t", "S")], anchor="middle")
s += text(*P(140, 140), [("t", "增強")], anchor="end")
s += text(*P(140, 222), [("t", "減弱")], anchor="end")
s += text(*P(140, 40), [("t", "減弱")])
s += text(*P(146, -42), [("t", "增強")])
s += text(CX + 22, CY - 8, [("n", "Φ"), ("vsub", "f")])
s += text(CX + 8, CY + 58, [("v", "F"), ("vsub", "a")])
s += text(CX + 28, CY + 34, [("n", "Φ"), ("vsub", "r")])
s += text(*P(132, 106), [("t", "旋轉")], anchor="end")
s += text(CX + 4, CY - 156, [("t", "幾何中性面")], anchor="middle")
s += ctext(BLUE, CX - 56, CY + 166, [("t", "磁中性面")], anchor="middle")
X = 400
s += text(X, 70, [("n", "Φ"), ("vsub", "f"), ("t", "：主磁極磁通（直軸）")])
s += text(X, 96, [("v", "F"), ("vsub", "a"), ("t", "：電樞磁勢（交軸，與 "), ("n", "Φ"), ("vsub", "f"), ("t", " 垂直）")])
s += text(X, 122, [("n", "Φ"), ("vsub", "r"), ("t", "：合成磁通，向下偏轉")])
s += ctext(RED, X, 158, [("t", "⊗ 流入紙面　⊙ 流出紙面（電樞電流）")])
s += text(X, 194, [("t", "N 極上緣、S 極下緣磁通增強；")])
s += text(X, 218, [("t", "另一緣減弱 → 磁通畸變")])
s += ctext(BLUE, X, 254, [("t", "磁中性面逆旋轉方向偏移")])
s += text(X, 278, [("t", "（電動機）；電刷仍在幾何中性面")])
s += text(X, 302, [("t", "→ 換向線圈有殘餘電勢、火花")])
s += text(X, 338, [("t", "鐵心飽和時增強側增不上去，")])
s += text(X, 362, [("t", "總磁通略減（去磁效應）")])
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-108-04-5-armature-reaction.svg'), 'w').write(s)
print(len(s))
