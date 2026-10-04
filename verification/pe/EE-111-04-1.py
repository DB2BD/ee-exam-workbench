"""EE-111-04-1 (descriptive): toroid inductance and four ways to raise it.

Toroid of permeability mu, N turns, mean radius r, circular section radius a (2a given).
"""
import sympy as sp

mu, N, a, r, i = sp.symbols("mu N a r i", positive=True)
H = N * i / (2 * sp.pi * r)            # Ampere's law on the mean path
lam = N * mu * H * sp.pi * a**2        # flux linkage
L = sp.simplify(lam / i)
assert sp.simplify(L - mu * N**2 * a**2 / (2 * r)) == 0
# reluctance route
Rm = 2 * sp.pi * r / (mu * sp.pi * a**2)
assert sp.simplify(N**2 / Rm - L) == 0
# monotonic dependences: dL/dmu, dL/dN, dL/da > 0 ; dL/dr < 0
assert sp.simplify(sp.diff(L, mu)) .is_positive
assert sp.simplify(sp.diff(L, N)).is_positive
assert sp.simplify(sp.diff(L, a)).is_positive
assert sp.simplify(sp.diff(L, r)).is_negative
# doubling N -> 4x, doubling a -> 4x, halving r -> 2x
assert sp.simplify(L.subs(N, 2 * N) / L) == 4
assert sp.simplify(L.subs(a, 2 * a) / L) == 4
assert sp.simplify(L.subs(r, r / 2) / L) == 2
print("PASS EE-111-04-1 (descriptive: L = mu N^2 a^2 / (2 r))")
