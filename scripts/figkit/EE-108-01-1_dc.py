"""EE-108-01-1: dc equivalent (voltage source shorted, inductors shorted, capacitor open)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 310
XS, XA, XI = 80, 420, 540
YT, YB = 90, 250
s = header(W, H)
s += line(XS, YT, XS, YB)                                      # shorted voltage source
s += line(XS, YT, 120, YT) + resistor(120, YT, 200, YT) + line(200, YT, XI, YT)
s += resistor(XA, YT, XA, YB, lead=40)
s += isrc(XI, YB, XI, YT)                                      # 6 A upward into node a
s += line(XS, YB, XI, YB)
s += dot(XA, YT) + dot(XA, YB)
s += line(XA, YB, XA, YB + 10) + ground(XA, YB + 10)
s += tint_arrow(135, YT - 14, 185, YT - 14)
s += end_group()
s += text(20, 28, [("t", "直流單獨作用：電壓源短路、兩個 "), ("v", "L"), ("t", " 短路、"), ("v", "C"), ("t", " 開路，"), ("n", "6 A"), ("t", " 保留")])
s += text(XS - 10, 176, [("t", "電壓源")], anchor="end")
s += text(XS - 10, 198, [("t", "短路")], anchor="end")
s += text(160, YT + 28, [("n", "1 Ω")], anchor="middle")
s += ttext(160, YT - 26, [("v", "I"), ("sub", "dc")], anchor="middle", color=RED)
s += text(310, YT - 12, [("v", "L"), ("t", " 短路（"), ("v", "C"), ("t", " 開路）")], anchor="middle")
s += text(XA, YT - 12, [("v", "a")], anchor="middle")
s += ttext(XA - 18, YT + 26, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(XA - 18, YB - 10, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(XA - 24, 176, [("v", "V"), ("vsub", "a")], anchor="end", color=BLUE)
s += text(XA + 14, 176, [("n", "2 Ω")])
s += text(XI + 24, 176, [("n", "6 A")])
s += footer()
write('EE-108-01-1-dc.svg', s)
