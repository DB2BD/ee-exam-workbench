"""EE-114-02-2 independent check: two-capacitor stage, Avo, zero, OCTC bandwidth.

Givens (official crop): Rs = 15k, Ra = 3k, Ca = 3 pF (va node -> vo node),
Gm = 15 mA/V (current Gm*va flows from vo node down to ground), RL = 1k, CL = 2 pF.
Method: two-node KCL in SymPy -> exact transfer function, DC gain, zero, exact
poles; compared with open-circuit time constants (Rx seen by each capacitor).
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(abs(y)) <= 0.005


Rs, Ra, Ca, Gm, RL, CL = 15e3, 3e3, 3e-12, 15e-3, 1e3, 2e-12
s, va, vo = sp.symbols("s va vo")
vs = 1
eqs = [
    sp.Eq((va - vs) / Rs + va / Ra + (va - vo) * s * Ca, 0),
    sp.Eq((vo - va) * s * Ca + Gm * va + vo / RL + vo * s * CL, 0),
]
sol = sp.solve(eqs, [va, vo], dict=True)[0]
H = sp.together(sp.simplify(sol[vo]))
num, den = sp.fraction(H)
Avo = float(H.subs(s, 0))
zeros = sp.solve(num, s)
poles = sorted(abs(float(p)) for p in sp.solve(den, s))
assert close(Avo, -2.5)
assert len(zeros) == 1 and close(zeros[0], 5e9) and float(zeros[0]) > 0  # RHP zero
wz_form = -float(zeros[0])            # 1 + s/wz = 0 at s = +5e9  ->  wz = -5e9
assert close(wz_form, -5e9)

# OCTC (independent): test-source resistances
Rp = Rs * Ra / (Rs + Ra)
Rx_a = Rp + RL + Gm * Rp * RL
tau = Ca * Rx_a + CL * RL
wH = 1 / tau
assert close(Rx_a, 41e3) and close(tau, 125e-9)
assert close(wH, 8.0e6)
assert close(poles[0], wH)          # exact dominant pole 8.0077e6
assert poles[1] / poles[0] > 100 and 5e9 / wH > 100
print(f"Avo={Avo} zero=+{float(zeros[0]):.4e} poles={poles[0]:.5e},{poles[1]:.5e} OCTC wH={wH:.4e}")
print("PASS EE-114-02-2")
