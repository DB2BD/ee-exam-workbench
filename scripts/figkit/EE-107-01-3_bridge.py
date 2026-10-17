"""EE-107-01-3: original bridge, Delta (a, b, c) to be converted, reference directions of I0..I5, V1 = V_bd, V2 = V_cd."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 680, 400
A, B, C, D = (380, 70), (230, 220), (530, 220), (380, 370)
XS = 80


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def side_arrow(p, q, off, t0=0.38, t1=0.62):
    """Red reference arrow parallel to segment p->q, offset by `off` px to the left of travel direction."""
    L = math.hypot(q[0] - p[0], q[1] - p[1]); nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L
    s0, s1 = lerp(p, q, t0), lerp(p, q, t1)
    return tint_arrow(s0[0] + off * nx, s0[1] + off * ny, s1[0] + off * nx, s1[1] + off * ny)


s = header(W, H)
s += f'<path d="M{A[0]} {A[1]} L{B[0]} {B[1]} L{C[0]} {C[1]} Z" fill="{FILL_BLUE}" stroke="none"/>\n'
s += line(XS, A[1], A[0], A[1]) + line(XS, D[1], D[0], D[1]) + vsrc(XS, A[1], XS, D[1], r=18)
s += line(*A, *lerp(A, B, 0.3)) + cap(*lerp(A, B, 0.3), *lerp(A, B, 0.7)) + line(*lerp(A, B, 0.7), *B)
s += line(*A, *lerp(A, C, 0.1)) + resistor(*lerp(A, C, 0.1), *lerp(A, C, 0.5), zigs=4, lead=6) + coil(*lerp(A, C, 0.5), *lerp(A, C, 0.95), turns=3) + line(*lerp(A, C, 0.95), *C)
s += resistor(B[0], B[1], C[0], C[1], lead=110)
s += line(*B, *lerp(B, D, 0.08)) + resistor(*lerp(B, D, 0.08), *lerp(B, D, 0.48), zigs=4, lead=6) + coil(*lerp(B, D, 0.52), *lerp(B, D, 0.92), turns=3) + line(*lerp(B, D, 0.48), *lerp(B, D, 0.52)) + line(*lerp(B, D, 0.92), *D)
s += line(*C, *lerp(C, D, 0.3)) + cap(*lerp(C, D, 0.3), *lerp(C, D, 0.7)) + line(*lerp(C, D, 0.7), *D)
for p in (A, B, C, D):
    s += dot(*p)
s += tint_arrow(170, A[1] - 16, 240, A[1] - 16)                       # I0 into a
s += side_arrow(A, B, 22) + side_arrow(A, C, 22) + side_arrow(B, C, -18, 0.62, 0.8)
s += side_arrow(B, D, 22) + side_arrow(C, D, -22)
s += end_group()
s += text(A[0], A[1] - 14, [("v", "a")], anchor="middle") + text(B[0] - 14, B[1] + 5, [("v", "b")], anchor="end")
s += text(C[0] + 14, C[1] + 5, [("v", "c")]) + text(D[0], D[1] + 24, [("v", "d")], anchor="middle")
s += text(XS + 26, 228, [("n", "120∠0° V")])
s += text(262, 118, [("n", "−"), ("v", "j"), ("n", "4 Ω")], anchor="end")
s += text(432, 140, [("n", "63.2 Ω")], anchor="end") + text(512, 176, [("v", "j"), ("n", "2.4 Ω")])
s += text(320, 238, [("n", "10 Ω")], anchor="middle")
s += text(258, 284, [("n", "20 Ω")], anchor="end") + text(296, 340, [("v", "j"), ("n", "60 Ω")], anchor="end")
s += text(500, 318, [("n", "−"), ("v", "j"), ("n", "20 Ω")])
s += text(420, 200, [("t", "Δ（"), ("v", "a"), ("t", "、"), ("v", "b"), ("t", "、"), ("v", "c"), ("t", "）")], anchor="middle")
s += ttext(205, A[1] - 24, [("v", "I"), ("sub", "0")], anchor="middle", color=RED)
s += ttext(330, 190, [("v", "I"), ("sub", "1")], color=RED)
s += ttext(490, 104, [("v", "I"), ("sub", "2")], color=RED)
s += ttext(478, 246, [("v", "I"), ("sub", "3")], color=RED)
s += ttext(352, 268, [("v", "I"), ("sub", "4")], color=RED)
s += ttext(432, 268, [("v", "I"), ("sub", "5")], anchor="end", color=RED)
s += ttext(B[0] - 12, B[1] + 34, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(B[0] - 40, 300, [("v", "V"), ("sub", "1")], anchor="middle", color=BLUE)
s += ttext(D[0] - 60, D[1] - 4, [("n", "−")], anchor="middle", color=BLUE)
s += ttext(C[0] + 14, C[1] + 34, [("n", "+")], anchor="middle", color=BLUE)
s += ttext(C[0] + 52, 300, [("v", "V"), ("sub", "2")], anchor="middle", color=BLUE)
s += ttext(D[0] + 60, D[1] - 4, [("n", "−")], anchor="middle", color=BLUE)
s += footer()
write('EE-107-01-3-bridge.svg', s)
