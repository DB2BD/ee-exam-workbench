"""EE-112-02-4: load voltage v_o (half-wave sine, D2 freewheels in the negative half) and load current i_o at L = 496.17 mH."""
import cmath, math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

Vm, w, R, Vdc, L = 170.0, 377.0, 10.0, 24.0, 0.49617
X0, X2, XE = 110, 590, 640           # wt = 0 .. 2*pi
XM = (X0 + X2) / 2                   # wt = pi
I0 = (Vm / math.pi - Vdc) / R


def i_o(th, N=60):
    i = I0
    terms = [(1, 0.0, Vm / 2)] + [(2 * k, -2 * Vm / (math.pi * (4 * k * k - 1)), 0.0) for k in range(1, N)]
    for n, a, b in terms:
        i += (complex(a, -b) / complex(R, n * w * L) * cmath.exp(1j * n * th)).real
    return i


def xs(th):
    return X0 + th / (2 * math.pi) * (X2 - X0)


W, H = 680, 450
s = header(W, H)
s += f'<rect x="{X0}" y="30" width="{XM - X0:.1f}" height="16" fill="{FILL_BLUE}" stroke="none"/>\n'
s += f'<rect x="{XM:.1f}" y="30" width="{X2 - XM:.1f}" height="16" fill="{FILL_RED}" stroke="none"/>\n'
s += dashed(XM, 30, XM, 406) + dashed(X2, 30, X2, 406)
# v_o panel: zero at 170, Vm -> 70 ; Vm/pi dashed
y0v, kv = 200, 130 / Vm
s += arrow(X0, 210, X0, 56) + arrow(X0, y0v, XE, y0v)
pts = [(xs(k * math.pi / 120), y0v - kv * Vm * math.sin(k * math.pi / 120)) for k in range(121)] + [(X2, y0v)]
s += poly(pts)
s += dashed(X0, y0v - kv * Vm / math.pi, X2, y0v - kv * Vm / math.pi, 1.2)
s += dashed(X0, y0v - kv * Vdc, X2, y0v - kv * Vdc, 1)
# i_o panel: zero offscreen; 2.4 A -> 360, 3.6 A -> 220  (116.7 px/A)
ki = 140 / 1.2
yi = lambda a: 390 - (a - 2.4) * ki
s += arrow(X0, 400, X0, 236)
ipts = [(xs(k * 2 * math.pi / 240), yi(i_o(k * 2 * math.pi / 240))) for k in range(241)]
s += poly(ipts, color=RED)
s += dashed(X0, yi(I0), X2, yi(I0), 1.2)
vals = [i_o(k * 2 * math.pi / 2000) for k in range(2000)]
imax, imin = max(vals), min(vals)
s += dashed(X0, yi(imax), XE - 10, yi(imax), 1) + dashed(X0, yi(imin), XE - 10, yi(imin), 1)
s += red_arrow(XE - 16, yi(I0), XE - 16, yi(imax) + 1) + red_arrow(XE - 16, yi(I0), XE - 16, yi(imin) - 1)
s += end_group()
s += text((X0 + XM) / 2, 43, [("v", "D"), ("sub", "1"), ("t", " 導通："), ("v", "v"), ("vsub", "o"), ("n", " = "), ("v", "v"), ("vsub", "s")], anchor="middle")
s += text((XM + X2) / 2, 43, [("v", "D"), ("sub", "2"), ("t", " 續流："), ("v", "v"), ("vsub", "o"), ("n", " = 0")], anchor="middle")
s += text(X0 + 8, 66, [("v", "v"), ("vsub", "o")])
s += text(104, y0v - kv * Vm + 5, [("n", "170 V")], anchor="end")
s += text(104, y0v - kv * Vm / math.pi + 5, [("n", "54.11 V")], anchor="end")
s += text(X2 + 6, y0v - kv * Vm / math.pi + 5, [("v", "V"), ("vsub", "m"), ("n", "/π")])
s += text(X2 + 6, y0v - kv * Vdc + 5, [("v", "V"), ("vsub", "dc"), ("n", " = 24 V")])
s += text(104, y0v + 5, [("n", "0")], anchor="end")
s += text(XE + 4, y0v + 5, [("v", "ωt")])
s += ctext(X0 + 8, 246, [("v", "i"), ("vsub", "o")])
s += text(104, yi(imax) + 5, [("n", "3.52 A")], anchor="end")
s += text(104, yi(I0) + 5, [("n", "3.01 A")], anchor="end")
s += text(104, yi(imin) + 5, [("n", "2.52 A")], anchor="end")
s += text(X2 + 6, yi(I0) - 6, [("v", "I"), ("sub", "0")])
s += ctext(XE - 6, yi(imax) - 8, [("n", "Δ"), ("v", "i"), ("vsub", "o"), ("n", " = 1 A")], anchor="end")
s += text(X0, 428, [("n", "0")], anchor="middle")
s += text(XM, 428, [("n", "π")], anchor="middle")
s += text(X2, 428, [("n", "2π")], anchor="middle")
s += footer()
write('EE-112-02-4-waveforms.svg', s)
