"""Shared geometry for the EE-113-01-3 Δ figures (coupled and decoupled)."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

A, B, C = (420, 70), (290, 295), (550, 295)
CEN = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)
BRANCHES = [(A, B, "ab"), (B, C, "bc"), (C, A, "ca")]  # reference direction a→b, b→c, c→a
T_R = (0.10, 0.40)   # resistor span (fraction of branch)
T_L = (0.54, 0.88)   # coil span

def at(P, Q, t, d=0.0):
    """Point at fraction t along P→Q, shifted d px along the outward normal (away from centroid)."""
    x, y = P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t
    L = math.hypot(Q[0] - P[0], Q[1] - P[1]); nx, ny = -(Q[1] - P[1]) / L, (Q[0] - P[0]) / L
    mx, my = (P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2
    if (mx + nx - CEN[0]) ** 2 + (my + ny - CEN[1]) ** 2 < (mx - CEN[0]) ** 2 + (my - CEN[1]) ** 2:
        nx, ny = -nx, -ny
    return x + nx * d, y + ny * d, nx

def anchor(nx):
    return "start" if nx > 0.3 else ("end" if nx < -0.3 else "middle")

def branch(P, Q):
    s = ''
    r0, r1 = at(P, Q, T_R[0]), at(P, Q, T_R[1]); l0, l1 = at(P, Q, T_L[0]), at(P, Q, T_L[1])
    s += line(P[0], P[1], r0[0], r0[1]) + resistor(r0[0], r0[1], r1[0], r1[1], zigs=6, lead=4)
    # svgkit.coil bulges to the left of its drawing direction; draw it so the bumps face outward
    o = at(P, Q, 0.5, 1.0); m = at(P, Q, 0.5); ox, oy = o[0] - m[0], o[1] - m[1]
    ux, uy = Q[0] - P[0], Q[1] - P[1]
    c0, c1 = (l1, l0) if ux * oy - uy * ox > 0 else (l0, l1)
    s += line(r1[0], r1[1], l0[0], l0[1]) + coil(c0[0], c0[1], c1[0], c1[1], turns=4)
    s += line(l1[0], l1[1], Q[0], Q[1])
    return s

def head(P, Q, t):
    """Solid triangle head on the wire at fraction t, pointing P→Q."""
    x, y, _ = at(P, Q, t); ux, uy = (Q[0] - P[0]), (Q[1] - P[1]); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    return arrow(x - ux * 2, y - uy * 2, x + ux * 5, y + uy * 5)

def frame(ylc):
    """Terminals a, b, c and the connecting wires; ylc = y of the c-terminal wire."""
    s = line(64, A[1], A[0], A[1]) + line(64, B[1], B[0], B[1])
    s += line(C[0], C[1], C[0], ylc) + line(C[0], ylc, 64, ylc)
    for y in (A[1], B[1], ylc):
        s += f'<circle cx="60" cy="{y}" r="4" fill="#fff"/>\n'
    for P in (A, B, C):
        s += dot(*P)
    return s

def labels_terminals(ylc):
    s = text(40, A[1] + 5, [("v", "a")], anchor="middle")
    s += text(40, B[1] + 5, [("v", "b")], anchor="middle")
    s += text(40, ylc + 5, [("v", "c")], anchor="middle")
    return s

def out_path(name):
    return pathlib.Path(__file__).resolve().parents[2].joinpath(f'02_題解/技師題解/01_電路學/figures/{name}')

RED, BLUE = "#c0392b", "#1f5fa8"
def tint(s, color):
    """Recolor a snippet produced by svgkit (arrow/text) to an accent color."""
    if s.startswith('<text'):
        return s.replace('#000', color)
    return f'<g stroke="{color}">' + s.replace('#000', color) + '</g>\n'
