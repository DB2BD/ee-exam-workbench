"""EE-109-02-2 independent check: boost converter ripple and critical values.

Givens (official crop): Vs = 15 V, Vo = 30 V, Io = 3 A, f = 25 kHz, L = 100 uH, C = 200 uF.
Method: steady-state balances solved with SymPy (inductor volt-second, capacitor charge),
CCM/DCM boundary from Imin = 0; critical capacitance = continuous-capacitor-voltage
boundary (ripple reaches 2*Vo, textbook definition), plus the C(eps) design form.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vs, Vo, Io, f, L, C = 15, 30, 3, 25_000, sp.Rational(1, 10**4), sp.Rational(2, 10**4)
T = sp.Rational(1, f)
D, IL, Lb, eps = sp.symbols("D I_L L_b epsilon", positive=True)
D = sp.solve(sp.Eq(Vs * D + (Vs - Vo) * (1 - D), 0), D)[0]          # volt-second
IL = sp.solve(sp.Eq(-Io * D + (IL - Io) * (1 - D), 0), IL)[0]         # capacitor charge balance
dIL = Vs * D * T / L
IL_peak = IL + dIL / 2
dVC = Io * D * T / C                                                  # C alone feeds load during DT
R = sp.Rational(Vo, Io)
# boundary: minimum inductor current reaches zero, IL = dIL/2 with L unknown
Lc = sp.solve(sp.Eq(Vo / R / (1 - D), Vs * D * T / Lb / 2), Lb)[0]
Cc = Io * D * T / (eps * Vo)                                          # C giving ripple eps*Vo

assert D == sp.Rational(1, 2) and IL == 6
assert close(dIL, 3) and close(IL_peak, 7.5) and close(dVC, 0.3)
assert IL - dIL / 2 > 0                    # given L operates in CCM
assert close(Lc * 1e6, 25)
assert sp.simplify(Cc - sp.Rational(2, 10**6) / eps) == 0
assert sp.simplify(Cc.subs(eps, dVC / Vo) - C) == 0   # actual ripple only returns the given C (circular)
Ccrit = sp.solve(sp.Eq(Io * D * T / sp.Symbol("Cx"), 2 * Vo), sp.Symbol("Cx"))[0]   # ripple = 2 Vo
assert close(Ccrit * 1e6, 1.0) and sp.simplify(Ccrit - D / (2 * f * R)) == 0
assert sp.simplify(Cc.subs(eps, 2) - Ccrit) == 0
print(f"D={D} IL={IL} dIL={float(dIL)} ILpk={float(IL_peak)} dVC={float(dVC)} Lc={float(Lc)*1e6} uH "
      f"Cc(eps)=2uF/eps, Cc(2)={float(Cc.subs(eps, 2))*1e6} uF")
print("PASS EE-109-02-2")
