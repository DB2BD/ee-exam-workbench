"""EE-107-02-1 independent check: silicon pn junction at 300 K.

Givens (official crop): NA = 5e16, ND = 2e16, ni = 2e10 (cm^-3), T = 300 K.
Constants NOT given in the stem (assumed): k = 1.380649e-23 J/K, q = 1.602177e-19 C, eps_Si = 11.7 eps0, eps0 = 8.854e-14 F/cm.
Method: V0 = (kT/q) ln(NA ND/ni^2); W from charge neutrality (NA xp = ND xn) and Poisson.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


k, q, T = 1.380649e-23, 1.602177e-19, 300
NA, ND, ni = 5e16, 2e16, 2e10
eps = 11.7 * 8.854e-14
VT = k * T / q
V0 = VT * sp.log(NA * ND / ni**2)
W = sp.sqrt(2 * eps * V0 / q * (1 / NA + 1 / ND))          # cm
xp, xn = sp.symbols("xp xn", positive=True)
s = sp.solve([sp.Eq(NA * xp, ND * xn), sp.Eq(xp + xn, W)], [xp, xn], dict=True)[0]
assert close(VT * 1e3, 25.852) and close(V0, 0.738)
assert close(W * 1e4, 0.2585) and close(s[xp] * 1e4, 0.0739) and close(s[xn] * 1e4, 0.1846)
# Poisson cross-check: peak field from each side, E = q ND xn / eps = q NA xp / eps ; V0 = E W / 2
E = q * ND * s[xn] / eps
assert close(E * W / 2, float(V0))
assert close(s[xn] / s[xp], 2.5)                          # xn/xp = NA/ND
print(f"V0={float(V0):.4f} V W={float(W)*1e4:.4f} um xp={float(s[xp])*1e4:.4f} um xn={float(s[xn])*1e4:.4f} um")
print("PASS EE-107-02-1")
