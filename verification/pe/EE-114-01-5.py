"""EE-114-01-5 independent check: mesh analysis in s-domain.

Givens (official crop): is=10u(t) A up into top-left node; middle branch: 2Ix
(+ top) in series with 5 ohm; 2 H inductor (Ix to the right, zero initial
current) into 5 ohm output resistor (vo across it).
"""
import sympy as sp

s, t = sp.symbols("s t", positive=True)
Ix, Im = sp.symbols("Ix Im")  # Im: middle-branch current downward
Is = 10 / s
eqs = [
    sp.Eq(Im + Ix, Is),                              # KCL at top node
    sp.Eq(2 * Ix + 5 * Im, (2 * s + 5) * Ix),        # middle branch voltage = right branch voltage
]
sol = sp.solve(eqs, [Ix, Im], dict=True)[0]
Vo = sp.simplify(5 * sol[Ix])
assert sp.simplify(Vo - 125 / (s * (s + 4))) == 0
vo = sp.inverse_laplace_transform(Vo, s, t)
assert sp.simplify(vo - sp.Rational(125, 4) * (1 - sp.exp(-4 * t))) == 0
print("PASS EE-114-01-5")
