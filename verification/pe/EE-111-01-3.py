"""EE-111-01-3 independent check: band-stop response of the loaded RLC.

Givens (official crop): vi -> Ro = 6 ohm -> node; R = 4 ohm from node to
ground; series L = 1 mH, C = 4 uF from node to ground; vo across the L-C branch.
The check derives H(s) by voltage division, then finds the -3 dB points
numerically from |H(jw)| = |H(0)|/sqrt(2) (not from the closed-form quadratic).
"""
import numpy as np
import sympy as sp

s = sp.symbols("s")
Ro, R, L, C = sp.symbols("R_o R L C", positive=True)
Zlc = s * L + 1 / (s * C)
Zp = R * Zlc / (R + Zlc)
H = sp.simplify(Zp / (Ro + Zp))
target = R / (Ro + R) * (s**2 + 1 / (L * C)) / (s**2 + s * Ro * R / ((Ro + R) * L) + 1 / (L * C))
assert sp.simplify(H - target) == 0

vals = {Ro: 6, R: 4, L: sp.Rational(1, 1000), C: sp.Rational(4, 10**6)}
Hn = sp.lambdify(s, H.subs(vals), "numpy")
H0 = abs(Hn(1e-9j))
assert abs(H0 - 0.4) < 1e-9
w0 = 1 / np.sqrt(1e-3 * 4e-6)

def g(w):
    return abs(Hn(1j * w)) - H0 / np.sqrt(2)

def bisect(lo, hi):
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if np.sign(g(mid)) == np.sign(g(lo)):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

w1 = bisect(1.0, w0 - 1e-6)
w2 = bisect(w0 + 1e-6, 1e7)
BW = w2 - w1
print(f"w0={w0:.3f} w1={w1:.3f} w2={w2:.3f} BW={BW:.4f}")
assert abs(BW - 2400) / 2400 < 1e-6
assert abs(w1 - 14656.86) / 14656.86 < 5e-5
assert abs(w2 - 17056.86) / 17056.86 < 5e-5
assert abs(w1 * w2 - w0**2) / w0**2 < 1e-9
print("PASS EE-111-01-3")
