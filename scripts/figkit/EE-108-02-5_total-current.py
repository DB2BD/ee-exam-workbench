"""EE-108-02-5: gate timing of S1-S3 and the summed output current, (a) stated V_L = 3 V (no steady state), (b) V_L = 1.5 V."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 700, 520
X0, SEG = 130, 90            # one T/6 segment = 90 px, period T = 540 px
XT = X0 + 6 * SEG
s = header(W, H)
# gate rows
rows = ((1, 52), (2, 100), (3, 148))
for k, y in rows:
    on0 = X0 + (k - 1) * 2 * SEG
    s += poly([(X0, y), (on0, y), (on0, y - 22), (on0 + SEG, y - 22), (on0 + SEG, y), (XT + 10, y)], w=1.8)
for j in range(7):
    s += dashed(X0 + j * SEG, 20, X0 + j * SEG, 480)
# (a) V_L = 3 V: flat, fall 0.75, ... (60 px per A); start 3.375 A at y = 215
ya = lambda a: 215 + 60 * (3.375 - a)
pa, cur = [], 3.375
for j in range(6):
    x0, x1 = X0 + j * SEG, X0 + (j + 1) * SEG
    nxt = cur if j % 2 == 0 else cur - 0.75
    pa += [(x0, ya(cur)), (x1, ya(nxt))]
    cur = nxt
s += poly(pa, color=RED)
# (b) V_L = 1.5 V: triangle 1.35..1.65 (300 px per A), centre line 1.50 at y = 440
yb = lambda a: 440 - 300 * (a - 1.5)
pb = [(X0 + j * SEG, yb(1.35 if j % 2 == 0 else 1.65)) for j in range(7)]
s += poly(pb, color=RED)
s += dashed(X0, yb(1.65), XT, yb(1.65)) + dashed(X0, yb(1.35), XT, yb(1.35))
s += end_group()
t = []
for k, y in rows:
    t.append(text(X0 - 10, y - 4, [("v", "S"), ("sub", str(k))], anchor="end"))
t.append(text(X0 + SEG / 2, 20, [("v", "T"), ("n", "/6")], anchor="middle"))
t.append(text(X0 + 3 * SEG, 498, [("v", "T"), ("n", "/2")], anchor="middle"))
t.append(text(XT, 498, [("v", "T")], anchor="middle"))
t.append(text(6, 200, [("t", "(甲) "), ("v", "V"), ("vsub", "L"), ("n", " = 3 V")]))
t.append(text(X0 - 10, 240, [("v", "i"), ("vsub", "o")], anchor="end"))
t.append(text(X0 + SEG / 2, ya(3.375) - 8, [("t", "斜率 0")], anchor="middle"))
t.append(text(X0 + 1.5 * SEG + 8, ya(3.0) - 22, [("n", "−0.09 A/μs")], anchor="start"))
t.append(text(X0 + 4 * SEG, ya(2.625) - 30, [("t", "每 "), ("v", "T"), ("n", "/3"), ("t", " 淨降 "), ("n", "Δ"), ("v", "I"), ("vsub", "o"), ("n", " = 0.75 A")], anchor="middle"))
t.append(text(6, 372, [("t", "(乙) "), ("v", "V"), ("vsub", "L"), ("n", " = 1.50 V")]))
t.append(text(X0 - 10, yb(1.65) + 5, [("v", "I"), ("vsub", "o,max"), ("n", " = 1.65 A")], anchor="end"))
t.append(text(X0 - 10, yb(1.35) + 5, [("v", "I"), ("vsub", "o,min"), ("n", " = 1.35 A")], anchor="end"))
t.append(text(X0 + SEG / 2, yb(1.65) - 8, [("n", "+0.036 A/μs")], anchor="middle"))
t.append(text(X0 + 1.5 * SEG, yb(1.65) - 8, [("n", "−0.036 A/μs")], anchor="middle"))
s += ''.join(t) + footer()
write('EE-108-02-5-total-current.svg', s)
