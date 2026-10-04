"""EE-104-01-5: g-parameters: I1 = g11 V1 + g12 I2, V2 = g21 V1 + g22 I2.  Dependent source 100*I2 (+ top) from node P to ground."""
import sympy as sp
V1, V2, I1, I2, VP, VQ = sp.symbols("V1 V2 I1 I2 VP VQ")
eqs = [sp.Eq(VP, 100 * I2),
       sp.Eq(V1, (20 + 10j) * I1 + VP),               # input mesh (I1 enters node P, dependent source fixes VP)
       sp.Eq(I2, V2 / (-50j) + (V2 - VP) / 500)]      # KCL at output node Q (I2 flows in)
s = sp.solve(eqs, [VP, I1, V2], dict=True)[0]
def coef(expr, var): return complex(sp.diff(expr, var))
g11, g12 = coef(s[I1], V1), coef(s[I1], I2)
g21, g22 = coef(s[V2], V1), coef(s[V2], I2)
assert abs(g11 - (0.04 - 0.02j)) < 1e-9, g11
assert abs(g12 - (-4 + 2j)) < 1e-9, g12
assert abs(g21) < 1e-12, g21
assert abs(g22 - 1.2 / (0.002 + 0.02j)) / abs(g22) < 5e-3, g22
assert abs(g22 - (5.9406 - 59.406j)) < 1e-2
print("PASS EE-104-01-5")
