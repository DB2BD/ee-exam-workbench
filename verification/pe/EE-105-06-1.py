"""EE-105-06-1: single-phase three-wire, neutral open between N and M, Rg from load mid-point."""
import sympy as sp

RA, RB = sp.Rational(110**2, 1000), sp.Rational(110**2, 5000)
vm = sp.symbols("vm")                       # load mid-point potential w.r.t. transformer centre tap (N)

def solve(Rg):
    # KCL at the load mid-point: currents in from A (+110) and B (-110) leave through Rg
    eq = sp.Eq((110 - vm) / RA + (-110 - vm) / RB, vm / Rg)
    v = sp.solve(eq, vm)[0]
    return 110 - v, -110 - v                # V_AN, V_BN of the loads (A top, B bottom)

a0, b0 = solve(sp.Rational(1, 10**9))
assert abs(float(a0) - 110) < 1e-3 and abs(float(b0) + 110) < 1e-3
a, b = solve(1000)
assert abs(float(a) - 183.186) / 183.186 < 0.005
assert abs(float(b) + 36.814) / 36.814 < 0.005
# limit Rg -> infinity: pure series divider of 220 V
assert abs(220 * float(RA) / float(RA + RB) - 183.333) < 1e-3
# power-balance check of the Rg result: source power = load power + Rg power
va, vb = float(a), -float(b)
Ia, Ib = va / float(RA), vb / float(RB)
Ig = Ib - Ia
assert abs(Ig * 1000 - (va - 110)) < 1e-6    # Rg drop equals mid-point shift
assert abs(110 * Ia + 110 * Ib - (va * Ia + vb * Ib + Ig**2 * 1000)) < 1e-6
print("PASS EE-105-06-1")
