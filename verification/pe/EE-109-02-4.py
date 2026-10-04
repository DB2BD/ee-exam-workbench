"""EE-109-02-4 independent check: enhancement NMOS Vt and beta from two VGS = VDS points.

Givens (official crop): VGS = VDS = 12 V -> ID = 6 mA; VGS = VDS = 8 V -> ID = 1.5 mA;
beta = un Cox (W/L), so ID = (beta/2)(VGS - Vt)^2 in saturation (VDS = VGS > VGS - Vt).
Method: solve the two square-law equations simultaneously with SymPy, keep the root
with Vt below both VGS values.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vt, beta = sp.symbols("Vt beta", real=True)
eqs = [sp.Eq(sp.Rational(6, 1000), beta / 2 * (12 - Vt) ** 2),
       sp.Eq(sp.Rational(15, 10000), beta / 2 * (8 - Vt) ** 2)]
sols = [s for s in sp.solve(eqs, [Vt, beta], dict=True) if s[Vt] < 8 and s[beta] > 0]
assert len(sols) == 1
s = sols[0]
assert close(s[Vt], 4.0) and close(s[beta] * 1e6, 187.5)
# rejected root Vt = 9.33 V would put the 8 V point in cut-off
print(f"Vt={s[Vt]} V beta={float(s[beta])*1e6:.2f} uA/V^2")
print("PASS EE-109-02-4")
