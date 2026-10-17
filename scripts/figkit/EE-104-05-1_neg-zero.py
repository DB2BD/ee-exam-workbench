import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 610
lab = lambda X, Y, parts, a="middle": text(X, Y, parts, anchor=a)
s = header(W, H)
t = ""
# ---------- (a) negative sequence: Fig. 1 topology, sources shorted ----------
YT, YR = 60, 230
XG, XT, XB, XS = 40, 236, 450, 690
s += line(XG, YT, XG, YR) + line(XS, YT, XS, YR)                                  # sources shorted
s += line(XG, YT, 80, YT) + coil(80, YT, 190, YT, turns=4) + line(190, YT, XT, YT)
s += line(XT, YT, 266, YT) + coil(266, YT, 376, YT, turns=4) + line(376, YT, XB, YT)
s += line(XB, YT, 545, YT) + coil(545, YT, 645, YT, turns=4) + line(645, YT, XS, YT)
for X in (XT, XB):
    s += line(X, YT, X, 72) + coil(X, 72, X, 112, turns=3) + line(X, 112, X, 120)
    s += resistor(X, 120, X, 170) + line(X, 170, X, 178) + coil(X, 178, X, 218, turns=3) + line(X, 218, X, YR)
s += line(XG, YR, XS, YR) + line(345, YR, 345, YR + 4) + ground(345, YR + 4)
s += dot(XT, YT) + dot(XB, YT) + dot(XT, YR) + dot(XB, YR)
s += line(XB, YT, XB, YT - 22)                                                    # fault terminal
t += ctext(RED, XB + 8, YT - 14, [("v", "F")])
t += lab(135, YT - 12, [("v", "j"), ("n", "0.25")]) + lab(321, YT - 12, [("v", "j"), ("n", "0.15")]) + lab(595, YT - 12, [("v", "j"), ("n", "0.025")])
for X, x1, r, x2 in ((XT, "1.6", "16", "12"), (XB, "1.0", "8", "6")):
    t += lab(X + 14, 98, [("v", "j"), ("n", x1)], "start") + lab(X + 14, 150, [("n", r)], "start") + lab(X + 14, 204, [("v", "j"), ("n", x2)], "start")
t += lab(XG + 12, 150, [("t", "電源短路")], "start") + lab(XS - 12, 150, [("t", "電源短路")], "end")
t += lab(360, YR + 40, [("t", "（a）負序網路：與圖 1 相同的阻抗，兩電源短路")])
# ---------- (b) zero sequence ----------
Y0, YG = 330, 530
XGN, XAT, XES, XB0, XSY = 130, 270, 390, 470, 660
# generator node: j0.12 + 3Rn,G to reference; MT_R delta side open
s += line(XGN, Y0, XGN, 350) + coil(XGN, 350, XGN, 410, turns=3) + line(XGN, 410, XGN, 425) + resistor(XGN, 425, XGN, 505) + line(XGN, 505, XGN, YG)
s += line(XGN, Y0, 190, Y0) + dot(XGN, Y0)
# AT_R secondary island: j1.6 + 3Rn,AT to reference
s += line(XAT, Y0, XAT, 350) + coil(XAT, 350, XAT, 410, turns=3) + line(XAT, 410, XAT, 425) + resistor(XAT, 425, XAT, 505) + line(XAT, 505, XAT, YG)
s += dot(XAT, Y0)
# MT_R grounded-Y side: bus - j0.10 - ES - reference
s += line(XES, Y0, 400, Y0) + coil(400, Y0, 455, Y0, turns=3) + line(455, Y0, XB0, Y0)
s += line(XES, Y0, XES, 410) + line(XES, 410, XES - 16, 440) + line(XES, 446, XES, YG) + dot(XES, 410) + dot(XES, 446)
# ST_R: bus - j1.0 - 78.75 - open (delta load)
s += line(XB0, Y0, XB0, 350) + coil(XB0, 350, XB0, 400, turns=3) + line(XB0, 400, XB0, 410) + resistor(XB0, 410, XB0, 480) + line(XB0, 480, XB0, 490)
s += f'<circle cx="{XB0}" cy="494" r="4"/>\n'
# system: bus - j0.025 - reference
s += line(XB0, Y0, 540, Y0) + coil(540, Y0, 620, Y0, turns=3) + line(620, Y0, XSY, Y0) + line(XSY, Y0, XSY, YG)
s += line(XGN, YG, XSY, YG) + line(570, YG, 570, YG + 4) + ground(570, YG + 4)
s += dot(XB0, Y0) + line(XB0, Y0, XB0, Y0 - 22)
t += ctext(RED, XB0 + 8, Y0 - 14, [("v", "F")])
t += lab(XGN, Y0 - 16, [("t", "發電機端")]) + lab(196, Y0 + 5, [("t", "Δ 開路")], "start")
t += lab(XGN - 12, 386, [("v", "j"), ("n", "0.12")], "end") + lab(XGN - 12, 460, [("n", "3"), ("v", "R"), ("vsub", "n,G")], "end") + lab(XGN - 12, 482, [("n", "= 9259.26")], "end")
t += lab(XAT + 10, Y0 - 16, [("v", "AT"), ("vsub", "R"), ("t", " 4.16 kV 側")])
t += lab(XAT + 12, 386, [("v", "j"), ("n", "1.6")], "start") + lab(XAT + 12, 460, [("n", "3"), ("v", "R"), ("vsub", "n,AT")], "start") + lab(XAT + 12, 482, [("n", "= 433.38")], "start")
t += lab(427, Y0 - 16, [("v", "j"), ("n", "0.10")]) + lab(XES - 22, 432, [("n", "ES")], "end")
t += lab(XB0 + 12, 380, [("v", "j"), ("n", "1.0（"), ("v", "ST"), ("vsub", "R"), ("n", "）")], "start") + lab(XB0 + 12, 440, [("n", "3"), ("v", "R"), ("vsub", "n,ST")], "start") + lab(XB0 + 12, 462, [("n", "= 78.75")], "start")
t += lab(XB0 + 12, 500, [("t", "負載 B（Δ）開路")], "start")
t += lab(580, Y0 - 16, [("v", "j"), ("n", "0.025")]) + lab(580, Y0 + 24, [("t", "系統")]) + lab(427, Y0 + 24, [("v", "MT"), ("vsub", "R")])
t += lab(360, YG + 44, [("t", "（b）零序網路：Δ 側開路；ES 切離時 "), ("v", "j"), ("n", "0.10"), ("t", " 支路斷開")])
s += end_group() + t + footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-104-05-1-neg-zero.svg'), 'w').write(s)
print(len(s))
