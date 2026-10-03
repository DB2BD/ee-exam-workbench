"""EE-108-02-4 independent check: GIC (Antoniou) low-Q band-pass with a non-inverting x5 stage.

Givens (official crop): all op amps ideal.  Chain from node X: R (X-P), 2R (P-Q), R (Q-Y), C (Y-Z), R (Z-ground);
op amp A: + at X, - at Q, output Y;  op amp B: output P, - at Q, + at Z.  Input network: Vi - R - X, C from X to ground.
Top stage: + input at X, R1 to ground, 4R1 feedback -> gain 1 + 4 = 5.
Method: nodal analysis with nullor (virtual short) equations for A and B; output nodes of A/B are not KCL nodes.
"""
import sympy as sp

s, R, C, Vi = sp.symbols("s R C Vi", positive=True)
vX, vP, vQ, vY, vZ = sp.symbols("vX vP vQ vY vZ")
eqs = [
    sp.Eq(vQ, vX),                                            # op amp A virtual short
    sp.Eq(vQ, vZ),                                            # op amp B virtual short
    sp.Eq((vQ - vP) / (2 * R) + (vQ - vY) / R, 0),            # KCL at Q (no current into op-amp inputs)
    sp.Eq((vZ - vY) * s * C + vZ / R, 0),                     # KCL at Z
    sp.Eq((vX - Vi) / R + vX * s * C + (vX - vP) / R, 0),     # KCL at X
]
sol = sp.solve(eqs, [vX, vP, vQ, vY, vZ], dict=True)[0]
T = sp.simplify(5 * sol[vX] / Vi)
T_ref = 5 * s * R * C / (s**2 * R**2 * C**2 + s * R * C + 2)
assert sp.simplify(T - T_ref) == 0

# impedance seen into the R that leaves X: GIC  Z1 Z3 Z5 / (Z2 Z4)
Zin = sp.simplify(sol[vX] / ((sol[vX] - sol[vP]) / R))
assert sp.simplify(Zin - s * R**2 * C / 2) == 0
Zgic = R * R * R / (2 * R * (1 / (s * C)))
assert sp.simplify(Zin - Zgic) == 0

# band-pass: T(0)=0, T(inf)=0, centre w0 = sqrt2/(RC), peak gain 5, Q = sqrt2
w = sp.symbols("w", positive=True)
Tw = sp.simplify(T_ref.subs(s, sp.I * w / (R * C)))
assert sp.limit(T_ref, s, 0) == 0 and sp.limit(T_ref, s, sp.oo) == 0
w0 = sp.sqrt(2)
assert sp.simplify(sp.Abs(Tw.subs(w, w0)) - 5) < 1e-12
assert sp.simplify(sp.Abs(Tw.subs(w, w0)) - 5 * 1) == 0
# peak is the maximum of |T(jw)|
mag2 = sp.simplify(sp.Abs(Tw) ** 2)
assert sp.solve(sp.diff(mag2, w), w) == [sp.sqrt(2)]
# half-power bandwidth = w0/Q = 1/(RC)
Q = w0 / 1
f_half = sp.solve(sp.Eq(mag2, sp.Rational(25, 2)), w)
bw = max(f_half) - min(f_half)
assert abs(float(bw) - 1.0) < 1e-9
# the same function in the unnormalised form 10 sRC / (2 s^2 R^2 C^2 + 2 sRC + 4)
assert sp.simplify(T_ref - 10 * s * R * C / (2 * s**2 * R**2 * C**2 + 2 * s * R * C + 4)) == 0
print("T(s) =", sp.factor(T), "; Zin =", Zin)
print("PASS EE-108-02-4")
