"""Shared drawing for EE-106-01-4: symmetric (45 V / 45 V) and antisymmetric (15 V lower+ / 15 V upper+) excitations."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 330
XS1, XA, XT1, XM, XT2, XB, XS2 = 90, 150, 240, 350, 460, 550, 610
YT, YB = 100, 260


def cross(x1, y1, x2, y2, body=84):
    """Crossing 3-ohm branch: zig-zag next to the top node, plain wire down to the far bottom node."""
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    xe, ye = x1 + body * ux, y1 + body * uy
    return resistor(x1, y1, xe, ye, zigs=6, lead=12, amp=7) + line(xe, ye, x2, y2)


def along(x1, y1, x2, y2, t0, t1):
    """Red arrow on the straight part of a crossing wire, between fractions t0 and t1."""
    return tint_arrow(x1 + t0 * (x2 - x1), y1 + t0 * (y2 - y1), x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1))


def node(x, y, parts, anchor, color="#000"):
    return ttext(x, y, parts, anchor=anchor, color=color)


def figure(mode):
    sym = mode == 'sym'
    s = header(W, H)
    if not sym:
        s += f'<path d="M{XM} 64 L{XM} 296" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
    s += vsrc(XS1, YT, XS1, YB) if sym else vsrc(XS1, YB, XS1, YT)
    s += vsrc(XS2, YT, XS2, YB)
    for y in (YT, YB):
        s += line(XS1, y, XA, y) + resistor(XA, y, 220, y, lead=10) + line(220, y, XT1, y)
        s += resistor(XT1, y, XT2, y, lead=70)
        s += line(XT2, y, 480, y) + resistor(480, y, XB, y, lead=10) + line(XB, y, XS2, y)
    s += cross(XT1, YT, XT2, YB) + cross(XT2, YT, XT1, YB)
    for p in ((XT1, YT), (XT2, YT), (XT1, YB), (XT2, YB)):
        s += dot(*p)
    s += tint_arrow(602, YT - 14, 566, YT - 14)          # I_o reference: leftward out of the right source's + terminal
    if sym:   # the single series loop, all segments carry I_{o,s}
        s += tint_arrow(100, YT - 14, 136, YT - 14) + tint_arrow(136, YB + 14, 100, YB + 14)
        s += tint_arrow(566, YB + 14, 602, YB + 14)
        s += along(XT2, YT, XT1, YB, 0.62, 0.74) + along(XT1, YT, XT2, YB, 0.62, 0.74)
    s += end_group()
    if sym:
        s += text(20, 30, [("t", "對稱激勵：兩源皆 45 V；鏡像節點等電位，兩個 2 Ω 無電流，其餘元件串成一個迴路")])
    else:
        s += text(20, 30, [("t", "反對稱激勵：左源 15 V（下正）、右源 15 V（上正）；虛線為對稱軸")])
        s += ttext(XM, 56, [("t", "對稱軸電位 0")], anchor="middle", color=BLUE)
    src = "45 V" if sym else "15 V"
    s += text(XS1 - 24, (YT + YB) // 2 + 5, [("n", src)], anchor="end")
    s += text(XS2 + 24, (YT + YB) // 2 + 5, [("n", src)])
    for y, dy in ((YT, -14), (YB, 28)):
        s += text(185, y + dy, [("n", "1 Ω")], anchor="middle") + text(515, y + dy, [("n", "1 Ω")], anchor="middle")
        s += text(XM if sym else 300, y + dy, [("n", "2 Ω")], anchor="middle")
    s += text(XT1 + 14, 170, [("n", "3 Ω")], anchor="end") + text(XT2 - 14, 170, [("n", "3 Ω")])
    sub = [("v", "I"), ("vsub", "o,s")] if sym else [("v", "I"), ("vsub", "o,a")]
    s += ttext(584, YT - 24, sub, anchor="middle", color=RED)
    T = lambda k: [("v", "T"), ("sub", k)]
    B = lambda k: [("v", "B"), ("sub", k)]
    if sym:
        s += node(XT1, YT - 14, T("1"), "middle") + node(XT2, YT - 14, T("2"), "middle")
        s += node(XT1, YB + 28, B("1"), "middle") + node(XT2, YB + 28, B("2"), "middle")
    else:
        V = lambda n, k: [("v", "V"), ("vsub", n), ("sub", k)]
        s += node(XT1 - 8, 130, V("T", "1") + [("n", " = −"), ("v", "x")], "end", BLUE)
        s += node(XT2 + 8, 130, V("T", "2") + [("n", " = "), ("v", "x")], "start", BLUE)
        s += node(XT1 - 8, 242, V("B", "1") + [("n", " = −"), ("v", "y")], "end", BLUE)
        s += node(XT2 + 8, 242, V("B", "2") + [("n", " = "), ("v", "y")], "start", BLUE)
    return s + footer()
