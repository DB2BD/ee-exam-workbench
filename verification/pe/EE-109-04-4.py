"""EE-109-04-4: three-phase stator, axes a 0, b 120, c 240 deg; ia = I cos wt, ...; w = 100 pi."""
import sympy as sp

N, I, t = sp.symbols("N I t", positive=True)
th = sp.symbols("theta", real=True)
axes = [0, 2 * sp.pi / 3, 4 * sp.pi / 3]
cur = [I * sp.cos(th - ax) for ax in axes]          # theta = w_e t
Fx = sum(N * c * sp.cos(ax) for c, ax in zip(cur, axes))
Fy = sum(N * c * sp.sin(ax) for c, ax in zip(cur, axes))
assert sp.simplify(Fx - sp.Rational(3, 2) * N * I * sp.cos(th)) == 0
assert sp.simplify(Fy - sp.Rational(3, 2) * N * I * sp.sin(th)) == 0
for ang in (0, sp.pi / 3):
    fx, fy = Fx.subs(th, ang), Fy.subs(th, ang)
    assert sp.simplify(sp.sqrt(fx**2 + fy**2) - sp.Rational(3, 2) * N * I) == 0
    assert sp.simplify(sp.atan2(fy, fx) - ang) == 0
# rotation: angle = w_e t -> f = w_e / (2 pi)
f = 100 * sp.pi / (2 * sp.pi)
assert f == 50
# t = 0 component values: ia = I, ib = ic = -I/2 ; 60 deg: ia = ib = I/2, ic = -I
assert [sp.nsimplify(c.subs(th, 0) / I) for c in cur] == [1, sp.Rational(-1, 2), sp.Rational(-1, 2)]
assert [sp.nsimplify(c.subs(th, sp.pi / 3) / I) for c in cur] == [sp.Rational(1, 2), sp.Rational(1, 2), -1]
print("PASS EE-109-04-4")
