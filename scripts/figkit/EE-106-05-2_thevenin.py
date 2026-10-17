import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
RED, BLUE = "#c0392b", "#1f5fa8"
W, H = 520, 240
SX, SY, R = 90, 120, 20          # Thevenin source V(0)
YT, YB, XF = 60, 180, 420        # top wire, bottom wire, fault branch x
s = header(W, H)
s += f'<circle cx="{SX}" cy="{SY}" r="{R}"/>\n'
s += line(SX - 5, SY - 9, SX + 5, SY - 9) + line(SX, SY - 14, SX, SY - 4)      # +
s += line(SX - 5, SY + 9, SX + 5, SY + 9)                                      # −
s += line(SX, SY - R, SX, YT) + line(SX, YT, 170, YT)
s += coil(170, YT, 290, YT, turns=5)                                            # Z11
s += line(290, YT, XF, YT)
s += line(XF, YT, XF, 85) + coil(XF, 85, XF, 155, turns=4) + line(XF, 155, XF, YB)   # Zf
s += line(XF, YB, SX, YB) + line(SX, YB, SX, SY + R)
s += dot(360, YT)
s += f'<g stroke="{RED}">' + arrow(298, YT, 334, YT).replace('#000', RED) + '</g>\n'   # I_f
s += end_group()
s += text(SX - R - 10, SY - 4, [("v", "V"), ("n", "(0)")], anchor="end").replace('#000', BLUE)
s += text(SX - R - 10, SY + 16, [("n", "1∠0°")], anchor="end").replace('#000', BLUE)
s += text(230, YT - 16, [("v", "Z"), ("sub", "11"), ("n", " = "), ("v", "j"), ("n", "0.16")], anchor="middle")
s += text(360, YT - 14, [("n", "Bus 1")], anchor="middle")
s += text(316, YT + 24, [("v", "I"), ("vsub", "f")], anchor="middle").replace('#000', RED)
s += text(XF + 26, 110, [("v", "Z"), ("vsub", "f")])
s += text(XF + 26, 138, [("v", "j"), ("n", "0.11")])
s += text(255, 216, [("v", "I"), ("vsub", "f"), ("n", "\u2009 = "), ("v", "V"), ("n", "(0) / ("), ("v", "Z"), ("sub", "11"),
                     ("n", " + "), ("v", "Z"), ("vsub", "f"), ("n", "\u2009)")], anchor="middle").replace('#000', RED)
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-106-05-2-thevenin.svg'), 'w').write(s)
print(len(s))
