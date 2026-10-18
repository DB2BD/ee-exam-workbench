"""EE-113-06-5 CO-7 curve reading: TD4/TD5/TD6 traced from the official crop (same pixel frame as
verification/pe/EE-113-06-5.py), zoomed to M = 8-20 (log axis), t = 0.6-1.6 s.
The 1.0 s operating line meets TD5 at M ≈ 15 (step 1 of the note).
"""
import math, sys, pathlib
import numpy as np
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
ROOT = pathlib.Path(__file__).resolve().parents[2]
im = np.array(Image.open(ROOT / "01_原始試題/依考科/06_工業配電/images/questions/PE_113年_工業配電_Q05.png").convert("L")).astype(int)
x1, x20, y0, y7 = 223.5, 1106.5, 1632, 675            # plot frame of the crop (pixel)
px_of = lambda M: x1 + (x20 - x1) * math.log10(M) / math.log10(20)
t_of = lambda y: (y0 - y) * 7 / (y0 - y7)
def clusters(x):
    ys = [y for y in range(690, 1625) if im[y, x] < 90]; cl = []
    for y in ys:
        if cl and y - cl[-1][-1] <= 1: cl[-1].append(y)
        else: cl.append([y])
    return [(c[0] + c[-1]) / 2 for c in cl if len(c) <= 6]
def track(t_start, M0=8.0, M1=20.0):
    y = y0 - t_start * (y0 - y7) / 7; out = []
    for x in range(int(px_of(M0)), int(px_of(M1)) - 1):
        c = clusters(x)
        if c:
            b = min(c, key=lambda v: abs(v - y))
            if abs(b - y) < 4: y = b
        out.append((10 ** ((x - x1) / (x20 - x1) * math.log10(20)), t_of(y)))
    return out
# ---- SVG frame ----
W, H = 640, 400; s = header(W, H); lab = ''
L, R, T, B = 90, 560, 40, 320                      # plot box (svg)
Mmin, Mmax, tmin, tmax = 8, 20, 0.6, 1.6
X = lambda M: L + (R - L) * math.log10(M / Mmin) / math.log10(Mmax / Mmin)
Y = lambda t: B - (B - T) * (t - tmin) / (tmax - tmin)
s += f'<rect x="{L}" y="{T}" width="{R - L}" height="{B - T}" stroke-width="1"/>\n'
for M in (8, 9, 10, 12, 14, 15, 16, 18, 20):
    s += f'<path d="M{X(M):.1f} {T} L{X(M):.1f} {B}" stroke-width="0.5" stroke-dasharray="2 4"/>\n'
    lab += text(round(X(M), 1), B + 20, [("n", str(M))], anchor="middle")
for k in range(6):
    t = 0.6 + 0.2 * k
    s += f'<path d="M{L} {Y(t):.1f} L{R} {Y(t):.1f}" stroke-width="0.5" stroke-dasharray="2 4"/>\n'
    lab += text(L - 8, round(Y(t) + 5, 1), [("n", f"{t:.1f}")], anchor="end")
for name, t0, w in (("4", 0.991, 1.2), ("5", 1.306, 2.4), ("6", 1.595, 1.2)):
    raw = track(t0)                                  # smooth pixel steps: quadratic fit in log M
    c = np.polyfit([math.log10(M) for M, _ in raw], [tt for _, tt in raw], 2)
    Ms = [8 * (20 / 8) ** (k / 60) for k in range(61)]
    pts = [(X(M), Y(float(np.polyval(c, math.log10(M))))) for M in Ms]
    s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" stroke-width="{w}"/>\n'
    lab += text(round(pts[-1][0] + 6, 1), round(pts[-1][1] + 5, 1), [("n", "TD" + name)])
# operating time line and reading
s += f'<path d="M{L} {Y(1.0):.1f} L{R} {Y(1.0):.1f}" stroke="{BLUE}" stroke-width="1.5"/>\n'
s += f'<path d="M{X(15):.1f} {Y(1.0):.1f} L{X(15):.1f} {B}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="5 4"/>\n'
s += f'<circle cx="{X(15):.1f}" cy="{Y(1.0):.1f}" r="4" fill="{BLUE}" stroke="none"/>\n'
s += end_group()
lab += ctext(BLUE, L + 8, round(Y(1.0) - 8, 1), [("v", "t"), ("n", " = 1.0 s")])
lab += ctext(BLUE, round(X(15) + 6, 1), B - 10, [("v", "M"), ("n", " ≈ 15")])
lab += text((L + R) / 2, B + 46, [("t", "電流倍數 "), ("v", "M"), ("n", " = "), ("v", "I"), ("sub", "relay"), ("n", "/"), ("v", "I"), ("sub", "tap"), ("t", "（對數刻度）")], anchor="middle")
lab += text(30, (T + B) / 2, [("t", "動作時間 "), ("v", "t"), ("t", "（s）")], anchor="middle").replace('<text ', f'<text transform="rotate(-90 30 {(T + B) / 2})" ', 1)
lab += text((L + R) / 2, 24, [("t", "CO-7 曲線局部放大（依官方圖 2 描出）")], anchor="middle")
s += lab + footer()
open(ROOT / '02_題解/技師題解/06_工業配電/figures/EE-113-06-5-td-curve.svg', 'w').write(s)
print(len(s))
