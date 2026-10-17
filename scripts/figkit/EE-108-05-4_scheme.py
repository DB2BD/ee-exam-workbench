import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def ct(x1, x2, y, r=None):
    """Bar-primary CT drawn as two humps over the line (as in the exam figure), leads at x1 and x2."""
    r = (x2 - x1) / 4
    return f'<path d="M{x1} {y} A{r} {r} 0 0 1 {x1 + 2 * r} {y} A{r} {r} 0 0 1 {x2} {y}"/>\n'
def dashed(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke-width="1" stroke-dasharray="5 4"/>\n'
# Reference directions follow the exam figure: I1 leaves CT1 down its outer lead and returns through coil 1
# (right-to-left); I2 leaves CT2 down its inner lead, flows right-to-left through coil 2; coil 3 carries
# I1 - I2 upward from the bottom pilot wire to the junction.
W, H = 680, 430
YL, YC, YBUS = 130, 280, 380
X1o, X1i, X2i, X2o, XJ = 110, 190, 470, 550, 330
s = header(W, H)
s += line(30, YL, 650, YL)
s += ct(X1o, X1i, YL) + ct(X2i, X2o, YL)
s += f'<rect x="280" y="{YL - 8}" width="100" height="16" fill="#fff" stroke="none"/>\n' + coil(280, YL, 380, YL, turns=5)
s += dot(X1o - 12, YL - 12) + dot(X2i - 12, YL - 12)
s += dashed(X1o, 40, X1o, 410) + dashed(X2o, 40, X2o, 410)
s += line(X1o, YL, X1o, YBUS) + line(X2o, YL, X2o, YBUS) + line(X1o, YBUS, X2o, YBUS)
s += line(X1i, YL, X1i, YC) + line(X1i, YC, 230, YC) + coil(230, YC, 310, YC, turns=4) + line(310, YC, 350, YC)
s += coil(350, YC, 430, YC, turns=4) + line(430, YC, X2i, YC) + line(X2i, YC, X2i, YL)
s += line(XJ, YC, XJ, 300) + coil(XJ, 300, XJ, 360, turns=3) + line(XJ, 360, XJ, YBUS)
s += dot(XJ, YC) + dot(XJ, YBUS) + dot(X1o, YL) + dot(X1i, YL) + dot(X2i, YL) + dot(X2o, YL) + dot(410, YL)
s += f'<path d="M410 {YL} L402 {YL + 18} L418 {YL + 22} L410 {YL + 42}" stroke="{RED}"/>\n'
s += arrow(410, YL + 30, 410, YL + 44, color=RED)
s += arrow(40, YL - 16, 85, YL - 16, color=RED) + arrow(590, YL - 16, 635, YL - 16, color=RED)
s += arrow(X1o - 14, 200, X1o - 14, 244, color=RED) + arrow(X2i + 14, 170, X2i + 14, 214, color=RED)
s += arrow(300, YC + 20, 250, YC + 20, color=RED) + arrow(450, YC + 20, 400, YC + 20, color=RED)
s += arrow(XJ + 24, 352, XJ + 24, 308, color=RED)
s += end_group()
s += ctext(RED, 60, YL - 26, [("v", "I"), ("sub", "1"), ("n", "′")], anchor="middle")
s += ctext(RED, 612, YL - 26, [("v", "I"), ("sub", "2"), ("n", "′")], anchor="middle")
s += ctext(RED, 424, YL + 50, [("v", "I"), ("vsub", "f"), ("n", "′")])
s += ctext(RED, X1o - 20, 228, [("v", "I"), ("sub", "1")], anchor="end")
s += ctext(RED, X2i + 22, 198, [("v", "I"), ("sub", "2")])
s += ctext(RED, 275, YC + 42, [("v", "I"), ("sub", "1")], anchor="middle")
s += ctext(RED, 425, YC + 42, [("v", "I"), ("sub", "2")], anchor="middle")
s += ctext(RED, XJ + 32, 336, [("v", "I"), ("sub", "1"), ("n", " − "), ("v", "I"), ("sub", "2")])
s += text(330, YL - 22, [("t", "發電機相繞組")], anchor="middle")
s += text(150, YL - 34, [("n", "CT1")], anchor="middle")
s += text(510, YL - 34, [("n", "CT2")], anchor="middle")
s += text(270, YC - 18, [("n", "1")], anchor="middle")
s += text(390, YC - 18, [("n", "2")], anchor="middle")
s += text(XJ - 10, 336, [("n", "3")], anchor="end")
s += text(330, 32, [("t", "← 保護區（兩 CT 之間）→")], anchor="middle")
s += text(340, 418, [("t", "1、2：抑制線圈（流 "), ("v", "I"), ("sub", "1"), ("t", "、"), ("v", "I"), ("sub", "2"), ("t", "）；3：動作線圈（流 "), ("v", "I"), ("sub", "1"), ("n", " − "), ("v", "I"), ("sub", "2"), ("t", "）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-4-scheme.svg'), 'w').write(s)
print(len(s))
