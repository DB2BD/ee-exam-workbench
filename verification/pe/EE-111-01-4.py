"""EE-111-01-4 independent check: h-parameters from a full nodal model.

Givens (official crop): port 1 (+V1, I1 in) -> 1 ohm -> node a; a: 2 ohm to
ground, 2 ohm to node b; b: dependent source 4*I1 pointing up (ground -> b),
1 ohm to port 2 (+V2, I2 in).
"""
import sympy as sp

V1, V2, I1, I2, va, vb = sp.symbols("V1 V2 I1 I2 va vb")
eqs = [
    sp.Eq(I1, (V1 - va) / 1),
    sp.Eq(I1, va / 2 + (va - vb) / 2),       # KCL at a
    sp.Eq((vb - va) / 2 + (vb - V2) / 1, 4 * I1),  # KCL at b (source injects 4 I1)
    sp.Eq(I2, (V2 - vb) / 1),
]
sol = sp.solve(eqs, [V1, I2, va, vb], dict=True)[0]  # V1, I2 in terms of I1, V2
V1e, I2e = sp.expand(sol[V1]), sp.expand(sol[I2])
h = sp.Matrix([[V1e.coeff(I1), V1e.coeff(V2)], [I2e.coeff(I1), I2e.coeff(V2)]])
print(h)
assert h == sp.Matrix([[sp.Rational(19, 5), sp.Rational(2, 5)], [sp.Rational(-18, 5), sp.Rational(1, 5)]])
print("PASS EE-111-01-4")
