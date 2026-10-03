"""EE-111-01-1 independent check: phasor nodal analysis of the active filter.

Givens (official crop): vs = 2 sin(400 t) V -> 10 kOhm -> node A; A: 0.25 uF to
ground, 20 kOhm to vo, 0.5 uF to node B; B: 10 kOhm to ground and op-amp (+)
input; (-) input: 20 kOhm to ground, 40 kOhm to vo (non-inverting gain 3).
"""
import cmath
import math

import sympy as sp

w = 400
s = sp.I * w
R1, R2, R3 = 10e3, 10e3, 20e3
C1, C2 = 0.25e-6, 0.5e-6
K = 1 + sp.Rational(40, 20)
vs = 2  # sine reference, phase 0
vA, vB = sp.symbols("vA vB")
vo = K * vB
eqs = [
    sp.Eq((vA - vs) / R1 + vA * s * C1 + (vA - vB) * s * C2 + (vA - vo) / R3, 0),
    sp.Eq((vB - vA) * s * C2 + vB / R2, 0),
]
sol = sp.solve(eqs, [vA, vB], dict=True)[0]
Vo = complex(sp.N(vo.subs(sol)))
amp, ph = abs(Vo), math.degrees(cmath.phase(Vo))
print(f"Vo = {amp:.5f} V at {ph:.4f} deg (sine reference)")

# Independent route: transfer function H(s) by symbolic s, then evaluate.
S = sp.symbols("s")
a, b = sp.symbols("a b")
e2 = [
    sp.Eq((a - 1) / R1 + a * S * C1 + (a - b) * S * C2 + (a - K * b) / R3, 0),
    sp.Eq((b - a) * S * C2 + b / R2, 0),
]
sb = sp.solve(e2, [a, b], dict=True)[0]
H = sp.simplify(K * sb[b])
H400 = complex(sp.N(H.subs(S, sp.I * w)))
assert abs(2 * H400 - Vo) < 1e-9

assert math.isclose(amp, 2 * abs(H400), rel_tol=1e-9)
print("H(s) =", sp.factor(H))
# boxed: vo = 24/sqrt(37) sin(400t - atan(1/6)) = 3.9456 sin(400t - 9.462 deg) V
assert abs(amp - 24 / math.sqrt(37)) < 1e-9
assert abs(ph + math.degrees(math.atan(1 / 6))) < 1e-9
assert abs(Vo - (144 - 24j) / 37) < 1e-9
print("PASS EE-111-01-1")
