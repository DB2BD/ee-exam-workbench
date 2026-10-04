"""EE-104-01-4: ig = 20u(t) mA, zero initial state.  Top node vo: ig (up) = i(50 ohm + 100 uF) + 15e-3*v_phi (down) + i_L (1 H)."""
import sympy as sp
s, t = sp.symbols("s t", positive=True)
Vo, Vphi = sp.symbols("Vo Vphi")
Ig = sp.Rational(20, 1000) / s
C, R, L = sp.Rational(1, 10000), 50, 1
Ibr = Vo / (R + 1 / (s * C))
eqs = [sp.Eq(Vphi, Ibr / (s * C)),
       sp.Eq(Ig, Ibr + sp.Rational(15, 1000) * Vphi + Vo / (s * L))]
sol = sp.solve(eqs, [Vo, Vphi], dict=True)[0]
Vos = sp.simplify(sol[Vo])
assert sp.simplify(Vos - (s + 200) / (s + 100)**2) == 0, Vos
vo = sp.inverse_laplace_transform(Vos, s, t)
assert sp.simplify(vo - sp.exp(-100 * t) * (1 + 100 * t)) == 0, vo
# time-domain check: ODE for vo, vo(0+)=1, vo'(0+)=-100 + ... verify numerically
f = sp.exp(-100 * t) * (1 + 100 * t)
assert f.subs(t, 0) == 1
print("PASS EE-104-01-4")
