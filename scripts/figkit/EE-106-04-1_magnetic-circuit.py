"""EE-106-04-1 fig 1: magnetic equivalent circuit of the electromagnet (iron and plate reluctance neglected):
MMF NI drives flux Phi through two air-gap reluctances R_g = g/(mu0 A) in series."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 540, 280; XS, XR, YT, YB = 120, 400, 70, 210
s = header(W, H)
s += vsrc(XS, YT, XS, YB, r=22)                    # + on top: MMF pushes Phi clockwise (out of the + end)
s += line(XS, YT, 200, YT) + resistor(200, YT, 300, YT) + line(300, YT, XR, YT)
s += line(XR, YT, XR, 90) + resistor(XR, 90, XR, 190) + line(XR, 190, XR, YB)
s += line(XR, YB, XS, YB)
s += arrow(215, YT - 18, 285, YT - 18, color=RED)
s += end_group()
s += ttext(XS - 30, 136, [("v", "ℱ"), ("n", " = "), ("v", "NI")], anchor="end", color=BLUE)
s += ttext(250, YT - 28, [("n", "Φ"), ("n", " = "), ("v", "BA")], anchor="middle", color=RED)
s += text(250, YT + 34, [("v", "ℛ"), ("vsub", "g"), ("t", "（氣隙 1）")], anchor="middle")
s += text(XR + 16, 136, [("v", "ℛ"), ("vsub", "g")])
s += text(XR + 16, 164, [("t", "（氣隙 2）")])
s += text(270, 252, [("v", "ℛ"), ("vsub", "g"), ("n", " = "), ("v", "g"), ("n", " / ("), ("v", "μ"), ("sub", "0"), ("v", "A"), ("n", ")"),
                     ("t", "，鐵心與鐵板磁阻忽略")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-106-04-1-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
