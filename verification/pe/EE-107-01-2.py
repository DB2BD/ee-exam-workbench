"""EE-107-01-2 independent check: two parallel inductors with initial currents, switch opens at t = 0.

Givens (official crop): L1 = 5 H, L2 = 20 H, initial currents 8 A and 4 A, BOTH arrows point
up in the figure while i1(t), i2(t) are defined downward => i1(0) = -8 A, i2(0) = -4 A.
After opening, the inductors see 40 ohm in parallel with [4 ohm + (15 || 10)] ohm.
i3 is the downward current in the 10 ohm resistor.
"""
import sympy as sp

t = sp.symbols("t", nonnegative=True)
L1, L2 = 5, 20
Rp = sp.Rational(15 * 10, 15 + 10)
Rbranch = 4 + Rp
Req = sp.Rational(40) * Rbranch / (40 + Rbranch)
assert Req == 8
# state ODE solved symbolically: node equation  i1 + i2 + v/Req = 0, v = L1 i1' = L2 i2'
i1 = sp.Function("i1")
i2expr = -4 + (L1 / sp.Integer(L2)) * (i1(t) - (-8))            # flux linkage constraint L1 di1 = L2 di2
ode = sp.Eq(i1(t) + i2expr + L1 * sp.diff(i1(t), t) / Req, 0)
sol = sp.dsolve(ode, i1(t), ics={i1(0): -8})
i1_t = sp.simplify(sol.rhs)
i2_t = sp.simplify(i2expr.subs(i1(t), i1_t))
v_t = sp.simplify(L1 * sp.diff(i1_t, t))
# resistor network
i_branch = v_t / Rbranch
i3_t = sp.simplify(i_branch * Rp / 10)   # voltage across 15||10 divided by 10 ohm
assert sp.simplify(i1_t - (sp.Rational(8, 5) - sp.Rational(48, 5) * sp.exp(-2 * t))) == 0, i1_t
assert sp.simplify(i3_t - sp.Rational(144, 25) * sp.exp(-2 * t)) == 0, i3_t
# independent: flux (L1 i1 + L2 i2) is not conserved, but the energy dissipated equals the stored energy
E0 = sp.Rational(1, 2) * L1 * 8**2 + sp.Rational(1, 2) * L2 * 4**2
Einf_circ = sp.Rational(1, 2) * L1 * i1_t.subs(t, sp.oo)**2 + sp.Rational(1, 2) * L2 * i2_t.subs(t, sp.oo)**2
Pdiss = sp.integrate(v_t**2 / Req, (t, 0, sp.oo))
assert sp.simplify(E0 - Einf_circ - Pdiss) == 0
print("PASS EE-107-01-2")
