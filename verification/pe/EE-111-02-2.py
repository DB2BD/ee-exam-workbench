"""EE-111-02-2 independent check: SEPIC converter (CCM) inductor and capacitor sizing.

Givens (official crop): Vin = 15 V, Vo = 6 V, R = 2 ohm, f = 250 kHz,
peak-to-peak inductor ripple = 40 % of each inductor's average current,
capacitor voltage ripple = 2 % of Vo for C1 and C2.
Method: solve the full steady-state balance set (volt-second on L1, L2 and
charge balance on C1, C2) symbolically for D, VC1, IL1, IL2, then size each
element from its on-interval slope / charge.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vin, Vo, R, f = sp.Integer(15), sp.Integer(6), sp.Integer(2), sp.Integer(250_000)
T = 1 / f
Io = Vo / R
D, VC1, IL1, IL2 = sp.symbols("D VC1 IL1 IL2", positive=True)
eqs = [
    sp.Eq(D * Vin + (1 - D) * (Vin - VC1 - Vo), 0),   # L1 volt-second (on: Vin; off: Vin - VC1 - Vo)
    sp.Eq(D * VC1 + (1 - D) * (-Vo), 0),              # L2 volt-second (on: +VC1; off: -Vo)
    sp.Eq(-IL2 * D + IL1 * (1 - D), 0),               # C1 charge (on: -IL2; off: +IL1)
    sp.Eq(-Io * D + (IL1 + IL2 - Io) * (1 - D), 0),   # C2 charge (on: -Io; off: IL1+IL2-Io)
]
sol = sp.solve(eqs, [D, VC1, IL1, IL2], dict=True)
sol = [s for s in sol if 0 < s[D] < 1][0]
assert sol[D] == sp.Rational(2, 7) and sol[VC1] == Vin

# both inductors see +Vin (L1: Vin; L2: VC1 = Vin) while the switch is on
L1 = Vin * sol[D] * T / (sp.Rational(2, 5) * sol[IL1])
L2 = sol[VC1] * sol[D] * T / (sp.Rational(2, 5) * sol[IL2])
dV = sp.Rational(2, 100) * Vo
C1 = sol[IL2] * sol[D] * T / dV      # C1 carries -IL2 during DT
C2 = Io * sol[D] * T / dV            # C2 alone feeds the load during DT

assert close(sol[IL1], 1.2) and close(sol[IL2], 3.0)
assert close(L1 * 1e6, 35.714) and close(L2 * 1e6, 14.286)
assert close(C1 * 1e6, 28.571) and close(C2 * 1e6, 28.571)
# off-interval charge must equal the on-interval charge (independent route for C1)
assert sp.simplify(sol[IL1] * (1 - sol[D]) * T - sol[IL2] * sol[D] * T) == 0
print(f"D={sol[D]} IL1={sol[IL1]} IL2={sol[IL2]} L1={float(L1)*1e6:.4f}uH L2={float(L2)*1e6:.4f}uH "
      f"C1={float(C1)*1e6:.4f}uF C2={float(C2)*1e6:.4f}uF")
print("PASS EE-111-02-2")
