"""EE-107-02-2 independent check: NMOS gm and ro.

Givens (official crop): un*Cox = 20 uA/V^2, W/L = 400 um/10 um, Vt = 1.2 V, lambda = 0.01 1/V.
(a) VGS = 2 V; (b) ID = 2 mA.   ro = 1/(lambda ID) (VDS not given, so ID(1+lambda VDS) ~ ID).
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


kn = sp.Rational(20, 10**6) * sp.Rational(400, 10)          # A/V^2
lam = sp.Rational(1, 100)
VOV = 2 - sp.Rational(6, 5)
ID_a = kn * VOV**2 / 2
gm_a = kn * VOV
ro_a = 1 / (lam * ID_a)
assert close(kn * 1e3, 0.8) and close(ID_a * 1e3, 0.256) and close(gm_a * 1e3, 0.64) and close(ro_a / 1e3, 390.625)
ID_b = sp.Rational(2, 1000)
gm_b = sp.sqrt(2 * kn * ID_b)
ro_b = 1 / (lam * ID_b)
assert close(gm_b * 1e3, 1.7889) and close(ro_b / 1e3, 50)
# cross-checks: gm = 2 ID / VOV ; gm*ro = 2/(lambda VOV) = intrinsic gain
assert close(2 * ID_a / VOV, float(gm_a))
assert close(gm_b * ro_b, 2 / (lam * (2 * ID_b / gm_b)))
VOV_b = 2 * ID_b / gm_b
assert close(VOV_b, 2.236)                                   # (b) overdrive, VGS = 3.436 V
print(f"(a) gm={float(gm_a)*1e3:.4f} mS ro={float(ro_a)/1e3:.2f} k; (b) gm={float(gm_b)*1e3:.4f} mS ro={float(ro_b)/1e3:.1f} k")
print("PASS EE-107-02-2")
