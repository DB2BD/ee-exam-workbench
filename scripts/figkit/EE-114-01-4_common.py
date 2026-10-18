"""Shared layout for the two EE-114-01-4 superposition phasor circuits (5 rad/s and 10 rad/s)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H, YT, YB = 720, 320, 90, 250
XS, XR0, XR1, XN, XC, XL, XI = 140, 180, 280, 310, 390, 510, 640


def frame(keep_vsrc, keep_isrc):
    s = header(W, H)
    s += line(XS, YT, XR0, YT) + resistor(XR0, YT, XR1, YT) + line(XR1, YT, XL, YT)
    s += line(XS, YB, XL, YB)
    if keep_vsrc:
        s += vsrc(XS, YT, XS, YB, r=18)
    else:
        s += line(XS, YT, XS, YB)                                  # voltage source killed: short circuit
    s += line(XC, YT, XC, 150) + cap(XC, 150, XC, 190) + line(XC, 190, XC, YB)
    s += line(XL, YT, XL, 130) + coil(XL, 130, XL, 210) + line(XL, 210, XL, YB)
    if keep_isrc:
        s += line(XL, YT, XI, YT) + line(XL, YB, XI, YB) + isrc(XI, YB, XI, YT, r=18)
    for x in (XN, XC):
        s += dot(x, YT) + dot(x, YB)
    s += dot(XL, YT) + dot(XL, YB)
    s += line(XC, YB, XC, YB + 12) + ground(XC, YB + 12)
    return s


def vo_label(sub):
    s = ttext(XN + 20, YT + 30, [("n", "+")], anchor="middle", color=BLUE)
    s += ttext(XN + 20, 176, [("v", "V"), ("vsub", "o"), ("sub", "," + sub)], anchor="middle", color=BLUE)
    s += ttext(XN + 20, YB - 12, [("n", "−")], anchor="middle", color=BLUE)
    return s.replace('<tspan class="v"', '<tspan class="v" font-weight="bold"', 1)


def common_labels(yc, yl):
    s = text((XR0 + XR1) / 2, YT - 16, [("n", "8 Ω")], anchor="middle")
    s += text(XC + 22, 164, [("v", "Y"), ("vsub", "C")])
    s += text(XC + 22, 186, [("n", "= " + yc)])
    s += text(XL + 16, 164, [("v", "Y"), ("vsub", "L")])
    s += text(XL + 16, 186, [("n", "= " + yl)])
    return s
