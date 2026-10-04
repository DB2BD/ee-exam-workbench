"""EE-110-01-2 independent check: ABCD (transmission) parameters.

Givens (official crop): port 1 -> series R1 -> node a; a: shunt R2 || C to the
bottom rail; a -> series L -> node b = port 2 (+); b: shunt R3.  I1 enters
port 1, I2 enters port 2 (so V1 = A V2 - B I2, I1 = C V2 - D I2).
The check solves the circuit by nodal analysis (not by cascading matrices).
"""
import sympy as sp

s, R1, R2, R3, L, C = sp.symbols("s R1 R2 R3 L C", positive=True)
V1, I1, V2, I2, va = sp.symbols("V1 I1 V2 I2 va")
Y2 = 1 / R2 + s * C
eqs = [
    sp.Eq(I1, (V1 - va) / R1),
    sp.Eq(I1, va * Y2 + (va - V2) / (s * L)),
    sp.Eq(I2 + (va - V2) / (s * L), V2 / R3),
]
sol = sp.solve(eqs, [V1, I1, va], dict=True)[0]
V1e, I1e = sp.expand(sol[V1]), sp.expand(sol[I1])
A = sp.simplify(V1e.coeff(V2)); B = sp.simplify(-V1e.coeff(I2))
Cp = sp.simplify(I1e.coeff(V2)); D = sp.simplify(-I1e.coeff(I2))

Ae = 1 + R1 * Y2 + (1 / R3) * (s * L + R1 + R1 * s * L * Y2)
Be = R1 + s * L + R1 * s * L * Y2
Ce = Y2 + (1 + s * L * Y2) / R3
De = 1 + s * L * Y2
for got, exp in ((A, Ae), (B, Be), (Cp, Ce), (D, De)):
    assert sp.simplify(got - exp) == 0, (got, exp)
# reciprocal network: AD - BC = 1
assert sp.simplify(A * D - B * Cp - 1) == 0
print("A =", sp.factor(A)); print("B =", sp.factor(B)); print("C =", sp.factor(Cp)); print("D =", sp.factor(D))
print("PASS EE-110-01-2")
