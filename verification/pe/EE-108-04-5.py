"""EE-108-04-5: descriptive (structures of SRM / SPM synchronous motor, stepper pros/cons, DC armature reaction).
Quantitative statements used in the answer are checked symbolically."""
import sympy as sp

th, i, L0, L1 = sp.symbols("theta i L0 L1", real=True)
L = L0 + L1 * sp.cos(2 * th)                  # SRM phase inductance vs rotor angle (4 rotor-pole style, any periodic L)
Wco = sp.Rational(1, 2) * L * i**2            # magnetic co-energy at constant current
Te = sp.diff(Wco, th)
assert sp.simplify(Te - sp.Rational(1, 2) * i**2 * sp.diff(L, th)) == 0
# torque sign follows the sign of dL/dtheta
assert sp.simplify(Te.subs(th, sp.pi / 8)) == -L1 * i**2 * sp.sin(sp.pi / 4)
# SPM: Ld = Lq removes the reluctance term of the dq torque expression
Ld, Lq, psi, id_, iq, p = sp.symbols("Ld Lq psi i_d i_q p", real=True)
T_dq = sp.Rational(3, 2) * p * (psi * iq + (Ld - Lq) * id_ * iq)
assert sp.simplify(T_dq.subs(Ld, Lq) - sp.Rational(3, 2) * p * psi * iq) == 0
print("PASS EE-108-04-5 (descriptive)")
