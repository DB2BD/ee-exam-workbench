"""Shared drawing for EE-104-01-1: the bridge circuit (open circuit / sources deactivated) and the Thevenin equivalent."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

X0, XC, XA, XT = 120, 300, 460, 570
YTOP, YM, YB = 70, 170, 290


def circuit(mode):
    """mode 'open' (V_th: node voltages, branch currents) or 'rth' (9 V shorted, 1.8 A opened)."""
    rth = mode == 'rth'
    W, H = 660, 350
    s = header(W, H)
    s += line(X0, YTOP, X0, YM)
    s += line(X0, YM, X0, YB) if rth else vsrc(X0, YM, X0, YB)
    s += line(X0, YTOP, 240, YTOP) + resistor(240, YTOP, 340, YTOP) + line(340, YTOP, XA, YTOP) + line(XA, YTOP, XA, YM)
    s += resistor(X0, YM, XC, YM, lead=50)
    if rth:
        s += line(XC, YM, 362, YM) + line(398, YM, XA, YM)       # current source removed: open gap
    else:
        s += isrc(XC, YM, XA, YM)
    s += line(XA, YM, XT - 4, YM) + terminal(XT, YM)
    s += resistor(XC, YM, XC, YB, lead=40) + resistor(XA, YM, XA, YB, lead=40)
    s += line(X0, YB, XC, YB) + resistor(XC, YB, XA, YB, lead=40) + line(XA, YB, XT - 4, YB) + terminal(XT, YB)
    s += line(X0, YB, X0, YB + 12) + ground(X0, YB + 12)
    for p in ((X0, YM), (XC, YM), (XA, YM), (XC, YB), (XA, YB)):
        s += dot(*p)
    if not rth:
        s += tint_arrow(370, YTOP + 18, 420, YTOP + 18)           # I_20: 9 V node -> a
        s += tint_arrow(XA - 20, 208, XA - 20, 250)               # I_60: a -> b (down)
        s += tint_arrow(410, YB + 20, 350, YB + 20)               # I_10: b -> ground (left)
    s += end_group()
    s += text(XT + 12, YM + 5, [("v", "a")]) + text(XT + 12, YB + 5, [("v", "b")])
    s += text(290, YTOP - 14, [("n", "20 Ω")], anchor="middle")
    s += text(210, YM - 14, [("n", "5 Ω")], anchor="middle")
    s += text(XC + 16, 236, [("n", "25 Ω")])
    s += text(XA + 16, 236, [("n", "60 Ω")])
    s += text(380, YB - 14, [("n", "10 Ω")], anchor="middle")
    if rth:
        s += text(20, 28, [("t", "求 "), ("v", "R"), ("vsub", "th"), ("t", "：9 V 短路、1.8 A 開路；5 Ω、25 Ω 與 "), ("v", "a"), ("t", "–"), ("v", "b"), ("t", " 間無通路")])
        s += text(X0 - 12, 236, [("t", "9 V 短路")], anchor="end")
        s += text(380, YM - 22, [("t", "1.8 A 開路")], anchor="middle")
        s += ttext(XT + 34, 236, [("v", "R"), ("vsub", "th")], anchor="middle", color=BLUE)
        s += f'<g fill="none" stroke="{BLUE}" stroke-width="1.5">' + arrow(XT + 34, 214, XT + 34, YM + 8, BLUE) + arrow(XT + 34, 244, XT + 34, YB - 8, BLUE) + '</g>\n'
    else:
        s += text(20, 28, [("t", "開路（"), ("v", "a"), ("t", "、"), ("v", "b"), ("t", " 無外接）；9 V 負端為參考地")])
        s += text(X0 - 24, 236, [("n", "9 V")], anchor="end")
        s += text(380, YM - 26, [("n", "1.8 A")], anchor="middle")
        s += ttext(XC + 8, YM + 24, [("v", "V"), ("vsub", "c")], color=BLUE)
        s += ttext(XA + 8, YM + 24, [("v", "V"), ("vsub", "a")], color=BLUE)
        s += ttext(XA + 8, YB - 10, [("v", "V"), ("vsub", "b")], color=BLUE)
        s += ttext(395, YTOP + 42, [("v", "I"), ("sub", "20")], anchor="middle", color=RED)
        s += ttext(XA - 28, 236, [("v", "I"), ("sub", "60")], anchor="end", color=RED)
        s += ttext(380, YB + 44, [("v", "I"), ("sub", "10")], anchor="middle", color=RED)
    s += footer()
    return s


def thevenin():
    W, H, XS, XR, XE = 520, 260, 130, 300, 420
    yt, yb = 80, 230
    s = header(W, H)
    s += vsrc(XS, yt, XS, yb) + line(XS, yt, 240, yt) + resistor(240, yt, 360, yt) + line(360, yt, XE - 4, yt)
    s += line(XS, yb, XE - 4, yb) + terminal(XE, yt) + terminal(XE, yb)
    s += end_group()
    s += text(20, 30, [("t", "戴維寧等效：電壓源串聯電阻，"), ("v", "a"), ("t", " 端為正")])
    s += text(XS - 26, 160, [("v", "V"), ("vsub", "th"), ("n", " = 30 V")], anchor="end")
    s += text(300, yt - 14, [("v", "R"), ("vsub", "th"), ("n", " = 20 Ω")], anchor="middle")
    s += text(XE + 14, yt + 5, [("v", "a")]) + text(XE + 14, yb + 5, [("v", "b")])
    s += ttext(XE, yt + 32, [("n", "+")], anchor="middle", color=BLUE)
    s += ttext(XE, yb - 20, [("n", "−")], anchor="middle", color=BLUE)
    s += ttext(XE - 10, 160, [("v", "V"), ("vsub", "ab")], anchor="end", color=BLUE)
    s += footer()
    return s
