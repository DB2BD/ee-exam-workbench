"""EE-110-01-3: |V_C| and |V_L| versus f near f0 (zoomed window), peaks at fC*, fL*."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 640, 400
X0, X1, Y0, Y1 = 90, 600, 330, 50           # plot box (screen)
F0, F1, V0, V1 = 7.4, 8.6, 340.0, 410.0      # data window (kHz, V)
fx = lambda f: X0 + (f - F0) / (F1 - F0) * (X1 - X0)
vy = lambda v: Y0 - (v - V0) / (V1 - V0) * (Y0 - Y1)
Q, VM, FR = 4.0, 100.0, 8.0

def vc(f):
    u = f / FR; return VM * Q / math.sqrt(u * u + Q * Q * (u * u - 1) ** 2)

def vl(f):
    u = f / FR; return VM * Q / math.sqrt(1 / u ** 2 + Q * Q * (1 - 1 / u ** 2) ** 2)

def curve(fn, color):
    pts = [(fx(F0 + k * (F1 - F0) / 400), vy(fn(F0 + k * (F1 - F0) / 400))) for k in range(401)]
    pts = [(x, y) for x, y in pts if y <= Y0]
    return poly(pts, w=2, color=color)

from power_parts import poly
s = header(W, H)
s += arrow(X0, Y0, X1 + 20, Y0) + arrow(X0, Y0, X0, Y1 - 20)
s += line(X0 - 6, Y0 - 14, X0 + 6, Y0 - 20) + line(X0 - 6, Y0 - 8, X0 + 6, Y0 - 14)   # axis break
s += curve(vc, "#000") + curve(vl, BLUE)
fc, fl, vmax = 8 * math.sqrt(31 / 32), 8 * math.sqrt(32 / 31), 3200 / math.sqrt(63)
for f, v in ((fc, vmax), (FR, 400.0), (fl, vmax)):
    s += dashed(fx(f), vy(v), fx(f), Y0)
s += dashed(X0, vy(vmax), fx(fl), vy(vmax)) + dashed(X0, vy(400), fx(FR), vy(400))
s += dot(fx(fc), vy(vmax)) + dot(fx(fl), vy(vmax)) + dot(fx(FR), vy(400))
s += end_group()
s += text(X1 + 20, Y0 + 22, [("v", "f"), ("n", " (kHz)")], anchor="end")
s += text(X0 - 8, Y1 - 24, [("t", "端電壓峰值"), ("n", " (V)")], anchor="start")
s += text(X0 - 8, vy(vmax) + 2, [("n", "403.16")], anchor="end")
s += text(X0 - 8, vy(400) + 14, [("n", "400")], anchor="end")
s += text(X0 - 8, Y0 + 5, [("n", "340")], anchor="end")
s += text(fx(fc), Y0 + 22, [("n", "7.87")], anchor="middle")
s += text(fx(FR), Y0 + 22, [("n", "8")], anchor="middle")
s += text(fx(fl), Y0 + 22, [("n", "8.13")], anchor="middle")
s += text(fx(fc) - 4, Y0 + 44, [("v", "f"), ("vsub", "C"), ("n", "*")], anchor="end")
s += text(fx(FR), Y0 + 44, [("v", "f"), ("sub", "0")], anchor="middle")
s += text(fx(fl) + 4, Y0 + 44, [("v", "f"), ("vsub", "L"), ("n", "*")])
s += text(fx(7.55) - 22, vy(vc(7.55)) - 16, [("n", "|"), ("v", "V"), ("vsub", "C"), ("n", "|")], anchor="middle")
s += ttext(fx(8.45) + 24, vy(vl(8.45)) - 16, [("n", "|"), ("v", "V"), ("vsub", "L"), ("n", "|")], anchor="middle", color=BLUE)
s += footer()
write('EE-110-01-3-peaks.svg', s)
