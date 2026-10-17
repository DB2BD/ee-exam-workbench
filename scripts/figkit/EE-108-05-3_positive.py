import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def src(cx, cy, r=18):
    """EMF source drawn vertically, + on top."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}"/>\n' + line(cx - 5, cy - 9, cx + 5, cy - 9) + line(cx, cy - 14, cx, cy - 4)
            + line(cx - 5, cy + 9, cx + 5, cy + 9))
# Positive-sequence network on the 1000 MVA base: both EMFs = 1.03 pu (no prefault current),
# G1+T1 and G2+T2 meet at the HV bus H, line X_L runs to the fault point P.
W, H = 660, 380
XG1, XG2, XH, YT, YR = 60, 600, 330, 80, 320
YP = 230
s = header(W, H)
s += src(XG1, 200) + line(XG1, 182, XG1, YT) + line(XG1, 218, XG1, YR)
s += src(XG2, 200) + line(XG2, 182, XG2, YT) + line(XG2, 218, XG2, YR)
s += line(XG1, YT, 90, YT) + coil(90, YT, 170, YT, turns=4) + line(170, YT, 190, YT) + coil(190, YT, 270, YT, turns=4) + line(270, YT, XH, YT)
s += line(XG2, YT, 570, YT) + coil(570, YT, 490, YT, turns=4) + line(490, YT, 470, YT) + coil(470, YT, 390, YT, turns=4) + line(390, YT, XH, YT)
s += line(XH, YT, XH, 120) + coil(XH, 120, XH, 190, turns=4) + line(XH, 190, XH, YP)
s += line(XG1, YR, XG2, YR)
s += dot(XH, YT) + dot(XH, YP) + dot(XH, YR)
s += f'<path d="M{XH} {YP} L{XH} {YR}" stroke="{RED}" stroke-dasharray="5 4"/>\n'   # bolted fault P -> reference
s += arrow(XH + 18, 250, XH + 18, 292, color=RED)
s += arrow(282, YT - 14, 316, YT - 14, color=RED)
s += arrow(378, YT - 14, 344, YT - 14, color=RED)
s += end_group()
s += ctext(BLUE, XG1 + 26, 196, [("v", "E"), ("n", "″"), ("sub", "1")])
s += ctext(BLUE, XG1 + 26, 218, [("n", "1.03")])
s += ctext(BLUE, XG2 - 26, 196, [("v", "E"), ("n", "″"), ("sub", "2")], anchor="end")
s += ctext(BLUE, XG2 - 26, 218, [("n", "1.03")], anchor="end")
s += text(130, YT + 32, [("v", "jX"), ("vsub", "G"), ("sub", "1")], anchor="middle")
s += text(130, YT + 54, [("v", "j"), ("n", "0.10")], anchor="middle")
s += text(230, YT + 32, [("v", "jX"), ("vsub", "T"), ("sub", "1")], anchor="middle")
s += text(230, YT + 54, [("v", "j"), ("n", "0.175")], anchor="middle")
s += text(430, YT + 32, [("v", "jX"), ("vsub", "T"), ("sub", "2")], anchor="middle")
s += text(430, YT + 54, [("v", "j"), ("n", "0.20")], anchor="middle")
s += text(530, YT + 32, [("v", "jX"), ("vsub", "G"), ("sub", "2")], anchor="middle")
s += text(530, YT + 54, [("v", "j"), ("n", "0.1875")], anchor="middle")
s += text(XH - 16, 152, [("v", "jX"), ("vsub", "L")], anchor="end")
s += text(XH - 16, 174, [("v", "j"), ("n", "0.10")], anchor="end")
s += text(XH + 12, YT + 24, [("v", "H")])
s += text(XH - 12, YP + 6, [("v", "P")], anchor="end")
s += ctext(RED, XH + 28, 278, [("v", "I"), ("vsub", "f")])
s += ctext(RED, 290, YT - 26, [("v", "I"), ("vsub", "G"), ("sub", "1")], anchor="middle")
s += ctext(RED, 372, YT - 26, [("v", "I"), ("vsub", "G"), ("sub", "2")], anchor="middle")
s += text(XH, YR + 26, [("t", "參考點（中性點）")], anchor="middle")
s += text(XH, 368, [("t", "標么值，1000 MVA 基準；三相故障時 "), ("v", "P"), ("t", " 直接接到參考點")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-108-05-3-positive.svg'), 'w').write(s)
print(len(s))
