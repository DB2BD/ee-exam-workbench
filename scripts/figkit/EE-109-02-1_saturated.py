"""EE-109-02-1: saturated-switch model. B-E replaced by V_BE(sat), C-E by V_CE(sat); emitter is the common node.

Reference directions as in the crop: I_B flows V_B -> R_B -> base, I_C flows V_CC -> R_C -> collector."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YC, YR = 60, 150, 290
XVB, XR1, XR2, XB, XC, XVCC = 70, 110, 230, 290, 470, 640
W, H = 720, 340
s = header(W, H)
# base loop
s += vsrc(XVB, YC, XVB, YR) + line(XVB, YC, XR1, YC) + resistor(XR1, YC, XR2, YC, zigs=6, lead=12) + line(XR2, YC, XB, YC)
s += dot(XB, YC) + vsrc(XB, YC, XB, YR)
# collector loop
s += line(XC, YT, XVCC, YT) + resistor(XC, YT, XC, YC, zigs=6, lead=12) + dot(XC, YC) + vsrc(XC, YC, XC, YR)
s += vsrc(XVCC, YT, XVCC, YR)
s += line(XVB, YR, XVCC, YR) + dot(XB, YR) + dot(XC, YR) + line(380, YR, 380, YR + 10) + ground(380, YR + 10)
# currents
s += red_arrow(XR1 + 10, YC - 22, XR2 - 10, YC - 22)
s += red_arrow(XC - 24, YT + 22, XC - 24, YC - 18)
s += end_group()
t = []
t.append(text(XVB - 24, (YC + YR) / 2 + 5, [("v", "V"), ("vsub", "B")], anchor="end"))
t.append(text(XVB - 24, (YC + YR) / 2 + 25, [("n", "10 V")], anchor="end"))
t.append(text((XR1 + XR2) / 2, YC + 30, [("v", "R"), ("vsub", "B")], anchor="middle"))
t.append(ctext((XR1 + XR2) / 2, YC - 32, [("v", "I"), ("vsub", "B")], anchor="middle"))
t.append(text(XB + 8, YC - 10, [("v", "B")]))
t.append(text(XB + 24, (YC + YR) / 2 - 4, [("v", "V"), ("vsub", "BE(sat)")]))
t.append(text(XB + 24, (YC + YR) / 2 + 16, [("n", "1.5 V")]))
t.append(text(XC + 14, (YT + YC) / 2 + 5, [("v", "R"), ("vsub", "C"), ("n", " = 11 Ω")]))
t.append(ctext(XC - 32, (YT + YC) / 2 + 5, [("v", "I"), ("vsub", "C"), ("n", " = "), ("v", "I"), ("vsub", "CS")], anchor="end"))
t.append(text(XC + 8, YC - 6, [("v", "C")]))
t.append(text(XC + 24, (YC + YR) / 2 - 4, [("v", "V"), ("vsub", "CE(sat)")]))
t.append(text(XC + 24, (YC + YR) / 2 + 16, [("n", "1.0 V")]))
t.append(text(XVCC + 24, (YT + YR) / 2 + 5, [("v", "V"), ("vsub", "CC")]))
t.append(text(XVCC + 24, (YT + YR) / 2 + 25, [("n", "200 V")]))
t.append(text(XC + 14, YR - 10, [("v", "E")]))
t.append(text(20, 330, [("t", "飽和模型："), ("v", "B"), ("n", "–"), ("v", "E"), ("t", " 以 "), ("v", "V"), ("vsub", "BE(sat)"), ("t", "、"),
                        ("v", "C"), ("n", "–"), ("v", "E"), ("t", " 以 "), ("v", "V"), ("vsub", "CE(sat)"),
                        ("t", " 定電壓取代，射極 "), ("v", "E"), ("t", " 為共同節點")]))
s += ''.join(t) + footer()
write('EE-109-02-1-saturated.svg', s)
