"""EE-110-06-1: (一) PF benefits + Taipower PF clause (descriptive, quantitative rule checked);
(二) R-L circuit switched onto v = Vm sin(wt + alpha): steady AC and decaying DC components.
"""
import sympy as sp

t, R, L, w, Vm, a = sp.symbols("t R L omega V_m alpha", positive=True)
i = sp.Function("i")
sol = sp.dsolve(sp.Eq(L * i(t).diff(t) + R * i(t), Vm * sp.sin(w * t + a)), i(t), ics={i(0): 0}).rhs
Z = sp.sqrt(R**2 + (w * L) ** 2)
theta = sp.atan(w * L / R)
i_ac = Vm / Z * sp.sin(w * t + a - theta)
i_dc = -Vm / Z * sp.sin(a - theta) * sp.exp(-R * t / L)
# symbolic equality with the closed form used in the note (boxed i_ac and i_dc)
diff = sp.simplify(sp.expand_trig(sol - (i_ac + i_dc)))
num = {R: 0.7, L: 0.013, w: 314.159, Vm: 311.0, a: 0.4}
for tv in (0.0, 0.003, 0.02, 0.1):
    assert abs(float(diff.subs(num).subs(t, tv))) < 1e-9
# independent checks: particular solution satisfies the ODE, natural part satisfies homogeneous ODE, i(0)=0
assert sp.simplify(sp.expand_trig(L * i_ac.diff(t) + R * i_ac - Vm * sp.sin(w * t + a))) == 0
assert sp.simplify(L * i_dc.diff(t) + R * i_dc) == 0
assert sp.simplify((i_ac + i_dc).subs(t, 0)) == 0
# no DC offset when alpha = theta
assert sp.simplify(i_dc.subs(a, theta)) == 0
# Taipower PF clause: base 80 %, +-0.1 % of bill per 1 %, credit capped at 95 %
def adj(pf):
    return -0.1 * (min(pf, 95) - 80) if pf >= 80 else 0.1 * (80 - pf)
assert adj(70) == 1.0 and abs(adj(95) + 1.5) < 1e-12 and abs(adj(99) + 1.5) < 1e-12
print("PASS EE-110-06-1")
