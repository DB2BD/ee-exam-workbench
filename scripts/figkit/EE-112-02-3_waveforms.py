import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

RED = "#c0392b"; FILL = "#fde2e0"
X0, X1, X2, XE = 110, 434, 650, 680   # t = 0, DTs, Ts, axis end

def red_arrow(x1, y1, x2, y2):
    return f'<g stroke="{RED}">' + arrow(x1, y1, x2, y2).replace('fill="#000"', f'fill="{RED}"') + '</g>\n'

def red_text(x, y, parts, anchor="start"):
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{RED}"', 1)

def axes(y0, ytop, ybot):
    """Horizontal t-axis at y0 with arrow, vertical axis from ybot up to ytop with arrow."""
    return arrow(X0, ybot, X0, ytop) + arrow(X0, y0, XE, y0)

def tick_y(y):
    return line(X0 - 4, y, X0, y)

def dashed(x1, y1, x2, y2, w=1):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke-width="{w}" stroke-dasharray="4 3"/>\n'

def poly(pts, w=2.2):
    return '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" stroke-width="{w}"/>\n'

W, H = 720, 480
s = header(W, H)
# discharge area of i_C (0 < t < DTs, i_C = -Io) shaded first so lines draw on top
s += f'<rect x="{X0}" y="410" width="{X1 - X0}" height="18" fill="{FILL}" stroke="none"/>\n'
# time guides
s += dashed(X1, 40, X1, 444) + dashed(X2, 40, X2, 444)
# v_L panel: zero at 95, +24 V -> 65, -36 V -> 140
s += axes(95, 30, 150) + tick_y(65) + tick_y(140)
s += poly([(X0, 65), (X1, 65), (X1, 140), (X2, 140)])
# i_L panel: zero at 300, 8 px/A
s += axes(300, 168, 310) + tick_y(184.8) + tick_y(228) + tick_y(271.2)
s += dashed(X0, 228, X2, 228, 1.2)
s += poly([(X0, 271.2), (X1, 184.8), (X2, 271.2)])
s += dashed(X1, 184.8, 708, 184.8) + dashed(X2, 271.2, 708, 271.2)
# i_C panel: zero at 410, 5 px/A
s += axes(410, 340, 440) + tick_y(356) + tick_y(428)
s += poly([(X0, 428), (X1, 428), (X1, 356), (X2, 410)])
s += end_group()
# ripple dimension (red, both ends)
s += red_arrow(700, 228, 700, 186.5) + red_arrow(700, 228, 700, 269.5)
s += red_text(706, 176, [("n", "Δ"), ("v", "i"), ("vsub", "L"), ("n", " = 10.80 A")], anchor="end")
# axis names and t labels
s += text(X0 + 8, 36, [("v", "v"), ("vsub", "L")])
s += text(X0 + 8, 176, [("v", "i"), ("vsub", "L")])
s += text(X0 + 8, 348, [("v", "i"), ("vsub", "C")])
for y in (114, 318, 428):
    s += text(XE + 6, y, [("v", "t")])
# v_L ticks / notes
s += text(104, 70, [("n", "24 V")], anchor="end")
s += text(104, 100, [("n", "0")], anchor="end")
s += text(104, 145, [("n", "−36 V")], anchor="end")
s += text(200, 58, [("n", "+"), ("v", "V"), ("sub", "s"), ("t", "（"), ("v", "Q"), ("t", " 導通）")])
s += text(480, 133, [("n", "−"), ("v", "V"), ("vsub", "o"), ("t", "（"), ("v", "D"), ("t", " 導通）")])
# i_L ticks / notes
s += text(104, 190, [("n", "14.40 A")], anchor="end")
s += text(104, 233, [("n", "9 A")], anchor="end")
s += text(104, 276, [("n", "3.60 A")], anchor="end")
s += text(104, 305, [("n", "0")], anchor="end")
s += text(124, 221, [("t", "平均 "), ("v", "I"), ("vsub", "L"), ("n", " = 9 A")])
s += text(462, 292, [("t", "谷值 "), ("n", "0.4"), ("v", "I"), ("vsub", "L"), ("n", " = 3.60 A")])
# i_C ticks / notes
s += text(104, 361, [("n", "10.80 A")], anchor="end")
s += text(104, 415, [("n", "0")], anchor="end")
s += text(104, 433, [("n", "−3.60 A")], anchor="end")
s += red_text(170, 400, [("t", "放電 "), ("v", "Q"), ("n", " = "), ("v", "I"), ("vsub", "o"), ("n", "·"), ("v", "DT"), ("sub", "s")])
s += text(560, 362, [("v", "i"), ("vsub", "L"), ("n", " − "), ("v", "I"), ("vsub", "o")])
# time ticks
s += text(X0, 464, [("n", "0")], anchor="middle")
s += text(X1, 464, [("v", "DT"), ("sub", "s"), ("n", " = 6 μs")], anchor="middle")
s += text(X2, 464, [("v", "T"), ("sub", "s"), ("n", " = 10 μs")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/02_電子學_含電力電子/figures/EE-112-02-3-waveforms.svg'
out.write_text(s); print(len(s))
