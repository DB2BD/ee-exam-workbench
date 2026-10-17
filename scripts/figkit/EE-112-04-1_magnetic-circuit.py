"""EE-112-04-1 fig 1: magnetic equivalent circuit of the inductor core (single loop, no leakage, linear core):
MMF source F = N i drives the flux phi through the core reluctance R = l_c / (mu_0 mu_r A_c)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext

W, H = 520, 250; XL, XR, YT, YB = 130, 380, 60, 190
s = header(W, H)
s += vsrc(XL, YT, XL, YB, r=22)
s += line(XL, YT, XR, YT) + line(XR, YT, XR, 80) + resistor(XR, 80, XR, 170) + line(XR, 170, XR, YB) + line(XR, YB, XL, YB)
s += arrow(210, YT - 16, 290, YT - 16)
s += end_group()
s += ttext(XL - 32, 122, [("v", "ℱ"), ("n", " = "), ("v", "Ni")], anchor="end", color=BLUE)
s += ttext(XL - 32, 146, [("v", "N"), ("n", " = 70")], anchor="end", color=BLUE)
s += text(250, YT - 26, [("v", "ϕ")], anchor="middle")
s += text(XR + 16, 120, [("v", "ℛ"), ("n", " = ")])
s += text(XR + 16, 146, [("v", "l"), ("vsub", "c"), ("n", "/("), ("v", "μ"), ("sub", "0"), ("v", "μ"), ("vsub", "r"), ("v", "A"), ("vsub", "c"), ("n", ")")])
s += text(255, 228, [("t", "磁路歐姆定律："), ("v", "ϕ"), ("n", " = "), ("v", "ℱ"), ("n", "/"), ("v", "ℛ")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-112-04-1-magnetic-circuit.svg'
out.write_text(s)
print(out.name, len(s))
