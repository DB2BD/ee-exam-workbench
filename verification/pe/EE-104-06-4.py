"""EE-104-06-4: sequence impedances from 3-phase and single-phase-to-ground fault MVA (22.8 kV)."""
import sympy as sp

V = sp.Rational(228, 10)                    # kV line-to-line
S3, S1 = 448, 470                           # MVA
Z1 = V**2 / S3                              # I3 = V/(sqrt3 Z1) -> S3 = V^2/Z1
Z2 = Z1
# I_f = 3 Vph/(Z1+Z2+Z0), S1 = sqrt3 V I_f = 3 V^2/(Z1+Z2+Z0)
Z0 = sp.symbols("Z0")
sol = sp.solve(sp.Eq(3 * V**2 / (Z1 + Z2 + Z0), S1), Z0)[0]
assert abs(float(Z1) - 1.16036) / 1.16036 < 0.005
assert abs(float(sol) - 0.99741) / 0.99741 < 0.005
# per-unit cross check on 100 MVA
X1pu = sp.Rational(100, S3)
X0pu = sp.Rational(300, S1) - 2 * X1pu
assert abs(float(X0pu) * float(V**2 / 100) - float(sol)) < 1e-9
print("PASS EE-104-06-4")
