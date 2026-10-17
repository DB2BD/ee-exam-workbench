"""EE-104-04-1 fig 1: reluctance network of the ring + Y-spoke core (complete graph on C, T, B, A).
Every branch is R; MMF F1 = N1 i1 in branch C-T (+ toward T, drives phi1 C->T),
MMF F2 = N2 i2 in branch B-A (+ toward A, drives phi2 B->A). Flux arrows follow the reference directions."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import vsrc, ttext


def res_on(p, q, f0=0.38, f1=0.62):
    """Resistor (reluctance) on the middle part of segment p-q, wires on both ends."""
    a = (p[0] + (q[0] - p[0]) * f0, p[1] + (q[1] - p[1]) * f0)
    b = (p[0] + (q[0] - p[0]) * f1, p[1] + (q[1] - p[1]) * f1)
    return line(*p, *a) + resistor(*a, *b, lead=6, amp=7) + line(*b, *q)


T, C, A, B = (300, 40), (300, 250), (80, 400), (520, 400)
W, H = 600, 470
s = header(W, H)
# branch C-T: F1 source near T (+ on top), R near C
s += line(300, 40, 300, 110) + vsrc(300, 110, 300, 162) + line(300, 162, 300, 172)
s += resistor(300, 172, 300, 236, lead=6) + line(300, 236, 300, 250)
# spokes C-A, C-B and arcs T-A, T-B
s += res_on(C, A) + res_on(C, B) + res_on(T, A) + res_on(T, B)
# branch B-A: F2 source near A (+ toward A, on the left), R near B
s += line(80, 400, 140, 400) + vsrc(140, 400, 200, 400) + line(200, 400, 340, 400)
s += resistor(340, 400, 440, 400, lead=8) + line(440, 400, 520, 400)
for p in (T, C, A, B):
    s += dot(*p)
# reference flux arrows (red): phi1 upward beside C-T, phi2 leftward under B-A
s += arrow(326, 238, 326, 190, color=RED)
s += arrow(330, 424, 280, 424, color=RED)
s += end_group()
s += text(300, 30, [("v", "T")], anchor="middle")
s += text(312, 276, [("v", "C")])
s += text(66, 416, [("v", "A")], anchor="end")
s += text(534, 416, [("v", "B")])
s += ttext(322, 142, [("v", "ℱ"), ("sub", "1")], color=BLUE)
s += ttext(170, 434, [("v", "ℱ"), ("sub", "2")], anchor="middle", color=BLUE)
s += ttext(336, 220, [("v", "ϕ"), ("sub", "1")], color=RED)
s += ttext(305, 450, [("v", "ϕ"), ("sub", "2")], anchor="middle", color=RED)
s += text(284, 210, [("v", "R")], anchor="end")
s += text(390, 386, [("v", "R")], anchor="middle")
for p, q, dx, dy in ((C, A, 6, 24), (C, B, -6, 24), (T, A, -22, -4), (T, B, 22, -4)):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    s += text(mx + dx, my + dy, [("v", "R")], anchor="middle")
s += ttext(586, 456, [("v", "ℱ"), ("sub", "1"), ("n", " = "), ("v", "N"), ("sub", "1"), ("v", "i"), ("sub", "1"), ("t", "，"),
                     ("v", "ℱ"), ("sub", "2"), ("n", " = "), ("v", "N"), ("sub", "2"), ("v", "i"), ("sub", "2")], anchor="end", color=BLUE)
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-104-04-1-reluctance-network.svg'
out.write_text(s)
print(out.name, len(s))
