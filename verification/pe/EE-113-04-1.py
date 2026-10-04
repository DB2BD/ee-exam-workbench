"""EE-113-04-1 (descriptive): transformer magnetic circuit -> T equivalent.

Model from the crop: MMFs N1 i1 and N2 i2 (both currents enter dotted ends),
core reluctance R_M carries phi_M, leakage reluctances R_l1 / R_l2.
"""
import sympy as sp

N1, N2, RM, Rl1, Rl2, R1, R2 = sp.symbols("N1 N2 R_M R_l1 R_l2 R1 R2", positive=True)
t = sp.Symbol("t")
i1, i2 = sp.Function("i1")(t), sp.Function("i2")(t)

phiM = (N1 * i1 + N2 * i2) / RM
lam1 = N1 * (N1 * i1 / Rl1 + phiM)
lam2 = N2 * (N2 * i2 / Rl2 + phiM)
v1 = R1 * i1 + sp.diff(lam1, t)
v2 = R2 * i2 + sp.diff(lam2, t)

Ll1, Ll2, Lm = N1**2 / Rl1, N2**2 / Rl2, N1**2 / RM      # boxed formulas
a = N1 / N2
# T circuit referred to primary: i2' = i2/a, R2' = a^2 R2, Ll2' = a^2 Ll2
i2p = i2 / a
v1_T = R1 * i1 + Ll1 * sp.diff(i1, t) + Lm * sp.diff(i1 + i2p, t)
v2p_T = a**2 * R2 * i2p + a**2 * Ll2 * sp.diff(i2p, t) + Lm * sp.diff(i1 + i2p, t)
assert sp.simplify(v1 - v1_T) == 0
assert sp.simplify(a * v2 - v2p_T) == 0
assert sp.simplify(a**2 * Ll2 - N1**2 / Rl2) == 0                  # referred leakage
assert sp.simplify(sp.diff(lam1, i1) - (Ll1 + Lm)) == 0             # self inductance L11
assert sp.simplify(sp.diff(lam1, i2) - N1 * N2 / RM) == 0           # mutual M
print("PASS EE-113-04-1 (descriptive: reluctance-to-inductance mapping)")
