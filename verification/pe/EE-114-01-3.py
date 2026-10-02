"""EE-114-01-3 independent check: series RLC after the switch opens.

Givens (official crop): 24 V, 4 ohm, 1 H, 0.25 F (v across C), 1 ohm switched
out at t=0; circuit at DC steady state with switch closed for t<0.
"""
import sympy as sp

t = sp.symbols("t", positive=True)
# t<0 DC: L short, C open -> 24 V across 4+1 ohm.
i0 = sp.Rational(24, 5)
v0 = 1 * i0
assert i0 == sp.Rational(24, 5) and v0 == sp.Rational(24, 5)

# t>0: state-space x=[v, i]; C v' = i, L i' = 24 - 4 i - v. Solve via matrix exponential.
A = sp.Matrix([[0, 4], [-1, -4]])
b = sp.Matrix([0, 24])
x_inf = -A.inv() * b
x = x_inf + (A * t).exp() * (sp.Matrix([v0, i0]) - x_inf)
v = sp.simplify(x[0])
expected = 24 - sp.Rational(96, 5) * (1 + t) * sp.exp(-2 * t)
assert sp.simplify(v - expected) == 0
assert sp.simplify(x[1] - sp.Rational(24, 5) * (1 + 2 * t) * sp.exp(-2 * t)) == 0
print("PASS EE-114-01-3")
