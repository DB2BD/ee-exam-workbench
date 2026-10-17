"""EE-105-04-1 fig 1: v_L(t) (= v_ac after the switch closes at the + to - zero crossing, t = 0) and
i_L(t) for the first period: 0 -> -5 A at 0.5 ms -> 0 at 1 ms; average -2.50 A."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from power_parts import dashed, poly
from circuit_parts import ttext

X = lambda t: 200 + 400 * t            # t in ms
Y1, KV = 110, 5.0                     # panel 1 baseline, px per V
Y2, KI = 250, 30.0                    # panel 2 baseline, px per A
W, H = 700, 450
s = header(W, H)
s += arrow(X(-0.42), Y1, X(1.2), Y1) + arrow(X(0), Y1 + 62, X(0), Y1 - 70)
s += arrow(X(-0.42), Y2, X(1.2), Y2) + arrow(X(0), Y2 + 5 * KI + 22, X(0), Y2 - 34)
# v_ac before closing (dashed), v_L after closing (blue)
s += dashed(X(-0.42), Y1 - 10 * KV, X(0), Y1 - 10 * KV)
s += poly([(X(0), Y1), (X(0), Y1 + 10 * KV), (X(0.5), Y1 + 10 * KV), (X(0.5), Y1 - 10 * KV),
           (X(1), Y1 - 10 * KV), (X(1), Y1)], w=2.2, color=BLUE)
# i_L (red) and its average
s += poly([(X(-0.42), Y2), (X(0), Y2), (X(0.5), Y2 + 5 * KI), (X(1), Y2)], w=2.2, color=RED)
s += dashed(X(0), Y2 + 2.5 * KI, X(1), Y2 + 2.5 * KI)
for t in (0.5, 1.0):
    s += dashed(X(t), Y1 - 10 * KV, X(t), Y2 + 5 * KI + 10)
s += dashed(X(0), Y2 + 5 * KI, X(0.5), Y2 + 5 * KI)
s += dot(X(0.5), Y2 + 5 * KI)
s += end_group()
s += ttext(X(0) + 8, Y1 - 56, [("v", "v"), ("vsub", "L")], color=BLUE)
s += text(X(-0.42), Y1 - 10 * KV - 10, [("v", "v"), ("vsub", "ac"), ("t", "（閉合前）")])
s += text(X(0) - 8, Y1 + 10 * KV + 5, [("n", "−10 V")], anchor="end")
s += text(X(1) + 8, Y1 - 10 * KV + 5, [("n", "10 V")])
s += text(X(1.2), Y1 + 22, [("v", "t"), ("n", " (ms)")], anchor="end")
s += text(X(1.2), Y2 + 22, [("v", "t"), ("n", " (ms)")], anchor="end")
s += ttext(X(0) + 8, Y2 - 18, [("v", "i"), ("vsub", "L")], color=RED)
s += text(X(0) - 8, Y2 + 5 * KI + 5, [("n", "−5 A")], anchor="end")
s += text(X(0) - 8, Y2 + 2.5 * KI + 5, [("n", "−2.50 A")], anchor="end")
s += text(X(0.5), Y2 + 5 * KI + 30, [("v", "i"), ("vsub", "L"), ("n", "(0.5 ms) = −5 A")], anchor="middle")
s += text(X(0.5) - 10, Y2 + 42, [("v", "di"), ("vsub", "L"), ("n", "/"), ("v", "dt")], anchor="end")
s += text(X(0.5) - 10, Y2 + 62, [("n", "= −10 A/ms")], anchor="end")
s += text(X(0.5) + 10, Y2 + 42, [("v", "di"), ("vsub", "L"), ("n", "/"), ("v", "dt")])
s += text(X(0.5) + 10, Y2 + 62, [("n", "= +10 A/ms")])
s += text(X(1) + 10, Y2 + 2.5 * KI + 5, [("t", "平均 "), ("v", "I"), ("vsub", "L"), ("sub", ","), ("vsub", "avg")])
for t, lab in ((0, "0"), (0.5, "0.5"), (1.0, "1")):
    s += text(X(t) + 5, Y2 + 20, [("n", lab)])
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-105-04-1-waveforms.svg'
out.write_text(s)
print(out.name, len(s))
