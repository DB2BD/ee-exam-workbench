"""EE-114-04-5: reluctance motor, R(theta) = R0 - R1 cos 4theta.

R1 = 1e5, N = 50, v = 110 sqrt2 sin(wt), 60 Hz; T = 1/2 phi^2 dR/dtheta (crop).
"""
import sympy as sp

t, w, wm, d = sp.symbols("t omega omega_m delta", positive=True)
R0, R1, N = 2 * 10**5, 10**5, 50
Vm = 110 * sp.sqrt(2)
phi = sp.integrate(Vm * sp.sin(w * t), t) / N            # zero dc flux
th = sp.Symbol("theta")
Rf = R0 - R1 * sp.cos(4 * th)
T = sp.Rational(1, 2) * phi**2 * sp.diff(Rf, th).subs(th, wm * t + d)
Phim = Vm / (N * w)
target = 2 * R1 * Phim**2 * sp.cos(w * t) ** 2 * sp.sin(4 * wm * t + 4 * d)
import random
for _ in range(20):                                        # boxed T(t), random points
    sub = {t: random.random(), w: 1 + 400 * random.random(), wm: 200 * random.random(), d: random.random()}
    assert abs(float((T - target).subs(sub))) <= 1e-9 * max(1.0, abs(float(target.subs(sub))))

for sgn in (1, -1):                                       # both synchronous directions
    Ts = T.subs(wm, sgn * w / 2)
    avg = sp.integrate(Ts, (t, 0, 2 * sp.pi / w)) / (2 * sp.pi / w)
    assert sp.simplify(avg - R1 * Phim**2 * sp.sin(4 * d) / 2) == 0

wv = 2 * sp.pi * 60
Tmax = float((R1 * Phim**2 / 2).subs(w, wv))
Pmax = Tmax * float(wv / 2)
assert abs(float(Phim.subs(w, wv)) - 8.2530e-3) / 8.2530e-3 <= 0.005
assert abs(Tmax - 3.4055) / 3.4055 <= 0.005
assert abs(Pmax - 642) / 642 <= 0.005
# the official hint identity sin a sin b = [sin(a+b)+sin(a-b)]/2 fails at a=b=pi/2
a = sp.pi / 2
assert sp.sin(a) * sp.sin(a) != (sp.sin(2 * a) + sp.sin(0)) / 2
print(f"Phim={float(Phim.subs(w, wv)):.5e} Wb Tmax={Tmax:.4f} N.m Pmax={Pmax:.1f} W")
print("PASS EE-114-04-5")
