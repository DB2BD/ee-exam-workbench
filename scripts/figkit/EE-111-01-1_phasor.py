"""EE-111-01-1: phasor circuit (kOhm, sine-reference peak phasors) of the op-amp filter; Vo = 3Vb fed back to node a."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 720, 420
XS, XA, XB, XN, XO, XT = 70, 220, 360, 440, 610, 670
YF, YT, YM, YB = 90, 190, 300, 370
OPX, OPY = 470, 215                                        # op-amp left side x, centre y
s = header(W, H)
s += line(XS, YT, XS, 266) + ac_source(XS, 280) + line(XS, 294, XS, YB)
s += line(XS, YT, 100, YT) + resistor(100, YT, 180, YT) + line(180, YT, XA, YT)
s += cap(XA, YT, XA, YB)                                    # C1 a-ground
s += line(XA, YT, 250, YT) + cap(250, YT, 320, YT) + line(320, YT, XB, YT)   # C2 a-b
s += resistor(XB, YT, XB, YB, lead=40)                      # 10k b-ground
s += line(XB, YT, OPX, YT)                                  # to + input (y = YT)
s += f'<path d="M{OPX} {OPY - 50} L{OPX} {OPY + 50} L{OPX + 80} {OPY} Z"/>\n'
s += line(OPX + 80, OPY, XT, OPY)
s += line(OPX, 240, XN, 240) + line(XN, 240, XN, YM)        # - input down to divider node
s += resistor(XN, YM, XN, YB, lead=14)                      # 20k to ground
s += line(XN, YM, 500, YM) + resistor(500, YM, 570, YM) + line(570, YM, XO, YM) + line(XO, YM, XO, OPY)   # 40k
s += line(XA, YT, XA, YF) + line(XA, YF, 380, YF) + resistor(380, YF, 460, YF) + line(460, YF, XO, YF) + line(XO, YF, XO, OPY)  # 20k feedback
s += line(XS, YB, XN, YB)
s += dot(XA, YT) + dot(XB, YT) + dot(XN, YM) + dot(XO, OPY) + dot(XA, YB) + dot(XB, YB)
s += terminal(XT, OPY)
s += line(XN, YB, XN, YB + 8) + ground(XN, YB + 8)
s += end_group()
s += text(20, 30, [("t", "相量電路：阻抗單位 kΩ，"), ("v", "ω"), ("n", " = 400 rad/s"), ("t", "，"), ("n", "sin"), ("t", " 基準峰值相量")])
s += ttext(XS - 20, 272, [("n", "+")], color=BLUE) + ttext(XS - 20, 300, [("n", "−")], color=BLUE)
s += ttext(XS + 22, 286, [("v", "V"), ("vsub", "s"), ("n", " = 2∠0° V")], color=BLUE)
s += text(140, YT - 14, [("n", "10")], anchor="middle")
s += text(XA - 8, YT - 10, [("v", "a")], anchor="end")
s += text(XB + 6, YT - 10, [("v", "b")])
s += text(285, YT + 34, [("v", "Z"), ("vsub", "C"), ("sub", "2"), ("n", " = −"), ("v", "j"), ("n", "5")], anchor="middle")
s += text(XA + 22, 300, [("v", "Z"), ("vsub", "C"), ("sub", "1"), ("n", " = −"), ("v", "j"), ("n", "10")])
s += text(XB + 14, 300, [("n", "10")])
s += text(420, YF - 14, [("n", "20")], anchor="middle")
s += text(535, YM + 30, [("n", "40")], anchor="middle")
s += text(XN - 14, 344, [("n", "20")], anchor="end")
s += text(OPX + 10, YT + 6, [("n", "+")]) + text(OPX + 10, 246, [("n", "−")])
s += ttext(XT, OPY - 14, [("v", "V"), ("vsub", "o"), ("n", " = 3"), ("v", "V"), ("vsub", "b")], anchor="middle", color=BLUE)
s += footer()
write('EE-111-01-1-phasor.svg', s)
