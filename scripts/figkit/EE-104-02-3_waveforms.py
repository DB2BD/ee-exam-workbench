"""EE-104-02-3: six-pulse bridge, resistive load: line voltages and v_o envelope, conduction table,
and the phase-a line current i_a (positive via D1, negative via D4). theta measured from v_an = V_p sin(theta)."""
import math, pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

X = lambda th: 90 + 1.5 * th            # theta (deg) -> px
Y1, A1 = 160, 120                        # panel 1 baseline, px per V_m
Y3, A3 = 340, 50                         # panel 3 baseline, px per V_m/R
LL = {"ab": 30, "ac": -30, "bc": -90, "ba": -150, "ca": 150, "cb": 90}  # v_xy = V_m sin(theta + shift)


def vll(name, th):
    return math.sin(math.radians(th + LL[name]))


def env(th):
    return max(vll(n, th) for n in LL)


W, H = 720, 460
s = header(W, H)
# panel 1: line voltages (thin) where positive, envelope v_o (blue), average dashed
s += arrow(X(0), Y1, X(372), Y1) + arrow(X(0), Y1 + 6, X(0), Y1 - A1 - 20)
for n in LL:
    seg = []
    for k in range(181):
        th = k * 2.0
        v = vll(n, th)
        if v >= 0.5:
            seg.append((X(th), Y1 - A1 * v))
        elif seg:
            s += poly(seg, w=0.8); seg = []
    if seg:
        s += poly(seg, w=0.8)
s += poly([(X(k * 1.0), Y1 - A1 * env(k * 1.0)) for k in range(361)], w=2.4, color=BLUE)
avg = 3 / math.pi
s += dashed(X(0), Y1 - A1 * avg, X(360), Y1 - A1 * avg)
for th in (30, 90, 150, 210, 270, 330):
    s += dashed(X(th), Y1, X(th), Y1 - A1 * env(th), w=0.8)
# panel 2: conduction table
top = [("1", 30, 150), ("3", 150, 270), ("5", 270, 360), ("5", 0, 30)]
bot = [("6", 0, 90), ("2", 90, 210), ("4", 210, 330), ("6", 330, 360)]
for row, y in ((top, 184), (bot, 210)):
    for d, a, b in row:
        s += f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="22" stroke-width="1"/>\n'
# panel 3: i_a
s += arrow(X(0), Y3, X(372), Y3) + arrow(X(0), Y3 + A3 + 10, X(0), Y3 - A3 - 14)
ia = []
for k in range(361):
    th = k * 1.0
    i = env(th) if 30 <= th <= 150 else (-env(th) if 210 <= th <= 330 else 0.0)
    ia.append((X(th), Y3 - A3 * i))
s = s.replace(G_OPEN, f'<path d="M{X(30):.1f} {Y3} ' + ' '.join(f'L{x:.1f} {y:.1f}' for x, y in ia[30:151]) + f' L{X(150):.1f} {Y3} Z" fill="{FILL_RED}" stroke="none"/>\n'
              + f'<path d="M{X(210):.1f} {Y3} ' + ' '.join(f'L{x:.1f} {y:.1f}' for x, y in ia[210:331]) + f' L{X(330):.1f} {Y3} Z" fill="{FILL_RED}" stroke="none"/>\n' + G_OPEN, 1)
s += poly(ia, w=2.2, color=RED)
s += end_group()
# labels
names = [("ab", 60), ("ac", 120), ("bc", 180), ("ba", 240), ("ca", 300), ("cb", 360)]
for n, c in names[:-1] + [("cb", 15)]:
    if True:
        s += text(X(c), Y1 - A1 - 8, [("v", "v"), ("vsub", n)], anchor="middle")
s += ctext(X(364), Y1 - A1 - 2, [("v", "v"), ("vsub", "o")], color=BLUE)
s += text(X(364), Y1 - A1 * avg + 14, [("v", "V"), ("vsub", "o")])
s += text(X(0) - 6, Y1 - A1 + 5, [("v", "V"), ("vsub", "m")], anchor="end")
s += text(X(0) - 6, Y1 + 5, [("n", "0")], anchor="end")
for th in (0, 30, 90, 150, 210, 270, 330, 360):
    s += text(X(th), Y3 + A3 + 44, [("n", f"{th}°")], anchor="middle")
s += text(X(372), Y1 + 20, [("v", "θ")], anchor="end")
for row, y in ((top, 184), (bot, 210)):
    for d, a, b in row:
        s += text((X(a) + X(b)) / 2, y + 14, [("v", "D"), ("sub", d)], anchor="middle")
s += text(X(0) - 6, 200, [("t", "上臂")], anchor="end")
s += text(X(0) - 6, 226, [("t", "下臂")], anchor="end")
s += ctext(X(0) - 6, Y3 - A3 + 8, [("v", "i"), ("vsub", "a")], anchor="end")
s += ctext(X(90), Y3 - A3 - 8, [("t", "經 "), ("v", "D"), ("sub", "1"), ("n", "：+"), ("v", "i"), ("vsub", "o")], anchor="middle")
s += ctext(X(270), Y3 + A3 + 22, [("t", "經 "), ("v", "D"), ("sub", "4"), ("n", "：−"), ("v", "i"), ("vsub", "o")], anchor="middle")
s += text(X(372), Y3 - 8, [("v", "θ")], anchor="end")
s += text(X(0), H - 8, [("v", "θ"), ("n", " = "), ("v", "ωt"), ("t", "，以 "), ("v", "v"), ("vsub", "an"), ("t", " 正向過零為 0°；"), ("v", "V"), ("vsub", "m"), ("n", " = 537.40 V"), ("t", "，"), ("v", "V"), ("vsub", "o"), ("n", " = 513.18 V")])
s += footer()
write('EE-104-02-3-waveforms.svg', s)
