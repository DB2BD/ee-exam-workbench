"""EE-107-02-1: pn junction depletion region (x_p, x_n), space charge rho(x) and field E(x)."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

XJ = 330                        # metallurgical junction
K = 1.4                         # px per nm
XP, XN = XJ - K * 73.85, XJ + K * 184.63
XL, XR = 50, 690


def dim(x1, x2, y):
    """Two-headed dimension arrow."""
    m = (x1 + x2) / 2
    return arrow(m, y, x1, y) + arrow(m, y, x2, y)


W, H = 720, 430
s = header(W, H)
# panel 1: the junction bar with the depletion region tinted (p side blue, n side red)
s += f'<rect x="{XP:.1f}" y="40" width="{XJ - XP:.1f}" height="50" fill="{FILL_BLUE}" stroke="none"/>\n'
s += f'<rect x="{XJ}" y="40" width="{XN - XJ:.1f}" height="50" fill="{FILL_RED}" stroke="none"/>\n'
s += f'<rect x="{XL}" y="40" width="{XR - XL}" height="50"/>\n' + line(XJ, 40, XJ, 90)
s += dashed(XP, 40, XP, 156) + dashed(XN, 40, XN, 156)
s += dim(XP, XJ, 122) + dim(XJ, XN, 122) + dim(XP, XN, 150)
# panel 2: rho(x); zero at y = 232, 10 px per 1e16 cm^-3
s += arrow(XL, 232, XR, 232)
s += f'<path d="M{XP:.1f} 232 L{XP:.1f} 282 L{XJ} 282 L{XJ} 212 L{XN:.1f} 212 L{XN:.1f} 232" stroke-width="2.2"/>\n'
# panel 3: E(x) (points from n to p, i.e. negative); zero at y = 330
s += arrow(XL, 330, XR, 330)
s += f'<path d="M{XP:.1f} 330 L{XJ} 400 L{XN:.1f} 330" stroke-width="2.2"/>\n'
s += dashed(XJ, 330, XJ, 400)
s += end_group()
s += text(70, 30, [("t", "p 型 "), ("v", "N"), ("vsub", "A"), ("n", " = 5×10"), ("n", "<tspan class=\"n\" baseline-shift=\"super\" font-size=\"11\">16</tspan>"), ("n", " cm"), ("n", "<tspan class=\"n\" baseline-shift=\"super\" font-size=\"11\">−3</tspan>")])
s += text(690, 30, [("t", "n 型 "), ("v", "N"), ("vsub", "D"), ("n", " = 2×10"), ("n", "<tspan class=\"n\" baseline-shift=\"super\" font-size=\"11\">16</tspan>"), ("n", " cm"), ("n", "<tspan class=\"n\" baseline-shift=\"super\" font-size=\"11\">−3</tspan>")], anchor="end")
s += text((XP + XJ) / 2, 72, [("n", "− − −")], anchor="middle")
s += text((XJ + XN) / 2, 72, [("n", "+ + + + +")], anchor="middle")
s += text(120, 72, [("t", "中性 p 區")], anchor="middle")
s += text(645, 72, [("t", "中性 n 區")], anchor="middle")
s += text((XP + XJ) / 2, 106, [("v", "x"), ("vsub", "p"), ("n", " = 73.85 nm")], anchor="middle")
s += text((XJ + XN) / 2, 106, [("v", "x"), ("vsub", "n"), ("n", " = 184.63 nm")], anchor="middle")
s += text((XP + XN) / 2, 172, [("v", "W"), ("sub", "dep"), ("n", " = 258.48 nm")], anchor="middle")
s += text(XL + 4, 212, [("v", "ρ"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(XP - 6, 280, [("n", "−"), ("v", "qN"), ("vsub", "A")], anchor="end")
s += text(XN + 6, 216, [("n", "+"), ("v", "qN"), ("vsub", "D")])
s += ctext(XJ + 20, 262, [("t", "面積相等："), ("v", "N"), ("vsub", "A"), ("v", "x"), ("vsub", "p"), ("n", " = "), ("v", "N"), ("vsub", "D"), ("v", "x"), ("vsub", "n")], color="#000")
s += text(XR - 4, 252, [("v", "x")], anchor="end")
s += text(XL + 4, 318, [("v", "E"), ("n", "("), ("v", "x"), ("n", ")")])
s += text(XJ - 8, 412, [("n", "−"), ("v", "E"), ("sub", "max"), ("t", "（接面處）")], anchor="end")
s += ctext(XJ + 30, 412, [("t", "三角形面積 = "), ("v", "V"), ("sub", "0")], color=BLUE)
s += text(XR - 4, 350, [("v", "x")], anchor="end")
s += footer()
write('EE-107-02-1-depletion.svg', s)
