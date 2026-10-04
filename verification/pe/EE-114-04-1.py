"""EE-114-04-1: two-pole structure, two series air gaps, ideal iron.

Givens (official crop): l_g = 2 mm per gap, A_g = 400 cm^2, N = 400, I = 4 A,
mu_c -> infinity, no leakage / fringing.
"""
import sympy as sp

mu0 = 4 * sp.pi * sp.Rational(1, 10**7)
lg, Ag, N, I = sp.Rational(2, 1000), sp.Rational(400, 10**4), 400, 4

Rg = lg / (mu0 * Ag)               # one gap
R_eq = 2 * Rg                      # flux crosses the gap twice
Phi = N * I / R_eq
B = Phi / Ag
L = N**2 / R_eq

def close(x, ref):
    return abs(float(x) - ref) / ref <= 0.005

assert close(B, 0.5027)            # boxed B_g
assert close(L, 2.011)             # boxed L
# independent: Ampere's law with H_g only, then flux linkage / current
B_amp = mu0 * N * I / (2 * lg)
assert sp.simplify(B_amp - B) == 0
assert sp.simplify(N * B_amp * Ag / I - L) == 0
print(f"B={float(B):.5f} T  Phi={float(Phi):.6f} Wb  L={float(L):.5f} H")
print("PASS EE-114-04-1")
