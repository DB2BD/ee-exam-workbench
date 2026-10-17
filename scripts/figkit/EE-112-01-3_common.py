"""Shared drawing for EE-112-01-3: the CCVS circuit with the R_L port open / shorted, and the Norton equivalent."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

YT, YB = 90, 250
XS, X1, X2, XT = 70, 250, 460, 560


def V(name, sub, kind="sub"):
    return [("v", name), (kind, sub)]


def circuit(mode):
    """mode 'open' (R_L removed) or 'short' (R_L port shorted)."""
    sh = mode == 'short'
    W, H = 680, 300
    s = header(W, H)
    s += vsrc(XS, YT, XS, YB)
    s += line(XS, YT, 110, YT) + resistor(110, YT, 190, YT) + line(190, YT, 300, YT)
    s += dep_vsrc(300, YT, 380, YT) + line(380, YT, XT - 4, YT)
    s += resistor(X1, YT, X1, YB, zigs=6, lead=50) + resistor(X2, YT, X2, YB, zigs=6, lead=50)
    s += line(XS, YB, XT - 4, YB) + terminal(XT, YT) + terminal(XT, YB)
    for p in ((X1, YT), (X2, YT), (X1, YB), (X2, YB)):
        s += dot(*p)
    s += tint_arrow(132, YT + 16, 168, YT + 16)                 # i_x
    s += tint_arrow(X1 + 16, 148, X1 + 16, 188)                 # R2 current
    s += tint_arrow(322, YT + 26, 358, YT + 26)                 # CCVS current
    if sh:
        s += line(XT + 4, YT, 610, YT) + line(610, YT, 610, YB) + line(610, YB, XT + 4, YB)
        s += tint_arrow(628, 150, 628, 192)                     # I_sc
    else:
        s += tint_arrow(X2 + 16, 148, X2 + 16, 188)             # R3 current
    s += end_group()
    s += text(XS - 22, 166, V("v", "s", "vsub"), anchor="end")
    s += text(XS - 22, 188, [("n", "8 V")], anchor="end")
    s += text(150, YT - 14, V("R", "1") + [("n", " = 10 Ω")], anchor="middle")
    s += text(340, YT - 26, [("v", "r i"), ("vsub", "x"), ("n", " = 5"), ("v", "i"), ("vsub", "x")], anchor="middle")
    s += text(X1 - 18, 174, V("R", "2") + [("n", " = 10 Ω")], anchor="end")
    s += text(X2 - 18, 174, V("R", "3") + [("n", " = 10 Ω")], anchor="end")
    s += text(X1 + 6, YT - 12, V("v", "1"))
    s += text(X2 + 6, YT - 12, V("v", "2"))
    s += ttext(150, YT + 40, V("i", "x", "vsub"), anchor="middle", color=RED)
    s += ttext(X1 + 26, 174, V("v", "1") + [("n", "/10")], color=RED)
    if sh:
        s += text(20, 30, [("t", "負載端短路："), ("v", "v"), ("sub", "2"), ("n", " = 0"), ("t", "，"), ("v", "R"), ("sub", "3"),
                           ("t", " 無電流，CCVS 電流全部流入短路線")])
        s += ttext(340, YT + 52, V("I", "sc", "vsub"), anchor="middle", color=RED)
        s += ttext(640, 176, V("I", "sc", "vsub"), color=RED)
    else:
        s += text(20, 30, [("t", "負載端開路：CCVS 電流 = "), ("v", "R"), ("sub", "3"), ("t", " 電流 "), ("v", "v"), ("sub", "2"), ("n", "/10")])
        s += ttext(340, YT + 52, V("v", "2") + [("n", "/10")], anchor="middle", color=RED)
        s += ttext(X2 + 26, 174, V("v", "2") + [("n", "/10")], color=RED)
        s += ttext(XT, YT + 34, [("n", "+")], anchor="middle", color=BLUE)
        s += ttext(XT, YB - 22, [("n", "−")], anchor="middle", color=BLUE)
        s += ttext(XT + 14, 174, V("V", "oc", "vsub") + [("n", " = "), ("v", "v"), ("sub", "2")], color=BLUE)
    s += footer()
    return s


def norton():
    W, H, XA, XB, XP, XL = 560, 290, 150, 290, 400, 480
    s = header(W, H)
    s += isrc(XA, YB, XA, YT) + resistor(XB, YT, XB, YB, zigs=6, lead=50)
    s += line(XA, YT, XP - 4, YT) + line(XA, YB, XP - 4, YB)
    s += terminal(XP, YT) + terminal(XP, YB) + dot(XB, YT) + dot(XB, YB)
    s += ('<g stroke-dasharray="4 3">' + line(XP + 4, YT, XL, YT) + resistor(XL, YT, XL, YB, zigs=6, lead=50)
          + line(XL, YB, XP + 4, YB) + '</g>\n')
    s += end_group()
    s += text(20, 30, [("t", "由 "), ("v", "R"), ("vsub", "L"), ("t", " 端看入的諾頓等效：電流源箭頭指向上端（"), ("v", "v"), ("sub", "2"), ("t", " 端）")])
    s += text(XA - 26, 160, V("I", "N", "vsub") + [("n", " = 4/15 A")], anchor="end")
    s += text(XA - 26, 182, [("n", "= 266.67 mA")], anchor="end")
    s += text(XB + 16, 160, V("R", "N", "vsub") + [("n", " = 30/7 Ω")])
    s += text(XB + 16, 182, [("n", "= 4.29 Ω")])
    s += text(XL + 16, 174, V("R", "L", "vsub"))
    s += footer()
    return s
