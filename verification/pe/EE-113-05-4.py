"""EE-113-05-4 independent check: governor speed regulation R = 0.05.

Givens (official crop): Δω/ω = -0.05 ΔPM (pu), frequency 60 -> 59 Hz;
range for PM from 0 to 1 pu.
"""
import sympy as sp

dP = sp.symbols("dP")
dPM = sp.solve(sp.Eq(sp.Rational(59 - 60, 60), -sp.Rational(5, 100) * dP), dP)[0]
assert dPM == sp.Rational(1, 3)
df = sp.Rational(5, 100) * 1 * 60
assert df == 3

# Method 2: droop line f = f_nl - R*f0*P; slope 3 Hz/pu -> 1 Hz drop gives 1/3 pu.
slope = 0.05 * 60
assert abs(1 / slope - float(dPM)) < 1e-12
assert abs(500 * float(dPM) - 166.667) / 166.667 <= 0.005
print("PASS EE-113-05-4")
