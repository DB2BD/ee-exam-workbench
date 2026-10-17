"""Shared drawing for EE-114-01-3: the RLC circuit before (DC steady state) and after the switch opens."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 640, 290, 90, 250
XS, XN, XR1 = 70, 380, 540


def figure(mode):
    """mode 'dc': t<0 steady state (L short, C open, switch closed); 'open': t>0 series RLC."""
    dc = mode == 'dc'
    s = header(W, H)
    s += vsrc(XS, YT, XS, YB)
    s += line(XS, YT, 120, YT) + resistor(120, YT, 200, YT) + line(200, YT, 240, YT)
    s += line(240, YT, 320, YT) if dc else coil(240, YT, 320, YT, turns=4)
    s += line(320, YT, XN, YT)
    if dc:   # capacitor removed: open terminals
        s += line(XN, YT, XN, 140) + terminal(XN, 144) + terminal(XN, 196) + line(XN, 200, XN, YB)
    else:
        s += cap(XN, YT, XN, YB)
    s += switch(XN, YT, 480, YT, closed=dc)
    s += line(480, YT, XR1, YT) + resistor(XR1, YT, XR1, YB, zigs=6, lead=50) + line(XS, YB, XR1, YB)
    s += dot(XN, YT) + dot(XN, YB)
    s += tint_arrow(205, YT + 16, 237, YT + 16, RED)
    s += end_group()
    s += text(XS - 22, (YT + YB) // 2 + 5, [("n", "24 V")], anchor="end")
    s += text(160, YT - 16, [("v", "R"), ("n", " = 4 Ω")], anchor="middle")
    s += text(280, YT - 16, [("v", "L"), ("n", " = 1 H（短路）" if dc else " = 1 H")], anchor="middle")
    s += text(430, YT - 30, [("v", "t"), ("n", " = 0")], anchor="middle")
    s += text(XR1 + 16, (YT + YB) // 2 + 5, [("n", "1 Ω")])
    s += ttext(XN + 20, YT + 46, [("n", "+")], color=BLUE)
    s += ttext(XN + 20, YB - 30, [("n", "−")], color=BLUE)
    if dc:
        s += text(20, 30, [("v", "t"), ("n", " &lt; 0 "), ("t", "直流穩態：電感短路、電容開路、開關閉合")])
        s += ttext(222, YT + 44, [("v", "i"), ("n", "(0⁻) = 4.80 A")], anchor="middle", color=RED)
        s += text(XN - 14, (YT + YB) // 2 + 5, [("v", "C"), ("t", " 開路")], anchor="end")
        s += ttext(XN + 20, (YT + YB) // 2 + 5, [("v", "v"), ("n", "(0⁻) = 4.80 V")], color=BLUE)
    else:
        s += text(20, 30, [("v", "t"), ("n", " &gt; 0 "), ("t", "開關打開：串聯 RLC（1 Ω 支路斷開，無電流）")])
        s += ttext(222, YT + 44, [("v", "i"), ("n", "("), ("v", "t"), ("n", ")")], anchor="middle", color=RED)
        s += text(XN - 22, (YT + YB) // 2 + 5, [("v", "C"), ("n", " = 0.25 F")], anchor="end")
        s += ttext(XN + 20, (YT + YB) // 2 + 5, [("v", "v"), ("n", "("), ("v", "t"), ("n", ")")], color=BLUE)
    s += footer()
    return s
