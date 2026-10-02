"""EE-112-02-3 independent check: inverting buck-boost, L for iL,min = 0.4 IL, C for 0.5 % ripple.

Givens (official crop): Vs = 24 V, |Vo| = 36 V (figure marks - on top, + at bottom),
R = 10 ohm, fs = 100 kHz, ideal, CCM.
Method: flux (volt-second) and charge balance solved in SymPy for D, IL, L and C,
with the off-interval fall and the CCM valley checked separately.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vs, Vo, R, fs = 24, 36, 10, 100_000
T = sp.Rational(1, fs)
D, L, C, IL = sp.symbols("D L C I_L", positive=True)
Dv = sp.solve(sp.Eq(Vs * D - Vo * (1 - D), 0), D)[0]          # volt-second balance
Io = sp.Rational(Vo, R)
ILv = sp.solve(sp.Eq(IL * (1 - Dv), Io), IL)[0]                 # diode current average = Io
ripple = 2 * (ILv - sp.Rational(2, 5) * ILv)                     # peak-to-peak from valley spec
Lv = sp.solve(sp.Eq(Vs * Dv * T / L, ripple), L)[0]
assert Dv == sp.Rational(3, 5) and ILv == 9 and close(Lv, 13.333e-6)
# off-interval fall must equal on-interval rise (consistency)
assert sp.simplify(Vo * (1 - Dv) * T / Lv - ripple) == 0
# capacitor: during ON the diode is off, C alone supplies Io
Cv = sp.solve(sp.Eq(Io * Dv * T / C, sp.Rational(5, 1000) * Vo), C)[0]
assert close(Cv, 120e-6)
# valley positive -> CCM
assert ILv - ripple / 2 > 0
print(f"D={Dv} IL={ILv} A L={float(Lv)*1e6:.3f} uH C={float(Cv)*1e6:.1f} uF")
print("PASS EE-112-02-3")
