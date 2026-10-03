"""EE-108-06-1: capacitive voltage transformer (CVT) transfer function V2/V1.

Givens (crop, Fig. 1): V1 across series C1-C2 to ground; L from the C1/C2 midpoint in
series with load Z_B to ground; V2 across Z_B.  Solved from node analysis, no note values used.
"""
import sympy as sp

s, C1, C2, L, ZB, V1, Va = sp.symbols("s C1 C2 L Z_B V1 V_a")
Z1, Z2, ZL = 1 / (s * C1), 1 / (s * C2), s * L

# KCL at the C1/C2/L node
Va_sol = sp.solve(sp.Eq((Va - V1) / Z1 + Va / Z2 + Va / (ZL + ZB), 0), Va)[0]
V2 = Va_sol * ZB / (ZL + ZB)
H = sp.simplify(V2 / V1)

boxed_impedance_form = Z2 * ZB / (Z1 * Z2 + (Z1 + Z2) * (ZL + ZB))
boxed_s_form = s * C1 * ZB / (1 + s * (C1 + C2) * ZB + s**2 * L * (C1 + C2))
assert sp.simplify(H - boxed_impedance_form) == 0
assert sp.simplify(H - boxed_s_form) == 0

# Thevenin check: V_th = V1*C1/(C1+C2), Z_th = 1/(s(C1+C2)) in series with L and Z_B
Vth = C1 / (C1 + C2)
Zth = 1 / (s * (C1 + C2))
assert sp.simplify(H - Vth * ZB / (Zth + ZL + ZB)) == 0

# Z_B -> infinity: ideal capacitive divider
assert sp.simplify(sp.limit(H, ZB, sp.oo) - C1 / (C1 + C2)) == 0

# Compensation: L = 1/(w0^2 (C1+C2)) makes the ratio C1/(C1+C2) for every Z_B at w0
w0 = sp.symbols("omega_0", positive=True)
H_comp = H.subs(s, sp.I * w0).subs(L, 1 / (w0**2 * (C1 + C2)))
assert sp.simplify(H_comp - C1 / (C1 + C2)) == 0

print("PASS EE-108-06-1")
