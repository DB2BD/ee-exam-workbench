"""EE-105-02-5 (1): half-wave vs centre-tapped full-wave rectifier, circuits and output waveforms (ideal diodes, resistive load)."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *


def xfmr(ox, ytop, ybot, ct):
    """AC source + primary + core + secondary (bumps facing the core); returns secondary x."""
    s = ac_source(ox + 40, (ytop + ybot) / 2) + line(ox + 40, ytop, ox + 40, (ytop + ybot) / 2 - 14) + line(ox + 40, (ytop + ybot) / 2 + 14, ox + 40, ybot)
    s += line(ox + 40, ytop, ox + 64, ytop) + line(ox + 40, ybot, ox + 64, ybot)
    s += coil(ox + 64, ytop, ox + 64, ybot, turns=5)
    s += line(ox + 76, ytop + 6, ox + 76, ybot - 6) + line(ox + 80, ytop + 6, ox + 80, ybot - 6)
    xs = ox + 92
    if ct:
        ym = (ytop + ybot) / 2
        s += coil(xs, ym, xs, ytop, turns=3) + coil(xs, ybot, xs, ym, turns=3) + dot(xs, ym)
    else:
        s += coil(xs, ybot, xs, ytop, turns=5)
    return s, xs


def wave(ox, y0, full):
    """Two input periods of v_o: half sine (half-wave) or |sin| (full-wave)."""
    pts = []
    for k in range(241):
        th = 4 * math.pi * k / 240
        v = math.sin(th)
        v = abs(v) if full else max(v, 0)
        pts.append((ox + 40 + 270 * k / 240, y0 - 40 * v))
    s = arrow(ox + 40, y0, ox + 330, y0) + arrow(ox + 40, y0 + 8, ox + 40, y0 - 56)
    s += poly(pts, w=2)
    avg = (2 if full else 1) / math.pi
    s += dashed(ox + 40, y0 - 40 * avg, ox + 310, y0 - 40 * avg)
    return s


W, H = 720, 360
s = header(W, H)
# (a) half-wave
a, xs = xfmr(0, 70, 190, False)
s += a + line(xs, 70, 140, 70) + diode(140, 70, 220, 70) + line(220, 70, 280, 70)
s += resistor(280, 70, 280, 190, zigs=6, lead=20) + line(xs, 190, 280, 190) + dot(280, 70) + dot(280, 190)
s += wave(0, 300, False)
# (b) centre-tapped full-wave
b, xs2 = xfmr(360, 60, 200, True)
s += b + line(xs2, 60, 500, 60) + diode(500, 60, 570, 60) + line(570, 60, 610, 60)
s += line(xs2, 200, 500, 200) + diode(500, 200, 570, 200) + line(570, 200, 610, 200)
s += line(610, 60, 610, 200) + dot(610, 130)
s += line(xs2, 130, 500, 130) + resistor(500, 130, 610, 130, zigs=6, lead=14)
s += wave(360, 300, True)
s += end_group()
s += text(6, 24, [("t", "(a) 半波：1 顆二極體")])
s += text(366, 24, [("t", "(b) 全波（中心抽頭）：2 顆二極體")])
s += text(22, 135, [("v", "v"), ("vsub", "s")], anchor="end")
s += text(180, 96, [("v", "D")], anchor="middle")
s += text(294, 134, [("v", "R"), ("vsub", "L")])
s += text(268, 98, [("n", "+")], anchor="end")
s += text(268, 176, [("n", "−")], anchor="end")
s += text(258, 140, [("v", "v"), ("vsub", "o")], anchor="end")
s += text(382, 135, [("v", "v"), ("vsub", "s")], anchor="end")
s += text(535, 86, [("v", "D"), ("sub", "1")], anchor="middle")
s += text(535, 226, [("v", "D"), ("sub", "2")], anchor="middle")
s += text(460, 152, [("t", "CT")])
s += text(555, 156, [("v", "R"), ("vsub", "L")], anchor="middle")
s += text(600, 124, [("n", "+")], anchor="end")
s += text(512, 124, [("n", "−")])
s += text(555, 112, [("v", "v"), ("vsub", "o")], anchor="middle")
s += text(46, 238, [("v", "v"), ("vsub", "o")])
s += text(406, 238, [("v", "v"), ("vsub", "o")])
s += ctext(340, 240, [("t", "虛線 "), ("v", "V"), ("sub", "DC"), ("n", " = "), ("v", "V"), ("vsub", "m"), ("n", "/π")], anchor="end", color=BLUE)
s += ctext(700, 240, [("t", "虛線 "), ("v", "V"), ("sub", "DC"), ("n", " = 2"), ("v", "V"), ("vsub", "m"), ("n", "/π")], anchor="end", color=BLUE)
s += text(40, 330, [("t", "漣波基頻 "), ("v", "f"), ("t", "；二次側電流含直流")])
s += text(400, 330, [("t", "漣波基頻 2"), ("v", "f"), ("t", "；兩半繞組輪流導通")])
s += footer()
write('EE-105-02-5-half-full-wave.svg', s)
