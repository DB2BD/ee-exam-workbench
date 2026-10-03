"""EE-106-02-1 independent check: three-op-amp state-variable filter.

Givens (official crop), all op amps ideal:
  A1: + node M = v_in --R4-- M --R5-- X ; - node N = v_out --R6-- N --R3-- Y ; output v_out.
  A2: v_out --R1--> (-), C1 from X (output) to (-), + grounded.   A3: X --R2--> (-), C2 from Y (output) to (-), + grounded.
Method: nullor equations / KCL on the summing nodes of A2, A3 and the virtual short of A1.
"""
import sympy as sp

s = sp.symbols("s")
R1, R2, R3, R4, R5, R6, C1, C2 = sp.symbols("R1 R2 R3 R4 R5 R6 C1 C2", positive=True)
vin, vout, vX, vY, vM, vN = sp.symbols("vin vout vX vY vM vN")
eqs = [
    sp.Eq(vout / R1 + vX * s * C1, 0),                 # summing node of A2 (virtual ground)
    sp.Eq(vX / R2 + vY * s * C2, 0),                   # summing node of A3
    sp.Eq((vin - vM) / R4 + (vX - vM) / R5, 0),        # node M (no current into A1 + input)
    sp.Eq((vout - vN) / R6 + (vY - vN) / R3, 0),       # node N
    sp.Eq(vM, vN),                                     # A1 virtual short
]
sol = sp.solve(eqs, [vX, vY, vM, vN, vout], dict=True)[0]
vo = sol[vout]
HX = sp.simplify(-1 / (s * R1 * C1))
HY = sp.simplify(1 / (s**2 * R1 * R2 * C1 * C2))
# (a), (b) in terms of v_out: substitute
sol2 = sp.solve(eqs[:2], [vX, vY], dict=True)[0]
assert sp.simplify(sol2[vX] / vout - HX) == 0
assert sp.simplify(sol2[vY] / vout - HY) == 0

# (c) v_out = A v_in + B v_out
A = R5 * (R3 + R6) / (R3 * (R4 + R5))
B = -R4 * (R3 + R6) / (R3 * (R4 + R5)) / (s * R1 * C1) - R6 / (R3 * s**2 * R1 * R2 * C1 * C2)
eq_c = sp.Eq(vout, A * vin + B * vout)
H_closed = sp.simplify(A / (1 - B))
assert sp.simplify(vo - H_closed * vin) == 0
# numeric spot check of the closed-form solution against the linear solve
vals = {R1: 1e3, R2: 2e3, R3: 3e3, R4: 4e3, R5: 5e3, R6: 6e3, C1: 1e-7, C2: 2e-7, s: 1j * 3000, vin: 1.0}
v_num = complex(vo.subs(vals))
v_chk = complex(H_closed.subs(vals))
assert abs(v_num - v_chk) / abs(v_chk) < 1e-9
# direct check: B-term form satisfies the original op-amp-1 relation
vXn = HX.subs(vals) * v_num
vYn = HY.subs(vals) * v_num
lhs = (vals[R5] * vals[vin] + vals[R4] * vXn) / (vals[R4] + vals[R5])                       # v+
rhs = (vals[R3] * v_num + vals[R6] * vYn) / (vals[R3] + vals[R6])                           # v-
assert abs(complex(lhs) - complex(rhs)) / abs(complex(lhs)) < 1e-9
print("A =", sp.simplify(A), "; closed loop =", sp.factor(H_closed))
print("PASS EE-106-02-1")
