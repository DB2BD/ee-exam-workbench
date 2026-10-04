"""EE-105-04-3 (descriptive): wound-rotor induction motor, external rotor resistance vs starting torque/current.
Quantitative arguments on the Thevenin equivalent with arbitrary sample parameters (not from the stem)."""
import sympy as sp

Rt, X, V, ws, r = sp.symbols("R_t X V omega_s r", positive=True)
# r = rotor-referred total rotor resistance R2'+Rext'; Rt = Thevenin resistance; X = Xth + X2' 
Tst = 3 * V**2 * r / (ws * ((Rt + r) ** 2 + X**2))
crit = sp.solve(sp.diff(Tst, r), r)
assert len(crit) == 1 and sp.simplify(crit[0] - sp.sqrt(Rt**2 + X**2)) == 0   # peak start torque at r=sqrt(Rth^2+X^2)
Ist = V / sp.sqrt((Rt + r) ** 2 + X**2)
assert sp.simplify(sp.diff(Ist, r).subs({Rt: 1, X: 2, V: 1, r: 3})) < 0     # current falls as r grows
# numeric example: Rth=0.3, X=1.0, R2'=0.2 -> r_opt=1.044; Rext'=0.844 raises Tst and lowers Ist
vals = {Rt: 0.3, X: 1.0, V: 1.0, ws: 1.0}
t0 = float(Tst.subs(vals).subs(r, 0.2)); t1 = float(Tst.subs(vals).subs(r, (0.3**2 + 1.0)**0.5))
i0 = float(Ist.subs(vals).subs(r, 0.2)); i1 = float(Ist.subs(vals).subs(r, (0.3**2 + 1.0)**0.5))
assert t1 > t0 and i1 < i0
print("PASS EE-105-04-3 (descriptive)")
