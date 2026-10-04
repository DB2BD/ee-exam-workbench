"""EE-104-02-5 independent check: three-section RC phase-shift oscillator (official crop).

Circuit (crop): Vo -> C -> V3 (R to ground) -> C -> V2 (R to ground) -> C -> V1 -> R -> inverting
input (virtual ground), RF from output to inverting input, non-inverting input grounded.
Method: nodal analysis of the ladder with an ideal op-amp, then the oscillation condition
L(j w0) = 1 for the loop gain L = A*beta.
"""
import sympy as sp

s, R, C, Rf, w = sp.symbols("s R C Rf w", positive=True)
V3, V2, V1, Vo = sp.symbols("V3 V2 V1 Vo")
sC = s * C
G = 1 / R
# node V3: (V3-Vo)sC + V3 G + (V3-V2) sC = 0 ; node V2 ; node V1 (R to virtual ground)
sol = sp.solve([
    sp.Eq((V3 - Vo) * sC + V3 * G + (V3 - V2) * sC, 0),
    sp.Eq((V2 - V3) * sC + V2 * G + (V2 - V1) * sC, 0),
    sp.Eq((V1 - V2) * sC + V1 * G, 0),
], [V3, V2, V1], dict=True)[0]
beta = sp.simplify(sol[V1] / Vo)
A = -Rf / R                     # inverting stage: Vo' = -(Rf/R) V1
L = sp.simplify(A * beta)
x = s * R * C
assert sp.simplify(beta - x**3 / (x**3 + 6 * x**2 + 5 * x + 1)) == 0
Lj = sp.simplify(L.subs(s, sp.I * w))
# phase condition: the ladder must contribute 180 deg, i.e. Im{1/beta(jw)} = 0
inv_beta = sp.simplify(sp.expand_complex(sp.simplify((1 / beta).subs(s, sp.I * w))))
w0 = [v for v in sp.solve(sp.im(inv_beta), w) if v.is_positive][0]
assert sp.simplify(w0 - 1 / (sp.sqrt(6) * R * C)) == 0
bw0 = sp.simplify(beta.subs(s, sp.I * w0))
assert sp.simplify(bw0 + sp.Rational(1, 29)) == 0          # beta(jw0) = -1/29
Lw0 = sp.simplify(Lj.subs(w, w0))                           # L = A beta
assert sp.simplify(Lw0 - Rf / (29 * R)) == 0                # positive real -> |L|=1 gives Rf = 29 R
assert sp.solve(sp.Eq(Lw0, 1), Rf) == [29 * R]
Rf_val = 29 * 6000
Cval = 1 / (2 * sp.pi * sp.sqrt(6) * 6000 * 5000)
assert abs(float(Cval) - 2.166e-9) / 2.166e-9 < 0.001 and Rf_val == 174000
print(f"beta(jw0)={bw0}, C={float(Cval):.4e} F, Rf={Rf_val} ohm")
print("PASS EE-104-02-5")
