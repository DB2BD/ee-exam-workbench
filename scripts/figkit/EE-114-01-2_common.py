"""Shared drawing for EE-114-01-2: the original circuit at a-b open / shorted, and the Norton equivalent."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

YT, YB = 90, 250
XR6, XS, XA, XT = 70, 170, 420, 520
VA = [("v", "v"), ("vsub", "a")]


def circuit(mode):
    """mode 'open' (a-b open) or 'short' (a-b shorted)."""
    sh = mode == 'short'
    W, H = 640, 300
    s = header(W, H)
    s += resistor(XR6, YT, XR6, YB, zigs=6, lead=50)
    s += isrc(XS, YB, XS, YT)                                   # 10 A, arrow up into node n
    s += line(XR6, YT, 240, YT) + dep_vsrc(240, YT, 320, YT) + line(320, YT, XT - 4, YT)
    s += resistor(XA, YT, XA, YB, zigs=6, lead=50) + line(XR6, YB, XT - 4, YB)
    s += terminal(XT, YT) + terminal(XT, YB)
    for p in ((XS, YT), (XA, YT), (XS, YB), (XA, YB)):
        s += dot(*p)
    if sh:
        s += line(XT + 4, YT, 560, YT) + line(560, YT, 560, YB) + line(560, YB, XT + 4, YB)
        s += tint_arrow(578, 150, 578, 192)                     # I_sc down the short (a -> b)
        s += tint_arrow(262, YT - 26, 300, YT - 26)             # 10 A through the dependent source
    else:
        s += tint_arrow(XR6 - 16, 148, XR6 - 16, 190)           # v_n/6 down the 6 ohm
        s += tint_arrow(262, YT - 26, 300, YT - 26)             # v_a/2 through the dependent source
        s += tint_arrow(XA - 16, 148, XA - 16, 190)             # v_a/2 down the 2 ohm
    s += end_group()
    s += text(XS - 6, YT - 12, [("v", "n")], anchor="end")
    if sh:
        s += text(XT, YT - 12, [("v", "a")], anchor="middle") + text(XT, YB + 24, [("v", "b")], anchor="middle")
    else:
        s += text(XT + 14, YT + 5, [("v", "a")]) + text(XT + 14, YB + 5, [("v", "b")])
    s += text(XS + 24, 175, [("n", "10 A")])
    s += text(280, YT + 34, [("n", "2"), ("v", "V"), ("vsub", "x")], anchor="middle")
    s += ttext(XA + 16, YT + 46, [("n", "+")], color=BLUE)
    s += ttext(XA + 16, YB - 30, [("n", "−")], color=BLUE)
    s += ttext(XA + 16, 175, [("v", "V"), ("vsub", "x")], color=BLUE)
    if sh:
        s += text(XR6 + 18, 175, [("n", "6 Ω")])
        s += text(XA - 22, 230, [("n", "2 Ω")], anchor="end")
        s += text(20, 30, [("v", "a"), ("t", "–"), ("v", "b"), ("t", " 短路："), ("v", "V"), ("vsub", "x"), ("n", " = 0 ⇒ "),
                           ("v", "v"), ("vsub", "n"), ("n", " = 0"), ("t", "，6 Ω、2 Ω 無電流")])
        s += ttext(281, YT - 34, [("n", "10 A")], anchor="middle", color=RED)
        s += ttext(592, 176, [("v", "I"), ("vsub", "sc")], color=RED)
    else:
        s += text(XR6 + 18, 175, [("n", "6 Ω")])
        s += text(XA - 22, 230, [("n", "2 Ω")], anchor="end")
        s += text(20, 30, [("v", "a"), ("t", "–"), ("v", "b"), ("t", " 開路：相依源支路電流 = 2 Ω 電流")])
        s += ttext(XR6 - 22, 176, [("v", "v"), ("vsub", "n"), ("n", "/6")], anchor="end", color=RED)
        s += ttext(281, YT - 34, VA + [("n", "/2")], anchor="middle", color=RED)
        s += ttext(XA - 22, 156, VA + [("n", "/2")], anchor="end", color=RED)
    s += footer()
    return s


def norton():
    W, H, X1, X2, XT2 = 520, 290, 160, 300, 420
    s = header(W, H)
    s += isrc(X1, YB, X1, YT) + resistor(X2, YT, X2, YB, zigs=6, lead=50)
    s += line(X1, YT, XT2 - 4, YT) + line(X1, YB, XT2 - 4, YB)
    s += terminal(XT2, YT) + terminal(XT2, YB) + dot(X2, YT) + dot(X2, YB)
    s += end_group()
    s += text(20, 30, [("t", "諾頓等效：電流源與電阻並聯，源內箭頭 "), ("v", "b"), ("n", " → "), ("v", "a")])
    s += text(X1 - 26, 166, [("v", "I"), ("vsub", "N"), ("n", " = 10 A")], anchor="end")
    s += text(X2 + 18, 166, [("v", "R"), ("vsub", "N"), ("n", " = 1 Ω")])
    s += text(XT2 + 14, YT + 5, [("v", "a")])
    s += text(XT2 + 14, YB + 5, [("v", "b")])
    s += ttext(XT2, YT + 34, [("n", "+")], anchor="middle", color=BLUE)
    s += ttext(XT2, YB - 22, [("n", "−")], anchor="middle", color=BLUE)
    s += ttext(XT2 - 8, 160, [("v", "V"), ("vsub", "ab")], anchor="middle", color=BLUE)
    s += ttext(XT2 - 8, 182, [("n", "= +10 V")], anchor="middle", color=BLUE)
    s += footer()
    return s
