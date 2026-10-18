"""EE-108-02-1: Bode plots of the single-pole op amp A(f) = A_0/(1 + j f/f_b), A_0 = 10^4 (80 dB),
f_b = 100.01 Hz, f_t = 1.00 MHz.  Magnitude: exact curve (blue) + asymptotes (dashed);
phase: exact curve (blue) + straight-line approximation (dashed).  Range 1 Hz ... 10 MHz."""
import math
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

FB = 1e4 / math.sqrt(9999)
XL, XR = 92, 652                       # f = 1 Hz ... 10 MHz (7 decades)
DEC = (XR - XL) / 7
YM0, KM = 62, 1.8                      # 80 dB at y = 62, 1.8 px per dB
YP0, KP = 312, 1.4                     # 0 deg at y = 312, 1.4 px per degree


def xf(f):
    return XL + DEC * math.log10(f)


def ym(db):
    return YM0 + (80 - db) * KM


def yp(deg):
    return YP0 - deg * KP


def mag(f):
    return 80 - 10 * math.log10(1 + (f / FB) ** 2)


def phase(f):
    return -math.degrees(math.atan(f / FB))


W, H = 700, 486
s = header(W, H)
# grids (light dashed) and axes
for k in range(8):
    s += dashed(xf(10 ** k), ym(80), xf(10 ** k), ym(-20), 0.6)
    s += dashed(xf(10 ** k), yp(0), xf(10 ** k), yp(-90), 0.6)
for db in (60, 40, 20, 0, -20):
    s += dashed(XL, ym(db), XR, ym(db), 0.6)
s += dashed(XL, yp(-45), XR, yp(-45), 0.6) + dashed(XL, yp(-90), XR, yp(-90), 0.6)
s += arrow(XL, ym(-24), XL, ym(88)) + line(XL, ym(-20), XR + 8, ym(-20))
s += arrow(XL, yp(-96), XL, yp(8)) + line(XL, yp(-90), XR + 8, yp(-90))
# magnitude: asymptotes (dashed) then exact curve (blue)
s += dashed(XL, ym(80), xf(FB), ym(80), 1.4) + dashed(xf(FB), ym(80), XR, ym(-20), 1.4)
pts = [(xf(10 ** (k / 20)), ym(mag(10 ** (k / 20)))) for k in range(0, 141)]
s += poly(pts, color=BLUE)
# phase: straight-line approximation (0 to f_b/10, -45 deg/decade to 10 f_b) and exact curve
s += dashed(XL, yp(0), xf(FB / 10), yp(0), 1.4) + dashed(xf(FB / 10), yp(0), xf(FB * 10), yp(-90), 1.4)
s += dashed(xf(FB * 10), yp(-90), XR, yp(-90), 1.4)
pts = [(xf(10 ** (k / 20)), yp(phase(10 ** (k / 20)))) for k in range(0, 141)]
s += poly(pts, color=BLUE)
# landmark dots
for f, d in ((FB, mag(FB)), (1e4, 40), (FB * 1e4, 0), (1e7, mag(1e7))):
    s += dot(xf(f), ym(d))
s += dot(xf(FB), yp(-45))
s += end_group()
# axis names, tick labels
s += text(XL + 8, ym(86), [("n", "|"), ("v", "A"), ("n", "|  (dB)")])
s += text(XL + 8, yp(4) - 8, [("v", "ϕ"), ("n", "  (°)")])
for db in (80, 60, 40, 20, 0, -20):
    s += text(XL - 8, ym(db) + 5, [("n", f"{db}".replace("-", "−"))], anchor="end")
for deg in (0, -45, -90):
    s += text(XL - 8, yp(deg) + 5, [("n", f"{deg}".replace("-", "−"))], anchor="end")
labels = ["1", "10", "100", "1k", "10k", "100k", "1M", "10M"]
for k, lab in enumerate(labels):
    s += text(xf(10 ** k), ym(-20) + 20, [("n", lab)], anchor="middle")
    s += text(xf(10 ** k), yp(-90) + 20, [("n", lab)], anchor="middle")
s += text(XR + 4, ym(-20) + 40, [("v", "f"), ("n", " (Hz)")], anchor="end")
s += text(XR + 4, yp(-90) + 40, [("v", "f"), ("n", " (Hz)")], anchor="end")
# magnitude landmarks
s += text(xf(FB) - 4, ym(80) - 10, [("v", "f"), ("vsub", "b"), ("n", " = 100.01 Hz")], anchor="start")
s += text(xf(FB) - 8, ym(mag(FB)) + 22, [("n", "76.99 dB")], anchor="end")
s += text(xf(1e4) + 10, ym(40) - 8, [("n", "(10 kHz, 40 dB)")])
s += text(xf(FB * 1e4) - 8, ym(0) + 22, [("v", "f"), ("vsub", "t"), ("n", " = 1.00 MHz")], anchor="end")
s += text(xf(1e7) - 30, ym(mag(1e7)) - 22, [("n", "−20 dB")])
s += btext(xf(1e3) - 6, ym(44), [("n", "−20 dB/dec")], anchor="end")
# phase landmarks
s += text(xf(FB) + 10, yp(-45) - 8, [("n", "−45°")])
s += text(xf(1) + 10, yp(0) + 22, [("n", "−0.57°")])
s += text(xf(1e7) - 8, yp(-90) - 10, [("n", "−90.00°")], anchor="end")
s += footer()
write('EE-108-02-1-bode.svg', s)
