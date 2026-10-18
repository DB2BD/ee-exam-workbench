"""EE-114-06-4 Y-Delta starter main circuit, part (一).
L1, L2, L3 -> main contactor MC -> overload relay OL -> winding starts U1, V1, W1.
Winding ends U2, V2, W2 -> MC-Y (shorted: star point, starting)
                      -> MC-Delta back to the lines: W2->L1, U2->L2, V2->L3 (running, delta).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def contact(x, y1, y2):
    """Normally-open contactor contact on a vertical wire between y1 (top) and y2 (bottom)."""
    return (line(x, y1, x, y1 + 8) + f'<circle cx="{x}" cy="{y1 + 11}" r="3" fill="#fff"/>\n'
            + line(x, y2 - 8, x, y2) + f'<circle cx="{x}" cy="{y2 - 11}" r="3" fill="#fff"/>\n'
            + line(x, y2 - 14, x - 12, y1 + 16))
def vhop(x, y1, y2, cross, r=6):
    """vertical wire y1 (top) -> y2 (bottom) hopping over horizontal wires at y in cross."""
    d = f'M{x} {y1} '
    for yc in sorted(cross):
        d += f'L{x} {yc - r} A{r} {r} 0 0 1 {x} {yc + r} '
    return f'<path d="{d}L{x} {y2}"/>\n'
def hhop(y, x1, x2, cross, r=6):
    """horizontal wire x1 -> x2 (either direction) hopping over vertical wires at x in cross."""
    sgn = 1 if x2 > x1 else -1
    d = f'M{x1} {y} '
    for xc in sorted(cross, reverse=(sgn < 0)):
        d += f'L{xc - sgn * r} {y} A{r} {r} 0 0 {1 if sgn > 0 else 0} {xc + sgn * r} {y} '
    return f'<path d="{d}L{x2} {y}"/>\n'
W, H = 640, 590; s = header(W, H); lab = ''
X = {"L1": 140, "L2": 200, "L3": 260}
yTop, yMC1, yMC2, yOL, yTap = 40, 70, 110, 150, {"L1": 200, "L2": 215, "L3": 230}
yU1, yU2 = 262, 358            # winding start / end terminals
yH = {"W2": 410, "U2": 395, "V2": 380}       # horizontal run from each winding end to its MC-Delta column
CD = {"W2": 380, "U2": 430, "V2": 480}       # MC-Delta columns
TO = {"W2": "L1", "U2": "L2", "V2": "L3"}
XE = {"U2": 140, "V2": 200, "W2": 260}       # winding ends: U at L1 column, V at L2, W at L3
yY1, yY2, yStar = 430, 470, 490
# supply lines, MC, OL down to winding starts
for k, x in X.items():
    s += line(x, yTop, x, yMC1) + contact(x, yMC1, yMC2) + line(x, yMC2, x, yOL - 10)
    s += f'<rect x="{x - 7}" y="{yOL - 10}" width="14" height="20" fill="#fff"/>\n'
    s += line(x, yOL + 10, x, yU1 - 4) + dot(x, yTap[k])
    s += f'<circle cx="{x}" cy="{yU1}" r="4" fill="#fff"/>\n'
s += f'<path d="M{X["L1"] - 20} {(yMC1 + yMC2) / 2} L{X["L3"] + 10} {(yMC1 + yMC2) / 2}" stroke-width="1" stroke-dasharray="4 3"/>\n'
# windings
for x in X.values():
    s += coil(x, yU1 + 4, x, yU2 - 4, turns=5, r=7)
    s += f'<circle cx="{x}" cy="{yU2}" r="4" fill="#fff"/>\n'
# winding ends down to MC-Y, star bar
for e, x in XE.items():                          # plain verticals; the horizontals hop over them
    s += line(x, yU2 + 4, x, yY1) + dot(x, yH[e]) + contact(x, yY1, yY2) + line(x, yY2, x, yStar)
s += line(XE["U2"], yStar, XE["W2"], yStar) + dot(XE["V2"], yStar)
s += f'<path d="M{XE["U2"] - 20} {(yY1 + yY2) / 2} L{XE["W2"] + 10} {(yY1 + yY2) / 2}" stroke-width="1" stroke-dasharray="4 3"/>\n'
# MC-Delta: from winding end node right to its column, up through the contact, then left to its supply line tap
yD1, yD2 = 290, 330
for e in ("V2", "U2", "W2"):
    xe, xc, y = XE[e], CD[e], yH[e]
    s += hhop(y, xe, xc, [xv for xv in XE.values() if xv > xe] + [CD[k] for k in CD if CD[k] < xc and yH[k] > y])
    top = yTap[TO[e]]
    s += line(xc, top, xc, yD1) + contact(xc, yD1, yD2) + line(xc, yD2, xc, y)
    xl = X[TO[e]]
    s += hhop(top, xc, xl, [xv for xv in X.values() if xv > xl] + [CD[k] for k in CD if CD[k] < xc])
s += f'<path d="M{CD["W2"] - 20} {(yD1 + yD2) / 2} L{CD["V2"] + 10} {(yD1 + yD2) / 2}" stroke-width="1" stroke-dasharray="4 3"/>\n'
s += end_group()
for k, x in X.items():
    lab += text(x, yTop - 10, [("v", "L"), ("sub", k[1])], anchor="middle")
lab += text(X["L3"] + 18, (yMC1 + yMC2) / 2 + 5, [("n", "MC"), ("t", "（主）")])
lab += text(X["L3"] + 18, yOL + 5, [("n", "OL")])
for x, nm in zip(X.values(), ("U", "V", "W")):
    lab += text(x - 10, yU1 + 5, [("v", nm), ("sub", "1")], anchor="end")
    lab += text(x - 10, yU2 + 5, [("v", nm), ("sub", "2")], anchor="end")
lab += text(XE["W2"] + 26, (yY1 + yY2) / 2 + 5, [("n", "MC-Y")])
lab += text(XE["V2"], yStar + 22, [("t", "Y 點（起動）")], anchor="middle")
lab += text(CD["V2"] + 18, (yD1 + yD2) / 2 + 5, [("n", "MC-Δ")])
lab += text(350, 452, [("n", "MC-Δ"), ("t", "："), ("v", "W"), ("sub", "2"), ("n", "→"), ("v", "L"), ("sub", "1"), ("t", "、"), ("v", "U"), ("sub", "2"), ("n", "→"), ("v", "L"), ("sub", "2"), ("t", "、"), ("v", "V"), ("sub", "2"), ("n", "→"), ("v", "L"), ("sub", "3")])
lab += text(350, 476, [("t", "（運轉：三繞組首尾相接成 Δ）")])
lab += text(W / 2, 552, [("t", "起動：MC＋MC-Y 閉合（Y 接）→ 延時 → MC-Y 斷開、MC-Δ 閉合（Δ 接）")], anchor="middle")
lab += text(W / 2, 576, [("t", "MC-Y 與 MC-Δ 機械＋電氣互鎖；跳線處為交越不相接，實心點為連接點")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-114-06-4-starter.svg'
out.write_text(s); print(out.name, len(s))
