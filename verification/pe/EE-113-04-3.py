"""EE-113-04-3: series DC motor 300 V, 60 A, 1800 rpm, Ra = Rs = 0.1 ohm;
0.1 ohm diverter across the field doubles the torque.  No magnetisation curve is
given; the answer is checked for linear and saturating curves."""
import sympy as sp

Ia = sp.Symbol("Ia", positive=True)
V, I1, n1, Ra, Rs, Rd = 300, 60, 1800, sp.Rational(1, 10), sp.Rational(1, 10), sp.Rational(1, 10)
If2 = Ia * Rd / (Rs + Rd)
sol = sp.solve(sp.Eq(If2 * Ia, 2 * I1 * I1), Ia)
Ia2 = sol[0]
assert Ia2 == 120
Ea1 = V - I1 * (Ra + Rs)
Rpar = Rs * Rd / (Rs + Rd)
Ea2 = V - Ia2 * (Ra + Rpar)
n2 = n1 * Ea2 / Ea1 * I1 / If2.subs(Ia, Ia2)
eta = Ea2 * Ia2 / (V * Ia2)
assert n2 == sp.Rational(3525, 2)          # 1762.5 rpm
assert eta == sp.Rational(94, 100)
# independent: power balance with individual copper losses
loss = Ia2**2 * Ra + If2.subs(Ia, Ia2) ** 2 * Rs + (Ia2 - If2.subs(Ia, Ia2)) ** 2 * Rd
assert V * Ia2 - loss == Ea2 * Ia2
# curve independence: for saturating curves Phi(If), solve Phi(Ia/2)*Ia = 2*Phi(60)*60
import math
for k in (0.005, 0.02, 0.05):
    Phi = lambda i_f: math.tanh(k * i_f)
    lo, hi = 1.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if Phi(mid / 2) * mid < 2 * Phi(60) * 60 else (lo, mid)
    assert abs((lo + hi) / 2 - 120) < 1e-6
print(f"Ia2={Ia2} A n2={float(n2)} rpm eta={float(eta)}")
print("PASS EE-113-04-3 (Ia2=120 A for any monotonic magnetisation curve)")
