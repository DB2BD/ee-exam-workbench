"""EE-105-03-2 independent check (official crop): L{|sin(wt)|}."""
import mpmath as mp
import sympy as sp

t, s, w = sp.symbols("t s omega", positive=True)
T = sp.pi / w
# one-period integral then geometric series: F = (1/(1-e^{-sT})) * int_0^T e^{-st} sin(wt) dt
I1 = sp.simplify(sp.integrate(sp.exp(-s * t) * sp.sin(w * t), (t, 0, T)))
F = I1 / (1 - sp.exp(-s * T))
closed = w / (s**2 + w**2) * sp.coth(sp.pi * s / (2 * w))
for sv, wv in [(1.3, 2.0), (0.7, 1.0), (3.0, 0.5)]:
    a = sp.N(F.subs({s: sv, w: wv}))
    b = sp.N(closed.subs({s: sv, w: wv}))
    assert abs(a - b) / abs(b) < 1e-9, (a, b)
    # brute-force numeric Laplace integral of |sin|
    num = mp.quad(lambda tt: mp.e ** (-sv * tt) * abs(mp.sin(wv * tt)),
                  [k * mp.pi / wv for k in range(0, 200)])
    assert abs(num - mp.mpf(str(b))) / abs(num) < 5e-3, (num, b)
print("PASS EE-105-03-2")
