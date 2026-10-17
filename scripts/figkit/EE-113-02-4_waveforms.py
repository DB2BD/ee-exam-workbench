"""EE-113-02-4: full-bridge BCM waveforms over one period: rectified voltage, v_Lx, i_Lx."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X0, X4, XE = 110, 610, 660
DUTY = 0.3
H2 = (X4 - X0) / 2
X1 = X0 + DUTY * (X4 - X0)          # DTs
X2 = X0 + H2                        # Ts/2
X3 = X2 + DUTY * (X4 - X0)          # (1/2 + D)Ts


def axes(y0, ytop, ybot):
    return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)


W, H = 700, 450
s = header(W, H)
# on-intervals shaded (both pulses)
for xa, xb in ((X0, X1), (X2, X3)):
    s += f'<rect x="{xa:.1f}" y="34" width="{xb - xa:.1f}" height="16" fill="{FILL_BLUE}" stroke="none"/>\n'
for x in (X1, X2, X3, X4):
    s += dashed(x, 34, x, 412)
# rectified voltage: zero 140, n_h V_s at 80
s += axes(140, 60, 150) + poly([(X0, 80), (X1, 80), (X1, 140), (X2, 140), (X2, 80), (X3, 80), (X3, 140), (X4, 140)])
# v_Lx: zero 250, n_hVs - Vo at 210, -Vo at 280
s += axes(250, 172, 292) + poly([(X0, 210), (X1, 210), (X1, 280), (X2, 280), (X2, 210), (X3, 210), (X3, 280), (X4, 280)])
# i_Lx: zero 395, peak 330 at DTs and (1/2+D)Ts
s += axes(395, 312, 405) + poly([(X0, 395), (X1, 330), (X2, 395), (X3, 330), (X4, 395)])
s += dashed(X0, 362.5, X4, 362.5, 1.2)
s += end_group()
s += text((X0 + X1) / 2, 47, [("v", "S"), ("sub", "1"), ("v", "S"), ("sub", "2"), ("t", " 導通")], anchor="middle")
s += text((X2 + X3) / 2, 47, [("v", "S"), ("sub", "3"), ("v", "S"), ("sub", "4"), ("t", " 導通")], anchor="middle")
s += text((X1 + X2) / 2, 47, [("t", "四開關皆關")], anchor="middle")
s += text((X3 + X4) / 2, 110, [("t", "整流輸出 "), ("v", "v"), ("vsub", "d")], anchor="middle")
s += text(104, 85, [("v", "n"), ("vsub", "h"), ("v", "V"), ("sub", "s")], anchor="end")
s += text(104, 145, [("n", "0")], anchor="end")
s += text((X1 + X2) / 2, 128, [("v", "D"), ("sub", "1"), ("v", "D"), ("sub", "2"), ("t", " 續流")], anchor="middle")
s += text(X0 + 8, 182, [("v", "v"), ("vsub", "Lx")])
s += text(104, 215, [("v", "n"), ("vsub", "h"), ("v", "V"), ("sub", "s"), ("n", " − "), ("v", "V"), ("vsub", "o")], anchor="end")
s += text(104, 255, [("n", "0")], anchor="end")
s += text(104, 285, [("n", "−"), ("v", "V"), ("vsub", "o")], anchor="end")
s += text(X0 + 8, 322, [("v", "i"), ("vsub", "Lx")])
s += text(104, 335, [("n", "Δ"), ("v", "i"), ("vsub", "L")], anchor="end")
s += text(104, 400, [("n", "0")], anchor="end")
s += text(X4 + 4, 358, [("v", "I"), ("vsub", "o")])
for y in (145, 255, 400):
    s += text(XE + 6, y - 14, [("v", "t")])
s += text(X0, 432, [("n", "0")], anchor="middle")
s += text(X1, 432, [("v", "DT"), ("sub", "s")], anchor="middle")
s += text(X2, 432, [("v", "T"), ("sub", "s"), ("n", "/2")], anchor="middle")
s += text(X3, 432, [("n", "("), ("n", "½ + "), ("v", "D"), ("n", ")"), ("v", "T"), ("sub", "s")], anchor="middle")
s += text(X4, 432, [("v", "T"), ("sub", "s")], anchor="middle")
s += footer()
write('EE-113-02-4-waveforms.svg', s)
