"""EE-108-04-5 fig 1: 6/4 switched reluctance motor cross-section (rotor aligned with phase A)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
W, H = 660, 420; CX, CY = 190, 200
RO, RY, RSP, RRP, RRC, RSH = 160, 128, 74, 67, 42, 12
WS, WR = 38, 40                                   # stator / rotor pole widths
def G(u, v, th):                                  # local (u along pole axis, v across) -> svg xy
    t = math.radians(th)
    return (CX + u * math.cos(t) - v * math.sin(t), CY - (u * math.sin(t) + v * math.cos(t)))
def salient(n, th0, r_tip, r_base, w, outward):
    """closed contour of n parallel-sided poles on a base circle (outward=True: rotor poles)."""
    ub = math.sqrt(r_base ** 2 - (w / 2) ** 2)
    d = ''
    for k in range(n):
        th = th0 + 360 / n * k
        a = G(ub, -w / 2, th); b = G(math.sqrt(r_tip ** 2 - (w / 2) ** 2), -w / 2, th)
        c = G(math.sqrt(r_tip ** 2 - (w / 2) ** 2), w / 2, th); e = G(ub, w / 2, th)
        sweep_tip = 0                      # CCW traversal on screen
        d += (f'M{a[0]:.1f} {a[1]:.1f} ' if k == 0 else f'L{a[0]:.1f} {a[1]:.1f} ')
        d += f'L{b[0]:.1f} {b[1]:.1f} A{r_tip} {r_tip} 0 0 {sweep_tip} {c[0]:.1f} {c[1]:.1f} L{e[0]:.1f} {e[1]:.1f} '
        nxt = G(ub, -w / 2, th + 360 / n)
        d += f'A{r_base} {r_base} 0 0 {sweep_tip} {nxt[0]:.1f} {nxt[1]:.1f} '
    return d + 'Z'
s = header(W, H)
s += f'<path d="M{CX + RO} {CY} A{RO} {RO} 0 1 0 {CX - RO} {CY} A{RO} {RO} 0 1 0 {CX + RO} {CY} Z ' \
     + salient(6, 90, RSP, RY, WS, False) + '" fill-rule="evenodd" fill="#fff"/>\n'
s += f'<path d="{salient(4, 90, RRP, RRC, WR, True)}"/>\n'
s += f'<circle cx="{CX}" cy="{CY}" r="{RSH}"/>\n'
for k in range(6):                                # concentrated coils, both sides of each stator pole
    th = 90 + 60 * k
    for sgn in (-1, 1):
        pts = [G(u, sgn * v, th) for u, v in ((RSP + 12, WS / 2), (RY - 8, WS / 2), (RY - 8, WS / 2 + 11), (RSP + 12, WS / 2 + 11))]
        s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f' Z" fill="{FILL_BLUE}"/>\n'
gx, gy = G(RSP - 3.5, 0, 90)
s += line(gx, gy, 400, 58)
s += line(*G(RY - 22, WS / 2 + 11, 30), 400, 180)
s += line(*G(144, 0, 0), 400, 302)
s += line(*G(54, 0, 0), 400, 238)
s += end_group()
for k, lab in enumerate(("A", "C′", "B", "A′", "C", "B′")):     # phase labels outside the yoke
    x, y = G(RO + 16, 0, 90 + 60 * k)
    s += text(x, y + 6, [("t", lab)], anchor="middle")
s += text(406, 54, [("t", "氣隙（定、轉子極面之間，很窄）")])
s += text(406, 76, [("t", "對齊位置磁阻最小")])
s += text(406, 176, [("t", "定子集中繞組（每極一個線圈；")])
s += text(406, 196, [("t", "對向兩極串聯為一相，如 A–A′）")])
s += text(406, 236, [("t", "轉子：凸極疊片鐵心（4 極），")])
s += text(406, 256, [("t", "無繞組、無永磁體")])
s += text(406, 308, [("t", "定子：凸極疊片鐵心（6 極）")])
s += text(W / 2, H - 12, [("t", "6/4 切換式磁阻電動機（圖為 A 相激磁、轉子對齊 A–A′）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-108-04-5-srm.svg'), 'w').write(s)
print(len(s))
